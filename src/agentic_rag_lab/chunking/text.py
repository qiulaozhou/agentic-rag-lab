"""Deterministic text chunking helpers."""

from __future__ import annotations

from collections.abc import Iterable

from agentic_rag_lab.schemas import DocumentChunk, SourceDocument


def chunk_text(text: str, chunk_size: int, overlap: int = 0) -> list[str]:
    """Split text with a fixed character window."""

    return [
        text[start:end]
        for start, end in _iter_chunk_spans(text, chunk_size=chunk_size, overlap=overlap)
    ]


def chunk_document(
    document: SourceDocument,
    chunk_size: int,
    overlap: int = 0,
) -> list[DocumentChunk]:
    """Split a source document into stable document chunks."""

    chunks: list[DocumentChunk] = []
    for chunk_index, (start, end) in enumerate(
        _iter_chunk_spans(document.text, chunk_size=chunk_size, overlap=overlap)
    ):
        metadata = dict(document.metadata)
        metadata.update(
            {
                "chunk_index": chunk_index,
                "start": start,
                "end": end,
            }
        )
        chunks.append(
            DocumentChunk(
                id=f"{document.id}:chunk-{chunk_index}",
                document_id=document.id,
                text=document.text[start:end],
                metadata=metadata,
            )
        )

    return chunks


def chunk_documents(
    documents: list[SourceDocument],
    chunk_size: int,
    overlap: int = 0,
) -> list[DocumentChunk]:
    """Split multiple source documents while preserving document order."""

    chunks: list[DocumentChunk] = []
    for document in documents:
        chunks.extend(
            chunk_document(document, chunk_size=chunk_size, overlap=overlap)
        )
    return chunks


def _iter_chunk_spans(
    text: str,
    chunk_size: int,
    overlap: int,
) -> Iterable[tuple[int, int]]:
    _validate_chunk_parameters(chunk_size=chunk_size, overlap=overlap)

    if not text.strip():
        return

    step = chunk_size - overlap
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        yield start, end
        if end == text_length:
            break
        start += step


def _validate_chunk_parameters(chunk_size: int, overlap: int) -> None:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0:
        raise ValueError("overlap must be greater than or equal to 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")


__all__ = ["chunk_document", "chunk_documents", "chunk_text"]
