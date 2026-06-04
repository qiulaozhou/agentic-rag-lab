"""Embedding provider factory."""

from agentic_rag_lab.config import Settings
from agentic_rag_lab.embeddings.base import EmbeddingProvider
from agentic_rag_lab.embeddings.local import LocalHashEmbeddingProvider
from agentic_rag_lab.embeddings.openai_compatible import OpenAICompatibleEmbeddingProvider


def create_embedding_provider(settings: Settings) -> EmbeddingProvider:
    """Create the configured embedding provider."""

    if settings.embedding_provider == "local_hash":
        return LocalHashEmbeddingProvider()
    if settings.embedding_provider == "openai_compatible":
        return OpenAICompatibleEmbeddingProvider(
            api_key=settings.openai_compatible_api_key,
            base_url=settings.openai_compatible_base_url,
            model=settings.openai_compatible_embedding_model,
        )

    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")


__all__ = ["create_embedding_provider"]
