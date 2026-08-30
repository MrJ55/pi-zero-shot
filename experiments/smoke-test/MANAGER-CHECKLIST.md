# Manager checklist (smoke test)

Use this in the **parent Pi session** (full tools, preferably a stronger model). Workers are pure generators — see [`agents/codegen-worker.md`](./agents/codegen-worker.md).

## Role

You are the **only** agent that may:

- read / search the repo
- write or edit files
- run shell / tests / typecheck
- update `plan.md`, `notes.md`, `tasks.json` (if used)

Workers only return text. You place their code and verify it.

## Before spawning a worker

- [ ] One unit only (one function, type, or small module)
- [ ] Brief includes **path** where you will place the result
- [ ] Brief includes **signature / types / exports**
- [ ] Brief includes **allowed imports** and forbidden ones
- [ ] Brief includes **1–3 examples** or acceptance bullets
- [ ] Brief includes relevant **snippets** (interfaces only — not the whole repo)
- [ ] Dependencies on other units are already in the tree, or the brief embeds them

## Brief template (paste into the subagent prompt)

```text
Unit id: <id>
Target path: <relative/path>
Language: <lang>

Implement:
<1–5 sentences>

Signature / shape:
<code fence>

Allowed imports:
- ...

Must not:
- touch other files
- add dependencies not listed
- change public API beyond the signature

Acceptance:
- ...

Context (read-only excerpts):
<code fence or quoted API>
```

## After the worker returns

- [ ] Extract `## code` (ignore prose outside the format)
- [ ] Write/patch **only** the target path (or planned paths)
- [ ] Run the smallest useful gate (`test` / `tsc` / `lint` on that area)
- [ ] On fail: either rebrief the **same** unit with error output, or split the unit
- [ ] On pass: mark task done; only then start dependent units
- [ ] Log a one-line note in `notes.md` (what changed, gate result)

## Parallelism rules

- [ ] Fan-out only units with **no** unmet deps
- [ ] Cap concurrency (start with 2)
- [ ] Merge serially: place → gate one unit before placing the next if they share files
- [ ] Prefer sequential until briefs are reliable

## Stop conditions

- Goal gates pass, or
- Budget exhausted (max worker calls / wall time), or
- Same unit failed N times with no progress → escalate (human or stronger single-agent pass)

## Anti-patterns

- Letting the worker “explore the repo” (it has no tools — don’t ask)
- Huge briefs (“implement the feature”) — split further
- Placing code without running a gate
- Parallel workers editing the same file
