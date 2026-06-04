# 学习记录：OpenAI-Compatible Provider Adapters

更新日期：2026-06-04

## 本步一句话总结

本步新增 OpenAI-compatible embedding provider 和 LLM-backed answer generator，让 `agentic-rag-lab` 可以显式配置真实模型服务，同时默认仍然保持本地离线可测。

## 本步做了什么

- 新增 `OpenAICompatibleEmbeddingProvider`。
  - 调用 `{base_url}/embeddings`。
  - 请求体包含 `model` 和 `input`。
  - 解析 `data[0].embedding` 为 `list[float]`。
- 新增 `OpenAICompatibleLLMProvider`。
  - 调用 `{base_url}/chat/completions`。
  - 通过 `LLMProvider` protocol 暴露 `generate()`。
  - 解析 `choices[0].message.content` 为模型回答文本。
- 新增 `LLMBackedCitationAwareAnswerGenerator`。
  - LLM 只负责生成 answer text。
  - citations 仍由本地 `RetrievalResult.chunk.metadata` 生成。
  - 空 evidence 时直接拒答，不调用 LLM。
- 新增 provider factories：
  - `create_embedding_provider(settings)`
  - `create_answer_generator(settings)`
  - `create_llm_provider(settings)` 支持 `openai_compatible`
- 更新 `create_app()`：
  - app 启动时根据 settings 创建 provider。
  - `POST /answer` 使用 app 注入的 provider。
  - disk-backed knowledge base registry 创建和恢复 pipeline 时也使用同一套 provider。
- 把 `httpx` 提升为运行时依赖。
- 新增 mock HTTP 测试，覆盖成功、缺配置、非 2xx、响应格式错误、citation 本地生成等场景。

## 作用是什么

之前的 `LocalHashEmbeddingProvider` 是本地替代实现：它用 `sha256` 和 token bag-of-words 生成固定维度向量，优点是离线、确定性、无外部依赖；缺点是它不理解真实语义，只适合学习和测试 RAG 工程链路。

现在新增真实 embedding provider 后，embedding 这一步可以交给真实模型服务：

```text
text
-> OpenAI-compatible /embeddings
-> semantic vector
```

之前的 `CitationAwareAnswerGenerator` 也是 deterministic generator：它只是把检索到的 evidence 摘要拼成回答，并生成 citation，优点是稳定可测；缺点是表达能力有限，不是真正的自然语言生成。

现在新增 LLM-backed generator 后，answer text 可以由真实 LLM 生成：

```text
question + retrieved evidence
-> OpenAI-compatible /chat/completions
-> answer text
```

但是 citation 仍然不能交给模型自由生成。模型可能编出不存在的来源，所以本项目继续把 citation authority 留在本地：

```text
RetrievalResult.chunk.metadata
-> source_path#chunk-{chunk_index}
-> GeneratedAnswer.citations
```

## 用什么实现

- `httpx`
  - 作为 OpenAI-compatible HTTP client。
  - 测试中使用 `httpx.MockTransport`。
- `src/agentic_rag_lab/embeddings/openai_compatible.py`
  - 实现 embedding adapter。
- `src/agentic_rag_lab/embeddings/factory.py`
  - 根据 settings 创建 embedding provider。
- `src/agentic_rag_lab/llm/openai_compatible.py`
  - 实现 chat completion provider。
- `src/agentic_rag_lab/generation/llm_backed.py`
  - 实现 LLM-backed answer generator。
- `src/agentic_rag_lab/generation/factory.py`
  - 根据 settings 创建 answer generator。
- `src/agentic_rag_lab/main.py`
  - app factory 中统一创建 provider，并注入 API 和 knowledge base registry。

## 输入输出是什么

### Embedding provider

输入：

```text
text: str
```

请求：

```json
{
  "model": "configured-embedding-model",
  "input": "text"
}
```

输出：

```text
list[float]
```

### LLM-backed generator

输入：

```text
question: str
evidence: list[RetrievalResult]
```

请求给 LLM 的内容只包含：

```text
question
retrieved evidence snippets
```

输出：

```text
GeneratedAnswer(text=model_text, citations=local_citations, refused=False)
```

空 evidence 输出：

```text
GeneratedAnswer(text=NO_EVIDENCE_TEXT, citations=[], refused=True)
```

## 在整体 RAG 链路中的定位

完成后，项目链路推进到：

