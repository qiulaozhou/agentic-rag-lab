# agentic-rag-lab Technical Notes

更新时间：2026-05-28

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

当前项目已经从 MVP skeleton 推进到第一个本地 RAG 数据切片：Markdown/TXT 文档可以被读取成 `SourceDocument`，再被切成 `DocumentChunk`。它还没有实现向量检索、rerank 和回答生成。

## 当前已完成内容

代码已经完成这些基础设施：

| 能力 | 当前实现 | 作用 |
| --- | --- | --- |
| FastAPI app | `src/agentic_rag_lab/main.py` | 创建应用并注册 router |
| health endpoint | `src/agentic_rag_lab/api/health.py` | 提供无需模型凭证的 smoke check |
| settings | `src/agentic_rag_lab/config.py` | 从环境变量和 `.env` 读取配置 |
| `.env.example` | `.env.example` | 给后续真实 provider 留配置入口，不提交 secrets |
| domain schemas | `src/agentic_rag_lab/schemas.py` | 定义文档、chunk、检索结果、生成答案的数据形状 |
| LLM boundary | `src/agentic_rag_lab/llm/base.py` | 用 protocol 隔离模型调用接口 |
| fake provider | `src/agentic_rag_lab/llm/fake.py` | 本地离线测试用，不依赖真实模型 |
| provider factory | `src/agentic_rag_lab/llm/factory.py` | 根据 settings 创建 provider |
| module boundaries | `ingestion`、`chunking`、`retrieval`、`generation`、`evals` | 先把后续功能边界留出来 |
| Markdown/TXT ingestion | `src/agentic_rag_lab/ingestion/text.py` | 把 UTF-8 `.md` / `.txt` 文件转成 `SourceDocument` |
| text chunking | `src/agentic_rag_lab/chunking/text.py` | 用确定性的字符窗口把文档切成 `DocumentChunk` |
| tests | `tests/` | 覆盖 health、ingestion、chunking 和本地 pipeline |

验证命令：

```powershell
uv run pytest
```

实现阶段记录的成功结果：

```text
20 passed
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
├── llm/
├── retrieval/
├── config.py
├── main.py
└── schemas.py
```

这些目录仍然按 RAG 层次拆开。当前只实现 ingestion 和 chunking 的最小本地闭环，retrieval、generation、evals 仍保持边界状态。

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

这些 dataclass 是后续功能的连接点。下一步 ingestion/chunking 应该直接使用 `SourceDocument` 和 `DocumentChunk`，不要重新发明一套数据形状。

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
- Embeddings and vector storage。
- Retrieval and rerank behavior。
- Citation-aware answer generation。
- RAG evaluation reports。

这些都不要误认为已经完成。现在只是本地文档进入系统并切片的第一步。

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

在 ingestion/chunking 之后，建议继续按这个顺序推进：

1. Local embedding and vector store adapter。
2. Basic retrieval API。
3. Citation-aware answer generation。
4. Refusal behavior。
5. Eval dataset and report。

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

当前 ingestion/chunking 任务路径：

```text
.trellis/tasks/05-28-add-markdown-txt-ingestion-chunking/
```

后续每个任务都应该留下类似记录，方便复习每一步为什么这样做。
