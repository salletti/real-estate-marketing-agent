from app.infrastructure.mcp.capability import Capability


class CapabilityRegistry:
    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}

    def register(self, capability: Capability) -> None:
        self._capabilities[capability.name] = capability

    def find(self, name: str) -> Capability | None:
        return self._capabilities.get(name)

    def has(self, name: str) -> bool:
        return name in self._capabilities

    def all(self) -> list[Capability]:
        return list(self._capabilities.values())

    def by_server(self, server_name: str) -> list[Capability]:
        return [c for c in self._capabilities.values() if c.server_name == server_name]


_registry = CapabilityRegistry()


def get_registry() -> CapabilityRegistry:
    return _registry
