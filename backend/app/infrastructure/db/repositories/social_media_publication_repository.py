from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.infrastructure.db.models.social_media_publication_model import SocialMediaPublicationModel


class SocialMediaPublicationRepository:
    """Encapsule la persistence métier des publications réseaux sociaux.

    Gère uniquement la projection métier (table social_media_publications).
    Le runtime LangGraph (MemorySaver / checkpointer) reste totalement indépendant.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(
        self,
        thread_id: str,
        status: str = "draft",
        approval_status: str | None = "pending",
        payload: dict | None = None,
    ) -> SocialMediaPublicationModel:
        publication = SocialMediaPublicationModel(
            thread_id=thread_id,
            status=status,
            approval_status=approval_status,
            payload=payload,
        )
        self._session.add(publication)
        self._session.commit()
        self._session.refresh(publication)
        return publication

    def find_by_thread_id(self, thread_id: str) -> SocialMediaPublicationModel | None:
        return (
            self._session.query(SocialMediaPublicationModel)
            .filter_by(thread_id=thread_id)
            .first()
        )

    def update_status(self, thread_id: str, status: str) -> SocialMediaPublicationModel | None:
        publication = self.find_by_thread_id(thread_id)
        if publication is None:
            return None
        publication.status = status
        publication.updated_at = datetime.now(UTC)
        self._session.commit()
        self._session.refresh(publication)
        return publication

    def update_payload(self, thread_id: str, payload: dict) -> SocialMediaPublicationModel | None:
        publication = self.find_by_thread_id(thread_id)
        if publication is None:
            return None
        publication.payload = payload
        publication.updated_at = datetime.now(UTC)
        self._session.commit()
        self._session.refresh(publication)
        return publication

    def update_approval_status(
        self, thread_id: str, approval_status: str
    ) -> SocialMediaPublicationModel | None:
        publication = self.find_by_thread_id(thread_id)
        if publication is None:
            return None
        publication.approval_status = approval_status
        publication.updated_at = datetime.now(UTC)
        self._session.commit()
        self._session.refresh(publication)
        return publication
