# 学习记录：Real Provider Planning

更新日期：2026-06-04

## 本步一句话总结

本步把真实 embedding / LLM provider 的配置、安全、默认关闭、mock 测试和文档边界固定下来，为后续 OpenAI-compatible provider adapter 提供可控入口。

## 本步做了什么

- 在 `Settings` 中新增 provider 选择配置：
  - `embedding_provider`
  - `answer_generator`
  - `openai_compatible_api_key`
  - `openai_compatible_base_url`
  - `openai_compatible_embedding_model`
  - `openai_compatible_chat_model`
- 保留默认离线模式：
  - `embedding_provider=local_hash`
  - `answer_generator=local_citation`
  - `llm_provider=fake`
- 更新 `.env.example`，只写变量名和占位值，不写真实密钥。
- 明确真实 provider 必须显式配置才启用。
- 明确 pytest 不请求真实网络，只通过 mock HTTP 验证 adapter 行为。

## 作用是什么

之前项目已经能完成本地 RAG 闭环，但 embedding 和 answer generation 都是学习阶段的本地替代实现。现在要准备接真实模型，如果直接把真实 API key、真实网络调用和真实模型不确定性塞进默认链路，会让项目失去离线可复现能力。

本步的作用是先把真实 provider 的工程边界想清楚：

- 默认怎么保持本地可测。
- 什么时候才允许调用真实服务。
- 密钥放在哪里。
- 测试如何不依赖真实服务。
- 文档如何说明“真实 provider 是可选能力，不是默认要求”。

## 用什么实现

- `src/agentic_rag_lab/config.py`
  - 用 `pydantic-settings` 读取环境变量和 `.env`。
  - 用 `Literal` 限定 provider 名称，避免无效字符串静默进入运行时。
- `.env.example`
  - 提供安全配置入口。
  - 只保留变量名和占位值。
- provider factory
  - 后续通过 factory 创建本地或 OpenAI-compatible provider。

## 输入输出是什么

输入是本地环境变量或 `.env`：

```text
EMBEDDING_PROVIDER
ANSWER_GENERATOR
OPENAI_COMPATIBLE_API_KEY
OPENAI_COMPATIBLE_BASE_URL
OPENAI_COMPATIBLE_EMBEDDING_MODEL
OPENAI_COMPATIBLE_CHAT_MODEL
```

输出是 `Settings` 对象中的配置值，后续由 factory 转成具体 provider 实例：

```text
Settings
-> create_embedding_provider()
-> create_answer_generator()
-> create_app()
```

## 在整体 RAG 链路中的定位

当前整体链路推进到：

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
-> real provider planning  <-- 本步
```

本步不直接提高回答质量，但它决定真实模型如何安全进入链路。

## 为什么现在做

现在做真实 provider planning 是因为前面的工程边界已经足够稳定：

- 文档可以导入。
- chunk 可以生成。
- retrieval 可以返回证据。
- answer pipeline 可以统一调用。
- refusal 可以阻止证据不足时继续生成。
- eval 可以检查 answer、citation、refusal。
- HTTP 和 knowledge base API 已经存在。

如果在这些边界之前就接真实模型，很容易把问题混在一起：不知道失败是 ingestion、chunking、retrieval、prompt、模型、网络还是 key 配置导致的。现在先规划 provider 边界，可以让真实模型只替换“embedding”和“answer text generation”两个清晰位置。

## 设计选择

### 选择 A：默认本地，真实 provider 显式开启

本次采用。

优点：
- 不配置 key 也能跑完整测试。
- 不会误用真实额度。
- 文档和测试能稳定复现。
- 用户可以在本地 `.env` 中手动开启真实 provider。

代价：
- 真实服务 smoke test 需要手动配置后再单独运行。

### 选择 B：默认真实 provider

没有采用。

原因：
- 没有 key 时项目无法运行。
- pytest 会依赖网络和额度。
- 容易把 secret 写进文档或测试。

### 选择 C：只写规划，不做 adapter

没有采用。

原因：
- 规划不能验证接口边界。
- 项目推进速度不够。
- 用户已经准备好后续提供真实服务配置。

## 本次没有做什么

- 没有把真实 API key 写入任何仓库文件。
- 没有在 pytest 中调用真实服务。
- 没有做真实服务自动 smoke test。
- 没有引入 Chroma、Qdrant、pgvector。
- 没有做 rerank。
- 没有做 UI、MCP、LangGraph、多 agent。
- 没有做生产级 provider fallback、重试、限流和成本统计。

## 如何验证

先用普通权限运行：

```powershell
uv run pytest
```

普通权限下失败，原因是本机 `uv` cache 目录拒绝访问：

```text
C:\Users\admin\AppData\Local\uv\cache
```

按环境规则使用同一条命令提升权限重跑：

```powershell
uv run pytest
```

最终结果：

```text
127 passed
```

## 学到什么

- 真实模型接入不是“直接把 key 填进去调用 API”，而是要先明确默认行为、配置入口、secret 安全、测试方式和失败边界。
- 本地替代实现仍然有价值：它让项目在没有真实模型时也能验证 RAG 工程链路。
- provider factory 是非常重要的隔离层：API route 不应该知道具体模型如何调用。
- `.env.example` 应该只提供安全占位，真实 key 只能放本地 `.env`。

## Trellis 反馈

这一步形成了可复用约定：

- 真实 provider 必须 opt-in。
- 默认 smoke test 必须离线。
- secret 不进入 README、learning.md、测试或代码。
- provider-specific HTTP 调用必须放在 adapter/factory 后面，不进入 API route。

这些约定已同步到 backend specs。

## 下一步是什么

下一步自然是实现 OpenAI-compatible provider adapters：

```text
Settings
-> OpenAICompatibleEmbeddingProvider
-> OpenAICompatibleLLMProvider
-> LLMBackedCitationAwareAnswerGenerator
-> mocked pytest
```

这一步会把规划落到真实 adapter，但仍然保持默认本地离线。

