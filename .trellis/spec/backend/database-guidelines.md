# Database Guidelines

> Persistence and vector-store guidance for this project.

---

## Current State

The skeleton does not use a relational database, document store, embedding
store, or vector database yet.

---

## Decision Rule

Do not introduce a permanent storage technology as incidental work. A future
task that adds embeddings or retrieval must explicitly choose and document the
first storage adapter.

---

## Expected Adapter Boundary

Retrieval code should stay behind `agentic_rag_lab.retrieval.Retriever`.
Storage-specific clients should not leak into API route functions or answer
generation code.

---

## Common Mistakes

- Choosing Chroma, Qdrant, pgvector, or another store before the retrieval task
  defines the target local demo and deployment constraints.
- Mixing document ingestion, storage writes, retrieval, and generation in one
  module.
