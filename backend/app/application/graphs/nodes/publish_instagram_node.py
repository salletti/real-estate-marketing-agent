from app.application.graphs.state import SocialMediaState
from app.application.observability.runtime_context import RuntimeContext
from app.application.observability.workflow_logger import WorkflowLogger
from app.infrastructure.mcp.capability_executor import get_executor
from app.infrastructure.mcp.capability_registry import get_registry


def publish_instagram_node(state: SocialMediaState) -> dict:
    wl = WorkflowLogger(RuntimeContext(thread_id=state["thread_id"]))
    started_at = wl.log_node_started("publish_instagram_node")

    registry = get_registry()
    executor = get_executor()
    capability = registry.find("publish_instagram")
    if capability is None:
        raise RuntimeError("Capability 'publish_instagram' not available")

    final = state.get("final_result") or {}
    ig = final.get("data", {}).get("platforms", {}).get("instagram", {})
    executor.execute(
        capability,
        {"caption": ig.get("caption", ""), "images": ig.get("images", [])},
        thread_id=state["thread_id"],
    )

    wl.log_node_completed("publish_instagram_node", started_at)
    return {}
