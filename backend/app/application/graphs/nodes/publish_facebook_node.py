from app.application.graphs.state import SocialMediaState
from app.application.observability.runtime_context import RuntimeContext
from app.application.observability.workflow_logger import WorkflowLogger
from app.infrastructure.mcp.capability_executor import get_executor
from app.infrastructure.mcp.capability_registry import get_registry


def publish_facebook_node(state: SocialMediaState) -> dict:
    wl = WorkflowLogger(RuntimeContext(thread_id=state["thread_id"]))
    started_at = wl.log_node_started("publish_facebook_node")

    registry = get_registry()
    executor = get_executor()
    capability = registry.find("publish_facebook")
    if capability is None:
        raise RuntimeError("Capability 'publish_facebook' not available")

    final = state.get("final_result") or {}
    fb = final.get("data", {}).get("platforms", {}).get("facebook", {})
    executor.execute(
        capability,
        {"post": fb.get("post", ""), "images": fb.get("images", [])},
        thread_id=state["thread_id"],
    )

    wl.log_node_completed("publish_facebook_node", started_at)
    return {}
