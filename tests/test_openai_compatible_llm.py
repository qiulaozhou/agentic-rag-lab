import asyncio

import httpx
import pytest

from agentic_rag_lab.llm import LLMRequest, OpenAICompatibleLLMProvider


def test_openai_compatible_llm_provider_parses_mock_response() -> None:
    captured_request = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_request["url"] = str(request.url)
        captured_request["authorization"] = request.headers["authorization"]
        captured_request["json"] = request.read().decode("utf-8")
        return httpx.Response(
            200,
            json={
                "model": "chat-test",
                "choices": [{"message": {"content": "Mock model answer."}}],
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = OpenAICompatibleLLMProvider(
        api_key="test-key",
        base_url="https://example.test/v1/",
        model="chat-test",
        client=client,
    )

    response = asyncio.run(
        provider.generate(
            LLMRequest(prompt="Use this evidence.", system_prompt="Stay grounded.")
        )
    )

    assert response.text == "Mock model answer."
    assert response.model == "chat-test"
    assert captured_request["url"] == "https://example.test/v1/chat/completions"
    assert captured_request["authorization"] == "Bearer test-key"
    assert '"model":"chat-test"' in captured_request["json"]
    assert '"role":"system"' in captured_request["json"]
    assert '"role":"user"' in captured_request["json"]


def test_openai_compatible_llm_provider_requires_configuration() -> None:
    with pytest.raises(ValueError, match="OPENAI_COMPATIBLE_API_KEY"):
        OpenAICompatibleLLMProvider(
            api_key=None,
            base_url="https://example.test/v1",
            model="chat-test",
        )

    with pytest.raises(ValueError, match="OPENAI_COMPATIBLE_BASE_URL"):
        OpenAICompatibleLLMProvider(
            api_key="test-key",
            base_url="",
            model="chat-test",
        )

    with pytest.raises(ValueError, match="OPENAI_COMPATIBLE_CHAT_MODEL"):
        OpenAICompatibleLLMProvider(
            api_key="test-key",
            base_url="https://example.test/v1",
            model=None,
        )


def test_openai_compatible_llm_provider_raises_for_non_2xx() -> None:
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(429, request=request, json={"error": "bad"})
        )
    )
    provider = OpenAICompatibleLLMProvider(
        api_key="test-key",
        base_url="https://example.test/v1",
        model="chat-test",
        client=client,
    )

    with pytest.raises(ValueError, match="chat request failed: 429"):
        asyncio.run(provider.generate(LLMRequest(prompt="RAG")))


def test_openai_compatible_llm_provider_raises_for_malformed_response() -> None:
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"choices": [{"message": {}}]})
        )
    )
    provider = OpenAICompatibleLLMProvider(
        api_key="test-key",
        base_url="https://example.test/v1",
        model="chat-test",
        client=client,
    )

    with pytest.raises(ValueError, match="Malformed chat completion response"):
        asyncio.run(provider.generate(LLMRequest(prompt="RAG")))
