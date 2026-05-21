"""Tests unitaires — RedisCheckpointerProvider.

Redis et RedisSaver sont mockés : aucune connexion réelle requise.
L'objectif est de vérifier la logique du provider (lifecycle, délégation),
pas le comportement de Redis lui-même.
"""
from unittest.mock import MagicMock, patch

import pytest

from app.application.graphs.checkpointers.checkpointer_provider_abc import (
    CheckpointerProvider,
)
from app.application.graphs.checkpointers.redis_checkpointer_provider import (
    RedisCheckpointerProvider,
)

_REDIS_URL = "redis://localhost:6379"
_MODULE = "app.application.graphs.checkpointers.redis_checkpointer_provider"


def _make_provider() -> tuple[RedisCheckpointerProvider, MagicMock, MagicMock]:
    """Crée un provider avec Redis et RedisSaver mockés.

    Retourne (provider, mock_redis_client, mock_saver).
    """
    mock_client = MagicMock()
    mock_saver = MagicMock()

    with patch(f"{_MODULE}.Redis") as mock_redis_cls, \
         patch(f"{_MODULE}.RedisSaver") as mock_saver_cls:
        mock_redis_cls.from_url.return_value = mock_client
        mock_saver_cls.return_value = mock_saver
        provider = RedisCheckpointerProvider(_REDIS_URL)

    return provider, mock_client, mock_saver


class TestRedisCheckpointerProviderInstanciation:

    def test_est_une_instance_de_checkpointer_provider(self):
        """RedisCheckpointerProvider implémente l'ABC CheckpointerProvider."""
        provider, _, _ = _make_provider()
        assert isinstance(provider, CheckpointerProvider)

    def test_instanciable_sans_erreur(self):
        """Le provider s'instancie sans lever d'exception."""
        provider, _, _ = _make_provider()
        assert provider is not None

    def test_redis_from_url_appele_avec_bonne_url(self):
        """Redis.from_url() est appelé avec l'URL fournie."""
        mock_client = MagicMock()
        mock_saver = MagicMock()

        with patch(f"{_MODULE}.Redis") as mock_redis_cls, \
             patch(f"{_MODULE}.RedisSaver") as mock_saver_cls:
            mock_redis_cls.from_url.return_value = mock_client
            mock_saver_cls.return_value = mock_saver
            RedisCheckpointerProvider(_REDIS_URL)

        mock_redis_cls.from_url.assert_called_once_with(_REDIS_URL)

    def test_setup_appele_une_fois_au_demarrage(self):
        """setup() est appelé exactement une fois lors de l'instanciation.

        setup() crée les index Redis (RedisJSON + RediSearch).
        Il doit être appelé avant tout usage du saver.
        """
        _, _, mock_saver = _make_provider()
        mock_saver.setup.assert_called_once()


class TestRedisCheckpointerProviderGetCheckpointer:

    def test_get_checkpointer_retourne_redis_saver(self):
        """get_checkpointer() retourne l'instance RedisSaver créée."""
        provider, _, mock_saver = _make_provider()
        assert provider.get_checkpointer() is mock_saver

    def test_get_checkpointer_idempotent(self):
        """Deux appels successifs retournent exactement la même instance."""
        provider, _, _ = _make_provider()
        assert provider.get_checkpointer() is provider.get_checkpointer()


class TestRedisCheckpointerProviderClose:

    def test_close_appelle_client_close(self):
        """close() délègue au client Redis sous-jacent."""
        provider, mock_client, _ = _make_provider()
        provider.close()
        mock_client.close.assert_called_once()
