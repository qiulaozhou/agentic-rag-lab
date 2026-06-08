# agentic-rag-lab

`agentic-rag-lab` 是一个可离线测试、可 HTTP 调用、可导入本地 Markdown/TXT、支持 citation / refusal / eval 的 RAG 知识库项目。

当前状态是 `Resume-ready V1`。它已经收口成一个清晰的 RAG 闭环，不再继续扩展 Web UI、LangGraph、MCP 或多 agent 编排。

## 当前能力

- 本地文件和目录导入。
- 文档切分、检索和 citation-aware answer 生成。
- 证据不足时的 refusal 行为。
- 离线 eval dataset / eval report。
- HTTP answer API 和 knowledge base API。
- 进程内与磁盘持久化知识库。
- 可选的 OpenAI-compatible embedding / chat provider adapters。

## 快速开始

运行测试：

```powershell
uv run pytest
```

启动 API：

```powershell
uv run uvicorn agentic_rag_lab.main:app --reload
```

默认离线配置：

```text
EMBEDDING_PROVIDER=local_hash
ANSWER_GENERATOR=local_citation
```

如果需要接入真实 provider，只在本地 `.env` 中显式配置：

```text
EMBEDDING_PROVIDER=openai_compatible
ANSWER_GENERATOR=openai_compatible
OPENAI_COMPATIBLE_API_KEY=your-api-key
OPENAI_COMPATIBLE_BASE_URL=your-openai-compatible-base-url
OPENAI_COMPATIBLE_EMBEDDING_MODEL=your-embedding-model
OPENAI_COMPATIBLE_CHAT_MODEL=your-chat-model
```

## 主要 API

```text
GET  /health
POST /answer
POST /knowledge-bases
POST /knowledge-bases/from-file
POST /knowledge-bases/from-directory
POST /knowledge-bases/{knowledge_base_id}/answer
```

`POST /answer` 适合临时问答；知识库 API 适合重复提问和本地持久化。

## 文档入口

- [学习索引](docs/LEARNING_INDEX.md)
- [项目展示](docs/PROJECT_SHOWCASE.md)
- [技术说明](docs/TECHNICAL_NOTES.md)
- [真实 provider smoke 指南](docs/REAL_PROVIDER_SMOKE_GUIDE.md)

## 当前范围

V1 还不包括：

- 生产级向量库。
- PDF / Word / HTML 复杂解析。
- 浏览器 multipart upload。
- 知识库 update / delete / list API。
- rerank、streaming response、auth、rate limit。
- Web UI、LangGraph、MCP、multi-agent 编排。

