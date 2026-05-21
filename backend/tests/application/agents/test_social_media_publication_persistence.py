"""Tests d'intégration : SocialMediaAgent + SocialMediaPublicationRepository.

Utilise un vrai SQLite in-memory pour le repository et mock le graph LangGraph.
Démontre la séparation runtime (LangGraph) / projection métier (SocialMediaPublicationRepository).
"""
import json
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.application.agents.social_media_agent import SocialMediaAgent
from app.infrastructure.db.models.social_media_publication_model import Base
from app.infrastructure.db.repositories.social_media_publication_repository import SocialMediaPublicationRepository


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.fixture
def mock_graph():
    """Graph qui se termine normalement (pas d'interruption)."""
    graph = MagicMock()
    graph.invoke.return_value = {
        "final_result": {"success": True, "error": None, "data": {}}
    }
    return graph


_FINAL_RESULT = {
    "success": True,
    "error": None,
    "data": {
        "status": "draft",
        "approval_status": "pending",
        "platforms": {"facebook": {"generated": True, "post": "Belle villa !", "hashtags": [], "images": []}},
    },
}


@pytest.fixture
def mock_graph_suspends():
    """Graph qui atteint wait_for_approval et retourne __interrupt__ + final_result."""
    graph = MagicMock()
    graph.invoke.return_value = {
        "__interrupt__": ["Waiting for approval"],
        "final_result": _FINAL_RESULT,
    }
    return graph


def _make_agent(session, mock_graph):
    repo = SocialMediaPublicationRepository(session)
    with patch("app.application.agents.social_media_agent.build_social_media_graph") as mock_build:
        mock_build.return_value = mock_graph
        agent = SocialMediaAgent(publication_repository=repo)
    return agent, repo


class TestRunPersistenceOnInterrupt:
    """La DB ne doit refléter que les états publication réellement atteints.

    save() est appelé uniquement si le graph confirme une interruption.
    Un graph qui réussit ou échoue sans interrupt ne doit laisser aucune trace.
    """

    def test_save_called_when_graph_suspends(self, session, mock_graph_suspends):
        agent, repo = _make_agent(session, mock_graph_suspends)

        raw = agent.run("Génère un post Facebook", "{}")

        # Le thread_id est généré dynamiquement dans run() et retourné dans la réponse.
        thread_id = json.loads(raw)["data"]["thread_id"]
        publication = repo.find_by_thread_id(thread_id)
        assert publication is not None
        assert publication.status == "draft"
        assert publication.approval_status == "pending"

    def test_save_not_called_when_graph_completes_normally(self, session, mock_graph):
        # mock_graph retourne final_result sans __interrupt__ :
        # la publication n'a jamais été suspendue, rien ne doit être persisté.
        agent, repo = _make_agent(session, mock_graph)

        agent.run("Génère un post Facebook", "{}")

        assert repo.find_by_thread_id("any-thread-id") is None

    def test_save_not_called_when_graph_fails(self, session):
        failing_graph = MagicMock()
        failing_graph.invoke.side_effect = Exception("graph error")
        agent, repo = _make_agent(session, failing_graph)

        agent.run("Génère un post Facebook", "{}")

        assert repo.find_by_thread_id("any-thread-id") is None

    def test_payload_persisted_when_graph_suspends(self, session, mock_graph_suspends):
        """final_result est persisté comme payload dans la DB à la suspension."""
        agent, repo = _make_agent(session, mock_graph_suspends)

        raw = agent.run("Génère un post Facebook", "{}")
        thread_id = json.loads(raw)["data"]["thread_id"]
        publication = repo.find_by_thread_id(thread_id)

        assert publication.payload == _FINAL_RESULT

    def test_payload_none_when_graph_has_no_final_result(self, session):
        """Payload est None si le graph suspend sans final_result (cas dégradé)."""
        graph = MagicMock()
        graph.invoke.return_value = {"__interrupt__": ["Waiting for approval"]}
        agent, repo = _make_agent(session, graph)

        raw = agent.run("Génère un post Facebook", "{}")
        thread_id = json.loads(raw)["data"]["thread_id"]
        publication = repo.find_by_thread_id(thread_id)

        assert publication.payload is None


class TestResumeUpdatesApprovalStatus:
    def test_resume_updates_approval_status_to_approved(self, session, mock_graph):
        agent, repo = _make_agent(session, mock_graph)
        repo.save("thread-abc", status="draft", approval_status="pending")

        agent.resume("thread-abc", "approved")

        publication = repo.find_by_thread_id("thread-abc")
        assert publication.approval_status == "approved"

    def test_resume_injects_payload_into_graph_checkpoint(self, session, mock_graph):
        """update_state est appelé avec le payload DB avant le resume du graph.

        On vérifie le thread_id dans le configurable et le payload : ce sont les
        deux invariants métier. Les champs observability (metadata, tags) sont
        testés dans tests/application/observability/.
        """
        agent, repo = _make_agent(session, mock_graph)
        repo.save("thread-pay", status="draft", approval_status="pending", payload=_FINAL_RESULT)

        agent.resume("thread-pay", "approved")

        call = mock_graph.update_state.call_args
        assert call is not None, "update_state doit être appelé"
        config_arg, payload_arg = call[0]
        assert config_arg["configurable"]["thread_id"] == "thread-pay"
        assert payload_arg == {"final_result": _FINAL_RESULT}

    def test_resume_skips_update_state_when_payload_is_none(self, session, mock_graph):
        """update_state n'est pas appelé si la publication n'a pas de payload."""
        agent, repo = _make_agent(session, mock_graph)
        repo.save("thread-nopay", status="draft", approval_status="pending")

        agent.resume("thread-nopay", "approved")

        mock_graph.update_state.assert_not_called()

    def test_resume_updates_approval_status_to_rejected(self, session, mock_graph):
        agent, repo = _make_agent(session, mock_graph)
        repo.save("thread-abc", status="draft", approval_status="pending")

        agent.resume("thread-abc", "rejected")

        publication = repo.find_by_thread_id("thread-abc")
        assert publication.approval_status == "rejected"

    def test_resume_uses_dynamic_thread_id(self, session, mock_graph):
        agent, repo = _make_agent(session, mock_graph)
        repo.save("thread-one", status="draft", approval_status="pending")
        repo.save("thread-two", status="draft", approval_status="pending")

        agent.resume("thread-one", "approved")

        assert repo.find_by_thread_id("thread-one").approval_status == "approved"
        assert repo.find_by_thread_id("thread-two").approval_status == "pending"


class TestAgentWithoutRepository:
    def test_run_without_repository_does_not_raise(self, mock_graph):
        with patch("app.application.agents.social_media_agent.build_social_media_graph") as mock_build:
            mock_build.return_value = mock_graph
            agent = SocialMediaAgent()

        result = agent.run("Génère un post Facebook", "{}")

        assert result is not None

    def test_resume_without_repository_does_not_raise(self, mock_graph):
        with patch("app.application.agents.social_media_agent.build_social_media_graph") as mock_build:
            mock_build.return_value = mock_graph
            agent = SocialMediaAgent()

        result = agent.resume("thread-abc", "approved")

        assert result is not None
