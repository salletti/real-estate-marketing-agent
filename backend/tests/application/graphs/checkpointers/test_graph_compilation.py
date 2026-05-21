import uuid
from unittest.mock import patch

from langgraph.types import Command

from app.application.graphs.social_media_graph import build_social_media_graph
from app.application.graphs.state import SocialMediaState

_MCP_CALL_TOOL = "app.infrastructure.mcp.client.MCPClient.call_tool"
_FB_TOOL_RESPONSE = '{"success": true, "error": null, "data": {"post": "test", "hashtags": []}}'
_PUB_FB_RESPONSE = '{"success": true, "error": null, "data": {"platform": "facebook", "status": "published", "post_preview": "test"}}'


def _state() -> SocialMediaState:
    return {
        "thread_id": "test-thread",
        "input": "test",
        "property_json": '{"id": 1}',
        "generate_facebook": True,
        "generate_instagram": False,
        "facebook_result": None,
        "instagram_result": None,
        "final_result": None,
        "approval_status": None,
    }


def _config():
    return {"configurable": {"thread_id": str(uuid.uuid4())}}


class TestGraphCompilationWithProvider:

    def test_graph_compiles(self):
        graph = build_social_media_graph()
        assert graph is not None

    def test_graph_reaches_interrupt(self):
        graph = build_social_media_graph()
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            result = graph.invoke(_state(), config=config)
        assert result.get("__interrupt__") is not None

    def test_graph_resume_after_interrupt(self):
        graph = build_social_media_graph()
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            graph.invoke(_state(), config=config)
        with patch(_MCP_CALL_TOOL, return_value=_PUB_FB_RESPONSE):
            result = graph.invoke(Command(resume="approved"), config=config)
        assert not result.get("__interrupt__")
