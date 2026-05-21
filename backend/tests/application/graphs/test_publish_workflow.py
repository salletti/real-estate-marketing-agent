"""Tests du workflow complet : generate → interrupt → resume → publish — étape 19.

Point pédagogique :

- Après resume("approved"), le graph ne s'arrête plus : il continue vers les publish nodes.
- Après resume("rejected"), le graph termine sans appeler aucun publish tool.
- Les publish nodes restent découplés du domaine Property : ils lisent uniquement
  le texte généré depuis final_result, sans importer Property ni PropertyPhoto.

Mise à jour step 21.3 : on patche MCPClient.call_tool comme point d'interception universel.
"""
import json
import uuid
from unittest.mock import patch

import pytest
from langgraph.types import Command

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
    "data": {"caption": "Superbe appartement #Nice", "hashtags": ["#immobilier", "#nice"]},
})

_PUB_FB_RESPONSE = json.dumps({
    "success": True,
    "error": None,
    "data": {"platform": "facebook", "status": "published", "post_preview": "Belle villa"},
})

_PUB_IG_RESPONSE = json.dumps({
    "success": True,
    "error": None,
    "data": {"platform": "instagram", "status": "published", "caption_preview": "Superbe appart"},
})


def _state(fb: bool = True, ig: bool = False) -> SocialMediaState:
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


def _config(thread_id: str | None = None) -> dict:
    return {"configurable": {"thread_id": thread_id or str(uuid.uuid4())}}


def _run_until_interrupt(graph, state, config, gen_tool_response=None):
    """Lance le graph jusqu'à l'interrupt en mockant MCPClient.call_tool."""
    with patch(_MCP_CALL_TOOL, return_value=gen_tool_response or _FB_TOOL_RESPONSE):
        return graph.invoke(state, config=config)


class TestPublishWorkflow:

    def test_resume_approved_workflow_completes(self):
        """Après resume approved, le workflow termine sans __interrupt__."""
        graph = build_social_media_graph()
        config = _config()
        _run_until_interrupt(graph, _state(fb=True, ig=False), config)

        with patch(_MCP_CALL_TOOL, return_value=_PUB_FB_RESPONSE):
            result = graph.invoke(Command(resume="approved"), config=config)

        assert not result.get("__interrupt__")

    def test_resume_approved_sets_approval_status_approved(self):
        """approval_status == 'approved' après resume approved."""
        graph = build_social_media_graph()
        config = _config()
        _run_until_interrupt(graph, _state(fb=True, ig=False), config)

        with patch(_MCP_CALL_TOOL, return_value=_PUB_FB_RESPONSE):
            result = graph.invoke(Command(resume="approved"), config=config)

        assert result["approval_status"] == "approved"

    def test_resume_rejected_sets_approval_status_rejected(self):
        """approval_status == 'rejected' après resume rejected."""
        graph = build_social_media_graph()
        config = _config()
        _run_until_interrupt(graph, _state(fb=True, ig=False), config)

        result = graph.invoke(Command(resume="rejected"), config=config)

        assert result["approval_status"] == "rejected"

    def test_resume_approved_calls_facebook_publish_tool(self):
        """Avec approved + facebook, l'executor appelle publish_facebook sur le MCP server."""
        graph = build_social_media_graph()
        config = _config()
        _run_until_interrupt(graph, _state(fb=True, ig=False), config)

        with patch(_MCP_CALL_TOOL, return_value=_PUB_FB_RESPONSE) as mock_call:
            graph.invoke(Command(resume="approved"), config=config)

        mock_call.assert_called_once()
        assert mock_call.call_args[0][0] == "publish_facebook"

    def test_resume_approved_calls_instagram_publish_tool(self):
        """Avec approved + instagram, l'executor appelle publish_instagram sur le MCP server."""
        graph = build_social_media_graph()
        config = _config()
        _run_until_interrupt(graph, _state(fb=False, ig=True), config, gen_tool_response=_IG_TOOL_RESPONSE)

        with patch(_MCP_CALL_TOOL, return_value=_PUB_IG_RESPONSE) as mock_call:
            graph.invoke(Command(resume="approved"), config=config)

        mock_call.assert_called_once()
        assert mock_call.call_args[0][0] == "publish_instagram"

    def test_resume_rejected_does_not_call_publish_tools(self):
        """Avec rejected, aucun appel MCP de publication n'est émis."""
        graph = build_social_media_graph()
        config = _config()
        _run_until_interrupt(graph, _state(fb=True, ig=False), config)

        with patch(_MCP_CALL_TOOL) as mock_call:
            graph.invoke(Command(resume="rejected"), config=config)

        mock_call.assert_not_called()

    def test_two_independent_workflows_do_not_share_state(self):
        """Deux workflows avec des thread_id distincts sont indépendants."""
        graph = build_social_media_graph()
        config_a = _config()
        config_b = _config()

        _run_until_interrupt(graph, _state(fb=True, ig=False), config_a)
        _run_until_interrupt(graph, _state(fb=True, ig=False), config_b)

        with patch(_MCP_CALL_TOOL, return_value=_PUB_FB_RESPONSE):
            result_a = graph.invoke(Command(resume="approved"), config=config_a)
            result_b = graph.invoke(Command(resume="rejected"), config=config_b)

        assert result_a["approval_status"] == "approved"
        assert result_b["approval_status"] == "rejected"


class TestPublishNodesDecoupled:
    """Les publish nodes n'importent pas le domaine Property."""

    def test_publish_facebook_node_imports_no_property_domain(self):
        import app.application.graphs.nodes.publish_facebook_node as mod
        source = mod.__file__
        with open(source) as f:
            content = f.read()
        assert "Property" not in content
        assert "property_mapper" not in content

    def test_publish_instagram_node_imports_no_property_domain(self):
        import app.application.graphs.nodes.publish_instagram_node as mod
        source = mod.__file__
        with open(source) as f:
            content = f.read()
        assert "Property" not in content
        assert "property_mapper" not in content
