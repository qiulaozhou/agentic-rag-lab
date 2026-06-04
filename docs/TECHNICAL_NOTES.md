## Resume-ready V1 技术总览

更新日期：2026-06-04

`agentic-rag-lab` 当前收口为 `Resume-ready V1`。技术上，它已经从 FastAPI skeleton 推进到一个可测试的 RAG 服务边界：

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

### 模块边界

| 边界 | 主要模块 | 设计约束 |
| --- | --- | --- |
| ingestion | `agentic_rag_lab.ingestion` | 只负责把本地 `.md` / `.txt` 输入转为 `SourceDocument`，并保留 `source_path`、`file_type` 等 metadata |
| chunking | `agentic_rag_lab.chunking` | 只负责稳定切分文档，输出 `DocumentChunk`，不关心 embedding 或 generation |
| embedding | `agentic_rag_lab.embeddings` | 默认使用本地 deterministic provider；OpenAI-compatible provider 只在显式配置时启用 |
| retrieval | `agentic_rag_lab.retrieval` | 负责 vector search 和 retrieval pipeline，返回保留 chunk metadata 的 `RetrievalResult` |
| generation | `agentic_rag_lab.generation` | 负责 citation-aware answer、LLM-backed answer、answer pipeline 和 refusal policy |
| eval | `agentic_rag_lab.evals` | 负责 deterministic eval 和 provider comparison，不复制 RAG pipeline 逻辑 |
| API | `agentic_rag_lab.api` | 只做 HTTP DTO、参数校验和边界调用，不重写检索、引用或拒答逻辑 |
| knowledge base | `agentic_rag_lab.knowledge_base` | 保存 documents/chunks/config，并重建 runtime pipeline |
| provider | `agentic_rag_lab.llm` | 封装 OpenAI-compatible `/chat/completions`，不让 route handler 直接调用真实 provider |

### citation 规则

回答中的 citation 不信任模型自由生成，而是固定从 retrieval evidence 的 metadata 派生：

```text
source_path#chunk-{chunk_index}
```

如果 metadata 不完整，则回退到稳定的 `chunk.id`。LLM-backed generator 只能生成 answer text，不能决定 citation 列表。

### refusal 规则

拒答发生在 retrieval 之后、generation 之前：

```text
question
-> retrieval evidence
-> MinimumEvidenceRefusalPolicy
-> answer generator or refused answer
```

默认规则用于学习阶段：

- 空 query 拒答。
- evidence 为空拒答。
- 最高分低于阈值拒答。
- 拒答时 `citations=[]`。

### provider 规则

默认 provider 是离线 deterministic：

```text
EMBEDDING_PROVIDER=local_hash
ANSWER_GENERATOR=local_citation
```

真实 provider 必须显式 opt-in：

```text
EMBEDDING_PROVIDER=openai_compatible
ANSWER_GENERATOR=openai_compatible
OPENAI_COMPATIBLE_API_KEY
OPENAI_COMPATIBLE_BASE_URL
OPENAI_COMPATIBLE_EMBEDDING_MODEL
OPENAI_COMPATIBLE_CHAT_MODEL
```

pytest 不调用真实 provider。OpenAI-compatible adapter 测试使用 mocked HTTP transport。

### eval 规则

当前 eval 只检查学习阶段最重要的三个信号：

```text
answer 是否包含预期信息
citation 是否命中预期来源
refusal 是否符合预期
```

`EvalComparisonReport` 用于比较 baseline 和 candidate provider 的差异，delta 语义是：

```text
candidate - baseline
```

它不是生产级 benchmark，不包含 latency、cost、token usage、LLM judge 或长期趋势。

### 收口验证结果

本次 V1 收口新增了文档完整性测试，检查 README、技术笔记、学习索引、项目展示文档和根目录学习笔记是否明确当前阶段、完整链路、下一主线和 secret 安全边界。

最终验证：

```text
普通权限运行 `uv run pytest` 先因本机 uv cache 权限失败；
提升权限运行同一命令后通过：139 passed。
```

### V1 边界

当前系统已经足够作为简历中的 RAG 工程项目，但还不是生产级 RAG 系统。未做内容包括生产级 vector database、复杂文档解析、rerank、streaming、auth、UI、LangGraph、MCP 和多 agent 编排。

---

## 2026-06-04 更新：real provider manual smoke guide + eval provider comparison

本次新增两类能力：真实 provider 手动 smoke 指南，以及 eval provider comparison。

### Manual smoke guide

新增：

```text
docs/REAL_PROVIDER_SMOKE_GUIDE.md
```

它说明如何在本机 `.env` 中配置：

```text
EMBEDDING_PROVIDER=openai_compatible
ANSWER_GENERATOR=openai_compatible
OPENAI_COMPATIBLE_API_KEY
OPENAI_COMPATIBLE_BASE_URL
OPENAI_COMPATIBLE_EMBEDDING_MODEL
OPENAI_COMPATIBLE_CHAT_MODEL
```

并手动验证：

```text
GET /health
POST /answer
POST /knowledge-bases
POST /knowledge-bases/{knowledge_base_id}/answer
POST /knowledge-bases/from-file
```

真实 provider smoke 不进入 pytest。原因是它依赖真实 key、网络、额度和模型名；这些属于本地人工验证条件，不属于默认自动化回归条件。

### Eval provider comparison

`agentic_rag_lab.evals` 现在保留原有入口：

```python
run_eval_cases(cases, chunk_size, overlap=0)
```

同时新增 provider-aware 入口：

```python
run_eval_cases_with_pipeline_factory(
    cases,
    chunk_size,
    overlap=0,
    pipeline_factory=...
)
```

