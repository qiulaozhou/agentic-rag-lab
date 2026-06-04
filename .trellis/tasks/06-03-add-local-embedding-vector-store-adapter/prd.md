# Add Local Embedding And Vector Store Adapter

## Goal

Implement the next local RAG pipeline slice:

```text
DocumentChunk
-> local embedding vector
-> in-memory vector store
-> query embedding
-> top-k RetrievalResult
-> pytest verification
```

This task turns the existing retrieval boundary from a placeholder into a
deterministic, offline, test-covered adapter that can rank chunks before the
project adds generation, citation-aware answers, or eval reports.

## Requirements

- Add an `agentic_rag_lab.embeddings` package.
- Add an `EmbeddingProvider` protocol.
- Add a deterministic `LocalHashEmbeddingProvider`.
- Use `hashlib.sha256` plus token bag-of-words.
- Default embedding dimension is `32`.
- Validate embedding dimension is greater than `0`.
- Lowercase text before tokenization.
- Tokenize alphanumeric and underscore terms with a regex.
- Return an all-zero vector for empty text or text without tokens.
- L2-normalize non-empty vectors.
- Add an in-memory vector retrieval adapter under `agentic_rag_lab.retrieval`.
- Reuse existing `DocumentChunk` and `RetrievalResult`.
- Return search results sorted by cosine score descending.
- Preserve stable ordering for equal scores.
- Return only positive-score matches.
- Return no results for empty query or zero-vector query.
- Raise `ValueError` when `limit <= 0`.
- Keep the task offline: no network, real embedding provider, vector database,
  real LLM provider, or API endpoint.

## Learning Goals

- Understand what an embedding vector is in a RAG system.
- Understand why chunk text must become vectors before vector retrieval.
- Understand how query embeddings and chunk embeddings can be compared.
- Understand what a vector store adapter is responsible for.
- Learn how deterministic local embeddings can test retrieval behavior before
  production model or database choices.

## Concepts

- `DocumentChunk`
- `EmbeddingProvider`
- deterministic local embedding
- bag-of-words vectorization
- L2 normalization
- cosine similarity
- in-memory vector store
- `RetrievalResult`

## Why Now

The project already has local Markdown/TXT ingestion and deterministic
chunking. The next missing step is to turn `DocumentChunk.text` into a form
that can be searched by query similarity.

This task comes before answer generation, citation-aware generation, refusal
behavior, eval reports, UI, Agent Loop, LangGraph, MCP, and multi-agent
behavior because those layers need a trustworthy retrieval boundary first.

## Approach Options

**Option A: Deterministic local hash embedding** (Recommended)

- Why: dependency-free, offline, stable, and easy to test.
- Trade-off: not semantically rich like a real embedding model.

**Option B: Real embedding provider**

- Why: closer to production retrieval quality.
- Trade-off: introduces credentials, network access, provider SDK choices, and
  cost before the adapter contract is clear.

**Option C: Production vector database**

- Why: closer to later storage needs.
- Trade-off: adds infrastructure and persistence choices too early.

## Acceptance Criteria

- [ ] Same text produces the same embedding vector.
- [ ] Case-insensitive token handling is verified.
- [ ] Empty text returns an all-zero vector.
- [ ] Non-empty vectors have the configured dimension and are normalized.
- [ ] Invalid dimension raises `ValueError`.
- [ ] Vector search returns the most relevant chunk first for shared tokens.
- [ ] `limit` is respected.
- [ ] `DocumentChunk` metadata and `document_id` are preserved in results.
- [ ] Empty query returns no results.
- [ ] `limit <= 0` raises `ValueError`.
- [ ] `load_text_file -> chunk_document -> vector store -> search` works in an
  offline pytest case.
- [ ] `uv run pytest` passes or any environment-level failure is recorded in
  `learning.md`.

## Definition of Done

- Tests cover embedding behavior, vector retrieval behavior, and the integrated
  local pipeline.
- README and technical notes describe the new current state.
- Root `AI_AGENT_PORTFOLIO_NOTES.md` reflects that the project has advanced
  past chunking into local embedding/vector retrieval.
- `learning.md` records the concept, design choice, verification, and next
  learning step.
- Reusable backend spec updates are applied.

## Technical Approach

- Add `src/agentic_rag_lab/embeddings/base.py`.
- Add `src/agentic_rag_lab/embeddings/local.py`.
- Export embedding helpers from `src/agentic_rag_lab/embeddings/__init__.py`.
- Add `src/agentic_rag_lab/retrieval/vector.py`.
- Export `InMemoryVectorStore` from `src/agentic_rag_lab/retrieval/__init__.py`.
- Keep retrieval behavior internal; do not add API routes.

## Decision (ADR-lite)

**Context**: The project needs retrieval behavior, but production embedding
providers and vector databases would make this learning step too large.

**Decision**: Use a deterministic local hash embedding and in-memory vector
store as the first retrieval adapter.

**Consequences**: Retrieval quality is not production-grade, but the project
gets a stable, inspectable contract for embedding and ranked chunk retrieval.
Future tasks can swap in a real provider or database behind the same boundary.

## Out of Scope

- PDF parsing.
- Real embedding provider.
- OpenAI, Azure OpenAI, or local model SDKs.
- Chroma, Qdrant, pgvector, or another production vector database.
- API routes.
- Rerank.
- Citation-aware answer generation.
- Refusal behavior.
- Eval reports.
- Web UI.
- LangGraph.
- MCP.
- Multi-agent workflows.

## Out of Scope for Learning

- Production semantic retrieval quality.
- Vector database operations and persistence.
- Provider cost/latency evaluation.
- Hybrid search.
- Rerank models.
- Answer generation quality.

## Technical Notes

- Relevant specs:
  - `.trellis/spec/backend/directory-structure.md`
  - `.trellis/spec/backend/quality-guidelines.md`
  - `.trellis/spec/guides/learning-mode-guide.md`
- Relevant code:
  - `src/agentic_rag_lab/schemas.py`
  - `src/agentic_rag_lab/chunking/text.py`
  - `src/agentic_rag_lab/retrieval/__init__.py`
- No external research or dependency installation is needed for this MVP.
