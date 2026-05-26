from agentic_rag_lab.config import Settings
from agentic_rag_lab.llm.base import LLMProvider
from agentic_rag_lab.llm.fake import FakeLLMProvider


def create_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "fake":
        return FakeLLMProvider()

    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
