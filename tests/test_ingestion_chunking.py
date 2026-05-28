from pathlib import Path

from agentic_rag_lab.chunking import chunk_document
from agentic_rag_lab.ingestion import load_text_file


def test_load_text_file_then_chunk_document_pipeline(tmp_path: Path) -> None:
    source_file = tmp_path / "knowledge.txt"
    source_file.write_text("RAG needs traceable source chunks.", encoding="utf-8")

    document = load_text_file(source_file)
    chunks = chunk_document(document, chunk_size=12, overlap=3)

    assert [chunk.text for chunk in chunks] == [
        "RAG needs tr",
        " traceable s",
        "e source chu",
        "chunks.",
    ]
    assert chunks[0].id == f"{document.id}:chunk-0"
    assert chunks[0].metadata["source_path"] == str(source_file.resolve())
    assert chunks[0].metadata["file_type"] == ".txt"
    assert chunks[-1].metadata["chunk_index"] == 3
