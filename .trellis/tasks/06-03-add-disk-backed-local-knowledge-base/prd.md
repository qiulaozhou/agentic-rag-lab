# Add Disk-Backed Local Knowledge Base

## Goal

把当前只在 FastAPI app 进程内保存的 local knowledge base，推进到本地磁盘 JSON 文件持久化：

```text
POST /knowledge-bases
-> SourceDocument
-> DocumentChunk
-> LocalAnswerPipeline
-> DiskBackedKnowledgeBaseRegistry
-> local JSON files

app restart / create_app()
-> load local JSON files
-> rebuild LocalAnswerPipeline
-> POST /knowledge-bases/{knowledge_base_id}/answer
-> GeneratedAnswer
```

本任务只做本地 JSON 文件持久化，不做 SQLite、Chroma、Qdrant、pgvector、真实 embedding、真实 LLM、文件上传、目录扫描、UI、MCP、LangGraph 或多 agent。

## Requirements

- 新增 `DiskBackedKnowledgeBaseRegistry`。
- 保留现有 `LocalKnowledgeBase` 数据结构。
- `DiskBackedKnowledgeBaseRegistry` 对外继续支持：
  - `create()`
  - `get()`
  - `list()`
- `create()` 创建知识库后写入本地 JSON 文件。
- registry 初始化时扫描 storage directory，加载已有 JSON，并重建 `LocalAnswerPipeline`。
- 不序列化 `pipeline` 对象，只保存 documents、chunks、chunk_size、overlap、id。
- 新增配置项 `knowledge_base_storage_path`。
- 默认 storage path 为 `.local/knowledge-bases`。
- 更新 `.env.example` 和 `.gitignore`。
- `create_app()` 默认使用 disk-backed registry。
- 测试使用 `tmp_path` 隔离磁盘数据。

## Learning Goals

- 理解进程内复用和磁盘持久化的区别。
- 理解哪些 RAG 数据可以序列化，哪些运行时对象需要重建。
- 理解为什么先做 JSON 文件持久化，而不是直接接数据库或 vector store。
- 理解如何通过配置和测试隔离本地运行数据。
- 继续用中文学习文档说明本步做了什么、作用、工具、输入输出、整体定位、验证和下一步。

## Concepts

- disk-backed persistence
- JSON serialization
- app restart recovery
- registry lifecycle
- atomic file replace
- runtime object rebuild

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
- persistent local knowledge base。

当前 knowledge base 能跨 HTTP 请求复用，但服务重启后会丢失。现在做 disk-backed local knowledge base，能让项目更接近真正的本地知识库系统，同时仍保持离线、确定性和无新依赖。

## Approach Options

**Option A: JSON 文件持久化（本次采用）**

- 优点：无新依赖、易观察、易测试，适合学习持久化边界。
- 代价：不是生产级数据库，不适合高并发或复杂查询。

**Option B: SQLite**

- 优点：更接近可用存储。
- 代价：需要表结构、迁移和查询设计，当前过早。

**Option C: Chroma / Qdrant / pgvector**

- 优点：更接近生产向量库。
- 代价：会引入外部依赖和部署复杂度，当前会遮住知识库生命周期学习重点。

## Acceptance Criteria

- [ ] `POST /knowledge-bases` 创建成功后生成 `<knowledge_base_id>.json`。
- [ ] 新 app 使用同一个 storage path 启动后能加载旧知识库。
- [ ] 加载后的知识库可以继续 answer，并保留 citation。
- [ ] 空 documents 知识库可以保存和恢复。
- [ ] 已存在 `kb-1.json` 时，下一次 create 生成 `kb-2`。
- [ ] unknown id 仍返回 `404`。
- [ ] `limit <= 0` 仍返回 `400`。
- [ ] 损坏 JSON 文件初始化时抛 `ValueError`。
- [ ] 现有 `POST /answer` 和 `/health` 继续通过。
- [ ] `uv run pytest` 通过，或环境级失败被记录到 `learning.md`。

## Definition of Done

- disk-backed registry 代码完成。
- 配置和 app 初始化完成。
- 单元测试和 API 测试完成。
- README、技术笔记、根目录学习笔记同步更新为中文。
- Trellis backend specs 记录 disk-backed knowledge base 约定。
- 本任务 `learning.md` 记录概念、设计选择、验证结果和下一步。

## Technical Approach

- 每个知识库一个 JSON 文件：`<knowledge_base_id>.json`。
- JSON 保存：
  - `id`
  - `documents`
  - `chunks`
  - `chunk_size`
  - `overlap`
- 写入时先写临时文件，再替换目标文件。
- 加载时把 JSON 转回 `SourceDocument` 和 `DocumentChunk`。
- 加载后用 `LocalAnswerPipeline.from_chunks(chunks)` 重建 pipeline。
- 初始化时根据已有 `kb-N.json` 计算下一个 id。

## Decision (ADR-lite)

**Context**：进程内 knowledge base 已经能跨请求复用，但重启后丢失。

**Decision**：新增 JSON 文件持久化 registry，并让 `create_app()` 默认使用它。

**Consequences**：项目具备本地重启恢复能力，但仍不是生产级存储。后续可在同一 registry 边界后替换 SQLite 或 vector database。

## Out of Scope

- SQLite。
- vector database。
- 文件上传。
- 目录扫描 API。
- 知识库更新、删除、重命名。
- 知识库列表 HTTP API。
- real provider。
- streaming。
- auth。
- Web UI。
- LangGraph。
- MCP。
- multi-agent orchestration。

## Out of Scope for Learning

- 数据迁移。
- 并发写入锁。
- 损坏文件修复。
- 多租户隔离。
- 生产级容量限制。
- 分布式部署。

## Technical Notes

- Relevant specs:
  - `.trellis/spec/backend/directory-structure.md`
  - `.trellis/spec/backend/quality-guidelines.md`
  - `.trellis/spec/guides/learning-mode-guide.md`
- Relevant code:
  - `src/agentic_rag_lab/knowledge_base/local.py`
  - `src/agentic_rag_lab/api/knowledge_base.py`
  - `src/agentic_rag_lab/config.py`
  - `src/agentic_rag_lab/main.py`