也可以使用命名配置：

```python
EvalRunConfig(
    label="candidate",
    chunk_size=400,
    overlap=0,
    pipeline_factory=...
)
```

对比方式：

```python
comparison = compare_eval_reports(
    "local",
    baseline_report,
    "candidate",
    candidate_report,
)
```

`EvalComparisonReport` 会记录：

- baseline label
- candidate label
- baseline report
- candidate report
- total cases
- passed delta
- answer passed delta
- citation passed delta
- refusal passed delta
- changed case ids

delta 的含义是：

```text
candidate - baseline
```

例如 `answer_passed_delta=-1` 表示 candidate 比 baseline 少通过 1 条 answer 检查。

### 为什么先比较 answer/citation/refusal

当前学习阶段最重要的不是复杂 benchmark，而是确认真实 provider 有没有破坏 RAG 的基本可靠性：

- answer 是否仍包含预期信息。
- citation 是否仍命中本地来源。
- refusal 是否仍在证据不足时触发。

这些信号与当前项目的工程边界直接对应，也能被 deterministic tests 覆盖。

### 当前限制

`EvalComparisonReport` 不是生产级 RAG benchmark。它暂时不包含：

- latency
- cost
- token usage
- LLM judge
- 长期趋势
- 大规模评测集

这些可以在真实 provider smoke 和基础 comparison 稳定后再加。

### 验证结果

最终验证：

```powershell
uv run pytest
```

普通权限先因本机 `uv` cache 权限失败；提升权限后同一命令通过：

```text
136 passed
```

### 下一步

建议下一步做：

```text
real provider smoke execution notes
```

或者：

```text
provider quality tuning
```

前者把一次真实 provider 手动 smoke 的实际结果记录下来；后者开始用 eval comparison 的结果指导 provider、prompt、eval case 或 refusal threshold 调整。

## 2026-06-04 更新：real provider planning + OpenAI-compatible providers

本次把项目从纯本地 deterministic RAG 闭环推进到“可选真实 provider”阶段。默认行为仍然离线，只有显式设置 provider 环境变量时才会调用 OpenAI-compatible 服务。

### 新增模块

| 模块 | 职责 |
| --- | --- |
| `agentic_rag_lab.embeddings.openai_compatible` | 调用 OpenAI-compatible `/embeddings`，把文本转成真实 embedding vector |
| `agentic_rag_lab.embeddings.factory` | 根据 `Settings.embedding_provider` 创建本地或 OpenAI-compatible embedding provider |
| `agentic_rag_lab.llm.openai_compatible` | 调用 OpenAI-compatible `/chat/completions`，通过 `LLMProvider` protocol 返回文本 |
| `agentic_rag_lab.generation.llm_backed` | 使用 LLM 生成 answer text，但 citation 仍由本地 evidence metadata 生成 |
| `agentic_rag_lab.generation.factory` | 根据 `Settings.answer_generator` 创建本地 deterministic generator 或 LLM-backed generator |

### 配置边界

新增配置项：

```text
EMBEDDING_PROVIDER=local_hash | openai_compatible
ANSWER_GENERATOR=local_citation | openai_compatible
OPENAI_COMPATIBLE_API_KEY
OPENAI_COMPATIBLE_BASE_URL
OPENAI_COMPATIBLE_EMBEDDING_MODEL
OPENAI_COMPATIBLE_CHAT_MODEL
```

默认值保持：

```text
EMBEDDING_PROVIDER=local_hash
ANSWER_GENERATOR=local_citation
LLM_PROVIDER=fake
```

这样做的原因是：学习项目必须保证不配置真实 key 也能运行和测试。真实 provider 是增强能力，不是默认前提。

### LocalHashEmbeddingProvider 的定位

`LocalHashEmbeddingProvider` 不是生产 embedding 模型。它的作用是：

- 离线运行。
- 不依赖 API key。
- 输出确定性向量。
- 让 retrieval、ranking、metadata preservation 和 citation 先被测试覆盖。

它的不足是：hash bag-of-words 不理解真实语义，因此不能代表真实 embedding 检索质量。

### OpenAICompatibleEmbeddingProvider 改变了什么

OpenAI-compatible embedding provider 替换的是这一段：

```text
text
-> embedding vector
```

它不改变：

- `SourceDocument`
- `DocumentChunk`
- `RetrievalResult`
- `InMemoryVectorStore`
- retrieval sorting contract
- citation metadata contract

也就是说，真实 embedding provider 是 adapter，不是重写 RAG 系统。

### CitationAwareAnswerGenerator 的定位

`CitationAwareAnswerGenerator` 是 deterministic generator。它不调用真实 LLM，只把 evidence 摘要拼成回答，并生成本地 citation。

它的作用是：

- 让 answer pipeline 可以离线测试。
- 让 citation 规则先稳定下来。
- 让 refusal 和 eval 可以在没有真实模型时运行。

它的不足是：回答表达能力有限，不具备真实 LLM 的语言生成能力。

### LLMBackedCitationAwareAnswerGenerator 改变了什么

LLM-backed generator 替换的是这一段：

```text
retrieved evidence
-> answer text
```

它不替换 citation 规则。citation 仍然来自：

```text
RetrievalResult.chunk.metadata["source_path"]
RetrievalResult.chunk.metadata["chunk_index"]
```

原因是模型生成的 citation 字符串不可信。即使模型正文中写了 `fake.md#chunk-99`，最终 `GeneratedAnswer.citations` 也只会使用本地 evidence 生成的来源。

### Provider 注入路径

当前注入路径是：

