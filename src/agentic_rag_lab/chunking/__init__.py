"""Document chunking boundary."""

from typing import Protocol

from agentic_rag_lab.schemas import DocumentChunk, SourceDocument
from agentic_rag_lab.chunking.text import (
    chunk_document,
    chunk_documents,
    chunk_text,
)


class Chunker(Protocol):
    def chunk(self, documents: list[SourceDocument]) -> list[DocumentChunk]:
        """Split source documents into retrievable chunks."""


__all__ = ["Chunker", "chunk_document", "chunk_documents", "chunk_text"]
