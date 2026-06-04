import asyncio

import pytest

from agentic_rag_lab.knowledge_base import InMemoryKnowledgeBaseRegistry
from agentic_rag_lab.schemas import SourceDocument


def test_registry_creates_gets_and_lists_knowledge_bases() -> None:
    registry = InMemoryKnowledgeBaseRegistry()
    document = SourceDocument(
        id="doc-1",
        text="RAG answers need citations for traceability.",
        metadata={"source_path": "docs/rag.md", "file_type": ".md"},
    )

    knowledge_base = registry.create([document], chunk_size=200)

    assert knowledge_base.id == "kb-1"
    assert registry.get("kb-1") is knowledge_base
    assert registry.list() == [knowledge_base]


def test_registry_preserves_document_and_chunk_counts() -> None:
    registry = InMemoryKnowledgeBaseRegistry()
    document = SourceDocument(
        id="doc-1",
        text="One two three four five six.",
        metadata={"source_path": "docs/counts.txt"},
    )

    knowledge_base = registry.create([document], chunk_size=10)

    assert knowledge_base.document_count == 1
    assert knowledge_base.chunk_count > 1
    assert knowledge_base.chunk_size == 10
    assert knowledge_base.overlap == 0


def test_registry_answer_preserves_metadata_in_citation() -> None:
    registry = InMemoryKnowledgeBaseRegistry()
    document = SourceDocument(
        id="doc-1",
        text="Knowledge base answers reuse stored local documents.",
        metadata={"source_path": "docs/kb.md", "file_type": ".md"},
    )
    knowledge_base = registry.create([document], chunk_size=200)

    answer = asyncio.run(knowledge_base.answer("stored local documents", limit=1))

    assert answer.refused is False
    assert answer.citations == ["docs/kb.md#chunk-0"]


def test_registry_raises_for_unknown_knowledge_base() -> None:
    registry = InMemoryKnowledgeBaseRegistry()

    with pytest.raises(KeyError):
        registry.get("kb-missing")
