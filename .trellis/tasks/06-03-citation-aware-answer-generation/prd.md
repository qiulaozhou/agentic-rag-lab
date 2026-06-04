# Citation-Aware Answer Generation

## Goal

实现下一个最小 RAG 回答生成闭环：

```text
SourceDocument
-> DocumentChunk
-> LocalRetrievalPipeline.search()
-> list[RetrievalResult]
-> CitationAwareAnswerGenerator.answer()
-> GeneratedAnswer(text, citations, refused)
-> pytest
```

本任务只做内部 generation 能力，不新增 HTTP endpoint，不接真实 LLM，不做 prompt engineering，不做 eval report。

## Requirements

- 新增确定性的本地 citation-aware answer generator。
- 继续使用已有 `GeneratedAnswer`、`RetrievalResult`、`DocumentChunk`，不新增复杂 schema。
- `answer(question, evidence)` 输入检索结果，输出 `GeneratedAnswer`。
- 非空 evidence 时，生成可读回答，并返回实际使用 evidence 的 citation。
- 空 evidence 时，不编造答案，返回 `refused=True`、`citations=[]`。
- citation 规则固定：
  - 优先使用 `source_path#chunk-{chunk_index}`。
  - metadata 不完整时回退到 `chunk.id`。
  - citation 按使用顺序去重。
- 不调用真实 LLM、不访问网络、不引入第三方依赖。

## Learning Goals

- 理解为什么 RAG 回答必须能追溯来源。
- 理解 `RetrievalResult` 如何变成 `GeneratedAnswer.citations`。
- 理解 citation-aware generation 和普通文本生成的区别。
- 理解“没有证据就不回答”是 RAG 可靠性的最小边界。
- 学会把学习说明写清楚：做了什么、作用是什么、用什么做、输入输出、整体流程定位、验证结果和下一步。

## Concepts

- citation-aware generation
- evidence-grounded answer
- `RetrievalResult`
- `GeneratedAnswer`
- source metadata
- deterministic local generation
- minimal refusal guard

## Why Now

项目已经完成：

- Markdown/TXT ingestion。
- deterministic chunking。
- local hash embedding。
- in-memory vector retrieval。
- `LocalRetrievalPipeline.search()`。

现在 retrieval 已经能返回带 metadata 的 `RetrievalResult`。下一步必须把检索结果转换成答案和引用，否则 RAG 只停留在“能找到片段”，还不能形成用户可用的问答输出。

这一任务位于整体流程的中段：

```text
文档进入系统
-> 切分
-> embedding
-> 检索
-> 带引用回答  <-- 本任务
-> 拒答策略
-> eval
-> UI / Agent / MCP
```

## Approach Options

**Option A: 确定性本地生成器**（本次采用）

- 优点：离线、可测试、无新依赖，能先证明 citation 和 evidence 边界。
- 代价：回答质量不是生产级自然语言生成。

**Option B: 使用 `FakeLLMProvider` 生成回答**

- 优点：能练习 LLM provider 调用。
- 代价：当前 fake provider 只是 echo prompt，不能真正证明 citation 规则。

**Option C: 直接接真实 LLM**

- 优点：回答更像真实产品。
- 代价：需要 API key、prompt、成本和失败处理，当前过早。

## Acceptance Criteria

- [ ] 非空 evidence 能生成 `GeneratedAnswer`。
- [ ] `GeneratedAnswer.refused` 对非空 evidence 为 `False`。
- [ ] citation 能从 `source_path` 和 `chunk_index` 生成。
- [ ] metadata 不完整时 citation 回退到 `chunk.id`。
- [ ] citation 去重且顺序稳定。
- [ ] 空 evidence 返回 `refused=True`，且 citations 为空。
- [ ] 端到端测试覆盖 `SourceDocument -> retrieval pipeline -> answer generation`。
- [ ] `uv run pytest` 通过，或环境级失败被记录到 `learning.md`。

## Definition of Done

- generation 代码和导出完成。
- 单元测试和端到端测试完成。
- `.trellis/spec/guides/learning-mode-guide.md` 更新为更详细的中文学习模板。
- README、`docs/TECHNICAL_NOTES.md`、根目录 `AI_AGENT_PORTFOLIO_NOTES.md` 同步更新为中文详细说明。
- 本任务 `learning.md` 记录做了什么、作用、工具、输入输出、整体定位、验证结果和下一步。

## Technical Approach

- 新增 `src/agentic_rag_lab/generation/citation.py`。
- 新增 `CitationAwareAnswerGenerator`。
- 默认最多使用前 `3` 条 evidence。
- 对 chunk text 做空白归一化并截取短片段，用于生成本地答案。
- 从 `src/agentic_rag_lab/generation/__init__.py` 导出 `CitationAwareAnswerGenerator`。
- 新增 generation 单元测试。
- 新增 retrieval + generation 端到端测试。

## Decision (ADR-lite)

**Context**：retrieval pipeline 已经能返回带 metadata 的 `RetrievalResult`，但系统还不能把这些结果变成可追溯回答。

**Decision**：先做确定性本地 `CitationAwareAnswerGenerator`，不接真实 LLM。

**Consequences**：项目可以离线证明 citation 规则、空证据拒答和端到端数据流。未来接真实 LLM 时，可以把这个生成器的 citation 约定作为外层 contract 或测试基线。

## Out of Scope

- HTTP answer endpoint。
- 真实 LLM provider。
- OpenAI / LangChain / LangGraph。
- prompt engineering。
- production answer quality。
- rerank。
- eval dataset / eval report。
- Web UI。
- MCP。
- multi-agent orchestration。

## Out of Scope for Learning

- 复杂自然语言生成质量。
- 引用是否充分支持每一句话的细粒度评估。
- confidence score。
- threshold-based refusal policy。
- 多轮对话记忆。

## Technical Notes

- Relevant specs:
  - `.trellis/spec/guides/learning-mode-guide.md`
  - `.trellis/spec/backend/directory-structure.md`
  - `.trellis/spec/backend/quality-guidelines.md`
- Relevant code:
  - `src/agentic_rag_lab/schemas.py`
  - `src/agentic_rag_lab/retrieval/pipeline.py`
  - `src/agentic_rag_lab/generation/__init__.py`
