import asyncio
from pathlib import Path

import pytest

from agentic_rag_lab.generation import LocalAnswerPipeline, MinimumEvidenceRefusalPolicy
from agentic_rag_lab.generation.refusal import DEFAULT_REFUSAL_TEXT
from agentic_rag_lab.ingestion import load_text_file
from agentic_rag_lab.schemas import DocumentChunk, SourceDocument


def test_answer_pipeline_answers_from_chunks_with_citation() -> None:
    pipeline = LocalAnswerPipeline.from_chunks(
        [
            _chunk(
                "chunk-a",
                "RAG answers need citations for traceability.",
                metadata={"source_path": "docs/rag.md", "chunk_index": 0},
            ),
            _chunk(
                "chunk-b",
                "FastAPI health endpoints support smoke tests.",
                metadata={"source_path": "docs/api.md", "chunk_index": 0},
            ),
        ]
    )

    answer = asyncio.run(pipeline.answer("Why do RAG answers need citations?", limit=1))

    assert answer.refused is False
    assert answer.citations == ["docs/rag.md#chunk-0"]
    assert "RAG answers need citations" in answer.text


def test_answer_pipeline_builds_from_documents_and_preserves_citation_metadata() -> None:
    document = SourceDocument(
        id="doc-1",
        text="Answer pipelines combine retrieval and generation into one boundary.",
        metadata={"source_path": "docs/pipeline.md", "file_type": ".md"},
    )

    pipeline = LocalAnswerPipeline.from_documents([document], chunk_size=120)
    answer = asyncio.run(pipeline.answer("retrieval generation boundary"))

    assert answer.refused is False
    assert answer.citations == ["docs/pipeline.md#chunk-0"]


def test_answer_pipeline_refuses_for_empty_query() -> None:
    pipeline = LocalAnswerPipeline.from_chunks(
        [_chunk("chunk-a", "RAG citations", metadata={"source_path": "rag.md", "chunk_index": 0})]
    )

    answer = asyncio.run(pipeline.answer("   "))

    assert answer.refused is True
    assert answer.citations == []
    assert answer.text == DEFAULT_REFUSAL_TEXT


def test_answer_pipeline_refuses_when_no_evidence_matches() -> None:
    pipeline = LocalAnswerPipeline.from_chunks(
        [_chunk("chunk-a", "!!!", metadata={"source_path": "symbols.txt", "chunk_index": 0})]
    )

    answer = asyncio.run(pipeline.answer("retrieval"))

    assert answer.refused is True
    assert answer.citations == []


def test_answer_pipeline_refuses_when_evidence_score_is_too_low() -> None:
    pipeline = LocalAnswerPipeline.from_chunks(
        [
            _chunk(
                "chunk-a",
                "alpha beta gamma",
                metadata={"source_path": "letters.md", "chunk_index": 0},
            )
        ],
        refusal_policy=MinimumEvidenceRefusalPolicy(min_score=0.9),
    )

    answer = asyncio.run(pipeline.answer("alpha"))

    assert answer.refused is True
    assert answer.citations == []


def test_answer_pipeline_allows_custom_lenient_refusal_policy() -> None:
    pipeline = LocalAnswerPipeline.from_chunks(
        [
            _chunk(
                "chunk-a",
                "alpha beta gamma",
                metadata={"source_path": "letters.md", "chunk_index": 0},
            )
        ],
        refusal_policy=MinimumEvidenceRefusalPolicy(min_score=0.1),
    )

    answer = asyncio.run(pipeline.answer("alpha"))

    assert answer.refused is False
    assert answer.citations == ["letters.md#chunk-0"]


def test_answer_pipeline_validates_limit_through_retriever() -> None:
    pipeline = LocalAnswerPipeline.from_chunks(
        [_chunk("chunk-a", "RAG citations", metadata={"source_path": "rag.md", "chunk_index": 0})]
    )

    with pytest.raises(ValueError):
        asyncio.run(pipeline.answer("RAG", limit=0))


def test_load_text_file_to_answer_pipeline_preserves_source_path(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "knowledge.txt"
    source_file.write_text(
        "Answer pipelines hide retrieval and generation composition.",
        encoding="utf-8",
    )

    document = load_text_file(source_file)
    pipeline = LocalAnswerPipeline.from_documents([document], chunk_size=120)
    answer = asyncio.run(pipeline.answer("retrieval generation composition"))

    assert answer.refused is False
    assert answer.citations == [f"{source_file.resolve()}#chunk-0"]
    assert "Answer pipelines hide retrieval" in answer.text


def _chunk(
    chunk_id: str,
    text: str,
    metadata: dict[str, str | int],
) -> DocumentChunk:
    return DocumentChunk(
        id=chunk_id,
        document_id="doc-1",
        text=text,
        metadata=metadata,
    )
