"""OpenAI-compatible embedding provider."""

from __future__ import annotations

from collections.abc import Sequence

import httpx


class OpenAICompatibleEmbeddingProvider:
    """Fetch embeddings from an OpenAI-compatible `/embeddings` endpoint."""

    def __init__(
        self,
        api_key: str | None,
        base_url: str | None,
        model: str | None,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = _required_value(api_key, "OPENAI_COMPATIBLE_API_KEY")
        self.base_url = _required_value(
            base_url,
            "OPENAI_COMPATIBLE_BASE_URL",
        ).rstrip("/")
        self.model = _required_value(model, "OPENAI_COMPATIBLE_EMBEDDING_MODEL")
        self._client = client or httpx.Client()

    def embed(self, text: str) -> list[float]:
        response = self._client.post(
            f"{self.base_url}/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "input": text},
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ValueError(
                f"OpenAI-compatible embedding request failed: {response.status_code}"
            ) from exc

        return _parse_embedding_response(response.json())


def _parse_embedding_response(payload: object) -> list[float]:
    if not isinstance(payload, dict):
        raise ValueError("Malformed embedding response: expected object")

    data = payload.get("data")
    if not isinstance(data, list) or not data:
        raise ValueError("Malformed embedding response: missing data")

    first_item = data[0]
    if not isinstance(first_item, dict):
        raise ValueError("Malformed embedding response: data item must be object")

    embedding = first_item.get("embedding")
    if not _is_number_sequence(embedding):
        raise ValueError("Malformed embedding response: missing embedding vector")

    return [float(value) for value in embedding]


def _is_number_sequence(value: object) -> bool:
    if not isinstance(value, Sequence) or isinstance(value, str):
        return False
    return all(isinstance(item, int | float) for item in value)


def _required_value(value: str | None, name: str) -> str:
    if value is None or not value.strip():
        raise ValueError(f"{name} is required for openai_compatible provider")
    return value.strip()


__all__ = ["OpenAICompatibleEmbeddingProvider"]
