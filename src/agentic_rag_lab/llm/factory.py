from agentic_rag_lab.config import Settings
from agentic_rag_lab.llm.base import LLMProvider
from agentic_rag_lab.llm.fake import FakeLLMProvider
from agentic_rag_lab.llm.openai_compatible import OpenAICompatibleLLMProvider


def create_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "fake":
        return FakeLLMProvider()
    if settings.llm_provider == "openai_compatible":
        return OpenAICompatibleLLMProvider(
            api_key=settings.openai_compatible_api_key,
            base_url=settings.openai_compatible_base_url,
            model=settings.openai_compatible_chat_model,
        )

    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
