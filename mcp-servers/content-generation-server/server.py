import json
import logging

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from config import settings
from tools.generate_facebook_post_tool import handle_generate_facebook_post
from tools.generate_instagram_post_tool import handle_generate_instagram_post

logging.basicConfig(level=logging.INFO, format="%(message)s")

mcp = FastMCP(
    "content-generation-server",
    host=settings.server_host,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=settings.allowed_hosts,
    ),
)


@mcp.tool()
def generate_facebook_post(property_json: str, thread_id: str = "") -> str:
    """Generate a Facebook post with hashtags for a real estate property."""
    return handle_generate_facebook_post(property_json, thread_id)


@mcp.tool()
def generate_instagram_post(property_json: str, thread_id: str = "") -> str:
    """Generate an Instagram caption with hashtags for a real estate property."""
    return handle_generate_instagram_post(property_json, thread_id)


class _HealthMiddleware:
    """Injects GET /health without interfering with MCP SSE lifespan.

    Why middleware and not a Starlette Route?
    Starlette's Mount("/", app=sse_app) does not propagate the mounted app's
    lifespan events. The middleware approach passes all ASGI events through
    (including type="lifespan") so FastMCP's startup/shutdown hooks run correctly.
    We only intercept type="http" path="/health" — everything else is untouched.
    """

    def __init__(self, app):
        self._app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"] == "/health":
            body = json.dumps(
                {"status": "ok", "server": "content-generation-server"}
            ).encode()
            await send(
                {"type": "http.response.start", "status": 200,
                 "headers": [[b"content-type", b"application/json"]]}
            )
            await send({"type": "http.response.body", "body": body})
        else:
            await self._app(scope, receive, send)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.info(json.dumps({
        "event": "server_startup",
        "server": "content-generation-server",
        "allowed_hosts": settings.allowed_hosts,
        "port": settings.server_port,
    }))
    app = _HealthMiddleware(mcp.sse_app())
    uvicorn.run(app, host=settings.server_host, port=settings.server_port, log_level="info")
