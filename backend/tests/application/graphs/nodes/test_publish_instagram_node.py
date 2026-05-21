import json
from unittest.mock import patch

from app.application.graphs.nodes.publish_instagram_node import publish_instagram_node

_MCP_CALL_TOOL = "app.infrastructure.mcp.client.MCPClient.call_tool"

_IG_MCP_RESPONSE = json.dumps({
    "success": True,
    "error": None,
    "data": {"platform": "instagram", "status": "published", "caption_preview": "Belle vue!"},
})


def _state(caption: str = "Belle vue!", images: list = None) -> dict:
    return {
        "thread_id": "test-thread",
        "input": "test",
        "property_json": "{}",
        "generate_facebook": False,
        "generate_instagram": True,
        "facebook_result": None,
        "instagram_result": None,
        "final_result": {
            "success": True,
            "error": None,
            "data": {
                "platforms": {
                    "instagram": {
                        "caption": caption,
                        "images": images if images is not None else [],
                    }
                }
            },
        },
        "approval_status": "approved",
    }


class TestPublishInstagramNode:

    def test_calls_publish_instagram_capability(self):
        with patch(_MCP_CALL_TOOL, return_value=_IG_MCP_RESPONSE) as mock_call:
            publish_instagram_node(_state())

        mock_call.assert_called_once()
        assert mock_call.call_args[0][0] == "publish_instagram"

    def test_passes_caption_from_state(self):
        with patch(_MCP_CALL_TOOL, return_value=_IG_MCP_RESPONSE) as mock_call:
            publish_instagram_node(_state(caption="My caption"))

        payload = mock_call.call_args[0][1]
        assert payload["caption"] == "My caption"

    def test_passes_images_from_state(self):
        images = ["https://img.com/a.jpg"]
        with patch(_MCP_CALL_TOOL, return_value=_IG_MCP_RESPONSE) as mock_call:
            publish_instagram_node(_state(images=images))

        payload = mock_call.call_args[0][1]
        assert payload["images"] == images

    def test_passes_thread_id_from_state(self):
        with patch(_MCP_CALL_TOOL, return_value=_IG_MCP_RESPONSE) as mock_call:
            publish_instagram_node(_state())

        payload = mock_call.call_args[0][1]
        assert payload["thread_id"] == "test-thread"

    def test_returns_empty_dict(self):
        with patch(_MCP_CALL_TOOL, return_value=_IG_MCP_RESPONSE):
            result = publish_instagram_node(_state())

        assert result == {}

    def test_handles_missing_final_result(self):
        state = _state()
        state["final_result"] = None
        with patch(_MCP_CALL_TOOL, return_value=_IG_MCP_RESPONSE) as mock_call:
            result = publish_instagram_node(state)

        payload = mock_call.call_args[0][1]
        assert payload["caption"] == ""
        assert payload["images"] == []
        assert result == {}
