import json
import logging

from langgraph.checkpoint.memory import MemorySaver

from app.application.graphs.checkpointers.checkpointer_provider_abc import (
    CheckpointerProvider,
)

logger = logging.getLogger(__name__)


class MemoryCheckpointerProvider(CheckpointerProvider):
    """Provider basé sur `MemorySaver`.

    C'est le mode le plus simple pour développer/tester:
    - les checkpoints sont stockés en RAM (rapide, zéro dépendance externe),
    - mais ils disparaissent quand le process s'arrête.
    """

    def __init__(self) -> None:
        self._checkpointer = MemorySaver()
        # Événement système : pas de thread_id (le provider est un singleton,
        # il n'appartient pas à une exécution workflow spécifique).
        logger.info(json.dumps({"event": "checkpointer_initialized", "provider": "memory"}))

    def get_checkpointer(self) -> MemorySaver:
        return self._checkpointer
