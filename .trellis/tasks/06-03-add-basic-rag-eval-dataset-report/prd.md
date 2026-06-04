# Add Basic RAG Eval Dataset And Report

## Goal

实现第一个本地、确定性、可测试的 RAG eval 闭环：

```text
EvalCase
-> LocalAnswerPipeline.answer()
-> GeneratedAnswer
-> expectation checks
-> EvalReport
-> pytest
```

本任务只做学习阶段最小 eval，不做生产级 benchmark。

## Requirements

- 在 `agentic_rag_lab.evals` 下新增最小 eval 能力。
- 新增 `EvalCase`。
- 新增 `EvalResult`。
- 新增 `EvalReport`。
- 新增 `run_eval_cases(cases, chunk_size, overlap=0)`。
- 使用现有 `LocalAnswerPipeline`，不重新实现 retrieval、generation 或 refusal。
- 检查 answer terms、citations 和 refusal。
- 不新增第三方依赖。
- 不改变 `GeneratedAnswer`、`RetrievalResult`、`SourceDocument` schema。

## Learning Goals

- 理解为什么 RAG 需要系统化 eval，而不是只靠手动问几个问题。
- 理解 answer accuracy、citation accuracy、refusal accuracy 的区别。
- 理解 eval case 如何把“问题、文档、预期结果”绑定在一起。
- 理解 eval report 如何成为后续迭代的反馈入口。
- 继续练习中文详细学习记录：做了什么、作用、工具、输入输出、流程定位、验证和下一步。

## Concepts

- eval dataset
- eval report
- answer term check
- citation check
- refusal check
- deterministic heuristic eval
- regression guard

## Why Now

项目已经完成：

- ingestion。
- chunking。
- local embedding。
- retrieval。
- citation-aware generation。
- answer pipeline。
- refusal behavior。

现在系统能跑完整问答，也能在证据不足时拒答。下一步应该开始评估这些能力是否可靠，而不是继续堆 UI、真实 LLM、MCP 或多 agent。

## Approach Options

**Option A: dataclass + Python fixture eval**（本次采用）

- 优点：离线、确定性、无新依赖，适合当前学习阶段。
- 代价：不是通用 benchmark 格式。

**Option B: JSONL fixture loader**

- 优点：更接近真实 eval dataset。
- 代价：需要先设计文件格式和 loader，当前可以后置。

**Option C: LLM-as-judge**

- 优点：能评估更复杂的语义正确性。
- 代价：需要真实模型、prompt、成本和稳定性控制，当前过早。

## Acceptance Criteria

- [ ] 正常回答 case 能通过 answer、citation、refusal 检查。
- [ ] 无关问题 case 能通过 refusal 检查。
- [ ] 空问题 case 能通过 refusal 检查。
- [ ] citation 不匹配时 case 失败。
- [ ] required answer term 缺失时 case 失败。
- [ ] report 能正确统计 total、passed、failed、answer_passed、citation_passed、refusal_passed。
- [ ] `uv run pytest` 通过，或环境级失败被记录到 `learning.md`。

## Definition of Done

- eval dataclass 和 runner 完成。
- 单元测试和端到端测试完成。
- README、技术笔记、根目录学习笔记同步更新为中文。
- Trellis backend specs 记录 reusable eval 约定。
- 本任务 `learning.md` 记录概念、设计选择、验证结果和下一步。

## Technical Approach

- 新增 `src/agentic_rag_lab/evals/basic.py`。
- `EvalCase` 包含：
  - `id`
  - `question`
  - `documents`
  - `expected_refused`
  - `expected_citations`
  - `required_answer_terms`
- `run_eval_cases()` 为每个 case 构建 `LocalAnswerPipeline.from_documents()`。
- 非拒答 case 检查 required answer terms 和 expected citations。
- 拒答 case 只检查 `GeneratedAnswer.refused`，不要求 answer terms 或 citations。
- `EvalReport` 汇总每个分项通过数。

## Decision (ADR-lite)

**Context**：当前 RAG 闭环已经能回答、引用和拒答，但没有系统化评估入口。

**Decision**：先做 dataclass + deterministic checks，不做 JSONL loader 或 LLM judge。

**Consequences**：项目具备第一个可重复 eval 闭环。后续可以把 case 存成 JSONL、扩展指标、或引入真实模型评估。

## Out of Scope

- JSONL loader。
- CLI eval command。
- HTML/Markdown report file 输出。
- LLM-as-judge。
- 生产级 benchmark。
- latency / cost metrics。
- real provider。
- Web UI。
- LangGraph。
- MCP。
- multi-agent orchestration。

## Out of Scope for Learning

- 复杂语义等价判断。
- 大规模评测集维护。
- eval dashboard。
- 模型间对比。
- 线上监控。

## Technical Notes

- Relevant specs:
  - `.trellis/spec/backend/directory-structure.md`
  - `.trellis/spec/backend/quality-guidelines.md`
  - `.trellis/spec/guides/learning-mode-guide.md`
- Relevant code:
  - `src/agentic_rag_lab/evals/__init__.py`
  - `src/agentic_rag_lab/generation/pipeline.py`
  - `src/agentic_rag_lab/schemas.py`
