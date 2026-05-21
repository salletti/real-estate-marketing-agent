import pytest

from app.infrastructure.mcp.capability import Capability


class TestCapability:

    def test_instantiates_with_all_fields(self):
        cap = Capability(
            name="generate_facebook_post",
            description="Generate a Facebook post",
            input_schema={"type": "object"},
            server_name="content-generation-server",
            server_url="http://content-generation-server:8001/sse",
        )
        assert cap.name == "generate_facebook_post"
        assert cap.description == "Generate a Facebook post"
        assert cap.input_schema == {"type": "object"}
        assert cap.server_name == "content-generation-server"
        assert cap.server_url == "http://content-generation-server:8001/sse"

    def test_frozen_raises_on_mutation(self):
        cap = Capability(
            name="test",
            description="",
            input_schema={},
            server_name="server",
            server_url="http://server/sse",
        )
        with pytest.raises(Exception):
            cap.name = "modified"

    def test_empty_description_is_accepted(self):
        cap = Capability(
            name="tool",
            description="",
            input_schema={},
            server_name="server",
            server_url="http://server/sse",
        )
        assert cap.description == ""

    def test_empty_input_schema_is_accepted(self):
        cap = Capability(
            name="tool",
            description="desc",
            input_schema={},
            server_name="server",
            server_url="http://server/sse",
        )
        assert cap.input_schema == {}
