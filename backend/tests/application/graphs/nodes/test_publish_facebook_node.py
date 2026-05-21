import json
from unittest.mock import patch

from app.application.graphs.nodes.publish_facebook_node import publish_facebook_node

_MCP_CALL_TOOL = "app.infrastructure.mcp.client.MCPClient.call_tool"

_FB_MCP_RESPONSE = json.dumps({
    "success": True,
    "error": None,
    "data": {"platform": "facebook", "status": "published", "post_preview": "Super appart!"},
})


def _state(post: str = "Super appart!", images: list = None) -> dict:
    return {
        "thread_id": "test-thread",
        "input": "test",
        "property_json": "{}",
        "generate_facebook": True,
        "generate_instagram": False,
        "facebook_result": None,
        "instagram_result": None,
        "final_result": {
            "success": True,
            "error": None,
            "data": {
                "platforms": {
                    "facebook": {
                        "post": post,
                        "images": images if images is not None else [],
                    }
                }
            },
        },
        "approval_status": "approved",
    }


class TestPublishFacebookNode:

    def test_calls_publish_facebook_capability(self):
        with patch(_MCP_CALL_TOOL, return_value=_FB_MCP_RESPONSE) as mock_call:
            publish_facebook_node(_state())

        mock_call.assert_called_once()
        assert mock_call.call_args[0][0] == "publish_facebook"

    def test_passes_post_from_state(self):
        with patch(_MCP_CALL_TOOL, return_value=_FB_MCP_RESPONSE) as mock_call:
            publish_facebook_node(_state(post="My post"))

        payload = mock_call.call_args[0][1]
        assert payload["post"] == "My post"

    def test_passes_images_from_state(self):
        images = ["https://img.com/1.jpg"]
        with patch(_MCP_CALL_TOOL, return_value=_FB_MCP_RESPONSE) as mock_call:
            publish_facebook_node(_state(images=images))

        payload = mock_call.call_args[0][1]
        assert payload["images"] == images

    def test_passes_thread_id_from_state(self):
        with patch(_MCP_CALL_TOOL, return_value=_FB_MCP_RESPONSE) as mock_call:
            publish_facebook_node(_state())

        payload = mock_call.call_args[0][1]
        assert payload["thread_id"] == "test-thread"

    def test_returns_empty_dict(self):
        with patch(_MCP_CALL_TOOL, return_value=_FB_MCP_RESPONSE):
            result = publish_facebook_node(_state())

        assert result == {}

    def test_handles_missing_final_result(self):
        state = _state()
        state["final_result"] = None
        with patch(_MCP_CALL_TOOL, return_value=_FB_MCP_RESPONSE) as mock_call:
            result = publish_facebook_node(state)

        payload = mock_call.call_args[0][1]
        assert payload["post"] == ""
        assert payload["images"] == []
        assert result == {}
