# Error Handling

> Error handling conventions for the current FastAPI skeleton.

---

## Current State

The skeleton currently exposes only `/health`, which returns a deterministic
success response and does not require custom error handling.

---

## Error Handling Patterns

- Let FastAPI handle framework-level validation and unexpected errors until a
  task introduces a real API contract that needs a stable error shape.
- Raise explicit exceptions at provider/adaptor boundaries when configuration
  is unsupported, as in `create_llm_provider`.
- Raise explicit `ValueError` for unsupported text ingestion extensions and
  invalid chunking parameters.
- Let `FileNotFoundError` and `NotADirectoryError` surface from filesystem
  ingestion helpers instead of returning empty successful results.
- Do not hide provider or retrieval failures inside fake successful RAG
  responses.
- Do not hide file-reading or chunk-parameter failures behind empty document or
  chunk lists. Empty lists should mean there was valid input with no supported
  content, not that an error was swallowed.

---

## API Error Responses

No project-wide API error response schema has been chosen yet. Define one only
when the first non-health API endpoint is added.

---

## Common Mistakes

- Returning successful placeholder answers when evidence is missing.
- Catching broad exceptions in API routes before there is a clear user-facing
  error contract.
- Treating unsupported files as successfully ingested documents.
- Allowing `overlap >= chunk_size`, which can create non-progressing chunk
  loops.
