## Resume-ready V1 收口：Agentic RAG Lab

更新日期：2026-06-04

`agentic-rag-lab` 当前已经收口为 `Resume-ready V1`。这个项目不是生产级 RAG 系统，但已经具备可运行、可测试、可 HTTP 调用、可导入本地文件、可恢复本地知识库、可选接真实 provider、可做最小 eval 对比的 RAG 工程闭环。

当前完整链路：

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

### V1 已完成能力

- FastAPI app factory 和 `/health`。
- Markdown/TXT 文件与目录导入。
- `SourceDocument -> DocumentChunk` 文档切分。
- 本地 deterministic `LocalHashEmbeddingProvider`。
- in-memory vector retrieval 和 retrieval pipeline。
- citation-aware deterministic answer generator。
- `LocalAnswerPipeline.answer()` 内部问答边界。
- `MinimumEvidenceRefusalPolicy` 基础拒答策略。
- `EvalCase -> EvalReport` 离线评估。
- `POST /answer` HTTP 问答接口。
- in-process knowledge base 和 disk-backed knowledge base。
- `POST /knowledge-bases/from-file` 与 `POST /knowledge-bases/from-directory`。
- OpenAI-compatible embedding / chat provider adapters，默认关闭，显式配置后启用。
- 真实 provider manual smoke guide。
- baseline/candidate eval provider comparison。

### 运行方式

安装依赖和运行测试：

```powershell
uv run pytest
```

本次收口验证结果：

```text
普通权限运行 `uv run pytest` 先因本机 uv cache 权限失败；
提升权限运行同一命令后通过：139 passed。
```

启动服务：

```powershell
uv run uvicorn agentic_rag_lab.main:app --reload
```

默认配置保持离线：

```text
EMBEDDING_PROVIDER=local_hash
ANSWER_GENERATOR=local_citation
```

真实 provider 只通过本地 `.env` 显式开启，文档和代码只记录变量名，不记录真实 key：

```text
EMBEDDING_PROVIDER=openai_compatible
ANSWER_GENERATOR=openai_compatible
OPENAI_COMPATIBLE_API_KEY=your-api-key
OPENAI_COMPATIBLE_BASE_URL=your-openai-compatible-base-url
OPENAI_COMPATIBLE_EMBEDDING_MODEL=your-embedding-model
OPENAI_COMPATIBLE_CHAT_MODEL=your-chat-model
```

### 主要 API

```text
GET  /health
POST /answer
POST /knowledge-bases
POST /knowledge-bases/from-file
POST /knowledge-bases/from-directory
POST /knowledge-bases/{knowledge_base_id}/answer
```

`POST /answer` 适合临时问答：每次请求携带 documents。

knowledge base API 适合复用式问答：先创建知识库，再用 `knowledge_base_id` 提问。

### 学习文档入口

- `docs/LEARNING_INDEX.md`：按任务顺序解释每一步做了什么、为什么做、在 RAG 链路中的位置、学到什么。
- `docs/PROJECT_SHOWCASE.md`：面向简历和面试的项目展示文档，区分项目整体能力和个人实现内容。
- `docs/TECHNICAL_NOTES.md`：按模块边界整理技术设计。
- `docs/REAL_PROVIDER_SMOKE_GUIDE.md`：真实 provider 的本地手动验证指南。

### 简历定位

一句话：

```text
实现了一个可离线测试、可 HTTP 调用、可导入本地 Markdown/TXT 文件、可恢复本地知识库、支持 citation/refusal/eval，并可选接入 OpenAI-compatible provider 的 RAG 问答服务。
```

这个项目适合在简历里证明：

- 理解 RAG 从文档导入到回答生成的完整工程链路。
- 能把 LLM 应用拆成可测试的模块边界。
- 能处理 citation、refusal、eval 这些可靠性问题。
- 能安全接入真实 provider，同时保留本地 deterministic baseline。
- 能用 Trellis/harness 约束任务顺序、PRD、学习目标、验证和复盘。

### 当前未做内容

本 V1 不包含：

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

### 下一主线

`agentic-rag-lab` 作为简历项目 V1 暂时收口。后续主线进入：

```text
ai-agent-workbench
```

`ai-agent-workbench` 会重点体现 Agent 工作台、任务规划、工具调用、执行观察和 Trellis/harness 工程化实践。

---

## 2026-06-04 进度更新：real provider manual smoke guide + eval provider comparison

本次一次推进了两个连续任务：