```text
Settings
-> create_embedding_provider(settings)
-> create_answer_generator(settings)
-> create_app(settings)
-> app.state.embedding_provider
-> app.state.answer_generator
-> LocalAnswerPipeline.from_documents/from_chunks
```

`POST /answer` 和 knowledge base registry 都复用这条路径。API route 不直接知道 `/embeddings` 或 `/chat/completions` 的 HTTP 细节。

### 错误和测试策略

OpenAI-compatible provider 需要以下配置：

- API key
- base URL
- model name

缺少配置时抛出 `ValueError`，而不是在请求时隐式失败。

测试策略：

- 使用 `httpx.MockTransport`。
- 检查请求体包含 `model`、`input` 或 `messages`。
- 检查非 2xx 响应会转成明确错误。
- 检查 malformed response 会转成明确错误。
- 不在 pytest 中访问真实网络。

### 验证结果

本次最终验证：

```powershell
uv run pytest
```

普通权限先因本机 `uv` cache 权限失败；提升权限后同一命令通过：

```text
127 passed
```

### 下一步

建议下一步做：

```text
real provider manual smoke guide
```

或者：

```text
expand eval dataset/report for real-provider comparison
```

前者解决“如何安全地用本地 `.env` 手动验证真实服务”；后者解决“真实 provider 输出如何和本地 deterministic baseline 对比”。当前仍不建议跳到 UI、MCP、LangGraph、Workbench 或多 agent。

# agentic-rag-lab Technical Notes

更新时间：2026-06-03

`agentic-rag-lab` 是三个 AI Agent 学习项目里的第一个项目。它的目标不是做一个普通聊天接口，而是做一个可靠的知识库问答系统，重点练习 RAG 的工程链路：

```text
文档导入
-> 文档切分
-> embedding
-> 检索
-> rerank
-> 回答生成
-> 引用来源
-> 拒答
-> eval
```

当前项目已经从 MVP skeleton 推进到本机文件/目录可导入的磁盘知识库问答闭环：Markdown/TXT 文档可以通过 HTTP 指定本机文件路径或目录路径导入成 `SourceDocument`，切成 `DocumentChunk`，通过本地 embedding 和内存向量检索返回 `RetrievalResult`，再生成带 citation 的 `GeneratedAnswer`，并保存到本地 JSON，app 重启后可以恢复。它还没有实现真实 LLM、生产型向量数据库、rerank、复杂拒答策略、multipart 浏览器上传和生产级 eval。

## 当前已完成内容

代码已经完成这些基础设施：

| 能力 | 当前实现 | 作用 |
| --- | --- | --- |
| FastAPI app | `src/agentic_rag_lab/main.py` | 创建应用并注册 router |
| health endpoint | `src/agentic_rag_lab/api/health.py` | 提供无需模型凭证的 smoke check |
| answer endpoint | `src/agentic_rag_lab/api/answer.py` | 通过 `POST /answer` 暴露最小 RAG 问答 API |
| knowledge base endpoint | `src/agentic_rag_lab/api/knowledge_base.py` | 暴露创建、导入和基于知识库问答的 HTTP API |
| settings | `src/agentic_rag_lab/config.py` | 从环境变量和 `.env` 读取配置 |
| `.env.example` | `.env.example` | 给后续真实 provider 留配置入口，不提交 secrets |
| domain schemas | `src/agentic_rag_lab/schemas.py` | 定义文档、chunk、检索结果、生成答案的数据形状 |
| LLM boundary | `src/agentic_rag_lab/llm/base.py` | 用 protocol 隔离模型调用接口 |
| fake provider | `src/agentic_rag_lab/llm/fake.py` | 本地离线测试用，不依赖真实模型 |
| provider factory | `src/agentic_rag_lab/llm/factory.py` | 根据 settings 创建 provider |
| module boundaries | `ingestion`、`chunking`、`retrieval`、`generation`、`evals` | 先把后续功能边界留出来 |
| Markdown/TXT ingestion | `src/agentic_rag_lab/ingestion/text.py` | 把 UTF-8 `.md` / `.txt` 文件转成 `SourceDocument` |
| text chunking | `src/agentic_rag_lab/chunking/text.py` | 用确定性的字符窗口把文档切成 `DocumentChunk` |
| local embedding | `src/agentic_rag_lab/embeddings/local.py` | 用确定性 hash embedding 把 chunk 转成向量 |
| in-memory vector retrieval | `src/agentic_rag_lab/retrieval/vector.py` | 在内存中按 cosine score 检索相关 chunk |
| retrieval pipeline | `src/agentic_rag_lab/retrieval/pipeline.py` | 把 chunking 和 vector store 组合成内部检索边界 |
| citation generation | `src/agentic_rag_lab/generation/citation.py` | 把 `RetrievalResult` 转成带 citation 的 `GeneratedAnswer` |
| answer pipeline | `src/agentic_rag_lab/generation/pipeline.py` | 把 retrieval 和 citation-aware generation 组合成内部问答边界 |
| refusal policy | `src/agentic_rag_lab/generation/refusal.py` | 在 evidence 不足时阻止答案生成 |
| local eval | `src/agentic_rag_lab/evals/basic.py` | 用小型 deterministic cases 评估 answer、citation 和 refusal |
| local knowledge base | `src/agentic_rag_lab/knowledge_base/local.py` | 在 FastAPI app 进程内保存可复用的本地知识库和 answer pipeline |
| disk-backed knowledge base | `src/agentic_rag_lab/knowledge_base/disk.py` | 把本地知识库保存为 JSON 文件，并在 app 启动时恢复 |
| tests | `tests/` | 覆盖 health、ingestion、chunking、embedding、retrieval、generation、answer pipeline、refusal、eval、answer API、knowledge base API、file/directory import API 和 disk-backed registry |

