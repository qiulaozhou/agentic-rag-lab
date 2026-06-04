# Add HTTP Answer API Boundary

## Goal

把已经完成的内部 `LocalAnswerPipeline.answer()` 暴露成最小 HTTP answer endpoint：

```text
POST /answer
-> AnswerRequest
-> SourceDocument
-> LocalAnswerPipeline.from_documents()
-> LocalAnswerPipeline.answer()
-> GeneratedAnswer
-> AnswerResponse
-> pytest
```

本任务只做 HTTP 边界，不做 UI、真实 LLM、真实 embedding provider、向量数据库或持久化知识库。

## Requirements

- 新增 `src/agentic_rag_lab/api/answer.py`。
- 新增 `POST /answer`。
- 新增 API DTO：
  - `AnswerDocument`
  - `AnswerRequest`
  - `AnswerResponse`
- 在 `main.py` 注册 answer router。
- endpoint 内部只调用 `LocalAnswerPipeline.from_documents()` 和 `LocalAnswerPipeline.answer()`。
- API 层不重新实现 chunking、embedding、retrieval、citation、refusal 或 eval。
- `ValueError` 转换为 `400 Bad Request`。
- 不改变现有 domain dataclass。

## Learning Goals

- 理解内部 pipeline 和 HTTP API boundary 的区别。
- 理解为什么要在内部 RAG 闭环稳定且有 eval 保护后再暴露 HTTP endpoint。
- 理解 API DTO 和 domain schema 的边界。
- 理解如何用 FastAPI `TestClient` 验证最小 HTTP 闭环。
- 继续练习中文详细学习记录：做了什么、作用、工具、输入输出、流程定位、验证和下一步。

## Concepts

- HTTP API boundary
- FastAPI router
- request/response DTO
- domain schema separation
- internal pipeline reuse
- API validation

## Why Now

项目已经完成：

- ingestion。
- chunking。
- embedding。
- retrieval。
- citation-aware generation。
- answer pipeline。
- refusal behavior。
- eval dataset / eval report。

现在内部 RAG 闭环已经可运行、可拒答、可评估。下一步自然是提供一个最小 HTTP 出口，让外部调用方可以通过 API 访问 answer pipeline。

## Approach Options

**Option A: 每次请求直接携带 documents**（本次采用）

- 优点：最小、无持久化、无新依赖，能证明 HTTP 边界。
- 代价：不是长期知识库 API。

**Option B: 文件上传或目录导入 API**

- 优点：更接近真实使用。
- 代价：需要文件上传、权限、路径和持久化设计，当前过早。

**Option C: 持久化知识库 / index**

- 优点：更像产品。
- 代价：需要存储、索引生命周期和更新策略，不适合当前最小任务。

## Acceptance Criteria

- [ ] `POST /answer` 高相关问题返回 `200`、`refused=false`、citation 命中。
- [ ] metadata 能从 request document 进入最终 citation。
- [ ] 空 question 返回 `200`、`refused=true`、citations 为空。
- [ ] 无关问题返回 `200`、`refused=true`、citations 为空。
- [ ] `documents=[]` 返回 `200`、`refused=true`。
- [ ] `limit <= 0` 返回 `400`。
- [ ] `chunk_size <= 0` 返回 `400`。
- [ ] `overlap >= chunk_size` 返回 `400`。
- [ ] `/health` 仍通过。
- [ ] `uv run pytest` 通过，或环境级失败被记录到 `learning.md`。

## Definition of Done

- answer router 代码和注册完成。
- API 测试完成。
- README、技术笔记、根目录学习笔记同步更新为中文。
- Trellis backend specs 记录 reusable HTTP answer API 约定。
- 本任务 `learning.md` 记录概念、设计选择、验证结果和下一步。

## Technical Approach

- `AnswerDocument` 使用 Pydantic model，字段为 `id`、`text`、`metadata`。
- `AnswerRequest` 使用 Pydantic model，字段为 `question`、`documents`、`chunk_size`、`overlap`、`limit`。
- `AnswerResponse` 使用 Pydantic model，字段为 `text`、`citations`、`refused`。
- endpoint 把 `AnswerDocument` 转成 `SourceDocument`。
- endpoint 用 `LocalAnswerPipeline.from_documents()` 创建 pipeline。
- endpoint 用 `await pipeline.answer(question, limit=limit)` 获取 `GeneratedAnswer`。
- `ValueError` 转为 `HTTPException(status_code=400)`。

## Decision (ADR-lite)

**Context**：内部 RAG 闭环已经具备 eval 保护，但还没有外部调用入口。

**Decision**：新增最小 `POST /answer`，请求内直接携带 documents。

**Consequences**：项目成为可通过 HTTP 调用的最小 RAG 服务。后续如果做持久化知识库，可以在这个 API 边界之后扩展，而不影响当前内部 pipeline。

## Out of Scope

- 文件上传。
- 目录读取。
- 持久化知识库。
- vector database。
- real provider。
- streaming。
- auth。
- Web UI。
- LangGraph。
- MCP。
- multi-agent orchestration。

## Out of Scope for Learning

- API versioning。
- 生产级错误码体系。
- 安全认证。
- 线上部署。
- OpenAPI 文档优化。
- 前端集成。

## Technical Notes

- Relevant specs:
  - `.trellis/spec/backend/directory-structure.md`
  - `.trellis/spec/backend/quality-guidelines.md`
  - `.trellis/spec/guides/learning-mode-guide.md`
- Relevant code:
  - `src/agentic_rag_lab/main.py`
  - `src/agentic_rag_lab/api/health.py`
  - `src/agentic_rag_lab/generation/pipeline.py`
