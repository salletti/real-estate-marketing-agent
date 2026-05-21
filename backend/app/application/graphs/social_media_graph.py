from langgraph.graph import END, START, StateGraph

# Le checkpointer est obtenu via la factory, pas instancié directement.
# Raison : le graph builder ne doit pas connaître l'implémentation concrète du
# runtime (MemorySaver, PostgreSQLSaver...). Seule la factory décide du backend.
from app.application.graphs.checkpointers.factory import get_checkpointer_provider

from app.application.graphs.nodes.aggregate_drafts_node import aggregate_drafts_node
from app.application.graphs.nodes.generate_facebook_node import generate_facebook_node
from app.application.graphs.nodes.generate_instagram_node import generate_instagram_node
from app.application.graphs.nodes.publish_facebook_node import publish_facebook_node
from app.application.graphs.nodes.publish_instagram_node import publish_instagram_node
from app.application.graphs.nodes.wait_for_approval_node import wait_for_approval_node
from app.application.graphs.state import SocialMediaState


def _route_entry(state: SocialMediaState) -> str:
    if state["generate_facebook"]:
        return "facebook_node"
    if state["generate_instagram"]:
        return "instagram_node"
    return "aggregate_drafts"


def _after_facebook(state: SocialMediaState) -> str:
    if state["generate_instagram"]:
        return "instagram_node"
    return "aggregate_drafts"


def _route_after_approval(state: SocialMediaState) -> str:
    # Routeur exécuté juste après `wait_for_approval`:
    # - `approval_status` est injecté au resume (`Command(resume=...)`),
    # - si approuvé, on repart vers les nodes de publication,
    # - sinon le workflow se termine immédiatement.
    # Les flags `generate_*` restent la source de vérité des plateformes visées.
    if state.get("approval_status") != "approved":
        return END
    if state["generate_facebook"]:
        return "publish_facebook"
    if state["generate_instagram"]:
        return "publish_instagram"
    return END


def _after_publish_facebook(state: SocialMediaState) -> str:
    if state["generate_instagram"]:
        return "publish_instagram"
    return END


def build_social_media_graph():
    workflow = StateGraph(SocialMediaState)

    workflow.add_node("facebook_node", generate_facebook_node)
    workflow.add_node("instagram_node", generate_instagram_node)
    workflow.add_node("aggregate_drafts", aggregate_drafts_node)
    workflow.add_node("wait_for_approval", wait_for_approval_node)
    workflow.add_node("publish_facebook", publish_facebook_node)
    workflow.add_node("publish_instagram", publish_instagram_node)

    workflow.add_conditional_edges(START, _route_entry)
    workflow.add_conditional_edges("facebook_node", _after_facebook)
    workflow.add_edge("instagram_node", "aggregate_drafts")
    workflow.add_edge("aggregate_drafts", "wait_for_approval")
    workflow.add_conditional_edges("wait_for_approval", _route_after_approval)
    workflow.add_conditional_edges("publish_facebook", _after_publish_facebook)
    workflow.add_edge("publish_instagram", END)

    # Le graph délègue le choix du runtime à la factory.
    # La topologie du graph (nœuds, arêtes, state) est indépendante du backend
    # de persistence du runtime — ce sont deux responsabilités distinctes.
    checkpointer_provider = get_checkpointer_provider()
    return workflow.compile(checkpointer=checkpointer_provider.get_checkpointer())
