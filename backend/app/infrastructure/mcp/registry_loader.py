from app.core.config import settings
from app.infrastructure.mcp.capability_registry import CapabilityRegistry
from app.infrastructure.mcp.discovery import MCPDiscovery


class RegistryLoader:
    def __init__(self, registry: CapabilityRegistry, discovery: MCPDiscovery) -> None:
        self._registry = registry
        self._discovery = discovery

    async def load(self) -> None:
        servers = [
            ("content-generation-server", settings.mcp_content_generation_server_url),
            ("publication-server", settings.mcp_publication_server_url),
        ]
        for server_name, server_url in servers:
            await self._discovery.discover_server(server_name, server_url)
