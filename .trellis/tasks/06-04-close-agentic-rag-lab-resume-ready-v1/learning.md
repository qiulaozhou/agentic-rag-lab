# 学习记录：Agentic RAG Lab Resume-ready V1 收口

更新日期：2026-06-04

## 本步一句话总结

本步没有继续扩展新的生产功能，而是把 `agentic-rag-lab` 整理成可以放进简历、可以复习、可以面试讲清楚的 RAG 项目 V1。

## 本步做了什么

- 新建 Trellis 收口任务：
  - `.trellis/tasks/06-04-close-agentic-rag-lab-resume-ready-v1/prd.md`
  - `.trellis/tasks/06-04-close-agentic-rag-lab-resume-ready-v1/learning.md`
  - `.trellis/tasks/06-04-close-agentic-rag-lab-resume-ready-v1/task.json`
- 新增项目学习索引：
  - `docs/LEARNING_INDEX.md`
- 新增项目展示文档：
  - `docs/PROJECT_SHOWCASE.md`
- 更新 `README.md`，把第一屏整理为 `Resume-ready V1` 状态说明。
- 更新 `docs/TECHNICAL_NOTES.md`，把第一屏整理为技术模块边界。
- 更新根目录 `AI_AGENT_PORTFOLIO_NOTES.md`，把 `agentic-rag-lab` 标记为收口，并把下一主线切到 `ai-agent-workbench`。
- 更新 Trellis backend specs：
  - `.trellis/spec/backend/directory-structure.md`
  - `.trellis/spec/backend/quality-guidelines.md`
- 新增文档完整性测试：
  - `tests/test_project_closeout_docs.py`

## 作用是什么

之前每一步已经完成了很多能力，但学习记录更像任务流水账。对简历和面试来说，还需要回答几个更高层的问题：

- 这个项目到底是什么？
- 现在完成到什么程度？
- 完整 RAG 链路是什么？
- 每一步在链路里起什么作用？
- 哪些能力是已经实现的？
- 哪些能力还不能夸大？
- 这个项目和后续 `ai-agent-workbench` 是什么关系？

本步的作用就是把这些问题整理成稳定入口，让项目从“还在不断追加任务”变成“已经可以作为简历项目 V1 展示”。

## 用什么实现

- 用 Trellis task 文档记录本次收口 PRD 和学习结果。
- 用 `docs/LEARNING_INDEX.md` 串联全部学习步骤。
- 用 `docs/PROJECT_SHOWCASE.md` 服务简历和面试讲述。
- 用 README 顶部收口区给用户和招聘方一个快速入口。
- 用 `TECHNICAL_NOTES.md` 顶部技术总览固定模块边界。
- 用根目录 `AI_AGENT_PORTFOLIO_NOTES.md` 记录作品集层面的项目状态和下一主线。
- 用 pytest 文档测试检查关键文档是否包含：
  - `Resume-ready V1`
  - `citation-aware generation`
  - `eval provider comparison`
  - `ai-agent-workbench`
  - secret 防护约束

## 输入输出是什么

输入：

```text
已经完成的 agentic-rag-lab RAG 能力
已有 README / TECHNICAL_NOTES / AI_AGENT_PORTFOLIO_NOTES
已有 Trellis task 学习记录
已有 pytest 回归测试
```

输出：

```text
Resume-ready V1 项目状态
项目学习索引
项目展示文档
根目录作品集学习笔记更新
Trellis 收口任务记录
文档完整性测试
139 passed 验证结果
```

## 在整体 RAG 链路中的定位

本步位于功能链路之后，是项目收口和作品集沉淀：

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
-> resume-ready project closeout  <-- 本步
```

它不改变 RAG runtime 行为，但改变项目的可理解性、可复习性和简历表达边界。

## 为什么现在做

`agentic-rag-lab` 已经具备了一个学习型 RAG 项目的关键工程能力：

- 文档导入。
- chunking。
- embedding/retrieval。
- citation-aware generation。
- refusal。
- eval。
- HTTP API。
- disk-backed knowledge base。
- file/directory import。
- OpenAI-compatible providers。
- provider smoke guide。
- eval provider comparison。

继续在这个项目里扩展 UI、LangGraph、MCP 或多 agent，会让项目主线变散。现在更重要的是把它收口成简历可讲的 V1，然后进入 `ai-agent-workbench`。

## 本次没有做什么

本次没有新增：

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

这些能力不是不重要，而是不属于 `agentic-rag-lab` 的 V1 收口范围。继续做会让当前项目变成生产级平台路线，不利于快速形成简历支撑。

## 如何验证

先运行新增文档测试：

```powershell
uv run pytest tests/test_project_closeout_docs.py
```

普通权限第一次被本机 `uv` cache 权限阻塞。提升权限运行同一命令后通过：

```text
3 passed
```

再运行完整回归：

```powershell
uv run pytest
```

普通权限仍因本机 `uv` cache 权限失败：

```text
Failed to initialize cache at `C:\Users\admin\AppData\Local\uv\cache`
```

按环境规则提升权限运行同一命令后通过：

```text
139 passed
```

## 学到什么

这一步最重要的学习不是代码技巧，而是项目收口能力。

一个 AI 项目能放进简历，不只是“功能越多越好”。更重要的是：

- 能说清楚系统链路。
- 能说清楚每个模块的职责。
- 能说清楚为什么按这个顺序做。
- 能说清楚哪些能力已经验证。
- 能说清楚哪些能力还没做。
- 能避免把本地 learning baseline 夸成生产级系统。

同时也学到：Trellis/harness 在这里的价值不是替代 RAG 功能，而是约束开发过程。它让每一步都有 PRD、学习目标、实现、验证和复盘，这会成为后续 `ai-agent-workbench` 的重要工程化实践基础。

## 下一步是什么

`agentic-rag-lab` 作为简历项目 V1 暂时收口。

下一主线进入：

```text
ai-agent-workbench
```

后续 `ai-agent-workbench` 应该重点体现：

- Agent 任务规划。
- 工具调用。
- 执行观察。
- 失败恢复。
- 结果验证。
- Trellis/harness 工程化约束。
- 可审计的 Agent 工作流。

`agentic-rag-lab` 后续只建议做维护或简历需要的微调，不再继续扩展大功能。