```text
real provider manual smoke guide
-> eval provider comparison
```

项目现在已经不仅能可选接 OpenAI-compatible provider，还具备了“如何安全手动验证真实 provider”和“如何比较本地 baseline 与 candidate provider 输出差异”的最小能力。

### 本步做了什么

- 新增 `docs/REAL_PROVIDER_SMOKE_GUIDE.md`。
- 指南说明真实 key 只放本地 `.env`，不进入仓库。
- 指南提供 PowerShell 手动验证步骤：
  - `/health`
  - `POST /answer`
  - `POST /knowledge-bases`
  - `POST /knowledge-bases/{id}/answer`
  - `POST /knowledge-bases/from-file`
- 扩展 `agentic_rag_lab.evals`：
  - `EvalRunConfig`
  - `run_eval_cases_with_pipeline_factory()`
  - `run_eval_cases_with_config()`
  - `EvalComparisonReport`
  - `compare_eval_reports()`
- 保留原有 `run_eval_cases()` 默认本地行为不变。
- 新增测试覆盖 smoke guide 安全内容和 eval comparison delta。

### 作用是什么

`REAL_PROVIDER_SMOKE_GUIDE.md` 解决的是“真实 provider 怎么安全验证”的问题。真实服务需要 key、网络、额度和模型名，因此不能默认进 pytest。手动 smoke guide 让你可以在本机 `.env` 中填真实配置，然后人工验证完整 RAG API 链路。

eval provider comparison 解决的是“真实 provider 接入后怎么和本地 baseline 对比”的问题。它先比较学习阶段最重要的三个信号：

```text
answer 是否命中预期
citation 是否仍然正确
refusal 是否被破坏
```

它不是生产级 benchmark，但足够帮助后续判断真实 embedding / LLM provider 是否让输出变好、变差或发生行为漂移。

### 当前链路位置

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
-> OpenAI-compatible providers
-> real provider manual smoke guide
-> eval provider comparison  <-- 当前已完成
```

### 验证结果

普通权限运行：

```powershell
uv run pytest
```

先因本机 `uv` cache 权限失败。按环境规则提升权限后，同一条命令通过：

```text
136 passed
```

### 下一步建议

下一步建议：

```text
real provider smoke execution notes
```

或者：

```text
provider quality tuning
```

前者记录一次真实 provider 手动 smoke 的实际结果；后者基于 `EvalComparisonReport` 开始调整 provider、prompt、eval case 或 refusal threshold。仍然不建议跳到 UI、Workbench、MCP、LangGraph 或多 agent。

## 2026-06-04 进度更新：real provider planning + OpenAI-compatible providers

本次一次推进了两个连续任务：

```text
real provider planning
-> OpenAI-compatible provider adapters
```

项目现在已经从“本地文件/目录可导入的 disk-backed RAG 服务”，推进到“默认离线、显式配置后可接 OpenAI-compatible embedding 和 chat completion provider”的阶段。

当前完整链路是：

```text
Markdown/TXT file or directory
-> load_text_file() / load_directory()
-> SourceDocument
-> DocumentChunk
-> EmbeddingProvider
   -> LocalHashEmbeddingProvider by default
   -> OpenAICompatibleEmbeddingProvider when configured
-> InMemoryVectorStore
-> LocalRetrievalPipeline.search()
-> MinimumEvidenceRefusalPolicy
-> AnswerGenerator
   -> CitationAwareAnswerGenerator by default
   -> LLMBackedCitationAwareAnswerGenerator when configured
