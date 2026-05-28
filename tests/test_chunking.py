import pytest

from agentic_rag_lab.chunking import chunk_document, chunk_documents, chunk_text
from agentic_rag_lab.schemas import SourceDocument


def test_chunk_text_splits_by_character_window_without_overlap() -> None:
    assert chunk_text("abcdefghij", chunk_size=4) == ["abcd", "efgh", "ij"]


def test_chunk_text_splits_by_character_window_with_overlap() -> None:
    assert chunk_text("abcdefghij", chunk_size=4, overlap=1) == [
        "abcd",
        "defg",
        "ghij",
    ]


@pytest.mark.parametrize(
    ("chunk_size", "overlap"),
    [
        (0, 0),
        (-1, 0),
        (4, -1),
        (4, 4),
        (4, 5),
    ],
)
def test_chunk_text_validates_chunk_parameters(
    chunk_size: int,
    overlap: int,
) -> None:
    with pytest.raises(ValueError):
        chunk_text("content", chunk_size=chunk_size, overlap=overlap)


@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
def test_chunk_text_returns_empty_list_for_blank_text(text: str) -> None:
    assert chunk_text(text, chunk_size=4) == []


def test_chunk_document_preserves_document_metadata_and_adds_offsets() -> None:
    document = SourceDocument(
        id="doc-123",
        text="abcdefghij",
        metadata={
            "source_path": "notes.md",
            "file_name": "notes.md",
            "file_type": ".md",
        },
    )

    chunks = chunk_document(document, chunk_size=4, overlap=1)

    assert [chunk.id for chunk in chunks] == [
        "doc-123:chunk-0",
        "doc-123:chunk-1",
        "doc-123:chunk-2",
    ]
    assert [chunk.text for chunk in chunks] == ["abcd", "defg", "ghij"]
    assert [chunk.document_id for chunk in chunks] == ["doc-123"] * 3
    assert chunks[0].metadata == {
        "source_path": "notes.md",
        "file_name": "notes.md",
        "file_type": ".md",
        "chunk_index": 0,
        "start": 0,
        "end": 4,
    }
    assert chunks[2].metadata["chunk_index"] == 2
    assert chunks[2].metadata["start"] == 6
    assert chunks[2].metadata["end"] == 10


def test_chunk_documents_preserves_input_document_order() -> None:
    documents = [
        SourceDocument(id="doc-a", text="abcd", metadata={}),
        SourceDocument(id="doc-b", text="wxyz", metadata={}),
    ]

    chunks = chunk_documents(documents, chunk_size=2)

    assert [chunk.id for chunk in chunks] == [
        "doc-a:chunk-0",
        "doc-a:chunk-1",
        "doc-b:chunk-0",
        "doc-b:chunk-1",
    ]
