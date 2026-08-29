# Review-by-GLM — Architecture Review

**Reviewer:** GLM (Z.ai), independent audit
**Date:** 2026-08-29
**Scope:** Architecture of pi-zero-shot's plan, the control-flow diagram, and the line-by-line gap analysis against GVS5H v2 `multiagent.py` and `orchestrator.py`.

---

## 1. What pi-zero-shot's plan says it will build

### 1.1 The control flow (from README:45-64)

```text
User coding task
    |
    ▼
Manager (plan) ──► plan.md + seed tasks
    |
    ▼
Ideation worker ──► notes.md (approaches only)
    |
    ▼
┌─ Manager manage ◄── sample-test verdict ──────────────┐
│         │                                              │
│         ▼                                              │
│   Worker (fresh context) ──► solution.py + notes.md    │
│         │                                              │
│         └────────────── loop until done / max iters ────┘
    |
    ▼
Finalize (if needed) ──► graded artifact + transcript.jsonl
```

### 1.2 The mapping table (from `docs/architecture.md` lines 9-20)

| Paper Concept | Pi Mapping |
|---|---|
| Shared filesystem workspace | `LedgerWorkspace` (real FS preferred) |
| Manager (primary) | Deterministic supervisor (TS state machine) |
| Worker / role call (fresh context) | Fresh one-shot via pi-subagents or `pi-ai` / RPC |
| `plan.md` / `notes.md` / `solution.py` | Files in ledger; harness writes after parse |
| `transcript.jsonl` | Owned by pi-zero-shot |
| Sample-test verifier | Subprocess in pi-zero-shot |
| Single model, zero-shot | Same model id for every role via `pi-ai` |
| Env-driven config | Extension config / skill options |

### 1.3 The recommended extension shape (from `docs/architecture.md`)

- Name: `pi-zero-shot` / ledger-orchestrator skill
- Activation: slash command (`/ledger`, `/self-orchestrate`) or explicit mode
- Core loop: sequential manager → one worker → sample tests → manager (GVS5H v2)
- Role children: paper prompts; ledger injection only; minimal/no tools when possible
- Observability: ledger files + full `transcript.jsonl`
- Baseline: single-shot mode for fair comparison

### 1.4 The non-goals (MVP)

- Changing Pi core agent loop.
- Training or learned orchestrators.
- Full multi-agent debate / MoA / parallel specialist teams as the measured path.
- Replacing Pi's default tools for ordinary interactive use.

---

## 2. The architecture is faithful in spirit

The plan correctly identifies:

- **The control-flow order.** Plan → ideation → manage ↔ worker (+ sample tests) → finalize. Matches `multiagent.py:547-595` (`multiagent_solve`).
- **The sample-test hard override.** The README diagram shows the feedback arrow from "sample-test verdict" back to the manager. Matches `multiagent.py:581-587`.
- **The notes-rewrite invariant.** `docs/architecture.md` line 18 and Phase 1 task list both state "notes **rewrite**." Matches `multiagent.py:18-20` and `:450`.
- **The size-bounded workspace feeds.** Phase 1 says "Hard size bounds (mirror paper `MAX_PLAN_CHARS` and notes cap)." Matches `multiagent.py:197` (`MAX_PLAN_CHARS=4000`) and the 8000-char notes bound at `:281`, `:450`.
- **The single-shot baseline.** Phase 3 task list includes "Single-shot baseline mode (one call, same model, for comparison)." Matches `multiagent.py:622-643` (`single_solve`).
- **The provider-agnostic intent.** ADR 0004 §7 commits to `@earendil-works/pi-ai` as the fallback. Matches GVS5H's `orchestrator.py:chat` dispatch by model-name prefix (`:487-542`).
- **The fresh-context worker.** ADR 0004 §1 says "fresh context every role call." Matches GVS5H's `_chat` at every role call.

The author(s) clearly read `multiagent.py` carefully. The vendored copy at `_upstream/GVS5H_multiagent_v2.py` is byte-identical to the GVS5H source (md5 `a00572b27462b57cc88b8315482d503a`), which is strong evidence of careful source-of-truth grounding.

---

## 3. The 12-line gap table (what the plan misses)

The table below is the result of a line-by-line cross-check of pi-zero-shot's plan against GVS5H `multiagent.py` and `orchestrator.py`. Each row shows a concrete invariant in GVS5H, the file:line where it lives, the status in pi-zero-shot's plan, and the consequence if a faithful port misses it.

