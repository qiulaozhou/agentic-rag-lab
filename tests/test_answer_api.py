from fastapi.testclient import TestClient

from agentic_rag_lab.main import create_app


def test_answer_endpoint_returns_answer_with_citation() -> None:
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
            "overlap": 0,
            "limit": 1,
        },
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["refused"] is False
    assert payload["citations"] == ["docs/rag.md#chunk-0"]
    assert "RAG answers need citations" in payload["text"]


def test_answer_endpoint_preserves_request_metadata_in_citation() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/answer",
        json={
            "question": "answer endpoint metadata citation",
            "documents": [
                {
                    "id": "doc-1",
                    "text": "The answer endpoint keeps metadata available for citation.",
                    "metadata": {"source_path": "notes/api.md", "file_type": ".md"},
                }
            ],
            "chunk_size": 200,
        },
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["refused"] is False
    assert payload["citations"] == ["notes/api.md#chunk-0"]


def test_answer_endpoint_refuses_empty_question() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/answer",
        json={
            "question": "   ",
            "documents": [
                {
                    "id": "doc-1",
                    "text": "RAG answers need citations.",
                    "metadata": {"source_path": "docs/rag.md"},
                }
            ],
        },
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["refused"] is True
    assert payload["citations"] == []


def test_answer_endpoint_refuses_unrelated_question() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/answer",
        json={
            "question": "retrieval",
            "documents": [
                {
                    "id": "doc-1",
                    "text": "!!!",
                    "metadata": {"source_path": "docs/symbols.txt"},
                }
            ],
        },
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["refused"] is True
    assert payload["citations"] == []


def test_answer_endpoint_refuses_empty_documents() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/answer",
        json={
            "question": "anything",
            "documents": [],
            "chunk_size": 200,
        },
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["refused"] is True
    assert payload["citations"] == []


def test_answer_endpoint_returns_bad_request_for_invalid_limit() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/answer",
        json={
            "question": "RAG",
            "documents": [],
            "limit": 0,
        },
    )

    assert response.status_code == 400
    assert "limit must be greater than 0" in response.json()["detail"]


def test_answer_endpoint_returns_bad_request_for_invalid_chunk_size() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/answer",
        json={
            "question": "RAG",
            "documents": [],
            "chunk_size": 0,
        },
    )

    assert response.status_code == 400
    assert "chunk_size must be greater than 0" in response.json()["detail"]


def test_answer_endpoint_returns_bad_request_for_invalid_overlap() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/answer",
        json={
            "question": "RAG",
            "documents": [],
            "chunk_size": 10,
            "overlap": 10,
        },
    )

    assert response.status_code == 400
    assert "overlap must be smaller than chunk_size" in response.json()["detail"]


def test_answer_endpoint_returns_bad_request_for_negative_overlap() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/answer",
        json={
            "question": "RAG",
            "documents": [],
            "chunk_size": 10,
            "overlap": -1,
        },
    )

    assert response.status_code == 400
    assert "overlap must be greater than or equal to 0" in response.json()["detail"]
