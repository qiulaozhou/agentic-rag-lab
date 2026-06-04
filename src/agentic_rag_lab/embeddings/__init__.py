"""Embedding provider boundary and local implementations."""

from agentic_rag_lab.embeddings.base import EmbeddingProvider
from agentic_rag_lab.embeddings.factory import create_embedding_provider
from agentic_rag_lab.embeddings.local import LocalHashEmbeddingProvider
from agentic_rag_lab.embeddings.openai_compatible import OpenAICompatibleEmbeddingProvider

__all__ = [
    "EmbeddingProvider",
    "LocalHashEmbeddingProvider",
    "OpenAICompatibleEmbeddingProvider",
    "create_embedding_provider",
]