The full per-row crosswalk (every plan claim → GVS5H source line) is in `04-GVS5H-FEATURE-MAPPING.md`. This section summarizes the 12 invariants that are missing or underspecified.

### 3.1 Critical gaps (blocks fidelity / reproduction)

#### Gap C1 — `infra_exhausted` / `infra_fail` flag

**GVS5H source:**
- `orchestrator.py:336` — `meta["infra_exhausted"] = True` when all reroute attempts fail without a usable completion.
- `multiagent.py:611-614` — `if final_empty and any(r.get("infra_exhausted") for r in recs): status_out["infra_fail"] = True`.

**What it does:** excludes provider outages from pass@1 scoring. Without this, a provider outage during a benchmark run is scored as a model failure, biasing pass@1 downward.

**Plan status:** ❌ Not mentioned anywhere — not in Phase 1 (transcript schema), not in Phase 3 (control flow), not in Phase 4 (observability).

**Consequence:** Any future evaluation claim is unverifiable. A single provider hiccup looks like a model regression.

#### Gap C2 — §3.3 MockBuffer / `readline()` fix in the evaluator

**GVS5H source:**
- `codebase/livecodebench/lcb_runner/evaluation/testing_util.py:94-100` — `BytesIO`-backed `MockBuffer` so reads advance position.
- GVS5H README §2: "every number in the paper is reported after fixing it."

**What it does:** upstream LiveCodeBench's mock returned line 1 on every `readline()` call. The fix makes reads stateful so multi-line stdin input works. Critically, this bug *silently poisoned the v2 verifier's external signal* — the verifier runs the candidate as a real subprocess where `readline()` works, so the manager was told "passed" for programs the hidden grader marked wrong.

**Plan status:** ❌ Phase 4 says "Minimal benchmark driver (subset of LCB or local fixtures)" — does not vendor or pin the fix.

**Consequence:** Local eval silently misgrades any candidate using `sys.stdin.buffer.readline()` for multi-line input.

#### Gap C3 — `capmatch_q38.py` — token-exact 250k→128k truncation

**GVS5H source:**
- `codebase/v2-current/escalation/capmatch_q38.py` (127 lines) — replays Qwen3.8-27B's single-call generations at 128k cap, token-exact, using the serving stack's own tokenizer.
- Paper §3.2: "the column reports that arm cap-matched back to 128k so the row is like-for-like."

**What it does:** Qwen3.8-27B's single arm was generated at 250k cap; its manager arm ran at 128k. To make the comparison fair, the single arm is token-exact truncated to 128k and the solution re-extracted. The +23.4 delta in the paper depends on this procedure.

**Plan status:** ❌ Not mentioned.

**Consequence:** Any future Qwen3.8-27B comparison with the manager arm is not like-for-like. The paper's headline +23.4 delta would not reproduce.

#### Gap C4 — Paired-pass protocol

**GVS5H source:**
- Paper §2.1 Table 1 — "five independent passes" with paired per-pass Δ = manager − single and Δ ± SD.
- GVS5H `runs/firstparty-128k-reasoning-on-5pass/` — 3,200 workspaces for the §2.1 condition alone (100 problems × 5 passes × 4 arms).

**What it does:** the paper's significance claims depend on a paired t-test across 5 paired passes. The per-pass Δ column shows the consistency of the effect.

**Plan status:** ❌ Phase 4 says "comparing single vs manager" — no commitment to passes, statistical test, or per-pass reporting.

**Consequence:** A single-pass comparison cannot reproduce the paper's significance claims. p-values and Δ±SD will be missing.

#### Gap C5 — "No tools, period" on workers

**GVS5H source:**
- Every role call in `multiagent.py` is a pure chat completion with no tools. Workers are single generations, not multi-turn agents.

**Plan status:** 🚫 ADR 0004 §5 says "prefer no / minimal tools so a role remains a generation, not a multi-turn edit agent." Phase 3 task says "Prefer minimal/no tools on role children (generation-shaped)."

**Consequence:** The word "minimal" opens a door the paper closes. Any tool surface breaks the "worker = single generation" invariant by allowing the worker to act as a multi-turn agent.

#### Gap C6 — Misleading status line

**GVS5H source:** N/A — this is an internal pi-zero-shot issue.

**Plan status:** 🚫 README:119 says "Planning complete in-repo. Implementation follows `plan/phase-*.md` in order."

