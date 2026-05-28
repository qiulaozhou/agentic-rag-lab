# Add Markdown/TXT ingestion and chunking

## Goal

Implement the first local RAG data pipeline slice:

```text
Markdown/TXT file -> SourceDocument -> DocumentChunk -> pytest
```

This task turns the skeleton's placeholder ingestion and chunking boundaries
into deterministic, offline, test-covered behavior.

## Requirements

- Support local `.md` and `.txt` files.
- Convert a supported file into a `SourceDocument`.
- Convert a directory into sorted `SourceDocument` values, ignoring unsupported files.
- Preserve source metadata needed for later citation work:
  - `source_path`
  - `file_name`
  - `file_type`
- Split text into `DocumentChunk` values with configurable `chunk_size` and `overlap`.
- Preserve source metadata on chunks and add:
  - `chunk_index`
  - `start`
  - `end`
- Keep output deterministic: stable file ordering and stable document/chunk IDs.
- Keep the whole task offline: no network, no real LLM provider, no vector database.

## Learning Goals

- Understand the difference between ingestion and chunking.
- Understand why RAG systems do not send whole documents directly to the model.
- Understand the trade-off between `chunk_size` and `overlap`.
- Understand how metadata enables future citation-aware answers.
- Learn how to verify text-processing behavior with deterministic pytest cases.

## Concepts

- `SourceDocument`
- `DocumentChunk`
- Markdown/TXT ingestion
- deterministic IDs
- chunk size
- overlap
- source metadata
- local/offline test fixtures

## Why Now

The FastAPI skeleton, settings, fake LLM provider, and RAG module boundaries
already exist. Before adding embeddings, vector storage, retrieval, generation,
or eval, the project needs a reliable way to get local knowledge into a stable
internal representation.

This task must come before UI, Agent Loop, LangGraph, MCP, and multi-agent
product behavior because those layers depend on the quality and traceability of
the underlying context pipeline.

## Approach Options

**Option A: Character-window chunking with overlap** (Recommended)

- Why: Minimal, deterministic, dependency-free, and easy to test.
- Trade-off: Less semantically aware than paragraph or token-based chunking.

**Option B: Paragraph-first chunking**

- Why: More natural boundaries for Markdown prose.
- Trade-off: More branchy behavior and harder first-step tests.

**Option C: Tokenizer-based chunking**

- Why: Closer to production LLM context budgeting.
- Trade-off: Adds dependency and model/tokenizer assumptions too early.

## Acceptance Criteria

- [ ] `.md` and `.txt` files can be loaded into `SourceDocument`.
- [ ] Unsupported extensions are rejected for single-file ingestion.
- [ ] Directory ingestion returns only supported files in stable sorted order.
- [ ] `chunk_text` validates `chunk_size` and `overlap`.
- [ ] Empty or whitespace-only text produces no chunks.
- [ ] Chunk IDs and metadata are stable.
- [ ] `load_text_file -> chunk_document` works in an offline test.
- [ ] `uv run pytest` passes.

## Definition of Done

- Tests added for ingestion, chunking, and the integrated local pipeline.
- README and technical notes reflect that Markdown/TXT ingestion and chunking
  now have a minimal implementation.
- `learning.md` records the concept, design choice, verification, and next
  learning step.
- Trellis spec updates are applied where the task establishes reusable
  implementation conventions.

## Technical Approach

- Add `agentic_rag_lab.ingestion.text` with `load_text_file` and `load_directory`.
- Add `agentic_rag_lab.chunking.text` with `chunk_text`, `chunk_document`, and
  `chunk_documents`.
- Reuse existing `SourceDocument` and `DocumentChunk`; do not introduce new
  schemas unless implementation proves it is necessary.
- Export public helpers from the package `__init__.py` files.

## Decision (ADR-lite)

**Context**: The project needs the first real RAG data step, but introducing
PDF parsing, embeddings, storage, or tokenizer dependencies would obscure the
learning objective.

**Decision**: Use UTF-8 local file loading plus character-window chunking with
overlap.

**Consequences**: The first implementation is simple and deterministic. It may
need a future paragraph-aware or tokenizer-aware chunker, but it gives later
embedding and retrieval tasks a stable contract immediately.

## Out of Scope

- PDF parsing.
- API upload endpoint.
- Embeddings.
- Vector database or retrieval store.
- Rerank.
- Citation-aware answer generation.
- Eval reports.
- Real LLM provider.
- Web UI.
- LangGraph.
- MCP.

## Out of Scope for Learning

- Production-grade document parsing.
- Token budgeting by model tokenizer.
- Semantic chunking quality evaluation.
- Multi-agent product workflows.
- External tool integration.

## Technical Notes

- Relevant specs:
  - `.trellis/spec/backend/index.md`
  - `.trellis/spec/backend/directory-structure.md`
  - `.trellis/spec/backend/quality-guidelines.md`
  - `.trellis/spec/backend/error-handling.md`
  - `.trellis/spec/guides/learning-mode-guide.md`
  - `.trellis/spec/guides/cross-layer-thinking-guide.md`
- Relevant code:
  - `src/agentic_rag_lab/schemas.py`
  - `src/agentic_rag_lab/ingestion/__init__.py`
  - `src/agentic_rag_lab/chunking/__init__.py`
- No external research needed for this MVP.
