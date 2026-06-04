from fastapi import FastAPI

from agentic_rag_lab.api.answer import router as answer_router
from agentic_rag_lab.api.health import router as health_router
from agentic_rag_lab.api.knowledge_base import router as knowledge_base_router
from agentic_rag_lab.config import Settings, get_settings
from agentic_rag_lab.embeddings import create_embedding_provider
from agentic_rag_lab.generation import create_answer_generator
from agentic_rag_lab.knowledge_base import DiskBackedKnowledgeBaseRegistry


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    embedding_provider = create_embedding_provider(settings)
    answer_generator = create_answer_generator(settings)

    app = FastAPI(title=settings.app_name)
    app.state.settings = settings
    app.state.embedding_provider = embedding_provider
    app.state.answer_generator = answer_generator
    app.state.knowledge_bases = DiskBackedKnowledgeBaseRegistry(
        settings.knowledge_base_storage_path,
        embedding_provider=embedding_provider,
        answer_generator=answer_generator,
    )
    app.include_router(answer_router)
    app.include_router(knowledge_base_router)
    app.include_router(health_router)
    return app


app = create_app()
