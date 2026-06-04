# Add Persistent Local Knowledge Base

## Goal

把当前每次请求都携带 `documents` 的 `POST /answer` 模式，推进到一个可跨 HTTP 请求复用的本地知识库模式：

```text
POST /knowledge-bases
-> documents
-> SourceDocument
-> DocumentChunk
-> LocalAnswerPipeline
-> in-process knowledge base registry

POST /knowledge-bases/{knowledge_base_id}/answer
-> LocalAnswerPipeline.answer()
-> GeneratedAnswer
-> HTTP response
-> pytest
```

本任务里的 `persistent` 指 FastAPI app 进程内复用，不是磁盘持久化、SQLite、文件上传或生产级向量数据库。

## Requirements

- 新增 `agentic_rag_lab.knowledge_base` 包。
- 新增 `LocalKnowledgeBase`，保存：
  - `id`
  - `documents`
  - `chunks`
  - `chunk_size`
  - `overlap`
  - `LocalAnswerPipeline`
- 新增 `InMemoryKnowledgeBaseRegistry`，支持 create、get、list。
- 创建知识库时复用现有 `chunk_documents()` 和 `LocalAnswerPipeline.from_chunks()`。
- 新增 `src/agentic_rag_lab/api/knowledge_base.py`。
- 在 `main.py` 注册 knowledge base router。
- 用 `app.state.knowledge_bases` 保存 registry，保证 `create_app()` 每次调用都有独立 registry。
- 保留现有 `POST /answer`，不替换临时 documents 模式。

## Learning Goals

- 理解“每次请求带 documents”和“可复用知识库”的工程边界差异。
- 理解为什么先做进程内 registry，而不是直接上磁盘、数据库或 vector database。
- 理解知识库管理 API 和问答 API 的职责区别。
- 理解怎样复用已经完成的 chunking、retrieval、generation、refusal pipeline。
- 继续练习中文学习记录：做了什么、作用、工具、输入输出、整体定位、验证和下一步。

## Concepts

- in-process persistence
- knowledge base registry
- index lifecycle
- API state
- FastAPI app.state
- pipeline reuse

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
- HTTP answer API boundary。

现在 `/answer` 已经能通过 HTTP 调用 RAG 闭环，但每次请求都要重新携带 documents 并重建 pipeline。下一步自然是把一组 documents 变成可复用的本地知识库，让调用方可以先创建知识库，再基于知识库 id 多次提问。

## Approach Options

**Option A: 进程内 registry（本次采用）**

- 优点：最小、离线、无新依赖，能学习知识库生命周期和 API 状态边界。
- 代价：服务重启后知识库丢失。

**Option B: 磁盘持久化 JSON / SQLite**

- 优点：重启后能保留知识库。
- 代价：需要序列化、迁移、并发和索引恢复设计，当前过早。

**Option C: Chroma / Qdrant / pgvector**

- 优点：更接近生产。
- 代价：引入外部依赖和部署复杂度，会遮住当前要学习的 API 边界。

## Acceptance Criteria

- [ ] `POST /knowledge-bases` 可以创建知识库并返回 `knowledge_base_id`、`document_count`、`chunk_count`。
- [ ] `POST /knowledge-bases/{knowledge_base_id}/answer` 可以基于已创建知识库回答。
- [ ] 高相关问题返回 `refused=false`，citation 命中 `source_path#chunk-0`。
- [ ] 空 question 返回 `refused=true`、citations 为空。
- [ ] 无关问题返回 `refused=true`、citations 为空。
- [ ] 空 documents 可以创建知识库，后续提问拒答。
- [ ] unknown knowledge base id 返回 `404`。
- [ ] `limit <= 0` 返回 `400`。
- [ ] `chunk_size <= 0` 返回 `400`。
- [ ] `overlap < 0` 返回 `400`。
- [ ] `overlap >= chunk_size` 返回 `400`。
- [ ] 现有 `POST /answer` 和 `/health` 测试继续通过。
- [ ] `uv run pytest` 通过，或环境级失败被记录到 `learning.md`。

## Definition of Done

- 知识库 registry 代码完成。
- knowledge base HTTP router 完成并注册。
- 单元测试和 API 测试完成。
- README、技术笔记、根目录学习笔记同步更新为中文。
- Trellis backend specs 记录 reusable knowledge base API 约定。
- 本任务 `learning.md` 记录概念、设计选择、验证结果和下一步。

## Technical Approach

- `LocalKnowledgeBase` 使用 dataclass，负责保存 documents、chunks、chunk 参数和已经构建好的 `LocalAnswerPipeline`。
- `InMemoryKnowledgeBaseRegistry.create()` 负责：
  - 生成 `kb-...` id。
  - 调用 `chunk_documents()`。
  - 调用 `LocalAnswerPipeline.from_chunks()`。
  - 保存并返回 `LocalKnowledgeBase`。
- `InMemoryKnowledgeBaseRegistry.get()` 找不到时抛 `KeyError`。
- API 层把 request DTO 转成 `SourceDocument`，再调用 registry。
- API 层不重新实现 embedding、retrieval、citation、refusal 或 eval。

## Decision (ADR-lite)

**Context**：HTTP answer API 已经可用，但每次请求都携带 documents，不像长期知识库。

**Decision**：新增进程内 knowledge base registry 和两个最小 HTTP endpoint。

**Consequences**：项目可以跨请求复用同一组 documents 和 answer pipeline，但重启后数据会丢失。后续如果要磁盘持久化，可以在 registry 边界后扩展。

## Out of Scope

- 磁盘持久化。
- SQLite。
- 文件上传。
- 目录扫描 API。
- vector database。
- real provider。
- streaming。
- auth。
- Web UI。
- LangGraph。
- MCP。
- multi-agent orchestration。

## Out of Scope for Learning

- 索引版本管理。
- 知识库更新和删除。
- 多租户隔离。
- 并发写入锁。
- 生产级资源限制。
- OpenAPI 文档优化。

## Technical Notes

- Relevant specs:
  - `.trellis/spec/backend/directory-structure.md`
  - `.trellis/spec/backend/quality-guidelines.md`
  - `.trellis/spec/guides/learning-mode-guide.md`
- Relevant code:
  - `src/agentic_rag_lab/main.py`
  - `src/agentic_rag_lab/api/answer.py`
  - `src/agentic_rag_lab/generation/pipeline.py`
  - `src/agentic_rag_lab/chunking/text.py`
