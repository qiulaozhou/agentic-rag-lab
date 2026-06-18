# Agentic RAG Lab Learning Index

更新日期：2026-06-18

## 当前状态

`agentic-rag-lab` 已收口为 `Resume-ready V1`。它不是生产级 RAG 系统，但已经具备一个可以运行、可以测试、可以通过 HTTP 调用、可以导入本地文件、可以恢复本地知识库、可以选择真实 provider、可以做最小 eval 对比的 RAG 工程闭环。

在当前三项目作品集里，后续两步也已经推进完成到：

```text
ai-agent-workbench: V9 read-only MCP DevTools observation integration
mcp-devtools-server: first real read-only GitHub + CI MCP tools
```

完整链路：

```text
ingestion
-> chunking
-> embedding
-> retrieval
-> citation-aware generation
-> answer pipeline
-> refusal behavior
-> eval dataset / eval report
-> HTTP answer API
-> persistent local knowledge base
-> disk-backed local knowledge base
-> file / directory import API
-> optional OpenAI-compatible providers
-> real provider manual smoke guide
-> eval provider comparison
-> resume-ready project closeout
```

## 学习路线总览

| 步骤 | 做了什么 | 作用 | 在整体链路中的位置 | 学到什么 |
| --- | --- | --- | --- | --- |
| 1. FastAPI skeleton | 建立 `create_app()`、`/health`、settings、fake LLM 边界 | 先让项目能启动、能测试、能扩展 | 服务入口 | AI 项目也要先有稳定工程骨架 |
| 2. Markdown/TXT ingestion | 实现 `load_text_file()` 和 `load_directory()` | 把本地文本变成 `SourceDocument` | ingestion | RAG 的输入必须保留 `source_path` 等元数据 |
| 3. Chunking | 实现 `chunk_document()` / `chunk_documents()` | 把长文档切成可检索片段 | chunking | chunk 是检索和 citation 的最小承载单位 |
| 4. Local embedding + vector store | 实现 `LocalHashEmbeddingProvider` 和 `InMemoryVectorStore` | 建立离线、确定性、可测试的检索前置闭环 | embedding / retrieval | 本地 hash embedding 是学习替代实现，不是真实语义模型 |
| 5. Retrieval pipeline | 组合 chunk、embedding、vector search | 让调用方不用手动拼检索流程 | retrieval pipeline | pipeline 负责组合，不复制底层排序逻辑 |
| 6. Citation-aware generation | 实现确定性 `CitationAwareAnswerGenerator` | 让回答带 citation，并且 citation 来自 metadata | generation | citation authority 应该来自本地 evidence，不应让模型自由编 |
| 7. Answer pipeline | 实现 `LocalAnswerPipeline.answer()` | 把 retrieval 和 generation 组合成内部问答边界 | answer pipeline | 内部 API 边界比直接拼模块更稳定 |
| 8. Refusal behavior | 实现 `MinimumEvidenceRefusalPolicy` | evidence 不足时拒答，避免无依据生成 | refusal | 拒答发生在 retrieval 之后、generation 之前 |
| 9. Eval dataset/report | 实现 `EvalCase`、`EvalReport` | 用离线 case 检查 answer、citation、refusal | eval | RAG 不能只看能不能回答，还要看是否引用正确、是否该拒答 |
| 10. HTTP answer API | 实现 `POST /answer` | 把内部 pipeline 暴露为 HTTP 问答服务 | API boundary | API 层只做 DTO 和参数校验，不复制 RAG 逻辑 |
| 11. In-process knowledge base | 实现可复用知识库 registry | 让多个请求复用同一个 pipeline | knowledge base | 复用式知识库和每次携带 documents 是两种调用模式 |
| 12. Disk-backed knowledge base | 用 JSON 保存知识库并启动恢复 | 服务重启后仍能通过旧 id 提问 | persistence | 不序列化 runtime pipeline，只保存 documents/chunks/config |
| 13. File/directory import API | 实现从本机 path 导入 `.md` / `.txt` | 调用方不必手动把文件内容塞进请求体 | import API | 文件导入仍要复用 ingestion helper，保留 citation metadata |
| 14. OpenAI-compatible providers | 实现 embedding 和 chat adapters | 显式配置后可接真实 provider | provider adapters | 默认离线，真实 provider opt-in，pytest 用 mock |
| 15. Manual smoke guide | 写真实 provider 手动验证指南 | 区分人工真实验证和自动化回归 | provider validation | 真实 key、网络、额度不适合默认 pytest |
| 16. Eval provider comparison | 扩展 baseline/candidate 对比 | 比较 provider 输出是否改变 answer/citation/refusal | provider eval | comparison report 不是 benchmark，但能观察行为漂移 |
| 17. Resume-ready closeout | 整理学习文档和项目展示 | 把项目变成可复习、可面试讲述的 V1 | project closeout | 项目收口要讲清完成内容、边界、验证和未做内容 |

## 每一步为什么按这个顺序

这个项目没有一开始就做 UI、LangGraph、MCP 或多 agent。原因是 RAG 的底层可靠性来自更基础的链路：

```text
可控输入
-> 可追溯 chunk
-> 可测试 retrieval
-> 可控 citation
-> 可解释 refusal
-> 可回归 eval
```

如果这些边界没有稳定，外层 Agent Loop 或 UI 只是在包装一个不可靠的上下文系统。

## 之前的本地替代实现是什么

`LocalHashEmbeddingProvider` 是本地 deterministic embedding 替代实现。它用 token + `sha256` 映射到固定维度向量，再做 L2 normalization。它的价值是离线、可测试、无外部依赖，适合学习检索边界。

它不是生产级语义 embedding。真实 provider 接入后，embedding 可以通过 OpenAI-compatible `/embeddings` 获得语义向量，但默认仍关闭，避免测试依赖真实 key。

`CitationAwareAnswerGenerator` 是 deterministic generator。它不调用真实 LLM，而是基于 evidence 组织一个稳定回答。它的价值是让 citation、refusal、eval 可以被确定性测试覆盖。

LLM-backed generator 接入后，回答正文可以由真实 LLM 生成，但 citation 仍由本地 `RetrievalResult.chunk.metadata` 生成。这样可以避免模型编造不存在的 citation。

## 这个项目现在可以怎么讲

一句话：

```text
实现了一个可离线测试、可 HTTP 调用、可导入本地文件、可恢复知识库、支持 citation/refusal/eval、并可选接入 OpenAI-compatible provider 的 RAG 问答服务。
```

更工程化的说法：

```text
按 ingestion、chunking、embedding、retrieval、generation、refusal、eval、API、knowledge base、provider adapters 拆分边界，逐步构建最小可运行 RAG 闭环，并用 pytest 覆盖每个阶段的关键行为。
```

## 这个项目还没有做什么

- 生产级向量库：Chroma、Qdrant、pgvector。
- PDF、Word、HTML 等复杂文档解析。
- multipart browser upload。
- 知识库 update/delete/list API。
- rerank。
- streaming response。
- auth、rate limit、request size limit。
- 生产级错误响应规范。
- 大规模 eval dataset、LLM judge、latency/cost/token 统计。
- Web UI。
- LangGraph / Agent Loop。
- MCP 集成。
- 多 agent 编排。

## 学习顺序中的下一站

`agentic-rag-lab` 作为简历项目 V1 暂时收口。学习顺序上，下一站是：

```text
ai-agent-workbench
```

`ai-agent-workbench` 现在已完成到 V9：让 Agent 不只是回答问题，而是围绕任务计划、约束、工具调用、执行记录、验证结果和只读外部 DevTools observation 形成可审计的工作台。
