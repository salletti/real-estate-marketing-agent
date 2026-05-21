import json
import logging
from unittest.mock import MagicMock, patch

from app.infrastructure.mcp.capability import Capability
from app.infrastructure.mcp.capability_executor import CapabilityExecutor

_CAPABILITY = Capability(
    name="generate_facebook_post",
    description="Generate a Facebook post",
    input_schema={},
    server_name="content-generation-server",
    server_url="http://content-generation-server:8001/sse",
)

_MCP_RESPONSE = json.dumps({
    "success": True,
    "error": None,
    "data": {"post": "Belle villa !", "hashtags": ["#immobilier"]},
})


class TestCapabilityExecutor:

    def test_execute_calls_mcp_client_with_capability_name(self):
        executor = CapabilityExecutor()
        with patch("app.infrastructure.mcp.capability_executor.MCPClient") as mock_cls:
            mock_client = MagicMock()
            mock_client.call_tool.return_value = _MCP_RESPONSE
            mock_cls.return_value = mock_client

            executor.execute(_CAPABILITY, {"property_json": "{}"}, thread_id="t-001")

        mock_client.call_tool.assert_called_once()
        assert mock_client.call_tool.call_args[0][0] == "generate_facebook_post"

    def test_execute_instantiates_mcp_client_with_capability_server_url(self):
        executor = CapabilityExecutor()
        with patch("app.infrastructure.mcp.capability_executor.MCPClient") as mock_cls:
            mock_client = MagicMock()
            mock_client.call_tool.return_value = _MCP_RESPONSE
            mock_cls.return_value = mock_client

            executor.execute(_CAPABILITY, {"property_json": "{}"}, thread_id="t-001")

        mock_cls.assert_called_once_with("http://content-generation-server:8001/sse")

    def test_execute_merges_thread_id_into_call_arguments(self):
        executor = CapabilityExecutor()
        with patch("app.infrastructure.mcp.capability_executor.MCPClient") as mock_cls:
            mock_client = MagicMock()
            mock_client.call_tool.return_value = _MCP_RESPONSE
            mock_cls.return_value = mock_client

            executor.execute(_CAPABILITY, {"property_json": "{}"}, thread_id="t-xyz")

        call_args = mock_client.call_tool.call_args[0][1]
        assert call_args["thread_id"] == "t-xyz"
        assert call_args["property_json"] == "{}"

    def test_execute_returns_mcp_client_result(self):
        executor = CapabilityExecutor()
        with patch("app.infrastructure.mcp.capability_executor.MCPClient") as mock_cls:
            mock_client = MagicMock()
            mock_client.call_tool.return_value = _MCP_RESPONSE
            mock_cls.return_value = mock_client

            result = executor.execute(_CAPABILITY, {}, thread_id="")

        assert result == _MCP_RESPONSE

    def test_execute_emits_capability_executed_log(self, caplog):
        executor = CapabilityExecutor()
        with patch("app.infrastructure.mcp.capability_executor.MCPClient") as mock_cls:
            mock_client = MagicMock()
            mock_client.call_tool.return_value = _MCP_RESPONSE
            mock_cls.return_value = mock_client

            with caplog.at_level(logging.INFO, logger="app.infrastructure.mcp.capability_executor"):
                executor.execute(_CAPABILITY, {}, thread_id="t-001")

        log_events = [json.loads(r.message) for r in caplog.records if r.message.startswith("{")]
        events = [e for e in log_events if e.get("event") == "capability_executed"]
        assert len(events) == 1
        assert events[0]["capability"] == "generate_facebook_post"
        assert events[0]["server"] == "content-generation-server"
        assert events[0]["thread_id"] == "t-001"