-> LocalAnswerPipeline.answer()
-> GeneratedAnswer(text, citations, refused)
-> POST /answer or knowledge base answer API
-> pytest
```

### 本步做了什么

- 新增真实 provider 规划配置：
  - `EMBEDDING_PROVIDER`
  - `ANSWER_GENERATOR`
  - `OPENAI_COMPATIBLE_API_KEY`
  - `OPENAI_COMPATIBLE_BASE_URL`
  - `OPENAI_COMPATIBLE_EMBEDDING_MODEL`
  - `OPENAI_COMPATIBLE_CHAT_MODEL`
- 新增 `OpenAICompatibleEmbeddingProvider`，调用 OpenAI-compatible `/embeddings`。
- 新增 `OpenAICompatibleLLMProvider`，调用 OpenAI-compatible `/chat/completions`。
- 新增 `LLMBackedCitationAwareAnswerGenerator`，用 LLM 生成回答正文，但 citation 仍由本地 evidence metadata 生成。
- 新增 `create_embedding_provider(settings)` 和 `create_answer_generator(settings)`。
- 更新 `create_app()`，让 `/answer`、disk-backed knowledge base、file/directory import 后的 answer pipeline 都能使用 settings 注入的 provider。
- 把 `httpx` 提升为运行时依赖，因为真实 provider adapter 在应用运行时需要 HTTP client。
- 新增 mocked provider tests，不在 pytest 中调用真实网络。

### 作用是什么

之前的 `LocalHashEmbeddingProvider` 是一个本地替代实现。它用 `sha256` 和 token bag-of-words 把文本变成固定维度向量，优点是离线、确定性、无外部依赖，适合学习 retrieval 和 metadata preservation；缺点是它不是真实语义 embedding，不适合声明为生产级检索质量。

现在新增 `OpenAICompatibleEmbeddingProvider` 后，embedding 这一步可以在显式配置后变成真实模型向量：

```text
text
-> /embeddings
-> semantic vector
```

之前的 `CitationAwareAnswerGenerator` 也是 deterministic generator。它不会调用真实 LLM，只根据 retrieval evidence 拼出一个稳定回答，适合测试 citation、refusal 和 eval；缺点是表达能力有限。

现在新增 `LLMBackedCitationAwareAnswerGenerator` 后，回答正文可以由真实 LLM 生成。但 citation 仍然不能让模型自由编。原因是模型可能输出看起来像来源、但实际不存在的 citation。项目继续把 citation authority 放在本地：

```text
RetrievalResult.chunk.metadata
-> source_path#chunk-{chunk_index}
-> GeneratedAnswer.citations
```

### 如何开启真实 provider

默认情况下不需要配置真实 key，项目仍然使用本地 provider。

如需本地手动开启真实 provider，在本机 `.env` 中配置：

```text
EMBEDDING_PROVIDER=openai_compatible
ANSWER_GENERATOR=openai_compatible
OPENAI_COMPATIBLE_API_KEY=your-api-key
OPENAI_COMPATIBLE_BASE_URL=your-openai-compatible-base-url
OPENAI_COMPATIBLE_EMBEDDING_MODEL=your-embedding-model
OPENAI_COMPATIBLE_CHAT_MODEL=your-chat-model
```

注意：

- 真实 API key 只放本地 `.env`。
- 不要写入 README、learning.md、测试或代码。
- pytest 不会请求真实服务。
- `/health` 不需要模型凭证。

### 本次没有做什么

- 没有做真实服务自动 smoke test。
- 没有把真实 key 写入仓库。
- 没有做 provider retry、timeout、rate limit、cost 统计。
- 没有接 Chroma、Qdrant、pgvector。
- 没有做 rerank。
- 没有做 streaming response。
- 没有做 UI、MCP、LangGraph、多 agent。

### 验证结果

普通权限运行：

```powershell
uv run pytest
```

先因本机 `uv` cache 权限失败。按环境规则提升权限后，使用同一条命令通过：

```text
127 passed
```

### 当前项目位置

当前 `agentic-rag-lab` 位于：

```text
file / directory import API
-> real provider planning
-> OpenAI-compatible provider adapters  <-- 当前已完成
```

下一步建议：

```text
real provider manual smoke guide
```

或者：

```text
expand eval dataset/report for real-provider comparison
```

也就是说，下一步可以写一份安全的本地手动验证指南，说明如何用 `.env` 配置真实服务并手动跑一个小例子；或者扩展 eval，让本地 deterministic provider 和真实 provider 的输出可以被并排比较。仍然不建议跳到 UI、Workbench、MCP、LangGraph 或多 agent。

# agentic-rag-lab

`agentic-rag-lab` 是 `D:\zrf\aiProject` 里三个 AI Agent 学习项目的第一个项目。

它的目标不是做一个普通聊天机器人，而是一步一步做出一个可靠的 RAG 知识库系统。当前重点是先把“文档如何进入系统、如何被切分、如何被检索、如何生成带来源回答”这些基础能力学扎实，再考虑 Agent Loop、MCP、多 agent 或 UI。

## 当前项目状态

当前已经完成到本机文件/目录可导入的磁盘知识库问答闭环：

```text
Markdown/TXT 文件
-> POST /knowledge-bases/from-file 或 /from-directory
-> SourceDocument
-> DocumentChunk
-> LocalHashEmbeddingProvider
-> InMemoryVectorStore
-> LocalRetrievalPipeline.search()
-> RetrievalResult
-> CitationAwareAnswerGenerator.answer()
-> GeneratedAnswer
-> POST /answer
-> POST /knowledge-bases
-> POST /knowledge-bases/{knowledge_base_id}/answer
-> local JSON files
-> app restart recovery
-> pytest 验证
```

已经实现：

- FastAPI 应用入口。
- `/health` 健康检查接口，不需要模型凭证。
- 基于 `.env` 的配置读取。
- 已提交 `.env.example`，真实密钥不进仓库。
- LLM provider 抽象层。
- 离线可用的 `fake` provider。
- RAG 分层目录：`ingestion`、`chunking`、`retrieval`、`generation`、`evals`、`knowledge_base`。
- Markdown/TXT 文档导入到 `SourceDocument`。
- 目录递归导入支持的文本文件。
- 字符窗口切分到 `DocumentChunk`。
- chunk id 和 metadata 都是确定性的，方便测试和后续引用。
- 本地 hash embedding。
- 内存向量检索。
- 内部 retrieval pipeline。
- 确定性 citation-aware answer generation。
- 空 evidence 时的最小拒答保护。
- 内部 answer pipeline。
- 基础 refusal policy。
- 本地 eval dataset / eval report。
- `POST /answer` HTTP answer API boundary。
- `POST /knowledge-bases` 和 `POST /knowledge-bases/{knowledge_base_id}/answer` 进程内知识库 API。
- `POST /knowledge-bases/from-file` 本机文件路径导入 API。
- `POST /knowledge-bases/from-directory` 本机目录路径导入 API。
- JSON 文件持久化的本地知识库 registry。
- app 重启后从本地 JSON 恢复知识库并重建 answer pipeline。
- pytest 覆盖 health、ingestion、chunking、embedding、retrieval、retrieval pipeline、citation generation、answer pipeline、refusal、eval、HTTP answer API、knowledge base API、file/directory import API、disk-backed registry、本地端到端闭环。

还没有实现：

- PDF 导入。
- 真实 embedding provider。
- 生产型 vector store。
- rerank。
- 复杂拒答策略。
- 生产级 RAG eval 报告。
- multipart 浏览器文件上传。
- Web UI。
- LangGraph / Agent Loop。
- MCP 集成。

## 为什么先做这个项目

RAG 是后面两个项目的基础。

如果模型不能稳定拿到正确上下文，后面做 `ai-agent-workbench` 或 `mcp-devtools-server` 时，就会变成“工具能调用，但模型不知道该相信什么”。所以当前阶段先解决这些问题：

- 文档如何读取。
- 文档如何保留来源。
- 文档如何切成可检索片段。
- 后续如何通过 metadata 追溯引用来源。
- 如何用测试证明这些行为稳定。

## 核心代码结构

```text
src/agentic_rag_lab/
├── api/          # FastAPI 路由
├── chunking/     # 文档切分
├── embeddings/   # 本地 embedding provider 边界
├── evals/        # 本地 eval 边界
├── generation/   # 回答生成和 citation 边界
├── ingestion/    # Markdown/TXT 文档导入
├── knowledge_base/ # 本地知识库 registry 和磁盘持久化
├── llm/          # 模型 provider 抽象和 fake provider
├── retrieval/    # 本地向量检索和 retrieval pipeline
├── config.py     # 环境配置
├── main.py       # FastAPI app 工厂
└── schemas.py    # 共享数据结构
```

当前最重要的数据结构在 `schemas.py`：

- `SourceDocument`：导入后的原始文档。
- `DocumentChunk`：切分后的文档片段。
- `RetrievalResult`：未来检索返回的 chunk 和分数。
- `GeneratedAnswer`：未来生成的答案、引用和拒答状态。

## 本地运行

前置要求：

- Python 3.12+
- `uv`

安装依赖：

```powershell
uv sync
```

创建本地配置：

```powershell
Copy-Item .env.example .env
```

`.env` 已被 git 忽略。以后接真实模型 provider 时，密钥只放在本地 `.env`。

启动 API：

```powershell
uv run uvicorn agentic_rag_lab.main:app --reload
```

健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

运行测试：

```powershell
uv run pytest
```

当前验证结果：

```text
108 passed
```

说明：这台机器在普通权限下可能会因为 `C:\Users\admin\AppData\Local\uv\cache` 权限导致 `uv run pytest` 在启动 pytest 前失败。本次最终验证是用同一个命令在提升权限后通过的。

## 本地文本导入和切分示例

```python
from agentic_rag_lab.ingestion import load_text_file
from agentic_rag_lab.chunking import chunk_document

