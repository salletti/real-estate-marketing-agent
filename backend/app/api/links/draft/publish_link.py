from app.api.links.draft.draft_link_abc import DraftLink


class PublishLink(DraftLink):
    """Exposes the publish transition when a draft is awaiting approval."""

    def supports(self, status: str, approval_status: str | None) -> bool:
        return status == "draft" and approval_status == "pending"

    def build_link(self, thread_id: str) -> dict:
        return {
            "method": "POST",
            "href": f"/drafts/{thread_id}/publish",
        }
