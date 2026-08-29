# Review-by-GLM — Risk Register

**Reviewer:** GLM (Z.ai), independent audit
**Date:** 2026-08-29
**Scope:** Risks for pi-zero-shot, ranked by impact × probability. Each risk has a concrete mitigation tied to a specific phase or ADR.

---

## Risk scoring

Each risk is scored on **Impact** (1=low, 5=critical) and **Probability** (1=unlikely, 5=will happen). The **Priority** column is `Impact × Probability`.

| Priority | Range | Action |
|---|---|---|
| 🔴 Critical | ≥ 16 | Must fix before any execution begins. |
| 🟠 High | 9–15 | Fix during the relevant phase. |
| 🟡 Medium | 5–8 | Fix during hardening (Phase 5) or document the divergence. |
| 🟢 Low | ≤ 4 | Acknowledge in README; not blocking. |

---

## Risk register

### 🔴 R1 — `infra_exhausted` gap biases pass@1 downward
- **Impact:** 5 (silently biases any future evaluation; provider outages look like model regressions)
- **Probability:** 5 (will happen on any long benchmark run; provider APIs are not 100% reliable)
- **Priority:** 25
- **GVS5H source:** `orchestrator.py:336` (set), `multiagent.py:611-614` (consumed as `infra_fail`)
- **Mitigation:** Add `infra_exhausted`/`infra_fail` to Phase 1 transcript schema, propagate through Phase 3 `status_out`, exclude from pass@1 in Phase 4 grader.

### 🔴 R2 — §3.3 MockBuffer fix not vendored silently misgrades local eval
- **Impact:** 5 (silently misgrades any candidate using `sys.stdin.buffer.readline()` for multi-line input)
- **Probability:** 5 (the bug is invisible without comparing against the fixed evaluator; GVS5H itself hit this)
- **Priority:** 25
- **GVS5H source:** `codebase/livecodebench/lcb_runner/evaluation/testing_util.py:94-100`
- **Mitigation:** Vendor or pin the §3.3 fix as a Phase 4 dependency of the eval driver.

### 🔴 R3 — "Minimal tools" wording silently breaks the worker = single-generation invariant
- **Impact:** 5 (any tool surface makes workers multi-turn agents, diverging from the paper)
- **Probability:** 4 (the word "minimal" invites interpretation; a future implementer will likely add "just one read tool")
- **Priority:** 20
- **GVS5H source:** All role calls in `multiagent.py` are pure chat completions with no tools.
- **Mitigation:** Change ADR 0004 §5 and Phase 3 task from "prefer no / minimal tools" to "no tools, period." Add a Phase 3 test that fails if any tool surface is exposed to a role call.

### 🔴 R4 — pi-subagents evolves to break "fresh context, no tools" invariant
- **Impact:** 4 (silent fidelity regression on pi-subagents version bump)
- **Probability:** 4 (pi-subagents is an evolving community package; minor version changes can shift semantics)
- **Priority:** 16
- **GVS5H source:** GVS5H doesn't use pi-subagents, but the invariants it must preserve (no parent session history, no inherited tools, ledger injection only) are at risk if pi-subagents' `context: "fresh"` semantics drift.
- **Mitigation:** Pin pi-subagents version in `package.json`. Add a Phase 3 regression test that asserts `context: "fresh"` does not inherit parent tools or session history. Keep the `pi-ai` fallback as the default if pi-subagents cannot preserve invariants.

### 🟠 R5 — Provider clamp detection missing makes mid-run cap shrinkage unsatisfiable
- **Impact:** 4 (GVS5H itself hit this: "16 attempts × a full 104k-token generation each, ~7h per call")
- **Probability:** 3 (only bites when a 400/context error shrinks the cap mid-run, which happened to one model in the paper)
- **Priority:** 12
- **GVS5H source:** `orchestrator.py:303-313` — compares against `cur_max` (cap actually sent), not `CLOUD_MAX_TOKENS`.
- **Mitigation:** Specify provider clamp detection logic in Phase 5, or document that `pi-ai` handles it (verify with `pi-ai` docs / source).

