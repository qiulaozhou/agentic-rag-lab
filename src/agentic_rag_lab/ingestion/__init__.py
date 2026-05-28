"""Document ingestion boundary."""

from typing import Protocol

from agentic_rag_lab.schemas import SourceDocument
from agentic_rag_lab.ingestion.text import load_directory, load_text_file


class DocumentIngestor(Protocol):
    def ingest(self, path: str) -> list[SourceDocument]:
        """Load source documents from a path."""


__all__ = ["DocumentIngestor", "load_directory", "load_text_file"]
