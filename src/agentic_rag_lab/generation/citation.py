"""Deterministic citation-aware answer generation."""

from __future__ import annotations

import re
from collections.abc import Iterable

from agentic_rag_lab.schemas import GeneratedAnswer, RetrievalResult

NO_EVIDENCE_TEXT = "当前知识库没有足够依据回答这个问题。"


class CitationAwareAnswerGenerator:
    """Build a local answer from retrieved evidence and stable citations."""

    def __init__(
        self,
        max_evidence_items: int = 3,
        snippet_length: int = 180,
    ) -> None:
        if max_evidence_items <= 0:
            raise ValueError("max_evidence_items must be greater than 0")
        if snippet_length <= 0:
            raise ValueError("snippet_length must be greater than 0")

        self.max_evidence_items = max_evidence_items
        self.snippet_length = snippet_length

    async def answer(
        self,
        question: str,
        evidence: list[RetrievalResult],
    ) -> GeneratedAnswer:
        if not evidence:
            return GeneratedAnswer(
                text=NO_EVIDENCE_TEXT,
                citations=[],
                refused=True,
            )

        used_evidence = evidence[: self.max_evidence_items]
        citations = _dedupe_preserving_order(
            _citation_for_result(result) for result in used_evidence
        )
        snippets = [
            _truncate(_normalize_text(result.chunk.text), self.snippet_length)
            for result in used_evidence
        ]
        answer_text = _compose_answer(question=question, snippets=snippets)

        return GeneratedAnswer(
            text=answer_text,
            citations=citations,
            refused=False,
        )


def _compose_answer(question: str, snippets: list[str]) -> str:
    normalized_question = _normalize_text(question)
    lines = ["基于检索到的资料，可以回答如下："]
    if normalized_question:
        lines.append(f"问题：{normalized_question}")
    lines.append("依据摘要：")
    lines.extend(f"{index}. {snippet}" for index, snippet in enumerate(snippets, start=1))
    return "\n".join(lines)


def _citation_for_result(result: RetrievalResult) -> str:
    metadata = result.chunk.metadata
    source_path = metadata.get("source_path")
    chunk_index = metadata.get("chunk_index")
    if source_path is not None and chunk_index is not None:
        return f"{source_path}#chunk-{chunk_index}"
    return result.chunk.id


def _dedupe_preserving_order(values: Iterable[object]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        citation = str(value)
        if citation not in seen:
            seen.add(citation)
            deduped.append(citation)
    return deduped


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _truncate(text: str, max_length: int) -> str:
    if len(text) <= max_length:
        return text
    return f"{text[: max_length - 3]}..."


__all__ = ["CitationAwareAnswerGenerator", "NO_EVIDENCE_TEXT"]
