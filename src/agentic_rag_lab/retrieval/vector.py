"""In-memory vector retrieval adapter."""

from __future__ import annotations

from collections.abc import Iterable

from agentic_rag_lab.embeddings import EmbeddingProvider, LocalHashEmbeddingProvider
from agentic_rag_lab.schemas import DocumentChunk, RetrievalResult


class InMemoryVectorStore:
    """Store chunk embeddings in memory and search by cosine similarity."""

    def __init__(
        self,
        chunks: Iterable[DocumentChunk],
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self.embedding_provider = embedding_provider or LocalHashEmbeddingProvider()
        self._entries = [
            (chunk, self.embedding_provider.embed(chunk.text))
            for chunk in chunks
        ]

    async def search(self, query: str, limit: int = 5) -> list[RetrievalResult]:
        if limit <= 0:
            raise ValueError("limit must be greater than 0")
        if not query.strip():
            return []

        query_vector = self.embedding_provider.embed(query)
        if _is_zero_vector(query_vector):
            return []

        scored: list[tuple[int, DocumentChunk, float]] = []
        for index, (chunk, chunk_vector) in enumerate(self._entries):
            score = _dot(query_vector, chunk_vector)
            if score > 0:
                scored.append((index, chunk, score))

        scored.sort(key=lambda item: (-item[2], item[0]))
        return [
            RetrievalResult(chunk=chunk, score=score)
            for _, chunk, score in scored[:limit]
        ]


def _dot(left: list[float], right: list[float]) -> float:
    return sum(left_value * right_value for left_value, right_value in zip(left, right))


def _is_zero_vector(vector: list[float]) -> bool:
    return all(value == 0 for value in vector)
