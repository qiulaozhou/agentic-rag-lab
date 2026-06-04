import httpx
import pytest

from agentic_rag_lab.embeddings import OpenAICompatibleEmbeddingProvider


def test_openai_compatible_embedding_provider_parses_mock_response() -> None:
    captured_request = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_request["url"] = str(request.url)
        captured_request["authorization"] = request.headers["authorization"]
        captured_request["json"] = request.read().decode("utf-8")
        return httpx.Response(
            200,
            json={"data": [{"embedding": [0.1, 0.2, 0.3]}]},
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenAICompatibleEmbeddingProvider(
        api_key="test-key",
        base_url="https://example.test/v1/",
        model="embedding-test",
        client=client,
    )

    vector = provider.embed("RAG citations")

    assert vector == [0.1, 0.2, 0.3]
    assert captured_request["url"] == "https://example.test/v1/embeddings"
    assert captured_request["authorization"] == "Bearer test-key"
    assert '"model":"embedding-test"' in captured_request["json"]
    assert '"input":"RAG citations"' in captured_request["json"]


def test_openai_compatible_embedding_provider_requires_configuration() -> None:
    with pytest.raises(ValueError, match="OPENAI_COMPATIBLE_API_KEY"):
        OpenAICompatibleEmbeddingProvider(
            api_key=None,
            base_url="https://example.test/v1",
            model="embedding-test",
        )

    with pytest.raises(ValueError, match="OPENAI_COMPATIBLE_BASE_URL"):
        OpenAICompatibleEmbeddingProvider(
            api_key="test-key",
            base_url=" ",
            model="embedding-test",
        )

    with pytest.raises(ValueError, match="OPENAI_COMPATIBLE_EMBEDDING_MODEL"):
        OpenAICompatibleEmbeddingProvider(
            api_key="test-key",
            base_url="https://example.test/v1",
            model=None,
        )


def test_openai_compatible_embedding_provider_raises_for_non_2xx() -> None:
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(500, request=request, json={"error": "bad"})
        )
    )
    provider = OpenAICompatibleEmbeddingProvider(
        api_key="test-key",
        base_url="https://example.test/v1",
        model="embedding-test",
        client=client,
    )

    with pytest.raises(ValueError, match="embedding request failed: 500"):
        provider.embed("RAG")


def test_openai_compatible_embedding_provider_raises_for_malformed_response() -> None:
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"data": [{"not_embedding": []}]})
        )
    )
    provider = OpenAICompatibleEmbeddingProvider(
        api_key="test-key",
        base_url="https://example.test/v1",
        model="embedding-test",
        client=client,
    )

    with pytest.raises(ValueError, match="Malformed embedding response"):
        provider.embed("RAG")