**Reality:**
- Phase 0's exit criteria are all unchecked (see `05-ROADMAP-AND-EXECUTION-CRITIQUE.md`).
- ADR 0002 status is "Proposed."
- `VERIFY-LOG.md` is empty (header row only).

**Consequence:** A reader who takes the status line at face value will be misled.

### 3.2 Significant gaps (affects architecture / fidelity)

#### Gap S1 — Provider clamp detection

**GVS5H source:** `orchestrator.py:303-313` — compares the *actual* cap sent (`cur_max`), not the configured cap (`CLOUD_MAX_TOKENS`), when detecting provider clamping.

```python
cap_used = cur_max or CLOUD_MAX_TOKENS
clamped = finish == "length" and cap_used and (ntok or 0) < 0.9 * cap_used
```

The GVS5H README §2 explicitly calls this out as a post-paper fix: a 400/context error shrinks `cur_max` mid-run, then a reply that fills the reduced budget looks "clamped" against the original cap and gets discarded and retried — "that made every call after a shrink unsatisfiable: 16 attempts × a full 104k-token generation each, ~7h per call. Cost muse's manager p3 sixteen hours on a single problem."

**Plan status:** ❌ Phase 5 mentions "provider quirks" generically. Does not specify the clamp-detection logic.

**Consequence:** A future Phase 5 implementer using `pi-ai` may not even have access to `cur_max`. Without the clamp-detection logic, mid-run cap shrinkage makes every subsequent call unsatisfiable.

#### Gap S2 — Reroute budget and wall-clock caps

**GVS5H source:** `orchestrator.py:openai_chat` — reroutes up to 16 attempts with hard wall-clock caps per attempt. Each discarded attempt is still real model output and is kept in the transcript (with its thinking) for token accounting.

**Plan status:** ❌ Does not specify a reroute budget or per-attempt timeout. Through `pi-ai` this may be hidden, but the plan should commit to "let pi-ai handle retries" or "implement reroute ourselves."

**Consequence:** Silence here is a future failure mode: a flaky provider can hang the loop or inflate cost.

#### Gap S3 — `MAX_TASKS=12` cap

**GVS5H source:** `multiagent.py:72` — `MAX_TASKS = int(os.environ.get("MULTIAGENT_MAX_TASKS", "12"))`. The live task list is capped at 12 entries.

**Plan status:** ❌ Phase 1 (LedgerWorkspace) and Phase 2 (task parser) do not mention this cap.

**Consequence:** A faithful port should expose it as a config knob and enforce it. Without it, the task list can grow unboundedly.

#### Gap S4 — `_strip_code` ideation invariant

**GVS5H source:** `multiagent.py:137-140` — `_strip_code` removes fenced code blocks from the ideation worker's reply *before* the manager sees it.

```python
def _strip_code(text):
    """Remove fenced code blocks. Ideation must contribute approaches in prose, never a
    finished program -- otherwise the manager reads it as solved and skips the worker loop."""
    return re.sub(r"```.*?```", "[code omitted -- approach only]", text, flags=re.DOTALL).strip()
```

**Plan status:** ❌ Phase 2 mentions "Code extraction from fenced blocks" but not the *negative* invariant — that ideation's output must have code stripped to prevent the manager misreading it as a solved problem.

**Consequence:** A naive port lets the manager misread ideation as a solved problem and skip the worker loop.

#### Gap S5 — Skip-finalize-when-done optimization

**GVS5H source:** `multiagent.py:592-595`:

```python
if status == "done" and _has_answer(ws, spec):
    log("    [finalize] skipped (primary marked done)")
else:
    _worker(problem_text, spec, ws, {"id": 0, "desc": "finalize"}, log, finalize=True)
```

Comment: "a redundant finalize can ramble past the token cap and destroy a correct intermediate answer."

**Plan status:** ⚠ Phase 3 says "Finalize worker if needed" but does not specify the optimization.

**Consequence:** A naive port that always runs finalize will occasionally destroy correct solutions.

#### Gap S6 — Cut-off digest never into `notes.md`

**GVS5H source:** `multiagent.py:456-458`:

```python
# manager-facing summary below, never into notes.md: appending a digest per cut-off is
# unbounded, and muse truncates often enough to reach ~400KB of notes that way.
digest = _summarize_cutoff(ws, reply, task["desc"])
summary = (f"worker EXCEEDED THE TOKEN LIMIT and was cut off before finishing task: ...")
```

