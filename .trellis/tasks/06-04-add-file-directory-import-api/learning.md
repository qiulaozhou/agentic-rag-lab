# 学习记录

更新日期：2026-06-04

## 本步一句话总结

这一步把 `agentic-rag-lab` 从“创建知识库时需要手写 documents”推进到“可以通过本机 `.md/.txt` 文件路径或目录路径导入 disk-backed knowledge base”。

## 本步做了什么

本次新增了两个知识库导入 API：

```text
POST /knowledge-bases/from-file
-> load_text_file()
-> SourceDocument
-> DiskBackedKnowledgeBaseRegistry.create()
-> local JSON knowledge base

POST /knowledge-bases/from-directory
-> load_directory()
-> list[SourceDocument]
-> DiskBackedKnowledgeBaseRegistry.create()
-> local JSON knowledge base
```

新增能力：

- `CreateKnowledgeBaseFromFileRequest`
- `CreateKnowledgeBaseFromDirectoryRequest`
- `POST /knowledge-bases/from-file`
- `POST /knowledge-bases/from-directory`
- 文件导入 API 测试
- 目录导入 API 测试

## 作用是什么

前一步已经让知识库可以保存到磁盘并在 app 重启后恢复，但创建知识库时还需要调用方直接传 `documents`。

本步的作用是把已有 ingestion 能力接到 HTTP API：

- 本机 `.md` / `.txt` 文件可以直接变成知识库。
- 本机目录可以递归导入 `.md` / `.txt`。
- 导入时保留 `source_path`、`file_name`、`file_type`。
- 后续 answer 的 citation 可以继续追溯到真实文件路径。

这让项目更像一个知识库系统，而不是只能接收手写 JSON 的 API demo。

## 用什么实现

本次复用的已有模块：

- `load_text_file()`
- `load_directory()`
- `SourceDocument`
- `DiskBackedKnowledgeBaseRegistry`
- `CreateKnowledgeBaseResponse`

新增或调整：

- knowledge base router 新增两个 request DTO。
- API 层把文件/目录错误转成 `400 Bad Request`。
- 测试用 `tmp_path` 创建本地 `.md/.txt` 文件和目录。

## 输入输出是什么

文件导入输入：

```json
{
  "path": "D:/docs/rag.md",
  "chunk_size": 400,
  "overlap": 0
}
```

目录导入输入：

```json
{
  "path": "D:/docs",
  "chunk_size": 400,
  "overlap": 0,
  "extensions": [".md", ".txt"]
}
```

输出继续沿用：

```json
{
  "knowledge_base_id": "kb-1",
  "document_count": 2,
  "chunk_count": 2
}
```

后续提问输出仍然是：

```json
{
  "text": "基于检索到的资料，可以回答如下：...",
  "citations": ["D:/docs/rag.md#chunk-0"],
  "refused": false
}
```

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
-> file / directory import API
```

这一步发生在 ingestion 和 knowledge base 之间。它不改变 RAG 内部逻辑，只是让真实本地文件可以进入已有闭环。

## 为什么现在做

现在已经有：

- Markdown/TXT ingestion。
- disk-backed knowledge base。
- answer API。
- citation。
- refusal。
- eval。

所以现在补文件/目录导入是自然下一步。它把已有的 ingestion 和已有的知识库持久化连起来，让后续接真实 provider 前，数据入口更接近真实使用。

## 设计选择

本次选择本机 path 导入，而不是 multipart upload。

原因：

- 不新增依赖。
- 不引入上传安全和文件大小限制问题。
- 可以直接复用 `load_text_file()` 和 `load_directory()`。
- 测试完全离线稳定。

真正浏览器上传要等后续单独设计，包括 `python-multipart`、临时文件、文件名安全、大小限制和清理策略。

## 本次没有做什么

本任务没有做：

- multipart browser upload。
- PDF。
- Word。
- HTML。
- 知识库更新、删除、重命名。
- 目录 watch。
- 真实 embedding provider。
- 真实 LLM。
- vector database。
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
108 passed
```

测试覆盖：

- from-file 从 `.md` 创建知识库。
- from-file 创建后 answer 保留真实 `source_path#chunk-0`。
- from-file 创建后 app recreate 仍能 answer。
- 文件不存在返回 `400`。
- 不支持扩展名返回 `400`。
- from-directory 递归导入 `.md/.txt`。
- from-directory 忽略不支持扩展名。
- extensions filter 生效。
- 空目录创建空知识库并拒答。
- invalid chunking 参数返回 `400`。
- 现有 answer API、knowledge base API 和 health API 继续通过。

## 学到什么

- ingestion 边界应该复用，API 层不应该重新写文件读取逻辑。
- citation 的可靠性依赖 metadata 从 ingestion 一直保留到 chunk。
- 本机 path import 和 multipart upload 是两个不同问题，不应该混在一个任务里。
- 在接真实 provider 前，先把数据入口补齐，可以让后续 eval 和真实 provider 对比更有意义。

## Trellis 反馈

本次继续符合学习型 Trellis 约束：

- 先创建任务目录和 PRD。
- PRD 明确 Learning Goals、Why Now、Approach Options、Out of Scope。
- 实现最小可运行闭环。
- 测试覆盖成功、错误、恢复和 citation。
- 学习记录用中文说明做了什么、作用、工具、输入输出、定位、验证和下一步。
- README、技术笔记、根目录学习文档和 backend specs 已同步更新。

## 下一步学习

下一步建议任务：

```text
real provider planning
```

原因是当前 RAG 工程链路、知识库持久化、文件导入、citation、refusal 和 eval 都已经有了最小闭环。下一步适合开始规划真实 embedding provider 和真实 LLM answer generation 的配置、API key、mock 测试和 eval 边界。
