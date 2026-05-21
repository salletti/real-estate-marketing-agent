import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.infrastructure.mcp.capability_registry import CapabilityRegistry
from app.infrastructure.mcp.discovery import MCPDiscovery


def _make_tool(name: str, description: str | None = None, schema: dict | None = None) -> MagicMock:
    tool = MagicMock()
    tool.name = name
    tool.description = description
    tool.inputSchema = schema or {}
    return tool


class TestMCPDiscovery:

    @pytest.mark.asyncio
    async def test_discover_server_registers_all_tools(self, monkeypatch):
        registry = CapabilityRegistry()
        discovery = MCPDiscovery(registry)
        tools = [_make_tool("tool_a"), _make_tool("tool_b")]

        monkeypatch.setattr(
            "app.infrastructure.mcp.discovery.MCPClient.list_tools_async",
            AsyncMock(return_value=tools),
        )

        await discovery.discover_server("test-server", "http://test/sse")

        assert registry.has("tool_a")
        assert registry.has("tool_b")

    @pytest.mark.asyncio
    async def test_discover_server_sets_server_metadata(self, monkeypatch):
        registry = CapabilityRegistry()
        discovery = MCPDiscovery(registry)
        tools = [_make_tool("my_tool")]

        monkeypatch.setattr(
            "app.infrastructure.mcp.discovery.MCPClient.list_tools_async",
            AsyncMock(return_value=tools),
        )

        await discovery.discover_server("my-server", "http://my-server/sse")

        cap = registry.find("my_tool")
        assert cap.server_name == "my-server"
        assert cap.server_url == "http://my-server/sse"

    @pytest.mark.asyncio
    async def test_discover_server_maps_input_schema(self, monkeypatch):
        registry = CapabilityRegistry()
        discovery = MCPDiscovery(registry)
        schema = {"type": "object", "properties": {"x": {"type": "string"}}}
        tools = [_make_tool("tool_x", schema=schema)]

        monkeypatch.setattr(
            "app.infrastructure.mcp.discovery.MCPClient.list_tools_async",
            AsyncMock(return_value=tools),
        )

        await discovery.discover_server("server", "http://server/sse")

        assert registry.find("tool_x").input_schema == schema

    @pytest.mark.asyncio
    async def test_discover_server_uses_empty_string_when_description_none(self, monkeypatch):
        registry = CapabilityRegistry()
        discovery = MCPDiscovery(registry)
        tools = [_make_tool("tool_x", description=None)]

        monkeypatch.setattr(
            "app.infrastructure.mcp.discovery.MCPClient.list_tools_async",
            AsyncMock(return_value=tools),
        )

        await discovery.discover_server("server", "http://server/sse")

        assert registry.find("tool_x").description == ""

    @pytest.mark.asyncio
    async def test_discover_server_emits_capabilities_discovered_log(self, monkeypatch, caplog):
        registry = CapabilityRegistry()
        discovery = MCPDiscovery(registry)
        tools = [_make_tool("tool_a"), _make_tool("tool_b")]

        monkeypatch.setattr(
            "app.infrastructure.mcp.discovery.MCPClient.list_tools_async",
            AsyncMock(return_value=tools),
        )

        import logging
        with caplog.at_level(logging.INFO, logger="app.infrastructure.mcp.discovery"):
            await discovery.discover_server("test-server", "http://test/sse")

        log_events = [json.loads(r.message) for r in caplog.records if r.message.startswith("{")]
        events = [e for e in log_events if e.get("event") == "capabilities_discovered"]
        assert len(events) == 1
        assert events[0]["server"] == "test-server"
        assert set(events[0]["capabilities"]) == {"tool_a", "tool_b"}
