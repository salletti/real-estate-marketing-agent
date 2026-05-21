"""Tests du node wait_for_approval et de son intégration dans le graph — étape 16.

Point pédagogique step 16 :

1. Appelé hors contexte graph, interrupt() lève RuntimeError (pas GraphInterrupt).
   LangGraph a besoin d'un contexte Runnable pour sauvegarder le state.

2. Dans le graph avec MemorySaver + thread_id, invoke() NE lève PAS d'exception.
   Il retourne le state avec une clé "__interrupt__" : le workflow est suspendu.
   L'appelant détecte la suspension en vérifiant result.get("__interrupt__").

3. graph.invoke(Command(resume=...), config) reprend depuis le point d'interruption.
   Le node retourne {"approval_status": "pending"} et le graph termine normalement.

Mise à jour step 21.3 : on patche MCPClient.call_tool comme point d'interception universel.
"""
import json
import uuid
from unittest.mock import patch

import pytest
from langgraph.types import Command

from app.application.graphs.nodes.wait_for_approval_node import wait_for_approval_node
from app.application.graphs.social_media_graph import build_social_media_graph
from app.application.graphs.state import SocialMediaState

_MCP_CALL_TOOL = "app.infrastructure.mcp.client.MCPClient.call_tool"

_PROPERTY_JSON = json.dumps({"id": 1, "property_type": "Appartement", "city": "Nice", "price": 350000})

_FB_TOOL_RESPONSE = json.dumps({
    "success": True,
    "error": None,
    "data": {"post": "Belle villa à Nice !", "hashtags": ["#immobilier"]},
})

_PUB_FB_RESPONSE = json.dumps({
    "success": True,
    "error": None,
    "data": {"platform": "facebook", "status": "published", "post_preview": "Belle villa"},
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


# ---------------------------------------------------------------------------
# Unitaire — nœud isolé (hors contexte graph)
# ---------------------------------------------------------------------------

class TestWaitForApprovalNode:

    def test_raises_runtime_error_outside_graph_context(self):
        """interrupt() a besoin d'un contexte Runnable (graph + checkpointer).
        Hors contexte, il lève RuntimeError — pas GraphInterrupt.
        """
        with pytest.raises(RuntimeError, match="outside of a runnable context"):
            wait_for_approval_node(_state())


# ---------------------------------------------------------------------------
# Intégration — graph complet : suspend puis reprend
# ---------------------------------------------------------------------------

class TestGraphApprovalFlow:

    def test_invoke_returns_interrupt_key_when_suspended(self):
        """invoke() ne lève pas d'exception : il retourne __interrupt__ dans le state.
        C'est la façon dont LangGraph signale une suspension dans invoke().
        """
        graph = build_social_media_graph()
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            result = graph.invoke(_state(fb=True, ig=False), config=config)
        assert result.get("__interrupt__") is not None
        assert bool(result["__interrupt__"]) is True

    def test_interrupt_message_is_waiting_for_human_approval(self):
        """Le message de l'interrupt identifie la nature de l'attente métier."""
        graph = build_social_media_graph()
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            result = graph.invoke(_state(fb=True, ig=False), config=config)
        interrupts = result.get("__interrupt__", [])
        assert any("Waiting for human approval" in str(i) for i in interrupts)

    def test_approval_status_none_before_resume(self):
        """Avant resume, wait_for_approval_node n'a pas encore retourné son état."""
        graph = build_social_media_graph()
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            result = graph.invoke(_state(fb=True, ig=False), config=config)
        assert result["approval_status"] is None

    def test_approval_status_equals_resume_decision(self):
        """Après resume, wait_for_approval_node retourne la décision passée au Command."""
        graph = build_social_media_graph()
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            graph.invoke(_state(fb=True, ig=False), config=config)
        with patch(_MCP_CALL_TOOL, return_value=_PUB_FB_RESPONSE):
            result = graph.invoke(Command(resume="approved"), config=config)
        assert result["approval_status"] == "approved"

    def test_final_result_available_after_resume(self):
        """final_result calculé par aggregate_drafts_node est présent après resume."""
        graph = build_social_media_graph()
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            graph.invoke(_state(fb=True, ig=False), config=config)
        with patch(_MCP_CALL_TOOL, return_value=_PUB_FB_RESPONSE):
            result = graph.invoke(Command(resume="approved"), config=config)
        assert result["final_result"]["success"] is True

    def test_final_result_contains_approval_status_in_data(self):
        """aggregate_drafts_node inclut approval_status dans data."""
        graph = build_social_media_graph()
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            graph.invoke(_state(fb=True, ig=False), config=config)
        with patch(_MCP_CALL_TOOL, return_value=_PUB_FB_RESPONSE):
            result = graph.invoke(Command(resume="approved"), config=config)
        assert result["final_result"]["data"]["approval_status"] == "pending"

    def test_workflow_completes_without_interrupt_after_resume(self):
        """Après resume, __interrupt__ est absent : le workflow a terminé."""
        graph = build_social_media_graph()
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            graph.invoke(_state(fb=True, ig=False), config=config)
        with patch(_MCP_CALL_TOOL, return_value=_PUB_FB_RESPONSE):
            result = graph.invoke(Command(resume="approved"), config=config)
        assert not result.get("__interrupt__")
