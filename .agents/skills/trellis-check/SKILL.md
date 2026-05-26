---
name: trellis-check
description: "Comprehensive quality verification: spec compliance, lint, type-check, tests, cross-layer data flow, code reuse, and consistency checks. Use when code is written and needs quality verification, before committing changes, or to catch context drift during long sessions."
---

# Code Quality Check

Comprehensive quality verification for recently written code. Combines spec compliance, cross-layer safety, and pre-commit checks.

---

## Step 1: Identify What Changed

```bash
git diff --name-only HEAD
git status
```

## Step 2: Read Applicable Specs

```bash
C:\Users\admin\AppData\Roaming\uv\python\cpython-3.12.12-windows-x86_64-none\python.exe ./.trellis/scripts/get_context.py --mode packages
```

For each changed package/layer, read the spec index and follow its **Quality Check** section:

```bash
cat .trellis/spec/<package>/<layer>/index.md
```

Read the specific guideline files referenced — the index is a pointer, not the goal.

## Step 3: Run Project Checks

Run the project's lint, type-check, and test commands. Fix any failures before proceeding.

## Step 4: Review Against Checklist

### Learning Mode

- [ ] `prd.md` includes Learning Goals, Concepts, Why Now, Approach Options, and Out of Scope for Learning?
- [ ] The change forms a minimal runnable loop instead of only adding disconnected code?
- [ ] `{TASK_DIR}/learning.md` exists for finished implementation work?
- [ ] `learning.md` records Concepts, Why Now, Design Choice, What Changed, How To Verify, Trellis Feedback, and Next Learning Step?
- [ ] Verification proves the concept with concrete commands and results?
- [ ] Trellis Feedback says either "no spec update needed" or points to the spec/guide update made?

### Code Quality

- [ ] Linter passes?
- [ ] Type checker passes (if applicable)?
- [ ] Tests pass?
- [ ] No debug logging left in?
- [ ] No suppressed warnings or type-safety bypasses?

### Test Coverage

- [ ] New function → unit test added?
- [ ] Bug fix → regression test added?
- [ ] Changed behavior → existing tests updated?

### Spec Sync

- [ ] Does `.trellis/spec/` need updates? (new patterns, conventions, lessons learned)
- [ ] Is any learning material incorrectly placed in long-term spec when it belongs only in task `learning.md`?
- [ ] Is any reusable workflow rule still only in `learning.md` when it belongs in `.trellis/spec/guides/`?

> "If I fixed a bug or discovered something non-obvious, should I document it so future me won't hit the same issue?" → If YES, update the relevant spec doc.

## Step 5: Cross-Layer Dimensions (if applicable)

Skip this step if your change is confined to a single layer.

### A. Data Flow (changes touch 3+ layers)

- [ ] Read flow traces correctly: Storage → Service → API → UI
- [ ] Write flow traces correctly: UI → API → Service → Storage
- [ ] Types/schemas correctly passed between layers?
- [ ] Errors properly propagated to caller?

### B. Code Reuse (modifying constants, creating utilities)

- [ ] Searched for existing similar code before creating new?
  ```bash
  grep -r "pattern" src/
  ```
- [ ] If 2+ places define same value → extracted to shared constant?
- [ ] After batch modification, all occurrences updated?

### C. Import/Dependency (creating new files)

- [ ] Correct import paths (relative vs absolute)?
- [ ] No circular dependencies?

### D. Same-Layer Consistency

- [ ] Other places using the same concept are consistent?

---

## Step 6: Report and Fix

Report violations found and fix them directly. Re-run project checks after fixes.

When reporting completion, include:
- Verification commands run and their results
- Whether the runnable loop is proven
- Where the learning note was written
- Whether Trellis/spec feedback was applied or intentionally skipped
