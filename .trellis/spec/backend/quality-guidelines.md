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
- Do not require real embedding credentials or vector database services for
  early retrieval smoke tests.
- Do not require a real LLM for early citation-aware generation tests.
- Do not commit `.env`, local credentials, `.venv/`, or pytest/cache output.
- Do not add placeholder API contracts that pretend RAG is implemented before
  retrieval and citation behavior exist.
- Do not duplicate RAG pipeline logic inside API route handlers.
- Do not put reusable knowledge base state in module-level globals; attach it
  to the FastAPI app or another explicit dependency boundary.
- Do not treat in-process knowledge base state as disk persistence.
- Do not commit local knowledge base data files. Runtime storage should stay
  under an ignored path such as `.local/`.
- Do not serialize runtime pipeline objects. Persist documents, chunks, and
  configuration, then rebuild pipelines during load.
- Do not add multipart upload or browser upload behavior without an explicit
  task for upload dependencies, file-size limits, and filename safety.
- Do not enable real embedding or LLM providers by default. Real providers
  must be opt-in through explicit settings.
- Do not write real API keys, Authorization headers, or local `.env` secrets
  into code, tests, README files, learning notes, or Trellis task documents.
- Do not trust LLM-generated citation strings. Citations must be derived from
  local retrieval evidence metadata.
- Do not let API route handlers call OpenAI-compatible HTTP endpoints directly.
  Use provider adapters and factories.

---

## Required Patterns

- Use `uv` and `pyproject.toml` for project dependencies.
- Keep a committed `.env.example` for safe local configuration examples.
- Keep FastAPI startup importable through `agentic_rag_lab.main:app`.
- Keep provider-specific model calls behind the `LLMProvider` protocol.
- Keep provider-specific embedding calls behind the `EmbeddingProvider`
  protocol.
- Use settings-driven factories for provider selection. Default providers
  should remain offline and deterministic.
- Add tests for each externally visible behavior added by a task.
- Keep text ingestion and chunking deterministic: stable ordering, stable IDs,
  and no random UUIDs in outputs that tests or later retrieval depend on.
- Preserve source metadata through ingestion and chunking so later citation
  work can trace answers back to files.
- Keep local embedding and vector retrieval deterministic until the adapter
  contract is proven by tests.
- Keep provider-specific embedding calls behind an `EmbeddingProvider` boundary
  when real embedding services are added later.
- Preserve `DocumentChunk` metadata in `RetrievalResult` outputs.
- Keep retrieval pipeline code focused on composition. It should not duplicate
  chunking, embedding, or vector similarity logic.
- Keep early answer generation grounded in `RetrievalResult` evidence. It
  should not invent citations or facts outside the retrieved chunks.
- Build citations from source metadata when available, and fall back to stable
  chunk identifiers when metadata is incomplete.
- Keep answer pipeline code focused on composition. It should call retrieval
  and generation boundaries instead of duplicating search, embedding, ranking,
  snippet, or citation logic.
- Keep refusal behavior explicit and testable. Refusal decisions should run
  after retrieval and before answer generation.
- Refused answers must not include citations, because no evidence has been
  accepted as sufficient.
- Knowledge base API handlers should call registry and answer pipeline
  boundaries. They should not reimplement chunking, embedding, retrieval,
  citation, or refusal logic inside route functions.
- In-process registries should use deterministic identifiers in tests so API
  behavior remains stable.
- Disk-backed registries should write UTF-8 JSON through a temporary file and
  replace the target file after a complete write.
- Disk-backed registries should fail loudly on malformed or incomplete JSON
  rather than silently skipping broken knowledge bases.
- File and directory import API handlers should reuse ingestion helpers. They
  should not duplicate text file parsing, extension filtering, or metadata
  construction inside route functions.
- File and directory import endpoints should preserve ingestion metadata so
  citations can still resolve to `source_path#chunk-{chunk_index}`.
- OpenAI-compatible provider adapters should validate required key, base URL,
  and model settings and fail with clear `ValueError` messages when missing.
- LLM-backed answer generators may use model output for `GeneratedAnswer.text`,
  but must attach citations from the evidence actually used by the generator.
- Empty evidence should not call a real LLM-backed generator; refusal should
  remain local and deterministic.
- Real provider smoke checks should be documented as manual steps. They should
  not be added to default pytest unless a later task creates an explicit
  opt-in integration test strategy.
- Eval provider comparison should compare reports by stable `case_id` and
  report candidate-minus-baseline deltas for answer, citation, refusal, and
  total pass counts.
- Project closeout tasks must update the project README, technical notes,
  project learning index, project showcase, root portfolio notes, and task
  learning notes in the same task.
- Project closeout documentation must clearly distinguish resume-ready V1 from
  production readiness. It should list completed capabilities, explicit
  limitations, verification results, and the next main project.
- Trellis/harness practice may be documented as an engineering workflow
  constraint, but it should not be misrepresented as the RAG product's business
  capability.

---

## Testing Requirements

- Run `uv run pytest` before completing a task when dependencies are available.
- `python -m pytest` from the project virtual environment must also work.
- Smoke tests must run without network access or paid model credentials.
- OpenAI-compatible provider tests must use mocked HTTP transports such as
  `httpx.MockTransport`; pytest must not call real provider endpoints.
- Text-processing tests must use local fixtures or `tmp_path`, not external
  files outside the test workspace.
- Retrieval tests must verify ranking, limit behavior, empty-query behavior,
  and source metadata preservation.
- Retrieval pipeline tests must verify both construction from chunks and
  construction from source documents.
- Generation tests must verify citation formatting, citation fallback,
  no-evidence refusal, and end-to-end flow from retrieval results to
  `GeneratedAnswer`.
- Answer pipeline tests must verify construction from chunks, construction from
  source documents, no-evidence refusal, limit validation, and source citation
  preservation.
- Refusal tests must verify empty queries, empty evidence, low-score evidence,
  threshold behavior, and custom policy configuration.
- Eval tests must verify answer term checks, citation checks, refusal checks,
  failing cases, and aggregate report counts.
- HTTP API tests must verify successful answer responses, refusal responses,
  metadata-to-citation preservation, and 400 responses for invalid request
  parameters.
- Knowledge base API tests must verify create, answer, unknown-id, refusal, and
  invalid-parameter behavior without external services.
- Disk-backed knowledge base tests must verify JSON creation, app-restart
  recovery, next-id behavior, empty knowledge bases, and malformed-file errors
  with `tmp_path`.
- File/directory import API tests must verify supported files, unsupported
  files, missing paths, empty directories, app-restart recovery, and citation
  preservation with `tmp_path`.
- Provider factory tests must verify local defaults and explicit opt-in
  provider construction.
- OpenAI-compatible adapter tests must verify request payloads, successful
  response parsing, non-2xx errors, malformed responses, and missing
  configuration behavior.
- Manual smoke guide tests should verify that the guide contains required
  environment variable names and endpoint examples, but should not include real
  secrets.
- Eval comparison tests should use fake or custom pipelines rather than real
  network providers.
- Project closeout documentation tests should verify key docs mention the
  resume-ready status, full RAG flow, next main project, and safe provider
  secret handling.

---

## Code Review Checklist

- The task stays within its PRD scope.
- New public behavior is covered by a focused test.
- Secrets and local-only files are ignored.
- New RAG behavior respects the existing subsystem boundaries.
