import json
import logging
import time

from langsmith.wrappers import wrap_openai
from openai import OpenAI

from config import settings

logger = logging.getLogger(__name__)

_PROVIDER = "groq"
_TEMPERATURE = 0.2
_CONTENT_MAX_CHARS = 300


class LLMClient:

    def __init__(self):
        raw_client = OpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        self._client = wrap_openai(raw_client)
        self._model = settings.llm_model

    def generate(self, prompt: str) -> str:
        t0 = time.perf_counter()
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=_TEMPERATURE,
            )
            content = response.choices[0].message.content or ""
        except Exception as exc:
            duration_ms = round((time.perf_counter() - t0) * 1000)
            if settings.llm_logging_enabled:
                logger.error(json.dumps({
                    "event": "llm_call_error",
                    "model": self._model,
                    "provider": _PROVIDER,
                    "duration_ms": duration_ms,
                    "error": str(exc),
                }))
            raise

        duration_ms = round((time.perf_counter() - t0) * 1000)
        if settings.llm_logging_enabled:
            extra: dict = {
                "event": "llm_call_success",
                "model": self._model,
                "provider": _PROVIDER,
                "duration_ms": duration_ms,
                "prompt_chars": len(prompt),
                "response_chars": len(content),
            }
            if settings.llm_logging_include_content:
                extra["prompt_excerpt"] = prompt[:_CONTENT_MAX_CHARS]
                extra["response_excerpt"] = content[:_CONTENT_MAX_CHARS]
            logger.info(json.dumps(extra))

        return content
