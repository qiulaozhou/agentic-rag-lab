# 学习记录

更新日期：2026-06-03

## 本步一句话总结

这一步给 `agentic-rag-lab` 增加了第一个本地 eval 闭环，让系统可以用小型评估集检查 answer、citation 和 refusal 是否符合预期。

## 本步做了什么

本次新增了最小 eval 能力：

```text
EvalCase
-> LocalAnswerPipeline.answer()
-> GeneratedAnswer
-> answer/citation/refusal checks
-> EvalResult
-> EvalReport
```

新增能力：

- `EvalCase`：描述一个问题、输入文档和预期结果。
- `EvalResult`：记录单条 case 的实际答案和各项检查结果。
- `EvalReport`：汇总 total、passed、failed 和分项通过数。
- `run_eval_cases()`：离线运行一组 eval cases。

## 作用是什么

RAG 项目不能只靠手动问几个问题来判断质量。现在项目已经能检索、引用、回答和拒答，下一步必须开始验证这些行为是否稳定。

本步的作用是把“感觉能用”变成“有可重复的检查结果”：

- answer 是否包含预期关键词。
- citation 是否命中预期来源。
- refusal 是否符合预期。

## 用什么实现

代码使用这些已有边界：

- `SourceDocument`：作为 eval case 的输入文档。
- `LocalAnswerPipeline`：运行当前 RAG 问答闭环。
- `GeneratedAnswer`：作为 eval 检查对象。
- `GeneratedAnswer.citations`：检查 citation。
- `GeneratedAnswer.refused`：检查 refusal。

新增实现：

- `src/agentic_rag_lab/evals/basic.py`
- `EvalCase`
- `EvalResult`
- `EvalReport`
- `run_eval_cases`

它是确定性的本地 heuristic eval，不调用真实 LLM，不访问网络，不新增依赖。

## 输入输出

输入：

```text
list[EvalCase]
chunk_size
overlap
```

单条 case 包含：

```text
id
question
documents
expected_refused
expected_citations
required_answer_terms
```

输出：

```text
EvalReport(
    results=[EvalResult(...)]
)
```

report 可读取：

```text
total
passed
failed
answer_passed
citation_passed
refusal_passed
```

## 在整体流程中的定位

当前项目整体链路已经推进到：

```text
Markdown/TXT file
-> SourceDocument
-> DocumentChunk
-> LocalHashEmbeddingProvider
-> InMemoryVectorStore
-> LocalRetrievalPipeline.search()
-> MinimumEvidenceRefusalPolicy
-> CitationAwareAnswerGenerator.answer()
-> LocalAnswerPipeline.answer()
-> EvalCase expectation checks
-> EvalReport
```

这一步位于 refusal behavior 之后。它说明第一阶段 RAG 核心闭环已经具备最小可运行和可评估版本。

## 为什么现在做

前面已经完成：

- ingestion。
- chunking。
- embedding。
- retrieval。
- citation-aware generation。
- answer pipeline。
- refusal behavior。

现在如果继续做 UI、真实 LLM 或 MCP，会缺少质量反馈。先做 eval，可以让后续每个能力都有回归依据。

## 设计选择

本次采用 dataclass + Python fixture eval。

考虑过的方案：

- dataclass + Python fixture：本次采用。最小、离线、可测试，适合当前学习阶段。
- JSONL loader：暂缓。后续 eval case 变多后再做更合适。
- LLM-as-judge：暂缓。需要真实模型、prompt、成本和稳定性控制。

## 本次没有做什么

本任务没有做：

- JSONL loader。
- CLI eval command。
- Markdown/HTML report 文件输出。
- LLM-as-judge。
- 生产级 benchmark。
- latency / cost metrics。
- real provider。
- Web UI。
- LangGraph。
- MCP。
- multi-agent orchestration。

这些能力可以在最小 eval 闭环稳定后再扩展。

## 如何验证

先运行普通命令：

```powershell
uv run pytest
```

普通权限下仍然因为本机 `uv` cache 权限失败：

```text
error: Failed to initialize cache at `C:\Users\admin\AppData\Local\uv\cache`
  Caused by: failed to open file `C:\Users\admin\AppData\Local\uv\cache\sdists-v9\.git`: 拒绝访问。 (os error 5)
```

随后用提升权限运行同一个命令，最终结果：

```text
65 passed
```

## 学到什么

- eval 的第一步不是复杂模型评判，而是先把可检查的预期结果结构化。
- answer、citation、refusal 是三个不同指标，应该分别统计。
- eval report 是后续迭代的反馈入口：以后改 retrieval、refusal 或 generation 时，可以看哪些 case 退化。
- 当前的关键词检查是学习阶段 heuristic，不代表生产级语义准确率。

## Trellis 反馈

本次继续符合增强后的学习型 Trellis 约束：

- PRD 先说明学习目标、Why Now 和 out-of-scope。
- 实现保持最小本地闭环。
- 测试覆盖正常回答、citation、拒答和失败统计。
- 文档同步说明本步做了什么、作用、工具、输入输出、定位、验证和下一步。

已同步更新 backend specs：

- `.trellis/spec/backend/directory-structure.md`
- `.trellis/spec/backend/quality-guidelines.md`

## 下一步学习

下一步建议任务：

```text
HTTP answer API boundary
```

原因是当前第一阶段 RAG 核心链路已经具备最小可运行和可评估版本。下一步可以把内部 `LocalAnswerPipeline` 暴露成最小 HTTP answer endpoint，但仍然不需要跳到 UI、Workbench、MCP、LangGraph 或多 agent。