验证命令：

```powershell
uv run pytest
```

实现阶段记录的成功结果：

```text
108 passed
```

本机普通权限下如果 `uv` 无法访问
`C:\Users\admin\AppData\Local\uv\cache`，该命令会在 pytest 启动前失败；以
本次 check worker 的实际输出为准。

## 代码结构解释

当前源码结构：

```text
src/agentic_rag_lab/
├── api/
├── chunking/
├── evals/
├── generation/
├── ingestion/
├── knowledge_base/
├── llm/
├── retrieval/
├── config.py
├── main.py
└── schemas.py
```

这些目录仍然按 RAG 层次拆开。当前已经实现 ingestion、chunking、embedding、retrieval 和 citation-aware generation 的本地确定性闭环；evals 仍保持边界状态。

### `main.py`

`main.py` 负责创建 FastAPI app：

```text
Settings
-> create_app
-> include health router
-> expose app
```

这里采用 `create_app(settings=None)` 的形式，方便测试时传入自定义配置，也方便以后扩展依赖注入。

### `config.py`

`Settings` 继承自 `pydantic_settings.BaseSettings`，会从环境变量和 `.env` 读取配置。

当前配置项：

```text
app_name
app_env
log_level
llm_provider
knowledge_base_storage_path
```

`llm_provider` 目前只允许 `"fake"`，这是为了保证本地 smoke test 不需要真实 API key。

后续接真实 provider 时，可以扩展为：

```text
fake
openai
azure_openai
local
```

但不要太早扩展。当前阶段先保持 fake provider，直到需要真实生成能力。

### `schemas.py`

这里定义的是 RAG 主链路的核心数据结构。

`SourceDocument`：

```text
导入后的原始文档
```

字段：

- `id`：文档唯一标识。
- `text`：解析后的纯文本。
- `metadata`：来源信息，例如路径、标题、文件类型。

`DocumentChunk`：

```text
切分后的文档片段
```

字段：

- `id`：chunk 唯一标识。
- `document_id`：来源文档 id。
- `text`：chunk 文本。
- `metadata`：来源路径、chunk index、起止位置等。

`RetrievalResult`：

```text
检索返回的 chunk + 分数
```

字段：

- `chunk`：命中的 `DocumentChunk`。
- `score`：检索分数。

`GeneratedAnswer`：

```text
最终回答
```

字段：

- `text`：回答文本。
- `citations`：引用来源。
- `refused`：是否拒答。

这些 dataclass 是后续功能的连接点。retrieval 代码应该继续使用 `DocumentChunk` 和 `RetrievalResult`，不要重新发明一套数据形状。

### `llm/`

LLM 层现在有三个文件：

```text
base.py
factory.py
fake.py
```

`base.py` 定义请求、响应和 provider protocol：

```text
LLMRequest
LLMResponse
LLMProvider
```

这样做的价值是：业务逻辑不直接依赖某个模型 SDK。后续换 OpenAI、本地模型或 mock provider 时，不需要改 generation 主逻辑。

`fake.py` 里的 `FakeLLMProvider` 是离线 provider。它会把输入 prompt 包成固定格式返回，适合 smoke test。

`factory.py` 根据 settings 创建 provider。当前只支持 fake。

## 当前已经实现的本地数据链路

最小闭环已经是：

```text
本地 Markdown/TXT 文件
-> load_text_file / load_directory
-> SourceDocument
-> chunk_text / chunk_document / chunk_documents
-> list[DocumentChunk]
-> pytest 验证输出
```

### Ingestion 当前行为

`src/agentic_rag_lab/ingestion/text.py` 提供：

- `load_text_file(path)`：读取单个 UTF-8 `.md` 或 `.txt` 文件。
- `load_directory(path, extensions=None)`：递归读取目录下支持的文件，并按路径排序。

`SourceDocument.metadata` 至少包含：

- `source_path`
- `file_name`
- `file_type`

单文件遇到不支持扩展名会抛 `ValueError`。路径不存在会抛 `FileNotFoundError`。目录入口如果不是目录会抛 `NotADirectoryError`。

### Chunking 当前行为

`src/agentic_rag_lab/chunking/text.py` 提供：

- `chunk_text(text, chunk_size, overlap=0)`
- `chunk_document(document, chunk_size, overlap=0)`
- `chunk_documents(documents, chunk_size, overlap=0)`

当前策略是字符窗口切分：

- `chunk_size` 必须大于 0。
- `overlap` 必须满足 `0 <= overlap < chunk_size`。
- 空字符串或纯空白字符串返回空列表。
- chunk id 形如 `<document.id>:chunk-<index>`。
- chunk metadata 继承来源 metadata，并增加 `chunk_index`、`start`、`end`。

这个方案不理解 Markdown 语义，也不按 token 预算切分；它的价值是确定性、离线、容易测试，适合作为 embedding 和 retrieval 之前的第一步。

## 当前还没有实现的能力

README 里已经明确列出了未实现内容：

- PDF ingestion。
- Real embedding provider。
- Production vector storage。
- Rerank behavior。
- Real LLM answer generation。
- Complex refusal behavior。
- Production RAG evaluation reports。
- File upload and directory import API。

这些都不要误认为已经完成。现在完成的是离线、确定性、可测试的本地 RAG 闭环，不是生产级 RAG 系统。

### Ingestion 应该做什么

Ingestion 负责文件读取和解析。

第一版建议只支持：

- `.md`
- `.txt`

暂不支持 PDF。PDF 解析会引入页码、布局、表格、编码等问题，容易让当前任务变大。

当前接口：

