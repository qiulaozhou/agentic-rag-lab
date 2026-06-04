# 学习记录：Real Provider Manual Smoke Guide

更新日期：2026-06-04

## 本步一句话总结

本步新增真实 OpenAI-compatible provider 的本地手动 smoke 指南，把真实服务验证和 pytest 自动化测试明确分开。

## 本步做了什么

- 新增 `docs/REAL_PROVIDER_SMOKE_GUIDE.md`。
- 说明真实 API key 只能放本地 `.env`。
- 列出真实 provider 需要配置的环境变量名。
- 提供 PowerShell 手动验证步骤：
  - 复制 `.env.example` 到 `.env`。
  - 手动填写本地 `.env`。
  - 启动 `uv run uvicorn agentic_rag_lab.main:app --reload`。
  - 验证 `/health`。
  - 验证 `POST /answer`。
  - 验证 `POST /knowledge-bases`。
  - 验证 `POST /knowledge-bases/{id}/answer`。
  - 验证 `POST /knowledge-bases/from-file`。
- 新增文档测试，检查 smoke guide 包含必要变量名和 endpoint。

## 作用是什么

上一阶段已经实现 OpenAI-compatible provider adapter，但 adapter 通过 mock 测试只能证明“请求格式和响应解析正确”，不能证明用户本地真实 key、真实 base URL、真实模型名、网络和额度都可用。

本步的作用是补上真实 provider 的人工验证入口，同时避免把真实服务变成默认测试依赖。

## 用什么实现

- `docs/REAL_PROVIDER_SMOKE_GUIDE.md`
  - 作为本地手动验证指南。
- `tests/test_real_provider_smoke_guide.py`
  - 用轻量文档测试检查指南是否包含必要安全配置和 API 手动验证步骤。
- `.env.example`
  - 继续只保存变量名和占位值。

## 输入输出是什么

输入：

```text
本地 .env
真实 OpenAI-compatible API key
真实 provider base URL
真实 embedding model 名称
真实 chat model 名称
```

输出：

```text
人工 smoke 检查结果：
/health 是否正常
/answer 是否能返回真实 LLM 正文和本地 citation
knowledge base 是否能创建和提问
from-file 是否能导入本机 Markdown/TXT 并回答
```

## 在整体 RAG 链路中的定位

当前链路位置：

```text
file / directory import API
-> disk-backed knowledge base
-> OpenAI-compatible providers
-> real provider manual smoke guide  <-- 本步
-> eval provider comparison
```

这一步不新增运行时代码能力，新增的是“如何安全验证真实 provider 已接入整个 RAG 链路”的操作边界。

## 为什么现在做

真实 provider adapter 已经存在，但如果没有 smoke guide，用户容易出现两个问题：

- 不知道 `.env` 应该怎么配置。
- 误以为 pytest 会自动调用真实服务。

现在补 smoke guide，可以把真实服务验证变成受控的人工步骤，并且继续保持默认自动测试离线、稳定、无 key。

## 设计选择

### 选择 A：手动 smoke 指南

本次采用。

优点：
- 不把 secret 带入仓库。
- 不让 pytest 依赖网络。
- 不消耗真实服务额度。
- 用户可以按需在本机验证。

代价：
- 不能自动证明真实 provider 在当前机器一定可用，需要人工执行。

### 选择 B：pytest 真实联网 smoke

没有采用。

原因：
- 需要真实 key。
- 依赖网络和额度。
- 测试结果会受 provider 稳定性影响。
- 不适合学习项目默认回归。

## 本次没有做什么

- 没有执行真实 provider 请求。
- 没有写入真实 API key。
- 没有写入真实 base URL。
- 没有写入真实模型名。
- 没有新增真实服务 CI。
- 没有做 provider 质量评估。

## 如何验证

先运行：

```powershell
uv run pytest
```

普通权限下因本机 `uv` cache 权限失败：

```text
C:\Users\admin\AppData\Local\uv\cache
```

提升权限后同一命令通过：

```text
136 passed
```

## 学到什么

- manual smoke 用来验证真实外部依赖是否可用。
- automated tests 用来验证代码行为是否稳定。
- 真实 provider 的 key、网络、额度和模型质量不应该进入默认 pytest。
- `/health` 不应该依赖真实 provider 凭证。
- citation 即使用真实 LLM，也仍然应该来自本地 metadata。

## Trellis 反馈

这一步形成可复用约定：

- 真实 provider 文档只写变量名和占位值。
- 真实服务验证放在 manual guide。
- pytest 使用 mock 或 fake，不调用真实 provider。

## 下一步是什么

下一步是扩展 eval provider comparison：

```text
local deterministic baseline
-> candidate provider run
-> EvalComparisonReport
```

它用于比较真实 provider 是否改变 answer、citation 或 refusal 行为。

