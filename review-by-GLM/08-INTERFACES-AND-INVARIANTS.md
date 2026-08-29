# Review-by-GLM — Interfaces and Invariants

**Reviewer:** GLM (Z.ai), independent audit
**Date:** 2026-08-29
**Scope:** The hard invariants a faithful pi-zero-shot port must preserve, with GVS5H source citations. This file is the reference for implementers: every invariant here is a "must" not a "should."

---

## How to read this file

This file enumerates the invariants a faithful pi-zero-shot port must preserve, with GVS5H source citations. Each invariant has:
- **ID** — `INV-#` for invariants (must hold at all times) and `IF-#` for interface contracts (specific function/type signatures).
- **GVS5H source** — file:line where the invariant lives in the reference implementation.
- **Status in pi-zero-shot plan** — ✅ captured, ⚠ partial, ❌ missing.
- **Test** — how to verify the invariant holds.

This file is the contract. If a port preserves every invariant here, it is faithful to GVS5H v2. If it misses any, it is not.

---

## A. Workspace invariants

### INV-1 — Per-problem workspace directory keyed by content hash

**GVS5H source:** `multiagent.py:78-79` (`_slug` returns `hashlib.md5(text.encode()).hexdigest()[:12]`); `multiagent.py:540-543` (workspace init writes `task.md` with the problem text).

**Status:** ✅ Phase 1 task list ("Create/reset directory keyed by content hash or session id").

**Invariant:** Every problem gets a fresh workspace directory. The directory name is derived from the problem text (content hash) or a session id. The workspace is the *only* shared state between role calls.

**Test:** Create two workspaces from the same problem text. Verify they have the same hash directory (idempotent) or different hash directories (session-keyed) — pick one and document it. Verify a workspace from a different problem gets a different directory.

### INV-2 — All six workspace files exist

**GVS5H source:** `multiagent.py:540-543`:

```python
for f in ("task.md", "notes.md", "transcript.jsonl", "plan.md",
          "solution.py", "answer.md", "tasks.json"):
    _write(ws, f, "")
_write(ws, "task.md", problem_text)
```

**Status:** ✅ Phase 1 task list names all six (plus `answer.md` for math).

**Invariant:** The workspace contains exactly these seven files: `task.md`, `plan.md`, `tasks.json`, `notes.md`, `solution.py`, `answer.md`, `transcript.jsonl`. No more, no less.

**Test:** After workspace init, verify all seven files exist and `task.md` contains the problem text. Verify `transcript.jsonl` is empty (will be appended to). Verify the other six files are empty (will be written to during the run).

### INV-3 — Workspace reset between runs of the same key

**GVS5H source:** `multiagent.py:540-543` — all files are truncated to empty at the start of each problem, regardless of prior state.

**Status:** ✅ Phase 1 task list ("Cleanup / isolation: reset workspace between runs of the same key").

**Invariant:** Re-running the same problem starts from a clean workspace. No state leaks between runs.

**Test:** Run a problem to completion. Re-run the same problem. Verify the second run's workspace starts empty (no leftover `notes.md` content, no leftover `solution.py` code).

### INV-4 — `plan.md` bounded at 4000 chars

**GVS5H source:** `multiagent.py:197` (`MAX_PLAN_CHARS = 4000`).

**Status:** ⚠ Phase 1 mentions "Hard size bounds (mirror paper `MAX_PLAN_CHARS`)" but doesn't pin the number.

**Invariant:** `plan.md` content is truncated to 4000 chars on write. The bound is configurable via the `MAX_PLAN_CHARS` env knob.

**Test:** Write a 10,000-char string to `plan.md`. Read it back. Verify the length is exactly 4000 chars.

### INV-5 — `notes.md` bounded at 8000 chars (= `MAX_PLAN_CHARS * 2`)

**GVS5H source:** `multiagent.py:281` (ideation appends `_strip_code(sec.get('NOTES') or reply.strip())[:MAX_PLAN_CHARS * 2]`); `multiagent.py:450` (worker writes `sec["NOTES"].strip()[:MAX_PLAN_CHARS * 2] + "\n"`).

