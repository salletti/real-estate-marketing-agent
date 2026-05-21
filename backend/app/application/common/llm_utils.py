import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def bool_to_str(value: Optional[bool]) -> str:
    """Converts a nullable bool to a French string for prompt injection."""
    if value is True:
        return "oui"
    if value is False:
        return "non"
    return ""


def list_to_str(values: List[str]) -> str:
    """Joins a list of strings as a comma-separated value, or returns empty string."""
    return ", ".join(values) if values else ""


def parse_json(raw: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a raw LLM string response into a dict, with graceful fallback.

    Tries strict parse first, then extracts the first {...} block if needed.
    Returns a copy of fallback if no valid JSON can be extracted.
    """
    try:
        return json.loads(raw.strip())
    except (json.JSONDecodeError, ValueError):
        pass

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and start < end:
        try:
            return json.loads(raw[start : end + 1])
        except (json.JSONDecodeError, ValueError):
            pass

    logger.warning("LLM response is not valid JSON: %s", raw[:200])
    return fallback.copy()
