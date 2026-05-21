from unittest.mock import MagicMock, patch

import pytest

from app.infrastructure.llm.llm_client import LLMClient


@pytest.fixture
def llm_and_create():
    """Yields (LLMClient instance, create mock) with OpenAI patched."""
    with patch("app.infrastructure.llm.llm_client.OpenAI") as mock_openai:
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "réponse LLM"
        create = mock_openai.return_value.chat.completions.create
        create.return_value = mock_response
        yield LLMClient(), create, mock_response


# ---------------------------------------------------------------------------
# API existante — comportement inchangé
# ---------------------------------------------------------------------------

class TestLLMClientGenerate:

    def test_returns_message_content(self, llm_and_create):
        client, create, response = llm_and_create
        response.choices[0].message.content = "résultat"
        assert client.generate("prompt") == "résultat"

    def test_returns_empty_string_when_content_is_none(self, llm_and_create):
        client, create, response = llm_and_create
        response.choices[0].message.content = None
        assert client.generate("prompt") == ""

    def test_uses_temperature_0_2(self, llm_and_create):
        client, create, _ = llm_and_create
        client.generate("prompt")
        assert create.call_args.kwargs["temperature"] == 0.2

    def test_passes_prompt_as_user_message(self, llm_and_create):
        client, create, _ = llm_and_create
        client.generate("mon prompt")
        assert create.call_args.kwargs["messages"] == [
            {"role": "user", "content": "mon prompt"}
        ]

    def test_called_once_per_generate(self, llm_and_create):
        client, create, _ = llm_and_create
        client.generate("prompt")
        create.assert_called_once()


# ---------------------------------------------------------------------------
# Journalisation succès
# ---------------------------------------------------------------------------

class TestLLMLoggingSuccess:

    def test_logs_info_on_success(self, llm_and_create):
        client, _, _ = llm_and_create
        with patch("app.infrastructure.llm.llm_client.settings") as s, \
             patch("app.infrastructure.llm.llm_client.logger") as mock_logger:
            s.llm_logging_enabled = True
            s.llm_logging_include_content = False
            client.generate("un prompt")
        mock_logger.info.assert_called_once()
        event = mock_logger.info.call_args[0][0]
        assert event == "llm_call_success"

    def test_log_contains_required_fields(self, llm_and_create):
        client, _, _ = llm_and_create
        with patch("app.infrastructure.llm.llm_client.settings") as s, \
             patch("app.infrastructure.llm.llm_client.logger") as mock_logger:
            s.llm_logging_enabled = True
            s.llm_logging_include_content = False
            client.generate("un prompt de test")
        extra = mock_logger.info.call_args.kwargs["extra"]
        assert "model" in extra
        assert "provider" in extra
        assert extra["provider"] == "groq"
        assert "temperature" in extra
        assert extra["temperature"] == 0.2
        assert "duration_ms" in extra
        assert isinstance(extra["duration_ms"], int)
        assert "prompt_chars" in extra
        assert extra["prompt_chars"] == len("un prompt de test")
        assert "response_chars" in extra

    def test_no_log_when_disabled(self, llm_and_create):
        client, _, _ = llm_and_create
        with patch("app.infrastructure.llm.llm_client.settings") as s, \
             patch("app.infrastructure.llm.llm_client.logger") as mock_logger:
            s.llm_logging_enabled = False
            s.llm_logging_include_content = False
            client.generate("prompt")
        mock_logger.info.assert_not_called()


# ---------------------------------------------------------------------------
# Confidentialité — pas de contenu complet par défaut
# ---------------------------------------------------------------------------

class TestLLMLoggingPrivacy:

    def test_no_content_logged_by_default(self, llm_and_create):
        client, _, response = llm_and_create
        response.choices[0].message.content = "réponse complète"
        with patch("app.infrastructure.llm.llm_client.settings") as s, \
             patch("app.infrastructure.llm.llm_client.logger") as mock_logger:
            s.llm_logging_enabled = True
            s.llm_logging_include_content = False
            client.generate("prompt complet")
        extra = mock_logger.info.call_args.kwargs["extra"]
        assert "prompt_excerpt" not in extra
        assert "response_excerpt" not in extra

    def test_excerpt_logged_when_include_content_enabled(self, llm_and_create):
        client, _, response = llm_and_create
        long_prompt = "x" * 500
        long_response = "y" * 500
        response.choices[0].message.content = long_response
        with patch("app.infrastructure.llm.llm_client.settings") as s, \
             patch("app.infrastructure.llm.llm_client.logger") as mock_logger:
            s.llm_logging_enabled = True
            s.llm_logging_include_content = True
            client.generate(long_prompt)
        extra = mock_logger.info.call_args.kwargs["extra"]
        assert extra["prompt_excerpt"] == "x" * 300
        assert extra["response_excerpt"] == "y" * 300

    def test_excerpt_not_truncated_when_short(self, llm_and_create):
        client, _, response = llm_and_create
        response.choices[0].message.content = "court"
        with patch("app.infrastructure.llm.llm_client.settings") as s, \
             patch("app.infrastructure.llm.llm_client.logger") as mock_logger:
            s.llm_logging_enabled = True
            s.llm_logging_include_content = True
            client.generate("bref")
        extra = mock_logger.info.call_args.kwargs["extra"]
        assert extra["prompt_excerpt"] == "bref"
        assert extra["response_excerpt"] == "court"


# ---------------------------------------------------------------------------
# Journalisation erreur
# ---------------------------------------------------------------------------

class TestLLMLoggingError:

    def test_logs_error_on_exception(self, llm_and_create):
        client, create, _ = llm_and_create
        create.side_effect = RuntimeError("timeout")
        with patch("app.infrastructure.llm.llm_client.settings") as s, \
             patch("app.infrastructure.llm.llm_client.logger") as mock_logger:
            s.llm_logging_enabled = True
            s.llm_logging_include_content = False
            with pytest.raises(RuntimeError):
                client.generate("prompt")
        mock_logger.error.assert_called_once()
        event = mock_logger.error.call_args[0][0]
        assert event == "llm_call_error"

    def test_error_log_contains_error_field(self, llm_and_create):
        client, create, _ = llm_and_create
        create.side_effect = RuntimeError("timeout")
        with patch("app.infrastructure.llm.llm_client.settings") as s, \
             patch("app.infrastructure.llm.llm_client.logger") as mock_logger:
            s.llm_logging_enabled = True
            s.llm_logging_include_content = False
            with pytest.raises(RuntimeError):
                client.generate("prompt")
        extra = mock_logger.error.call_args.kwargs["extra"]
        assert extra["error"] == "timeout"
        assert "duration_ms" in extra
        assert "prompt_chars" in extra

    def test_exception_reraised_after_logging(self, llm_and_create):
        client, create, _ = llm_and_create
        create.side_effect = ValueError("bad request")
        with patch("app.infrastructure.llm.llm_client.settings") as s:
            s.llm_logging_enabled = True
            s.llm_logging_include_content = False
            with pytest.raises(ValueError, match="bad request"):
                client.generate("prompt")

    def test_no_error_log_when_disabled(self, llm_and_create):
        client, create, _ = llm_and_create
        create.side_effect = RuntimeError("timeout")
        with patch("app.infrastructure.llm.llm_client.settings") as s, \
             patch("app.infrastructure.llm.llm_client.logger") as mock_logger:
            s.llm_logging_enabled = False
            s.llm_logging_include_content = False
            with pytest.raises(RuntimeError):
                client.generate("prompt")
        mock_logger.error.assert_not_called()