```text
ingestion
-> chunking
-> embedding
   -> LocalHashEmbeddingProvider by default
   -> OpenAICompatibleEmbeddingProvider when explicitly configured
-> retrieval
-> citation-aware generation
   -> CitationAwareAnswerGenerator by default
   -> LLMBackedCitationAwareAnswerGenerator when explicitly configured
-> answer pipeline
-> refusal behavior
-> eval dataset / eval report
-> HTTP answer API boundary
-> persistent local knowledge base
-> disk-backed local knowledge base
-> file / directory import API
-> OpenAI-compatible providers  <-- 本步
```

这一步改变的是 embedding 和 answer text generation 的 provider，可复用已有 ingestion、chunking、retrieval、refusal、citation、eval、API 和 knowledge base 边界。

## 为什么现在做

现在项目已经有稳定的最小 RAG 工程链路。如果此时接真实 provider，真实模型只是替换局部能力，而不是重写整个系统：

- embedding provider 替换 `LocalHashEmbeddingProvider`。
- answer generator 替换 deterministic generator。
- citation、refusal、eval、HTTP API、knowledge base 继续复用。

这比一开始就接真实模型更清楚，因为我们可以用已有 tests 判断真实 provider adapter 有没有破坏默认本地链路。

## 设计选择

### 选择 A：OpenAI-compatible HTTP adapter

本次采用。

优点：
- 适配用户提供的自定义 `base_url`。
- 不绑定特定 SDK。
- `httpx.MockTransport` 易于测试。

代价：
- 响应解析和错误处理需要自己实现。

### 选择 B：官方 SDK

没有采用。

原因：
- 增加 provider SDK 依赖。
- 自定义 OpenAI-compatible 网关不一定完全兼容 SDK 的所有行为。

### 选择 C：先只接 LLM，不接 embedding

没有采用。

原因：
- 真实 RAG 不只需要模型写答案，也需要真实语义 embedding。
- 只接 LLM 会让检索仍停留在 hash 替代实现，链路不完整。

## 本次没有做什么

- 没有把真实 API key 写入仓库。
- 没有在 pytest 中请求真实网络。
- 没有做真实服务 smoke test 自动化。
- 没有做 streaming response。
- 没有做 provider retry、timeout、rate limit、cost 统计。
- 没有做 Chroma/Qdrant/pgvector。
- 没有做 rerank。
- 没有做 UI、MCP、LangGraph、多 agent。

## 如何验证

新增测试覆盖：

- `tests/test_openai_compatible_embedding.py`
  - mock `/embeddings` 成功响应。
  - 请求体包含 model/input。
  - 缺配置抛 `ValueError`。
  - 非 2xx 抛明确错误。
  - malformed response 抛明确错误。
- `tests/test_openai_compatible_llm.py`
  - mock `/chat/completions` 成功响应。
  - 请求体包含 model/messages。
  - 缺配置、非 2xx、malformed response 均有测试。
- `tests/test_llm_backed_generation.py`
  - 模型正文进入 `GeneratedAnswer.text`。
  - citations 来自本地 metadata。
  - 模型文本中的假 citation 不会进入 `GeneratedAnswer.citations`。
  - 空 evidence 不调用 LLM。
- `tests/test_provider_factories.py`
  - 默认 factory 返回本地 provider。
  - opt-in factory 创建 OpenAI-compatible provider。
  - `.env.example` 只包含变量名和占位值。

验证命令：

```powershell
uv run pytest
```

普通权限下先因本机 `uv` cache 权限失败；提升权限后同一命令通过：

```text
127 passed
```

## 学到什么

- 真实 embedding provider 接入后，改变的是“文本到向量”的实现，不应该改变 retrieval pipeline 的数据结构。
- LLM-backed answer generation 接入后，改变的是“证据到回答正文”的实现，不应该让模型自由编 citation。
- citation 的可信来源仍然是本地检索结果和 metadata。
- provider factory 可以把配置选择集中起来，避免 API route 直接知道模型细节。
- 默认关闭真实 provider 是为了保护离线测试、secret 安全和学习过程的可复现性。

## Trellis 反馈

这一步形成了新的可复用后端约定：

- provider adapter 放在 `embeddings/` 或 `llm/`。
- answer generator adapter 放在 `generation/`。
- API route 只能使用 pipeline/factory 注入的能力，不直接调用 provider HTTP。
- OpenAI-compatible provider 测试必须 mock HTTP。
- citation 由本地 evidence metadata 生成，不信任模型文本里的 citation。

这些约定已同步到 backend specs。

## 下一步是什么

下一步建议做：

```text
real provider manual smoke guide
```

或者：

```text
expand eval dataset/report for real-provider comparison
```

现在项目已经可以通过配置接真实 OpenAI-compatible provider，但还没有一份手动 smoke 指南说明如何安全地用本地 `.env` 验证真实服务，也还没有把本地 deterministic eval 和真实 provider 输出做对比的扩展报告。

