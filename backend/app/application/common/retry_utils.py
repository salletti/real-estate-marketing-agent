import json
import logging
from typing import Callable


def retry_operation(
    operation: Callable[[], str],
    *,
    max_attempts: int = 3,
    logger: logging.Logger,
    operation_name: str,
) -> dict:
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            raw = operation()
            return json.loads(raw)
        except Exception as exc:
            last_error = exc
            logger.warning(
                "Attempt %d/%d failed for %s: %s",
                attempt, max_attempts, operation_name, exc,
            )

    logger.error(
        "All %d attempts failed for %s: %s",
        max_attempts, operation_name, last_error,
    )
    return {
        "success": False,
        "error": "node_execution_failed",
        "data": {"attempts": max_attempts, "operation": operation_name},
    }
