import json
import logging
import time

from app.application.observability.runtime_context import RuntimeContext

logger = logging.getLogger(__name__)


class WorkflowLogger:
    """Émet des logs structurés JSON pour les événements runtime du workflow.

    Pourquoi ne pas simplement utiliser logger.info("node started") ?
    Parce qu'une string libre n'est pas interrogeable :
    - impossible de filtrer par thread_id
    - impossible d'agréger les durées de node
    - impossible de corréler avec LangSmith ou un futur système distribué

    En Symfony : c'est la différence entre `echo "erreur"` et Monolog avec
    JSON formatter + ProcessorInterface qui enrichit chaque entrée avec
    request_id, user_id, env, etc.

    Chaque méthode correspond à un événement runtime précis :
    ces événements décrivent le cycle de vie du WORKFLOW, pas la logique métier.
    """

    def __init__(self, context: RuntimeContext) -> None:
        self._ctx = context

    def log_workflow_started(self) -> None:
        self._emit("workflow_started")

    def log_node_started(self, node: str) -> float:
        """Retourne le timestamp monotonic pour calculer la durée d'exécution."""
        self._emit("node_started", node=node)
        return time.monotonic()

    def log_node_completed(self, node: str, started_at: float) -> None:
        duration_ms = round((time.monotonic() - started_at) * 1000)
        self._emit("node_completed", node=node, duration_ms=duration_ms)

    def log_interrupt(self) -> None:
        """Workflow suspendu — checkpoint sauvegardé, attente humaine."""
        self._emit("workflow_interrupted")

    def log_resume(self, approval: str) -> None:
        """Workflow repris — la décision humaine est connue."""
        self._emit("workflow_resumed", approval=approval)

    def log_workflow_recovered(self) -> None:
        """État workflow récupéré depuis le checkpointer persistant (Redis)."""
        self._emit("workflow_recovered")

    def log_error(self, node: str, error: str) -> None:
        self._emit("node_error", node=node, error=error)

    def _emit(self, event: str, **extra) -> None:
        record = {"event": event, **self._ctx.as_dict(), **extra}
        logger.info(json.dumps(record, ensure_ascii=False))
