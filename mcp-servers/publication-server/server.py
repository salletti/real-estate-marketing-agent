import json
import logging

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from config import settings
from tools.publish_facebook_tool import handle_publish_facebook
from tools.publish_instagram_tool import handle_publish_instagram

logging.basicConfig(level=logging.INFO, format="%(message)s")

mcp = FastMCP(
    "publication-server",
    host=settings.server_host,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=settings.allowed_hosts,
    ),
)


@mcp.tool()
def publish_facebook(post: str, images: list[str], thread_id: str = "") -> str:
    """Publish a Facebook post with optional images to the Facebook platform."""
    return handle_publish_facebook(post, images, thread_id)


@mcp.tool()
def publish_instagram(caption: str, images: list[str], thread_id: str = "") -> str:
    """Publish an Instagram caption with optional images to the Instagram platform."""
    return handle_publish_instagram(caption, images, thread_id)


class _HealthMiddleware:
    """Injects GET /health without interfering with MCP SSE lifespan.

    Même rationale que content-generation-server : le middleware laisse passer
    les events de type "lifespan" que Starlette Route supprimerait.
    On intercepte uniquement type="http" path="/health".
    """

    def __init__(self, app):
        self._app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"] == "/health":
            body = json.dumps(
                {"status": "ok", "server": "publication-server"}
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
        "server": "publication-server",
        "allowed_hosts": settings.allowed_hosts,
        "port": settings.server_port,
    }))
    app = _HealthMiddleware(mcp.sse_app())
    uvicorn.run(app, host=settings.server_host, port=settings.server_port, log_level="info")
