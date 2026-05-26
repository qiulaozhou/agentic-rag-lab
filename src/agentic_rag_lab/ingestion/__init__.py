"""Document ingestion boundary.

Future tasks will add Markdown/TXT and PDF-specific ingestors here.
"""

from typing import Protocol

from agentic_rag_lab.schemas import SourceDocument


class DocumentIngestor(Protocol):
    def ingest(self, path: str) -> list[SourceDocument]:
        """Load source documents from a path."""