**Plan status:** ❌ Phase 3 says "cutoff detection + summarizer call" but does not specify where the digest goes.

**Consequence:** A naive port would append the digest to `notes.md` and blow the notes bound. (The GVS5H comment notes this actually happened to them on 2026-08-13 — notes.md reached ~400KB — before they fixed it.)

#### Gap S7 — `ANS_RE` non-empty-answer guard

**GVS5H source:** `multiagent.py:192` — `ANS_RE = re.compile(r"ANSWER:\s*\S", re.I)`, used at `:433`:

```python
if ans and (ANS_RE.search(ans) or not _read(ws, "answer.md").strip()):
    _write(ws, "answer.md", ans)
    wrote = True
```

The `answer.md` is only overwritten if the new reply has a parseable `ANSWER:` line (or the file is empty), so a rambling/truncated call cannot destroy a good prior answer.

**Plan status:** ❌ Phase 1 (LedgerWorkspace) does not mention this guard.

**Consequence:** Without it, a rambling worker can destroy a good prior answer.

#### Gap S8 — `STRICT_FORMAT` "auto" detection

**GVS5H source:** `multiagent.py:59-61`:

```python
def _strict():
    return STRICT_FORMAT == "1" or (
        STRICT_FORMAT == "auto" and any(s in MODEL.lower() for s in ("muse", "glimmer")))
```

Strict-format mode auto-detects models with "muse" or "glimmer" in the name.

**Plan status:** ⚠ Phase 2 mentions "Strict-format mode (config flag) that appends the paper's 'literal headers only' rule" but not the env name, "auto" mode, or the model-name-prefix logic.

**Consequence:** Without it, strict-format mode is a flag with no behavior on the models that actually need it.

#### Gap S9 — No LICENSE file

**Plan status:** ❌ README:123 says "TBD (recommended: MIT)" but no `LICENSE` file exists.

**Consequence:** A public repo without a LICENSE is "all rights reserved" by default — nobody can legally use, copy, or contribute to the code. Trivial fix.

#### Gap S10 — No build tooling despite committing to TypeScript

**Plan status:** ❌ ADR 0004 §1 commits to "deterministic TypeScript manager loop matching GVS5H v2." `.gitignore` lists `node_modules/`, `dist/`, `.turbo/`. But no `package.json`, `tsconfig.json`, or lockfile exists.

**Consequence:** A Phase 1 implementer must invent project structure from scratch. Intent and artifact out of sync.

### 3.3 Moderate gaps (quality / process)

| # | Gap | GVS5H source | Plan status | Consequence |
|---|---|---|---|---|
| M1 | Per-role temperatures (0.3 plan, 0.4 brainstorm, 0.2 task/curate/single) | `multiagent.py:_primary_plan`, `_ideation_worker`, `_worker`, `single_solve` | ❌ Not specified | Without per-role temperatures, the loop's behavior differs from GVS5H. |
| M2 | `finish_reason` string normalization across providers | `multiagent.py:447`, `:453` (`finish_reason == "length"` triggers cut-off summarizer) | ❌ Not specified | The cut-off summarizer depends on this string. `pi-ai` may collapse providers' finish_reason variants into a generic type. |
| M3 | `wrote` guard: only run sample tests when worker actually wrote code | `multiagent.py:574` (`if spec["kind"] == "code" and tests and wrote:`) | ❌ Not specified | A naive port would re-grade the previous round's solution.py and hand the manager a verdict about work this round didn't do. |
| M4 | `tasks.json` is debug-only, written after each manager round but NOT read back | `multiagent.py:209-211`, `:588` | ⚠ Plan lists `tasks.json` but doesn't specify it's write-only debug | Could lead an implementer to over-engineer read-back logic. |
| M5 | No tests, no test runner, no CI | — | ❌ Phase 1, 2, 5 all promise tests; nothing exists | Tests deferred indefinitely in practice. |
| M6 | No dependency pinning (`@earendil-works/pi-ai`, pi-subagents, `@earendil-works/pi-agent-core`) | — | ❌ No `package.json` | A future `npm install` may pull a breaking version. |
| M7 | ADR 0002 status contradicts its Decision section | — | 🚫 ADR says Proposed, Decision says "Prefer a real filesystem workspace… as the primary ledger implementation." Phase 0 has a redundant task to "decide." | Internal contradiction. Costs a Phase 0 implementer time. |
| M8 | `raw/PAPER.md` is a 21-line extract — abstract + link table only | — | ⚠ Does not include §3.1 four-difference list, §3.3 MockBuffer fix, or any headline numbers | Least faithful document in the repo. |

