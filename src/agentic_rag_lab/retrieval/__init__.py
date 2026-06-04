"""Retrieval boundary for vector, keyword, and hybrid search."""

from typing import Protocol

from agentic_rag_lab.schemas import RetrievalResult
from agentic_rag_lab.retrieval.pipeline import LocalRetrievalPipeline
from agentic_rag_lab.retrieval.vector import InMemoryVectorStore


class Retriever(Protocol):
    async def search(self, query: str, limit: int = 5) -> list[RetrievalResult]:
        """Return relevant chunks for a query."""


__all__ = ["InMemoryVectorStore", "LocalRetrievalPipeline", "Retriever"]
