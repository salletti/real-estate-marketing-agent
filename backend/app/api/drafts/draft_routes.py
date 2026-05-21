import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.links.draft.draft_links_builder import DraftLinksBuilder, get_draft_links_builder
from app.api.schemas.draft_request import DraftGenerateRequest
from app.api.schemas.draft_response import DraftResponse
from app.application.agents.social_media_agent import SocialMediaAgent
from app.infrastructure.db.repositories.social_media_publication_repository import SocialMediaPublicationRepository
from app.infrastructure.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/drafts", tags=["drafts"])


def _require_content_or_500(payload: dict | None) -> dict:
    if payload is None:
        raise HTTPException(status_code=500, detail="draft_content_missing")
    return payload


def _raise_on_generation_failure(content: dict) -> None:
    if content.get("success") is False:
        raise HTTPException(
            status_code=502,
            detail={
                "error": content.get("error", "generation_failed"),
                "data": content.get("data", {}),
            },
        )


@router.post("/generate", response_model=DraftResponse, response_model_by_alias=True, status_code=201)
def generate_draft(
    request: DraftGenerateRequest,
    db: Session = Depends(get_db),
    links_builder: DraftLinksBuilder = Depends(get_draft_links_builder),
) -> DraftResponse:
    repo = SocialMediaPublicationRepository(db)
    agent = SocialMediaAgent(publication_repository=repo)

    try:
        raw = agent.run(input=request.input, property_json=json.dumps(request.property_json))
    except Exception:
        logger.exception("Agent raised an unexpected exception")
        raise HTTPException(status_code=500, detail="agent_error")

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        logger.error("Agent returned non-JSON output: %s", raw[:200])
        raise HTTPException(status_code=500, detail="agent_response_parse_error")

    data = result.get("data", {})
    thread_id = data.get("thread_id")
    if not thread_id:
        raise HTTPException(status_code=500, detail="draft_creation_failed")

    status = data.get("status", "draft")
    approval_status = data.get("approval_status")
    publication = repo.find_by_thread_id(thread_id)
    if publication is None:
        raise HTTPException(status_code=500, detail="draft_creation_failed")
    content = _require_content_or_500(publication.payload)
    _raise_on_generation_failure(content)

    return DraftResponse(
        thread_id=thread_id,
        status=status,
        approval_status=approval_status,
        content=content,
        links=links_builder.build(
            status=status,
            approval_status=approval_status,
            thread_id=thread_id,
        ),
    )


@router.get("/{thread_id}", response_model=DraftResponse, response_model_by_alias=True)
def get_draft(
    thread_id: str,
    db: Session = Depends(get_db),
    links_builder: DraftLinksBuilder = Depends(get_draft_links_builder),
) -> DraftResponse:
    repo = SocialMediaPublicationRepository(db)
    publication = repo.find_by_thread_id(thread_id)

    if publication is None:
        raise HTTPException(status_code=404, detail="draft_not_found")
    content = _require_content_or_500(publication.payload)

    return DraftResponse(
        thread_id=publication.thread_id,
        status=publication.status,
        approval_status=publication.approval_status,
        content=content,
        links=links_builder.build(
            status=publication.status,
            approval_status=publication.approval_status,
            thread_id=publication.thread_id,
        ),
    )


@router.post("/{thread_id}/reject", response_model=DraftResponse, response_model_by_alias=True)
def reject_draft(
    thread_id: str,
    db: Session = Depends(get_db),
    links_builder: DraftLinksBuilder = Depends(get_draft_links_builder),
) -> DraftResponse:
    repo = SocialMediaPublicationRepository(db)
    publication = repo.find_by_thread_id(thread_id)

    if publication is None:
        raise HTTPException(status_code=404, detail="draft_not_found")

    if publication.approval_status != "pending":
        raise HTTPException(status_code=409, detail="draft_not_rejectable")

    agent = SocialMediaAgent(publication_repository=repo)
    agent.resume(thread_id=thread_id, approval="rejected")

    repo.update_status(thread_id=thread_id, status="rejected")

    publication = repo.find_by_thread_id(thread_id)
    content = _require_content_or_500(publication.payload)
    return DraftResponse(
        thread_id=publication.thread_id,
        status=publication.status,
        approval_status=publication.approval_status,
        content=content,
        links=links_builder.build(
            status=publication.status,
            approval_status=publication.approval_status,
            thread_id=publication.thread_id,
        ),
    )


@router.post("/{thread_id}/publish", response_model=DraftResponse, response_model_by_alias=True)
def publish_draft(
    thread_id: str,
    db: Session = Depends(get_db),
    links_builder: DraftLinksBuilder = Depends(get_draft_links_builder),
) -> DraftResponse:
    repo = SocialMediaPublicationRepository(db)
    publication = repo.find_by_thread_id(thread_id)

    if publication is None:
        raise HTTPException(status_code=404, detail="draft_not_found")

    if publication.approval_status != "pending":
        raise HTTPException(status_code=409, detail="draft_not_publishable")

    agent = SocialMediaAgent(publication_repository=repo)
    agent.resume(thread_id=thread_id, approval="approved")

    repo.update_status(thread_id=thread_id, status="published")

    publication = repo.find_by_thread_id(thread_id)
    content = _require_content_or_500(publication.payload)
    return DraftResponse(
        thread_id=publication.thread_id,
        status=publication.status,
        approval_status=publication.approval_status,
        content=content,
        links=links_builder.build(
            status=publication.status,
            approval_status=publication.approval_status,
            thread_id=publication.thread_id,
        ),
    )
