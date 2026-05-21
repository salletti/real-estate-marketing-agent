from app.application.graphs.checkpointers.memory_checkpointer_provider import (
    MemoryCheckpointerProvider,
)


class TestMemoryCheckpointerProvider:

    def test_returns_same_checkpointer_instance(self):
        provider = MemoryCheckpointerProvider()
        assert provider.get_checkpointer() is provider.get_checkpointer()

    def test_checkpointer_is_not_none(self):
        provider = MemoryCheckpointerProvider()
        assert provider.get_checkpointer() is not None
