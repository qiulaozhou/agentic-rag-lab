import asyncio

import pytest

from agentic_rag_lab.retrieval import LocalRetrievalPipeline
from agentic_rag_lab.schemas import DocumentChunk, SourceDocument


def test_pipeline_searches_from_chunks() -> None:
    pipeline = LocalRetrievalPipeline.from_chunks(
        [
            _chunk("chunk-a", "FastAPI health endpoint"),
            _chunk("chunk-b", "retrieval pipeline wraps vector search"),
        ]
    )

    results = asyncio.run(pipeline.search("retrieval pipeline"))

    assert results[0].chunk.id == "chunk-b"
    assert results[0].score > 0


def test_pipeline_builds_chunks_from_documents_and_preserves_metadata() -> None:
    document = SourceDocument(
        id="doc-1",
        text="retrieval pipeline keeps metadata for citation",
        metadata={"source_path": "docs/retrieval.md", "file_type": ".md"},
    )

    pipeline = LocalRetrievalPipeline.from_documents([document], chunk_size=64)
    result = asyncio.run(pipeline.search("metadata citation"))[0]

    assert result.chunk.document_id == "doc-1"
    assert result.chunk.metadata["source_path"] == "docs/retrieval.md"
    assert result.chunk.metadata["file_type"] == ".md"
    assert result.chunk.metadata["chunk_index"] == 0


def test_pipeline_respects_search_limit() -> None:
    pipeline = LocalRetrievalPipeline.from_chunks(
        [
            _chunk("chunk-a", "retrieval alpha"),
            _chunk("chunk-b", "retrieval beta"),
            _chunk("chunk-c", "retrieval gamma"),
        ]
    )

    results = asyncio.run(pipeline.search("retrieval", limit=1))

    assert len(results) == 1


def test_pipeline_returns_empty_results_for_empty_query() -> None:
    pipeline = LocalRetrievalPipeline.from_chunks([_chunk("chunk-a", "retrieval")])

    assert asyncio.run(pipeline.search("   ")) == []


def test_pipeline_validates_limit() -> None:
    pipeline = LocalRetrievalPipeline.from_chunks([_chunk("chunk-a", "retrieval")])

    with pytest.raises(ValueError):
        asyncio.run(pipeline.search("retrieval", limit=0))


def test_pipeline_uses_chunk_parameter_validation() -> None:
    with pytest.raises(ValueError):
        LocalRetrievalPipeline.from_documents(
            [SourceDocument(id="doc-1", text="content", metadata={})],
            chunk_size=4,
            overlap=4,
        )


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
