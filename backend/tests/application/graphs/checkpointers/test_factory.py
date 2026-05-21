import pytest

import app.application.graphs.checkpointers.factory as factory_module
from app.application.graphs.checkpointers.checkpointer_provider_abc import (
    CheckpointerProvider,
)
from app.application.graphs.checkpointers.factory import get_checkpointer_provider


@pytest.fixture(autouse=True)
def reset_singleton():
    factory_module._provider = None
    yield
    factory_module._provider = None


class TestGetCheckpointerProvider:

    def test_returns_a_provider(self):
        provider = get_checkpointer_provider()
        assert isinstance(provider, CheckpointerProvider)

    def test_returns_same_instance_each_call(self):
        assert get_checkpointer_provider() is get_checkpointer_provider()

    def test_provider_has_a_checkpointer(self):
        assert get_checkpointer_provider().get_checkpointer() is not None
