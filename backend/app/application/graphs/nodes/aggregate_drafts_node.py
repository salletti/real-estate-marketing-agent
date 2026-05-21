from app.application.graphs.state import SocialMediaState
from app.application.observability.runtime_context import RuntimeContext
from app.application.observability.workflow_logger import WorkflowLogger


def aggregate_drafts_node(state: SocialMediaState) -> dict:
    wl = WorkflowLogger(RuntimeContext(thread_id=state["thread_id"]))
    started_at = wl.log_node_started("aggregate_drafts_node")

    platforms: dict = {}

    facebook = state.get("facebook_result")
    if facebook and facebook.get("success"):
        facebook_data = facebook.get("data", {})
        platforms["facebook"] = {
            "generated": True,
            "post": facebook_data.get("post", ""),
            "hashtags": facebook_data.get("hashtags", []),
            "images": [],
        }

    instagram = state.get("instagram_result")
    if instagram and instagram.get("success"):
        instagram_data = instagram.get("data", {})
        platforms["instagram"] = {
            "generated": True,
            "caption": instagram_data.get("caption", ""),
            "hashtags": instagram_data.get("hashtags", []),
            "images": [],
        }

    if not platforms:
        platform_errors: dict = {}
        if facebook and not facebook.get("success"):
            platform_errors["facebook"] = facebook.get("error", "unknown")
        if instagram and not instagram.get("success"):
            platform_errors["instagram"] = instagram.get("error", "unknown")
        wl.log_node_completed("aggregate_drafts_node", started_at)
        return {
            "final_result": {
                "success": False,
                "error": "no_platform_generated",
                "data": {"platform_errors": platform_errors},
            }
        }

    wl.log_node_completed("aggregate_drafts_node", started_at)
    return {
        "final_result": {
            "success": True,
            "error": None,
            "data": {
                "status": "draft",
                "approval_status": "pending",
                "platforms": platforms,
            },
        }
    }
