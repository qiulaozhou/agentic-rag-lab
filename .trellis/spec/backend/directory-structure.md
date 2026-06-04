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
├── embeddings/   # embedding provider boundary
├── evals/        # evaluation boundary
├── generation/   # answer generation boundary
├── ingestion/    # document ingestion boundary
├── knowledge_base/ # local knowledge base registry boundary
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
- Keep API request/response DTOs in `api/` modules when they only describe
  HTTP wire shape. Do not force HTTP DTOs into shared domain schemas.
- Keep model-specific code behind `llm/LLMProvider`; application code should
  not call vendor SDKs directly.
- Keep ingestion, chunking, retrieval, generation, and eval as separate
  boundaries. Do not implement RAG flow logic inside API route functions.
- Put local Markdown/TXT file loading in `ingestion/text.py`. It should turn
  filesystem inputs into `SourceDocument` values and preserve source metadata.
- Put deterministic text splitting in `chunking/text.py`. It should turn
  `SourceDocument` values into `DocumentChunk` values without knowing about
  embeddings, retrieval stores, or answer generation.
- Put embedding providers in `embeddings/`. Local test providers should stay
  deterministic and offline; real provider SDKs should remain behind the
  `EmbeddingProvider` protocol when added later.
- Put OpenAI-compatible embedding adapters in `embeddings/` and create them
  through `create_embedding_provider(settings)`. API route handlers should not
  call embedding HTTP endpoints directly.
- Put vector retrieval adapters in `retrieval/`. Retrieval code should return
  `RetrievalResult` values and preserve the original `DocumentChunk` metadata.
- Put retrieval composition code in `retrieval/pipeline.py`. Pipeline code
  should compose chunking and vector search without duplicating similarity
  logic.
- Put citation-aware answer generation in `generation/`. Generation code should
  consume `RetrievalResult` values and return `GeneratedAnswer` values without
  reaching back into ingestion, chunking, embedding, or vector-store internals.
- Put LLM-backed answer generator adapters in `generation/`. They may ask an
  `LLMProvider` for answer text, but citations must still be derived from local
  `RetrievalResult` metadata.
- Put answer pipeline composition in `generation/pipeline.py` until the project
  needs a broader application service layer. The answer pipeline should compose
  retrieval and generation without duplicating either subsystem's logic.
- Put refusal policies in `generation/refusal.py`. Refusal code should decide
  whether evidence is sufficient before answer generation runs.
- Put local eval helpers in `evals/`. Eval code should run existing pipelines
  and compare outputs against deterministic expectations; it should not
  duplicate retrieval, generation, or refusal logic.
- Put provider comparison eval helpers in `evals/`. Comparison code should
  compare `EvalReport` outputs by `case_id` and should allow custom pipeline
  factories for provider-specific runs without coupling evals to HTTP routes.
- Put local knowledge base registry code in `knowledge_base/`. Knowledge base
  code may compose chunking and answer pipeline construction, but it should not
  duplicate embedding, retrieval ranking, citation, or refusal logic.
- Put disk-backed knowledge base persistence in `knowledge_base/`. Disk
  persistence should store serializable documents/chunks/config and rebuild
  runtime pipelines on load.
- Put small shared domain data shapes in `schemas.py` until there is enough
  complexity to split them by subsystem.

---

## Naming Conventions

- Use snake_case for Python modules and functions.
- Use explicit provider names such as `FakeLLMProvider`.
- Keep public factory functions named `create_*`, for example `create_app`
  and `create_llm_provider`. Provider selection should flow through factories
  such as `create_embedding_provider` and `create_answer_generator`.

---

## Examples

- `src/agentic_rag_lab/main.py` shows the FastAPI app factory pattern.
- `src/agentic_rag_lab/api/health.py` shows a minimal router.
- `src/agentic_rag_lab/api/answer.py` shows the minimal HTTP answer boundary
  around the local answer pipeline.
- `src/agentic_rag_lab/api/knowledge_base.py` shows the minimal reusable local
  knowledge base HTTP boundary, including direct document creation and local
  file/directory import entrypoints.
- `src/agentic_rag_lab/llm/base.py` and `llm/fake.py` show the provider
  boundary and offline implementation.
- `src/agentic_rag_lab/ingestion/text.py` is the expected home for local text
  file ingestion.
- `src/agentic_rag_lab/chunking/text.py` is the expected home for local text
  chunking.
- `src/agentic_rag_lab/embeddings/local.py` is the expected home for the
  deterministic local embedding provider.
- `src/agentic_rag_lab/embeddings/openai_compatible.py` is the expected home
  for the optional OpenAI-compatible embedding provider.
- `src/agentic_rag_lab/embeddings/factory.py` is the expected home for
  settings-driven embedding provider creation.
- `src/agentic_rag_lab/retrieval/vector.py` is the expected home for the
  in-memory vector retrieval adapter.
- `src/agentic_rag_lab/retrieval/pipeline.py` is the expected home for the
  local retrieval pipeline boundary.
- `src/agentic_rag_lab/generation/citation.py` is the expected home for the
  deterministic citation-aware answer generator.
- `src/agentic_rag_lab/generation/llm_backed.py` is the expected home for
  LLM-backed answer generation that still keeps local citation authority.
- `src/agentic_rag_lab/generation/factory.py` is the expected home for
  settings-driven answer generator creation.
- `src/agentic_rag_lab/generation/pipeline.py` is the expected home for the
  local answer pipeline boundary.
- `src/agentic_rag_lab/generation/refusal.py` is the expected home for
  deterministic refusal policies.
- `src/agentic_rag_lab/evals/basic.py` is the expected home for the first local
  deterministic RAG eval runner.
- `docs/REAL_PROVIDER_SMOKE_GUIDE.md` is the expected home for manual real
  provider smoke checks. It must use environment variable placeholders rather
  than real secrets.
- `docs/LEARNING_INDEX.md` is the expected home for the project-level learning
  sequence. It should explain what each task did, why it mattered, where it
  sits in the RAG flow, and what was learned.
- `docs/PROJECT_SHOWCASE.md` is the expected home for resume/interview project
  presentation. It should separate overall project capability from
  author-scoped implementation work and should not overstate production
  readiness.
- `src/agentic_rag_lab/llm/openai_compatible.py` is the expected home for the
  optional OpenAI-compatible chat completion provider.
- `src/agentic_rag_lab/knowledge_base/local.py` is the expected home for the
  in-process local knowledge base registry.
- `src/agentic_rag_lab/knowledge_base/disk.py` is the expected home for the
  JSON-backed local knowledge base registry.