document = load_text_file("docs/example.md")
chunks = chunk_document(document, chunk_size=800, overlap=100)
```

当前支持：

- `.md`
- `.txt`

导入时会保留：

- `source_path`
- `file_name`
- `file_type`

切分时会继续保留来源 metadata，并新增：

- `chunk_index`
- `start`
- `end`

这一步的意义是：后续生成答案时，可以知道每个 chunk 来自哪个文件、哪个位置，从而做 citation。

## Trellis 学习工作流

这个仓库使用 Trellis 来保证每次开发都留下学习资料，而不是只留下代码。

主要入口：

- `AGENTS.md`：给 Codex/Cursor 的项目级指引。
- `.trellis/workflow.md`：Trellis 阶段、任务和上下文规则。
- `.trellis/spec/`：长期规范和可复用知识。
- `.trellis/tasks/`：当前任务和已归档任务。
- `.trellis/workspace/`：本地工作日志。
- `docs/TECHNICAL_NOTES.md`：本项目的学习型技术文档。

当前没有 active task：

```powershell
$py = 'C:\Users\admin\AppData\Roaming\uv\python\cpython-3.12.12-windows-x86_64-none\python.exe'
& $py .\.trellis\scripts\task.py current --source
```

已完成并归档的关键任务：

- `05-25-bootstrap-rag-mvp-skeleton`：项目骨架。
- `05-28-add-markdown-txt-ingestion-chunking`：Markdown/TXT 导入和切分。

## 你现在应该怎么继续

下一步不要开新项目，也不要急着做 UI、MCP 或多 agent 产品功能。

现在应该继续做第一个项目的下一块：

```text
real provider planning
```

这一步要学习的是：

- 为什么现在可以开始设计真实模型 provider。
- 如何把真实 embedding / LLM provider 接到已有边界，而不是推倒 RAG 链路。
- 如何处理 API key、`.env`、mock 测试和 eval 波动。
- 为什么仍然不急着接 UI、MCP 或多 agent。

建议你下一次直接这样对我说：

```text
继续 agentic-rag-lab，下一个任务做 real provider planning。
请使用学习型 Trellis harness，先更新 PRD 和学习目标，再实现最小可运行闭环。
```

我会按 Trellis 流程做：

1. 创建新 task。
2. 写 PRD，说明这次学什么、为什么现在做、什么不做。
3. 选择最小实现方案。
4. 必要时使用多 agent。
5. 实现代码和测试。
6. 写 `learning.md`。
7. 更新长期 spec。
8. 跑测试。
9. 提交并归档任务。

## 后续路线

建议顺序：

1. real provider planning。
2. real embedding provider adapter。
3. 再考虑 `ai-agent-workbench`。
4. 最后做 `mcp-devtools-server`。

每一步都要形成一个小闭环，不要一次把所有能力堆上去。
## 2026-06-03 进度更新

本地 embedding 和内存向量检索切片已经实现：

```text
DocumentChunk
-> LocalHashEmbeddingProvider
-> InMemoryVectorStore
-> query embedding
-> list[RetrievalResult]
-> pytest
```

当前实现细节：

- `agentic_rag_lab.embeddings.LocalHashEmbeddingProvider` 会生成确定性、离线的 hash embedding。
- `agentic_rag_lab.retrieval.InMemoryVectorStore` 会按 cosine score 给 chunks 排序，并返回 `RetrievalResult`。
- 当前实现不调用外部 embedding provider，也不使用生产型向量数据库。
- 本次验证结果是 `31 passed`。

下一步建议任务：

```text
persistent local knowledge base。
```

下一步仍然不做：拒答、eval report、Web UI、LangGraph、MCP 和多 agent 编排。

## 2026-06-03 进度更新：retrieval pipeline

basic retrieval pipeline / API boundary 已经实现：

```text
SourceDocument
-> DocumentChunk
-> InMemoryVectorStore
-> LocalRetrievalPipeline.search()
-> list[RetrievalResult]
-> pytest
```

当前实现细节：

- `agentic_rag_lab.retrieval.LocalRetrievalPipeline` 可以从 `DocumentChunk` 列表构建。
- `LocalRetrievalPipeline.from_documents()` 可以从 `SourceDocument` 列表构建，并内部完成 chunking。
- `search(query, limit=5)` 会返回 `RetrievalResult`，继续保留 chunk metadata。
- 本次验证结果是 `37 passed`。

HTTP answer API boundary、persistent local knowledge base、disk-backed local knowledge base 和 file / directory import API 都已经完成。当前下一步建议任务：

```text
real provider planning。
```

## 2026-06-03 进度更新：citation-aware answer generation

带引用回答生成已经实现：

```text
list[RetrievalResult]
-> CitationAwareAnswerGenerator.answer()
-> GeneratedAnswer(text, citations, refused)
-> pytest
```

这一步做了什么：

- 新增 `agentic_rag_lab.generation.CitationAwareAnswerGenerator`。
- 使用 `RetrievalResult.chunk.metadata` 生成 citation。
- citation 优先使用 `source_path#chunk-{chunk_index}`。
- metadata 不完整时回退到 `chunk.id`。
- 空 evidence 时返回 `refused=True`，不编造答案。

