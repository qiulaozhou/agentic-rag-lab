"""Document chunking boundary."""

from typing import Protocol

from agentic_rag_lab.schemas import DocumentChunk, SourceDocument


class Chunker(Protocol):
    def chunk(self, documents: list[SourceDocument]) -> list[DocumentChunk]:
        """Split source documents into retrievable chunks."""
