# Learning Notes

## Concepts

This task exercised the first real RAG data pipeline boundary:

```text
local Markdown/TXT file -> SourceDocument -> DocumentChunk -> pytest
```

The key concept is that ingestion and chunking are separate responsibilities.
Ingestion turns external files into a stable internal source-document shape.
Chunking turns those source documents into smaller retrievable units that later
embedding and retrieval code can consume.

## Why Now

The project already had a FastAPI skeleton, settings, fake LLM provider, and
empty RAG subsystem boundaries. Before adding embeddings, vector storage,
retrieval, generation, eval, UI, LangGraph, or MCP, the project needed a
deterministic way to get local knowledge into the system.

This task is the smallest useful step after the skeleton because every later
RAG capability depends on stable source text, metadata, and chunk IDs.

## Design Choice

The implementation uses UTF-8 `.md` / `.txt` file ingestion plus
character-window chunking with overlap.

Options considered:

- Character-window chunking: chosen because it is deterministic,
  dependency-free, and easy to test.
- Paragraph-first chunking: deferred because it introduces more branchy
  behavior before the basic pipeline is proven.
- Tokenizer-based chunking: deferred because it introduces model/tokenizer
  assumptions too early.

The trade-off is that the current chunks are not semantically optimized, but
they are stable enough for the next embedding/retrieval task.

## What Changed

- Added `agentic_rag_lab.ingestion.text`.
- Added `load_text_file` and `load_directory`.
- Added `agentic_rag_lab.chunking.text`.
- Added `chunk_text`, `chunk_document`, and `chunk_documents`.
- Expanded metadata typing to allow numeric chunk offsets.
- Added pytest coverage for ingestion, chunking, and the integrated local
  pipeline.
- Updated README and technical notes to reflect the new current state.
- Updated Trellis backend specs and learning guide with reusable conventions.

## How To Verify

Command:

```powershell
uv run pytest
```

Result:

```text
20 passed
```

Check-worker note: running the same command under normal permissions on this
machine currently fails before pytest because `uv` cannot initialize its cache:

```text
error: Failed to initialize cache at `C:\Users\admin\AppData\Local\uv\cache`
  Caused by: failed to open file `C:\Users\admin\AppData\Local\uv\cache\sdists-v9\.git`: 拒绝访问。 (os error 5)
```

## Trellis Feedback

The learning workflow worked well for this task:

- The previous task's summary moved into long-term docs and spec only where it
  created reusable conventions.
- The new task kept a clear PRD with learning goals, why-now, approach options,
  and out-of-scope items.
- Using a worker for implementation and keeping Trellis/spec orchestration in
  the main session avoided conflicting writes.

Future Trellis tasks should keep this split:

- Main session: task lifecycle, PRD, spec updates, final verification.
- Worker/check agent: bounded code changes and focused review.

## Next Learning Step

Next recommended task:

```text
Add local embedding and vector store adapter
```

The next learning goal is to understand how `DocumentChunk` text becomes
embedding vectors and how a local retrieval adapter can return ranked chunks
without yet solving answer generation.