**Status:** ⚠ Phase 1 mentions "size caps" but doesn't pin the formula.

**Invariant:** `notes.md` content is truncated to 8000 chars on every write. The bound is `MAX_PLAN_CHARS * 2` (derived, not hardcoded).

**Test:** Write a 20,000-char string to `notes.md`. Read it back. Verify the length is exactly 8000 chars. Change `MAX_PLAN_CHARS` to 5000. Verify `notes.md` is now truncated to 10,000 chars.

### INV-6 — `answer.md` bounded at 20000 chars

**GVS5H source:** `multiagent.py:194` (`MAX_ANSWER_CHARS = 20000`).

**Status:** ⚠ Phase 1 mentions "size caps" but doesn't pin the number.

**Invariant:** `answer.md` content is truncated to 20000 chars on write. The bound is configurable via the `MAX_ANSWER_CHARS` env knob.

**Test:** Write a 30,000-char string to `answer.md`. Read it back. Verify the length is exactly 20000 chars.

### INV-7 — Notes REWRITE-not-append

**GVS5H source:** `multiagent.py:18-20` (comment: "each worker REWRITES it rather than appending, so it stays organised and bounded -- append-only growth used to blow past the context window"); `multiagent.py:450` (`_write(ws, "notes.md", sec["NOTES"].strip()[:MAX_PLAN_CHARS * 2] + "\n")` — note `_write`, not `_append`).

**Status:** ✅ Phase 1 task list ("Notes **rewrite** semantics (not pure append)").

**Invariant:** The worker's `NOTES` section is written to `notes.md` *in place*, replacing the entire file. It is *not* appended. The only exception is ideation (the first worker), which appends to the empty file (equivalent to a write).

**Test:** Write a 1000-char string A to `notes.md`. Then write a 500-char string B to `notes.md` (worker rewrite). Read it back. Verify the content is exactly B (not A+B). Verify the length is exactly 500 chars (not 1500).

### INV-8 — `tasks.json` is write-only debug

**GVS5H source:** `multiagent.py:209-211` (`_save_tasks` writes tasks to `tasks.json`); `multiagent.py:588` (called after each manager round). The file is *never* read back.

**Status:** ⚠ Phase 1 lists `tasks.json` but doesn't specify it's write-only debug.

**Invariant:** `tasks.json` is a debug dump of the in-memory task list, written after each manager round. It is *not* read back by any role. The live task list is the in-memory `tasks` value threaded through the loop.

**Test:** Run a problem. Verify `tasks.json` is written after each manager round. Verify no role call's prompt includes the contents of `tasks.json` (only the in-memory `task_lines` formatted by `_primary_manage`).

### INV-9 — `MAX_TASKS=12` cap

**GVS5H source:** `multiagent.py:72` (`MAX_TASKS = int(os.environ.get("MULTIAGENT_MAX_TASKS", "12"))`).

**Status:** ❌ Not mentioned in plan.

**Invariant:** The live task list is capped at 12 entries. New tasks beyond 12 are dropped.

**Test:** Create a workspace. Add 20 tasks via the task parser. Verify the live task list contains exactly 12 entries.

### INV-10 — `ANS_RE` non-empty-answer guard

**GVS5H source:** `multiagent.py:192` (`ANS_RE = re.compile(r"ANSWER:\s*\S", re.I)` — any non-empty final answer); `multiagent.py:433`:

```python
if ans and (ANS_RE.search(ans) or not _read(ws, "answer.md").strip()):
    _write(ws, "answer.md", ans)
    wrote = True
```

**Status:** ❌ Not mentioned in plan.

**Invariant:** `answer.md` is only overwritten if (a) the new reply has a parseable `ANSWER:` line (matches `ANS_RE`), OR (b) the file is currently empty. A rambling or truncated call cannot destroy a good prior answer.

