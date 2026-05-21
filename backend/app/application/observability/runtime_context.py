from dataclasses import dataclass, field

from app.core.config import settings


@dataclass
class RuntimeContext:
    """Metadata de corrélation pour une exécution workflow.

    thread_id est le correlation ID principal : il relie les checkpoints LangGraph,
    les traces LangSmith et les logs structurés sous un identifiant unique.

    C'est l'équivalent d'un trace_id en OpenTelemetry / Datadog.
    En Symfony : c'est le champ `extra.request_id` que Monolog propage dans
    tous les handlers (fichier, Slack, ELK) via un ProcessorInterface.
    """

    thread_id: str
    workflow: str = "social_media"
    runtime_provider: str = field(default_factory=lambda: settings.checkpointer_provider)

    def as_dict(self) -> dict:
        return {
            "thread_id": self.thread_id,
            "workflow": self.workflow,
            "runtime_provider": self.runtime_provider,
        }
