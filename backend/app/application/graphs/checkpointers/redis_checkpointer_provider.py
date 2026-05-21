import json
import logging

from redis import Redis
from langgraph.checkpoint.redis import RedisSaver

from app.application.graphs.checkpointers.checkpointer_provider_abc import (
    CheckpointerProvider,
)

logger = logging.getLogger(__name__)


class RedisCheckpointerProvider(CheckpointerProvider):
    """Provider Redis — checkpoints durables, survivent au redémarrage process.

    Utilise le constructeur direct RedisSaver(redis_client=...) plutôt que
    from_conn_string() qui retourne un context manager inadapté à un service
    long-running.

    setup() crée les index Redis (RedisJSON + RediSearch) au démarrage.
    close() libère la connexion Redis — prévu pour FastAPI lifespan events (futur).
    """

    def __init__(self, redis_url: str) -> None:
        self._client = Redis.from_url(redis_url)
        self._saver = RedisSaver(redis_client=self._client)
        self._saver.setup()
        logger.info(json.dumps({"event": "checkpointer_initialized", "provider": "redis"}))

    def get_checkpointer(self) -> RedisSaver:
        return self._saver

    def close(self) -> None:
        """Libère la connexion Redis. Appeler depuis FastAPI lifespan (futur)."""
        self._client.close()
