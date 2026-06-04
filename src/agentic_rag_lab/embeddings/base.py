"""Embedding provider protocol."""

from typing import Protocol


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> list[float]:
        """Convert text into an embedding vector."""
