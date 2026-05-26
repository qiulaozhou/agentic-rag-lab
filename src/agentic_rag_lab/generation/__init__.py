"""Answer generation boundary."""

from typing import Protocol

from agentic_rag_lab.schemas import GeneratedAnswer, RetrievalResult


class AnswerGenerator(Protocol):
    async def answer(self, question: str, evidence: list[RetrievalResult]) -> GeneratedAnswer:
        """Generate a citation-aware answer from retrieved evidence."""
