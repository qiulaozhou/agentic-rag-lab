# Real Provider Manual Smoke Guide

更新日期：2026-06-04

## 目的

这份指南用于在本机手动验证 OpenAI-compatible provider 是否已经接入 `agentic-rag-lab` 的 RAG 链路。

它不是自动化测试，也不会进入 pytest。原因是：真实 provider 需要 API key、网络、额度和具体模型名，这些都不适合放进默认测试链路。

## 安全边界

真实 API key 只能放在本地 `.env` 文件里。

不要把真实 key 写入：

- README
- `learning.md`
- pytest
- Trellis task 文档
- `.env.example`
- 代码文件
- git commit

`.env` 应保持本地私有，并由 `.gitignore` 排除。

## 需要配置的环境变量

先复制示例配置：

```powershell
Copy-Item .env.example .env
```

然后在本地 `.env` 中填写：

```text
EMBEDDING_PROVIDER=openai_compatible
ANSWER_GENERATOR=openai_compatible
OPENAI_COMPATIBLE_API_KEY=your-api-key
OPENAI_COMPATIBLE_BASE_URL=your-openai-compatible-base-url
OPENAI_COMPATIBLE_EMBEDDING_MODEL=your-embedding-model
OPENAI_COMPATIBLE_CHAT_MODEL=your-chat-model
```

说明：

- `OPENAI_COMPATIBLE_BASE_URL` 应该是不带 endpoint path 的 base URL。
- embedding endpoint 会由代码拼成 `{base_url}/embeddings`。
- chat endpoint 会由代码拼成 `{base_url}/chat/completions`。
- 真实模型名由你本地 provider 决定，本指南不写死模型名。

## 启动服务

```powershell
uv run uvicorn agentic_rag_lab.main:app --reload
```

如果 provider 配置缺失，服务创建 provider 时会抛出明确错误。先修正 `.env`，再重新启动。

## 1. 验证 health endpoint

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/health"
```

期望：

```text
返回 200 OK，并显示服务健康状态。
```

`/health` 不应该依赖模型凭证。

## 2. 验证 POST /answer

```powershell
$body = @{
  question = "Why do RAG answers need citations?"
  documents = @(
    @{
      id = "doc-1"
      text = "RAG answers need citations so users can inspect sources."
      metadata = @{
        source_path = "docs/rag.md"
        file_type = ".md"
      }
    }
  )
  chunk_size = 400
  overlap = 0
  limit = 5
} | ConvertTo-Json -Depth 8

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/answer" `
  -ContentType "application/json" `
  -Body $body
```

期望：

```text
refused=false
citations 包含 docs/rag.md#chunk-0
text 是真实 LLM 根据 evidence 生成的回答正文
```

注意：citation 仍然来自本地 metadata，不来自模型自由生成的文本。

## 3. 创建 knowledge base

```powershell
$body = @{
  documents = @(
    @{
      id = "doc-1"
      text = "RAG answers need citations so users can inspect sources."
      metadata = @{
        source_path = "docs/rag.md"
        file_type = ".md"
      }
    }
  )
  chunk_size = 400
  overlap = 0
} | ConvertTo-Json -Depth 8

$created = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/knowledge-bases" `
  -ContentType "application/json" `
  -Body $body

$created
```

期望：

```text
返回 knowledge_base_id、document_count、chunk_count
```

## 4. 基于 knowledge base 提问

```powershell
$knowledgeBaseId = $created.knowledge_base_id

$body = @{
  question = "Why do RAG answers need citations?"
  limit = 5
} | ConvertTo-Json -Depth 4

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/knowledge-bases/$knowledgeBaseId/answer" `
  -ContentType "application/json" `
  -Body $body
```

期望：

```text
refused=false
citations 包含 docs/rag.md#chunk-0
text 由真实 LLM 基于知识库 evidence 生成
```

## 5. 从本机文件导入 knowledge base

先准备一个本机 Markdown 文件，例如：

```powershell
New-Item -ItemType Directory -Force .local\manual-smoke | Out-Null
Set-Content -Path .local\manual-smoke\rag.md -Encoding UTF8 -Value "RAG citations let users inspect the source document."
```

再调用 file import API：

```powershell
$path = (Resolve-Path .local\manual-smoke\rag.md).Path

$body = @{
  path = $path
  chunk_size = 400
  overlap = 0
} | ConvertTo-Json -Depth 4

$fileKb = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/knowledge-bases/from-file" `
  -ContentType "application/json" `
  -Body $body

$fileKb
```

然后基于导入的 knowledge base 提问：

```powershell
$body = @{
  question = "What do RAG citations let users inspect?"
  limit = 5
} | ConvertTo-Json -Depth 4

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/knowledge-bases/$($fileKb.knowledge_base_id)/answer" `
  -ContentType "application/json" `
  -Body $body
```

期望：

```text
refused=false
citations 包含本机文件绝对路径加 #chunk-0
```

## 6. 验证拒答

```powershell
$body = @{
  question = "   "
  limit = 5
} | ConvertTo-Json -Depth 4

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/knowledge-bases/$($fileKb.knowledge_base_id)/answer" `
  -ContentType "application/json" `
  -Body $body
```

期望：

```text
refused=true
citations=[]
```

拒答仍然由本地 refusal policy 控制，不需要调用真实 LLM。

## 和 pytest 的关系

pytest 不会跑真实服务。

pytest 只验证：

- 默认本地 provider 可以离线运行。
- OpenAI-compatible adapter 的 HTTP 请求和响应解析能通过 mock 验证。
- provider factory 能正确处理默认配置和显式配置。
- eval comparison 能用 fake pipeline 验证差异计算。

pytest 不验证：

- 真实 key 是否可用。
- 真实 base URL 是否可访问。
- 真实模型质量。
- 真实 provider 延迟、额度和稳定性。

这些内容通过本指南手动验证。

## 常见问题

### 启动时报缺少 OPENAI_COMPATIBLE_API_KEY

说明你已经启用了 `openai_compatible` provider，但 `.env` 中没有填写 key。填写本地 `.env` 后重启服务。

### POST /answer 返回 refused=true

先检查：

- question 是否为空。
- documents 是否为空。
- 文档和问题是否有足够相关 token。
- retrieval score 是否低于 refusal threshold。

### citations 看起来不是模型生成的

这是预期行为。citation 必须来自本地 evidence metadata。模型只生成 answer text，不能决定最终 `GeneratedAnswer.citations`。

## 下一步

手动 smoke 通过后，下一步可以扩展 eval comparison，用同一组 `EvalCase` 对比：

```text
local deterministic baseline
vs
OpenAI-compatible provider run
```

这样可以观察真实 provider 是否改变 answer、citation 或 refusal 行为。
