"""OpenAI-compatible chat completion provider."""

from __future__ import annotations

import httpx

from agentic_rag_lab.llm.base import LLMRequest, LLMResponse


class OpenAICompatibleLLMProvider:
    """Generate text through an OpenAI-compatible `/chat/completions` endpoint."""

    def __init__(
        self,
        api_key: str | None,
        base_url: str | None,
        model: str | None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = _required_value(api_key, "OPENAI_COMPATIBLE_API_KEY")
        self.base_url = _required_value(
            base_url,
            "OPENAI_COMPATIBLE_BASE_URL",
        ).rstrip("/")
        self.model = _required_value(model, "OPENAI_COMPATIBLE_CHAT_MODEL")
        self._client = client or httpx.AsyncClient()

    async def generate(self, request: LLMRequest) -> LLMResponse:
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        response = await self._client.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": messages,
                "temperature": 0,
            },
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ValueError(
                f"OpenAI-compatible chat request failed: {response.status_code}"
            ) from exc

        return _parse_chat_response(response.json(), fallback_model=self.model)


def _parse_chat_response(payload: object, fallback_model: str) -> LLMResponse:
    if not isinstance(payload, dict):
        raise ValueError("Malformed chat completion response: expected object")

    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("Malformed chat completion response: missing choices")

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise ValueError("Malformed chat completion response: choice must be object")

    message = first_choice.get("message")
    if not isinstance(message, dict):
        raise ValueError("Malformed chat completion response: missing message")

    content = message.get("content")
    if not isinstance(content, str):
        raise ValueError("Malformed chat completion response: missing content")

    model = payload.get("model")
    if not isinstance(model, str) or not model.strip():
        model = fallback_model

    return LLMResponse(text=content, model=model)


def _required_value(value: str | None, name: str) -> str:
    if value is None or not value.strip():
        raise ValueError(f"{name} is required for openai_compatible provider")
    return value.strip()


__all__ = ["OpenAICompatibleLLMProvider"]
