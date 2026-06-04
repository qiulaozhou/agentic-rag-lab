# Expand Eval Report For Provider Comparison

## Goal

扩展 `agentic-rag-lab` 当前本地 eval 能力，让同一组 `EvalCase` 可以在 baseline 和 candidate provider 配置下运行，并生成 `EvalComparisonReport`。

本任务只做 deterministic comparison，不做生产级 benchmark，也不在 pytest 中访问真实 provider。

## Requirements

- 保留现有 `EvalCase`、`EvalResult`、`EvalReport` 和 `run_eval_cases()` 行为。
- 新增 provider-aware runner：
  - `EvalRunConfig`
  - `run_eval_cases_with_pipeline_factory(...)`
- 新增 comparison report：
  - `EvalComparisonReport`
  - `compare_eval_reports(...)`
- comparison report 至少包含：
  - baseline label
  - candidate label
  - baseline report
  - candidate report
  - total cases
  - passed delta
  - answer passed delta
  - citation passed delta
  - refusal passed delta
  - changed case ids
- pytest 使用 fake/mock pipeline，不请求真实网络。

## Learning Goals

- 理解 eval 不只是单次通过率，也可以比较两个 provider 输出差异。
- 理解为什么真实 provider 输出需要和本地 deterministic baseline 对比。
- 理解 provider-aware eval runner 应该复用 `LocalAnswerPipeline`，而不是复制 retrieval/generation 逻辑。
- 理解 answer、citation、refusal 是当前最小 eval 信号。

## Concepts

- eval baseline
- candidate provider
- comparison report
- pipeline factory
- answer/citation/refusal deltas
- deterministic eval

## Why Now

项目已经能可选接入 OpenAI-compatible embedding 和 LLM provider。下一步需要知道真实 provider 是否改善或改变了输出，而不是只看“能不能请求成功”。provider comparison 可以先用现有最小 eval 信号比较 baseline 和 candidate。

## Approach Options

**Option A: pipeline factory 注入（本次采用）**

- 优点：测试可以用 fake pipeline；真实 provider 可以通过外部 factory 构造；eval 不复制 RAG 逻辑。
- 代价：接口比单一 `run_eval_cases()` 多一个 factory 概念。

**Option B: eval 内部直接读取 Settings 创建 provider**

- 优点：调用更简单。
- 代价：eval 和配置耦合更重，不利于测试 fake provider。

**Option C: 只输出两个 EvalReport，不做 comparison report**

- 优点：改动少。
- 代价：调用方需要自己计算差异，学习文档不够清楚。

## Acceptance Criteria

- [ ] 现有 eval 测试继续通过。
- [ ] provider-aware runner 可以使用自定义 pipeline factory。
- [ ] 相同 reports 对比时 delta 为 0，changed case ids 为空。
- [ ] answer/citation/refusal 任一变化都能进入 changed case ids。
- [ ] comparison report 能正确计算各项 delta。
- [ ] README、TECHNICAL_NOTES、根目录学习文档说明 provider comparison 的作用和限制。
- [ ] `uv run pytest` 通过，或环境级失败被记录。

## Out of Scope

- 真实 provider 自动联网评测。
- 生产级 RAG benchmark。
- latency/cost/token 指标。
- LLM judge。
- rerank。
- UI、MCP、LangGraph、多 agent。

## Out of Scope for Learning

- 长期指标趋势。
- 大规模评测集管理。
- 模型质量统计学分析。
- provider 成本归因。

