"""Markdown and plain-text ingestion helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path

from agentic_rag_lab.schemas import SourceDocument

SUPPORTED_TEXT_EXTENSIONS = {".md", ".txt"}


def load_text_file(path: str | Path) -> SourceDocument:
    """Load one UTF-8 Markdown or text file into a source document."""

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(file_path)

    file_type = file_path.suffix.lower()
    if file_type not in SUPPORTED_TEXT_EXTENSIONS:
        raise ValueError(f"Unsupported text file extension: {file_type}")

    resolved_path = file_path.resolve()
    text = resolved_path.read_text(encoding="utf-8")

    return SourceDocument(
        id=_document_id_for_path(resolved_path),
        text=text,
        metadata={
            "source_path": str(resolved_path),
            "file_name": resolved_path.name,
            "file_type": file_type,
        },
    )


def load_directory(
    path: str | Path,
    extensions: set[str] | None = None,
) -> list[SourceDocument]:
    """Recursively load supported text documents from a directory."""

    directory_path = Path(path)
    if not directory_path.is_dir():
        raise NotADirectoryError(directory_path)

    allowed_extensions = _normalize_extensions(extensions)
    documents: list[SourceDocument] = []

    for file_path in sorted(directory_path.rglob("*"), key=lambda item: str(item)):
        if file_path.is_file() and file_path.suffix.lower() in allowed_extensions:
            documents.append(load_text_file(file_path))

    return documents


def _document_id_for_path(path: Path) -> str:
    normalized_path = str(path.resolve())
    digest = hashlib.sha256(normalized_path.encode("utf-8")).hexdigest()
    return f"doc-{digest[:16]}"


def _normalize_extensions(extensions: set[str] | None) -> set[str]:
    if extensions is None:
        return set(SUPPORTED_TEXT_EXTENSIONS)

    normalized = {
        extension.lower() if extension.startswith(".") else f".{extension.lower()}"
        for extension in extensions
    }
    return normalized & SUPPORTED_TEXT_EXTENSIONS


__all__ = ["SUPPORTED_TEXT_EXTENSIONS", "load_directory", "load_text_file"]
