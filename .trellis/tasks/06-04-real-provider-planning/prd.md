# Real Provider Planning

## Goal

把 `agentic-rag-lab` 从纯本地替代实现，推进到“可以接真实 provider，但默认仍然离线”的工程边界。

本任务先规划真实模型接入方式，不要求自动调用真实服务，不把密钥写入仓库，不让测试依赖网络或额度。

## Requirements

- 新增真实 provider 相关配置项：
  - `EMBEDDING_PROVIDER`
  - `ANSWER_GENERATOR`
  - `OPENAI_COMPATIBLE_API_KEY`
  - `OPENAI_COMPATIBLE_BASE_URL`
  - `OPENAI_COMPATIBLE_EMBEDDING_MODEL`
  - `OPENAI_COMPATIBLE_CHAT_MODEL`
- 默认配置必须保持：
  - embedding 使用 `local_hash`
  - answer generation 使用 `local_citation`
- `.env.example` 只写变量名和占位值，不写真实 secret。
- 真实 provider 必须显式 opt-in，缺少 key、base URL 或 model 时抛出明确 `ValueError`。
- pytest 只使用 mock HTTP，不请求真实网络。
- 学习文档必须解释：
  - 为什么之前的 embedding 是本地替代实现。
  - 为什么之前的 answer generator 是 deterministic generator。
  - 为什么真实 provider 默认关闭。
  - API key 应该只放在本地 `.env`。

## Learning Goals

- 理解“本地替代实现”和“真实 provider adapter”的区别。
- 理解 provider 配置为什么要通过 settings/factory，而不是散落在 API route 里。
- 理解真实模型接入时的 secret 管理边界。
- 理解为什么测试真实 provider adapter 时应使用 mock transport。
- 理解 eval 与 refusal 在真实 provider 接入后的角色：它们仍然负责控制可验证性和证据不足时的行为。

## Concepts

- provider boundary
- opt-in configuration
- environment variables
- secret safety
- mock transport testing
- offline default behavior
- RAG reproducibility

## Why Now

当前项目已经完成：

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

这说明 RAG 的工程骨架已经可以导入文件、建知识库、检索、生成回答、拒答、评估和通过 HTTP 调用。下一步自然是规划真实模型接入，但不能直接把真实 key、真实网络和真实模型不稳定性塞进默认测试链路。

## Approach Options

**Option A: 默认本地，真实 provider 显式开启（本次采用）**

- 优点：保留离线可测能力；真实服务接入有明确开关；不会让普通测试依赖 key。
- 代价：用户需要配置环境变量后才能手动试真实服务。

**Option B: 默认直接用真实 provider**

- 优点：更接近真实 RAG。
- 代价：没有 key 就无法运行；测试不稳定；容易误把 secret 写入仓库。

**Option C: 只写文档，不做 adapter**

- 优点：风险最低。
- 代价：项目仍无法验证真实 provider 边界，推进速度不够。

## Acceptance Criteria

- [ ] settings 中有真实 provider 相关配置项。
- [ ] `.env.example` 只包含安全占位值。
- [ ] 默认 provider 仍然离线可运行。
- [ ] 真实 provider 缺少必要配置时抛出明确错误。
- [ ] 项目文档解释真实 provider 默认关闭的原因。
- [ ] 本任务 `learning.md` 用中文记录学习内容和验证结果。

## Definition of Done

- 配置规划落到代码和文档。
- 不写入真实 API key。
- 后续 OpenAI-compatible adapter 能基于这些配置创建。
- `uv run pytest` 通过，或环境级失败被记录。

## Out of Scope

- 自动真实服务 smoke test。
- 真实 key 写入仓库文件。
- 真实模型效果调优。
- Chroma、Qdrant、pgvector。
- rerank。
- UI、MCP、LangGraph、多 agent。

## Out of Scope for Learning

- 复杂 secret vault。
- 多租户 key 管理。
- 生产级 provider fallback。
- 额度统计和成本控制。
- 模型质量 benchmark。

