import json
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.api.links.draft.draft_links_builder import DraftLinksBuilder, get_draft_links_builder
from app.infrastructure.db.session import get_db
from app.main import app

_THREAD_ID = "abc-123-uuid"

_AGENT_DRAFT_RESPONSE = json.dumps({
    "success": True,
    "error": None,
    "data": {
        "thread_id": _THREAD_ID,
        "status": "draft",
        "approval_status": "pending",
    },
})

_MOCK_PUBLICATION = MagicMock()
_MOCK_PUBLICATION.thread_id = _THREAD_ID
_MOCK_PUBLICATION.status = "draft"
_MOCK_PUBLICATION.approval_status = "pending"
_MOCK_PUBLICATION.payload = {"platforms": {"facebook": {"post": "test"}}}

_MOCK_PUBLICATION_GENERATION_FAILED = MagicMock()
_MOCK_PUBLICATION_GENERATION_FAILED.thread_id = _THREAD_ID
_MOCK_PUBLICATION_GENERATION_FAILED.status = "draft"
_MOCK_PUBLICATION_GENERATION_FAILED.approval_status = "pending"
_MOCK_PUBLICATION_GENERATION_FAILED.payload = {
    "success": False,
    "error": "no_platform_generated",
    "data": {},
}

_MOCK_PUBLICATION_REJECTED = MagicMock()
_MOCK_PUBLICATION_REJECTED.thread_id = _THREAD_ID
_MOCK_PUBLICATION_REJECTED.status = "draft"
_MOCK_PUBLICATION_REJECTED.approval_status = "rejected"
_MOCK_PUBLICATION_REJECTED.payload = {"platforms": {"facebook": {"post": "test"}}}

_MOCK_PUBLICATION_PUBLISHED = MagicMock()
_MOCK_PUBLICATION_PUBLISHED.thread_id = _THREAD_ID
_MOCK_PUBLICATION_PUBLISHED.status = "published"
_MOCK_PUBLICATION_PUBLISHED.approval_status = "approved"
_MOCK_PUBLICATION_PUBLISHED.payload = {"platforms": {"facebook": {"post": "test"}}}

_VALID_PAYLOAD = {
    "input": "Génère un post Facebook",
    "property_json": {},
}


def _mock_db():
    yield MagicMock()


def _empty_links_builder():
    return DraftLinksBuilder(links=[])


app.dependency_overrides[get_db] = _mock_db
app.dependency_overrides[get_draft_links_builder] = _empty_links_builder
client = TestClient(app)


