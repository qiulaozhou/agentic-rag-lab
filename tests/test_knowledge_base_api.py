from pathlib import Path

from fastapi.testclient import TestClient

from agentic_rag_lab.config import Settings
from agentic_rag_lab.main import create_app


def test_create_knowledge_base_returns_summary(tmp_path: Path) -> None:
    client = _client(tmp_path)

    response = client.post(
        "/knowledge-bases",
        json={
            "documents": [
                {
                    "id": "doc-1",
                    "text": "RAG answers need citations so users can inspect sources.",
                    "metadata": {"source_path": "docs/rag.md", "file_type": ".md"},
                }
            ],
            "chunk_size": 200,
            "overlap": 0,
        },
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload == {
        "knowledge_base_id": "kb-1",
        "document_count": 1,
        "chunk_count": 1,
    }


def test_knowledge_base_answer_returns_answer_with_citation(tmp_path: Path) -> None:
    client = _client(tmp_path)
    knowledge_base_id = _create_rag_knowledge_base(client)

    response = client.post(
        f"/knowledge-bases/{knowledge_base_id}/answer",
        json={
            "question": "Why do RAG answers need citations?",
            "limit": 1,
        },
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["refused"] is False
    assert payload["citations"] == ["docs/rag.md#chunk-0"]
    assert "RAG answers need citations" in payload["text"]


def test_knowledge_base_answer_preserves_request_metadata_in_citation(tmp_path: Path) -> None:
    client = _client(tmp_path)

    create_response = client.post(
        "/knowledge-bases",
        json={
            "documents": [
                {
                    "id": "doc-1",
                    "text": "Knowledge base answers keep metadata available for citation.",
                    "metadata": {"source_path": "notes/kb.md", "file_type": ".md"},
                }
            ],
            "chunk_size": 200,
        },
    )
    knowledge_base_id = create_response.json()["knowledge_base_id"]

    response = client.post(
        f"/knowledge-bases/{knowledge_base_id}/answer",
        json={"question": "metadata citation"},
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["refused"] is False
    assert payload["citations"] == ["notes/kb.md#chunk-0"]


def test_knowledge_base_answer_refuses_empty_question(tmp_path: Path) -> None:
    client = _client(tmp_path)
    knowledge_base_id = _create_rag_knowledge_base(client)

    response = client.post(
        f"/knowledge-bases/{knowledge_base_id}/answer",
        json={"question": "   "},
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["refused"] is True
    assert payload["citations"] == []


def test_knowledge_base_answer_refuses_unrelated_question(tmp_path: Path) -> None:
    client = _client(tmp_path)
    create_response = client.post(
        "/knowledge-bases",
        json={
            "documents": [
                {
                    "id": "doc-1",
                    "text": "!!!",
                    "metadata": {"source_path": "docs/symbols.txt"},
                }
            ],
            "chunk_size": 200,
        },
    )
    knowledge_base_id = create_response.json()["knowledge_base_id"]

    response = client.post(
        f"/knowledge-bases/{knowledge_base_id}/answer",
        json={"question": "retrieval"},
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["refused"] is True
    assert payload["citations"] == []


def test_empty_knowledge_base_can_be_created_and_refuses_answers(tmp_path: Path) -> None:
    client = _client(tmp_path)

    create_response = client.post(
        "/knowledge-bases",
        json={"documents": [], "chunk_size": 200},
    )
    knowledge_base_id = create_response.json()["knowledge_base_id"]

    answer_response = client.post(
        f"/knowledge-bases/{knowledge_base_id}/answer",
        json={"question": "anything"},
    )

    answer_payload = answer_response.json()

    assert create_response.status_code == 200
    assert create_response.json()["document_count"] == 0
    assert create_response.json()["chunk_count"] == 0
    assert answer_response.status_code == 200
    assert answer_payload["refused"] is True
    assert answer_payload["citations"] == []


def test_knowledge_base_answer_returns_not_found_for_unknown_id(tmp_path: Path) -> None:
    client = _client(tmp_path)

    response = client.post(
        "/knowledge-bases/kb-missing/answer",
        json={"question": "RAG"},
    )

    assert response.status_code == 404
    assert "Unknown knowledge base" in response.json()["detail"]


def test_knowledge_base_answer_returns_bad_request_for_invalid_limit(tmp_path: Path) -> None:
    client = _client(tmp_path)
    knowledge_base_id = _create_rag_knowledge_base(client)

    response = client.post(
        f"/knowledge-bases/{knowledge_base_id}/answer",
        json={"question": "RAG", "limit": 0},
    )

    assert response.status_code == 400
    assert "limit must be greater than 0" in response.json()["detail"]


def test_create_knowledge_base_returns_bad_request_for_invalid_chunk_size(
    tmp_path: Path,
) -> None:
    client = _client(tmp_path)

    response = client.post(
        "/knowledge-bases",
        json={"documents": [], "chunk_size": 0},
    )

    assert response.status_code == 400
    assert "chunk_size must be greater than 0" in response.json()["detail"]


def test_create_knowledge_base_returns_bad_request_for_negative_overlap(
    tmp_path: Path,
) -> None:
    client = _client(tmp_path)

    response = client.post(
        "/knowledge-bases",
        json={"documents": [], "chunk_size": 10, "overlap": -1},
    )

    assert response.status_code == 400
    assert "overlap must be greater than or equal to 0" in response.json()["detail"]


def test_create_knowledge_base_returns_bad_request_for_invalid_overlap(
    tmp_path: Path,
) -> None:
    client = _client(tmp_path)

    response = client.post(
        "/knowledge-bases",
        json={"documents": [], "chunk_size": 10, "overlap": 10},
    )

    assert response.status_code == 400
    assert "overlap must be smaller than chunk_size" in response.json()["detail"]


def test_existing_answer_endpoint_still_works() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/answer",
        json={
            "question": "Why do RAG answers need citations?",
            "documents": [
                {
                    "id": "doc-1",
                    "text": "RAG answers need citations so users can inspect sources.",
                    "metadata": {"source_path": "docs/rag.md", "file_type": ".md"},
                }
            ],
            "chunk_size": 200,
            "limit": 1,
        },
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["refused"] is False
    assert payload["citations"] == ["docs/rag.md#chunk-0"]


def test_knowledge_base_survives_app_recreation(tmp_path: Path) -> None:
    first_client = _client(tmp_path)
    knowledge_base_id = _create_rag_knowledge_base(first_client)

    second_client = _client(tmp_path)
    response = second_client.post(
        f"/knowledge-bases/{knowledge_base_id}/answer",
        json={"question": "Why do RAG answers need citations?", "limit": 1},
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["refused"] is False
    assert payload["citations"] == ["docs/rag.md#chunk-0"]


def test_create_knowledge_base_from_file_returns_answer_with_source_path(
    tmp_path: Path,
) -> None:
    storage_path = tmp_path / "storage"
    source_file = tmp_path / "docs" / "rag.md"
    source_file.parent.mkdir()
    source_file.write_text(
        "File import answers preserve citations for local Markdown files.",
        encoding="utf-8",
    )
    client = _client(storage_path)

    create_response = client.post(
        "/knowledge-bases/from-file",
        json={"path": str(source_file), "chunk_size": 200},
    )
    knowledge_base_id = create_response.json()["knowledge_base_id"]

    answer_response = client.post(
        f"/knowledge-bases/{knowledge_base_id}/answer",
        json={"question": "local Markdown files citations", "limit": 1},
    )

    payload = answer_response.json()

    assert create_response.status_code == 200
    assert create_response.json()["document_count"] == 1
    assert create_response.json()["chunk_count"] == 1
    assert answer_response.status_code == 200
    assert payload["refused"] is False
    assert payload["citations"] == [f"{source_file.resolve()}#chunk-0"]


def test_file_imported_knowledge_base_survives_app_recreation(tmp_path: Path) -> None:
    storage_path = tmp_path / "storage"
    source_file = tmp_path / "docs" / "rag.txt"
    source_file.parent.mkdir()
    source_file.write_text(
        "Imported files are restored from disk-backed knowledge bases.",
        encoding="utf-8",
    )
    first_client = _client(storage_path)
    create_response = first_client.post(
        "/knowledge-bases/from-file",
        json={"path": str(source_file), "chunk_size": 200},
    )
    knowledge_base_id = create_response.json()["knowledge_base_id"]

    second_client = _client(storage_path)
    answer_response = second_client.post(
        f"/knowledge-bases/{knowledge_base_id}/answer",
        json={"question": "restored disk-backed knowledge bases", "limit": 1},
    )

    payload = answer_response.json()

    assert create_response.status_code == 200
    assert answer_response.status_code == 200
    assert payload["refused"] is False
    assert payload["citations"] == [f"{source_file.resolve()}#chunk-0"]


def test_create_knowledge_base_from_file_returns_bad_request_for_missing_file(
    tmp_path: Path,
) -> None:
    client = _client(tmp_path / "storage")

    response = client.post(
        "/knowledge-bases/from-file",
        json={"path": str(tmp_path / "missing.md")},
    )

    assert response.status_code == 400


def test_create_knowledge_base_from_file_returns_bad_request_for_unsupported_extension(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "unsupported.pdf"
    source_file.write_text("not supported", encoding="utf-8")
    client = _client(tmp_path / "storage")

    response = client.post(
        "/knowledge-bases/from-file",
        json={"path": str(source_file)},
    )

    assert response.status_code == 400
    assert "Unsupported text file extension" in response.json()["detail"]


def test_create_knowledge_base_from_directory_imports_supported_files(
    tmp_path: Path,
) -> None:
    storage_path = tmp_path / "storage"
    source_directory = tmp_path / "docs"
    nested_directory = source_directory / "nested"
    nested_directory.mkdir(parents=True)
    (source_directory / "rag.md").write_text(
        "Directory import reads Markdown files.",
        encoding="utf-8",
    )
    nested_note = nested_directory / "notes.txt"
    nested_note.write_text(
        "Directory import includes nested text notes.",
        encoding="utf-8",
    )
    (source_directory / "ignored.pdf").write_text("ignored", encoding="utf-8")
    client = _client(storage_path)

    create_response = client.post(
        "/knowledge-bases/from-directory",
        json={"path": str(source_directory), "chunk_size": 200},
    )
    knowledge_base_id = create_response.json()["knowledge_base_id"]

    answer_response = client.post(
        f"/knowledge-bases/{knowledge_base_id}/answer",
        json={"question": "nested text notes", "limit": 1},
    )

    payload = answer_response.json()

    assert create_response.status_code == 200
    assert create_response.json()["document_count"] == 2
    assert create_response.json()["chunk_count"] == 2
    assert answer_response.status_code == 200
    assert payload["refused"] is False
    assert payload["citations"] == [f"{nested_note.resolve()}#chunk-0"]


def test_create_knowledge_base_from_directory_honors_extensions_filter(
    tmp_path: Path,
) -> None:
    source_directory = tmp_path / "docs"
    source_directory.mkdir()
    (source_directory / "rag.md").write_text("Markdown file", encoding="utf-8")
    note_file = source_directory / "notes.txt"
    note_file.write_text("Text extension filter keeps this note.", encoding="utf-8")
    client = _client(tmp_path / "storage")

    response = client.post(
        "/knowledge-bases/from-directory",
        json={"path": str(source_directory), "extensions": [".txt"], "chunk_size": 200},
    )
    knowledge_base_id = response.json()["knowledge_base_id"]

    answer_response = client.post(
        f"/knowledge-bases/{knowledge_base_id}/answer",
        json={"question": "extension filter note", "limit": 1},
    )

    payload = answer_response.json()

    assert response.status_code == 200
    assert response.json()["document_count"] == 1
    assert payload["refused"] is False
    assert payload["citations"] == [f"{note_file.resolve()}#chunk-0"]


def test_empty_directory_import_creates_refusing_knowledge_base(tmp_path: Path) -> None:
    source_directory = tmp_path / "empty"
    source_directory.mkdir()
    client = _client(tmp_path / "storage")

    create_response = client.post(
        "/knowledge-bases/from-directory",
        json={"path": str(source_directory), "chunk_size": 200},
    )
    knowledge_base_id = create_response.json()["knowledge_base_id"]

    answer_response = client.post(
        f"/knowledge-bases/{knowledge_base_id}/answer",
        json={"question": "anything"},
    )

    payload = answer_response.json()

    assert create_response.status_code == 200
    assert create_response.json()["document_count"] == 0
    assert create_response.json()["chunk_count"] == 0
    assert answer_response.status_code == 200
    assert payload["refused"] is True
    assert payload["citations"] == []


def test_create_knowledge_base_from_directory_returns_bad_request_for_non_directory(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "rag.md"
    source_file.write_text("not a directory", encoding="utf-8")
    client = _client(tmp_path / "storage")

    response = client.post(
        "/knowledge-bases/from-directory",
        json={"path": str(source_file)},
    )

    assert response.status_code == 400


def test_create_knowledge_base_from_file_validates_chunking_request(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "rag.md"
    source_file.write_text("RAG", encoding="utf-8")
    client = _client(tmp_path / "storage")

    response = client.post(
        "/knowledge-bases/from-file",
        json={"path": str(source_file), "chunk_size": 0},
    )

    assert response.status_code == 400
    assert "chunk_size must be greater than 0" in response.json()["detail"]


def test_create_knowledge_base_from_directory_validates_overlap(
    tmp_path: Path,
) -> None:
    source_directory = tmp_path / "docs"
    source_directory.mkdir()
    client = _client(tmp_path / "storage")

    response = client.post(
        "/knowledge-bases/from-directory",
        json={"path": str(source_directory), "chunk_size": 10, "overlap": 10},
    )

    assert response.status_code == 400
    assert "overlap must be smaller than chunk_size" in response.json()["detail"]


def _client(storage_path: Path) -> TestClient:
    settings = Settings(knowledge_base_storage_path=storage_path)
    return TestClient(create_app(settings))


def _create_rag_knowledge_base(client: TestClient) -> str:
    response = client.post(
        "/knowledge-bases",
        json={
            "documents": [
                {
                    "id": "doc-1",
                    "text": "RAG answers need citations so users can inspect sources.",
                    "metadata": {"source_path": "docs/rag.md", "file_type": ".md"},
                }
            ],
            "chunk_size": 200,
            "overlap": 0,
        },
    )

    assert response.status_code == 200
    return response.json()["knowledge_base_id"]