**Test:** Write a parseable answer "ANSWER: 42" to `answer.md`. Then attempt to overwrite with a rambling string that has no `ANSWER:` line. Verify `answer.md` still contains "ANSWER: 42". Then attempt to overwrite with "ANSWER: 43". Verify `answer.md` now contains "ANSWER: 43".

---

## B. Control flow invariants

### INV-11 — Control-flow order

**GVS5H source:** `multiagent.py:547-595` (`multiagent_solve`).

**Status:** ✅ Phase 3 task list and `docs/architecture.md` both capture the order.

**Invariant:** The control flow is strictly:
1. Manager writes `plan.md` + seed tasks (`_primary_plan`).
2. First worker brainstorms (`_ideation_worker`) — no code, appends to `notes.md`.
3. Manager curates task list and picks first task (`_primary_manage`).
4. Loop (up to `MAX_ITERS`):
   a. Worker executes the chosen task (`_worker`) — fresh context, rewrites `solution.py`.
   b. Sample tests run (`_run_samples`) — only if worker actually wrote code.
   c. Manager re-curates and decides done/next (`_primary_manage`).
   d. Hard override: if samples failed and manager says "done", force `continue`.
5. Finalize (`_worker` with `finalize=True`) — only if manager did not mark done with a usable answer.

**Test:** Run a problem. Verify the transcript shows the order: primary_plan, ideation, primary_manage, worker, primary_manage, worker, …, finalize (or skip). Verify no role call appears out of order.

### INV-12 — `MAX_ITERS=10`

**GVS5H source:** `multiagent.py:42` (`MAX_ITERS = int(os.environ.get("MULTIAGENT_MAX_ITERS", "10"))`).

**Status:** ✅ Phase 3 task list ("`max iters`" config).

**Invariant:** The loop runs at most 10 manager→worker cycles. Configurable via `MULTIAGENT_MAX_ITERS`.

**Test:** Run a problem that never converges (manager always says `continue`). Verify the loop stops after exactly 10 cycles.

### INV-13 — Sample-test hard override

**GVS5H source:** `multiagent.py:581-587`:

```python
# Hard guard: never accept a solution that fails the public samples, no matter what
# the manager said -- keep iterating (fix / different approach) until they pass.
if res and res.get("ran") and res["passed"] < res["total"] and status == "done":
    status = "continue"
    if not next_desc:
        next_desc = "The solution fails the public sample tests; fix it or try a different approach."
    log("    [primary-manage] overriding 'done' -- sample tests still failing")
```

**Status:** ✅ Phase 3 task list ("hard override if manager says done while samples fail").

**Invariant:** The code does *not* merely instruct the manager to keep going; it *overrides* a `"done"` verdict when samples fail. The override is unconditional — it does not depend on the manager's reasoning.

**Test:** Construct a case where the manager says `done` but the sample tests fail. Verify the loop continues. Verify the next task is "The solution fails the public sample tests; fix it or try a different approach."

### INV-14 — Sample tests only run when worker actually wrote code

**GVS5H source:** `multiagent.py:574` (`if spec["kind"] == "code" and tests and wrote:`).

**Status:** ❌ Plan doesn't specify the `wrote` guard.

**Invariant:** Sample tests run only if (a) the problem is a code problem, (b) tests are provided, AND (c) the worker actually wrote new code in this round. Without the `wrote` guard, the loop would re-grade the previous round's `solution.py` and hand the manager a verdict about work this round didn't do.

**Test:** Construct a case where the worker truncates without writing new code. Verify sample tests do *not* run that round. Verify the manager's prompt does *not* include a sample-test verdict for that round.

### INV-15 — No-progress guard

**GVS5H source:** `multiagent.py:558-563`:

```python
# No-progress guard: if the manager hands back the very same task it just assigned,
# the worker achieved nothing and another identical cycle will too. Each cycle can
# cost a full CLOUD_MAX_TOKENS generation, so stop rather than spend the budget.
if prev_desc is not None and next_desc.strip().lower() == prev_desc.strip().lower():
    log(f"    [primary] reissued the same task; no progress, stopping after {iters} iters")
    break
```

