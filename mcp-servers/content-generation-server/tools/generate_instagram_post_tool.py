import json
import logging
from typing import Any, Dict, List

from mappers.property_mapper import PropertyMapper
from services.generate_instagram_post_service import GenerateInstagramPostService

logger = logging.getLogger(__name__)

_FALLBACK_DATA: Dict[str, Any] = {"caption": "", "hashtags": []}
_service = GenerateInstagramPostService()


def handle_generate_instagram_post(property_json: str, thread_id: str = "") -> str:
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
        logger.error(json.dumps({"event": "tool_error", "tool": "generate_instagram_post",
                                  "thread_id": thread_id, "error": str(exc)}))
        return _error("llm_generation_failed", thread_id)

    if not isinstance(result, dict) or not all(k in result for k in ("caption", "hashtags")):
        return _error("incomplete_llm_response", thread_id)

    result["caption"] = str(result.get("caption", ""))[:500]
    result["hashtags"] = _normalize_hashtags(result.get("hashtags"))

    logger.info(json.dumps({"event": "tool_executed", "tool": "generate_instagram_post",
                             "thread_id": thread_id, "success": True}))
    return json.dumps({"success": True, "error": None, "data": result}, ensure_ascii=False)


def _normalize_hashtags(raw: Any) -> List[str]:
    if not isinstance(raw, list):
        return []
    tags = [t for t in raw if isinstance(t, str)]
    tags = [t if t.startswith("#") else f"#{t}" for t in tags]
    return tags[:12]


def _error(reason: str, thread_id: str) -> str:
    logger.warning(json.dumps({"event": "tool_error", "tool": "generate_instagram_post",
                                "thread_id": thread_id, "error": reason}))
    return json.dumps({"success": False, "error": reason, "data": _FALLBACK_DATA},
                      ensure_ascii=False)
