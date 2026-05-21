import json
import logging

from fastapi import APIRouter
from pydantic import BaseModel

from app.application.agents.social_media_agent import SocialMediaAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/social-media", tags=["social-media"])


class SocialMediaExecuteRequest(BaseModel):
    input: str
    property: dict


class SocialMediaExecuteResponse(BaseModel):
    success: bool
    error: str | None
    data: dict


@router.post("/execute", response_model=SocialMediaExecuteResponse)
def execute(request: SocialMediaExecuteRequest) -> SocialMediaExecuteResponse:
    try:
        raw = SocialMediaAgent().run(
            input=request.input,
            property_json=json.dumps(request.property),
        )
    except Exception:
        logger.exception("Agent raised an unexpected exception")
        return SocialMediaExecuteResponse(success=False, error="agent_error", data={})

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        logger.error("Agent returned non-JSON output: %s", raw[:200])
        return SocialMediaExecuteResponse(success=False, error="agent_response_parse_error", data={})

    return SocialMediaExecuteResponse(
        success=result.get("success", False),
        error=result.get("error"),
        data=result.get("data", {}),
    )
