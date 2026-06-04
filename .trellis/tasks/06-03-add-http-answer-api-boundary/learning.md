# 学习记录

更新日期：2026-06-03

## 本步一句话总结

这一步把内部 `LocalAnswerPipeline.answer()` 暴露成了最小 HTTP endpoint：`POST /answer`，让 `agentic-rag-lab` 从本地 Python 闭环推进到可通过 HTTP 调用的 RAG 问答服务。

## 本步做了什么

本次新增了 HTTP answer API boundary：

```text
POST /answer
-> AnswerRequest
-> SourceDocument
-> LocalAnswerPipeline.from_documents()
-> LocalAnswerPipeline.answer()
-> GeneratedAnswer
-> AnswerResponse
```

新增能力：

- `src/agentic_rag_lab/api/answer.py`
- `AnswerDocument`
- `AnswerRequest`
- `AnswerResponse`
- `POST /answer`
- 在 `main.py` 注册 answer router

## 作用是什么

前面已经完成了内部 RAG 闭环，但调用方只能在 Python 代码里使用 `LocalAnswerPipeline`。本步的作用是提供一个最小 HTTP 出口，让外部程序可以通过请求调用当前 RAG 能力。

这一步不是做完整产品 API，而是验证 API 边界：

- request 如何变成 `SourceDocument`。
- HTTP endpoint 如何复用内部 pipeline。
- `GeneratedAnswer` 如何变成 response。
- 参数错误如何转成 `400 Bad Request`。

## 用什么实现

代码使用这些已有边界：

- `SourceDocument`
- `LocalAnswerPipeline`
- `GeneratedAnswer`
- `MinimumEvidenceRefusalPolicy`
- `CitationAwareAnswerGenerator`

新增实现：

- FastAPI `APIRouter`
- Pydantic `BaseModel` DTO
- `TestClient` API 测试

API 层没有重新实现 chunking、embedding、retrieval、citation、refusal 或 eval。

## 输入输出

输入：

```json
{
  "question": "Why do RAG answers need citations?",
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
  "overlap": 0,
  "limit": 5
}
```

输出：

```json
{
  "text": "基于检索到的资料，可以回答如下：...",
  "citations": ["docs/rag.md#chunk-0"],
  "refused": false
}
```

错误输入：

```text
limit <= 0 -> 400
chunk_size <= 0 -> 400
overlap < 0 -> 400
overlap >= chunk_size -> 400
```

## 在整体流程中的定位

当前项目整体链路已经推进到：

```text
POST /answer
-> AnswerRequest
-> SourceDocument
-> DocumentChunk
-> LocalHashEmbeddingProvider
-> InMemoryVectorStore
-> LocalRetrievalPipeline.search()
-> MinimumEvidenceRefusalPolicy
-> CitationAwareAnswerGenerator.answer()
-> LocalAnswerPipeline.answer()
-> AnswerResponse
```

这一步位于 eval dataset / eval report 之后，说明第一阶段 RAG 核心闭环已经具备最小 HTTP 调用入口。

## 为什么现在做

现在项目已经完成：

- ingestion。
- chunking。
- embedding。
- retrieval。
- citation-aware generation。
- answer pipeline。
- refusal behavior。
- eval dataset / eval report。

内部链路已经可运行、可拒答、可评估。现在暴露最小 HTTP endpoint，比直接做 UI、MCP 或真实 LLM 更合适，因为它把内部能力变成外部可调用能力，同时仍然保持范围可控。

## 设计选择

本次选择“请求内直接携带 documents”。

考虑过的方案：

- 请求内携带 documents：本次采用。最小、无持久化、无新依赖。
- 文件上传或目录读取 API：暂缓。需要文件和路径安全设计。
- 持久化知识库：暂缓。需要索引生命周期和存储设计。

## 本次没有做什么

本任务没有做：

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

这些能力可以在 HTTP answer boundary 稳定后再按顺序设计。

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

随后用提升权限运行同一个命令。第一次发现当 `documents=[]` 时底层 chunking 不会触发 `chunk_size/overlap` 校验，因此 API 层补了显式请求参数校验。

最终验证结果：

```text
74 passed
```

## 学到什么

- HTTP API boundary 应该复用内部 pipeline，而不是重写业务逻辑。
- API DTO 和 domain dataclass 应该分开，避免 HTTP 请求形状污染内部模型。
- 当底层逻辑在某些输入下不会触发校验时，API 层需要补足请求边界校验。
- 现在 endpoint 每次请求携带 documents，这证明了 HTTP 调用能力，但还不是持久化知识库。

## Trellis 反馈

本次继续符合增强后的学习型 Trellis 约束：

- PRD 先说明学习目标、Why Now 和 out-of-scope。
- 实现保持最小 HTTP 闭环。
- 测试覆盖成功回答、拒答和 400 错误。
- 文档同步说明本步做了什么、作用、工具、输入输出、定位、验证和下一步。

已同步更新 backend specs：

- `.trellis/spec/backend/directory-structure.md`
- `.trellis/spec/backend/quality-guidelines.md`

## 下一步学习

下一步建议任务：

```text
persistent local knowledge base
```

原因是当前 `/answer` 每次请求都要携带 documents。下一步可以学习如何在本地维护一个简单知识库或索引入口，但仍然不需要跳到 UI、Workbench、MCP、LangGraph 或多 agent。
