# Directory Structure

> Backend code organization for the Agentic RAG Lab skeleton.

---

## Overview

This project uses a Python `src` layout with one import package:
`agentic_rag_lab`.

The first milestone is a FastAPI service skeleton. RAG capabilities are split
by boundary so later tasks can add real behavior incrementally without mixing
document loading, retrieval, and answer generation in one module.

---

## Directory Layout

```text
src/agentic_rag_lab/
├── api/          # FastAPI routers
├── chunking/     # document chunking boundary
├── evals/        # evaluation boundary
├── generation/   # answer generation boundary
├── ingestion/    # document ingestion boundary
├── llm/          # model provider interface and implementations
├── retrieval/    # retrieval/search boundary
├── config.py     # environment settings
├── main.py       # FastAPI app factory and ASGI app object
└── schemas.py    # shared domain data shapes
```

Tests live under `tests/` and import the package through pytest's configured
`pythonpath = ["src"]`.

---

## Module Organization

- Put HTTP endpoints in `api/` routers and register them in `main.py`.
- Keep model-specific code behind `llm/LLMProvider`; application code should
  not call vendor SDKs directly.
- Keep ingestion, chunking, retrieval, generation, and eval as separate
  boundaries. Do not implement RAG flow logic inside API route functions.
- Put local Markdown/TXT file loading in `ingestion/text.py`. It should turn
  filesystem inputs into `SourceDocument` values and preserve source metadata.
- Put deterministic text splitting in `chunking/text.py`. It should turn
  `SourceDocument` values into `DocumentChunk` values without knowing about
  embeddings, retrieval stores, or answer generation.
- Put small shared domain data shapes in `schemas.py` until there is enough
  complexity to split them by subsystem.

---

## Naming Conventions

- Use snake_case for Python modules and functions.
- Use explicit provider names such as `FakeLLMProvider`.
- Keep public factory functions named `create_*`, for example `create_app`
  and `create_llm_provider`.

---

## Examples

- `src/agentic_rag_lab/main.py` shows the FastAPI app factory pattern.
- `src/agentic_rag_lab/api/health.py` shows a minimal router.
- `src/agentic_rag_lab/llm/base.py` and `llm/fake.py` show the provider
  boundary and offline implementation.
- `src/agentic_rag_lab/ingestion/text.py` is the expected home for local text
  file ingestion.
- `src/agentic_rag_lab/chunking/text.py` is the expected home for local text
  chunking.
