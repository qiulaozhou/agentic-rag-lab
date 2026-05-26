"""Retrieval boundary for vector, keyword, and hybrid search."""

from typing import Protocol

from agentic_rag_lab.schemas import RetrievalResult


class Retriever(Protocol):
    async def search(self, query: str, limit: int = 5) -> list[RetrievalResult]:
        """Return relevant chunks for a query."""
