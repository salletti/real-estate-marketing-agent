import json
import logging

logger = logging.getLogger(__name__)


def log_tool_call(platform: str, thread_id: str) -> None:
    logger.info(json.dumps({
        "event": "mcp_publish_call",
        "platform": platform,
        "thread_id": thread_id,
    }))


def log_tool_success(platform: str, thread_id: str) -> None:
    logger.info(json.dumps({
        "event": "publication_mock_executed",
        "platform": platform,
        "thread_id": thread_id,
    }))


def log_tool_error(platform: str, thread_id: str, error: str) -> None:
    logger.warning(json.dumps({
        "event": "publication_error",
        "platform": platform,
        "thread_id": thread_id,
        "error": error,
    }))
