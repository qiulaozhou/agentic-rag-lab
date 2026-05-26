from agentic_rag_lab.llm.base import LLMRequest, LLMResponse


class FakeLLMProvider:
    """Deterministic offline provider for smoke tests and local development."""

    async def generate(self, request: LLMRequest) -> LLMResponse:
        prompt = request.prompt.strip()
        text = prompt if prompt else "No prompt provided."
        return LLMResponse(text=f"fake response: {text}", model="fake")
