"""Tests de résilience du graph LangGraph — étape 14.

Point pédagogique : chaque node gère sa propre résilience.
Le graph ne plante plus si un seul node échoue.

Avant (AgentExecutor) : retryWholeWorkflow()
Après (LangGraph)     : retryGenerateInstagramOnly()

Mise à jour step 21.3 : les nodes utilisent CapabilityExecutor. On patche
MCPClient.call_tool comme point d'interception universel.
"""
import json
import uuid
from unittest.mock import patch

import pytest

from app.application.graphs.social_media_graph import build_social_media_graph
from app.application.graphs.state import SocialMediaState

_MCP_CALL_TOOL = "app.infrastructure.mcp.client.MCPClient.call_tool"

_PROPERTY_JSON = json.dumps({"id": 1, "property_type": "Appartement", "city": "Nice", "price": 350000})

_IG_TOOL_RESPONSE = json.dumps({
    "success": True,
    "error": None,
    "data": {"caption": "☀️ Rêve à Nice", "hashtags": ["#realestate"]},
})

_FB_TOOL_RESPONSE = json.dumps({
    "success": True,
    "error": None,
    "data": {"post": "Belle villa à Nice !", "hashtags": ["#immobilier"]},
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
    """Invoque le graph avec thread_id unique et récupère le state sauvegardé."""
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    result = graph.invoke(state, config=config)
    if result.get("__interrupt__"):
        return graph.get_state(config).values
    return result


class TestNodeIsolation:

    def test_facebook_exception_does_not_crash_graph(self):
        """Facebook lève une exception × 3 → graph survit, Instagram réussit."""
        graph = build_social_media_graph()

        def _side_effect(tool_name, arguments):
            if tool_name == "generate_facebook_post":
                raise RuntimeError("API down")
            return _IG_TOOL_RESPONSE

        with patch(_MCP_CALL_TOOL, side_effect=_side_effect):
            result = _invoke(graph, _state(fb=True, ig=True))
        assert result["final_result"]["success"] is True

    def test_instagram_exception_does_not_crash_graph(self):
        """Instagram lève une exception × 3 → graph survit, Facebook réussit."""
        graph = build_social_media_graph()

        def _side_effect(tool_name, arguments):
            if tool_name == "generate_instagram_post":
                raise RuntimeError("timeout")
            return _FB_TOOL_RESPONSE

        with patch(_MCP_CALL_TOOL, side_effect=_side_effect):
            result = _invoke(graph, _state(fb=True, ig=True))
        assert result["final_result"]["success"] is True

    def test_partial_aggregation_includes_only_successful_platform(self):
        """Facebook échoue → platforms contient seulement instagram."""
        graph = build_social_media_graph()

        def _side_effect(tool_name, arguments):
            if tool_name == "generate_facebook_post":
                raise RuntimeError("API down")
            return _IG_TOOL_RESPONSE

        with patch(_MCP_CALL_TOOL, side_effect=_side_effect):
            result = _invoke(graph, _state(fb=True, ig=True))
        platforms = result["final_result"]["data"]["platforms"]
        assert "instagram" in platforms
        assert "facebook" not in platforms

    def test_facebook_node_result_is_error_dict_on_failure(self):
        """Après échec complet, facebook_result contient le dict d'erreur standardisé."""
        graph = build_social_media_graph()

        def _side_effect(tool_name, arguments):
            if tool_name == "generate_facebook_post":
                raise RuntimeError("API down")
            return _IG_TOOL_RESPONSE

        with patch(_MCP_CALL_TOOL, side_effect=_side_effect):
            result = _invoke(graph, _state(fb=True, ig=True))
        fb_result = result["facebook_result"]
        assert fb_result["success"] is False
        assert fb_result["error"] == "node_execution_failed"
        assert fb_result["data"]["operation"] == "generate_facebook"
