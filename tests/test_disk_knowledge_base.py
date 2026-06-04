import asyncio

import pytest

from agentic_rag_lab.knowledge_base import DiskBackedKnowledgeBaseRegistry
from agentic_rag_lab.schemas import SourceDocument


def test_disk_registry_writes_json_file(tmp_path) -> None:
    registry = DiskBackedKnowledgeBaseRegistry(tmp_path)
    document = SourceDocument(
        id="doc-1",
        text="RAG answers need citations for traceability.",
        metadata={"source_path": "docs/rag.md", "file_type": ".md"},
    )

    knowledge_base = registry.create([document], chunk_size=200)

    assert knowledge_base.id == "kb-1"
    assert (tmp_path / "kb-1.json").exists()


def test_disk_registry_loads_existing_knowledge_base(tmp_path) -> None:
    registry = DiskBackedKnowledgeBaseRegistry(tmp_path)
    document = SourceDocument(
        id="doc-1",
        text="Disk-backed knowledge bases survive app restarts.",
        metadata={"source_path": "docs/disk.md", "file_type": ".md"},
    )
    registry.create([document], chunk_size=200)

    restored_registry = DiskBackedKnowledgeBaseRegistry(tmp_path)
    restored = restored_registry.get("kb-1")
    answer = asyncio.run(restored.answer("survive app restarts", limit=1))

    assert restored.document_count == 1
    assert restored.chunk_count == 1
    assert answer.refused is False
    assert answer.citations == ["docs/disk.md#chunk-0"]


def test_disk_registry_persists_empty_knowledge_base(tmp_path) -> None:
    registry = DiskBackedKnowledgeBaseRegistry(tmp_path)
    registry.create([], chunk_size=200)

    restored_registry = DiskBackedKnowledgeBaseRegistry(tmp_path)
    restored = restored_registry.get("kb-1")
    answer = asyncio.run(restored.answer("anything"))

    assert restored.document_count == 0
    assert restored.chunk_count == 0
    assert answer.refused is True
    assert answer.citations == []


def test_disk_registry_uses_next_id_after_existing_files(tmp_path) -> None:
    registry = DiskBackedKnowledgeBaseRegistry(tmp_path)
    registry.create([], chunk_size=200)

    restored_registry = DiskBackedKnowledgeBaseRegistry(tmp_path)
    knowledge_base = restored_registry.create([], chunk_size=200)

    assert knowledge_base.id == "kb-2"
    assert (tmp_path / "kb-2.json").exists()


def test_disk_registry_raises_for_unknown_knowledge_base(tmp_path) -> None:
    registry = DiskBackedKnowledgeBaseRegistry(tmp_path)

    with pytest.raises(KeyError):
        registry.get("kb-missing")


def test_disk_registry_raises_for_corrupt_json(tmp_path) -> None:
    (tmp_path / "kb-1.json").write_text("{not-json", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid knowledge base JSON"):
        DiskBackedKnowledgeBaseRegistry(tmp_path)


def test_disk_registry_raises_for_missing_required_fields(tmp_path) -> None:
    (tmp_path / "kb-1.json").write_text('{"id": "kb-1"}', encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid knowledge base payload"):
        DiskBackedKnowledgeBaseRegistry(tmp_path)
