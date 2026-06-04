# 学习记录

更新日期：2026-06-03

## 本步一句话总结

这一步把 `agentic-rag-lab` 从“每次 `POST /answer` 都携带 documents”推进到“先创建进程内本地知识库，再基于 knowledge base id 多次提问”的最小可复用知识库闭环。

## 本步做了什么

本次新增了 persistent local knowledge base 的第一版实现：

```text
POST /knowledge-bases
-> documents
-> SourceDocument
-> DocumentChunk
-> LocalAnswerPipeline
-> InMemoryKnowledgeBaseRegistry

POST /knowledge-bases/{knowledge_base_id}/answer
-> LocalKnowledgeBase.answer()
-> LocalAnswerPipeline.answer()
-> GeneratedAnswer
-> HTTP response
```

新增能力：

- `agentic_rag_lab.knowledge_base.LocalKnowledgeBase`
- `agentic_rag_lab.knowledge_base.InMemoryKnowledgeBaseRegistry`
- `src/agentic_rag_lab/api/knowledge_base.py`
- `POST /knowledge-bases`
- `POST /knowledge-bases/{knowledge_base_id}/answer`
- `app.state.knowledge_bases`
- knowledge base 单元测试
- knowledge base HTTP API 测试

## 作用是什么

前一步的 `POST /answer` 已经能通过 HTTP 调用 RAG 闭环，但它有一个明显限制：每次请求都要重新携带 documents，服务端也要重新构建 pipeline。

本步的作用是把“临时问答请求”推进到“可复用知识库入口”：

- 调用方先提交 documents 创建知识库。
- 服务端在 app 进程内保存该知识库和 answer pipeline。
- 后续请求只需要带 `knowledge_base_id` 和 `question`。
- citation、refusal、retrieval 仍然复用原有内部 pipeline。

这让项目开始具备“知识库管理 API”和“问答 API”的分层意识。

## 用什么实现

本次使用的已有模块：

- `SourceDocument`
- `DocumentChunk`
- `chunk_documents()`
- `LocalAnswerPipeline`
- `GeneratedAnswer`
- `MinimumEvidenceRefusalPolicy`
- `CitationAwareAnswerGenerator`

本次新增的实现：

- `LocalKnowledgeBase`：保存 documents、chunks、chunk 参数和已构建的 `LocalAnswerPipeline`。
- `InMemoryKnowledgeBaseRegistry`：保存多个知识库，提供 create/get/list。
- FastAPI `Request.app.state`：保存 registry，避免模块级全局状态。
- Pydantic DTO：定义创建知识库和基于知识库提问的 HTTP 输入输出。
- `TestClient`：验证跨请求创建和提问。

## 输入输出是什么

创建知识库输入：

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

创建知识库输出：

```json
{
  "knowledge_base_id": "kb-1",
  "document_count": 1,
  "chunk_count": 1
}
```

基于知识库提问输入：

```json
{
  "question": "Why do RAG answers need citations?",
  "limit": 5
}
```

基于知识库提问输出：

```json
{
  "text": "基于检索到的资料，可以回答如下：...",
  "citations": ["docs/rag.md#chunk-0"],
  "refused": false
}
```

错误输出：

```text
chunk_size <= 0 -> 400
overlap < 0 -> 400
overlap >= chunk_size -> 400
limit <= 0 -> 400
unknown knowledge_base_id -> 404
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
```

这一步位于 HTTP answer API 之后。它没有改变检索、生成、拒答或 eval 的内部逻辑，而是在 API 层之上增加了“知识库生命周期”这个概念。

## 为什么现在做

现在做这一步的原因是：内部 RAG 闭环已经可运行、可拒答、可评估，并且已经能通过 HTTP 调用。

如果此时直接跳到 UI、MCP、LangGraph 或真实 LLM，会绕过一个重要问题：知识库系统不能长期依赖“每次请求都携带 documents”。所以现在先做进程内知识库 registry，学习：

- 如何创建知识库。
- 如何复用知识库。
- 如何基于知识库 id 提问。
- 如何保持 API 层只做边界转换，不重写 RAG 逻辑。

## 设计选择

本次选择“FastAPI app 进程内 registry”。

原因：

- 不引入新依赖。
- 不需要数据库。
- 不需要磁盘序列化。
- 测试可以完全离线。
- 能清楚学习知识库 API 和 answer pipeline 的组合关系。

没有使用模块级全局变量。registry 放在 `app.state.knowledge_bases`，这样每次 `create_app()` 都会创建独立 registry，测试之间不会互相污染。

knowledge base id 使用 registry 内递增的 `kb-1`、`kb-2`，这样行为确定，测试稳定。

## 本次没有做什么

本任务没有做：

- 磁盘级持久化。
- SQLite。
- 文件上传。
- 目录扫描 API。
- 知识库删除或更新。
- 多租户隔离。
- 并发写入锁。
- 真实 embedding provider。
- 真实 LLM。
- Chroma / Qdrant / pgvector。
- rerank。
- streaming。
- auth。
- Web UI。
- LangGraph。
- MCP。
- multi-agent orchestration。

当前知识库只在 app 进程内存在，服务重启后会丢失。这是本任务的明确边界，不是生产级持久化。

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
90 passed
```

测试覆盖：

- registry create/get/list。
- document count 和 chunk count。
- metadata 到 citation 的保留。
- unknown knowledge base id。
- `POST /knowledge-bases` 创建成功。
- `POST /knowledge-bases/{id}/answer` 正常回答。
- 空 question 拒答。
- 无关问题拒答。
- 空 documents 知识库拒答。
- unknown id 返回 404。
- invalid limit/chunk_size/overlap 返回 400。
- 现有 `POST /answer` 继续工作。

## 学到什么

- `/answer` 是临时问答 API，knowledge base API 是可复用知识入口。
- “进程内持久化”和“磁盘持久化”不是一回事，文档里必须写清楚边界。
- API route handler 应该只做参数校验、DTO 转换和调用内部边界，不应该复制 RAG pipeline 逻辑。
- `app.state` 适合当前学习阶段保存 app 生命周期内的 registry。
- 用确定性 id 可以让测试更稳定，但后续生产版本可能需要更适合分布式和持久化的 id 策略。

## Trellis 反馈

本次继续符合学习型 Trellis 约束：

- 先创建任务目录和 PRD。
- PRD 明确 Learning Goals、Why Now、Approach Options、Out of Scope。
- 实现最小可运行闭环。
- 测试验证成功路径、拒答路径和错误路径。
- 学习记录用中文说明做了什么、作用、工具、输入输出、定位、验证和下一步。
- README、技术笔记、根目录学习文档和 backend specs 已同步更新。

## 下一步学习

下一步建议任务：

```text
disk-backed local knowledge base
```

原因是当前 knowledge base 只保存在 app 进程内。它能跨 HTTP 请求复用，但服务重启后会丢失。下一步可以学习如何把 documents/chunks/index 保存到本地磁盘，并在服务启动后恢复。

另一个可选方向是：

```text
real provider planning
```

但仍然不要直接跳到 UI、Workbench、MCP、LangGraph 或多 agent。
