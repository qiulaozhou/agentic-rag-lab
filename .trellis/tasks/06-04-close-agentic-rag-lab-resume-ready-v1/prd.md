# Agentic RAG Lab Resume-Ready V1 Closeout

## Goal

把 `agentic-rag-lab` 从持续加功能的学习项目收口成可以放进简历、可以清楚讲解工程链路的 RAG 项目 V1。

本任务不新增大型 RAG 功能，重点是整理项目文档、学习文档、技术边界、简历讲法、未做内容和后续项目切换。

## Requirements

- 新增项目学习索引文档，按任务顺序说明每一步做了什么、为什么做、在整体 RAG 链路中的位置和学到什么。
- 新增项目展示文档，服务简历和面试讲述，区分项目整体能力与个人实现内容。
- 更新 `README.md`，让第一屏展示当前 V1 状态、完整链路、运行入口、provider 配置、安全边界和未做内容。
- 更新 `docs/TECHNICAL_NOTES.md`，按模块边界整理当前技术架构。
- 更新根目录 `AI_AGENT_PORTFOLIO_NOTES.md`，把 `agentic-rag-lab` 标记为 `Resume-ready V1`，并把下一主线切换到 `ai-agent-workbench`。
- 更新 Trellis backend specs，固化项目收口时的文档和质量要求。
- 增加轻量文档完整性测试，确保收口文档包含关键状态、链路和安全约束。
- 不写入真实 API key、真实 Authorization header 或用户提供的真实 secret。

## Learning Goals

- 理解一个学习型 RAG 项目如何从功能开发进入简历收口。
- 理解项目收口不等于生产级完工，而是把已完成能力、边界、验证结果和未做内容讲清楚。
- 理解学习文档不是流水账，需要把“做了什么”和“为什么这样做”串成可复习的工程链路。
- 理解简历项目表述需要有证据边界，不能把本地 deterministic baseline 夸成生产级系统。
- 理解 Trellis/harness 在本项目中的角色是工程化约束，不是 RAG 业务能力本身。

## Concepts

- resume-ready V1
- project closeout
- learning index
- project showcase
- technical boundary
- evidence-backed resume wording
- next-project handoff

## Why Now

`agentic-rag-lab` 已经完成了本地 RAG 闭环、HTTP API、知识库导入和恢复、OpenAI-compatible provider adapters、真实 provider 手动 smoke 指南和 provider eval comparison。继续盲目加 UI、LangGraph、MCP 或多 agent 会稀释当前项目的主线。

现在更重要的是把它整理成一个可讲、可复习、可放简历的 V1，然后把后续主线切到 `ai-agent-workbench`。

## Approach Options

**Option A: 收口文档 + 轻量文档测试（本次采用）**

- 优点：不破坏现有实现；能快速形成简历可讲版本；保留所有历史学习记录。
- 代价：不新增生产级 RAG 能力。

**Option B: 继续追加生产功能**

- 优点：能力继续变多。
- 代价：当前项目会变得发散，简历主线反而不清楚。

**Option C: 直接切到 Workbench，不整理 RAG Lab**

- 优点：进入下一个项目更快。
- 代价：`agentic-rag-lab` 的学习价值和简历价值没有沉淀，后续还要回来补文档。

## Acceptance Criteria

- [ ] 新增中文 `learning.md`，完整记录本步收口学习内容。
- [ ] 新增 `docs/LEARNING_INDEX.md`。
- [ ] 新增 `docs/PROJECT_SHOWCASE.md`。
- [ ] `README.md` 第一屏明确 `Resume-ready V1` 和完整 RAG 链路。
- [ ] `TECHNICAL_NOTES.md` 第一屏明确当前模块边界。
- [ ] 根目录 `AI_AGENT_PORTFOLIO_NOTES.md` 标记 `agentic-rag-lab` 已收口，并把下一主线切到 `ai-agent-workbench`。
- [ ] 文档明确未做内容，不把项目包装成生产级 RAG 系统。
- [ ] 文档不包含真实 API key。
- [ ] `uv run pytest` 通过，或环境级失败被记录。

## Out of Scope

- UI。
- LangGraph。
- MCP。
- 多 agent。
- Chroma、Qdrant、pgvector。
- PDF、Word、HTML 解析。
- rerank。
- streaming response。
- auth、rate limit、request size limit。
- 真实 provider 自动化联网测试。

## Out of Scope for Learning

- 生产级 RAG 质量评测。
- 长期指标趋势。
- 模型成本优化。
- 大规模知识库索引管理。
- 真实业务权限和合规策略。
