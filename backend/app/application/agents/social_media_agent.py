import json
import logging
import uuid
from typing import Any, Dict

from langgraph.types import Command

from app.application.graphs.social_media_graph import build_social_media_graph
from app.application.graphs.state import SocialMediaState
from app.application.intent.social_media_intent_resolver import SocialMediaIntentResolver
from app.application.observability.langsmith import build_run_config
from app.application.observability.runtime_context import RuntimeContext
from app.application.observability.workflow_logger import WorkflowLogger
from app.infrastructure.db.repositories.social_media_publication_repository import SocialMediaPublicationRepository

logger = logging.getLogger(__name__)

_GRAPH_FAILURE: Dict[str, Any] = {
    "success": False,
    "error": "graph_error",
    "data": {},
}


class SocialMediaAgent:

    def __init__(self, publication_repository: SocialMediaPublicationRepository | None = None) -> None:
        self._graph = build_social_media_graph()
        self._intent_resolver = SocialMediaIntentResolver()
        self._publication_repository = publication_repository

    def run(self, input: str, property_json: str) -> str:
        # Chaque appel à run() crée un draft indépendant identifié par son propre thread_id.
        thread_id = str(uuid.uuid4())

        wl = WorkflowLogger(RuntimeContext(thread_id=thread_id))
        wl.log_workflow_started()

        intent = self._intent_resolver.resolve(input)

        state: SocialMediaState = {
            "thread_id": thread_id,
            "input": input,
            "property_json": property_json,
            "generate_facebook": intent["generate_facebook"],
            "generate_instagram": intent["generate_instagram"],
            "facebook_result": None,
            "instagram_result": None,
            "final_result": None,
            "approval_status": None,
        }

        config = build_run_config(thread_id)

        try:
            result = self._graph.invoke(state, config=config)
        except Exception:
            logger.exception("Graph execution failed")
            return json.dumps(_GRAPH_FAILURE, ensure_ascii=False)

        # invoke() ne lève pas d'exception sur interrupt : il retourne le state
        # avec une clé "__interrupt__" si le workflow est suspendu.
        # C'est un état métier normal, pas une erreur.
        if result.get("__interrupt__"):
            wl.log_interrupt()
            if self._publication_repository:
                # payload = final_result complet (posts, hashtags, images par plateforme).
                # Source de vérité durable pour la phase de publication.
                self._publication_repository.save(
                    thread_id=thread_id,
                    status="draft",
                    approval_status="pending",
                    payload=result.get("final_result"),
                )
            return json.dumps({
                "success": True,
                "error": None,
                "data": {
                    "thread_id": thread_id,
                    "status": "draft",
                    "approval_status": "pending",
                },
            }, ensure_ascii=False)

        final = result.get("final_result") or _GRAPH_FAILURE
        return json.dumps(final, ensure_ascii=False)

    def resume(self, thread_id: str, approval: str) -> str:
        wl = WorkflowLogger(RuntimeContext(thread_id=thread_id))
        config = build_run_config(thread_id)

        # Réhydratation avant resume:
        # on remet final_result depuis la DB dans le state du graphe, pour que les nodes
        # publish_* retrouvent le contenu (post/caption/hashtags/images) même si l'état
        # mémoire du checkpointer n'est plus complet.
        if self._publication_repository:
            workflow = self._publication_repository.find_by_thread_id(thread_id)
            if workflow and workflow.payload:
                self._graph.update_state(config, {"final_result": workflow.payload})
                # L'état a été récupéré depuis la DB (checkpoint durable) — c'est le
                # scénario "recovery" : le process a redémarré ou l'état mémoire est perdu.
                wl.log_workflow_recovered()

        wl.log_resume(approval)

        try:
            # Command(resume=approval) fournit la réponse à l'interrupt en attente.
            # Dans wait_for_approval_node, interrupt(...) "retourne" alors cette valeur
            # ("approved" / "rejected"), utilisée pour router la suite du workflow.
            result = self._graph.invoke(Command(resume=approval), config=config)
        except Exception:
            logger.exception("Graph resume failed")
            return json.dumps(_GRAPH_FAILURE, ensure_ascii=False)

        # Mise à jour DB uniquement après que le workflow a changé d'état avec succès.
        if self._publication_repository:
            self._publication_repository.update_approval_status(
                thread_id=thread_id,
                approval_status=approval,
            )

        final = result.get("final_result") or _GRAPH_FAILURE
        return json.dumps(final, ensure_ascii=False)
