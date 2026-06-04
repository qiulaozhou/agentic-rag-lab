import asyncio

import pytest

from agentic_rag_lab.generation import CitationAwareAnswerGenerator
from agentic_rag_lab.generation.citation import NO_EVIDENCE_TEXT
from agentic_rag_lab.schemas import DocumentChunk, RetrievalResult


def test_generator_builds_answer_with_source_path_citation() -> None:
    generator = CitationAwareAnswerGenerator()
    evidence = [
        _result(
            "chunk-1",
            "Citation metadata keeps answers traceable.",
            metadata={"source_path": "docs/rag.md", "chunk_index": 2},
        )
    ]

    answer = asyncio.run(generator.answer("Why citation?", evidence))

    assert answer.refused is False
    assert "基于检索到的资料" in answer.text
    assert "Citation metadata keeps answers traceable." in answer.text
    assert answer.citations == ["docs/rag.md#chunk-2"]


def test_generator_falls_back_to_chunk_id_when_metadata_is_incomplete() -> None:
    generator = CitationAwareAnswerGenerator()
    evidence = [_result("chunk-1", "No source metadata.", metadata={})]

    answer = asyncio.run(generator.answer("missing metadata", evidence))

    assert answer.citations == ["chunk-1"]


def test_generator_deduplicates_citations_and_preserves_order() -> None:
    generator = CitationAwareAnswerGenerator()
    evidence = [
        _result(
            "chunk-a",
            "first source",
            metadata={"source_path": "docs/a.md", "chunk_index": 0},
        ),
        _result(
            "chunk-a-duplicate",
            "same source again",
            metadata={"source_path": "docs/a.md", "chunk_index": 0},
        ),
        _result(
            "chunk-b",
            "second source",
            metadata={"source_path": "docs/b.md", "chunk_index": 1},
        ),
    ]

    answer = asyncio.run(generator.answer("dedupe", evidence))

    assert answer.citations == ["docs/a.md#chunk-0", "docs/b.md#chunk-1"]


def test_generator_uses_only_the_configured_number_of_evidence_items() -> None:
    generator = CitationAwareAnswerGenerator(max_evidence_items=1)
    evidence = [
        _result("chunk-a", "first source", metadata={"source_path": "a.md", "chunk_index": 0}),
        _result("chunk-b", "second source", metadata={"source_path": "b.md", "chunk_index": 1}),
    ]

    answer = asyncio.run(generator.answer("limit evidence", evidence))

    assert "first source" in answer.text
    assert "second source" not in answer.text
    assert answer.citations == ["a.md#chunk-0"]


def test_generator_refuses_when_evidence_is_empty() -> None:
    generator = CitationAwareAnswerGenerator()

    answer = asyncio.run(generator.answer("unknown", []))

    assert answer.text == NO_EVIDENCE_TEXT
    assert answer.citations == []
    assert answer.refused is True


def test_generator_validates_constructor_values() -> None:
    with pytest.raises(ValueError):
        CitationAwareAnswerGenerator(max_evidence_items=0)

    with pytest.raises(ValueError):
        CitationAwareAnswerGenerator(snippet_length=0)


def _result(
    chunk_id: str,
    text: str,
    metadata: dict[str, str | int],
) -> RetrievalResult:
    return RetrievalResult(
        chunk=DocumentChunk(
            id=chunk_id,
            document_id="doc-1",
            text=text,
            metadata=metadata,
        ),
        score=0.8,
    )
