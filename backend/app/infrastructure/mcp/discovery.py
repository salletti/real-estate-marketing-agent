import json
import logging

from app.infrastructure.mcp.capability import Capability
from app.infrastructure.mcp.capability_registry import CapabilityRegistry
from app.infrastructure.mcp.client import MCPClient

logger = logging.getLogger(__name__)


class MCPDiscovery:
    def __init__(self, registry: CapabilityRegistry) -> None:
        self._registry = registry

    async def discover_server(self, server_name: str, server_url: str) -> None:
        client = MCPClient(server_url)
        tools = await client.list_tools_async()
        for tool in tools:
            cap = Capability(
                name=tool.name,
                description=tool.description or "",
                input_schema=tool.inputSchema or {},
                server_name=server_name,
                server_url=server_url,
            )
            self._registry.register(cap)

        logger.info(json.dumps({
            "event": "capabilities_discovered",
            "server": server_name,
            "capabilities": [t.name for t in tools],
        }))
