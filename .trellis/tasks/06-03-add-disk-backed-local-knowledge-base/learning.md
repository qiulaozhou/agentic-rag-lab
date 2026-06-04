# 学习记录

更新日期：2026-06-03

## 本步一句话总结

这一步把 `agentic-rag-lab` 的知识库从“只在 FastAPI app 进程内存在”推进到“保存到本地 JSON 文件，并在 app 启动时恢复”的磁盘可恢复闭环。

## 本步做了什么

本次新增了 disk-backed local knowledge base：

```text
POST /knowledge-bases
-> SourceDocument
-> DocumentChunk
-> LocalAnswerPipeline
-> DiskBackedKnowledgeBaseRegistry
-> .local/knowledge-bases/kb-1.json

create_app()
-> load .local/knowledge-bases/*.json
-> rebuild LocalAnswerPipeline
-> POST /knowledge-bases/{knowledge_base_id}/answer
-> GeneratedAnswer
```

新增能力：

- `agentic_rag_lab.knowledge_base.DiskBackedKnowledgeBaseRegistry`
- `src/agentic_rag_lab/knowledge_base/disk.py`
- `Settings.knowledge_base_storage_path`
- `.env.example` 中的 `KNOWLEDGE_BASE_STORAGE_PATH`
- `.gitignore` 忽略 `.local/`
- `create_app()` 默认使用 disk-backed registry
- disk-backed registry 单元测试
- app recreate 后继续 answer 的 API 测试

## 作用是什么

前一步的 persistent local knowledge base 只是在 app 进程内保存知识库。它能跨 HTTP 请求复用，但服务重启后会丢失。

本步的作用是让知识库具备最小本地恢复能力：

- 创建知识库后写入 JSON 文件。
- app 重新创建时读取 JSON 文件。
- 根据保存的 documents/chunks 重建 `LocalAnswerPipeline`。
- 继续用原 `knowledge_base_id` 提问。

这让项目从“进程内 demo”更接近“本地知识库系统”。

## 用什么实现

本次使用的已有模块：

- `SourceDocument`
- `DocumentChunk`
- `LocalKnowledgeBase`
- `LocalAnswerPipeline`
- `chunk_documents()`
- `GeneratedAnswer`

本次新增或调整：

- `DiskBackedKnowledgeBaseRegistry`
- `Path`
- `json`
- `Path.replace()` 原子替换目标文件
- `Settings.knowledge_base_storage_path`
- `FastAPI create_app(settings=...)`
- `tmp_path` 测试隔离

## 输入输出是什么

创建知识库输入仍然不变：

```json
{
  "documents": [
    {
      "id": "doc-1",
      "text": "RAG answers need citations so users can inspect sources.",
      "metadata": {
        "source_path": "docs/rag.md",
        "file_type": ".md"
      }
    }
  ],
  "chunk_size": 400,
  "overlap": 0
}
```

HTTP 输出仍然不变：

```json
{
  "knowledge_base_id": "kb-1",
  "document_count": 1,
  "chunk_count": 1
}
```

新增磁盘输出：

```text
.local/knowledge-bases/kb-1.json
```

JSON 内容保存：

```json
{
  "id": "kb-1",
  "documents": [],
  "chunks": [],
  "chunk_size": 400,
  "overlap": 0
}
```

实际非空知识库会保存 documents 和 chunks，启动恢复时用 chunks 重建 answer pipeline。

## 在整体 RAG 链路中的定位

当前项目整体链路已经推进到：

```text
ingestion
-> chunking
-> embedding
-> retrieval
-> citation-aware generation
-> answer pipeline
-> refusal behavior
-> eval dataset / eval report
-> HTTP answer API boundary
-> persistent local knowledge base
-> disk-backed local knowledge base
```

这一步位于 knowledge base API 之后。它不改变 retrieval、citation、refusal 或 eval，只补上知识库生命周期里的“重启恢复”能力。

## 为什么现在做

现在项目已经能：

- 创建知识库。
- 基于知识库 id 提问。
- 返回 citation。
- 在证据不足时拒答。
- 用 eval 和 pytest 验证。

但只要 app 重启，之前创建的知识库就会丢失。这个缺口比真实 LLM、真实 embedding 或 UI 更基础，所以现在先补磁盘恢复。

## 设计选择

本次选择 JSON 文件持久化。

原因：

- 不引入新依赖。
- 文件可直接打开检查。
- 测试可以用 `tmp_path` 隔离。
- 适合学习“什么能序列化，什么要重建”。

没有选择 SQLite 或 vector database，因为当前目标不是生产存储选型，而是把本地知识库生命周期跑通。

本次不序列化 `LocalAnswerPipeline`。它是运行时对象，保存到磁盘没有意义。磁盘只保存 documents、chunks 和 chunk 参数，启动时再重建 pipeline。

## 本次没有做什么

本任务没有做：

- SQLite。
- Chroma / Qdrant / pgvector。
- 文件上传。
- 目录扫描 API。
- 知识库更新、删除、重命名。
- 知识库列表 HTTP API。
- 真实 embedding provider。
- 真实 LLM。
- rerank。
- streaming。
- auth。
- Web UI。
- LangGraph。
- MCP。
- multi-agent orchestration。

## 如何验证

先运行普通命令：

```powershell
uv run pytest
```

普通权限下仍然因为本机 `uv` cache 权限失败：

```text
error: Failed to initialize cache at `C:\Users\admin\AppData\Local\uv\cache`
  Caused by: failed to open file `C:\Users\admin\AppData\Local\uv\cache\sdists-v9\.git`: 拒绝访问。 (os error 5)
```

随后用提升权限运行同一个命令，最终结果：

```text
98 passed
```

测试覆盖：

- 创建知识库后生成 JSON 文件。
- 使用同一个 storage path 重新初始化 registry 后能加载旧知识库。
- 加载后仍能 answer，并保留 citation。
- 空 documents 知识库能保存和恢复。
- 已存在 `kb-1.json` 时，下一次 create 生成 `kb-2`。
- unknown id 仍抛 `KeyError`。
- 损坏 JSON 文件初始化时抛 `ValueError`。
- app recreate 后通过旧 `knowledge_base_id` 继续 answer。
- 现有 `POST /knowledge-bases`、`POST /answer` 和 `/health` 继续通过。

## 学到什么

- 进程内复用不等于磁盘持久化。
- 运行时 pipeline 不应该直接保存到磁盘，应该保存可重建它的数据。
- 本地运行数据应该放进 `.local/`，并且必须被 git ignore。
- app factory 传入 settings 可以让测试使用 `tmp_path` 隔离运行数据。
- 损坏持久化数据不应该静默跳过，否则会让知识库状态难以定位。

## Trellis 反馈

本次继续符合学习型 Trellis 约束：

- 先创建任务目录和 PRD。
- PRD 明确 Learning Goals、Why Now、Approach Options、Out of Scope。
- 实现最小可运行闭环。
- 测试覆盖恢复、错误、空知识库和 API 行为。
- 学习记录用中文说明做了什么、作用、工具、输入输出、定位、验证和下一步。
- README、技术笔记、根目录学习文档和 backend specs 已同步更新。

## 下一步学习

下一步建议任务：

```text
file upload / directory import API
```

原因是当前知识库虽然能保存和恢复，但创建时仍然需要调用方在 JSON request body 里直接写 documents。下一步可以学习如何把本地 `.md` / `.txt` 文件导入到已经具备磁盘恢复能力的知识库中。

另一个可选方向是：

```text
real provider planning
```

但仍然不要直接跳到 UI、Workbench、MCP、LangGraph 或多 agent。