class TestGenerateDraft:

    def test_returns_201(self):
        with patch("app.api.drafts.draft_routes.SocialMediaAgent") as MockAgent, \
             patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo:
            MockAgent.return_value.run.return_value = _AGENT_DRAFT_RESPONSE
            MockRepo.return_value.find_by_thread_id.return_value = _MOCK_PUBLICATION
            response = client.post("/drafts/generate", json=_VALID_PAYLOAD)
        assert response.status_code == 201

    def test_thread_id_correctly_returned(self):
        with patch("app.api.drafts.draft_routes.SocialMediaAgent") as MockAgent, \
             patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo:
            MockAgent.return_value.run.return_value = _AGENT_DRAFT_RESPONSE
            MockRepo.return_value.find_by_thread_id.return_value = _MOCK_PUBLICATION
            response = client.post("/drafts/generate", json=_VALID_PAYLOAD)
        assert response.json()["thread_id"] == _THREAD_ID

    def test_approval_status_correctly_returned(self):
        with patch("app.api.drafts.draft_routes.SocialMediaAgent") as MockAgent, \
             patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo:
            MockAgent.return_value.run.return_value = _AGENT_DRAFT_RESPONSE
            MockRepo.return_value.find_by_thread_id.return_value = _MOCK_PUBLICATION
            response = client.post("/drafts/generate", json=_VALID_PAYLOAD)
        body = response.json()
        assert body["status"] == "draft"
        assert body["approval_status"] == "pending"

    def test_response_keys(self):
        with patch("app.api.drafts.draft_routes.SocialMediaAgent") as MockAgent, \
             patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo:
            MockAgent.return_value.run.return_value = _AGENT_DRAFT_RESPONSE
            MockRepo.return_value.find_by_thread_id.return_value = _MOCK_PUBLICATION
            response = client.post("/drafts/generate", json=_VALID_PAYLOAD)
        assert set(response.json().keys()) == {"thread_id", "status", "approval_status", "content", "_links"}

    def test_missing_content_returns_500(self):
        with patch("app.api.drafts.draft_routes.SocialMediaAgent") as MockAgent, \
             patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo:
            MockAgent.return_value.run.return_value = _AGENT_DRAFT_RESPONSE
            empty_payload_publication = MagicMock(
                thread_id=_THREAD_ID, status="draft", approval_status="pending", payload=None
            )
            MockRepo.return_value.find_by_thread_id.return_value = empty_payload_publication
            response = client.post("/drafts/generate", json=_VALID_PAYLOAD)
        assert response.status_code == 500
        assert response.json()["detail"] == "draft_content_missing"

    def test_generation_failure_returns_502(self):
        with patch("app.api.drafts.draft_routes.SocialMediaAgent") as MockAgent, \
             patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo:
            MockAgent.return_value.run.return_value = _AGENT_DRAFT_RESPONSE
            MockRepo.return_value.find_by_thread_id.return_value = _MOCK_PUBLICATION_GENERATION_FAILED
            response = client.post("/drafts/generate", json=_VALID_PAYLOAD)
        assert response.status_code == 502
        assert response.json()["detail"]["error"] == "no_platform_generated"

    def test_missing_input_returns_422(self):
        response = client.post("/drafts/generate", json={"property_json": "{}"})
        assert response.status_code == 422

    def test_missing_property_json_returns_422(self):
        response = client.post("/drafts/generate", json={"input": "test"})
        assert response.status_code == 422


