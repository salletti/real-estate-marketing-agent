from app.api.links.draft.draft_link_abc import DraftLink
from app.api.links.draft.publish_link import PublishLink
from app.api.links.draft.reject_link import RejectLink


class DraftLinksBuilder:
    """
    Aggregates all registered DraftLink instances and builds the _links
    payload for a given draft state.

    The key for each link is derived automatically from the class name:
      PublishLink -> "publish"
      RejectLink  -> "reject"

    Adding a new transition requires only a new DraftLink implementation
    and registration here — no conditional logic anywhere in the codebase.
    """

    def __init__(self, links: list[DraftLink]) -> None:
        self._links = links

    def build(
        self,
        status: str,
        approval_status: str | None,
        thread_id: str,
    ) -> dict[str, dict]:
        result = {}
        for link in self._links:
            if link.supports(status, approval_status):
                key = type(link).__name__.replace("Link", "").lower()
                result[key] = link.build_link(thread_id)
        return result


def get_draft_links_builder() -> DraftLinksBuilder:
    return DraftLinksBuilder(links=[PublishLink(), RejectLink()])
