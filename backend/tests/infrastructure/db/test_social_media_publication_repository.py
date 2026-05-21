import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.infrastructure.db.models.social_media_publication_model import Base
from app.infrastructure.db.repositories.social_media_publication_repository import SocialMediaPublicationRepository


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


_SAMPLE_PAYLOAD = {
    "success": True,
    "error": None,
    "data": {
        "status": "draft",
        "approval_status": "pending",
        "platforms": {"facebook": {"generated": True, "post": "Belle villa !", "hashtags": [], "images": []}},
    },
}


class TestSocialMediaPublicationRepositorySave:
    def test_save_creates_publication_with_defaults(self, session):
        repo = SocialMediaPublicationRepository(session)
        publication = repo.save("thread-001")

        assert publication.id is not None
        assert publication.thread_id == "thread-001"
        assert publication.status == "draft"
        assert publication.approval_status == "pending"

    def test_save_persists_custom_status(self, session):
        repo = SocialMediaPublicationRepository(session)
        publication = repo.save("thread-002", status="completed", approval_status="approved")

        assert publication.status == "completed"
        assert publication.approval_status == "approved"

    def test_save_sets_timestamps(self, session):
        repo = SocialMediaPublicationRepository(session)
        publication = repo.save("thread-003")

        assert publication.created_at is not None
        assert publication.updated_at is not None

    def test_save_with_payload_persists_payload(self, session):
        repo = SocialMediaPublicationRepository(session)
        publication = repo.save("thread-payload", payload=_SAMPLE_PAYLOAD)

        assert publication.payload == _SAMPLE_PAYLOAD

    def test_save_without_payload_defaults_to_none(self, session):
        repo = SocialMediaPublicationRepository(session)
        publication = repo.save("thread-no-payload")

        assert publication.payload is None


class TestSocialMediaPublicationRepositoryFindByThreadId:
    def test_find_by_thread_id_returns_publication(self, session):
        repo = SocialMediaPublicationRepository(session)
        repo.save("thread-abc")

        found = repo.find_by_thread_id("thread-abc")

        assert found is not None
        assert found.thread_id == "thread-abc"

    def test_find_by_thread_id_returns_none_when_missing(self, session):
        repo = SocialMediaPublicationRepository(session)

        result = repo.find_by_thread_id("non-existent")

        assert result is None


class TestSocialMediaPublicationRepositoryUpdatePayload:
    def test_update_payload_sets_payload(self, session):
        repo = SocialMediaPublicationRepository(session)
        repo.save("thread-upd")

        updated = repo.update_payload("thread-upd", _SAMPLE_PAYLOAD)

        assert updated is not None
        assert updated.payload == _SAMPLE_PAYLOAD

    def test_update_payload_overwrites_existing_payload(self, session):
        repo = SocialMediaPublicationRepository(session)
        repo.save("thread-over", payload={"old": True})
        new_payload = {"new": True}

        updated = repo.update_payload("thread-over", new_payload)

        assert updated.payload == new_payload

    def test_update_payload_returns_none_when_missing(self, session):
        repo = SocialMediaPublicationRepository(session)

        result = repo.update_payload("non-existent", _SAMPLE_PAYLOAD)

        assert result is None


class TestSocialMediaPublicationRepositoryUpdateApprovalStatus:
    def test_update_approval_status_updates_field(self, session):
        repo = SocialMediaPublicationRepository(session)
        repo.save("thread-xyz", approval_status="pending")

        updated = repo.update_approval_status("thread-xyz", "approved")

        assert updated is not None
        assert updated.approval_status == "approved"

    def test_update_approval_status_to_rejected(self, session):
        repo = SocialMediaPublicationRepository(session)
        repo.save("thread-rej", approval_status="pending")

        updated = repo.update_approval_status("thread-rej", "rejected")

        assert updated.approval_status == "rejected"

    def test_update_approval_status_returns_none_when_missing(self, session):
        repo = SocialMediaPublicationRepository(session)

        result = repo.update_approval_status("non-existent", "approved")

        assert result is None

    def test_update_approval_status_updates_updated_at(self, session):
        repo = SocialMediaPublicationRepository(session)
        publication = repo.save("thread-ts")
        original_updated_at = publication.updated_at

        updated = repo.update_approval_status("thread-ts", "approved")

        assert updated.updated_at >= original_updated_at