### 🟠 R6 — No paired-pass protocol makes future benchmark claims unverifiable
- **Impact:** 4 (cannot reproduce the paper's significance claims; p-values and Δ±SD missing)
- **Probability:** 4 (Phase 4 as written would produce single-pass numbers by default)
- **Priority:** 16
- **GVS5H source:** Paper §2.1 Table 1 (5 paired passes, paired t-test, per-pass Δ); GVS5H `runs/firstparty-128k-reasoning-on-5pass/` (3,200 workspaces for the §2.1 condition alone).
- **Mitigation:** Commit to a paired-pass protocol in Phase 4: 5 passes, paired t-test, per-pass Δ = manager − single, per-pass Δ reported alongside aggregate.

### 🟠 R7 — No LICENSE file blocks legal use and contribution
- **Impact:** 4 (nobody can legally use, copy, or contribute to the code)
- **Probability:** 5 (currently true; the repo has no LICENSE)
- **Priority:** 20
- **Mitigation:** Ship the MIT LICENSE. README:123 already says "recommended: MIT." It's a 21-line file.

### 🟠 R8 — No `package.json` / `tsconfig.json` / lockfile blocks Phase 1
- **Impact:** 4 (Phase 1 implementer must invent project structure from scratch; intent and artifact out of sync)
- **Probability:** 5 (currently true; ADR 0004 commits to TypeScript but no build tooling exists)
- **Priority:** 20
- **Mitigation:** Add `package.json`, `tsconfig.json`, lockfile before Phase 1 starts.

### 🟠 R9 — Misleading "Planning complete in-repo" status line misleads contributors
- **Impact:** 3 (misleads readers; wastes contributor time)
- **Probability:** 5 (currently true)
- **Priority:** 15
- **Mitigation:** Change `README.md:119` to "Planning drafted; Phase 0 (Discovery & mapping) not yet started."

### 🟠 R10 — ADR 0002 status-vs-Decision contradiction costs Phase 0 implementer time
- **Impact:** 3 (internal contradiction; Phase 0 task is redundant if ADR is Accepted, ADR is mislabeled if task is genuine)
- **Probability:** 5 (currently true)
- **Priority:** 15
- **Mitigation:** Mark ADR 0002 as Accepted and delete the Phase 0 task, OR rewrite ADR 0002 to present both options neutrally and leave the Phase 0 task as the decider.

### 🟡 R11 — No `capmatch_q38.py` analog makes Qwen3.8-27B comparison not like-for-like
- **Impact:** 3 (the paper's +23.4 delta for Qwen3.8-27B depends on cap-match; without it, the comparison is unfair)
- **Probability:** 3 (only bites if a future eval uses Qwen3.8-27B)
- **Priority:** 9
- **GVS5H source:** `codebase/v2-current/escalation/capmatch_q38.py` (127 lines, token-exact 250k→128k truncation using vLLM's own tokenizer).
- **Mitigation:** Implement a `capmatch` analog in Phase 5, or document that the local Qwen arm won't be cap-matched (and therefore the Qwen3.8-27B comparison is not directly paper-comparable).

### 🟡 R12 — `_strip_code` invariant missing lets manager misread ideation as solved
- **Impact:** 3 (manager may skip the worker loop if ideation includes code)
- **Probability:** 3 (ideation workers often include code blocks "to illustrate the approach")
- **Priority:** 9
- **GVS5H source:** `multiagent.py:137-140` (`_strip_code` strips fenced blocks from ideation).
- **Mitigation:** Port `_strip_code` in Phase 2 and document the negative invariant (ideation output must have code stripped).

### 🟡 R13 — Skip-finalize-when-done optimization missing can destroy correct solutions
- **Impact:** 3 (a redundant finalize can ramble past the token cap and destroy a correct intermediate answer)
- **Probability:** 3 (some fraction of "done" runs will hit this)
- **Priority:** 9
- **GVS5H source:** `multiagent.py:592-595`.
- **Mitigation:** Implement the skip-finalize-when-done optimization in Phase 3.

### 🟡 R14 — Cut-off digest into `notes.md` blows the size bound
- **Impact:** 3 (notes.md can reach hundreds of KB; GVS5H itself hit ~400KB on 2026-08-13)
- **Probability:** 3 (happens on models that truncate often — "muse" in GVS5H's case)
- **Priority:** 9
- **GVS5H source:** `multiagent.py:456-458` (cut-off digest goes to manager-facing summary only, never into `notes.md`).
- **Mitigation:** Specify the cut-off digest never-into-notes invariant in Phase 3.

### 🟡 R15 — No tests, no CI ships without automated quality gates
- **Impact:** 3 (regression risk; Phase 1, 2, 5 all promise tests but none exist)
- **Probability:** 5 (currently true)
- **Priority:** 15
- **Mitigation:** Add a test runner (Vitest or Jest for TypeScript) and `.github/workflows/ci.yml` before Phase 1 starts.

### 🟡 R16 — `ANS_RE` non-empty-answer guard missing lets rambling worker destroy good prior answer
- **Impact:** 2 (only bites for math problems where `answer.md` is used; code problems use `solution.py` which has its own guard)
- **Probability:** 3 (some fraction of truncated calls on math problems)
- **Priority:** 6
- **GVS5H source:** `multiagent.py:192` (`ANS_RE = re.compile(r"ANSWER:\s*\S", re.I)`), used at `:433`.
- **Mitigation:** Port the `ANS_RE` guard in Phase 1.

### 🟡 R17 — `STRICT_FORMAT` "auto" detection missing makes the flag a no-op on models that need it
- **Impact:** 2 (strict-format mode does nothing on "muse"/"glimmer" models without auto detection)
- **Probability:** 3 (only bites if a future eval uses those models)
- **Priority:** 6
- **GVS5H source:** `multiagent.py:59-61` (`STRICT_FORMAT == "auto"` and any of `("muse", "glimmer")` in `MODEL.lower()`).
- **Mitigation:** Port the `STRICT_FORMAT` env knob with "auto" mode and the muse/glimmer model list in Phase 2.

### 🟡 R18 — `MAX_TASKS=12` cap missing lets task list grow unboundedly
- **Impact:** 2 (task list can grow large enough to inflate manager prompts)
- **Probability:** 3 (some fraction of long runs)
- **Priority:** 6
- **GVS5H source:** `multiagent.py:72` (`MAX_TASKS = int(os.environ.get("MULTIAGENT_MAX_TASKS", "12"))`).
- **Mitigation:** Add `MAX_TASKS=12` as a config knob in Phase 1.

### 🟡 R19 — `wrote` guard missing re-grades previous round's solution
- **Impact:** 2 (manager gets a verdict about work this round didn't do; may declare "done" based on stale code)
- **Probability:** 3 (any round where worker truncates without writing new code)
- **Priority:** 6
- **GVS5H source:** `multiagent.py:574` (`if spec["kind"] == "code" and tests and wrote:`).
- **Mitigation:** Implement the `wrote` guard in Phase 3.

### 🟢 R20 — Per-role temperatures not specified
- **Impact:** 2 (loop behavior differs from GVS5H; results may diverge)
- **Probability:** 2 (default temperature from `pi-ai` may or may not match)
- **Priority:** 4
- **GVS5H source:** `multiagent.py:_primary_plan` (0.3), `_ideation_worker` (0.4), `_primary_manage` (0.2), `_worker` (0.2), `single_solve` (0.2).
- **Mitigation:** Specify per-role temperatures as config knobs in Phase 2.

### 🟢 R21 — `finish_reason` string normalization not specified
- **Impact:** 2 (cut-off summarizer depends on `finish_reason == "length"`; providers use different strings)
- **Probability:** 2 (depends on `pi-ai`'s normalization)
- **Priority:** 4
- **GVS5H source:** `multiagent.py:447`, `:453` (`if wmeta.get("finish_reason") == "length"`).
- **Mitigation:** Specify the `finish_reason` string union in Phase 5, or document that `pi-ai` normalizes.

### 🟢 R22 — `raw/PAPER.md` extract is thin
- **Impact:** 1 (the extract is the least faithful document in the repo, but it's just a reference doc)
- **Probability:** 5 (currently true)
- **Priority:** 5
- **Mitigation:** Expand `raw/PAPER.md` to include the §3.1 four-difference list and §3.3 MockBuffer fix description verbatim.

### 🟢 R23 — Single-commit history looks abandoned
- **Impact:** 2 (signals liveness; reviewers may judge harshly)
- **Probability:** 4 (currently true; repo pushed in one commit on 2026-08-29)
- **Priority:** 8
- **Mitigation:** Add `CHANGELOG.md`. Start committing Phase 0 work in small commits.

### 🟢 R24 — `tasks.json` write-only debug not specified
- **Impact:** 1 (could lead an implementer to over-engineer read-back logic)
- **Probability:** 3 (implementer may add read-back since the file is listed as a workspace file)
- **Priority:** 3
- **GVS5H source:** `multiagent.py:209-211` (`_save_tasks` writes), `:588` (called after each manager round); never read back.
- **Mitigation:** Document `tasks.json` as write-only debug in Phase 1.

### 🟢 R25 — Reasoning capture per provider not specified
- **Impact:** 2 (transcript won't include reasoning content for providers that support it)
- **Probability:** 2 (depends on `pi-ai`'s reasoning capture)
- **Priority:** 4
- **GVS5H source:** `orchestrator.py:300` (`meta["reasoning"] = reasoning`).
- **Mitigation:** Specify reasoning capture per provider in Phase 5, or document that `pi-ai` handles it.

---

## Risk summary

| Priority bucket | Count | Risks |
|---|---|---|
| 🔴 Critical (≥ 16) | 4 | R1, R2, R3, R4 |
| 🟠 High (9–15) | 6 | R5, R6, R7, R8, R9, R10 |
| 🟡 Medium (5–8) | 9 | R11, R12, R13, R14, R15, R16, R17, R18, R19 |
| 🟢 Low (≤ 4) | 6 | R20, R21, R22, R23, R24, R25 |

**Total:** 25 risks identified.

---

## Critical risks (must fix before execution)

The four critical risks (R1, R2, R3, R4) all share a common pattern: **silent fidelity regressions that are invisible without comparing against the GVS5H reference.** A port that misses any of these will run, will produce output, and may even look like it works — but the output will not be paper-comparable.

- **R1 (`infra_exhausted`)** — provider outages look like model failures.
- **R2 (MockBuffer fix)** — local eval silently misgrades.
- **R3 (no tools, period)** — workers become multi-turn agents.
- **R4 (pi-subagents version pin)** — pi-subagents drift silently breaks the fresh-context invariant.

These four should be fixed before any Phase 1 code is written. R1 and R2 are documentation/specification gaps that can be closed in Phase 0 (revised). R3 is a one-line ADR fix. R4 is a `package.json` + test addition.

---

## High risks (fix during the relevant phase)

The six high risks (R5, R6, R7, R8, R9, R10) are a mix of:
- **Specification gaps** (R5 — clamp detection; R6 — paired-pass protocol) — fix in the relevant phase (Phase 5 and Phase 4 respectively).
- **Repo health** (R7 — LICENSE; R8 — build tooling; R9 — status line; R10 — ADR 0002 contradiction) — fix in Phase 0 (revised) before any code is written.

The repo health risks (R7–R10) are all 5–30 minute fixes. They should be batched into a single "Phase 0 repo health" PR before any Phase 1 work begins.

---

## Risk-register verdict

The risk profile is dominated by **silent fidelity regressions** (R1, R2, R3, R4, R5, R11, R12, R13, R14, R16, R17, R18, R19) — 13 of 25 risks are places where a port that misses the gap will run but produce output that's not paper-comparable. This is the signature risk of porting a research artifact: the gaps don't crash, they silently diverge.

The mitigations are all concrete and tied to specific phases. The total mitigation effort is ~2–3 days of documentation/specification work (Phase 0 revised + ADR fixes + adding tasks to existing phases) plus the implementation work already scoped in `07-IMPLEMENTATION-PRIORITY.md`.

The risk register should be revisited at each phase exit. `VERIFY-LOG.md` (currently empty) is the right place to record "we closed R1 in Phase 1 commit X; we closed R6 in Phase 4 commit Y."
