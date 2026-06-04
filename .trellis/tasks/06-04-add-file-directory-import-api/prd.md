# Add File And Directory Import API

## Goal

让 `agentic-rag-lab` 可以从本机 `.md` / `.txt` 文件路径或目录路径创建 disk-backed knowledge base：

```text
local .md/.txt path
-> load_text_file() / load_directory()
-> SourceDocument
-> DiskBackedKnowledgeBaseRegistry
-> local JSON knowledge base
-> answer
```

本任务先做本机 path 导入，不做浏览器 multipart upload，不接真实 embedding provider，不接真实 LLM，也不需要 API key。

## Requirements

- 在现有 knowledge base HTTP 边界新增：
  - `POST /knowledge-bases/from-file`
  - `POST /knowledge-bases/from-directory`
- `from-file` 接收：
  - `path`
  - `chunk_size`
  - `overlap`
- `from-directory` 接收：
  - `path`
  - `chunk_size`
  - `overlap`
  - 可选 `extensions`
- 内部复用已有：
  - `load_text_file()`
  - `load_directory()`
  - `DiskBackedKnowledgeBaseRegistry.create()`
- 返回继续使用 `CreateKnowledgeBaseResponse`。
- 现有 `POST /knowledge-bases` 继续保留。

## Learning Goals

- 理解直接传 documents 和从文件/目录导入的工程边界差异。
- 理解 ingestion metadata 如何进入 citation。
- 理解为什么先做本机 path 导入，而不是直接做 multipart upload。
- 理解如何把文件导入接到 disk-backed knowledge base。
- 继续用中文学习文档说明本步做了什么、作用、工具、输入输出、整体定位、验证和下一步。

## Concepts

- file path import
- directory import
- ingestion boundary reuse
- source metadata preservation
- disk-backed knowledge base creation
- API input validation

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
- disk-backed local knowledge base。

现在知识库能保存和恢复，但创建知识库时仍然需要调用方手写 `documents`。下一步自然是让已有 Markdown/TXT 文件和目录进入知识库。

## Approach Options

**Option A: 本机 path 导入（本次采用）**

- 优点：无新依赖、复用已有 ingestion、测试稳定。
- 代价：调用方必须传服务端可访问的本机路径。

**Option B: multipart upload**

- 优点：更接近浏览器上传体验。
- 代价：需要 `python-multipart`、上传大小限制、文件名安全策略和临时文件生命周期，当前过早。

**Option C: 目录 watch / 自动索引**

- 优点：更像长期知识库。
- 代价：需要后台任务和变更检测，不适合当前最小闭环。

## Acceptance Criteria

- [ ] `POST /knowledge-bases/from-file` 可以从 `.md` 创建知识库。
- [ ] 创建后 answer 返回 `refused=false` 和真实 `source_path#chunk-0`。
- [ ] app recreate 后旧 `knowledge_base_id` 仍可 answer。
- [ ] 文件不存在返回 `400`。
- [ ] 不支持扩展名返回 `400`。
- [ ] `POST /knowledge-bases/from-directory` 可以递归导入 `.md/.txt`。
- [ ] directory import 忽略不支持扩展名。
- [ ] 空目录允许创建空知识库，后续 answer 拒答。
- [ ] invalid `chunk_size/overlap` 返回 `400`。
- [ ] 现有 `POST /knowledge-bases`、`POST /knowledge-bases/{id}/answer`、`POST /answer`、`/health` 继续通过。
- [ ] `uv run pytest` 通过，或环境级失败被记录到 `learning.md`。

## Definition of Done

- file/directory import endpoint 完成。
- API 测试完成。
- README、技术笔记、根目录学习笔记同步更新为中文。
- Trellis backend specs 记录 file/directory import API 约定。
- 本任务 `learning.md` 记录概念、设计选择、验证结果和下一步。

## Technical Approach

- 新增 Pydantic DTO：
  - `CreateKnowledgeBaseFromFileRequest`
  - `CreateKnowledgeBaseFromDirectoryRequest`
- `from-file` 调用 `load_text_file(path)`，再调用 registry `create()`。
- `from-directory` 调用 `load_directory(path, extensions)`，再调用 registry `create()`。
- `FileNotFoundError`、`NotADirectoryError`、`ValueError` 和 `OSError` 转为 `400 Bad Request`。
- API 层不重新实现文件读取、chunking、embedding、retrieval、citation 或 refusal。

## Decision (ADR-lite)

**Context**：知识库已经可以持久化，但导入入口仍然需要手写 documents。

**Decision**：新增本机 file path / directory path 导入 endpoint。

**Consequences**：项目可以从真实 `.md` / `.txt` 文件构建可恢复知识库。后续如果需要浏览器上传，可以在这个边界之后单独扩展 multipart upload。

## Out of Scope

- multipart upload。
- PDF。
- Word。
- HTML。
- 真实 embedding provider。
- 真实 LLM。
- vector database。
- 知识库更新、删除、重命名。
- 目录 watch。
- Web UI。
- LangGraph。
- MCP。
- multi-agent orchestration。

## Out of Scope for Learning

- 上传安全策略。
- 文件大小限制。
- 临时文件清理。
- 后台索引任务。
- 目录增量同步。
- 权限沙箱设计。

## Technical Notes

- Relevant specs:
  - `.trellis/spec/backend/directory-structure.md`
  - `.trellis/spec/backend/quality-guidelines.md`
  - `.trellis/spec/guides/learning-mode-guide.md`
- Relevant code:
  - `src/agentic_rag_lab/api/knowledge_base.py`
  - `src/agentic_rag_lab/ingestion/text.py`
  - `src/agentic_rag_lab/knowledge_base/disk.py`
