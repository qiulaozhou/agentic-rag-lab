from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMRequest:
    prompt: str
    system_prompt: str | None = None


@dataclass(frozen=True)
class LLMResponse:
    text: str
    model: str


class LLMProvider(Protocol):
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text for a prompt."""