这一步的作用：

- 把 retrieval 的输出变成用户可用的回答结构。
- 让回答能追溯到原始文档片段。
- 为后续 refusal、eval 和真实 LLM generation 固定输出 contract。

本次使用的工具和模块：

- `GeneratedAnswer`
- `RetrievalResult`
- `DocumentChunk.metadata`
- `LocalRetrievalPipeline`
- `CitationAwareAnswerGenerator`
- `uv run pytest`

本次验证结果：

```text
44 passed
```

下一步建议任务：

```text
persistent local knowledge base。
```

## 2026-06-03 进度更新：answer pipeline / internal QA boundary

内部问答边界已经实现：

```text
question
-> LocalAnswerPipeline.answer()
-> LocalRetrievalPipeline.search()
-> CitationAwareAnswerGenerator.answer()
-> GeneratedAnswer
-> pytest
```

这一步做了什么：

- 新增 `agentic_rag_lab.generation.LocalAnswerPipeline`。
- 支持 `from_chunks()` 从已有 chunks 构建问答 pipeline。
- 支持 `from_documents()` 从 `SourceDocument` 构建问答 pipeline，并内部完成 chunking 和 retrieval。
- `answer(question, limit=5)` 会先检索 evidence，再生成带 citation 的 `GeneratedAnswer`。

