import json
import logging
from typing import Any, Dict, List

from observability.logger import log_tool_call, log_tool_error
from services.publish_instagram_service import PublishInstagramService

logger = logging.getLogger(__name__)

_FALLBACK_DATA: Dict[str, Any] = {"platform": "instagram", "status": "failed"}
_service = PublishInstagramService()


def handle_publish_instagram(caption: str, images: List[str], thread_id: str = "") -> str:
    log_tool_call("instagram", thread_id)

    if not caption or not isinstance(caption, str):
        return _error("missing_or_invalid_caption", thread_id)

    if not isinstance(images, list) or not all(isinstance(i, str) for i in images):
        return _error("invalid_images_format", thread_id)

    try:
        result = _service.publish(caption=caption, images=images, thread_id=thread_id)
    except Exception as exc:
        logger.error(json.dumps({
            "event": "tool_error",
            "tool": "publish_instagram",
            "thread_id": thread_id,
            "error": str(exc),
        }))
        return _error("publish_failed", thread_id)

    return json.dumps({"success": True, "error": None, "data": result}, ensure_ascii=False)


def _error(reason: str, thread_id: str) -> str:
    log_tool_error("instagram", thread_id, reason)
    return json.dumps(
        {"success": False, "error": reason, "data": _FALLBACK_DATA},
        ensure_ascii=False,
    )
