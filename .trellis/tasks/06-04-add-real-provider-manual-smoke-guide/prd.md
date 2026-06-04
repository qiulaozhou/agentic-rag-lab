# Add Real Provider Manual Smoke Guide

## Goal

为 `agentic-rag-lab` 新增真实 OpenAI-compatible provider 的本地手动 smoke 指南，说明如何配置 `.env` 并手动验证 `/health`、`/answer`、knowledge base 和 file import 链路。

本任务不自动调用真实服务，不把真实 key、真实 base URL 或真实模型名写入仓库。

## Requirements

- 新增 `docs/REAL_PROVIDER_SMOKE_GUIDE.md`。
- 指南必须说明真实密钥只放本地 `.env`。
- 指南必须列出需要配置的环境变量名：
  - `EMBEDDING_PROVIDER`
  - `ANSWER_GENERATOR`
  - `OPENAI_COMPATIBLE_API_KEY`
  - `OPENAI_COMPATIBLE_BASE_URL`
  - `OPENAI_COMPATIBLE_EMBEDDING_MODEL`
  - `OPENAI_COMPATIBLE_CHAT_MODEL`
- 指南必须包含 PowerShell 手动验证步骤：
  - 复制 `.env.example` 到 `.env`
  - 手动填写 `.env`
  - 启动 `uv run uvicorn agentic_rag_lab.main:app --reload`
  - 调用 `/health`
  - 调用 `POST /answer`
  - 调用 `POST /knowledge-bases`
  - 调用 `POST /knowledge-bases/{id}/answer`
  - 调用 `POST /knowledge-bases/from-file`
- 指南必须明确 pytest 不跑真实 provider。

## Learning Goals

- 理解 manual smoke 和 automated tests 的区别。
- 理解为什么真实 provider 验证不能默认进入 pytest。
- 理解真实 key 为什么只能放本地 `.env`。
- 理解如何用最小 HTTP 请求证明真实 provider 已接入现有 RAG 链路。

## Concepts

- manual smoke test
- OpenAI-compatible provider
- local `.env`
- secret safety
- opt-in provider configuration
- HTTP RAG API verification

## Why Now

项目已经完成 OpenAI-compatible provider adapters，但还缺一份安全、明确、可手动执行的真实 provider 验证指南。现在补这份指南，可以让真实服务验证和自动化测试分离，避免 key、网络和额度进入 pytest。

## Approach Options

**Option A: 文档化手动 smoke（本次采用）**

- 优点：安全、清晰、不依赖 CI 或 pytest 网络。
- 代价：真实服务验证需要人工执行。

**Option B: pytest 自动打真实服务**

- 优点：自动化程度高。
- 代价：需要 key、网络、额度，且结果受 provider 状态影响，不适合作为默认测试。

**Option C: 不写指南，只保留 README 简短说明**

- 优点：文档更少。
- 代价：真实 provider 验证步骤分散，容易误把 secret 写入仓库。

## Acceptance Criteria

- [ ] `docs/REAL_PROVIDER_SMOKE_GUIDE.md` 存在。
- [ ] 指南只包含变量名和占位值，不包含真实 secret。
- [ ] 指南包含 `/health`、`/answer`、knowledge base、file import 的手动验证步骤。
- [ ] README、TECHNICAL_NOTES 和根目录学习文档指向该指南。
- [ ] 文档测试或轻量检查确认必要变量和 endpoint 出现在指南中。
- [ ] `uv run pytest` 通过，或环境级失败被记录。

## Out of Scope

- 真实服务自动 smoke test。
- 真实 key 写入仓库。
- 模型名推荐和效果调优。
- provider retry、rate limit、cost tracking。
- UI、MCP、LangGraph、多 agent。

## Out of Scope for Learning

- 生产级 secret vault。
- CI secret 注入。
- 多 provider 灰度发布。
- 真实服务监控和报警。