这一步的作用：

- 把 retrieval 和 citation-aware generation 的组合收进一个内部 QA 边界。
- 让后续 HTTP endpoint、refusal、eval 不需要重复拼底层流程。
- 让项目从“两个可用能力”推进到“一条可调用问答链路”。

本次使用的工具和模块：

- `Retriever`
- `LocalRetrievalPipeline`
- `AnswerGenerator`
- `CitationAwareAnswerGenerator`
- `LocalAnswerPipeline`
- `GeneratedAnswer`
- `uv run pytest`

本次验证结果：

```text
50 passed
```

当前项目在整体链路中的位置：

```text
ingestion
-> chunking
-> embedding
-> retrieval
-> citation-aware generation
-> answer pipeline / internal QA boundary  <-- 当前已完成
-> refusal behavior
-> eval
```

下一步建议任务：

```text
persistent local knowledge base。
```

## 2026-06-03 进度更新：HTTP answer API boundary

最小 HTTP answer endpoint 已经实现：

```text
POST /answer
-> AnswerRequest
-> SourceDocument
-> LocalAnswerPipeline.from_documents()
-> LocalAnswerPipeline.answer()
-> AnswerResponse
-> pytest
```

这一步做了什么：

- 新增 `agentic_rag_lab.api.answer`。
- 新增 `POST /answer`。
- 新增 HTTP DTO：`AnswerDocument`、`AnswerRequest`、`AnswerResponse`。
- 在 `create_app()` 中注册 answer router。
- `ValueError` 会转换为 `400 Bad Request`。

这一步的作用：

- 把内部 RAG 闭环暴露成 HTTP 可调用服务。
- 让外部调用方可以通过请求直接获得 `text`、`citations` 和 `refused`。
- 为后续持久化知识库或真实 provider 留出 API 边界。

本次使用的工具和模块：

- FastAPI `APIRouter`
- Pydantic `BaseModel`
- `LocalAnswerPipeline`
- `SourceDocument`
- `TestClient`
- `uv run pytest`

本次验证结果：

```text
74 passed
```

当前项目在整体链路中的位置：

```text
ingestion
-> chunking
-> embedding
-> retrieval
-> citation-aware generation
-> answer pipeline / internal QA boundary
-> refusal behavior
-> eval dataset / eval report
-> HTTP answer API boundary  <-- 当前已完成
```

