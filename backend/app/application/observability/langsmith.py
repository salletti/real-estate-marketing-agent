import logging
import os

from app.core.config import settings

logger = logging.getLogger(__name__)


def init_tracing() -> None:
    """Active LangSmith si la config le permet.

    LangGraph lit LANGCHAIN_TRACING_V2 / LANGCHAIN_API_KEY automatiquement à
    chaque invoke(). On se contente de positionner les env vars au démarrage.
    Sans clé API : comportement normal, aucune erreur.
    """
    if not settings.langchain_tracing_v2 or not settings.langchain_api_key:
        logger.info("LangSmith tracing disabled")
        return

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
    os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
    logger.info("LangSmith tracing enabled (project=%s)", settings.langchain_project)


def build_run_config(thread_id: str) -> dict:
    """Construit le RunnableConfig LangGraph avec metadata et tags observability.

    thread_id joue le rôle de correlation ID dans LangSmith :
    toutes les spans d'une même exécution workflow sont regroupées sous ce thread_id.
    C'est l'équivalent d'un trace_id en distributed tracing (OpenTelemetry, Datadog).

    metadata et tags sont passés tels quels à LangSmith — ils permettent de
    filtrer et regrouper les runs dans l'UI (par workflow, par runtime, par thread).
    """
    return {
        "configurable": {"thread_id": thread_id},
        "metadata": {
            "thread_id": thread_id,
            "workflow": "social_media",
            "runtime": settings.checkpointer_provider,
        },
        "tags": [
            "langgraph",
            "social-media",
            f"runtime:{settings.checkpointer_provider}",
        ],
    }