**Status:** ✅ Phase 3 task list ("No-progress guard (identical re-issued task → stop)").

**Invariant:** If the manager hands back the very same task it just assigned, the loop stops. The comparison is case-insensitive and whitespace-trimmed.

**Test:** Construct a case where the manager re-issues the same task description twice in a row. Verify the loop stops after the second issue.

### INV-16 — Cut-off summarizer

**GVS5H source:** `multiagent.py:353-371` (`_summarize_cutoff`).

**Status:** ✅ Phase 3 task list ("cutoff detection + summarizer call").

**Invariant:** When a worker's `finish_reason == "length"` (cut off mid-thought), a fresh, cheap model call summarizes the partial attempt. The summary is fed to the manager, *not* written to `notes.md`.

**Test:** Construct a worker call that truncates with `finish_reason == "length"`. Verify `_summarize_cutoff` is called. Verify the digest appears in the manager-facing summary but *not* in `notes.md`.

### INV-17 — Cut-off digest never into `notes.md`

**GVS5H source:** `multiagent.py:456-458`:

```python
# manager-facing summary below, never into notes.md: appending a digest per cut-off is
# unbounded, and muse truncates often enough to reach ~400KB of notes that way.
digest = _summarize_cutoff(ws, reply, task["desc"])
summary = (f"worker EXCEEDED THE TOKEN LIMIT and was cut off before finishing task: "
           ...)
```

**Status:** ❌ Plan says "cutoff detection + summarizer call" but doesn't specify where the digest goes.

**Invariant:** The cut-off digest is appended to the manager-facing `summary` string only. It is *never* written to `notes.md`. Appending a digest per cut-off is unbounded — GVS5H itself hit ~400KB of notes that way on 2026-08-13 before fixing it.

**Test:** Construct a worker call that truncates with `finish_reason == "length"`. Verify `notes.md` is *not* modified by the cut-off path. Verify the manager's prompt for the next round includes the digest in the `LATEST WORKER RESULT` field.

### INV-18 — Skip-finalize-when-done optimization

**GVS5H source:** `multiagent.py:592-595`:

```python
# Finalize only if the primary didn't already sign off on a usable answer (a redundant
# finalize can ramble past the token cap and destroy a correct intermediate answer).
if status == "done" and _has_answer(ws, spec):
    log("    [finalize] skipped (primary marked done)")
else:
    _worker(problem_text, spec, ws, {"id": 0, "desc": "finalize"}, log, finalize=True)
```

**Status:** ⚠ Phase 3 says "finalize if needed" but doesn't specify the optimization.

**Invariant:** Finalize is *skipped* if the manager already marked `done` with a usable answer. A redundant finalize can ramble past the token cap and destroy a correct intermediate answer.

**Test:** Construct a case where the manager marks `done` with a non-empty `solution.py`. Verify the finalize worker is *not* called. Construct a case where the manager marks `done` but `solution.py` is empty. Verify the finalize worker *is* called.

### INV-19 — Single-shot baseline (one call, no ledger)

**GVS5H source:** `multiagent.py:622-643` (`single_solve`).

**Status:** ⚠ Phase 3 mentions "Single-shot baseline mode (one call, same model)" but doesn't specify "no ledger" or that prompts differ.

**Invariant:** The single-shot baseline is one model call with the single-call prompt only. No `task.md`, no `plan.md`, no `notes.md` is written. The transcript records the single call.

**Test:** Run the single-shot baseline. Verify the workspace has only `task.md` (written at init) and `transcript.jsonl` (one entry). Verify no `plan.md`, `notes.md`, `solution.py`, `answer.md`, or `tasks.json` is written by the baseline.

---

## C. Worker / role-call invariants

### INV-20 — Worker = fresh context (no parent session history)

