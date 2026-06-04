import asyncio

from agentic_rag_lab.generation import CitationAwareAnswerGenerator
from agentic_rag_lab.retrieval import LocalRetrievalPipeline
from agentic_rag_lab.schemas import SourceDocument


def test_retrieval_pipeline_feeds_citation_aware_answer_generation() -> None:
    document = SourceDocument(
        id="doc-1",
        text=(
            "RAG answers need citations so the user can inspect the source. "
            "Retrieval results preserve source metadata for generation."
        ),
        metadata={"source_path": "docs/rag.md", "file_type": ".md"},
    )
    pipeline = LocalRetrievalPipeline.from_documents([document], chunk_size=200)
    generator = CitationAwareAnswerGenerator()

    evidence = asyncio.run(pipeline.search("citations source metadata", limit=2))
    answer = asyncio.run(generator.answer("Why do RAG answers need citations?", evidence))

    assert answer.refused is False
    assert answer.citations
    assert answer.citations[0] == "docs/rag.md#chunk-0"
    assert "RAG answers need citations" in answer.text