```text
load_text_file(path) -> SourceDocument
load_directory(path, extensions={".md", ".txt"}) -> list[SourceDocument]
```

metadata 至少保留：

- `source_path`
- `file_name`
- `file_type`

后续做 citation 时，这些 metadata 可以直接成为引用来源。

### Chunking 应该做什么

Chunking 负责把 `SourceDocument.text` 切成多个 `DocumentChunk`。

第一版采用字符长度窗口，不引入复杂 tokenizer。

建议参数：

- `chunk_size`
- `overlap`

基本规则：

- chunk 文本不能为空。
- overlap 必须小于 chunk size。
- 每个 chunk 保留 `document_id`。
- metadata 里记录 `chunk_index`。
- 尽量保留原始 `source_path`。

### 为什么 chunking 重要

RAG 不能直接把完整文档丢给模型，原因有三个：

1. 上下文窗口有限。
2. 大量无关内容会降低回答质量。
3. 成本和延迟会随 token 增加而上升。

chunking 的目标是把文档拆成“刚好足够表达一个局部语义”的片段。

chunk 太小会丢上下文。chunk 太大会带来噪声。overlap 是折中手段，用来减少切断语义的问题。

## 后续路线

在 disk-backed local knowledge base 之后，建议继续按这个顺序推进：

1. Real provider planning。
2. Real embedding provider adapter。

不要跳过 eval。RAG 项目最有价值的地方不是“能问答”，而是能评估问答质量。

## 当前不做的事情

这些能力重要，但不是现在的下一步：

- PDF parsing：等 Markdown/TXT 稳定后再做。
- Chroma/Qdrant/pgvector 选型：等 chunk 输出稳定后再选。
- Real LLM provider：等 generation 层需要真实模型时再接。
- Rerank model：先有基本检索结果，再做 rerank。
- Web UI：API 和评估闭环未稳定前不做。
- LangGraph：当前还不是复杂 Agent Loop。
- MCP：属于第三个项目的能力。
- Multi-agent：当前任务没有复杂到需要多 agent。

## Trellis 学习记录

当前 Trellis 学习模式要求每个任务结束时写 `learning.md`。

已归档的骨架任务路径：

```text
.trellis/tasks/archive/2026-05/05-25-bootstrap-rag-mvp-skeleton/
```

已归档的 ingestion/chunking 任务路径：

```text
.trellis/tasks/archive/2026-05/05-28-add-markdown-txt-ingestion-chunking/
```

后续每个任务都应该留下类似记录，方便复习每一步为什么这样做。
## 2026-06-03 更新：本地 embedding 和向量检索

项目现在已经有了下一段本地 RAG 链路：

```text
DocumentChunk
-> local hash embedding
-> in-memory vector store
-> query embedding
-> RetrievalResult
```

### Embedding 行为

`src/agentic_rag_lab/embeddings/` 定义 embedding 边界。

- `EmbeddingProvider` 是协议。
- `LocalHashEmbeddingProvider` 是第一个离线实现。
- 它会把文本转成小写，用正则提取字母/数字/下划线 token，用 `sha256` 把 token 映射到固定维度的 bag-of-words 向量，并对非空向量做 L2 normalization。
- 空文本或没有 token 的文本会返回全零向量。

这个 provider 是为了确定性学习和测试，不是生产级语义 embedding 模型。

### Retrieval 行为

`src/agentic_rag_lab/retrieval/vector.py` 定义 `InMemoryVectorStore`。

- 它把 `DocumentChunk` 和本地 embedding 保存在内存里。
- `search(query, limit=5)` 会给 query 做 embedding，用 dot product 计算 cosine score，只保留正分结果，并按分数返回 `RetrievalResult`。
- 它会保留原始 chunk，包括 `document_id`，以及 `source_path`、`file_type`、`chunk_index` 等 metadata。

本阶段验证结果：

```text
31 passed
```

basic retrieval pipeline / API boundary、citation-aware answer generation、answer pipeline / internal QA boundary、refusal behavior、eval dataset / eval report、HTTP answer API boundary、persistent local knowledge base、disk-backed local knowledge base 和 file / directory import API 都已经完成。当前下一步可以做 real provider planning。不要直接跳到 UI、LangGraph、MCP 或多 agent 编排。

## 2026-06-03 更新：basic retrieval pipeline / API boundary

项目现在已经有了内部 retrieval pipeline：

```text
SourceDocument
-> chunk_documents
-> InMemoryVectorStore
-> LocalRetrievalPipeline.search()
-> list[RetrievalResult]
```

### Pipeline 行为

`src/agentic_rag_lab/retrieval/pipeline.py` 定义 `LocalRetrievalPipeline`。

- `from_chunks(chunks)` 可以从已有 `DocumentChunk` 构建 pipeline。
- `from_documents(documents, chunk_size, overlap=0)` 可以从 `SourceDocument` 构建 pipeline，并内部完成 chunking。
- `search(query, limit=5)` 委托给底层 `InMemoryVectorStore`。
- 空 query、`limit <= 0`、排序和 metadata 保留行为继续沿用 vector store。

这个 pipeline 的价值是把 chunking 和 vector store 的组合细节藏起来。后续 answer generation 只需要拿 `RetrievalResult`，不应该重新拼底层 retrieval 细节。

本阶段验证结果：

```text
37 passed
```

citation-aware answer generation 已经基于 `RetrievalResult` 完成，answer pipeline、refusal behavior、eval dataset / eval report、HTTP answer API boundary、persistent local knowledge base、disk-backed local knowledge base 和 file / directory import API 也已经完成。当前下一步可以做 `real provider planning`。

