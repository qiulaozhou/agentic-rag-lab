import asyncio

from agentic_rag_lab.generation import LLMBackedCitationAwareAnswerGenerator
from agentic_rag_lab.generation.citation import NO_EVIDENCE_TEXT
from agentic_rag_lab.llm import LLMRequest, LLMResponse
from agentic_rag_lab.schemas import DocumentChunk, RetrievalResult


class RecordingLLMProvider:
    def __init__(self, text: str = "LLM answer from evidence.") -> None:
        self.text = text
        self.requests: list[LLMRequest] = []

    async def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(text=self.text, model="recording")


def test_llm_backed_generator_uses_model_text_and_local_citations() -> None:
    llm_provider = RecordingLLMProvider("A citation-aware answer from the model.")
    generator = LLMBackedCitationAwareAnswerGenerator(llm_provider)
    evidence = [
        _result(
            "chunk-1",
            "RAG answers need citations so users can inspect sources.",
            {"source_path": "docs/rag.md", "chunk_index": 0},
        )
    ]

    answer = asyncio.run(generator.answer("Why citations?", evidence))

    assert answer.refused is False
    assert answer.text == "A citation-aware answer from the model."
    assert answer.citations == ["docs/rag.md#chunk-0"]
    assert len(llm_provider.requests) == 1
    assert "RAG answers need citations" in llm_provider.requests[0].prompt


def test_llm_backed_generator_ignores_model_supplied_citation_text() -> None:
    llm_provider = RecordingLLMProvider("Model says see fake.md#chunk-99.")
    generator = LLMBackedCitationAwareAnswerGenerator(llm_provider)
    evidence = [
        _result(
            "chunk-1",
            "Only local evidence metadata should control citations.",
            {"source_path": "docs/local.md", "chunk_index": 2},
        )
    ]

    answer = asyncio.run(generator.answer("Which citation?", evidence))

    assert answer.text == "Model says see fake.md#chunk-99."
    assert answer.citations == ["docs/local.md#chunk-2"]


def test_llm_backed_generator_deduplicates_local_citations() -> None:
    llm_provider = RecordingLLMProvider()
    generator = LLMBackedCitationAwareAnswerGenerator(llm_provider)
    evidence = [
        _result("chunk-a", "first", {"source_path": "docs/a.md", "chunk_index": 0}),
        _result("chunk-b", "again", {"source_path": "docs/a.md", "chunk_index": 0}),
        _result("chunk-c", "second", {"source_path": "docs/b.md", "chunk_index": 1}),
    ]

    answer = asyncio.run(generator.answer("dedupe?", evidence))

    assert answer.citations == ["docs/a.md#chunk-0", "docs/b.md#chunk-1"]


def test_llm_backed_generator_refuses_empty_evidence_without_calling_llm() -> None:
    llm_provider = RecordingLLMProvider()
    generator = LLMBackedCitationAwareAnswerGenerator(llm_provider)

    answer = asyncio.run(generator.answer("unknown", []))

    assert answer.text == NO_EVIDENCE_TEXT
    assert answer.refused is True
    assert answer.citations == []
    assert llm_provider.requests == []


def test_llm_backed_generator_falls_back_to_chunk_id_for_incomplete_metadata() -> None:
    llm_provider = RecordingLLMProvider()
    generator = LLMBackedCitationAwareAnswerGenerator(llm_provider)
    evidence = [_result("chunk-fallback", "No metadata.", {})]

    answer = asyncio.run(generator.answer("fallback?", evidence))

    assert answer.citations == ["chunk-fallback"]


def _result(
    chunk_id: str,
    text: str,
    metadata: dict[str, str | int],
) -> RetrievalResult:
    return RetrievalResult(
        chunk=DocumentChunk(
            id=chunk_id,
            document_id="doc-1",
            text=text,
            metadata=metadata,
        ),
        score=0.8,
    )
