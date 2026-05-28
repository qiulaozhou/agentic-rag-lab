# Quality Guidelines

> Code quality standards for backend development.

---

## Overview

The initial project standard is a small, runnable FastAPI skeleton verified by
pytest. Keep early tasks narrow: build one capability at a time and preserve
offline smoke tests.

---

## Forbidden Patterns

- Do not require real model credentials for smoke tests.
- Do not call LLM or embedding provider SDKs directly from API route functions.
- Do not choose a permanent vector database inside unrelated tasks.
- Do not introduce PDF parsing, embeddings, vector storage, real LLM calls,
  LangGraph, MCP, or a web UI inside an ingestion/chunking task.
- Do not commit `.env`, local credentials, `.venv/`, or pytest/cache output.
- Do not add placeholder API contracts that pretend RAG is implemented before
  retrieval and citation behavior exist.

---

## Required Patterns

- Use `uv` and `pyproject.toml` for project dependencies.
- Keep a committed `.env.example` for safe local configuration examples.
- Keep FastAPI startup importable through `agentic_rag_lab.main:app`.
- Keep provider-specific model calls behind the `LLMProvider` protocol.
- Add tests for each externally visible behavior added by a task.
- Keep text ingestion and chunking deterministic: stable ordering, stable IDs,
  and no random UUIDs in outputs that tests or later retrieval depend on.
- Preserve source metadata through ingestion and chunking so later citation
  work can trace answers back to files.

---

## Testing Requirements

- Run `uv run pytest` before completing a task when dependencies are available.
- `python -m pytest` from the project virtual environment must also work.
- Smoke tests must run without network access or paid model credentials.
- Text-processing tests must use local fixtures or `tmp_path`, not external
  files outside the test workspace.

---

## Code Review Checklist

- The task stays within its PRD scope.
- New public behavior is covered by a focused test.
- Secrets and local-only files are ignored.
- New RAG behavior respects the existing subsystem boundaries.
