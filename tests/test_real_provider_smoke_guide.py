from pathlib import Path


def test_real_provider_smoke_guide_contains_required_safe_configuration() -> None:
    guide = Path("docs/REAL_PROVIDER_SMOKE_GUIDE.md").read_text(encoding="utf-8")
    env_example = Path(".env.example").read_text(encoding="utf-8")

    required_names = [
        "EMBEDDING_PROVIDER=openai_compatible",
        "ANSWER_GENERATOR=openai_compatible",
        "OPENAI_COMPATIBLE_API_KEY",
        "OPENAI_COMPATIBLE_BASE_URL",
        "OPENAI_COMPATIBLE_EMBEDDING_MODEL",
        "OPENAI_COMPATIBLE_CHAT_MODEL",
    ]

    for name in required_names:
        assert name in guide

    assert "OPENAI_COMPATIBLE_API_KEY=" in env_example
    assert "your-api-key" in guide
    assert "your-openai-compatible-base-url" in guide
    assert "your-embedding-model" in guide
    assert "your-chat-model" in guide


def test_real_provider_smoke_guide_documents_manual_api_checks() -> None:
    guide = Path("docs/REAL_PROVIDER_SMOKE_GUIDE.md").read_text(encoding="utf-8")

    for endpoint in [
        "/health",
        "/answer",
        "/knowledge-bases",
        "/knowledge-bases/from-file",
    ]:
        assert endpoint in guide

    assert "uv run uvicorn agentic_rag_lab.main:app --reload" in guide
    assert "pytest 不会跑真实服务" in guide
