from pathlib import Path


def test_project_closeout_docs_exist_and_describe_resume_ready_v1() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    technical_notes = Path("docs/TECHNICAL_NOTES.md").read_text(encoding="utf-8")
    learning_index = Path("docs/LEARNING_INDEX.md").read_text(encoding="utf-8")
    showcase = Path("docs/PROJECT_SHOWCASE.md").read_text(encoding="utf-8")

    for text in [readme, technical_notes, learning_index, showcase]:
        assert "Resume-ready V1" in text
        assert "citation-aware generation" in text
        assert "eval provider comparison" in text

    assert "ai-agent-workbench" in learning_index
    assert "ai-agent-workbench" in showcase


def test_project_closeout_root_notes_mark_next_mainline() -> None:
    root_notes = Path("../AI_AGENT_PORTFOLIO_NOTES.md").read_text(encoding="utf-8")

    assert "agentic-rag-lab" in root_notes
    assert "Resume-ready V1" in root_notes
    assert "ai-agent-workbench" in root_notes
    assert "下一主线" in root_notes


def test_project_closeout_docs_do_not_contain_real_provider_secret() -> None:
    docs = [
        Path("README.md"),
        Path("docs/TECHNICAL_NOTES.md"),
        Path("docs/LEARNING_INDEX.md"),
        Path("docs/PROJECT_SHOWCASE.md"),
        Path("docs/REAL_PROVIDER_SMOKE_GUIDE.md"),
        Path("../AI_AGENT_PORTFOLIO_NOTES.md"),
    ]

    combined = "\n".join(path.read_text(encoding="utf-8") for path in docs)

    assert "OPENAI_COMPATIBLE_API_KEY" in combined
    assert "your-api-key" in combined
    assert "tp-" not in combined
    assert "Authorization: Bearer" not in combined