---

## 4. The pi-subagents dependency question

### 4.1 What ADR 0004 gets right

ADR 0004's decision (pi-subagents as optional spawn helper, not as builtin agents/teams) is reasonable. The "do not use" list (builtin `worker`/`reviewer`/`scout`, council modes, parallel fan-out, fork-default context) shows the author(s) understand the fidelity risk. The fallback path (direct `pi-ai` or `pi --mode rpc` one-shots) is a sensible escape hatch.

### 4.2 Three concerns

1. **No version pin.** pi-subagents and `@earendil-works/pi-agent-core` versions are unspecified. pi-subagents' own evolution could break the "fresh context, no tools" invariant. The plan should commit to a pinned version (or to the no-pi-subagents fallback as the default).

2. **"Context: fresh" is asserted, not verified.** ADR 0004 §1 says "fresh context every role call." But pi-subagents' actual `context: "fresh"` semantics are not tested against GVS5H's invariant. A "fresh" context that still inherits parent tools or system prompts would silently break the worker = single-generation invariant. The plan should include a Phase 3 task to *test* pi-subagents' `context: "fresh"` against GVS5H's role-call shape.

3. **"Prefer no / minimal tools" should be "no tools, period."** See Gap C5. This is the single most important ADR-level fix.

### 4.3 The TypeScript assumption

The `.gitignore` (Node/TS patterns) and ADR 0004 §1 ("deterministic TypeScript manager loop") both commit to TypeScript. The Pi harness is (per the docs) JS/TS, so TypeScript is reasonable. But:

- No `package.json` exists. No `tsconfig.json`. No lockfile.
- No Pi extension API surface is pinned (which `@earendil-works/pi-agent-core` version? which extension schema version?).
- Porting Python control flow to TypeScript introduces subtle questions (numeric precision for temperatures/tokens, string union types for `finish_reason`) that the plan does not address. GVS5H uses string comparisons (`finish_reason == "length"`); TypeScript would use string literal types. Either is fine — but the plan should pick.

---

## 5. What's right about the architecture (worth keeping)

Despite the gaps, the architecture plan has several real strengths that should be preserved in any revision:

1. **The control-flow diagram is correct.** Plan → ideation → manage ↔ worker (+ sample tests) → finalize. The sample-test feedback arrow is foregrounded, not buried.

2. **The mapping table is faithful.** `docs/architecture.md` lines 9–20 correctly map paper primitives to Pi equivalents. No invented concepts, no renamed invariants.

3. **The ADR discipline is strong.** Four ADRs with clear context/decision/consequences. ADR 0001 (extension not core fork) and ADR 0003 (sequential manager-worker) are well-reasoned.

4. **The pi-subagents decision is right.** "Package = plumbing, paper semantics stay in this repo" is exactly the right framing.

5. **The non-goals are honest.** Disclaiming paper-number reproduction is the right call given the scope.

6. **The vendored reference is byte-identical.** `_upstream/GVS5H_multiagent_v2.py` md5-matches GVS5H's `multiagent.py`. The author(s) did their homework on the source-of-truth copy.

The architecture review verdict: **the plan is faithful in spirit and in the headline invariants, but a faithful port requires closing the 12 gaps before any "GVS5H v2 compatible" claim is justified.** The 12 gaps cluster in three areas:

- **Provider quirks** (clamp detection, reroute budget, infra flag, temperature, finish_reason, reasoning capture) — 6 gaps. Most consequential for runtime correctness.
- **Evaluation harness** (LCB split, MockBuffer fix, regrade, capmatch, paired-pass, per-pass Δ) — 6 gaps. Most consequential for any future benchmark claim.
- **Workspace subtleties** (`MAX_TASKS`, `wrote` guard, cut-off digest never into notes, `ANS_RE`) — 4 gaps. Most consequential for fidelity to the paper's "size-bounded workspace feeds" invariant.

The next sections give detailed critiques of the ADRs (`03-ADR-CRITIQUE.md`), the full per-row crosswalk (`04-GVS5H-FEATURE-MAPPING.md`), and the execution state (`05-ROADMAP-AND-EXECUTION-CRITIQUE.md`).
