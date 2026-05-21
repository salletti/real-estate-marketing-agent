import json
import logging
from typing import Any, Dict

from mappers.property_mapper import PropertyMapper
from services.generate_facebook_post_service import GenerateFacebookPostService

logger = logging.getLogger(__name__)

_FALLBACK_DATA: Dict[str, Any] = {"post": "", "hashtags": []}
_service = GenerateFacebookPostService()


def handle_generate_facebook_post(property_json: str, thread_id: str = "") -> str:
    try:
        data = json.loads(property_json)
    except Exception:
        return _error("invalid_input_json", thread_id)

    try:
        property_ = PropertyMapper.from_raw(data)
    except Exception:
        return _error("mapping_failed", thread_id)

    try:
        result = _service.generate(property_)
    except Exception as exc:
        logger.error(json.dumps({"event": "tool_error", "tool": "generate_facebook_post",
                                  "thread_id": thread_id, "error": str(exc)}))
        return _error("llm_generation_failed", thread_id)

    if not isinstance(result, dict) or not all(k in result for k in ("post", "hashtags")):
        return _error("incomplete_llm_response", thread_id)

    if not isinstance(result["hashtags"], list):
        result["hashtags"] = []

    logger.info(json.dumps({"event": "tool_executed", "tool": "generate_facebook_post",
                             "thread_id": thread_id, "success": True}))
    return json.dumps({"success": True, "error": None, "data": result}, ensure_ascii=False)


def _error(reason: str, thread_id: str) -> str:
    logger.warning(json.dumps({"event": "tool_error", "tool": "generate_facebook_post",
                                "thread_id": thread_id, "error": reason}))
    return json.dumps({"success": False, "error": reason, "data": _FALLBACK_DATA},
                      ensure_ascii=False)
