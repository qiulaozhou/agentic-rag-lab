"""LLM-backed answer generation with local citation authority."""

from __future__ import annotations

import re
from collections.abc import Iterable

from agentic_rag_lab.generation.citation import NO_EVIDENCE_TEXT
from agentic_rag_lab.llm import LLMProvider, LLMRequest
from agentic_rag_lab.schemas import GeneratedAnswer, RetrievalResult

_SYSTEM_PROMPT = (
    "You are a retrieval-augmented answer generator. "
    "Answer only from the evidence in the user prompt. "
    "Do not invent citations; citations are attached by the application."
)


class LLMBackedCitationAwareAnswerGenerator:
    """Use an LLM for answer text while keeping citations local and deterministic."""

    def __init__(
        self,
        llm_provider: LLMProvider,
        max_evidence_items: int = 3,
        snippet_length: int = 1200,
    ) -> None:
        if max_evidence_items <= 0:
            raise ValueError("max_evidence_items must be greater than 0")
        if snippet_length <= 0:
            raise ValueError("snippet_length must be greater than 0")

        self.llm_provider = llm_provider
        self.max_evidence_items = max_evidence_items
        self.snippet_length = snippet_length

    async def answer(
        self,
        question: str,
        evidence: list[RetrievalResult],
    ) -> GeneratedAnswer:
        if not evidence:
            return GeneratedAnswer(text=NO_EVIDENCE_TEXT, citations=[], refused=True)

        used_evidence = evidence[: self.max_evidence_items]
        citations = _dedupe_preserving_order(
            _citation_for_result(result) for result in used_evidence
        )
        prompt = _compose_prompt(
            question=question,
            evidence=used_evidence,
            snippet_length=self.snippet_length,
        )
        response = await self.llm_provider.generate(
            LLMRequest(prompt=prompt, system_prompt=_SYSTEM_PROMPT)
        )
        answer_text = response.text.strip()
        if not answer_text:
            raise ValueError("LLM response text must not be empty")

        return GeneratedAnswer(text=answer_text, citations=citations, refused=False)


def _compose_prompt(
    question: str,
    evidence: list[RetrievalResult],
    snippet_length: int,
) -> str:
    lines = [
        "Question:",
        question.strip(),
        "",
        "Evidence:",
    ]
    for index, result in enumerate(evidence, start=1):
        snippet = _truncate(_normalize_text(result.chunk.text), snippet_length)
        lines.append(f"[{index}] {snippet}")
    lines.extend(
        [
            "",
            "Write a concise answer based only on the evidence above.",
            "Do not include citation strings in the answer text.",
        ]
    )
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


__all__ = ["LLMBackedCitationAwareAnswerGenerator"]
