# 学习记录

更新日期：2026-06-03

## 核心概念

这次任务练习的是 RAG 数据链路里的下一层边界：

```text
DocumentChunk -> embedding vector -> vector store -> RetrievalResult
```

核心概念是：检索需要把 `chunk` 文本和用户查询都转换成可比较的向量。只有当二者处在同一个向量空间里，系统才能用相似度给候选 `chunk` 排序。

## 为什么现在做

项目已经有了确定性的 Markdown/TXT 导入和 chunking，能够稳定产生带来源 metadata 的 `DocumentChunk`。

下一步最小闭环不是生成答案，也不是接 UI、LangGraph、MCP 或多 agent，而是先让这些 `DocumentChunk` 可以被查询检索。后续的引用回答、拒答和 eval 都依赖这个检索边界。

## 设计选择

本次选择了“确定性的本地 hash embedding + 内存向量检索”。

考虑过的方案：

- 确定性本地 hash embedding：本次采用。优点是离线、无依赖、稳定、容易测试。
- 真实 embedding provider：暂缓。它会引入密钥、网络、SDK 选择和调用成本，太早。
- 生产型向量数据库：暂缓。当前还不需要持久化和数据库选型，先证明 adapter 边界。

这个选择的代价是：hash embedding 不是真正的语义 embedding，也可能有 hash 碰撞。但它足够用来学习和测试检索 adapter 的形状、排序行为以及 metadata 保留。

## 本次变更

- 新增 `agentic_rag_lab.embeddings`。
- 新增 `EmbeddingProvider`。
- 新增 `LocalHashEmbeddingProvider`。
- 新增 `agentic_rag_lab.retrieval.vector`。
- 新增 `InMemoryVectorStore`。
- 导出新的 embedding 和 retrieval helper。
- 新增 pytest 覆盖 embedding、向量检索、以及 `ingestion -> chunking -> retrieval` 的本地闭环。
- 更新 README、技术笔记、根目录学习笔记和 Trellis backend specs。

## 如何验证

普通命令：

```powershell
uv run pytest
```

这台机器在普通权限下会在 pytest 启动前失败，原因是 `uv` 无法访问本地 cache：

```text
error: Failed to initialize cache at `C:\Users\admin\AppData\Local\uv\cache`
  Caused by: failed to open file `C:\Users\admin\AppData\Local\uv\cache\sdists-v9\.git`: refused access (os error 5)
```

随后用提升权限运行同一个命令，结果为：

```text
31 passed
```

## Trellis 反馈

这次学习型 Trellis 流程仍然适用：

- PRD 在实现前明确了 concept、Why Now、方案选择和 out-of-scope。
- 实现保持在本地 RAG 数据链路内。
- 没有引入外部 provider、数据库、API endpoint、UI、LangGraph、MCP 或多 agent 行为。

本次沉淀到 backend specs 的可复用约定：

- embedding provider 放在 `embeddings/`。
- retrieval adapter 放在 `retrieval/`。
- 未来接真实 embedding 服务时，要藏在 `EmbeddingProvider` 后面。
- retrieval 输出必须保留 `DocumentChunk` metadata。

## 下一步学习

下一步建议任务：

```text
构建基于本地向量库的 basic retrieval pipeline / API boundary。
```

这个任务应该让 RAG 系统里的其他模块更容易调用 retrieval，同时仍然不要跳到答案生成、引用生成、拒答、eval report、Workbench、MCP、LangGraph、UI 或多 agent 编排。
