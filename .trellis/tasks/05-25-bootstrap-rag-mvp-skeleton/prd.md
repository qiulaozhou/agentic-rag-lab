# Bootstrap Agentic RAG Lab MVP skeleton

## Background

`agentic-rag-lab` is the first project in the local AI Agent portfolio plan. Its purpose is to build a reliable RAG foundation before moving on to the developer agent workbench and MCP tooling projects.

This task should create the first runnable engineering skeleton, not a full RAG implementation. The skeleton must make the later document parsing, retrieval, rerank, citation, refusal, and eval work easy to add in small tasks.

## Goals

- Create a Python project structure suitable for a FastAPI service.
- Add configuration loading from `.env` with a committed `.env.example`.
- Define a minimal LLM provider boundary so model calls are isolated from app logic.
- Define explicit module boundaries for ingestion, chunking, retrieval, answer generation, and eval.
- Add a health endpoint or CLI smoke path that can run without real model credentials.
- Add a basic pytest structure.
- Update README with local setup, run, and test commands.

## Non-Goals

- Do not implement production PDF parsing in this task.
- Do not choose a permanent vector database yet.
- Do not require paid model credentials for the smoke test.
- Do not add a web UI yet.

## Acceptance Criteria

- `python -m pytest` can run at least one smoke test.
- The project has an obvious entry point for local development.
- The README explains how to configure credentials later without committing secrets.
- The code layout makes these next tasks straightforward:
  - Markdown/TXT ingestion.
  - Chunking with size and overlap settings.
  - Vector retrieval.
  - Citation-aware answering.
  - Evaluation report generation.

## Suggested Next Tasks

- Add Markdown/TXT ingestion and chunking.
- Add local embedding and vector store adapter.
- Add citation-aware answer generation with refusal behavior.
- Add `evals/tasks.jsonl`, `evals/run_eval.py`, and `evals/report.md`.
