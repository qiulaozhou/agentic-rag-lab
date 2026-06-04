# 学习记录

更新日期：2026-06-03

## 本步一句话总结

这一步把 `LocalRetrievalPipeline.search()` 和 `CitationAwareAnswerGenerator.answer()` 组合成了 `LocalAnswerPipeline.answer()`，让项目从“检索 + 带引用生成两个独立能力”推进到“内部问答边界”。

## 本步做了什么

本次新增了 `LocalAnswerPipeline`：

```text
question
-> LocalAnswerPipeline.answer()
-> LocalRetrievalPipeline.search()
-> CitationAwareAnswerGenerator.answer()
-> GeneratedAnswer
```

它提供两个便捷构造入口：

- `LocalAnswerPipeline.from_chunks()`
- `LocalAnswerPipeline.from_documents()`

这样调用方可以直接问问题，不需要自己手动写 retrieval 和 generation 的组合代码。

## 作用是什么

上一阶段已经能先检索 evidence，再生成带 citation 的答案，但调用方还要自己拼这两步。

本步的作用是把这个组合收进一个内部问答边界里。后续如果要做 HTTP answer endpoint、refusal behavior 或 eval，就可以统一调用 `LocalAnswerPipeline.answer()`，而不是在每个地方重复拼底层流程。

## 用什么实现

代码使用这些已有边界：

- `Retriever`：负责 `search(query, limit)`。
- `LocalRetrievalPipeline`：本地检索实现。
- `AnswerGenerator`：负责从 evidence 生成 `GeneratedAnswer`。
- `CitationAwareAnswerGenerator`：当前本地确定性生成器。
- `GeneratedAnswer`：当前问答闭环的输出结构。

新增实现：

- `src/agentic_rag_lab/generation/pipeline.py`
- `LocalAnswerPipeline`

它仍然不调用真实 LLM，不访问网络，不新增第三方依赖。

## 输入输出

输入：

```text
question: str
limit: int = 5
```

内部处理：

```text
question
-> retriever.search(question, limit)
-> list[RetrievalResult]
-> answer_generator.answer(question, evidence)
-> GeneratedAnswer
```

输出：

```text
GeneratedAnswer(text, citations, refused)
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
-> CitationAwareAnswerGenerator.answer()
-> LocalAnswerPipeline.answer()
-> GeneratedAnswer
```

这一步位于 citation-aware generation 之后、refusal 和 eval 之前。它不是新的生成策略，而是把已有能力组合成一个更稳定的内部 QA 边界。

## 为什么现在做

现在 retrieval 和 citation-aware generation 都已经完成。如果不先做 answer pipeline，后续 HTTP endpoint、refusal 和 eval 都会各自手动拼：

```python
evidence = await retriever.search(question)
answer = await generator.answer(question, evidence)
```

这会让组合逻辑散落在多个地方。现在先收成一个 pipeline，后续每个能力都能站在同一个问答入口上继续推进。

## 设计选择

本次选择把 `LocalAnswerPipeline` 放在 `generation/pipeline.py`。

考虑过的方案：

- `generation/pipeline.py`：本次采用。输出是 `GeneratedAnswer`，且当前没有独立 application 层。
- 新增 `application/` 或 `qa/` 层：暂缓。项目还小，过早增加层级。
- 新增 FastAPI endpoint：暂缓。HTTP 请求/响应、错误码和文档输入方式需要单独设计。

## 本次没有做什么

本任务没有做：

- FastAPI answer endpoint。
- 请求/响应 DTO。
- 真实 LLM。
- prompt engineering。
- 复杂 refusal policy。
- eval dataset / eval report。
- rerank。
- production vector database。
- Web UI。
- LangGraph。
- MCP。
- multi-agent orchestration。

这些能力都应该建立在内部问答边界稳定之后。

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

随后用提升权限运行同一个命令。第一次发现一个测试断言过窄：answer pipeline 默认可能使用多条 evidence，所以 citation 不一定只有一条。已把该测试改成 `limit=1`，让它专门验证 limit 传递和首条 citation。

最终验证结果：

```text
50 passed
```

## 学到什么

- answer pipeline 的职责是组合，不是重写 retrieval 或 generation。
- `Retriever` 和 `AnswerGenerator` protocol 已经足够支撑内部问答边界。
- 内部 API boundary 可以先用 Python class 证明行为，不需要马上做 HTTP endpoint。
- 测试要匹配真实 contract：默认 limit 允许多条 evidence，就不能断言只返回一个 citation。

## Trellis 反馈

本次继续沿用增强后的中文学习模板。需要沉淀到 backend specs 的可复用约定是：

- answer pipeline 负责组合 retrieval 和 generation。
- answer pipeline 不复制检索排序、embedding 或 citation 规则。
- 早期 answer pipeline 不需要真实 LLM 或 HTTP endpoint。

已同步更新：

- `.trellis/spec/backend/directory-structure.md`
- `.trellis/spec/backend/quality-guidelines.md`

## 下一步学习

下一步建议任务：

```text
refusal behavior
```

原因是现在系统已经有了内部问答入口，下一步应该学习“什么时候不应该回答”。eval dataset / eval report 也可以排在后面，但最好先有更明确的 refusal 行为，再评估 refusal accuracy。