class TestGetDraft:

    def test_returns_200(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo:
            MockRepo.return_value.find_by_thread_id.return_value = _MOCK_PUBLICATION
            response = client.get(f"/drafts/{_THREAD_ID}")
        assert response.status_code == 200

    def test_thread_id_correctly_returned(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo:
            MockRepo.return_value.find_by_thread_id.return_value = _MOCK_PUBLICATION
            response = client.get(f"/drafts/{_THREAD_ID}")
        assert response.json()["thread_id"] == _THREAD_ID

    def test_approval_status_correctly_returned(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo:
            MockRepo.return_value.find_by_thread_id.return_value = _MOCK_PUBLICATION
            response = client.get(f"/drafts/{_THREAD_ID}")
        body = response.json()
        assert body["status"] == "draft"
        assert body["approval_status"] == "pending"

    def test_unknown_thread_id_returns_404(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo:
            MockRepo.return_value.find_by_thread_id.return_value = None
            response = client.get("/drafts/inexistant")
        assert response.status_code == 404

    def test_rejected_draft_remains_persisted(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo:
            MockRepo.return_value.find_by_thread_id.return_value = _MOCK_PUBLICATION_REJECTED
            response = client.get(f"/drafts/{_THREAD_ID}")
        assert response.status_code == 200
        assert response.json()["approval_status"] == "rejected"


class TestPublishDraft:

    def test_publish_returns_200(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo, \
             patch("app.api.drafts.draft_routes.SocialMediaAgent"):
            MockRepo.return_value.find_by_thread_id.side_effect = [
                _MOCK_PUBLICATION, _MOCK_PUBLICATION_PUBLISHED
            ]
            response = client.post(f"/drafts/{_THREAD_ID}/publish")
        assert response.status_code == 200

    def test_publish_status_becomes_published(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo, \
             patch("app.api.drafts.draft_routes.SocialMediaAgent"):
            MockRepo.return_value.find_by_thread_id.side_effect = [
                _MOCK_PUBLICATION, _MOCK_PUBLICATION_PUBLISHED
            ]
            response = client.post(f"/drafts/{_THREAD_ID}/publish")
        assert response.json()["status"] == "published"

    def test_publish_approval_status_becomes_approved(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo, \
             patch("app.api.drafts.draft_routes.SocialMediaAgent"):
            MockRepo.return_value.find_by_thread_id.side_effect = [
                _MOCK_PUBLICATION, _MOCK_PUBLICATION_PUBLISHED
            ]
            response = client.post(f"/drafts/{_THREAD_ID}/publish")
        assert response.json()["approval_status"] == "approved"

    def test_publish_calls_resume_with_thread_id(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo, \
             patch("app.api.drafts.draft_routes.SocialMediaAgent") as MockAgent:
            MockRepo.return_value.find_by_thread_id.side_effect = [
                _MOCK_PUBLICATION, _MOCK_PUBLICATION_PUBLISHED
            ]
            client.post(f"/drafts/{_THREAD_ID}/publish")
        MockAgent.return_value.resume.assert_called_once_with(
            thread_id=_THREAD_ID, approval="approved"
        )

    def test_publish_unknown_thread_id_returns_404(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo:
            MockRepo.return_value.find_by_thread_id.return_value = None
            response = client.post("/drafts/inexistant/publish")
        assert response.status_code == 404

    def test_publish_already_published_returns_409(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo:
            MockRepo.return_value.find_by_thread_id.return_value = _MOCK_PUBLICATION_PUBLISHED
            response = client.post(f"/drafts/{_THREAD_ID}/publish")
        assert response.status_code == 409

    def test_publish_already_rejected_returns_409(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo:
            MockRepo.return_value.find_by_thread_id.return_value = _MOCK_PUBLICATION_REJECTED
            response = client.post(f"/drafts/{_THREAD_ID}/publish")
        assert response.status_code == 409


class TestRejectDraft:

    def test_reject_returns_200(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo, \
             patch("app.api.drafts.draft_routes.SocialMediaAgent"):
            MockRepo.return_value.find_by_thread_id.side_effect = [
                _MOCK_PUBLICATION, _MOCK_PUBLICATION_REJECTED
            ]
            response = client.post(f"/drafts/{_THREAD_ID}/reject")
        assert response.status_code == 200

    def test_reject_status_becomes_rejected(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo, \
             patch("app.api.drafts.draft_routes.SocialMediaAgent"):
            MockRepo.return_value.find_by_thread_id.side_effect = [
                _MOCK_PUBLICATION, _MOCK_PUBLICATION_REJECTED
            ]
            response = client.post(f"/drafts/{_THREAD_ID}/reject")
        assert response.json()["status"] == "draft"

    def test_reject_approval_status_becomes_rejected(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo, \
             patch("app.api.drafts.draft_routes.SocialMediaAgent"):
            MockRepo.return_value.find_by_thread_id.side_effect = [
                _MOCK_PUBLICATION, _MOCK_PUBLICATION_REJECTED
            ]
            response = client.post(f"/drafts/{_THREAD_ID}/reject")
        assert response.json()["approval_status"] == "rejected"

    def test_reject_calls_resume_with_rejected(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo, \
             patch("app.api.drafts.draft_routes.SocialMediaAgent") as MockAgent:
            MockRepo.return_value.find_by_thread_id.side_effect = [
                _MOCK_PUBLICATION, _MOCK_PUBLICATION_REJECTED
            ]
            client.post(f"/drafts/{_THREAD_ID}/reject")
        MockAgent.return_value.resume.assert_called_once_with(
            thread_id=_THREAD_ID, approval="rejected"
        )

    def test_reject_unknown_thread_id_returns_404(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo:
            MockRepo.return_value.find_by_thread_id.return_value = None
            response = client.post("/drafts/inexistant/reject")
        assert response.status_code == 404

    def test_reject_already_rejected_returns_409(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo:
            MockRepo.return_value.find_by_thread_id.return_value = _MOCK_PUBLICATION_REJECTED
            response = client.post(f"/drafts/{_THREAD_ID}/reject")
        assert response.status_code == 409

    def test_reject_already_published_returns_409(self):
        with patch("app.api.drafts.draft_routes.SocialMediaPublicationRepository") as MockRepo:
            MockRepo.return_value.find_by_thread_id.return_value = _MOCK_PUBLICATION_PUBLISHED
            response = client.post(f"/drafts/{_THREAD_ID}/reject")
        assert response.status_code == 409
