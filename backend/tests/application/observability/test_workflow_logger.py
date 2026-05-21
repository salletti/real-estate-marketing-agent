"""Tests du structured workflow logging.

Pédagogique :
- WorkflowLogger émet des JSON valides via le module logging standard Python.
- RuntimeContext centralise les metadata de corrélation (thread_id, workflow, provider).
- On capture les logs avec caplog (pytest) — aucun appel réseau, 100 % unitaire.
- On vérifie la STRUCTURE et la PRÉSENCE des metadata, pas le contenu exact des chaînes.
"""
import json
import logging

import pytest

from app.application.observability.runtime_context import RuntimeContext
from app.application.observability.workflow_logger import WorkflowLogger


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------

def _make_logger(thread_id: str = "test-thread-42") -> WorkflowLogger:
    ctx = RuntimeContext(thread_id=thread_id, runtime_provider="memory")
    return WorkflowLogger(ctx)


def _last_record(caplog) -> dict:
    """Retourne le dernier log parsé en JSON."""
    return json.loads(caplog.records[-1].getMessage())


# ---------------------------------------------------------------------------
# TestRuntimeContext — corrélation metadata
# ---------------------------------------------------------------------------

class TestRuntimeContext:

    def test_thread_id_stored(self):
        ctx = RuntimeContext(thread_id="abc-123")
        assert ctx.thread_id == "abc-123"

    def test_default_workflow_name(self):
        ctx = RuntimeContext(thread_id="x")
        assert ctx.workflow == "social_media"

    def test_as_dict_contains_required_keys(self):
        ctx = RuntimeContext(thread_id="x", runtime_provider="memory")
        d = ctx.as_dict()
        assert "thread_id" in d
        assert "workflow" in d
        assert "runtime_provider" in d

    def test_as_dict_propagates_thread_id(self):
        ctx = RuntimeContext(thread_id="my-thread", runtime_provider="redis")
        assert ctx.as_dict()["thread_id"] == "my-thread"

    def test_as_dict_propagates_runtime_provider(self):
        ctx = RuntimeContext(thread_id="x", runtime_provider="redis")
        assert ctx.as_dict()["runtime_provider"] == "redis"

    def test_custom_workflow_name(self):
        ctx = RuntimeContext(thread_id="x", workflow="email_campaign")
        assert ctx.workflow == "email_campaign"


# ---------------------------------------------------------------------------
# TestWorkflowLoggerFormat — chaque log est un JSON valide et complet
# ---------------------------------------------------------------------------

class TestWorkflowLoggerFormat:

    def test_log_is_valid_json(self, caplog):
        wl = _make_logger()
        with caplog.at_level(logging.INFO):
            wl.log_workflow_started()
        record_text = caplog.records[-1].getMessage()
        parsed = json.loads(record_text)  # lève ValueError si pas JSON valide
        assert isinstance(parsed, dict)

    def test_event_field_present(self, caplog):
        wl = _make_logger()
        with caplog.at_level(logging.INFO):
            wl.log_workflow_started()
        assert _last_record(caplog)["event"] == "workflow_started"

    def test_thread_id_propagated(self, caplog):
        wl = _make_logger(thread_id="unique-thread-99")
        with caplog.at_level(logging.INFO):
            wl.log_workflow_started()
        assert _last_record(caplog)["thread_id"] == "unique-thread-99"

    def test_workflow_field_present(self, caplog):
        wl = _make_logger()
        with caplog.at_level(logging.INFO):
            wl.log_workflow_started()
        assert _last_record(caplog)["workflow"] == "social_media"

    def test_runtime_provider_field_present(self, caplog):
        wl = _make_logger()
        with caplog.at_level(logging.INFO):
            wl.log_workflow_started()
        assert "runtime_provider" in _last_record(caplog)


# ---------------------------------------------------------------------------
# TestWorkflowLoggerEvents — chaque méthode émet le bon event
# ---------------------------------------------------------------------------

