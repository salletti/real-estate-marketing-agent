"""Tests du routing dynamique de get_checkpointer_provider().

Vérifie que la factory sélectionne le bon provider selon
settings.checkpointer_provider ("memory" ou "redis").
"""
from unittest.mock import MagicMock, patch

import pytest

import app.application.graphs.checkpointers.factory as factory_module
from app.application.graphs.checkpointers.factory import get_checkpointer_provider
from app.application.graphs.checkpointers.memory_checkpointer_provider import (
    MemoryCheckpointerProvider,
)
from app.application.graphs.checkpointers.redis_checkpointer_provider import (
    RedisCheckpointerProvider,
)
from app.core.config import settings

_REDIS_MODULE = "app.application.graphs.checkpointers.redis_checkpointer_provider"


@pytest.fixture(autouse=True)
def reset_singleton():
    """Remet le cache lru_cache à None avant et après chaque test.

    Sans ce reset, le lazy singleton conserverait sa valeur entre les tests
    et fausserait les assertions sur le type de provider retourné.
    """
    factory_module.get_checkpointer_provider.cache_clear()
    yield
    factory_module.get_checkpointer_provider.cache_clear()


def _mock_redis_deps():
    """Context manager qui mocke Redis et RedisSaver pour éviter une vraie connexion."""
    mock_client = MagicMock()
    mock_saver = MagicMock()

    redis_patch = patch(f"{_REDIS_MODULE}.Redis")
    saver_patch = patch(f"{_REDIS_MODULE}.RedisSaver")
    return redis_patch, saver_patch, mock_client, mock_saver


class TestFactoryRoutingMemory:

    def test_retourne_memory_provider_par_defaut(self, monkeypatch):
        """Config 'memory' → MemoryCheckpointerProvider."""
        monkeypatch.setattr(settings, "checkpointer_provider", "memory")
        provider = get_checkpointer_provider()
        assert isinstance(provider, MemoryCheckpointerProvider)

    def test_retourne_memory_si_valeur_inconnue(self, monkeypatch):
        """Toute valeur autre que 'redis' fall back sur MemoryCheckpointerProvider."""
        monkeypatch.setattr(settings, "checkpointer_provider", "unknown_value")
        provider = get_checkpointer_provider()
        assert isinstance(provider, MemoryCheckpointerProvider)


class TestFactoryRoutingRedis:

    def test_retourne_redis_provider_si_config_redis(self, monkeypatch):
        """Config 'redis' → RedisCheckpointerProvider."""
        monkeypatch.setattr(settings, "checkpointer_provider", "redis")
        monkeypatch.setattr(settings, "redis_url", "redis://localhost:6379")

        with patch(f"{_REDIS_MODULE}.Redis") as mock_redis_cls, \
             patch(f"{_REDIS_MODULE}.RedisSaver") as mock_saver_cls:
            mock_redis_cls.from_url.return_value = MagicMock()
            mock_saver_cls.return_value = MagicMock()
            provider = get_checkpointer_provider()

        assert isinstance(provider, RedisCheckpointerProvider)

    def test_redis_provider_recoit_la_bonne_url(self, monkeypatch):
        """Le provider Redis est instancié avec l'URL depuis les settings."""
        expected_url = "redis://my-redis:6380"
        monkeypatch.setattr(settings, "checkpointer_provider", "redis")
        monkeypatch.setattr(settings, "redis_url", expected_url)

        with patch(f"{_REDIS_MODULE}.Redis") as mock_redis_cls, \
             patch(f"{_REDIS_MODULE}.RedisSaver"):
            mock_redis_cls.from_url.return_value = MagicMock()
            get_checkpointer_provider()

        mock_redis_cls.from_url.assert_called_once_with(expected_url)


class TestFactoryLazySingleton:

    def test_lazy_singleton_meme_instance(self):
        """Deux appels successifs retournent exactement la même instance."""
        assert get_checkpointer_provider() is get_checkpointer_provider()

    def test_singleton_reset_permet_nouveau_provider(self, monkeypatch):
        """Après reset du singleton, un nouveau provider est créé selon les settings."""
        monkeypatch.setattr(settings, "checkpointer_provider", "memory")
        first = get_checkpointer_provider()

        factory_module.get_checkpointer_provider.cache_clear()  # reset explicite

        second = get_checkpointer_provider()
        assert first is not second
