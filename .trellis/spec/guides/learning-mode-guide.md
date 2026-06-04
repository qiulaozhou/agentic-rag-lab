# 学习型 Trellis 工作指南

> **目的**：让每一次开发都同时成为可复习的 AI Agent 工程学习资料，而不是只留下代码和测试。

---

## 适用范围

本仓库里的每个 Trellis 任务都必须使用这个学习流程。默认顺序是：

1. 先写 PRD 和学习目标。
2. 再说明本步在整体路线里的位置。
3. 实现最小可运行闭环。
4. 用 pytest 或其他明确命令验证。
5. 写中文 `learning.md`。
6. 同步更新项目学习文档和根目录学习文档。
7. 判断是否需要更新长期 spec。

这条规则尤其适用于容易发散的话题，例如 UI、Agent Loop、LangGraph、MCP、真实 LLM、向量数据库、多 agent 或工作流自动化。

---

## 每一步必须讲清楚什么

每个任务完成后，`learning.md`、项目学习文档和根目录学习文档都要尽量回答这些问题：

- **本步做了什么**：新增了哪些能力，形成了哪条最小闭环。
- **作用是什么**：这一步解决了 RAG 或 Agent 工程中的哪个问题。
- **用什么去做**：使用了哪些模块、类、函数、测试命令或工具。
- **输入输出是什么**：数据从什么结构进入，经过什么处理，最后输出什么结构。
- **在整体流程中的定位**：它位于 `ingestion -> chunking -> embedding -> retrieval -> generation -> refusal -> eval` 的哪一段。
- **为什么现在做**：它依赖了哪个已完成能力，又为哪个后续能力铺路。
- **没有做什么**：明确排除的范围，以及为什么现在不做。
- **如何验证**：运行了什么命令，期望结果是什么，实际结果是什么。
- **学到什么**：本步抽象出来的概念、工程边界或可复用约定。
- **下一步是什么**：下一步为什么自然接在这里，而不是跳到别的项目或大功能。

不要只写“实现了某某功能”。学习文档要让后来复习的人能看懂：为什么这个功能按这个顺序出现，为什么用这个最小实现，而不是更复杂的生产方案。

---

## Required Learning Loop

### 1. Concept / 核心概念

说明本任务练习的核心概念。

示例：

- FastAPI app factory and health-check boundary。
- Markdown/TXT ingestion and chunking。
- Embedding adapter boundary。
- Retrieval pipeline / API boundary。
- Citation-aware answer generation。

### 2. Why Now / 为什么现在做

说明本任务为什么属于当前阶段。

必须讲清楚：

- 它建立在哪个已完成任务之上。
- 它为哪个后续任务铺路。
- 为什么不跳到 UI、Agent Loop、LangGraph、MCP、真实 LLM 或多 agent。

### 3. Design Choice / 设计选择

如果存在有意义的技术选择，记录 2-3 个方案，并说明本次采用哪个。

设计选择要和当前里程碑匹配。早期任务优先选择离线、确定性、可测试的最小方案，等边界清楚后再引入真实 provider、数据库或复杂框架。

### 4. Implementation / 实现

实现能证明概念的最小可运行闭环。

不要因为某个框架或抽象“以后可能有用”就提前引入。只有当前验收标准需要时，才新增依赖、抽象或 endpoint。

### 5. Verification / 验证

验证必须证明行为能跑通，而不是只证明文件存在。

记录：

- 运行命令。
- 期望结果。
- 实际结果。
- 如果失败，失败原因是代码问题还是环境问题。
- 如果使用提升权限重跑，要记录原因和最终结果。

### 6. Learning Note / 学习记录

每个已完成任务必须留下：

```text
.trellis/tasks/<task>/learning.md
```

`learning.md` 使用中文，推荐结构：

```markdown
# 学习记录

更新日期：YYYY-MM-DD

## 本步一句话总结

## 本步做了什么

## 作用是什么

## 用什么实现

## 输入输出

## 在整体流程中的定位

## 为什么现在做

## 设计选择

## 本次没有做什么

## 如何验证

## 学到什么

## Trellis 反馈

## 下一步学习
```

可以根据任务大小增减小节，但上面的信息不能缺失。

### 7. Project Notes / 项目学习文档

任务完成后，必须更新项目内学习文档，例如：

```text
README.md
docs/TECHNICAL_NOTES.md
```

这些文档不是流水账，而是给当前项目学习者看的复习入口。更新时要讲清楚本步能力在项目里的作用。

### 8. Portfolio Notes / 根目录学习文档

任务完成后，必须更新根目录：

```text
D:\zrf\aiProject\AI_AGENT_PORTFOLIO_NOTES.md
```

根目录文档要从三个项目整体路线解释当前进度，特别要说明为什么现在仍然在 `agentic-rag-lab`，而不是切到 `ai-agent-workbench` 或 `mcp-devtools-server`。

### 9. Trellis Feedback / Trellis 反馈

任务末尾判断 Trellis 本身是否需要更新：

- 一次性实现细节 -> 写在本任务 `learning.md`。
- 可复用代码约定 -> 更新 `.trellis/spec/backend/*`。
- 可复用学习或推理习惯 -> 更新 `.trellis/spec/guides/*`。

---

## PRD 必填字段

每个任务 PRD 必须包含：

- `Learning Goals`
- `Concepts`
- `Why Now`
- `Approach Options`
- `Out of Scope for Learning`

如果 PRD 只写“要做什么”，没有解释“这次学什么、为什么现在学、什么暂时不学”，就不完整。

---

## Pre-Code Explanation

写代码前要简短告诉用户：

- 本任务练习的概念。
- 当前采用的设计选择。
- 要构建的最小闭环。
- 明确不做的范围。

说明要短，但必须能让用户知道这一步在学习路线中的位置。

---

## Completion Checklist

- [ ] PRD 写明学习目标和核心概念。
- [ ] PRD 解释为什么现在做。
- [ ] 有意义的方案选择已记录。
- [ ] 实现形成最小可运行闭环。
- [ ] 新行为有测试覆盖。
- [ ] 验证命令和结果被记录。
- [ ] 当前任务有中文 `learning.md`。
- [ ] 项目 README 或技术笔记已更新。
- [ ] 根目录 `AI_AGENT_PORTFOLIO_NOTES.md` 已更新。
- [ ] Trellis feedback 已记录，必要时已更新 spec。
