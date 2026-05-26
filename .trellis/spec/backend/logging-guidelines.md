# Logging Guidelines

> Logging conventions for the current FastAPI skeleton.

---

## Current State

The skeleton exposes a `LOG_LEVEL` setting but does not configure application
logging yet.

---

## Log Levels

- Use `INFO` for lifecycle events and task-level progress once logging is
  introduced.
- Use `DEBUG` for local diagnostic details that are not useful in normal runs.
- Use `WARNING` for recoverable degraded behavior.
- Use `ERROR` for failed operations that block the requested action.

---

## What to Log

Future RAG tasks should log high-level pipeline events such as ingestion,
chunking, retrieval, generation, and eval runs. Include counts and timings when
available.

---

## What NOT to Log

Never log API keys, `.env` values, raw credentials, or full private documents.
When adding model calls later, do not log full prompts by default.
