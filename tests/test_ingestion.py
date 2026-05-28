from pathlib import Path

import pytest

from agentic_rag_lab.ingestion import load_directory, load_text_file


def test_load_text_file_returns_source_document_with_metadata(tmp_path: Path) -> None:
    source_file = tmp_path / "notes.md"
    source_file.write_text("# Title\n\nBody text.", encoding="utf-8")

    document = load_text_file(source_file)

    assert document.text == "# Title\n\nBody text."
    assert document.id == load_text_file(source_file).id
    assert document.metadata == {
        "source_path": str(source_file.resolve()),
        "file_name": "notes.md",
        "file_type": ".md",
    }


def test_load_text_file_rejects_unsupported_extension(tmp_path: Path) -> None:
    source_file = tmp_path / "notes.pdf"
    source_file.write_text("pdf placeholder", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported text file extension"):
        load_text_file(source_file)


def test_load_text_file_raises_for_missing_path(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_text_file(tmp_path / "missing.md")


def test_load_directory_recursively_loads_supported_files_in_path_order(
    tmp_path: Path,
) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    txt_file = tmp_path / "b.txt"
    md_file = nested / "a.md"
    ignored_file = tmp_path / "ignore.pdf"
    txt_file.write_text("second", encoding="utf-8")
    md_file.write_text("first", encoding="utf-8")
    ignored_file.write_text("ignored", encoding="utf-8")

    documents = load_directory(tmp_path)

    assert [document.metadata["file_name"] for document in documents] == [
        "b.txt",
        "a.md",
    ]
    assert [document.text for document in documents] == ["second", "first"]


def test_load_directory_can_filter_supported_extensions(tmp_path: Path) -> None:
    (tmp_path / "notes.md").write_text("markdown", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("text", encoding="utf-8")

    documents = load_directory(tmp_path, extensions={"md"})

    assert [document.metadata["file_name"] for document in documents] == ["notes.md"]


def test_load_directory_rejects_non_directory(tmp_path: Path) -> None:
    source_file = tmp_path / "notes.md"
    source_file.write_text("content", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        load_directory(source_file)
