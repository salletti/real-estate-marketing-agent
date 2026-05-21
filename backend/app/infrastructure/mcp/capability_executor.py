import json
import logging

from app.infrastructure.mcp.capability import Capability
from app.infrastructure.mcp.client import MCPClient

logger = logging.getLogger(__name__)


class CapabilityExecutor:
    def execute(
        self,
        capability: Capability,
        payload: dict,
        thread_id: str = "",
    ) -> str:
        client = MCPClient(capability.server_url)
        result = client.call_tool(
            capability.name,
            {**payload, "thread_id": thread_id},
        )
        logger.info(json.dumps({
            "event": "capability_executed",
            "capability": capability.name,
            "server": capability.server_name,
            "thread_id": thread_id,
        }))
        return result


_executor = CapabilityExecutor()


def get_executor() -> CapabilityExecutor:
    return _executor
