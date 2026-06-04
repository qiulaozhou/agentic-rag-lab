# 学习记录

更新日期：2026-06-03

## 本步一句话总结

这一步把 retrieval 返回的 `RetrievalResult` 转成了带来源引用的 `GeneratedAnswer`，让本地 RAG 链路从“能检索片段”推进到“能基于片段生成可追溯回答”。

## 本步做了什么

本次新增了 `CitationAwareAnswerGenerator`：

```text
list[RetrievalResult]
-> CitationAwareAnswerGenerator.answer()
-> GeneratedAnswer(text, citations, refused)
```

同时新增了 generation 单元测试和 retrieval + generation 端到端测试，并更新了 Trellis 学习约束、项目文档和根目录学习文档。

## 作用是什么

RAG 的关键不是只把相关 chunk 找出来，而是让回答能说明依据来自哪里。

如果只有 retrieval，系统最多只能返回一些片段；用户还需要自己判断这些片段是否支持答案。本步的作用是把检索结果整理成回答结构，并把来源写入 `GeneratedAnswer.citations`，为后续真实 LLM、拒答策略和 eval 打基础。

## 用什么实现

代码使用这些现有边界：

- `RetrievalResult`：检索命中的 chunk 和 score。
- `DocumentChunk.metadata`：保存 `source_path`、`file_type`、`chunk_index` 等来源信息。
- `GeneratedAnswer`：保存回答文本、引用列表和拒答状态。
- `LocalRetrievalPipeline`：端到端测试中负责从文档检索 evidence。

新增实现：

- `src/agentic_rag_lab/generation/citation.py`
- `CitationAwareAnswerGenerator`

它是一个确定性本地生成器，不调用真实 LLM，不访问网络，不引入第三方依赖。

## 输入输出

输入：

```text
question: str
evidence: list[RetrievalResult]
```

处理：

```text
取前 3 条 evidence
-> 归一化 chunk text
-> 截取 evidence 摘要
-> 从 metadata 生成 citation
-> citation 去重并保持顺序
```

输出：

```text
GeneratedAnswer(
    text="基于检索到的资料...",
    citations=["docs/rag.md#chunk-0"],
    refused=False,
)
```

如果 `evidence` 为空，输出：

```text
GeneratedAnswer(
    text="当前知识库没有足够依据回答这个问题。",
    citations=[],
    refused=True,
)
```

## 在整体流程中的定位

当前 RAG 学习链路已经推进到：

```text
Markdown/TXT file
-> SourceDocument
-> DocumentChunk
-> LocalHashEmbeddingProvider
-> InMemoryVectorStore
-> LocalRetrievalPipeline.search()
-> RetrievalResult
-> CitationAwareAnswerGenerator.answer()
-> GeneratedAnswer
```

这一步位于 retrieval 之后、refusal 和 eval 之前。它不是最终的生产级回答质量方案，而是先固定“回答必须有 evidence 和 citation”这个工程边界。

## 为什么现在做

上一阶段已经完成 `LocalRetrievalPipeline.search()`，它能返回带 metadata 的 `RetrievalResult`。如果下一步直接做 UI、真实 LLM 或 eval，就会缺少一个关键中间层：检索结果如何变成可追溯答案。

现在做 citation-aware generation，可以把前面保留的 `source_path` 和 `chunk_index` 真正用起来，也能为后续 eval 提供可检查的 citation 输出。

## 设计选择

本次采用确定性本地生成器。

考虑过的方案：

- 确定性本地生成器：本次采用。优点是离线、稳定、可测试，能专注验证 citation contract。
- 使用 `FakeLLMProvider`：暂缓。当前 fake provider 只是 echo prompt，不适合证明 citation 规则。
- 接真实 LLM：暂缓。会引入 API key、成本、prompt 设计和不稳定输出，不适合当前最小闭环。

## 本次没有做什么

本任务没有做：

- HTTP answer endpoint。
- 真实 LLM。
- prompt engineering。
- production answer quality。
- confidence score。
- 复杂拒答策略。
- eval dataset / eval report。
- UI、LangGraph、MCP 或多 agent。

这些能力都重要，但它们应该建立在“检索结果能稳定变成带引用答案”之后。

## 如何验证

先运行普通命令：

```powershell
uv run pytest
```

普通权限下失败，原因仍然是本机 `uv` cache 权限：

```text
error: Failed to initialize cache at `C:\Users\admin\AppData\Local\uv\cache`
  Caused by: failed to open file `C:\Users\admin\AppData\Local\uv\cache\sdists-v9\.git`: 拒绝访问。 (os error 5)
```

随后用提升权限运行同一个命令。第一次发现端到端测试里对 chunk 排序的假设过窄，已修正为单 chunk fixture，让该测试专注验证 citation 追溯。

最终验证结果：

```text
44 passed
```

## 学到什么

- citation 不应该由 generation 随意编写，而应该从 `DocumentChunk.metadata` 或稳定 chunk id 派生。
- `RetrievalResult` 是 retrieval 和 generation 的边界对象，generation 不应该重新进入 vector store 内部。
- 空 evidence 时必须有最小拒答保护，否则 RAG 会在没有依据时编答案。
- 端到端测试要验证当前层的职责，不要把 retrieval 排序细节和 generation citation 追溯混在一个断言里。

## Trellis 反馈

本次 Trellis 需要优化，因为用户明确要求学习文档讲得更细。

已更新：

- `.trellis/spec/guides/learning-mode-guide.md`
- `.trellis/spec/backend/directory-structure.md`
- `.trellis/spec/backend/quality-guidelines.md`

新的学习约束要求后续任务说明：

- 做了什么。
- 作用是什么。
- 用什么实现。
- 输入输出是什么。
- 在整体流程里的定位。
- 为什么现在做。
- 没有做什么。
- 如何验证。
- 学到了什么。
- 下一步是什么。

## 下一步学习

下一步建议任务：

```text
basic answer pipeline / API boundary
```

也可以先做更窄的：

```text
refusal behavior
```

推荐优先考虑 basic answer pipeline，因为现在已经有 retrieval pipeline 和 citation-aware generator，下一步自然是把二者组合成一个应用层问答边界。仍然不要跳到 Workbench、MCP、LangGraph、UI 或多 agent 编排。
