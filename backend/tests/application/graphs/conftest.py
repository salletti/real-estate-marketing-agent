import pytest

from app.infrastructure.mcp.capability import Capability
from app.infrastructure.mcp.capability_registry import get_registry

_TEST_CAPABILITIES = [
    Capability(
        name="generate_facebook_post",
        description="Generate a Facebook post",
        input_schema={},
        server_name="content-generation-server",
        server_url="http://content-generation-server:8001/sse",
    ),
    Capability(
        name="generate_instagram_post",
        description="Generate an Instagram post",
        input_schema={},
        server_name="content-generation-server",
        server_url="http://content-generation-server:8001/sse",
    ),
    Capability(
        name="publish_facebook",
        description="Publish to Facebook",
        input_schema={},
        server_name="publication-server",
        server_url="http://publication-server:8002/sse",
    ),
    Capability(
        name="publish_instagram",
        description="Publish to Instagram",
        input_schema={},
        server_name="publication-server",
        server_url="http://publication-server:8002/sse",
    ),
]


@pytest.fixture(autouse=True)
def populate_capability_registry():
    registry = get_registry()
    for cap in _TEST_CAPABILITIES:
        registry.register(cap)
    yield
    registry._capabilities.clear()
