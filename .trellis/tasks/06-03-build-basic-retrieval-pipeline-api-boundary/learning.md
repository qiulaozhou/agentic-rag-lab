# 学习记录

更新日期：2026-06-03

## 核心概念

这次任务练习的是 retrieval pipeline / API boundary：

```text
SourceDocument
-> DocumentChunk
-> InMemoryVectorStore
-> LocalRetrievalPipeline.search()
-> RetrievalResult
```

核心概念是：上层模块不应该自己拼装 chunking、embedding 和 vector store。它们应该通过一个稳定的 retrieval 边界拿到 `RetrievalResult`，然后再决定如何生成答案、引用或拒答。

## 为什么现在做

项目已经完成：

- Markdown/TXT ingestion。
- deterministic chunking。
- local hash embedding。
- in-memory vector retrieval。

底层 adapter 已经能工作，但如果后续 generation 直接调用 `chunk_documents` 和 `InMemoryVectorStore`，generation 层会知道太多检索实现细节。现在先抽出 `LocalRetrievalPipeline`，可以让后续 answer generation 只依赖 retrieval 结果。

## 设计选择

本次选择新增内部 `LocalRetrievalPipeline`，暂时不新增 HTTP endpoint。

考虑过的方案：

- 内部 `LocalRetrievalPipeline`：本次采用。优点是最小、离线、无新依赖，可以直接复用已有代码。
- FastAPI retrieval endpoint：暂缓。它需要请求/响应结构、错误处理、文档输入方式等设计，当前过早。
- 在 generation 层直接调用 vector store：暂缓。这样会让 generation 知道太多 retrieval 细节，不利于后续替换 provider 或 store。

## 本次变更

- 新增 `agentic_rag_lab.retrieval.pipeline`。
- 新增 `LocalRetrievalPipeline`。
- 支持 `LocalRetrievalPipeline.from_chunks()`。
- 支持 `LocalRetrievalPipeline.from_documents()`。
- `search(query, limit=5)` 委托给底层 `InMemoryVectorStore`。
- 更新 `retrieval.__init__` 导出 pipeline。
- 新增 pipeline 单元测试。
- 将原本的 ingestion/chunking/retrieval 集成测试改为使用 pipeline。
- 更新 README、技术笔记、根目录学习笔记和 backend specs。

## 如何验证

普通命令：

```powershell
uv run pytest
```

这台机器在普通权限下仍然会在 pytest 启动前失败，原因是 `uv` 无法访问本地 cache：

```text
error: Failed to initialize cache at `C:\Users\admin\AppData\Local\uv\cache`
  Caused by: failed to open file `C:\Users\admin\AppData\Local\uv\cache\sdists-v9\.git`: refused access (os error 5)
```

随后用提升权限运行同一个命令，结果为：

```text
37 passed
```

## Trellis 反馈

这次任务符合学习型 Trellis 流程：

- PRD 先明确了 concept、Why Now、方案选择和 out-of-scope。
- 实现只做 retrieval pipeline，没有跳到 HTTP endpoint、答案生成、eval、UI、LangGraph、MCP 或多 agent。
- 代码复用已有 chunking 和 vector store，没有复制底层相似度逻辑。

本次沉淀到 backend specs 的可复用约定：

- retrieval composition 放在 `retrieval/pipeline.py`。
- pipeline 负责组合已有能力，不复制 chunking、embedding 或 vector similarity 逻辑。
- pipeline 测试要覆盖从 chunks 构建和从 documents 构建两种入口。

## 下一步学习

下一步建议任务：

```text
citation-aware answer generation
```

这个任务应该基于 `LocalRetrievalPipeline.search()` 返回的 `RetrievalResult` 生成带来源的 `GeneratedAnswer`。仍然不要跳到 refusal、eval report、Workbench、MCP、LangGraph、UI 或多 agent 编排。
