# Build Basic Retrieval Pipeline API Boundary

## Goal

实现下一个最小 RAG 检索闭环：

```text
SourceDocument
-> DocumentChunk
-> InMemoryVectorStore
-> LocalRetrievalPipeline.search()
-> list[RetrievalResult]
-> pytest
```

这次任务不新增 HTTP endpoint，而是先做一个内部 retrieval pipeline / API boundary，让后续 answer generation 不需要直接关心 chunking、embedding 或 vector store 细节。

## Requirements

- 新增 `agentic_rag_lab.retrieval.pipeline`。
- 新增 `LocalRetrievalPipeline`。
- 支持从 `list[DocumentChunk]` 构建 pipeline。
- 支持从 `list[SourceDocument]` + `chunk_size` + `overlap` 构建 pipeline。
- 内部复用 `chunk_documents` 和 `InMemoryVectorStore`。
- `search(query, limit=5)` 返回 `list[RetrievalResult]`。
- 保留底层 vector store 的行为：
  - 空 query 返回空列表。
  - `limit <= 0` 抛 `ValueError`。
  - 结果按 score 降序。
  - `DocumentChunk` metadata 保留。
- 不新增 answer generation、citation generation、refusal、eval、UI、LangGraph、MCP 或多 agent 行为。

## Learning Goals

- 理解 retrieval pipeline 的职责。
- 理解为什么上层模块不应该直接拼 chunking 和 vector store 细节。
- 理解 retrieval API boundary 应该返回 `RetrievalResult`，而不是直接生成答案。
- 理解如何继续保留 metadata，给后续 citation 使用。
- 学会用测试验证 pipeline 组合行为，而不是只验证底层 adapter。

## Concepts

- retrieval pipeline
- API boundary
- `SourceDocument`
- `DocumentChunk`
- `RetrievalResult`
- composition over duplication
- metadata preservation

## Why Now

项目已经完成 Markdown/TXT ingestion、chunking、本地 embedding 和内存向量检索。现在底层 adapter 已经能工作，但调用方还需要自己知道怎么切分文档、怎么创建 vector store。

下一步应该把这些细节收进一个 pipeline 边界里，让后续 answer generation 只依赖 retrieval 结果，而不是依赖底层实现。

## Approach Options

**Option A: 内部 `LocalRetrievalPipeline`**（推荐）

- 优点：最小、离线、无新依赖，可以直接复用已有代码。
- 代价：还不是 HTTP API，也没有持久化。

**Option B: FastAPI retrieval endpoint**

- 优点：更像对外 API。
- 代价：需要设计请求/响应、错误处理和文档输入方式，当前过早。

**Option C: 直接在 generation 层调用 vector store**

- 优点：少写一个类。
- 代价：会让 generation 层知道太多 retrieval 细节，不利于后续替换 provider 或 store。

## Acceptance Criteria

- [ ] 可以从 `DocumentChunk` 列表构建 pipeline 并搜索。
- [ ] 可以从 `SourceDocument` 列表构建 pipeline，内部完成 chunking。
- [ ] `search()` 返回 `RetrievalResult`。
- [ ] `limit` 行为被验证。
- [ ] 空 query 行为被验证。
- [ ] `limit <= 0` 错误行为被验证。
- [ ] chunk metadata 在结果中保留。
- [ ] pipeline 测试不需要网络、真实 embedding provider 或 vector database。
- [ ] `uv run pytest` 通过，或环境级失败被记录到 `learning.md`。

## Definition of Done

- pipeline 代码和导出完成。
- 测试覆盖 pipeline 构建和搜索行为。
- README、技术笔记、根目录学习笔记同步更新为中文。
- Trellis backend specs 记录 reusable retrieval pipeline 约定。
- 本任务 `learning.md` 记录概念、设计选择、验证结果和下一步。

## Technical Approach

- 新增 `src/agentic_rag_lab/retrieval/pipeline.py`。
- `LocalRetrievalPipeline.from_chunks(chunks, embedding_provider=None)` 创建底层 `InMemoryVectorStore`。
- `LocalRetrievalPipeline.from_documents(documents, chunk_size, overlap=0, embedding_provider=None)` 先调用 `chunk_documents`，再创建 pipeline。
- `LocalRetrievalPipeline.search(query, limit=5)` 委托给底层 store。
- 从 `src/agentic_rag_lab/retrieval/__init__.py` 导出 `LocalRetrievalPipeline`。

## Decision (ADR-lite)

**Context**：底层 vector store 已经能返回相似 chunks，但上层模块还缺少稳定调用边界。

**Decision**：先新增内部 `LocalRetrievalPipeline`，不新增 HTTP endpoint。

**Consequences**：后续 generation 能依赖 pipeline，而不是直接依赖 chunking 和 vector store。未来如果需要 HTTP endpoint 或持久化 store，可以在这个边界后面替换实现。

## Out of Scope

- HTTP retrieval endpoint。
- 请求/响应 DTO。
- answer generation。
- citation-aware generation。
- refusal behavior。
- eval dataset / eval report。
- real embedding provider。
- production vector database。
- Web UI。
- LangGraph。
- MCP。
- multi-agent orchestration。

## Out of Scope for Learning

- API 版本设计。
- HTTP 错误码设计。
- 生产级检索质量评估。
- citation formatting。
- generation prompt design。

## Technical Notes

- Relevant specs:
  - `.trellis/spec/backend/directory-structure.md`
  - `.trellis/spec/backend/quality-guidelines.md`
  - `.trellis/spec/guides/learning-mode-guide.md`
- Relevant code:
  - `src/agentic_rag_lab/chunking/text.py`
  - `src/agentic_rag_lab/retrieval/vector.py`
  - `src/agentic_rag_lab/schemas.py`
