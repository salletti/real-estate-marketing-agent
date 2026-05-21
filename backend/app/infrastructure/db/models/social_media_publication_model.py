from datetime import UTC, datetime

from sqlalchemy import JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SocialMediaPublicationModel(Base):
    """Projection métier durable d'une publication réseaux sociaux.

    Distinct du checkpoint LangGraph (MemorySaver) qui gère le runtime technique.
    Cette table représente l'aggregate lifecycle métier : draft → published/rejected,
    payload marketing, historique et dashboard.
    """

    __tablename__ = "social_media_publications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    thread_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft")
    approval_status: Mapped[str | None] = mapped_column(String, nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
