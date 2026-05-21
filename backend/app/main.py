from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.drafts.draft_routes import router as drafts_router
from app.api.health import router as health_router
from app.api.social_media import router as social_media_router
from app.application.observability.langsmith import init_tracing
from app.core.config import settings
from app.infrastructure.mcp.capability_registry import get_registry
from app.infrastructure.mcp.discovery import MCPDiscovery
from app.infrastructure.mcp.registry_loader import RegistryLoader


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_tracing()
    registry = get_registry()
    discovery = MCPDiscovery(registry)
    loader = RegistryLoader(registry, discovery)
    await loader.load()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Agent IA de marketing immobilier — génération et publication de contenus.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(social_media_router)
app.include_router(drafts_router)
