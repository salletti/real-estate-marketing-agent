"""Tests du module observability/langsmith.

Pédagogique :
- init_tracing() positionne (ou non) des env vars selon la config.
- build_run_config() construit un config LangGraph avec correlation ID.
- Aucun appel réseau réel vers LangSmith — tests purement unitaires.
"""
import os
from unittest.mock import patch

import pytest

from app.application.observability.langsmith import build_run_config, init_tracing


# ---------------------------------------------------------------------------
# TestTracingInit — init_tracing() active/désactive proprement
# ---------------------------------------------------------------------------

class TestTracingInit:

    def test_no_tracing_without_api_key(self, monkeypatch):
        """Sans clé API, aucune env var LangSmith n'est positionnée."""
        monkeypatch.delenv("LANGCHAIN_TRACING_V2", raising=False)
        monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)

        with patch("app.application.observability.langsmith.settings") as mock_settings:
            mock_settings.langchain_tracing_v2 = True
            mock_settings.langchain_api_key = None
            mock_settings.langchain_project = "test-project"
            init_tracing()

        assert "LANGCHAIN_TRACING_V2" not in os.environ
        assert "LANGCHAIN_API_KEY" not in os.environ

    def test_no_tracing_when_disabled(self, monkeypatch):
        """tracing_v2=False → aucune env var, même si la clé est présente."""
        monkeypatch.delenv("LANGCHAIN_TRACING_V2", raising=False)
        monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)

        with patch("app.application.observability.langsmith.settings") as mock_settings:
            mock_settings.langchain_tracing_v2 = False
            mock_settings.langchain_api_key = "lsv2_test_key"
            mock_settings.langchain_project = "test-project"
            init_tracing()

        assert "LANGCHAIN_TRACING_V2" not in os.environ
        assert "LANGCHAIN_API_KEY" not in os.environ

    def test_tracing_enabled_sets_env_vars(self, monkeypatch):
        """tracing_v2=True + clé présente → env vars correctement positionnées."""
        monkeypatch.delenv("LANGCHAIN_TRACING_V2", raising=False)
        monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)
        monkeypatch.delenv("LANGCHAIN_PROJECT", raising=False)

        with patch("app.application.observability.langsmith.settings") as mock_settings:
            mock_settings.langchain_tracing_v2 = True
            mock_settings.langchain_api_key = "lsv2_test_key_abc"
            mock_settings.langchain_project = "real-estate-marketing-agent"
            init_tracing()

        assert os.environ.get("LANGCHAIN_TRACING_V2") == "true"
        assert os.environ.get("LANGCHAIN_API_KEY") == "lsv2_test_key_abc"
        assert os.environ.get("LANGCHAIN_PROJECT") == "real-estate-marketing-agent"

        # Nettoyage explicite
        monkeypatch.delenv("LANGCHAIN_TRACING_V2", raising=False)
        monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)
        monkeypatch.delenv("LANGCHAIN_PROJECT", raising=False)

    def test_no_exception_without_key(self):
        """Sans configuration, init_tracing() ne lève aucune exception."""
        with patch("app.application.observability.langsmith.settings") as mock_settings:
            mock_settings.langchain_tracing_v2 = False
            mock_settings.langchain_api_key = None
            mock_settings.langchain_project = "test"
            init_tracing()  # doit passer sans erreur


# ---------------------------------------------------------------------------
# TestBuildRunConfig — structure du config LangGraph
# ---------------------------------------------------------------------------

class TestBuildRunConfig:

    def test_configurable_contains_thread_id(self):
        config = build_run_config("thread-abc-123")
        assert config["configurable"]["thread_id"] == "thread-abc-123"

    def test_metadata_contains_thread_id(self):
        config = build_run_config("thread-abc-123")
        assert config["metadata"]["thread_id"] == "thread-abc-123"

    def test_metadata_contains_workflow(self):
        config = build_run_config("any-thread")
        assert config["metadata"]["workflow"] == "social_media"

    def test_metadata_contains_runtime(self):
        config = build_run_config("any-thread")
        assert "runtime" in config["metadata"]

    def test_tags_contain_langgraph(self):
        config = build_run_config("any-thread")
        assert "langgraph" in config["tags"]

    def test_tags_contain_social_media(self):
        config = build_run_config("any-thread")
        assert "social-media" in config["tags"]

    def test_tags_contain_runtime_tag(self):
        config = build_run_config("any-thread")
        runtime_tags = [t for t in config["tags"] if t.startswith("runtime:")]
        assert len(runtime_tags) == 1

    def test_two_configs_are_independent(self):
        """Deux thread_ids distincts → deux configs indépendantes."""
        config_a = build_run_config("thread-A")
        config_b = build_run_config("thread-B")
        assert config_a["configurable"]["thread_id"] != config_b["configurable"]["thread_id"]
        assert config_a["metadata"]["thread_id"] != config_b["metadata"]["thread_id"]


# ---------------------------------------------------------------------------
# TestRuntimeContinuity — cohérence du correlation ID run/resume
# ---------------------------------------------------------------------------

class TestRuntimeContinuity:

    def test_run_and_resume_share_thread_id(self):
        """run() et resume() sur le même thread_id produisent le même configurable.

        C'est la garantie de continuité dans LangSmith : toutes les spans
        (exécution initiale + interrupt + resume) sont regroupées sous le même
        thread_id dans l'UI — exactement comme un trace_id en OpenTelemetry.
        """
        thread_id = "workflow-continuity-test"
        config_run = build_run_config(thread_id)
        config_resume = build_run_config(thread_id)

        assert config_run["configurable"]["thread_id"] == thread_id
        assert config_resume["configurable"]["thread_id"] == thread_id
        assert config_run["configurable"] == config_resume["configurable"]

    def test_run_and_resume_have_same_metadata_thread_id(self):
        thread_id = "workflow-continuity-test"
        config_run = build_run_config(thread_id)
        config_resume = build_run_config(thread_id)
        assert config_run["metadata"]["thread_id"] == config_resume["metadata"]["thread_id"]
