"""Local answer pipeline boundary."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from agentic_rag_lab.embeddings import EmbeddingProvider
from agentic_rag_lab.generation.citation import CitationAwareAnswerGenerator
from agentic_rag_lab.generation.refusal import (
    MinimumEvidenceRefusalPolicy,
    RefusalPolicy,
    refused_answer,
)
from agentic_rag_lab.retrieval import LocalRetrievalPipeline, Retriever
from agentic_rag_lab.schemas import DocumentChunk, GeneratedAnswer, SourceDocument

if TYPE_CHECKING:
    from agentic_rag_lab.generation import AnswerGenerator


class LocalAnswerPipeline:
    """Compose retrieval and citation-aware generation behind one answer call."""

    def __init__(
        self,
        retriever: Retriever,
        answer_generator: AnswerGenerator | None = None,
        refusal_policy: RefusalPolicy | None = None,
    ) -> None:
        self._retriever = retriever
        self._answer_generator = answer_generator or CitationAwareAnswerGenerator()
        self._refusal_policy = refusal_policy or MinimumEvidenceRefusalPolicy()

    @classmethod
    def from_chunks(
        cls,
        chunks: Iterable[DocumentChunk],
        embedding_provider: EmbeddingProvider | None = None,
        answer_generator: AnswerGenerator | None = None,
        refusal_policy: RefusalPolicy | None = None,
    ) -> "LocalAnswerPipeline":
        retriever = LocalRetrievalPipeline.from_chunks(
            chunks,
            embedding_provider=embedding_provider,
        )
        return cls(
            retriever=retriever,
            answer_generator=answer_generator,
            refusal_policy=refusal_policy,
        )

    @classmethod
    def from_documents(
        cls,
        documents: list[SourceDocument],
        chunk_size: int,
        overlap: int = 0,
        embedding_provider: EmbeddingProvider | None = None,
        answer_generator: AnswerGenerator | None = None,
        refusal_policy: RefusalPolicy | None = None,
    ) -> "LocalAnswerPipeline":
        retriever = LocalRetrievalPipeline.from_documents(
            documents,
            chunk_size=chunk_size,
            overlap=overlap,
            embedding_provider=embedding_provider,
        )
        return cls(
            retriever=retriever,
            answer_generator=answer_generator,
            refusal_policy=refusal_policy,
        )

    async def answer(self, question: str, limit: int = 5) -> GeneratedAnswer:
        evidence = await self._retriever.search(question, limit=limit)
        if self._refusal_policy.should_refuse(question, evidence):
            return refused_answer()
        return await self._answer_generator.answer(question, evidence)


__all__ = ["LocalAnswerPipeline"]
