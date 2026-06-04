import asyncio
from pathlib import Path

from agentic_rag_lab.ingestion import load_text_file
from agentic_rag_lab.retrieval import LocalRetrievalPipeline


def test_load_chunk_and_search_pipeline_preserves_source_metadata(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "knowledge.txt"
    source_file.write_text(
        "Embedding vectors make chunks searchable.\n"
        "Citation metadata keeps answers traceable.",
        encoding="utf-8",
    )

    document = load_text_file(source_file)
    pipeline = LocalRetrievalPipeline.from_documents([document], chunk_size=43)

    results = asyncio.run(pipeline.search("embedding vectors searchable"))

    assert results
    assert results[0].chunk.metadata["source_path"] == str(source_file.resolve())
    assert results[0].chunk.metadata["file_type"] == ".txt"
    assert results[0].chunk.metadata["chunk_index"] == 0
