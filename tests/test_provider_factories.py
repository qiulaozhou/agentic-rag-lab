from pathlib import Path

import pytest

from agentic_rag_lab.config import Settings
from agentic_rag_lab.embeddings import (
    LocalHashEmbeddingProvider,
    OpenAICompatibleEmbeddingProvider,
    create_embedding_provider,
)
from agentic_rag_lab.generation import (
    CitationAwareAnswerGenerator,
    LLMBackedCitationAwareAnswerGenerator,
    create_answer_generator,
)
from agentic_rag_lab.llm import FakeLLMProvider, OpenAICompatibleLLMProvider, create_llm_provider
from agentic_rag_lab.main import create_app


def test_default_factories_keep_offline_local_providers() -> None:
    settings = Settings()

    assert isinstance(create_embedding_provider(settings), LocalHashEmbeddingProvider)
    assert isinstance(create_answer_generator(settings), CitationAwareAnswerGenerator)
    assert isinstance(create_llm_provider(settings), FakeLLMProvider)


def test_openai_compatible_embedding_factory_requires_configuration() -> None:
    settings = Settings(embedding_provider="openai_compatible")

    with pytest.raises(ValueError, match="OPENAI_COMPATIBLE_API_KEY"):
        create_embedding_provider(settings)


def test_openai_compatible_answer_factory_requires_configuration() -> None:
    settings = Settings(answer_generator="openai_compatible")

    with pytest.raises(ValueError, match="OPENAI_COMPATIBLE_API_KEY"):
        create_answer_generator(settings)


def test_openai_compatible_factories_create_provider_instances() -> None:
    settings = Settings(
        llm_provider="openai_compatible",
        embedding_provider="openai_compatible",
        answer_generator="openai_compatible",
        openai_compatible_api_key="test-key",
        openai_compatible_base_url="https://example.test/v1",
        openai_compatible_embedding_model="embedding-test",
        openai_compatible_chat_model="chat-test",
    )

    assert isinstance(
        create_embedding_provider(settings),
        OpenAICompatibleEmbeddingProvider,
    )
    assert isinstance(
        create_llm_provider(settings),
        OpenAICompatibleLLMProvider,
    )
    assert isinstance(
        create_answer_generator(settings),
        LLMBackedCitationAwareAnswerGenerator,
    )


def test_create_app_keeps_default_local_providers(tmp_path: Path) -> None:
    app = create_app(Settings(knowledge_base_storage_path=tmp_path))

    assert isinstance(app.state.embedding_provider, LocalHashEmbeddingProvider)
    assert isinstance(app.state.answer_generator, CitationAwareAnswerGenerator)


def test_env_example_contains_only_provider_variable_placeholders() -> None:
    env_example = Path(".env.example").read_text(encoding="utf-8")

    assert "OPENAI_COMPATIBLE_API_KEY=" in env_example
    assert "OPENAI_COMPATIBLE_BASE_URL=" in env_example
    assert "OPENAI_COMPATIBLE_EMBEDDING_MODEL=your-embedding-model" in env_example
    assert "OPENAI_COMPATIBLE_CHAT_MODEL=your-chat-model" in env_example
