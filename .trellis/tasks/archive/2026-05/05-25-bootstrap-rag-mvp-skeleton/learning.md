# Learning Notes

## Concepts

本任务练习的是 Agentic RAG 项目的工程骨架，而不是完整 RAG 功能。

核心概念包括：

- FastAPI app factory：用 `create_app()` 创建应用，方便测试和后续依赖注入。
- Environment settings：用 `.env` 和环境变量管理配置，不把 secrets 写进仓库。
- Provider boundary：用 `LLMProvider` protocol 隔离模型调用，避免业务逻辑绑定某个具体 SDK。
- Offline fake provider：用 deterministic fake provider 保证本地 smoke test 不依赖真实模型凭证。
- RAG module boundaries：先分出 ingestion、chunking、retrieval、generation、evals，为后续小任务留清晰边界。
- Smoke test：先验证服务能启动和基础 endpoint 可用，再继续堆功能。

## Why Now

`agentic-rag-lab` 是整个 AI Agent 学习路线的第一个项目。它要先解决“模型如何拿到可靠上下文”的问题。

当前阶段先做骨架是必要的，因为后面的文档导入、chunking、embedding、retrieval、citation、refusal、eval 都需要稳定的工程入口和模块边界。

这个任务应该排在这些事情之前：

- Web UI：现在还没有可展示的 RAG 能力。
- LangGraph：现在还没有复杂 Agent Loop。
- MCP：现在还没有工具生态要接。
- 多 agent：当前问题可以用单项目模块边界解决。
- 真实 LLM provider：smoke test 应该先离线可跑。

## Design Choice

本任务选择了最小可运行骨架：

```text
FastAPI app
-> /health
-> Settings
-> fake LLM provider boundary
-> RAG 模块目录
-> pytest smoke test
```

当时可选方案有三种：

1. 一次性实现完整 RAG。
2. 先搭完整框架和目录，但不验证运行。
3. 先做可运行骨架，再逐步补 ingestion/chunking/retrieval。

当前选择第 3 种。原因是它能尽快得到一个可运行基线，同时不提前锁死 vector database、PDF parser、real model provider 等后续选型。

## What Changed

本任务已经完成：

- 新增 Python + FastAPI 项目结构。
- 新增 `/health` endpoint。
- 新增 `Settings` 配置读取。
- 新增 `.env.example`。
- 新增 `LLMRequest`、`LLMResponse`、`LLMProvider`。
- 新增 `FakeLLMProvider`。
- 新增 `SourceDocument`、`DocumentChunk`、`RetrievalResult`、`GeneratedAnswer`。
- 新增 ingestion、chunking、retrieval、generation、evals 模块边界。
- 新增 pytest smoke test。
- README 记录本地 setup、run、test 和下一步任务。

本任务没有实现：

- Markdown/TXT/PDF ingestion。
- Chunking logic。
- Embeddings。
- Vector store。
- Citation-aware generation。
- Refusal behavior。
- Eval report。

## How To Verify

运行命令：

```powershell
uv run pytest
```

当前验证结果：

```text
tests\test_health.py . [100%]
1 passed
```

这个验证只证明骨架和 `/health` smoke endpoint 可用。它不证明 RAG 功能已经存在。

## Trellis Feedback

这次任务暴露出两个流程点：

- 学习型任务需要在完成代码后补 `learning.md`，否则以后复习只能看 README 和代码，缺少“为什么这样做”的记录。
- 当前 task 的 `implement.jsonl` 和 `check.jsonl` 仍是 seed example。后续真正进入 Trellis Phase 2 时，应该在启动实现前把相关 spec 和 learning guide 加进去。

这属于学习流程习惯，不需要改代码规范，但后续任务要严格执行 `.trellis/spec/guides/learning-mode-guide.md`。

## Next Learning Step

下一步建议任务：

```text
Add Markdown/TXT ingestion and chunking
```

这个任务应该学习：

- ingestion 和 chunking 的区别。
- 为什么 RAG 需要把文档切成 chunk。
- chunk size 和 overlap 的权衡。
- metadata 如何支撑后续 citation。
- 如何用 deterministic pytest 验证文本处理逻辑。

下一步仍然不要做：

- PDF parsing。
- Vector database。
- Real LLM provider。
- LangGraph。
- MCP。
- Web UI。