下一步建议任务：

```text
persistent local knowledge base。
```

## 2026-06-03 进度更新：eval dataset / eval report

本地 eval 闭环已经实现：

```text
EvalCase
-> LocalAnswerPipeline.answer()
-> GeneratedAnswer
-> answer/citation/refusal checks
-> EvalReport
-> pytest
```

这一步做了什么：

- 新增 `agentic_rag_lab.evals.EvalCase`。
- 新增 `EvalResult` 和 `EvalReport`。
- 新增 `run_eval_cases()`。
- 用 answer term、citation 和 refused 三类检查评估当前 RAG 输出。

这一步的作用：

- 把“手动试问题”推进为“可重复的本地评估”。
- 让 answer、citation、refusal 三类行为都有可检查结果。
- 为后续改 retrieval、refusal 或 generation 提供回归依据。

本次使用的工具和模块：

- `SourceDocument`
- `LocalAnswerPipeline`
- `GeneratedAnswer`
- `EvalCase`
- `EvalReport`
- `uv run pytest`

本次验证结果：

```text
65 passed
```

当前项目在整体链路中的位置：

```text
ingestion
-> chunking
-> embedding
-> retrieval
-> citation-aware generation
-> answer pipeline / internal QA boundary
-> refusal behavior
-> eval dataset / eval report  <-- 当前已完成
```

下一步建议任务：

```text
HTTP answer API boundary。
```

## 2026-06-03 进度更新：refusal behavior

基础拒答行为已经实现：

```text
question
-> LocalAnswerPipeline.answer()
-> LocalRetrievalPipeline.search()
-> MinimumEvidenceRefusalPolicy
-> GeneratedAnswer(refused=True/False)
-> pytest
```

这一步做了什么：

- 新增 `agentic_rag_lab.generation.MinimumEvidenceRefusalPolicy`。
- 新增 `RefusalPolicy` protocol。
- `LocalAnswerPipeline` 支持默认和自定义 refusal policy。
- 空 query、无 evidence、最高 score 低于 `0.25` 时返回 `refused=True`。
- 拒答时 citations 为空，避免展示未被接受的证据。

这一步的作用：

- 防止系统在证据不足时继续生成答案。
- 把“是否应该回答”的判断放在 retrieval 和 generation 中间。
- 为后续 eval dataset / eval report 提供可评估的 `refused` 输出。

本次使用的工具和模块：

- `GeneratedAnswer`
- `RetrievalResult`
- `LocalAnswerPipeline`
- `MinimumEvidenceRefusalPolicy`
- `RefusalPolicy`
- `uv run pytest`

本次验证结果：

```text
59 passed
```

当前项目在整体链路中的位置：

```text
ingestion
-> chunking
-> embedding
-> retrieval
-> citation-aware generation
-> answer pipeline / internal QA boundary
-> refusal behavior  <-- 当前已完成
-> eval
```

下一步建议任务：

```text
eval dataset / eval report。
```

## 2026-06-03 进度更新：persistent local knowledge base

进程内本地知识库已经实现：

```text
POST /knowledge-bases
-> documents
-> SourceDocument
-> DocumentChunk
-> LocalAnswerPipeline
-> InMemoryKnowledgeBaseRegistry

POST /knowledge-bases/{knowledge_base_id}/answer
-> LocalKnowledgeBase.answer()
-> GeneratedAnswer
-> AnswerResponse
```

这一步做了什么：

- 新增 `agentic_rag_lab.knowledge_base.LocalKnowledgeBase`。
- 新增 `agentic_rag_lab.knowledge_base.InMemoryKnowledgeBaseRegistry`。
- 新增 `src/agentic_rag_lab/api/knowledge_base.py`。
- 新增 `POST /knowledge-bases`。
- 新增 `POST /knowledge-bases/{knowledge_base_id}/answer`。
- `create_app()` 通过 `app.state.knowledge_bases` 初始化每个 app 实例自己的 registry。
- 保留现有 `POST /answer`，让临时 documents 问答模式继续可用。

这一步的作用：

- 让调用方不必每次提问都重新提交 documents。
- 把“问答 API”和“知识库管理 API”拆开。
- 在不引入数据库和向量库的前提下，先学习知识库生命周期边界。
- 继续复用已有 chunking、embedding、retrieval、citation、refusal 和 answer pipeline。

本次使用的工具和模块：