class TestWorkflowLoggerEvents:

    def test_workflow_started(self, caplog):
        wl = _make_logger()
        with caplog.at_level(logging.INFO):
            wl.log_workflow_started()
        assert _last_record(caplog)["event"] == "workflow_started"

    def test_node_started(self, caplog):
        wl = _make_logger()
        with caplog.at_level(logging.INFO):
            wl.log_node_started("generate_facebook_node")
        record = _last_record(caplog)
        assert record["event"] == "node_started"
        assert record["node"] == "generate_facebook_node"

    def test_node_started_returns_float(self):
        """log_node_started() retourne un timestamp pour calculer la durée."""
        wl = _make_logger()
        result = wl.log_node_started("some_node")
        assert isinstance(result, float)
        assert result > 0

    def test_node_completed(self, caplog):
        wl = _make_logger()
        with caplog.at_level(logging.INFO):
            started_at = wl.log_node_started("generate_facebook_node")
            wl.log_node_completed("generate_facebook_node", started_at)
        record = _last_record(caplog)
        assert record["event"] == "node_completed"
        assert record["node"] == "generate_facebook_node"

    def test_node_completed_has_duration_ms(self, caplog):
        """duration_ms doit être présent et >= 0."""
        wl = _make_logger()
        with caplog.at_level(logging.INFO):
            started_at = wl.log_node_started("my_node")
            wl.log_node_completed("my_node", started_at)
        record = _last_record(caplog)
        assert "duration_ms" in record
        assert record["duration_ms"] >= 0

    def test_workflow_interrupted(self, caplog):
        wl = _make_logger()
        with caplog.at_level(logging.INFO):
            wl.log_interrupt()
        assert _last_record(caplog)["event"] == "workflow_interrupted"

    def test_workflow_resumed_with_approval(self, caplog):
        wl = _make_logger()
        with caplog.at_level(logging.INFO):
            wl.log_resume("approved")
        record = _last_record(caplog)
        assert record["event"] == "workflow_resumed"
        assert record["approval"] == "approved"

    def test_workflow_resumed_rejected(self, caplog):
        wl = _make_logger()
        with caplog.at_level(logging.INFO):
            wl.log_resume("rejected")
        assert _last_record(caplog)["approval"] == "rejected"

    def test_workflow_recovered(self, caplog):
        wl = _make_logger()
        with caplog.at_level(logging.INFO):
            wl.log_workflow_recovered()
        assert _last_record(caplog)["event"] == "workflow_recovered"

    def test_node_error(self, caplog):
        wl = _make_logger()
        with caplog.at_level(logging.INFO):
            wl.log_error("generate_facebook_node", "timeout")
        record = _last_record(caplog)
        assert record["event"] == "node_error"
        assert record["node"] == "generate_facebook_node"
        assert record["error"] == "timeout"


# ---------------------------------------------------------------------------
# TestContextPropagation — thread_id cohérent à travers plusieurs events
# ---------------------------------------------------------------------------

class TestContextPropagation:

    def test_thread_id_stable_across_events(self, caplog):
        """Le même thread_id apparaît dans tous les events d'une exécution."""
        wl = _make_logger(thread_id="stable-thread")
        with caplog.at_level(logging.INFO):
            wl.log_workflow_started()
            wl.log_node_started("node_a")
            wl.log_interrupt()

        records = [json.loads(r.getMessage()) for r in caplog.records]
        thread_ids = {r["thread_id"] for r in records}
        assert thread_ids == {"stable-thread"}

    def test_two_contexts_are_independent(self, caplog):
        """Deux WorkflowLogger avec des thread_ids distincts n'interfèrent pas."""
        wl_a = WorkflowLogger(RuntimeContext(thread_id="thread-A", runtime_provider="memory"))
        wl_b = WorkflowLogger(RuntimeContext(thread_id="thread-B", runtime_provider="memory"))

        with caplog.at_level(logging.INFO):
            wl_a.log_workflow_started()
            wl_b.log_workflow_started()

        records = [json.loads(r.getMessage()) for r in caplog.records[-2:]]
        assert records[0]["thread_id"] == "thread-A"
        assert records[1]["thread_id"] == "thread-B"
