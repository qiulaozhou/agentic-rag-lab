"""Deterministic refusal policy for local RAG answers."""

from __future__ import annotations

from typing import Protocol

from agentic_rag_lab.generation.citation import NO_EVIDENCE_TEXT
from agentic_rag_lab.schemas import GeneratedAnswer, RetrievalResult

DEFAULT_REFUSAL_TEXT = NO_EVIDENCE_TEXT


class RefusalPolicy(Protocol):
    def should_refuse(
        self,
        question: str,
        evidence: list[RetrievalResult],
    ) -> bool:
        """Return whether the answer pipeline should refuse to answer."""


class MinimumEvidenceRefusalPolicy:
    """Refuse when the query is empty or retrieval evidence is too weak."""

    def __init__(self, min_score: float = 0.25) -> None:
        if min_score < 0:
            raise ValueError("min_score must be greater than or equal to 0")
        self.min_score = min_score

    def should_refuse(
        self,
        question: str,
        evidence: list[RetrievalResult],
    ) -> bool:
        if not question.strip():
            return True
        if not evidence:
            return True
        return max(result.score for result in evidence) < self.min_score


def refused_answer(text: str = DEFAULT_REFUSAL_TEXT) -> GeneratedAnswer:
    return GeneratedAnswer(text=text, citations=[], refused=True)


__all__ = [
    "DEFAULT_REFUSAL_TEXT",
    "MinimumEvidenceRefusalPolicy",
    "RefusalPolicy",
    "refused_answer",
]
