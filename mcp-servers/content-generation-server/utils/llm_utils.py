import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def bool_to_str(value: Optional[bool]) -> str:
    if value is True:
        return "oui"
    if value is False:
        return "non"
    return ""


def list_to_str(values: List[str]) -> str:
    return ", ".join(values) if values else ""


def _escape_newlines_in_strings(raw: str) -> str:
    """Escape literal newlines that appear inside JSON string values."""
    result = []
    in_string = False
    escape_next = False
    for ch in raw:
        if escape_next:
            result.append(ch)
            escape_next = False
        elif ch == "\\":
            result.append(ch)
            escape_next = True
        elif ch == '"':
            result.append(ch)
            in_string = not in_string
        elif ch == "\n" and in_string:
            result.append("\\n")
        else:
            result.append(ch)
    return "".join(result)


def parse_json(raw: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    stripped = raw.strip()

    for candidate in (stripped, _escape_newlines_in_strings(stripped)):
        try:
            return json.loads(candidate)
        except (json.JSONDecodeError, ValueError):
            pass

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and start < end:
        block = raw[start : end + 1]
        for candidate in (block, _escape_newlines_in_strings(block)):
            try:
                return json.loads(candidate)
            except (json.JSONDecodeError, ValueError):
                pass

    logger.warning("LLM response is not valid JSON: %s", raw[:200])
    return fallback.copy()
