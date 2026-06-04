# Build Basic Answer Pipeline API Boundary

## Goal

实现一个内部 answer pipeline，把已经完成的 retrieval pipeline 和 citation-aware generator 组合成一个最小问答边界：

```text
SourceDocument
-> DocumentChunk
-> LocalRetrievalPipeline.search()
-> CitationAwareAnswerGenerator.answer()
-> LocalAnswerPipeline.answer()
-> GeneratedAnswer
-> pytest
```

本任务的 “API boundary” 指 Python 内部调用边界，不是 FastAPI HTTP endpoint。

## Requirements

- 新增 `LocalAnswerPipeline`。
- `LocalAnswerPipeline` 组合已有 `Retriever` 和 `AnswerGenerator`。
- 暴露 async `answer(question: str, limit: int = 5) -> GeneratedAnswer`。
- 提供 `from_chunks()` 和 `from_documents()` 便捷构造。
- 继续使用 `GeneratedAnswer`，不新增复杂 schema。
- 不改变 retrieval ranking、embedding 算法、citation 规则或 no-evidence 行为。
- 不新增真实 LLM、HTTP endpoint、UI、LangGraph、MCP、eval report 或多 agent 编排。

## Learning Goals

- 理解 answer pipeline 的职责是组合 retrieval 和 generation，而不是重写它们。
- 理解内部 API boundary 和 HTTP API 的区别。
- 理解为什么调用方应该依赖 `answer(question)`，而不是手动拼 `search()` 和 `answer()`。
- 理解 `GeneratedAnswer` 如何成为当前 RAG 闭环的输出边界。
- 继续练习详细学习记录：做了什么、作用、工具、输入输出、流程定位、验证和下一步。

## Concepts

- answer pipeline
- internal API boundary
- composition
- `Retriever`
- `AnswerGenerator`
- `GeneratedAnswer`
- evidence-grounded response

## Why Now

项目已经完成：

- Markdown/TXT ingestion。
- deterministic chunking。
- local hash embedding。
- in-memory vector retrieval。
- `LocalRetrievalPipeline.search()`。
- `CitationAwareAnswerGenerator.answer()`。

现在调用方仍然需要自己写：

```python
evidence = await retriever.search(question)
answer = await generator.answer(question, evidence)
```

这会让后续调用方知道太多组合细节。现在把组合收进 `LocalAnswerPipeline`，可以让后续 HTTP endpoint、refusal behavior 或 eval 只依赖一个问答入口。

## Approach Options

**Option A: 在 `generation/pipeline.py` 新增 `LocalAnswerPipeline`**（本次采用）

- 优点：最小、离线、无新依赖，输出就是 `GeneratedAnswer`。
- 代价：还不是独立 application service 层。

**Option B: 新增 `application/` 或 `qa/` 层**

- 优点：更像完整应用服务。
- 代价：当前项目结构还很小，过早增加层级。

**Option C: 直接新增 FastAPI endpoint**

- 优点：更像外部 API。
- 代价：需要请求/响应、错误码和文档输入方式设计，当前过早。

## Acceptance Criteria

- [ ] `LocalAnswerPipeline.answer()` 返回 `GeneratedAnswer`。
- [ ] 可以从 `DocumentChunk` 列表构建 pipeline。
- [ ] 可以从 `SourceDocument` 列表构建 pipeline。
- [ ] 非空 evidence 返回 `refused=False` 和 citations。
- [ ] 空 query 或无 evidence 时返回 `refused=True` 和空 citations。
- [ ] `limit <= 0` 抛 `ValueError`。
- [ ] citation 能追溯到 `source_path#chunk-{chunk_index}`。
- [ ] 端到端测试覆盖 `load_text_file -> LocalAnswerPipeline.from_documents -> answer`。
- [ ] `uv run pytest` 通过，或环境级失败被记录到 `learning.md`。

## Definition of Done

- `LocalAnswerPipeline` 代码和导出完成。
- 单元测试和端到端测试完成。
- README、技术笔记、根目录学习笔记同步更新为中文。
- Trellis backend specs 记录 reusable answer pipeline 约定。
- 本任务 `learning.md` 记录概念、设计选择、验证结果和下一步。

## Technical Approach

- 新增 `src/agentic_rag_lab/generation/pipeline.py`。
- `LocalAnswerPipeline.__init__(retriever, answer_generator=None)` 保存依赖。
- `from_chunks(chunks, embedding_provider=None, answer_generator=None)` 创建 `LocalRetrievalPipeline`。
- `from_documents(documents, chunk_size, overlap=0, embedding_provider=None, answer_generator=None)` 创建 `LocalRetrievalPipeline`。
- `answer(question, limit=5)` 先调用 `retriever.search()`，再调用 `answer_generator.answer()`。
- 从 `src/agentic_rag_lab/generation/__init__.py` 导出 `LocalAnswerPipeline`。

## Decision (ADR-lite)

**Context**：retrieval 和 citation-aware generation 已经分别可用，但还没有一个内部问答入口来组合它们。

**Decision**：新增 `LocalAnswerPipeline`，放在 `generation/pipeline.py`。

**Consequences**：后续 HTTP endpoint、refusal behavior 和 eval 可以依赖 `LocalAnswerPipeline.answer()`，不需要重复拼底层 retrieval 和 generation 细节。

## Out of Scope

- FastAPI answer endpoint。
- 请求/响应 DTO。
- 真实 LLM provider。
- prompt engineering。
- 复杂 refusal policy。
- eval dataset / eval report。
- rerank。
- production vector database。
- Web UI。
- LangGraph。
- MCP。
- multi-agent orchestration。

## Out of Scope for Learning

- HTTP API design。
- API versioning。
- 生产级自然语言生成。
- citation accuracy eval。
- confidence scoring。
- multi-step agent planning。

## Technical Notes

- Relevant specs:
  - `.trellis/spec/backend/directory-structure.md`
  - `.trellis/spec/backend/quality-guidelines.md`
  - `.trellis/spec/guides/learning-mode-guide.md`
- Relevant code:
  - `src/agentic_rag_lab/retrieval/pipeline.py`
  - `src/agentic_rag_lab/generation/citation.py`
  - `src/agentic_rag_lab/schemas.py`
