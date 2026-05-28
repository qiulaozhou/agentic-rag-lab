# agentic-rag-lab

`agentic-rag-lab` 是 `D:\zrf\aiProject` 里三个 AI Agent 学习项目的第一个项目。

它的目标不是做一个普通聊天机器人，而是一步一步做出一个可靠的 RAG 知识库系统。当前重点是先把“文档如何进入系统、如何被切分、如何被检索”这些基础能力学扎实，再考虑 Agent Loop、MCP、多 agent 或 UI。

## 当前项目状态

当前已经完成到第一个本地 RAG 数据切片：

```text
Markdown/TXT 文件
-> SourceDocument
-> DocumentChunk
-> pytest 验证
```

已经实现：

- FastAPI 应用入口。
- `/health` 健康检查接口，不需要模型凭证。
- 基于 `.env` 的配置读取。
- 已提交 `.env.example`，真实密钥不进仓库。
- LLM provider 抽象层。
- 离线可用的 `fake` provider。
- RAG 分层目录：`ingestion`、`chunking`、`retrieval`、`generation`、`evals`。
- Markdown/TXT 文档导入到 `SourceDocument`。
- 目录递归导入支持的文本文件。
- 字符窗口切分到 `DocumentChunk`。
- chunk id 和 metadata 都是确定性的，方便测试和后续引用。
- pytest 覆盖 health、ingestion、chunking、本地导入到切分闭环。

还没有实现：

- PDF 导入。
- embedding。
- vector store。
- retrieval / rerank。
- 带引用的回答生成。
- 检索不到时的拒答。
- RAG eval 报告。
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
├── evals/        # 评估边界，后续实现
├── generation/   # 回答生成边界，后续实现
├── ingestion/    # Markdown/TXT 文档导入
├── llm/          # 模型 provider 抽象和 fake provider
├── retrieval/    # 检索边界，后续实现
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
20 passed
```

说明：这台机器在普通权限下可能会因为 `C:\Users\admin\AppData\Local\uv\cache` 权限导致 `uv run pytest` 在启动 pytest 前失败。之前最终验证是用同一个命令在提升权限后通过的。

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
Add local embedding and vector store adapter
```

这一步要学习的是：

- embedding 是什么。
- 文本为什么能变成向量。
- `DocumentChunk.text` 如何变成 embedding。
- 向量存在哪里。
- 如何用一个本地 adapter 返回相似 chunk。
- 为什么 retrieval 要在 answer generation 之前做。

建议你下一次直接这样对我说：

```text
继续 agentic-rag-lab，下一个任务做 Add local embedding and vector store adapter。
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

1. 本地 embedding 和 vector store adapter。
2. 基础 retrieval，能根据 query 找到相关 chunks。
3. citation-aware answer generation，让回答带来源。
4. refusal behavior，检索不到时不胡编。
5. eval dataset 和 eval report。
6. 再考虑 `ai-agent-workbench`。
7. 最后做 `mcp-devtools-server`。

每一步都要形成一个小闭环，不要一次把所有能力堆上去。