**GVS5H source:** Every role call in `multiagent.py` is a fresh `messages = [{"role": "system", ...}, {"role": "user", ...}]` construction. No prior conversation history is included.

**Status:** ✅ `docs/architecture.md` lines 18-19; ⚠ Phase 3 says "fresh context and ledger injection only" but doesn't restate the workspace-shared invariant.

**Invariant:** Each role call is a fresh chat completion. The worker receives only:
- The system prompt for the role.
- The user message, which contains only the ledger-injected state (`task.md`, `plan.md`, `notes.md`, `solution.py`/`answer.md`, `tasks.json` as relevant).

The worker does *not* receive:
- Prior conversation history.
- Parent session context.
- Tool definitions.
- Other roles' outputs (except via the ledger).

**Test:** Spawn a worker. Inspect the prompt. Verify it contains exactly the system prompt + the ledger-injected user message. Verify no prior conversation history is present. Verify no tool definitions are present.

### INV-21 — Worker = same model for every role

**GVS5H source:** `multiagent.py:42-43` — `MODEL` is read from env and used by every role call. No role-specific model selection.

**Status:** ✅ ADR 0004 §5 ("same model for every role").

**Invariant:** Every role call uses the same model id. No role-specific model selection. (The paper's experimental design depends on this — the manager and worker are the same model in a fresh context.)

**Test:** Configure a model id. Run a problem. Verify every role call in the transcript used the same model id.

### INV-22 — Worker = no tools, period

**GVS5H source:** Every role call in `multiagent.py` is a pure chat completion. No `tools` parameter is passed to the chat API.

**Status:** 🚫 ADR 0004 §5 says "prefer no / minimal tools"; Phase 3 says "Prefer minimal/no tools on role children (generation-shaped)."

**Invariant:** Workers have zero tools. They are pure chat completions, single generations. Any tool surface (even file read) breaks the "worker = single generation" invariant by allowing the worker to act as a multi-turn agent.

**Test:** Spawn a worker. Inspect the API call. Verify no `tools` parameter is passed. Add a regression test that fails if any tool surface is exposed to a role call.

### INV-23 — Sample-test verifier is a subprocess, not a "verifier agent"

**GVS5H source:** `multiagent.py:473-509` (`_run_samples` — runs `solution.py` via `sys.executable` against public stdin tests). ADR 0004 §6: "Sample tests remain an **external subprocess** owned by pi-zero-shot, not a 'verifier agent.'"

**Status:** ✅ ADR 0004 §6 + Phase 1 task ("Sample-test runner: run `solution.py` against public stdin samples (subprocess)").

**Invariant:** The sample-test verifier is a subprocess owned by pi-zero-shot. It is *not* an LLM "verifier agent." The verdict is a deterministic `{ran, passed, total, fail}` dict, not a model output.

**Test:** Inspect the sample-test runner. Verify it spawns a subprocess (`sys.executable` or equivalent). Verify the return value is a structured dict, not a model output.

### INV-24 — `_strip_code` strips fenced blocks from ideation

**GVS5H source:** `multiagent.py:137-140`:

```python
def _strip_code(text):
    """Remove fenced code blocks. Ideation must contribute approaches in prose, never a
    finished program -- otherwise the manager reads it as solved and skips the worker loop."""
    return re.sub(r"```.*?```", "[code omitted -- approach only]", text, flags=re.DOTALL).strip()
```

**Status:** ❌ Phase 2 mentions "Code extraction from fenced blocks" but not the *negative* invariant.

**Invariant:** The ideation worker's reply has fenced code blocks stripped *before* the manager sees it. Ideation must contribute approaches in prose, never a finished program — otherwise the manager reads it as solved and skips the worker loop.

**Test:** Construct an ideation reply that includes a fenced code block. Run it through `_strip_code`. Verify the code block is replaced with `[code omitted -- approach only]`. Verify the manager's prompt for the next round does *not* include the code block.

### INV-25 — `STRICT_FORMAT` env knob with "auto" detection

**GVS5H source:** `multiagent.py:59-61`:

```python
def _strict():
    return STRICT_FORMAT == "1" or (
        STRICT_FORMAT == "auto" and any(s in MODEL.lower() for s in ("muse", "glimmer")))
```

**Status:** ⚠ Phase 2 mentions "Strict-format mode (config flag)" but not the env name, "auto" mode, or the muse/glimmer model list.

**Invariant:** Strict-format mode is enabled if `STRICT_FORMAT == "1"` OR (`STRICT_FORMAT == "auto"` AND the model name contains "muse" or "glimmer"). When enabled, the prompt appends the "literal headers only" rule.

**Test:** Set `STRICT_FORMAT=1` with a non-muse model. Verify strict-format mode is enabled. Set `STRICT_FORMAT=auto` with a model named "muse-7b". Verify strict-format mode is enabled. Set `STRICT_FORMAT=auto` with a model named "qwen3.8-27b". Verify strict-format mode is disabled. Set `STRICT_FORMAT=0` with a muse model. Verify strict-format mode is disabled.

### INV-26 — Per-role temperatures

**GVS5H source:** `multiagent.py:_primary_plan` (0.3), `_ideation_worker` (0.4), `_primary_manage` (0.2), `_worker` (0.2), `single_solve` (0.2).

**Status:** ❌ Plan doesn't specify per-role temperatures.

**Invariant:** Each role uses a specific temperature: plan = 0.3, ideation = 0.4, manage = 0.2, worker = 0.2, single = 0.2. All configurable via env knobs.

**Test:** Run a problem with each role. Inspect the transcript. Verify each role call used the correct temperature.

---

## D. Transcript invariants

### INV-27 — Transcript records every call

**GVS5H source:** `multiagent.py:102-105` (`_record` appends a JSON line to `transcript.jsonl`); called at every role call via `_chat`.

**Status:** ✅ Phase 1 task ("Transcript recorder: append JSONL records with role, request, response, reasoning, tokens, finish_reason, provider metadata").

**Invariant:** Every role call appends a JSONL record to `transcript.jsonl`. The record includes: role, request (messages), response (content), reasoning (if available), tokens (completion_tokens), finish_reason, provider metadata.

**Test:** Run a problem. Read `transcript.jsonl`. Verify one line per role call. Verify each line has all the required fields.

### INV-28 — `infra_exhausted`/`infra_fail` flag

**GVS5H source:** `orchestrator.py:336` (`meta["infra_exhausted"] = True` when all reroute attempts fail without a usable completion); `multiagent.py:611-614` (`if final_empty and any(r.get("infra_exhausted") for r in recs): status_out["infra_fail"] = True`).

**Status:** ❌ Not mentioned anywhere in plan.

**Invariant:** When all reroute attempts fail without a usable completion, the transcript record has `infra_exhausted: True`. When a problem ends with no artifact and any call had `infra_exhausted: True`, the problem's `status_out` has `infra_fail: True`. The grader excludes `infra_fail` rows from pass@1.

**Test:** Construct a problem where all reroute attempts fail. Verify the transcript records have `infra_exhausted: True`. Verify the problem's `status_out` has `infra_fail: True`. Verify the grader excludes this problem from pass@1.

---

## E. Provider / orchestrator invariants

### INV-29 — Provider dispatch by model-name prefix

**GVS5H source:** `orchestrator.py:487-542` (`chat` dispatches by prefix: `groq:`/`claude:`/`openai:`/`dashscope:`/`anthropic:`/`openrouter:`/ollama).

**Status:** ⚠ Plan says "via `pi-ai`" but doesn't specify how model routing works.

**Invariant:** The model id's prefix determines the provider. `groq:` → Groq, `claude:` → Anthropic, `openai:` → OpenAI, `dashscope:` → DashScope, `anthropic:` → Anthropic, `openrouter:` → OpenRouter, no prefix → local ollama.

**Test:** Configure a model id with each prefix. Verify the corresponding provider is used. Verify no prefix → local ollama.

### INV-30 — Provider clamp detection

**GVS5H source:** `orchestrator.py:303-313`:

```python
# A provider clamping output below our cap is an infra cutoff, not the model's doing.
# Compare against cur_max -- the cap ACTUALLY SENT -- not CLOUD_MAX_TOKENS. After the
# 400/context shrink above lowers cur_max (e.g. 128000 -> 104000), a reply that fills
# the reduced budget is a legitimate truncation, but against the original cap it looks
# clamped (104000 < 0.9*128000) and gets discarded and retried.
cap_used = cur_max or CLOUD_MAX_TOKENS
clamped = finish == "length" and cap_used and (ntok or 0) < 0.9 * cap_used
```

**Status:** ❌ Phase 5 mentions "provider quirks" generically.

**Invariant:** Clamp detection compares the actual cap sent (`cur_max`), not the configured cap (`CLOUD_MAX_TOKENS`). A reply that fills a reduced budget is a legitimate truncation, not a clamp. A clamped reply is discarded and retried.

**Test:** Construct a case where a 400/context error shrinks `cur_max` from 128000 to 104000. Verify a reply that fills 104000 tokens is *not* marked clamped. Verify a reply that fills 90000 tokens *is* marked clamped (90000 < 0.9 × 128000). Verify a clamped reply is discarded and retried.

### INV-31 — Reroute budget and wall-clock caps

**GVS5H source:** `orchestrator.py:openai_chat` — up to 16 attempts with hard wall-clock caps per attempt.

**Status:** ❌ Plan doesn't specify a reroute budget or per-attempt timeout.

**Invariant:** When a provider returns a clamped or empty reply, the call is rerouted to another provider. Up to 16 attempts. Each attempt has a hard wall-clock cap. Discarded attempts are kept in the transcript (with their thinking) for token accounting.

**Test:** Configure a model that always returns empty replies. Verify the call is rerouted up to 16 times. Verify each discarded attempt is in the transcript. Verify the call eventually fails with `infra_exhausted: True` if no attempt produces usable output.

### INV-32 — `finish_reason` string comparison

**GVS5H source:** `multiagent.py:447` (`if wmeta.get("finish_reason") != "length":`), `:453` (`if wmeta.get("finish_reason") == "length" and not finalize:`).

**Status:** ❌ Plan doesn't specify the string union or how providers normalize.

**Invariant:** `finish_reason` is the string `"length"` (cut off mid-thought) or `"stop"` (clean completion). The cut-off summarizer triggers on `"length"`. Provider-specific variants (`"max_tokens"`, `"content_filter"`, etc.) must be normalized to this string union.

**Test:** Mock a provider that returns `finish_reason: "max_tokens"`. Verify the orchestrator normalizes to `"length"`. Verify the cut-off summarizer triggers.

### INV-33 — Reasoning capture

**GVS5H source:** `orchestrator.py:300` (`meta["reasoning"] = reasoning`).

**Status:** ❌ Phase 1 mentions "reasoning" in transcript but not how it's sourced per provider.

**Invariant:** For providers that support reasoning (e.g., GPT-5.6 with "thinking" mode), the reasoning content is captured in the transcript record's `reasoning` field. Provider-specific reasoning fields are normalized.

**Test:** Configure a provider with reasoning support. Run a call. Verify the transcript record has a non-empty `reasoning` field.

---

## F. Evaluation invariants

### INV-34 — LiveCodeBench `release_v6` hard split, 100 problems

**GVS5H source:** `codebase/v2-current/escalation/lcb100_hardest_v6.json` (100 pinned question_ids).

**Status:** ❌ Phase 4 says "subset of LCB or local fixtures" — doesn't pin the split or id list.

**Invariant:** Evaluation uses the LiveCodeBench `release_v6` hard split, 100 latest problems by contest date, with the frozen id list `lcb100_hardest_v6.json`.

**Test:** Run the eval. Verify exactly 100 problems are evaluated. Verify the question_ids match `lcb100_hardest_v6.json`.

### INV-35 — §3.3 MockBuffer / `readline()` fix

**GVS5H source:** `codebase/livecodebench/lcb_runner/evaluation/testing_util.py:94-100` — `BytesIO`-backed `MockBuffer` so reads advance position.

**Status:** ❌ Plan doesn't vendor or pin this fix.

**Invariant:** The eval driver uses a `MockBuffer` whose `readline()` advances position (via `BytesIO`). Upstream's broken `readline()` returned line 1 on every call. Every paper number is reported *after* this fix.

**Test:** Construct a candidate solution that reads multi-line input via `sys.stdin.buffer.readline()`. Run it through the eval driver. Verify the candidate is graded correctly (not misgraded as failing on multi-line input).

### INV-36 — Paired-pass protocol

**GVS5H source:** Paper §2.1 Table 1 (5 paired passes, paired t-test, per-pass Δ); GVS5H `runs/firstparty-128k-reasoning-on-5pass/` (3,200 workspaces).

**Status:** ❌ Phase 4 says "comparing single vs manager" — doesn't commit to passes or statistical test.

**Invariant:** Evaluation runs 5 paired passes. Each pass runs both the manager and single arms on the same 100 problems. Per-pass Δ = manager − single is reported. A paired t-test is used for significance.

**Test:** Run the eval. Verify 5 passes are run. Verify per-pass Δ is reported. Verify a paired t-test is computed.

### INV-37 — `capmatch` for Qwen3.8-27B single arm

**GVS5H source:** `codebase/v2-current/escalation/capmatch_q38.py` (127 lines, token-exact 250k→128k truncation using vLLM's own tokenizer).

**Status:** ❌ Not mentioned in plan.

**Invariant:** Qwen3.8-27B's single arm is generated at 250k cap. For like-for-like comparison with the manager arm (which ran at 128k), the single arm is token-exact truncated to 128k and the solution re-extracted. Without this, the +23.4 delta is not like-for-like.

**Test:** Run the Qwen3.8-27B single arm at 250k. Apply cap-match to 128k. Verify the truncated solution matches what would have been generated at 128k.

### INV-38 — `infra_fail` excluded from pass@1

**GVS5H source:** `multiagent.py:611-614` (`if final_empty and any(r.get("infra_exhausted") for r in recs): status_out["infra_fail"] = True`); consumed by the grader (excluded from pass@1).

**Status:** ❌ Not mentioned anywhere in plan.

**Invariant:** Problems with `infra_fail: True` are excluded from pass@1 scoring. They are not counted as failures (which would bias pass@1 downward) and not counted as successes.

**Test:** Construct a problem where the manager arm has `infra_fail: True`. Verify it is excluded from pass@1. Verify pass@1 is computed over the remaining 99 problems.

---

## Summary

| Section | Invariants | ✅ | ⚠ | ❌ | 🚫 |
|---|---|---|---|---|---|
| A. Workspace | 10 | 4 | 4 | 2 | 0 |
| B. Control flow | 9 | 5 | 2 | 2 | 0 |
| C. Worker / role-call | 7 | 3 | 1 | 2 | 1 |
| D. Transcript | 2 | 1 | 0 | 1 | 0 |
| E. Provider / orchestrator | 5 | 0 | 1 | 4 | 0 |
| F. Evaluation | 5 | 0 | 0 | 5 | 0 |
| **Total** | **38** | **13** | **8** | **16** | **1** |

The 16 ❌ gaps and 1 🚫 gap are the work. They map directly to the architecture gaps in `02-ARCHITECTURE-REVIEW.md` and the implementation tasks in `07-IMPLEMENTATION-PRIORITY.md`. The 8 ⚠ partial gaps need specification tightening.

This file is the contract. If a port preserves every invariant here, it is faithful to GVS5H v2. If it misses any, it is not.
