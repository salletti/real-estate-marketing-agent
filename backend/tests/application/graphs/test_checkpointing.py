"""Tests pédagogiques — Étape 16 : Checkpointing & Real Workflow Interruption.

Comportement réel de LangGraph 1.1.10 avec invoke() + interrupt() :
- invoke() NE lève PAS GraphInterrupt — il retourne le state avec "__interrupt__"
- L'interrupt est détectable via result.get("__interrupt__") (liste non vide)
- get_state(config).next == ("wait_for_approval",) indique la suspension
- get_state(config).values contient le state sauvegardé
- Command(resume=...) reprend le workflow depuis le point d'interruption
- thread_id différent => workflow indépendant dans le même MemorySaver

Mise à jour step 21.3 : on patche MCPClient.call_tool comme point d'interception universel.
"""
import json
import uuid
from unittest.mock import patch

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from app.application.graphs.nodes.aggregate_drafts_node import aggregate_drafts_node
from app.application.graphs.nodes.generate_facebook_node import generate_facebook_node
from app.application.graphs.nodes.generate_instagram_node import generate_instagram_node
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


def _build_fresh_graph(memory: MemorySaver):
    """Construit un graph minimal avec le MemorySaver fourni."""
    workflow = StateGraph(SocialMediaState)
    workflow.add_node("facebook_node", generate_facebook_node)
    workflow.add_node("instagram_node", generate_instagram_node)
    workflow.add_node("aggregate_drafts", aggregate_drafts_node)
    workflow.add_node("wait_for_approval", wait_for_approval_node)
    workflow.add_conditional_edges(START, lambda s: "facebook_node" if s["generate_facebook"] else "aggregate_drafts")
    workflow.add_conditional_edges("facebook_node", lambda s: "aggregate_drafts")
    workflow.add_edge("instagram_node", "aggregate_drafts")
    workflow.add_edge("aggregate_drafts", "wait_for_approval")
    workflow.add_edge("wait_for_approval", END)
    return workflow.compile(checkpointer=memory)


# ---------------------------------------------------------------------------
# Interrupt — le workflow se suspend réellement
# ---------------------------------------------------------------------------

class TestInterruptSuspendsWorkflow:

    def test_invoke_returns_interrupt_key_not_exception(self):
        """invoke() ne lève pas d'exception : il retourne __interrupt__ dans le state.
        C'est le signal LangGraph que le workflow est suspendu, pas terminé.
        """
        graph = build_social_media_graph()
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            result = graph.invoke(_state(), config=config)
        assert result.get("__interrupt__") is not None
        assert bool(result["__interrupt__"]) is True

    def test_workflow_suspended_before_approval(self):
        """Le graph est suspendu : approval_status est None, pas encore 'pending'."""
        graph = build_social_media_graph()
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            result = graph.invoke(_state(), config=config)
        assert result["approval_status"] is None

    def test_get_state_next_points_to_wait_for_approval(self):
        """get_state().next indique que le workflow attend au node wait_for_approval."""
        graph = build_social_media_graph()
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            graph.invoke(_state(), config=config)
        snap = graph.get_state(config)
        assert "wait_for_approval" in snap.next

    def test_get_state_tasks_contain_interrupt(self):
        """Le message d'interrupt est retourné dans le résultat d'invoke().

        Note : dans cette version de LangGraph, task.interrupts est vide —
        l'information est dans result["__interrupt__"], pas dans snap.tasks.
        """
        graph = build_social_media_graph()
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            result = graph.invoke(_state(), config=config)
        snap = graph.get_state(config)
        assert "wait_for_approval" in snap.next
        all_interrupts = list(result.get("__interrupt__", []))
        assert any("Waiting for human approval" in str(i) for i in all_interrupts)


# ---------------------------------------------------------------------------
# État sauvegardé — le checkpointer conserve le contexte
# ---------------------------------------------------------------------------

