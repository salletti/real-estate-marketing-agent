from abc import ABC, abstractmethod


class DraftLink(ABC):
    """
    Specification-like interface for a single HATEOAS transition on a draft.

    Each implementation knows two things:
    - whether it applies to the current draft state (supports)
    - how to build its hypermedia descriptor (build_link)

    This pattern is the foundation for agentic systems: an agent reads
    _links and discovers which actions are currently authorized without
    needing to know the workflow rules itself.
    """

    @abstractmethod
    def supports(self, status: str, approval_status: str | None) -> bool:
        pass

    @abstractmethod
    def build_link(self, thread_id: str) -> dict:
        pass
