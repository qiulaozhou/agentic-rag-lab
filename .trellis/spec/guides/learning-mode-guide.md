# Learning Mode Guide

> **Purpose**: Keep each project task useful as both implementation work and AI-engineering study.

---

## When to Use

Use this guide for every Trellis task in this repository. The default working style is:

1. Explain the concept being exercised.
2. Make the smallest useful design choice.
3. Build a runnable slice.
4. Verify it with concrete commands.
5. Record what was learned and whether Trellis needs adjustment.

This guide is especially important when the task could drift into a larger topic such as UI, agents, LangGraph, MCP, vector stores, or workflow automation.

---

## Required Learning Loop

### 1. Concept

State the core concept this task is meant to teach or reinforce.

Examples:
- FastAPI app factory and health-check boundaries
- Markdown/TXT ingestion and chunking
- Embedding adapter boundaries
- Retrieval evaluation with deterministic fixtures

### 2. Why Now

Explain why this task belongs at the current project stage.

Make the sequencing explicit:
- Why this task comes before a UI, agent layer, LangGraph, MCP, or deployment work
- What previous milestone it builds on
- What later milestone it enables

### 3. Design Choice

For any non-obvious technical decision, record 2-3 feasible options and the recommended choice.

Keep the choice proportional to the milestone. Prefer the smallest design that proves the next concept without blocking future extension.

### 4. Implementation

Implement the smallest runnable loop that exercises the concept.

Avoid adding frameworks or abstractions just because they are interesting. Add them only when the current task needs them to pass its acceptance criteria.

### 5. Verification

Verification must prove the runnable loop, not just static code shape.

Record:
- Commands run
- Expected result
- Actual result
- Any unverified risk

### 6. Learning Note

Each finished task should leave a lightweight learning note at:

```text
.trellis/tasks/<task>/learning.md
```

Use this structure:

```markdown
# Learning Notes

## Concepts

## Why Now

## Design Choice

## What Changed

## How To Verify

## Trellis Feedback

## Next Learning Step
```

Do not retroactively rewrite old tasks just to satisfy the format. Add it for the current active task when finishing real work.

### 7. Trellis Feedback

At the end of each task, decide whether the workflow itself needs an update.

Use this rule:
- One-time implementation detail -> keep it in the task's `learning.md`
- Reusable coding convention or contract -> update `.trellis/spec/<area>/*`
- Reusable learning or reasoning habit -> update `.trellis/spec/guides/*`

---

## PRD Fields

Every task PRD should include these learning fields:

- `Learning Goals`
- `Concepts`
- `Why Now`
- `Approach Options`
- `Out of Scope for Learning`

The PRD is incomplete if it only says what to build and does not explain what the task is meant to teach.

---

## Pre-Code Explanation

Before writing code, briefly tell the user:

- The concept this task exercises
- The current design choice
- The minimal runnable loop you will build
- What will intentionally remain out of scope

Keep this short. The goal is orientation, not a lecture.

---

## Completion Checklist

- [ ] PRD names the learning goal and concept.
- [ ] PRD explains why this task is next in sequence.
- [ ] Trade-offs are recorded when there is a meaningful choice.
- [ ] Implementation forms a minimal runnable loop.
- [ ] Verification commands and results are recorded.
- [ ] `learning.md` exists for the active task when finishing implementation work.
- [ ] Trellis feedback is recorded as "no spec update needed" or applied to the right spec/guide.
