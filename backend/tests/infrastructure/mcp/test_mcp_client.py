import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.infrastructure.mcp.client import MCPClient

_SERVER_URL = "http://localhost:8001/sse"
_FACEBOOK_RESPONSE = json.dumps(
    {"success": True, "error": None, "data": {"post": "Super appart!", "hashtags": ["#paris"]}}
)


def _make_text_content(text: str) -> MagicMock:
    c = MagicMock()
    c.type = "text"
    c.text = text
    return c


def _make_call_result(text: str) -> MagicMock:
    r = MagicMock()
    r.content = [_make_text_content(text)]
    return r


class TestMCPClientAsync:

    @pytest.mark.asyncio
    async def test_call_tool_async_returns_text_content(self):
        client = MCPClient(_SERVER_URL)

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.call_tool = AsyncMock(return_value=_make_call_result(_FACEBOOK_RESPONSE))

        with patch("app.infrastructure.mcp.client.sse_client") as mock_sse, \
             patch("app.infrastructure.mcp.client.ClientSession") as mock_cls:

            mock_sse.return_value.__aenter__ = AsyncMock(
                return_value=(MagicMock(), MagicMock())
            )
            mock_sse.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await client.call_tool_async(
                "generate_facebook_post", {"property_json": "{}", "thread_id": "t-001"}
            )

        assert result == _FACEBOOK_RESPONSE
        mock_session.call_tool.assert_called_once_with(
            "generate_facebook_post", {"property_json": "{}", "thread_id": "t-001"}
        )

    @pytest.mark.asyncio
    async def test_call_tool_async_handles_empty_content(self):
        client = MCPClient(_SERVER_URL)

        empty_result = MagicMock()
        empty_result.content = []

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.call_tool = AsyncMock(return_value=empty_result)

        with patch("app.infrastructure.mcp.client.sse_client") as mock_sse, \
             patch("app.infrastructure.mcp.client.ClientSession") as mock_cls:

            mock_sse.return_value.__aenter__ = AsyncMock(
                return_value=(MagicMock(), MagicMock())
            )
            mock_sse.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await client.call_tool_async("generate_facebook_post", {})

        parsed = json.loads(result)
        assert parsed["success"] is False
        assert parsed["error"] == "empty_mcp_response"

    @pytest.mark.asyncio
    async def test_call_tool_async_initializes_session(self):
        client = MCPClient(_SERVER_URL)
        mock_session = AsyncMock()
        mock_session.call_tool = AsyncMock(return_value=_make_call_result("{}"))

        with patch("app.infrastructure.mcp.client.sse_client") as mock_sse, \
             patch("app.infrastructure.mcp.client.ClientSession") as mock_cls:

            mock_sse.return_value.__aenter__ = AsyncMock(
                return_value=(MagicMock(), MagicMock())
            )
            mock_sse.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=None)

            await client.call_tool_async("any_tool", {})

        mock_session.initialize.assert_called_once()
