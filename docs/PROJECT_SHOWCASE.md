# Agentic RAG Lab Project Showcase

更新日期：2026-06-04

## 项目定位

`agentic-rag-lab` 是一个面向学习和简历展示的 RAG 工程项目。它的目标不是一次性做成生产级知识库系统，而是把 RAG 的核心工程链路拆成清晰边界，并逐步实现可运行、可测试、可解释的最小闭环。

当前状态：

```text
Resume-ready V1
```

## 项目一句话

实现了一个可离线测试、可 HTTP 调用、可导入本地 Markdown/TXT 文件、可恢复本地知识库、支持 citation/refusal/eval，并可选接入 OpenAI-compatible provider 的 RAG 问答服务。

## 核心能力

- 本地文档导入：支持 `.md` / `.txt` 文件和目录导入。
- 文档切分：把 `SourceDocument` 转成保留 metadata 的 `DocumentChunk`。
- 本地检索 baseline：使用 deterministic hash embedding 和 in-memory vector store。
- citation-aware answer：回答返回 `text`、`citations`、`refused`。
- refusal behavior：空问题、无 evidence、低分 evidence 会拒答。
- eval report：检查 answer term、citation、refusal 三类最小信号。
- HTTP API：支持 `POST /answer` 和 knowledge base API。
- disk-backed knowledge base：用本地 JSON 文件保存知识库，服务重启后可恢复。
- file/directory import API：从服务端本机 path 导入知识库。
- OpenAI-compatible providers：显式配置后可接 embedding 和 chat completion provider。
- eval provider comparison：支持 baseline/candidate eval report 对比。

## 技术边界

| 边界 | 模块 | 说明 |
| --- | --- | --- |
| ingestion | `agentic_rag_lab.ingestion` | 从本地文件或目录生成 `SourceDocument` |
| chunking | `agentic_rag_lab.chunking` | 生成可检索的 `DocumentChunk` |
| embedding | `agentic_rag_lab.embeddings` | 默认本地 hash embedding，可选 OpenAI-compatible embedding |
| retrieval | `agentic_rag_lab.retrieval` | in-memory vector search 和 retrieval pipeline |
| generation | `agentic_rag_lab.generation` | citation-aware generator、LLM-backed generator、answer pipeline、refusal policy |
| eval | `agentic_rag_lab.evals` | deterministic eval 和 provider comparison |
| API | `agentic_rag_lab.api` | HTTP request/response DTO 和 route handler |
| knowledge base | `agentic_rag_lab.knowledge_base` | in-process 和 disk-backed knowledge base registry |
| provider | `agentic_rag_lab.llm` | OpenAI-compatible chat completion provider |

## 代表性接口

临时问答：

```http
POST /answer
```

创建知识库：

```http
POST /knowledge-bases
POST /knowledge-bases/from-file
POST /knowledge-bases/from-directory
```

基于知识库问答：

```http
POST /knowledge-bases/{knowledge_base_id}/answer
```

## 我在项目中做了什么

- 按 Trellis 学习流程，把每个任务拆成 PRD、实现、测试、学习记录。
- 从 FastAPI skeleton 开始，逐步建立 ingestion、chunking、embedding、retrieval、generation、refusal、eval、API、knowledge base 和 provider adapters。
- 用 deterministic baseline 保证早期能力离线可测，不依赖真实模型和网络。
- 实现 citation-aware answer，确保 citations 来自本地 retrieval metadata，而不是模型自由生成。
- 实现 refusal policy，让系统在 evidence 不足时返回 `refused=True`。
- 实现 eval dataset/report，用 answer/citation/refusal 三个信号回归验证 RAG 行为。
- 实现 disk-backed knowledge base，让知识库可以跨 FastAPI app 重启恢复。
- 实现 OpenAI-compatible provider adapters，但默认保持本地离线，真实 provider 通过环境变量显式开启。
- 编写真实 provider manual smoke guide，明确真实 key 只放本地 `.env`，pytest 不联网。
- 扩展 provider comparison，让 candidate provider 能与本地 baseline 做最小对比。
- 整理项目学习文档和根目录学习笔记，把项目收口为 `Resume-ready V1`。

## 简历可用表述

短版：

```text
实现 Agentic RAG Lab：基于 FastAPI 构建本地可测试的 RAG 问答服务，覆盖文档导入、chunking、embedding/retrieval、citation-aware generation、refusal、eval report、HTTP API、disk-backed knowledge base，并支持 OpenAI-compatible provider 的可选接入。
```

强调工程边界版：

```text
按 ingestion、chunking、embedding、retrieval、generation、refusal、eval、API、knowledge base、provider adapters 拆分 RAG 系统边界，使用 pytest 覆盖关键行为，并通过 Trellis 任务文档沉淀 PRD、学习目标、验证结果和技术取舍。
```

强调可靠性版：

```text
为 RAG 问答链路加入 citation 和 refusal 约束：citation 固定由检索 evidence 的 metadata 生成，证据不足时返回拒答；同时构建 deterministic eval report，对 answer、citation、refusal 做最小回归验证。
```

## 面试讲解顺序

1. 先讲为什么做 RAG：LLM 需要可靠上下文和可追溯来源。
2. 再讲核心链路：document -> chunk -> embedding -> retrieval -> generation -> citation/refusal。
3. 然后讲工程拆分：每个边界都有独立模块和测试。
4. 再讲为什么默认本地 deterministic：学习阶段要稳定、离线、可回归。
5. 接着讲真实 provider 怎么接：通过 OpenAI-compatible adapters 和 settings opt-in。
6. 最后讲还没做什么：生产级向量库、复杂文档解析、rerank、streaming、auth、UI、LangGraph/MCP。

## 项目边界

这个项目可以说明你理解并实现了 RAG 核心工程链路，但不要把它描述成生产级系统。当前还没有：

- 生产级 vector database。
- 大规模知识库管理。
- PDF/Word/HTML 解析。
- rerank。
- streaming。
- auth/rate limit。
- UI。
- LangGraph 或多 agent 编排。

## 后续主线

`agentic-rag-lab` 已经可以作为简历中的 RAG 项目 V1。下一步建议进入 `ai-agent-workbench`，把重点放在 Agent 任务规划、工具调用、执行观察、Trellis/harness 工程化约束和可审计工作流上。
