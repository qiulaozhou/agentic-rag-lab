"""Disk-backed local knowledge base registry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from agentic_rag_lab.embeddings import EmbeddingProvider
from agentic_rag_lab.generation import LocalAnswerPipeline
from agentic_rag_lab.generation.refusal import RefusalPolicy
from agentic_rag_lab.knowledge_base.local import LocalKnowledgeBase
from agentic_rag_lab.schemas import DocumentChunk, MetadataValue, SourceDocument

if TYPE_CHECKING:
    from agentic_rag_lab.generation import AnswerGenerator


class DiskBackedKnowledgeBaseRegistry:
    """Persist local knowledge bases as JSON files and rebuild pipelines on load."""

    def __init__(
        self,
        storage_path: str | Path,
        embedding_provider: EmbeddingProvider | None = None,
        answer_generator: AnswerGenerator | None = None,
        refusal_policy: RefusalPolicy | None = None,
    ) -> None:
        self._storage_path = Path(storage_path)
        self._storage_path.mkdir(parents=True, exist_ok=True)
        self._knowledge_bases: dict[str, LocalKnowledgeBase] = {}
        self._next_id = 1
        self._embedding_provider = embedding_provider
        self._answer_generator = answer_generator
        self._refusal_policy = refusal_policy
        self._load()

    def create(
        self,
        documents: list[SourceDocument],
        chunk_size: int,
        overlap: int = 0,
    ) -> LocalKnowledgeBase:
        from agentic_rag_lab.chunking import chunk_documents

        chunks = chunk_documents(documents, chunk_size=chunk_size, overlap=overlap)
        knowledge_base_id = self._new_id()
        knowledge_base = self._build_knowledge_base(
            knowledge_base_id=knowledge_base_id,
            documents=list(documents),
            chunks=chunks,
            chunk_size=chunk_size,
            overlap=overlap,
        )
        self._knowledge_bases[knowledge_base_id] = knowledge_base
        self._save(knowledge_base)
        return knowledge_base

    def get(self, knowledge_base_id: str) -> LocalKnowledgeBase:
        try:
            return self._knowledge_bases[knowledge_base_id]
        except KeyError as exc:
            raise KeyError(f"Unknown knowledge base: {knowledge_base_id}") from exc

    def list(self) -> list[LocalKnowledgeBase]:
        return list(self._knowledge_bases.values())

    def _load(self) -> None:
        max_numeric_id = 0
        for path in sorted(self._storage_path.glob("*.json")):
            knowledge_base = self._load_file(path)
            self._knowledge_bases[knowledge_base.id] = knowledge_base
            numeric_id = _numeric_suffix(knowledge_base.id)
            if numeric_id is not None:
                max_numeric_id = max(max_numeric_id, numeric_id)
        self._next_id = max_numeric_id + 1

    def _load_file(self, path: Path) -> LocalKnowledgeBase:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid knowledge base JSON: {path}") from exc

        if not isinstance(raw, dict):
            raise ValueError(f"Invalid knowledge base payload: {path}")

        try:
            knowledge_base_id = _required_str(raw, "id")
            documents = _load_documents(raw["documents"])
            chunks = _load_chunks(raw["chunks"])
            chunk_size = _required_int(raw, "chunk_size")
            overlap = _required_int(raw, "overlap")
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid knowledge base payload: {path}") from exc

        if knowledge_base_id != path.stem:
            raise ValueError(f"Knowledge base id does not match file name: {path}")

        return self._build_knowledge_base(
            knowledge_base_id=knowledge_base_id,
            documents=documents,
            chunks=chunks,
            chunk_size=chunk_size,
            overlap=overlap,
        )

    def _save(self, knowledge_base: LocalKnowledgeBase) -> None:
        target = self._path_for(knowledge_base.id)
        temp = target.with_suffix(".json.tmp")
        payload = {
            "id": knowledge_base.id,
            "documents": [
                {
                    "id": document.id,
                    "text": document.text,
                    "metadata": dict(document.metadata),
                }
                for document in knowledge_base.documents
            ],
            "chunks": [
                {
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "text": chunk.text,
                    "metadata": dict(chunk.metadata),
                }
                for chunk in knowledge_base.chunks
            ],
            "chunk_size": knowledge_base.chunk_size,
            "overlap": knowledge_base.overlap,
        }
        temp.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temp.replace(target)

    def _build_knowledge_base(
        self,
        knowledge_base_id: str,
        documents: list[SourceDocument],
        chunks: list[DocumentChunk],
        chunk_size: int,
        overlap: int,
    ) -> LocalKnowledgeBase:
        return LocalKnowledgeBase(
            id=knowledge_base_id,
            documents=documents,
            chunks=chunks,
            chunk_size=chunk_size,
            overlap=overlap,
            pipeline=LocalAnswerPipeline.from_chunks(
                chunks,
                embedding_provider=self._embedding_provider,
                answer_generator=self._answer_generator,
                refusal_policy=self._refusal_policy,
            ),
        )

    def _path_for(self, knowledge_base_id: str) -> Path:
        return self._storage_path / f"{knowledge_base_id}.json"

    def _new_id(self) -> str:
        knowledge_base_id = f"kb-{self._next_id}"
        self._next_id += 1
        return knowledge_base_id


def _load_documents(raw_documents: Any) -> list[SourceDocument]:
    if not isinstance(raw_documents, list):
        raise ValueError("documents must be a list")
    return [
        SourceDocument(
            id=_required_str(raw_document, "id"),
            text=_required_str(raw_document, "text"),
            metadata=_load_metadata(raw_document.get("metadata", {})),
        )
        for raw_document in raw_documents
    ]


def _load_chunks(raw_chunks: Any) -> list[DocumentChunk]:
    if not isinstance(raw_chunks, list):
        raise ValueError("chunks must be a list")
    return [
        DocumentChunk(
            id=_required_str(raw_chunk, "id"),
            document_id=_required_str(raw_chunk, "document_id"),
            text=_required_str(raw_chunk, "text"),
            metadata=_load_metadata(raw_chunk.get("metadata", {})),
        )
        for raw_chunk in raw_chunks
    ]


def _load_metadata(raw_metadata: Any) -> dict[str, MetadataValue]:
    if not isinstance(raw_metadata, dict):
        raise ValueError("metadata must be an object")
    metadata: dict[str, MetadataValue] = {}
    for key, value in raw_metadata.items():
        if not isinstance(key, str):
            raise ValueError("metadata keys must be strings")
        if not isinstance(value, str | int):
            raise ValueError("metadata values must be strings or integers")
        metadata[key] = value
    return metadata


def _required_str(raw: Any, key: str) -> str:
    if not isinstance(raw, dict):
        raise ValueError("payload must be an object")
    value = raw[key]
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    return value


def _required_int(raw: dict[str, Any], key: str) -> int:
    value = raw[key]
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _numeric_suffix(knowledge_base_id: str) -> int | None:
    prefix = "kb-"
    if not knowledge_base_id.startswith(prefix):
        return None
    suffix = knowledge_base_id[len(prefix) :]
    if not suffix.isdigit():
        return None
    return int(suffix)


__all__ = ["DiskBackedKnowledgeBaseRegistry"]
