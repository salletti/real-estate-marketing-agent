import json
import logging
from typing import Any, Dict, List

from observability.logger import log_tool_call, log_tool_error
from services.publish_facebook_service import PublishFacebookService

logger = logging.getLogger(__name__)

_FALLBACK_DATA: Dict[str, Any] = {"platform": "facebook", "status": "failed"}
_service = PublishFacebookService()


def handle_publish_facebook(post: str, images: List[str], thread_id: str = "") -> str:
    log_tool_call("facebook", thread_id)

    if not post or not isinstance(post, str):
        return _error("missing_or_invalid_post", thread_id)

    if not isinstance(images, list) or not all(isinstance(i, str) for i in images):
        return _error("invalid_images_format", thread_id)

    try:
        result = _service.publish(post=post, images=images, thread_id=thread_id)
    except Exception as exc:
        logger.error(json.dumps({
            "event": "tool_error",
            "tool": "publish_facebook",
            "thread_id": thread_id,
            "error": str(exc),
        }))
        return _error("publish_failed", thread_id)

    return json.dumps({"success": True, "error": None, "data": result}, ensure_ascii=False)


def _error(reason: str, thread_id: str) -> str:
    log_tool_error("facebook", thread_id, reason)
    return json.dumps(
        {"success": False, "error": reason, "data": _FALLBACK_DATA},
        ensure_ascii=False,
    )
