import pytest

from app.infrastructure.mcp.capability import Capability
from app.infrastructure.mcp.capability_registry import CapabilityRegistry


def _make_capability(name: str, server_name: str = "server") -> Capability:
    return Capability(
        name=name,
        description=f"Tool {name}",
        input_schema={},
        server_name=server_name,
        server_url=f"http://{server_name}/sse",
    )


class TestCapabilityRegistry:

    def test_find_returns_registered_capability(self):
        registry = CapabilityRegistry()
        cap = _make_capability("generate_facebook_post")
        registry.register(cap)
        assert registry.find("generate_facebook_post") is cap

    def test_find_returns_none_for_unknown_capability(self):
        registry = CapabilityRegistry()
        assert registry.find("unknown_tool") is None

    def test_has_returns_true_for_registered(self):
        registry = CapabilityRegistry()
        registry.register(_make_capability("publish_facebook"))
        assert registry.has("publish_facebook") is True

    def test_has_returns_false_for_unregistered(self):
        registry = CapabilityRegistry()
        assert registry.has("publish_facebook") is False

    def test_all_returns_all_registered_capabilities(self):
        registry = CapabilityRegistry()
        registry.register(_make_capability("tool_a"))
        registry.register(_make_capability("tool_b"))
        names = {c.name for c in registry.all()}
        assert names == {"tool_a", "tool_b"}

    def test_all_returns_empty_list_when_no_capabilities(self):
        registry = CapabilityRegistry()
        assert registry.all() == []

    def test_by_server_filters_by_server_name(self):
        registry = CapabilityRegistry()
        registry.register(_make_capability("tool_a", server_name="server-1"))
        registry.register(_make_capability("tool_b", server_name="server-2"))
        registry.register(_make_capability("tool_c", server_name="server-1"))
        result = registry.by_server("server-1")
        assert {c.name for c in result} == {"tool_a", "tool_c"}

    def test_by_server_returns_empty_for_unknown_server(self):
        registry = CapabilityRegistry()
        registry.register(_make_capability("tool_a", server_name="server-1"))
        assert registry.by_server("unknown-server") == []

    def test_register_overwrites_existing_capability(self):
        registry = CapabilityRegistry()
        cap_v1 = _make_capability("tool_a")
        cap_v2 = Capability(
            name="tool_a",
            description="Updated",
            input_schema={},
            server_name="server",
            server_url="http://server/sse",
        )
        registry.register(cap_v1)
        registry.register(cap_v2)
        assert registry.find("tool_a").description == "Updated"
