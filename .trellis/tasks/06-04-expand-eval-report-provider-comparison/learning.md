# 学习记录：Eval Provider Comparison

更新日期：2026-06-04

## 本步一句话总结

本步扩展 eval 能力，让同一组 `EvalCase` 可以在 baseline 和 candidate pipeline 下运行，并生成 `EvalComparisonReport` 对比差异。

## 本步做了什么

- 保留原有 `run_eval_cases()` 行为不变。
- 新增 `EvalRunConfig`。
- 新增 `run_eval_cases_with_pipeline_factory()`。
- 新增 `run_eval_cases_with_config()`。
- 新增 `EvalComparisonReport`。
- 新增 `compare_eval_reports()`。
- 新增 provider comparison 测试：
  - 自定义 pipeline factory。
  - 相同 report delta 为 0。
  - answer 变化进入 delta 和 changed case ids。
  - citation 变化进入 delta 和 changed case ids。
  - refusal 变化进入 delta 和 changed case ids。
  - case id 不一致时抛 `ValueError`。

## 作用是什么

之前 eval 只能回答一个问题：“当前本地 pipeline 是否符合预期？”

现在 provider 接入后，我们还需要回答第二个问题：“换成 candidate provider 后，结果和本地 baseline 有什么不同？”

本步的作用就是给这个问题建立最小对比结构：

```text
baseline EvalReport
candidate EvalReport
-> EvalComparisonReport
```

## 用什么实现

- `src/agentic_rag_lab/evals/basic.py`
  - 新增 provider-aware runner 和 comparison report。
- `tests/test_evals.py`
  - 新增 fake pipeline 和 report comparison 测试。
- `GeneratedAnswer`
  - 继续作为 eval 的实际输出对象。
- `EvalCase`
  - 继续作为最小评测输入。

## 输入输出是什么

输入：

```text
list[EvalCase]
baseline pipeline
candidate pipeline
```

输出：

```text
EvalComparisonReport(
    baseline_label,
    candidate_label,
    baseline_report,
    candidate_report,
    changed_case_ids,
)
```

delta 含义：

```text
candidate count - baseline count
```

例如 `answer_passed_delta=-1` 表示 candidate 比 baseline 少通过 1 条 answer 检查。

## 在整体 RAG 链路中的定位

当前链路位置：

```text
ingestion
-> chunking
-> embedding
-> retrieval
-> citation-aware generation
-> answer pipeline
-> refusal behavior
-> eval dataset / eval report
-> OpenAI-compatible providers
-> real provider manual smoke guide
-> eval provider comparison  <-- 本步
```

这一步属于 eval 层，不改变 ingestion、retrieval、generation 或 API 行为。

## 为什么现在做

真实 provider adapter 已经可选接入，manual smoke guide 也说明了如何人工验证真实服务能不能跑通。下一步自然不是马上调 prompt 或换向量库，而是先让 eval 能比较不同 provider 的输出。

这样后续如果切真实 embedding 或真实 LLM，就能观察：

- answer term 是否更容易命中。
- citation 是否仍然正确。
- refusal 行为是否被破坏。

## 设计选择

### 选择 A：pipeline factory 注入

本次采用。

优点：
- eval 不依赖具体 provider。
- 测试可以用 fake pipeline。
- 真实 provider 可以在外部 factory 中构造。
- 不复制 RAG 逻辑。

代价：
- 比原来的 `run_eval_cases()` 多一个 factory 概念。

### 选择 B：eval 内部读取 Settings

没有采用。

原因：
- eval 会和配置系统耦合。
- 测试 fake candidate provider 更麻烦。

## 本次没有做什么

- 没有联网跑真实 provider eval。
- 没有加入 latency、cost、token 指标。
- 没有做 LLM judge。
- 没有做生产级 benchmark。
- 没有做大规模 eval dataset。
- 没有做 rerank。

## 如何验证

普通权限运行：

```powershell
uv run pytest
```

普通权限下因本机 `uv` cache 权限失败。提升权限后同一命令通过：

```text
136 passed
```

## 学到什么

- eval 不只是判断“当前是否通过”，还可以比较“两个 pipeline 有什么差异”。
- provider comparison 先看 answer、citation、refusal 这三个最小信号，足够支撑学习阶段判断。
- comparison report 不是生产 benchmark，但能作为后续真实 provider tuning 的起点。
- pipeline factory 是比直接读 settings 更灵活的 eval 注入点。

## Trellis 反馈

这一步形成可复用约定：

- eval 默认入口保持稳定。
- provider-aware eval 通过 pipeline factory 注入。
- comparison report 的 delta 使用 candidate 减 baseline。
- case id 必须一致才能对比。

## 下一步是什么

下一步建议：

```text
real provider smoke execution notes
```

或者：

```text
provider quality tuning
```

前者记录一次真实 provider 手动 smoke 的实际结果；后者基于 comparison report 开始调整 provider、prompt、eval case 或 refusal threshold。

