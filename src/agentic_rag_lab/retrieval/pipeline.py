"""Local retrieval pipeline boundary."""

from __future__ import annotations

from collections.abc import Iterable

from agentic_rag_lab.chunking import chunk_documents
from agentic_rag_lab.embeddings import EmbeddingProvider
from agentic_rag_lab.retrieval.vector import InMemoryVectorStore
from agentic_rag_lab.schemas import DocumentChunk, RetrievalResult, SourceDocument


class LocalRetrievalPipeline:
    """Compose chunking and local vector search behind one search boundary."""

    def __init__(self, vector_store: InMemoryVectorStore) -> None:
        self._vector_store = vector_store

    @classmethod
    def from_chunks(
        cls,
        chunks: Iterable[DocumentChunk],
        embedding_provider: EmbeddingProvider | None = None,
    ) -> "LocalRetrievalPipeline":
        return cls(InMemoryVectorStore(chunks, embedding_provider=embedding_provider))

    @classmethod
    def from_documents(
        cls,
        documents: list[SourceDocument],
        chunk_size: int,
        overlap: int = 0,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> "LocalRetrievalPipeline":
        chunks = chunk_documents(documents, chunk_size=chunk_size, overlap=overlap)
        return cls.from_chunks(chunks, embedding_provider=embedding_provider)

    async def search(self, query: str, limit: int = 5) -> list[RetrievalResult]:
        return await self._vector_store.search(query=query, limit=limit)
