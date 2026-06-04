"""Answer generation boundary."""

from typing import Protocol

from agentic_rag_lab.schemas import GeneratedAnswer, RetrievalResult
from agentic_rag_lab.generation.citation import CitationAwareAnswerGenerator
from agentic_rag_lab.generation.factory import create_answer_generator
from agentic_rag_lab.generation.llm_backed import LLMBackedCitationAwareAnswerGenerator
from agentic_rag_lab.generation.refusal import (
    DEFAULT_REFUSAL_TEXT,
    MinimumEvidenceRefusalPolicy,
    RefusalPolicy,
)


class AnswerGenerator(Protocol):
    async def answer(self, question: str, evidence: list[RetrievalResult]) -> GeneratedAnswer:
        """Generate a citation-aware answer from retrieved evidence."""


from agentic_rag_lab.generation.pipeline import LocalAnswerPipeline


__all__ = [
    "AnswerGenerator",
    "CitationAwareAnswerGenerator",
    "DEFAULT_REFUSAL_TEXT",
    "LLMBackedCitationAwareAnswerGenerator",
    "LocalAnswerPipeline",
    "MinimumEvidenceRefusalPolicy",
    "RefusalPolicy",
    "create_answer_generator",
]
