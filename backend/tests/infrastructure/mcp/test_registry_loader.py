from unittest.mock import AsyncMock, call, patch

import pytest

from app.infrastructure.mcp.capability_registry import CapabilityRegistry
from app.infrastructure.mcp.discovery import MCPDiscovery
from app.infrastructure.mcp.registry_loader import RegistryLoader


class TestRegistryLoader:

    @pytest.mark.asyncio
    async def test_load_calls_discover_for_both_servers(self):
        registry = CapabilityRegistry()
        discovery = MCPDiscovery(registry)
        loader = RegistryLoader(registry, discovery)

        with patch.object(discovery, "discover_server", new_callable=AsyncMock) as mock_discover:
            await loader.load()

        assert mock_discover.call_count == 2

    @pytest.mark.asyncio
    async def test_load_passes_content_generation_server_url_from_settings(self):
        registry = CapabilityRegistry()
        discovery = MCPDiscovery(registry)
        loader = RegistryLoader(registry, discovery)

        with patch.object(discovery, "discover_server", new_callable=AsyncMock) as mock_discover, \
             patch("app.infrastructure.mcp.registry_loader.settings") as mock_settings:
            mock_settings.mcp_content_generation_server_url = "http://cg-server:8001/sse"
            mock_settings.mcp_publication_server_url = "http://pub-server:8002/sse"
            await loader.load()

        urls = [c.args[1] for c in mock_discover.call_args_list]
        assert "http://cg-server:8001/sse" in urls
        assert "http://pub-server:8002/sse" in urls

    @pytest.mark.asyncio
    async def test_load_passes_correct_server_names(self):
        registry = CapabilityRegistry()
        discovery = MCPDiscovery(registry)
        loader = RegistryLoader(registry, discovery)

        with patch.object(discovery, "discover_server", new_callable=AsyncMock) as mock_discover, \
             patch("app.infrastructure.mcp.registry_loader.settings") as mock_settings:
            mock_settings.mcp_content_generation_server_url = "http://cg/sse"
            mock_settings.mcp_publication_server_url = "http://pub/sse"
            await loader.load()

        names = [c.args[0] for c in mock_discover.call_args_list]
        assert "content-generation-server" in names
        assert "publication-server" in names
