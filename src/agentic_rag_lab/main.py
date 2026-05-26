from fastapi import FastAPI

from agentic_rag_lab.api.health import router as health_router
from agentic_rag_lab.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(health_router)
    return app


app = create_app()
