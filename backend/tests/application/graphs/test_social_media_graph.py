"""Tests du graph LangGraph — step 12.

Point pédagogique : le state est explicite, l'orchestration est en Python,
le LLM ne décide plus de rien. Tous les tests mockent les tools.

Mise à jour step 16 : le graph utilise désormais MemorySaver + interrupt().
Chaque invocation nécessite un thread_id unique. Comme interrupt() lève
GraphInterrupt avant d'atteindre END, on récupère le state via get_state().

Mise à jour step 21.3 : les nodes utilisent CapabilityExecutor. On patche
MCPClient.call_tool comme point d'interception universel.
"""
import json
import uuid
from unittest.mock import patch

from langgraph.errors import GraphInterrupt

from app.application.graphs.social_media_graph import build_social_media_graph
from app.application.graphs.state import SocialMediaState

_MCP_CALL_TOOL = "app.infrastructure.mcp.client.MCPClient.call_tool"

_PROPERTY_JSON = json.dumps({"id": 1, "property_type": "Appartement", "city": "Nice", "price": 350000})

_FB_TOOL_RESPONSE = json.dumps({
    "success": True,
    "error": None,
    "data": {"post": "Belle villa à Nice !", "hashtags": ["#immobilier"]},
})

_IG_TOOL_RESPONSE = json.dumps({
    "success": True,
    "error": None,
    "data": {"caption": "☀️ Rêve à Nice", "hashtags": ["#realestate"]},
})

_FB_TOOL_FAILURE = json.dumps({
    "success": False,
    "error": "llm_generation_failed",
    "data": {"post": "", "hashtags": []},
})


def _state(fb: bool, ig: bool) -> SocialMediaState:
    return {
        "thread_id": "test-thread",
        "input": "test",
        "property_json": _PROPERTY_JSON,
        "generate_facebook": fb,
        "generate_instagram": ig,
        "facebook_result": None,
        "instagram_result": None,
        "final_result": None,
        "approval_status": None,
    }


def _invoke(graph, state: SocialMediaState) -> dict:
    """Invoque le graph avec un thread_id unique et gère GraphInterrupt.

    Le graph se suspend à wait_for_approval_node (interrupt). On récupère
    le state sauvegardé via get_state — il contient final_result et les
    résultats des nodes qui ont tourné avant l'interruption.
    """
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    try:
        return graph.invoke(state, config=config)
    except GraphInterrupt:
        return graph.get_state(config).values


def _mcp_router(**responses):
    """Crée un side_effect pour MCPClient.call_tool routant par nom de tool."""
    def _call_tool(tool_name, arguments):
        return responses[tool_name]
    return _call_tool


# ---------------------------------------------------------------------------
# Facebook uniquement
# ---------------------------------------------------------------------------

