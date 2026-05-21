import logging

from app.application.common.retry_utils import retry_operation
from app.application.graphs.state import SocialMediaState
from app.application.observability.runtime_context import RuntimeContext
from app.application.observability.workflow_logger import WorkflowLogger
from app.infrastructure.mcp.capability_executor import get_executor
from app.infrastructure.mcp.capability_registry import get_registry

logger = logging.getLogger(__name__)


def generate_instagram_node(state: SocialMediaState) -> dict:
    wl = WorkflowLogger(RuntimeContext(thread_id=state["thread_id"]))
    started_at = wl.log_node_started("generate_instagram_node")

    registry = get_registry()
    executor = get_executor()
    capability = registry.find("generate_instagram_post")
    if capability is None:
        raise RuntimeError("Capability 'generate_instagram_post' not available")

    result = retry_operation(
        lambda: executor.execute(
            capability,
            {"property_json": state["property_json"]},
            thread_id=state["thread_id"],
        ),
        logger=logger,
        operation_name="generate_instagram",
    )

    wl.log_node_completed("generate_instagram_node", started_at)
    return {"instagram_result": result}
