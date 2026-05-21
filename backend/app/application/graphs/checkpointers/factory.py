from functools import lru_cache

from app.application.graphs.checkpointers.checkpointer_provider_abc import CheckpointerProvider
from app.application.graphs.checkpointers.memory_checkpointer_provider import MemoryCheckpointerProvider
from app.core.config import settings


@lru_cache(maxsize=1)
def get_checkpointer_provider() -> CheckpointerProvider:
    if settings.checkpointer_provider == "redis":
        from app.application.graphs.checkpointers.redis_checkpointer_provider import (
            RedisCheckpointerProvider,
        )
        return RedisCheckpointerProvider(settings.redis_url)
    return MemoryCheckpointerProvider()