## 2026-06-03 更新：citation-aware answer generation

项目现在已经能把检索结果变成带来源的回答结构：

```text
LocalRetrievalPipeline.search()
-> list[RetrievalResult]
-> CitationAwareAnswerGenerator.answer()
-> GeneratedAnswer(text, citations, refused)
```

### 本步做了什么

新增 `src/agentic_rag_lab/generation/citation.py`，实现 `CitationAwareAnswerGenerator`。

它的输入是：

```text
question: str
evidence: list[RetrievalResult]
```

它的输出是：

```text
GeneratedAnswer
```

非空 evidence 时，生成器会：

- 取前 3 条 evidence。
- 归一化 chunk text。
- 把 evidence 摘要写入回答文本。
- 从 `DocumentChunk.metadata` 生成 citation。
- citation 去重并保持顺序。
- 返回 `refused=False`。

空 evidence 时，生成器会：

- 返回 `当前知识库没有足够依据回答这个问题。`
- citations 为空。
- `refused=True`。

### Citation 规则

citation 优先来自来源 metadata：

```text
source_path#chunk-{chunk_index}
```

例如：

```text
docs/rag.md#chunk-0
```

如果 `source_path` 或 `chunk_index` 缺失，则回退到稳定的 `chunk.id`。

这个规则的作用是让回答能追溯到原始文件和 chunk。它也为后续 eval 提供了可检查对象：eval 不仅能看答案文本，还能检查 citation 是否真的支持答案。

### 在整体流程中的定位

当前完整本地链路是：

```text
Markdown/TXT file
-> SourceDocument
-> DocumentChunk
-> LocalHashEmbeddingProvider
-> InMemoryVectorStore
-> LocalRetrievalPipeline.search()
-> RetrievalResult
-> CitationAwareAnswerGenerator.answer()
-> GeneratedAnswer
```

这一步解决的是“检索结果如何变成可追溯回答”。它还没有解决“证据是否足够”“答案质量是否正确”“citation 是否充分支持每句话”等问题。

### 验证结果

普通权限运行：

```powershell
uv run pytest
```

仍然因为本机 `uv` cache 权限失败。提升权限运行同一命令后通过：

```text
44 passed
```

answer pipeline / internal QA boundary、refusal behavior、eval dataset / eval report、HTTP answer API boundary 都已经完成。下一步建议做 `persistent local knowledge base`。

## 2026-06-03 更新：answer pipeline / internal QA boundary

项目现在已经有了内部问答入口：

```text
question
-> LocalAnswerPipeline.answer()
-> LocalRetrievalPipeline.search()
-> CitationAwareAnswerGenerator.answer()
-> GeneratedAnswer
```

### 本步做了什么

新增 `src/agentic_rag_lab/generation/pipeline.py`，实现 `LocalAnswerPipeline`。

它提供：

- `from_chunks(chunks)`：从已有 `DocumentChunk` 构建问答 pipeline。
- `from_documents(documents, chunk_size, overlap=0)`：从 `SourceDocument` 构建问答 pipeline。
- `answer(question, limit=5)`：返回 `GeneratedAnswer`。

### 作用是什么

上一阶段的调用方式是：

```text
retriever.search()
-> answer_generator.answer()
```

现在调用方只需要：

```text
answer_pipeline.answer()
```

这让后续 HTTP endpoint、refusal behavior 和 eval 都可以复用同一个内部问答入口。

### 输入输出

输入：

```text
question: str
limit: int = 5
```

输出：

```text
GeneratedAnswer(text, citations, refused)
```

### 在整体流程中的定位

当前完整本地链路是：

```text
Markdown/TXT file
-> SourceDocument
-> DocumentChunk
-> LocalHashEmbeddingProvider
-> InMemoryVectorStore
-> LocalRetrievalPipeline.search()
-> CitationAwareAnswerGenerator.answer()
-> LocalAnswerPipeline.answer()
-> GeneratedAnswer
```

answer pipeline 不改变检索排序、不改变 citation 规则、不接真实 LLM。它只是把已有 retrieval 和 generation 能力组合成更稳定的内部 QA 边界。

### 验证结果

普通权限运行 `uv run pytest` 仍然因为本机 `uv` cache 权限失败。提升权限运行同一命令后通过：

```text
50 passed
```

refusal behavior、eval dataset / eval report 和 HTTP answer API boundary 都已经完成。下一步建议做 `persistent local knowledge base`。

## 2026-06-03 更新：refusal behavior

项目现在已经有了基础拒答策略：

```text
question
-> LocalAnswerPipeline.answer()
-> LocalRetrievalPipeline.search()
-> MinimumEvidenceRefusalPolicy.should_refuse()
-> GeneratedAnswer(refused=True/False)
```

### 本步做了什么

新增 `src/agentic_rag_lab/generation/refusal.py`，实现：

- `RefusalPolicy`
- `MinimumEvidenceRefusalPolicy`
- `DEFAULT_REFUSAL_TEXT`
- `refused_answer()`

`LocalAnswerPipeline` 现在会在 retrieval 之后、generation 之前执行 refusal 判断。

### 作用是什么

RAG 不能在证据不足时继续生成答案。否则用户会看到一个带自然语言解释的回答，但这个回答可能没有足够 evidence 支持。

refusal policy 的作用是把“是否应该回答”变成一个明确、可测试、可替换的边界。

### 输入输出

输入：

```text
question: str
evidence: list[RetrievalResult]
```

默认规则：

```text
空 query -> 拒答
evidence 为空 -> 拒答
最高 score < 0.25 -> 拒答
最高 score >= 0.25 -> 允许生成
```

拒答输出：

