from typing import Any, Dict

from pydantic import BaseModel


class DraftGenerateRequest(BaseModel):
    input: str
    property_json: Dict[str, Any]
