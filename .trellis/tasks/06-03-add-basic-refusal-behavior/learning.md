# 学习记录

更新日期：2026-06-03

## 本步一句话总结

这一步给 `LocalAnswerPipeline` 增加了基础 refusal behavior，让系统在 query 为空、没有 evidence、或 evidence 分数明显不足时返回 `refused=True`，而不是继续生成看似有依据的答案。

## 本步做了什么

本次新增了 refusal policy 边界：

```text
question
-> LocalAnswerPipeline.answer()
-> LocalRetrievalPipeline.search()
-> MinimumEvidenceRefusalPolicy.should_refuse()
-> CitationAwareAnswerGenerator.answer()
-> GeneratedAnswer(refused=True/False)
```

新增能力：

- `RefusalPolicy` protocol。
- `MinimumEvidenceRefusalPolicy`。
- `DEFAULT_REFUSAL_TEXT`。
- `refused_answer()`。
- `LocalAnswerPipeline` 支持默认和自定义 refusal policy。

## 作用是什么

RAG 系统不能只要检索到一点内容就回答。证据不足时继续回答，会让用户误以为答案有来源支持。

本步的作用是给问答链路加一道“证据门槛”：检索之后先判断 evidence 是否足够，再决定是否进入 generation。这样后续 eval 才能评估“什么时候应该回答、什么时候应该拒答”。

## 用什么实现

代码使用这些已有边界：

- `LocalAnswerPipeline`：内部问答入口。
- `LocalRetrievalPipeline`：返回 `RetrievalResult`。
- `GeneratedAnswer`：用 `refused` 字段表达是否拒答。
- `CitationAwareAnswerGenerator`：只在不拒答时生成答案。

新增实现：

- `src/agentic_rag_lab/generation/refusal.py`
- `MinimumEvidenceRefusalPolicy(min_score=0.25)`

这个 policy 是确定性的本地规则，不调用真实 LLM，不访问网络，不新增依赖。

## 输入输出

输入：

```text
question: str
evidence: list[RetrievalResult]
```

refusal policy 判断：

```text
空 query -> 拒答
evidence 为空 -> 拒答
最高 score < 0.25 -> 拒答
最高 score >= 0.25 -> 允许生成
```

拒答输出：

```text
GeneratedAnswer(
    text="当前知识库没有足够依据回答这个问题。",
    citations=[],
    refused=True,
)
```

非拒答输出继续由 `CitationAwareAnswerGenerator` 生成：

```text
GeneratedAnswer(text, citations, refused=False)
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
-> GeneratedAnswer
```

这一步位于 answer pipeline 之后、eval 之前。它先把“是否应该回答”的边界固定下来，后续 eval 才能评估 refusal accuracy。

## 为什么现在做

上一阶段已经完成内部问答入口。如果没有 refusal policy，后续所有调用方都会得到一个答案，即使 evidence 很弱。

现在先做基础 refusal，可以让后续 eval 有明确对象：

- 该回答时是否回答。
- 不该回答时是否拒答。
- citation 是否只在有足够 evidence 时出现。

## 设计选择

本次选择独立 `MinimumEvidenceRefusalPolicy`。

考虑过的方案：

- 独立 policy：本次采用。它让 refusal 可以单独测试、单独替换。
- 写进 `CitationAwareAnswerGenerator`：暂缓。这样会混合 evidence 质量判断和答案生成。
- 用真实 LLM judge：暂缓。它需要 prompt、成本、模型稳定性和更多测试设计。

默认 `min_score=0.25` 是当前本地 hash embedding 阶段的学习阈值，不是生产标准。后续 eval 可以调整。

## 本次没有做什么

本任务没有做：

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

这些能力都应该建立在基础 refusal 边界稳定之后。

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
59 passed
```

## 学到什么

- refusal 应该发生在 retrieval 之后、generation 之前。
- `GeneratedAnswer.refused` 是当前系统表达“是否回答”的最小输出边界。
- 空 evidence 兜底和 evidence quality policy 是两层不同能力。
- 把 refusal 做成独立 policy，后续可以替换成 eval-driven policy、rerank-based policy 或 LLM judge，而不用改 answer pipeline 主流程。

## Trellis 反馈

本次继续符合增强后的学习型 Trellis 约束：

- PRD 先说明学习目标和为什么现在做。
- 实现保持最小本地闭环。
- 测试覆盖 policy 和 pipeline。
- 文档同步说明本步做了什么、作用、工具、输入输出、定位、验证和下一步。

已同步更新 backend specs：

- `.trellis/spec/backend/directory-structure.md`
- `.trellis/spec/backend/quality-guidelines.md`

## 下一步学习

下一步建议任务：

```text
eval dataset / eval report
```

原因是当前系统已经有 retrieval、citation、answer pipeline 和 refusal。下一步应该开始评估它们是否工作得好，而不是继续堆 UI、真实 LLM、MCP 或多 agent。