```text
GeneratedAnswer(
    text="当前知识库没有足够依据回答这个问题。",
    citations=[],
    refused=True,
)
```

### 在整体流程中的定位

当前完整本地链路是：

```text
Markdown/TXT file
-> SourceDocument
-> DocumentChunk
-> LocalHashEmbeddingProvider
-> InMemoryVectorStore
-> LocalRetrievalPipeline.search()
-> MinimumEvidenceRefusalPolicy
-> CitationAwareAnswerGenerator.answer()
-> LocalAnswerPipeline.answer()
-> GeneratedAnswer
```

refusal behavior 发生在 retrieval 之后、generation 之前。

### 验证结果

普通权限运行 `uv run pytest` 仍然因为本机 `uv` cache 权限失败。提升权限运行同一命令后通过：

```text
59 passed
```

eval dataset / eval report 和 HTTP answer API boundary 都已经完成。下一步建议做 `persistent local knowledge base`。

## 2026-06-03 更新：eval dataset / eval report

项目现在已经有了第一个本地 eval 闭环：

```text
EvalCase
-> LocalAnswerPipeline.answer()
-> GeneratedAnswer
-> expectation checks
-> EvalReport
```

### 本步做了什么

新增 `src/agentic_rag_lab/evals/basic.py`，实现：

- `EvalCase`
- `EvalResult`
- `EvalReport`
- `run_eval_cases()`

### 作用是什么

RAG 项目不能只靠手动问几个问题来判断质量。eval 的作用是把预期答案、预期 citation 和预期 refusal 写成结构化 case，然后用同一条本地 pipeline 重复验证。

### 输入输出

输入：

```text
list[EvalCase]
chunk_size
overlap
```

输出：

```text
EvalReport(total, passed, failed, answer_passed, citation_passed, refusal_passed)
```

### 当前检查规则

- 非拒答 case 检查 required answer terms 是否出现在 `GeneratedAnswer.text`。
- 非拒答 case 检查 expected citations 是否出现在 `GeneratedAnswer.citations`。
- 所有 case 都检查 `GeneratedAnswer.refused` 是否等于 `expected_refused`。
- 拒答 case 不要求 answer terms 或 citations。

### 在整体流程中的定位

当前完整本地链路是：

```text
Markdown/TXT file
-> SourceDocument
-> DocumentChunk
-> LocalHashEmbeddingProvider
-> InMemoryVectorStore
-> LocalRetrievalPipeline.search()
-> MinimumEvidenceRefusalPolicy
-> CitationAwareAnswerGenerator.answer()
-> LocalAnswerPipeline.answer()
-> EvalCase expectation checks
-> EvalReport
```

这说明第一阶段 RAG 核心闭环已经具备最小可运行和可评估版本。

### 验证结果

普通权限运行 `uv run pytest` 仍然因为本机 `uv` cache 权限失败。提升权限运行同一命令后通过：

```text
65 passed
```

HTTP answer API boundary 已经完成。下一步建议做 `persistent local knowledge base`，因为当前 `/answer` 每次请求都要携带 documents。

## 2026-06-03 更新：HTTP answer API boundary

项目现在已经有了最小 HTTP answer endpoint：

```text
POST /answer
-> AnswerRequest
-> SourceDocument
-> LocalAnswerPipeline.from_documents()
-> LocalAnswerPipeline.answer()
-> AnswerResponse
```

### 本步做了什么

新增 `src/agentic_rag_lab/api/answer.py`，实现：

- `AnswerDocument`
- `AnswerRequest`
- `AnswerResponse`
- `POST /answer`

`main.py` 现在会注册 answer router 和 health router。

### 作用是什么

HTTP answer API 把内部 RAG 闭环变成外部可调用服务。调用方不需要知道 chunking、embedding、retrieval、citation 或 refusal 的内部实现，只需要提交 question 和 documents。

### 输入输出

请求：

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

响应：

```json
{
  "text": "基于检索到的资料，可以回答如下：...",
  "citations": ["docs/rag.md#chunk-0"],
  "refused": false
}
```

### 在整体流程中的定位

当前完整链路是：

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

这说明第一阶段 RAG 核心闭环已经可以通过 HTTP 调用。

### 验证结果

普通权限运行 `uv run pytest` 仍然因为本机 `uv` cache 权限失败。提升权限运行同一命令后通过：

```text
74 passed
```

下一步建议做 `persistent local knowledge base`。当前 API 每次请求都携带 documents，下一步可以学习如何在本地维护可复用知识库入口。

## 2026-06-03 更新：persistent local knowledge base

项目现在已经有了进程内可复用知识库 API：

```text
POST /knowledge-bases
-> CreateKnowledgeBaseRequest
-> SourceDocument
-> chunk_documents()
-> LocalAnswerPipeline.from_chunks()
-> InMemoryKnowledgeBaseRegistry
-> CreateKnowledgeBaseResponse

POST /knowledge-bases/{knowledge_base_id}/answer
-> KnowledgeBaseAnswerRequest
-> LocalKnowledgeBase.answer()
-> GeneratedAnswer
-> KnowledgeBaseAnswerResponse
```

### 本步做了什么

新增 `src/agentic_rag_lab/knowledge_base/local.py`，实现：

- `LocalKnowledgeBase`
- `InMemoryKnowledgeBaseRegistry`

新增 `src/agentic_rag_lab/api/knowledge_base.py`，实现：

- `KnowledgeBaseDocument`
- `CreateKnowledgeBaseRequest`
- `CreateKnowledgeBaseResponse`
- `KnowledgeBaseAnswerRequest`
- `KnowledgeBaseAnswerResponse`
- `POST /knowledge-bases`
- `POST /knowledge-bases/{knowledge_base_id}/answer`