class TestFacebookOnly:

    def test_final_result_success(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            result = _invoke(graph, _state(fb=True, ig=False))
        assert result["final_result"]["success"] is True

    def test_status_is_draft(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            result = _invoke(graph, _state(fb=True, ig=False))
        assert result["final_result"]["data"]["status"] == "draft"

    def test_facebook_platform_present(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            result = _invoke(graph, _state(fb=True, ig=False))
        assert "facebook" in result["final_result"]["data"]["platforms"]

    def test_instagram_platform_absent(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            result = _invoke(graph, _state(fb=True, ig=False))
        assert "instagram" not in result["final_result"]["data"]["platforms"]

    def test_facebook_result_stored_in_state(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            result = _invoke(graph, _state(fb=True, ig=False))
        assert result["facebook_result"] is not None

    def test_instagram_result_absent_from_state(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            result = _invoke(graph, _state(fb=True, ig=False))
        assert result["instagram_result"] is None


# ---------------------------------------------------------------------------
# Instagram uniquement
# ---------------------------------------------------------------------------

class TestInstagramOnly:

    def test_final_result_success(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, return_value=_IG_TOOL_RESPONSE):
            result = _invoke(graph, _state(fb=False, ig=True))
        assert result["final_result"]["success"] is True

    def test_instagram_platform_present(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, return_value=_IG_TOOL_RESPONSE):
            result = _invoke(graph, _state(fb=False, ig=True))
        assert "instagram" in result["final_result"]["data"]["platforms"]

    def test_facebook_platform_absent(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, return_value=_IG_TOOL_RESPONSE):
            result = _invoke(graph, _state(fb=False, ig=True))
        assert "facebook" not in result["final_result"]["data"]["platforms"]

    def test_instagram_result_stored_in_state(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, return_value=_IG_TOOL_RESPONSE):
            result = _invoke(graph, _state(fb=False, ig=True))
        assert result["instagram_result"] is not None

    def test_facebook_result_absent_from_state(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, return_value=_IG_TOOL_RESPONSE):
            result = _invoke(graph, _state(fb=False, ig=True))
        assert result["facebook_result"] is None


# ---------------------------------------------------------------------------
# Facebook + Instagram
# ---------------------------------------------------------------------------

class TestBothPlatforms:

    def test_final_result_success(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, side_effect=_mcp_router(
            generate_facebook_post=_FB_TOOL_RESPONSE,
            generate_instagram_post=_IG_TOOL_RESPONSE,
        )):
            result = _invoke(graph, _state(fb=True, ig=True))
        assert result["final_result"]["success"] is True

    def test_both_platforms_in_result(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, side_effect=_mcp_router(
            generate_facebook_post=_FB_TOOL_RESPONSE,
            generate_instagram_post=_IG_TOOL_RESPONSE,
        )):
            result = _invoke(graph, _state(fb=True, ig=True))
        platforms = result["final_result"]["data"]["platforms"]
        assert "facebook" in platforms
        assert "instagram" in platforms

    def test_both_results_stored_in_state(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, side_effect=_mcp_router(
            generate_facebook_post=_FB_TOOL_RESPONSE,
            generate_instagram_post=_IG_TOOL_RESPONSE,
        )):
            result = _invoke(graph, _state(fb=True, ig=True))
        assert result["facebook_result"] is not None
        assert result["instagram_result"] is not None

    def test_status_is_draft(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, side_effect=_mcp_router(
            generate_facebook_post=_FB_TOOL_RESPONSE,
            generate_instagram_post=_IG_TOOL_RESPONSE,
        )):
            result = _invoke(graph, _state(fb=True, ig=True))
        assert result["final_result"]["data"]["status"] == "draft"


# ---------------------------------------------------------------------------
# Agrégation — contenu préservé
# ---------------------------------------------------------------------------

class TestAggregation:

    def test_facebook_post_content_preserved(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            result = _invoke(graph, _state(fb=True, ig=False))
        fb = result["final_result"]["data"]["platforms"]["facebook"]
        assert fb["post"] == "Belle villa à Nice !"
        assert fb["hashtags"] == ["#immobilier"]
        assert fb["images"] == []
        assert fb["generated"] is True

    def test_instagram_caption_content_preserved(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, return_value=_IG_TOOL_RESPONSE):
            result = _invoke(graph, _state(fb=False, ig=True))
        ig = result["final_result"]["data"]["platforms"]["instagram"]
        assert ig["caption"] == "☀️ Rêve à Nice"
        assert ig["hashtags"] == ["#realestate"]
        assert ig["images"] == []
        assert ig["generated"] is True

    def test_no_platform_returns_failure(self):
        graph = build_social_media_graph()
        result = _invoke(graph, _state(fb=False, ig=False))
        assert result["final_result"]["success"] is False
        assert result["final_result"]["error"] == "no_platform_generated"
        assert "platform_errors" in result["final_result"]["data"]

    def test_failed_tool_excluded_from_platforms(self):
        graph = build_social_media_graph()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_FAILURE):
            result = _invoke(graph, _state(fb=True, ig=False))
        assert result["final_result"]["success"] is False
        assert "facebook" not in result["final_result"].get("data", {}).get("platforms", {})
