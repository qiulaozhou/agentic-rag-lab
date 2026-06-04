import asyncio

import pytest

from agentic_rag_lab.embeddings import LocalHashEmbeddingProvider
from agentic_rag_lab.retrieval import InMemoryVectorStore
from agentic_rag_lab.schemas import DocumentChunk


def test_vector_store_returns_most_relevant_chunk_first() -> None:
    chunks = [
        _chunk("chunk-a", "FastAPI health endpoint smoke test"),
        _chunk("chunk-b", "Vector retrieval adapter stores document chunks"),
        _chunk("chunk-c", "Markdown ingestion reads source files"),
    ]
    store = InMemoryVectorStore(chunks, LocalHashEmbeddingProvider())

    results = asyncio.run(store.search("vector retrieval chunks"))

    assert results[0].chunk.id == "chunk-b"
    assert results[0].score > results[1].score


def test_vector_store_respects_limit() -> None:
    chunks = [
        _chunk("chunk-a", "retrieval alpha"),
        _chunk("chunk-b", "retrieval beta"),
        _chunk("chunk-c", "retrieval gamma"),
    ]
    store = InMemoryVectorStore(chunks)

    results = asyncio.run(store.search("retrieval", limit=2))

    assert len(results) == 2


def test_vector_store_preserves_chunk_metadata_and_document_id() -> None:
    chunk = _chunk(
        "doc-1:chunk-0",
        "source metadata retrieval",
        document_id="doc-1",
        metadata={"source_path": "docs/source.md", "chunk_index": 0},
    )
    store = InMemoryVectorStore([chunk])

    result = asyncio.run(store.search("metadata"))[0]

    assert result.chunk.document_id == "doc-1"
    assert result.chunk.metadata["source_path"] == "docs/source.md"
    assert result.chunk.metadata["chunk_index"] == 0


def test_vector_store_returns_empty_results_for_empty_query() -> None:
    store = InMemoryVectorStore([_chunk("chunk-a", "retrieval")])

    assert asyncio.run(store.search("   ")) == []


def test_vector_store_validates_limit() -> None:
    store = InMemoryVectorStore([_chunk("chunk-a", "retrieval")])

    with pytest.raises(ValueError):
        asyncio.run(store.search("retrieval", limit=0))


def _chunk(
    chunk_id: str,
    text: str,
    document_id: str = "doc-1",
    metadata: dict[str, str | int] | None = None,
) -> DocumentChunk:
    return DocumentChunk(
        id=chunk_id,
        document_id=document_id,
        text=text,
        metadata=metadata or {},
    )
