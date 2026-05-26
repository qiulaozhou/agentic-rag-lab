# agentic-rag-lab

展示文档解析、检索、rerank、引用、评估。

## Current scope

This repository is the first project in the local AI Agent portfolio plan. The
current milestone is a runnable FastAPI skeleton, not a full RAG system yet.

Implemented in this skeleton:

- FastAPI application entry point.
- `/health` smoke endpoint that works without model credentials.
- Environment-based settings with a committed `.env.example`.
- Minimal LLM provider boundary with an offline `fake` provider.
- Explicit module boundaries for ingestion, chunking, retrieval, generation,
  and eval.
- Basic pytest smoke test.

Not implemented yet:

- Markdown/TXT/PDF ingestion.
- Chunking logic.
- Embeddings and vector storage.
- Citation-aware answer generation.
- RAG evaluation reports.

## Local setup

Prerequisites:

- Python 3.12+
- `uv`

Install dependencies:

```powershell
uv sync
```

Create local configuration:

```powershell
Copy-Item .env.example .env
```

`.env` is ignored by git. Put real provider credentials there only after a
future task adds a real model adapter.

Run the API:

```powershell
uv run uvicorn agentic_rag_lab.main:app --reload
```

Smoke check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Run tests:

```powershell
uv run pytest
```

## Project layout

```text
src/agentic_rag_lab/
├── api/          # FastAPI routers
├── chunking/     # document chunking boundary
├── evals/        # evaluation boundary
├── generation/   # answer generation boundary
├── ingestion/    # document ingestion boundary
├── llm/          # provider interface and fake provider
├── retrieval/    # search/retrieval boundary
├── config.py     # environment settings
├── main.py       # FastAPI app factory and app object
└── schemas.py    # shared domain data shapes
```

## Next tasks

Suggested Trellis tasks after this skeleton:

1. Add Markdown/TXT ingestion and chunking.
2. Add local embedding and vector store adapter.
3. Add citation-aware answer generation with refusal behavior.
4. Add `evals/tasks.jsonl`, `evals/run_eval.py`, and `evals/report.md`.

## Trellis workflow

这个仓库已经初始化 Trellis，用来实践轻量 harness 工作流。

主要入口：

- `AGENTS.md`：给 Codex/Cursor 的项目级指引。
- `.trellis/workflow.md`：Trellis 阶段、任务和上下文规则。
- `.trellis/tasks/`：当前任务和任务上下文。
- `.trellis/spec/`：项目/分层规范。
- `.trellis/workspace/`：本地工作日志和索引。

当前第一个真实任务：

```powershell
$py = 'C:\Users\admin\AppData\Roaming\uv\python\cpython-3.12.12-windows-x86_64-none\python.exe'
& $py .\.trellis\scripts\task.py start .\.trellis\tasks\05-25-bootstrap-rag-mvp-skeleton
& $py .\.trellis\scripts\task.py current --source
```

常用命令：

```powershell
# 查看任务列表
& $py .\.trellis\scripts\task.py list

# 创建新任务
& $py .\.trellis\scripts\task.py create "Add Markdown TXT ingestion" --slug add-markdown-txt-ingestion --assignee zrf --priority P1

# 当前任务完成后清除 active 指针
& $py .\.trellis\scripts\task.py finish
```

在 Codex 里使用时，可以直接这样说：

```text
请按 Trellis 当前任务推进：先读 AGENTS.md、.trellis/workflow.md 和当前 task 的 prd.md，然后给出实现计划并执行。
```

如果要启用 Trellis 的 Codex hook，需要在用户级 `C:\Users\admin\.codex\config.toml` 打开：

```toml
[features]
hooks = true
```

然后在 Codex TUI 里运行一次 `/hooks`，批准 Trellis 的 `UserPromptSubmit` hook。
