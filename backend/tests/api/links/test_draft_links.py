import pytest

from app.api.links.draft.publish_link import PublishLink
from app.api.links.draft.reject_link import RejectLink
from app.api.links.draft.draft_links_builder import DraftLinksBuilder

_THREAD_ID = "test-thread-abc"


class TestPublishLinkSupports:

    def test_supports_draft_pending(self):
        assert PublishLink().supports("draft", "pending") is True

    def test_does_not_support_published(self):
        assert PublishLink().supports("published", "approved") is False

    def test_does_not_support_rejected_approval(self):
        assert PublishLink().supports("draft", "rejected") is False

    def test_does_not_support_none_approval(self):
        assert PublishLink().supports("draft", None) is False

    def test_does_not_support_already_published_status(self):
        assert PublishLink().supports("published", "pending") is False


class TestPublishLinkBuildLink:

    def test_method_is_post(self):
        assert PublishLink().build_link(_THREAD_ID)["method"] == "POST"

    def test_href_contains_thread_id(self):
        assert PublishLink().build_link(_THREAD_ID)["href"] == f"/drafts/{_THREAD_ID}/publish"


class TestRejectLinkSupports:

    def test_supports_draft_pending(self):
        assert RejectLink().supports("draft", "pending") is True

    def test_does_not_support_published(self):
        assert RejectLink().supports("published", "approved") is False

    def test_does_not_support_rejected_approval(self):
        assert RejectLink().supports("draft", "rejected") is False

    def test_does_not_support_none_approval(self):
        assert RejectLink().supports("draft", None) is False

    def test_does_not_support_already_published_status(self):
        assert RejectLink().supports("published", "pending") is False


class TestRejectLinkBuildLink:

    def test_method_is_post(self):
        assert RejectLink().build_link(_THREAD_ID)["method"] == "POST"

    def test_href_contains_thread_id(self):
        assert RejectLink().build_link(_THREAD_ID)["href"] == f"/drafts/{_THREAD_ID}/reject"


class TestDraftLinksBuilder:

    def test_build_draft_pending_returns_both_links(self):
        builder = DraftLinksBuilder(links=[PublishLink(), RejectLink()])
        result = builder.build("draft", "pending", _THREAD_ID)
        assert set(result.keys()) == {"publish", "reject"}

    def test_build_published_returns_empty(self):
        builder = DraftLinksBuilder(links=[PublishLink(), RejectLink()])
        assert builder.build("published", "approved", _THREAD_ID) == {}

    def test_build_rejected_approval_returns_empty(self):
        builder = DraftLinksBuilder(links=[PublishLink(), RejectLink()])
        assert builder.build("draft", "rejected", _THREAD_ID) == {}

    def test_build_none_approval_returns_empty(self):
        builder = DraftLinksBuilder(links=[PublishLink(), RejectLink()])
        assert builder.build("draft", None, _THREAD_ID) == {}

    def test_publish_link_href(self):
        builder = DraftLinksBuilder(links=[PublishLink()])
        result = builder.build("draft", "pending", _THREAD_ID)
        assert result["publish"]["href"] == f"/drafts/{_THREAD_ID}/publish"
        assert result["publish"]["method"] == "POST"

    def test_reject_link_href(self):
        builder = DraftLinksBuilder(links=[RejectLink()])
        result = builder.build("draft", "pending", _THREAD_ID)
        assert result["reject"]["href"] == f"/drafts/{_THREAD_ID}/reject"
        assert result["reject"]["method"] == "POST"

    def test_empty_links_list_returns_empty(self):
        builder = DraftLinksBuilder(links=[])
        assert builder.build("draft", "pending", _THREAD_ID) == {}

    def test_key_derived_from_class_name(self):
        builder = DraftLinksBuilder(links=[PublishLink()])
        result = builder.build("draft", "pending", _THREAD_ID)
        assert "publish" in result
        assert "PublishLink" not in result