class TestCheckpointerSavesState:

    def test_checkpoint_exists_after_interrupt(self):
        """Après interrupt, MemorySaver a un checkpoint pour le thread."""
        memory = MemorySaver()
        g = _build_fresh_graph(memory)
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            g.invoke(_state(), config=config)
        checkpoint = memory.get(config)
        assert checkpoint is not None

    def test_saved_state_contains_facebook_result(self):
        """Le state sauvegardé via get_state() contient facebook_result."""
        memory = MemorySaver()
        g = _build_fresh_graph(memory)
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            g.invoke(_state(), config=config)
        snap = g.get_state(config)
        assert snap.values.get("facebook_result") is not None
        assert snap.values["facebook_result"]["success"] is True

    def test_saved_state_contains_final_result(self):
        """aggregate_drafts_node a tourné avant l'interrupt : final_result présent."""
        memory = MemorySaver()
        g = _build_fresh_graph(memory)
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            g.invoke(_state(), config=config)
        snap = g.get_state(config)
        assert snap.values.get("final_result") is not None
        assert snap.values["final_result"]["success"] is True


# ---------------------------------------------------------------------------
# Reprise — le workflow repart depuis le point d'interruption
# ---------------------------------------------------------------------------

class TestResumeWorkflow:

    def test_resume_approved_completes_workflow(self):
        """Après Command(resume='approved'), le workflow termine sans interrupt."""
        graph = build_social_media_graph()
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            graph.invoke(_state(), config=config)
        with patch(_MCP_CALL_TOOL, return_value=_PUB_FB_RESPONSE):
            result = graph.invoke(Command(resume="approved"), config=config)
        assert not result.get("__interrupt__")

    def test_resume_sets_approval_status_pending(self):
        """Après resume, wait_for_approval_node retourne la décision passée au Command."""
        graph = build_social_media_graph()
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            graph.invoke(_state(), config=config)
        with patch(_MCP_CALL_TOOL, return_value=_PUB_FB_RESPONSE):
            result = graph.invoke(Command(resume="approved"), config=config)
        assert result["approval_status"] == "approved"

    def test_resume_rejected_also_completes_workflow(self):
        """Command(resume='rejected') termine aussi le workflow proprement."""
        graph = build_social_media_graph()
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            graph.invoke(_state(), config=config)
            result = graph.invoke(Command(resume="rejected"), config=config)
        assert result is not None
        assert not result.get("__interrupt__")

    def test_final_result_preserved_after_resume(self):
        """final_result calculé avant l'interrupt est toujours présent après resume."""
        graph = build_social_media_graph()
        config = _config()
        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            graph.invoke(_state(), config=config)
        with patch(_MCP_CALL_TOOL, return_value=_PUB_FB_RESPONSE):
            result = graph.invoke(Command(resume="approved"), config=config)
        assert result["final_result"]["success"] is True


# ---------------------------------------------------------------------------
# thread_id — isolation des workflows
# ---------------------------------------------------------------------------

class TestThreadIdIsolation:

    def test_two_threads_are_independently_suspended(self):
        """Deux thread_id différents = deux workflows indépendants suspendus."""
        graph = build_social_media_graph()
        config_a = _config("thread-a")
        config_b = _config("thread-b")

        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            result_a = graph.invoke(_state(), config=config_a)
            result_b = graph.invoke(_state(), config=config_b)

        assert bool(result_a.get("__interrupt__")) is True
        assert bool(result_b.get("__interrupt__")) is True

    def test_resume_on_thread_a_does_not_affect_thread_b(self):
        """Reprendre le thread A ne modifie pas l'état du thread B."""
        graph = build_social_media_graph()
        config_a = _config("iso-a")
        config_b = _config("iso-b")

        with patch(_MCP_CALL_TOOL, return_value=_FB_TOOL_RESPONSE):
            graph.invoke(_state(), config=config_a)
            graph.invoke(_state(), config=config_b)
        with patch(_MCP_CALL_TOOL, return_value=_PUB_FB_RESPONSE):
            graph.invoke(Command(resume="approved"), config=config_a)

        snap_b = graph.get_state(config_b)
        assert "wait_for_approval" in snap_b.next
