# Add OpenAI-Compatible Provider Adapters

## Goal

新增 OpenAI-compatible embedding provider 和 LLM-backed citation-aware answer generator，让项目可以在显式配置后接入真实模型服务。

默认仍保持本地离线模式：

```text
LocalHashEmbeddingProvider
-> InMemoryVectorStore
-> CitationAwareAnswerGenerator
```

显式配置后可切换为：

```text
OpenAICompatibleEmbeddingProvider
-> InMemoryVectorStore
-> LLMBackedCitationAwareAnswerGenerator
```

## Requirements

- 新增 `OpenAICompatibleEmbeddingProvider`：
  - 调用 `{base_url}/embeddings`
  - 请求体包含 `model` 和 `input`
  - 返回 `list[float]`
  - 非 2xx 或响应格式错误时抛出明确异常
- 新增 `OpenAICompatibleLLMProvider`：
  - 调用 `{base_url}/chat/completions`
  - 使用 `LLMProvider` protocol
  - 请求体包含 `model`、`messages` 和 `temperature`
- 新增 `LLMBackedCitationAwareAnswerGenerator`：
  - 只让 LLM 生成 answer text
  - citations 仍然由本地 evidence metadata 生成
  - 空 evidence 不调用 LLM，直接拒答
- 新增 provider factories：
  - 默认返回本地 deterministic provider
  - opt-in settings 才创建 OpenAI-compatible provider
- API 和 knowledge base registry 使用 factory 创建的 provider。
- 测试使用 `httpx.MockTransport`，不请求真实网络。

## Learning Goals

- 理解 embedding adapter 如何把文本交给外部模型并解析向量。
- 理解 LLM-backed generator 为什么仍然不能信任模型生成 citation。
- 理解 provider factory 如何把配置选择和业务调用解耦。
- 理解 mock HTTP 测试如何覆盖 provider 请求和响应解析。
- 理解真实 provider 接入后，当前 RAG 链路哪些部分改变了，哪些部分保持不变。

## Concepts

- OpenAI-compatible API
- `/embeddings`
- `/chat/completions`
- adapter pattern
- factory pattern
- local citation authority
- mocked provider tests

## Why Now

项目已经有 file/directory import、disk-backed knowledge base、answer API、refusal 和 eval。此时接真实 provider 不再是“孤立调用模型”，而是把真实 embedding 和真实 LLM 放进一个已有、可测试、可评估、可拒答的 RAG 工程链路。

## Approach Options

**Option A: 使用 OpenAI-compatible HTTP adapter（本次采用）**

- 优点：不绑定某一家 SDK；只依赖通用 HTTP；便于 mock 测试；适合用户提供自定义 `base_url`。
- 代价：需要自己解析响应和处理错误。

**Option B: 使用官方 SDK**

- 优点：类型和错误处理可能更完整。
- 代价：新增 SDK 依赖；对 OpenAI-compatible 自定义网关不一定完全适配。

**Option C: 只接真实 LLM，不接真实 embedding**

- 优点：改动更小。
- 代价：检索质量仍停留在 hash embedding，真实 RAG 链路不完整。

## Acceptance Criteria

- [ ] 默认未配置 key 时所有现有测试仍离线通过。
- [ ] opt-in embedding provider 能用 mock `/embeddings` 返回向量。
- [ ] opt-in LLM provider 能用 mock `/chat/completions` 返回文本。
- [ ] LLM-backed generator 的 citations 来自本地 evidence，而不是模型文本。
- [ ] 空 evidence 时 LLM 不被调用并返回拒答。
- [ ] API 和 knowledge base 使用 provider factory 注入的 provider。
- [ ] `uv run pytest` 通过，或环境级失败被记录。

## Definition of Done

- OpenAI-compatible embedding provider 完成。
- OpenAI-compatible LLM provider 完成。
- LLM-backed citation-aware generator 完成。
- Settings/factory/API/knowledge base 接入完成。
- Mock 测试覆盖成功、错误和默认离线行为。
- README、TECHNICAL_NOTES、根目录学习文档和本任务 `learning.md` 更新。

## Out of Scope

- 真实服务自动 smoke test。
- 把真实 key 写入代码或文档。
- provider 重试、限流、超时策略调优。
- streaming response。
- rerank。
- vector database。
- UI、MCP、LangGraph、多 agent。

## Out of Scope for Learning

- 生产级成本控制。
- 复杂 prompt 优化。
- 多模型路由。
- embedding 维度迁移策略。
- provider SLA 和监控。