- FastAPI `APIRouter`
- FastAPI `app.state`
- Pydantic `BaseModel`
- `chunk_documents`
- `LocalAnswerPipeline`
- `SourceDocument`
- `GeneratedAnswer`
- `TestClient`
- `uv run pytest`

本次验证结果：

```text
90 passed
```

当前项目在整体链路中的位置：

```text
ingestion
-> chunking
-> embedding
-> retrieval
-> citation-aware generation
-> answer pipeline / internal QA boundary
-> refusal behavior
-> eval dataset / eval report
-> HTTP answer API boundary
-> persistent local knowledge base  <-- 当前已完成
```

注意：这里的 persistent 指 app 进程内跨请求复用，不是磁盘持久化。服务重启后知识库会丢失。

下一步建议任务：

```text
disk-backed local knowledge base
```

或者先做：

```text
real provider planning
```

## 2026-06-04 进度更新：file / directory import API

本机文件和目录导入 API 已经实现：

```text
POST /knowledge-bases/from-file
-> load_text_file()
-> SourceDocument
-> DiskBackedKnowledgeBaseRegistry
-> local JSON knowledge base

POST /knowledge-bases/from-directory
-> load_directory()
-> list[SourceDocument]
-> DiskBackedKnowledgeBaseRegistry
-> local JSON knowledge base
```

这一步做了什么：

- 新增 `POST /knowledge-bases/from-file`。
- 新增 `POST /knowledge-bases/from-directory`。
- 新增 `CreateKnowledgeBaseFromFileRequest`。
- 新增 `CreateKnowledgeBaseFromDirectoryRequest`。
- 继续复用 `CreateKnowledgeBaseResponse`。
- 复用已有 `load_text_file()` 和 `load_directory()`。
- 成功导入后继续写入 disk-backed knowledge base。

这一步的作用：

- 让调用方不必手写 documents JSON。
- 让本机 `.md` / `.txt` 文件可以直接进入知识库。
- 让本机目录可以递归导入支持的文本文件。
- 保留 `source_path`、`file_type`、`chunk_index`，让 citation 继续可追溯。

本次没有做浏览器 multipart upload。这里的 file import 指服务端本机可访问路径导入。

本次验证结果：

```text
108 passed
```

当前项目在整体链路中的位置：

```text
ingestion
-> chunking
-> embedding
-> retrieval
-> citation-aware generation
-> answer pipeline / internal QA boundary
-> refusal behavior
-> eval dataset / eval report
-> HTTP answer API boundary
-> persistent local knowledge base
-> disk-backed local knowledge base
-> file / directory import API  <-- 当前已完成
```

下一步建议任务：

```text
real provider planning
```

## 2026-06-03 进度更新：disk-backed local knowledge base

磁盘可恢复的本地知识库已经实现：

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

这一步做了什么：

- 新增 `agentic_rag_lab.knowledge_base.DiskBackedKnowledgeBaseRegistry`。
- 新增 `src/agentic_rag_lab/knowledge_base/disk.py`。
- 新增配置项 `knowledge_base_storage_path`。
- `.env.example` 增加 `KNOWLEDGE_BASE_STORAGE_PATH=.local/knowledge-bases`。
- `.gitignore` 忽略 `.local/`，避免本地知识库数据进仓库。
- `create_app()` 默认使用 disk-backed registry。
- 测试通过 `tmp_path` 验证 app recreate 后仍能用旧 knowledge base id answer。

这一步的作用：

- 让知识库不再只存在于 app 进程内。
- 让服务重启后可以恢复已创建知识库。
- 学习哪些数据应该保存到磁盘，哪些运行时对象应该重建。
- 为后续文件上传、目录导入和真实 provider 留出更稳定的本地知识库边界。

本次使用的工具和模块：

- `DiskBackedKnowledgeBaseRegistry`
- `LocalKnowledgeBase`
- `SourceDocument`
- `DocumentChunk`
- `LocalAnswerPipeline`
- `json`
- `Path.replace()`
- `Settings.knowledge_base_storage_path`
- `uv run pytest`

本次验证结果：

```text
98 passed
```

当前项目在整体链路中的位置：

```text
ingestion
-> chunking
-> embedding
-> retrieval
-> citation-aware generation
-> answer pipeline / internal QA boundary
-> refusal behavior
-> eval dataset / eval report
-> HTTP answer API boundary
-> persistent local knowledge base
-> disk-backed local knowledge base  <-- 当前已完成
```

下一步建议任务：

```text
real provider planning
```

或者先做：

```text
real provider planning
```
