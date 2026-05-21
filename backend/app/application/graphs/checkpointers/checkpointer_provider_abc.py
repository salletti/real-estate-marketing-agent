from abc import ABC, abstractmethod
from typing import Any


class CheckpointerProvider(ABC):
    @abstractmethod
    def get_checkpointer(self) -> Any:
        """Retourne l'instance à passer à `workflow.compile(checkpointer=...)`."""
        pass