`main.py` 现在会在 `create_app()` 中初始化 `app.state.knowledge_bases`，并注册 knowledge base router。

### 作用是什么

`POST /answer` 适合一次性问答，但不适合作为长期知识库入口，因为每次请求都要携带 documents。

本步把系统拆成两个 API 边界：

- `POST /knowledge-bases`：创建可复用知识库。
- `POST /knowledge-bases/{knowledge_base_id}/answer`：基于已创建知识库提问。

API 层仍然不重写 RAG 逻辑。它只做参数校验、DTO 转换、registry 调用和 response 转换。

### 输入输出

创建知识库请求：

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

创建知识库响应：

```json
{
  "knowledge_base_id": "kb-1",
  "document_count": 1,
  "chunk_count": 1
}
```

提问响应：

```json
{
  "text": "基于检索到的资料，可以回答如下：...",
  "citations": ["docs/rag.md#chunk-0"],
  "refused": false
}
```

### 在整体流程中的定位

当前完整链路是：

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

这里的 persistent 是进程内跨请求复用，不是磁盘持久化。

### 验证结果

普通权限运行 `uv run pytest` 仍然因为本机 `uv` cache 权限失败。提升权限运行同一命令后通过：

```text
90 passed
```

下一步建议做 `disk-backed local knowledge base`，因为当前 registry 在服务重启后会丢失。也可以先做 `real provider planning`，但仍然不要跳到 UI、Workbench、MCP、LangGraph 或多 agent。

## 2026-06-03 更新：disk-backed local knowledge base

项目现在已经有了磁盘可恢复的本地知识库：

```text
POST /knowledge-bases
-> SourceDocument
-> DocumentChunk
-> LocalAnswerPipeline
-> DiskBackedKnowledgeBaseRegistry
-> local JSON file

create_app()
-> load local JSON files
-> rebuild LocalAnswerPipeline
-> POST /knowledge-bases/{knowledge_base_id}/answer
```

### 本步做了什么

新增 `src/agentic_rag_lab/knowledge_base/disk.py`，实现：

- `DiskBackedKnowledgeBaseRegistry`
- JSON 文件保存。
- app 启动时加载 JSON。
- 根据已有 `kb-N.json` 计算下一个 id。
- 加载 documents/chunks 后重建 `LocalAnswerPipeline`。

同时更新：

- `Settings.knowledge_base_storage_path`
- `.env.example`
- `.gitignore`
- `create_app()`
- disk-backed registry 测试
- app recreate API 测试

### 作用是什么

进程内 registry 只能跨请求复用，不能跨服务重启复用。disk-backed registry 让知识库具备最小恢复能力。

本步没有改变 HTTP request/response 形状。调用方仍然使用：

```text
POST /knowledge-bases
POST /knowledge-bases/{knowledge_base_id}/answer
```

变化发生在内部：创建知识库后会写入 `.local/knowledge-bases/<id>.json`，下次 app 创建时会加载这些文件。

### 输入输出

新增磁盘输出：

```text
.local/knowledge-bases/kb-1.json
```

JSON 保存：

```text
id
documents
chunks
chunk_size
overlap
```

不保存：

```text
LocalAnswerPipeline
EmbeddingProvider
InMemoryVectorStore
```

这些运行时对象会在恢复时重建。

### 在整体流程中的定位

当前完整链路是：

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

### 验证结果

普通权限运行 `uv run pytest` 仍然因为本机 `uv` cache 权限失败。提升权限运行同一命令后通过：

```text
98 passed
```

file / directory import API 已经完成。下一步建议做 `real provider planning`，开始规划真实模型 API key、embedding provider、LLM answer generation、mock 测试和 eval 边界。

## 2026-06-04 更新：file / directory import API

项目现在已经可以从本机 `.md` / `.txt` 文件或目录创建 disk-backed knowledge base：

```text
POST /knowledge-bases/from-file
-> load_text_file()
-> SourceDocument
-> DiskBackedKnowledgeBaseRegistry.create()

POST /knowledge-bases/from-directory
-> load_directory()
-> list[SourceDocument]
-> DiskBackedKnowledgeBaseRegistry.create()
```

### 本步做了什么

在 `src/agentic_rag_lab/api/knowledge_base.py` 中新增：

- `CreateKnowledgeBaseFromFileRequest`
- `CreateKnowledgeBaseFromDirectoryRequest`
- `POST /knowledge-bases/from-file`
- `POST /knowledge-bases/from-directory`

### 作用是什么

以前创建知识库需要直接在 request body 中传 documents。现在可以直接给服务端本机可访问的文件路径或目录路径，由 ingestion 层负责读取。

这一步把两个已有边界连起来：

```text
ingestion
-> disk-backed knowledge base
```

### 输入输出

文件导入请求：

```json
{
  "path": "D:/docs/rag.md",
  "chunk_size": 400,
  "overlap": 0
}
```

目录导入请求：

```json
{
  "path": "D:/docs",
  "chunk_size": 400,
  "overlap": 0,
  "extensions": [".md", ".txt"]
}
```

响应继续是：

```json
{
  "knowledge_base_id": "kb-1",
  "document_count": 2,
  "chunk_count": 2
}
```

### 在整体流程中的定位

当前完整链路是：

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

### 验证结果

普通权限运行 `uv run pytest` 仍然因为本机 `uv` cache 权限失败。提升权限运行同一命令后通过：

```text
108 passed
```

下一步建议做 `real provider planning`。到这个阶段再讨论真实模型 API key、embedding provider、LLM answer generation、mock 测试和 eval 边界。
