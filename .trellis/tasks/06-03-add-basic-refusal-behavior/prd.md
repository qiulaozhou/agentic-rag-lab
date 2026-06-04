# Add Basic Refusal Behavior

## Goal

实现一个基础 refusal boundary，让系统在证据不足时不要继续生成看似有依据的答案：

```text
question
-> LocalAnswerPipeline.answer()
-> LocalRetrievalPipeline.search()
-> RefusalPolicy
-> CitationAwareAnswerGenerator.answer()
-> GeneratedAnswer(refused=True/False)
-> pytest
```

本任务只做确定性、本地、可测试的最小 refusal 行为，不做生产级拒答策略。

## Requirements

- 新增 `generation/refusal.py`。
- 新增 `RefusalPolicy` protocol。
- 新增 `MinimumEvidenceRefusalPolicy`。
- 更新 `LocalAnswerPipeline`，在 retrieval 之后、generation 之前执行 refusal 判断。
- 拒答时直接返回 `GeneratedAnswer(refused=True, citations=[])`。
- 默认拒答文案为：`当前知识库没有足够依据回答这个问题。`
- 不改变 `GeneratedAnswer` schema。
- 不改变 embedding、retrieval ranking、citation 格式或真实 LLM 边界。
- 不新增 HTTP endpoint、UI、LangGraph、MCP、eval report 或多 agent。

## Learning Goals

- 理解为什么 RAG 不能在证据不足时继续回答。
- 理解空 evidence 最小保护和更完整 refusal policy 的区别。
- 理解 refusal 应该发生在 retrieval 之后、generation 之前。
- 理解 `GeneratedAnswer.refused` 在当前链路里的作用。
- 继续练习中文详细学习记录：做了什么、作用、工具、输入输出、流程定位、验证和下一步。

## Concepts

- refusal behavior
- refusal policy
- evidence threshold
- `GeneratedAnswer.refused`
- reliability boundary
- deterministic local policy

## Why Now

项目已经完成：

- Markdown/TXT ingestion。
- deterministic chunking。
- local hash embedding。
- in-memory vector retrieval。
- citation-aware generation。
- internal answer pipeline。

现在 `LocalAnswerPipeline.answer()` 已经是统一问答入口。下一步自然是在这个入口里加入 refusal policy，让系统能在证据不足时停止生成。否则后续 eval 会发现系统仍然可能对低质量 evidence 给出答案。

## Approach Options

**Option A: `MinimumEvidenceRefusalPolicy`**（本次采用）

- 优点：离线、确定性、无新依赖，可以测试 refusal 位置和边界。
- 代价：阈值是学习阶段的工程规则，不是生产级质量判断。

**Option B: 在 `CitationAwareAnswerGenerator` 里继续扩展拒答**

- 优点：少一个类。
- 代价：会把 evidence 质量判断和答案生成混在一起，不利于后续 eval 或替换策略。

**Option C: 用真实 LLM judge 判断是否拒答**

- 优点：更接近真实产品。
- 代价：需要模型调用、prompt、成本和不稳定输出，当前过早。

## Acceptance Criteria

- [ ] 空 query 返回 `refused=True`。
- [ ] evidence 为空返回 `refused=True`。
- [ ] 最高 score 低于 `0.25` 返回 `refused=True`。
- [ ] 最高 score 等于或高于 `0.25` 允许生成。
- [ ] 自定义 `min_score` 能改变判断结果。
- [ ] `LocalAnswerPipeline` 默认使用 `MinimumEvidenceRefusalPolicy`。
- [ ] `LocalAnswerPipeline` 支持传入自定义 refusal policy。
- [ ] `limit <= 0` 仍抛 `ValueError`。
- [ ] 高相关 query 仍返回 citation。
- [ ] `uv run pytest` 通过，或环境级失败被记录到 `learning.md`。

## Definition of Done

- refusal policy 代码和导出完成。
- 单元测试和 answer pipeline 测试完成。
- README、技术笔记、根目录学习笔记同步更新为中文。
- Trellis backend specs 记录 reusable refusal policy 约定。
- 本任务 `learning.md` 记录概念、设计选择、验证结果和下一步。

## Technical Approach

- 新增 `src/agentic_rag_lab/generation/refusal.py`。
- `RefusalPolicy.should_refuse(question, evidence)` 返回 bool。
- `MinimumEvidenceRefusalPolicy(min_score=0.25)` 使用最高 evidence score 判断。
- `LocalAnswerPipeline.__init__()` 增加 `refusal_policy=None`。
- `from_chunks()` 和 `from_documents()` 透传 `refusal_policy`。
- `answer()` 流程变为：

```text
evidence = await retriever.search(...)
if refusal_policy.should_refuse(...):
    return GeneratedAnswer(text=DEFAULT_REFUSAL_TEXT, citations=[], refused=True)
return await answer_generator.answer(...)
```

## Decision (ADR-lite)

**Context**：answer pipeline 已经能返回 `GeneratedAnswer`，但还没有明确的 evidence 质量门槛。

**Decision**：新增独立 `MinimumEvidenceRefusalPolicy`，让 refusal 成为 retrieval 和 generation 之间的明确边界。

**Consequences**：后续 eval 可以单独评估 refusal accuracy，也可以替换 policy，而不需要改 citation-aware generator。

## Out of Scope

- 真实 LLM judge。
- prompt-based refusal。
- confidence score schema。
- eval dataset / eval report。
- rerank。
- HTTP answer endpoint。
- Web UI。
- LangGraph。
- MCP。
- multi-agent orchestration。

## Out of Scope for Learning

- 生产级阈值调优。
- citation accuracy 评估。
- 多证据一致性判断。
- answer factuality scoring。
- 复杂用户意图分类。

## Technical Notes

- Relevant specs:
  - `.trellis/spec/backend/directory-structure.md`
  - `.trellis/spec/backend/quality-guidelines.md`
  - `.trellis/spec/guides/learning-mode-guide.md`
- Relevant code:
  - `src/agentic_rag_lab/generation/pipeline.py`
  - `src/agentic_rag_lab/generation/citation.py`
  - `src/agentic_rag_lab/schemas.py`
