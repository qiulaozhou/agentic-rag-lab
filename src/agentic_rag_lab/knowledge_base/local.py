"""In-process local knowledge base registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from agentic_rag_lab.chunking import chunk_documents
from agentic_rag_lab.embeddings import EmbeddingProvider
from agentic_rag_lab.generation import LocalAnswerPipeline
from agentic_rag_lab.generation.refusal import RefusalPolicy
from agentic_rag_lab.schemas import DocumentChunk, GeneratedAnswer, SourceDocument

if TYPE_CHECKING:
    from agentic_rag_lab.generation import AnswerGenerator


@dataclass(frozen=True)
class LocalKnowledgeBase:
    """Reusable in-process answer pipeline built from local documents."""

    id: str
    documents: list[SourceDocument]
    chunks: list[DocumentChunk]
    chunk_size: int
    overlap: int
    pipeline: LocalAnswerPipeline

    @property
    def document_count(self) -> int:
        return len(self.documents)

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)

    async def answer(self, question: str, limit: int = 5) -> GeneratedAnswer:
        return await self.pipeline.answer(question, limit=limit)


class InMemoryKnowledgeBaseRegistry:
    """Store local knowledge bases for the lifetime of one app process."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider | None = None,
        answer_generator: AnswerGenerator | None = None,
        refusal_policy: RefusalPolicy | None = None,
    ) -> None:
        self._knowledge_bases: dict[str, LocalKnowledgeBase] = {}
        self._next_id = 1
        self._embedding_provider = embedding_provider
        self._answer_generator = answer_generator
        self._refusal_policy = refusal_policy

    def create(
        self,
        documents: list[SourceDocument],
        chunk_size: int,
        overlap: int = 0,
    ) -> LocalKnowledgeBase:
        chunks = chunk_documents(documents, chunk_size=chunk_size, overlap=overlap)
        knowledge_base_id = self._new_id()
        knowledge_base = LocalKnowledgeBase(
            id=knowledge_base_id,
            documents=list(documents),
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
        self._knowledge_bases[knowledge_base_id] = knowledge_base
        return knowledge_base

    def get(self, knowledge_base_id: str) -> LocalKnowledgeBase:
        try:
            return self._knowledge_bases[knowledge_base_id]
        except KeyError as exc:
            raise KeyError(f"Unknown knowledge base: {knowledge_base_id}") from exc

    def list(self) -> list[LocalKnowledgeBase]:
        return list(self._knowledge_bases.values())

    def _new_id(self) -> str:
        knowledge_base_id = f"kb-{self._next_id}"
        self._next_id += 1
        return knowledge_base_id


__all__ = ["InMemoryKnowledgeBaseRegistry", "LocalKnowledgeBase"]
