"""Answer generator factory."""

from agentic_rag_lab.config import Settings
from agentic_rag_lab.generation.citation import CitationAwareAnswerGenerator
from agentic_rag_lab.generation.llm_backed import LLMBackedCitationAwareAnswerGenerator
from agentic_rag_lab.llm.openai_compatible import OpenAICompatibleLLMProvider


def create_answer_generator(settings: Settings):
    """Create the configured answer generator."""

    if settings.answer_generator == "local_citation":
        return CitationAwareAnswerGenerator()
    if settings.answer_generator == "openai_compatible":
        return LLMBackedCitationAwareAnswerGenerator(
            OpenAICompatibleLLMProvider(
                api_key=settings.openai_compatible_api_key,
                base_url=settings.openai_compatible_base_url,
                model=settings.openai_compatible_chat_model,
            )
        )

    raise ValueError(f"Unsupported answer generator: {settings.answer_generator}")


__all__ = ["create_answer_generator"]
