# Review-by-GLM — Implementation Priority

**Reviewer:** GLM (Z.ai), independent audit
**Date:** 2026-08-29
**Scope:** Recommended execution order with effort estimates. Each item is tied to a specific phase, ADR, or risk from the rest of this review.

---

## How to use this file

This file converts the critique in `02-ARCHITECTURE-REVIEW.md`, `03-ADR-CRITIQUE.md`, `05-ROADMAP-AND-EXECUTION-CRITIQUE.md`, and `06-RISK-REGISTER.md` into a concrete ordered to-do list. Each item shows:
- **ID** — `P#` for process, `A#` for architecture, `E#` for evaluation, `D#` for documentation.
- **Effort** — estimated wall-clock time for one full-time implementer.
- **Ties to** — risks (R#), gaps (C#/S#/M#), ADRs, phases.
- **Why it matters** — one-sentence justification.

The list is ordered: do the items at the top first. Items in the same priority bucket can be done in parallel.

---

## Priority 1 — Pre-Phase-0 repo health (do today, ~2 hours total)

These are the trivial fixes that should land before any planning or implementation work continues. They are all 5–30 minute fixes with disproportionate impact on legality, contributor experience, and the misleading status quo.

| ID | Item | Effort | Ties to | Why it matters |
|---|---|---|---|---|
| P1 | Mark ADR 0002 as Accepted (or rewrite it to genuinely Proposed). | 5 min | R10, ADR 0002 | Resolves the ADR-vs-Phase-0 contradiction. |
| P2 | Add a `LICENSE` file (MIT, per the README's own recommendation). | 2 min | R7 | Unblocks legal use and contribution. |
| P3 | Add `package.json` + `tsconfig.json` + lockfile before Phase 1 starts. | 30 min | R8 | Unblocks Phase 1; aligns intent with artifact. |
| P4 | Add a CI workflow (`.github/workflows/ci.yml`) that runs `tsc --noEmit` + `npm test` + markdown-lint. | 1 hour | R15 | Catches regressions before they ship. |
| P5 | Add a `CHANGELOG.md` so the single-commit history doesn't look abandoned. | 10 min | R23 | Signals liveness. |
| P6 | Update README status line from "Planning complete in-repo" to "Planning drafted; Phase 0 not yet started." | 1 min | R9, Gap C6 | Stops misleading readers. |
| P7 | Change "prefer no / minimal tools" to "no tools, period" in ADR 0004 §5 and Phase 3 task. | 5 min | R3, Gap C5, ADR 0004 | Closes the most consequential ADR-level gap. |

**Subtotal: ~2 hours.**

---

## Priority 2 — Phase 0 (revised) gap closure (~1 day)

These are the documentation/specification tasks that should land before Phase 1 begins. They convert the 12 architectural gaps from `02-ARCHITECTURE-REVIEW.md` into concrete phase tasks.

| ID | Item | Effort | Ties to | Why it matters |
|---|---|---|---|---|
| P8 | Actually execute Phase 0's discovery tasks. Update `docs/architecture.md` with the 12 gaps from `02-ARCHITECTURE-REVIEW.md` §3. | 1–2 days | Phase 0 exit criteria | Closes the gap between "planning drafted" and "planning complete." |
| P9 | Add a "Known divergences from GVS5H" section to `docs/` listing the 12 gaps and how each will be closed in later phases. | 30 min | All 12 gaps | Forces honesty about fidelity. |
| P10 | Add a "Reference file:line map" appendix to `docs/architecture.md` showing each plan claim → GVS5H source line. | 1 hour | All 12 gaps | Makes the fidelity claim verifiable. |
| P11 | Expand `raw/PAPER.md` to include the §3.1 four-difference list and §3.3 MockBuffer fix description verbatim. | 30 min | R22, Gap M8 | The current extract is the least faithful document in the repo. |
| P12 | Pin pi-subagents version (or commit to the no-pi-subagents fallback as the default). | 30 min | R4 | Without it, a future `npm install` may pull a breaking version. |
| P13 | Add a Phase 3 task to test pi-subagents' `context: "fresh"` against GVS5H's role-call shape. | 10 min (planning) | R4 | "Fresh" is asserted, not verified. |

**Subtotal: ~1 day.**

---

## Priority 3 — Architecture gaps (close during Phases 1–5, ~3 days total)

These are the 12 architectural gaps from `02-ARCHITECTURE-REVIEW.md` §3, distributed across the phases where they belong. Each is a specification or implementation task that should be added to the existing phase plan.

### During Phase 1 (Core ledger primitives)

| ID | Item | Effort | Ties to | Why it matters |
|---|---|---|---|---|
| A1 | Pin the size bound numbers: `MAX_PLAN_CHARS=4000`, `MAX_NOTES_CHARS=8000`, `MAX_ANSWER_CHARS=20000`, `MAX_TASKS=12`. Expose all four as config knobs. | 30 min | Gap S3, R18, R20 | Phase 1 mentions "size caps" but doesn't pin numbers. |
| A2 | Implement the `wrote` guard: only run sample tests when worker actually wrote code. | 30 min | Gap M3, R19 | Without it, manager gets a verdict about work this round didn't do. |
| A3 | Implement the `ANS_RE` non-empty-answer guard for `answer.md` overwrites. | 15 min | Gap S7, R16 | Without it, a rambling worker can destroy a good prior answer. |
| A4 | Add `infra_exhausted`/`infra_fail` to the transcript schema (one extra field on `_record`). | 30 min | Gap C1, R1 | Without it, provider outages bias pass@1 downward. |
| A5 | Implement workspace reset semantics (all files cleared at the start of each problem). | 30 min | ADR 0002 | Matches `multiagent.py:540-543`. |
| A6 | Document the atomicity choice (match GVS5H plain read/write OR add atomicity with documented divergence). | 30 min | Phase 1 task | Phase 1 promises "atomic read/write" without specifying the mechanism. |

**Phase 1 subtotal: ~3 hours.**

### During Phase 2 (Role prompts & parsing)

| ID | Item | Effort | Ties to | Why it matters |
|---|---|---|---|---|
| A7 | Port `_strip_code` and document the negative invariant (ideation output must have code stripped). | 30 min | Gap S4, R12 | Without it, manager misreads ideation as solved. |
| A8 | Specify `STRICT_FORMAT` env knob with "auto" mode and muse/glimmer model list. | 30 min | Gap S8, R17 | Without it, strict-format mode is a no-op on models that need it. |
| A9 | Specify per-role temperatures (0.3 plan, 0.4 brainstorm, 0.2 task/curate/single) as config knobs. | 15 min | Gap M1, R20 | Without it, loop behavior differs from GVS5H. |

**Phase 2 subtotal: ~1.5 hours.**

### During Phase 3 (Manager-worker loop as Pi extension)

| ID | Item | Effort | Ties to | Why it matters |
|---|---|---|---|---|
| A10 | Add a Phase 3 test that fails if any tool surface is exposed to a role call. | 1 hour | Gap C5, R3, R4 | Hardens the "worker = single generation" invariant. |
| A11 | Implement the skip-finalize-when-done optimization. | 30 min | Gap S5, R13 | Without it, redundant finalize can destroy correct solutions. |
| A12 | Implement the cut-off digest never-into-notes invariant. | 30 min | Gap S6, R14 | Without it, notes.md can blow the size bound. |
| A13 | Propagate `infra_exhausted` through `status_out` and consume it in the grader. | 1 hour | Gap C1, R1 | The Phase 1 schema addition must be consumed to be useful. |
| A14 | Document `tasks.json` as write-only debug (written after each manager round, never read back). | 15 min | Gap M4, R24 | Prevents over-engineering read-back logic. |

**Phase 3 subtotal: ~3 hours.**

### During Phase 4 (Observability & packaging)

| ID | Item | Effort | Ties to | Why it matters |
|---|---|---|---|---|
| A15 | Vendor or pin the §3.3 MockBuffer fix in the eval driver. | 1 hour | Gap C2, R2 | Without it, local eval silently misgrades. |
| A16 | Pin the LCB `release_v6` split + `lcb100_hardest_v6.json` id list. | 30 min | Gap (eval) | Without these, "subset of LCB" is meaningless. |
| A17 | Commit to a paired-pass protocol (5 passes, paired t-test, per-pass Δ). | 30 min | Gap C4, R6 | Without it, no future benchmark claim is verifiable. |
| A18 | Implement `infra_fail` exclusion from pass@1 in the grader. | 30 min | Gap C1, R1 | The Phase 1 schema + Phase 3 propagation must be consumed by the grader. |

**Phase 4 subtotal: ~2.5 hours.**

### During Phase 5 (Hardening & polish)

| ID | Item | Effort | Ties to | Why it matters |
|---|---|---|---|---|
| A19 | Specify provider clamp detection logic. | 1 hour | Gap S1, R5 | Without it, mid-run cap shrinkage makes every subsequent call unsatisfiable. |
| A20 | Specify reroute budget and wall-clock caps (or document that `pi-ai` handles retries). | 30 min | Gap S2 | Without it, a flaky provider can hang the loop or inflate cost. |
| A21 | Specify `finish_reason` string normalization across providers. | 30 min | Gap M2, R21 | Cut-off summarizer depends on the string `"length"`. |
| A22 | Specify reasoning capture per provider. | 30 min | Gap (provider), R25 | Transcript won't include reasoning content without it. |
| A23 | Implement `capmatch_q38.py` analog (or document that the local Qwen arm won't be cap-matched). | 2 hours | Gap C3, R11 | Without it, Qwen3.8-27B comparison is not like-for-like. |
| A24 | If parallel workers are added, specify the concurrency-control mechanism. | 1 hour (if needed) | Phase 5 optional | Parallel workers with a shared filesystem ledger require a concurrency-control mechanism. |

**Phase 5 subtotal: ~5 hours (excluding the optional parallel-workers task).**

### Architecture subtotal: ~15 hours ≈ 2 days.

---

## Priority 4 — Evaluation closure (~1 day)

These are the evaluation-specific items that should land before any benchmark claim is made. They are a subset of Priority 3 items, grouped here because they form a coherent evaluation strategy.

| ID | Item | Effort | Ties to | Why it matters |
|---|---|---|---|---|
| E1 | Add a Phase 4 task to vendor or pin the LiveCodeBench `release_v6` hard split + `lcb100_hardest_v6.json` id list. | 30 min | Gap (eval) | Without these, "subset of LCB" is meaningless. (Same as A16.) |
| E2 | Add a Phase 4 task to implement a paired-pass protocol (5 passes, paired t-test). | 30 min | Gap C4, R6 | The paper's headline numbers depend on this. (Same as A17.) |
| E3 | Add a Phase 4 task to compute per-pass Δ (manager − single) per problem, not just aggregate accuracy. | 1 hour | Gap (eval) | The paper's Table 1 reports per-pass Δ. |
| E4 | Add a Phase 5 task to implement cap-match (or document that the local Qwen arm won't be cap-matched). | 2 hours | Gap C3, R11 | Without it, the Qwen3.8-27B comparison is not like-for-like. (Same as A23.) |
| E5 | Add a Phase 4 task to vendor the §3.3 MockBuffer fix and pin it as a dependency of the eval driver. | 1 hour | Gap C2, R2 | Without it, local eval silently misgrades. (Same as A15.) |

**Evaluation subtotal: ~5 hours ≈ 1 day.** (Overlaps with Priority 3; net new effort is the per-pass Δ computation, ~1 hour.)

---

## Priority 5 — Documentation (~1 day)

| ID | Item | Effort | Ties to | Why it matters |
|---|---|---|---|---|
| D1 | Add a "Status: Planning (Phase 0 not started)" line to the README. | 1 min | R9, Gap C6 | The current line is misleading. (Same as P6.) |
| D2 | Add a "Reproducing the paper" section that explicitly says: this repo does not reproduce paper numbers; it ports the scaffold. Phase 4's "minimal benchmark driver" is for sanity, not for paper-comparable results. | 30 min | All evaluation gaps | Forces honesty about scope. |
| D3 | Add a "Known divergences from GVS5H" section listing the 12 gaps from `02-ARCHITECTURE-REVIEW.md` §3. | 30 min | All 12 gaps | Forces honesty about fidelity. (Same as P9.) |
| D4 | Add a "Reference file:line map" appendix showing each plan claim → GVS5H source line. | 1 hour | All 12 gaps | Makes the fidelity claim verifiable. (Same as P10.) |
| D5 | Expand `raw/PAPER.md` to include the §3.1 four-difference list and §3.3 MockBuffer fix description verbatim. | 30 min | R22, Gap M8 | The current extract is the least faithful document in the repo. (Same as P11.) |
| D6 | Add a `CHANGELOG.md` and start committing Phase 0 work in small commits. | 30 min | R23 | Signals liveness and makes the history reviewable. (Same as P5.) |

**Documentation subtotal: ~3 hours.** (Overlaps with Priorities 1 and 2; net new effort is D2, ~30 min.)

---

## Recommended execution order

A single implementer working full-time can close all the gaps in ~12–16 days:

### Day 1: Pre-Phase-0 repo health + Phase 0 (revised)
- Morning (2 hours): P1–P7 (Priority 1: ADR 0002 status, LICENSE, `package.json`, CI, CHANGELOG, status line, "no tools, period" fix).
- Afternoon (1 day): P8–P13 (Priority 2: execute Phase 0 discovery, gap-closure docs, paper extract expansion, pi-subagents pin).

### Days 2–4: Phase 1 (revised) — Core ledger primitives
- 2–3 days including the architecture gaps A1–A6.

### Days 5–6: Phase 2 (revised) — Role prompts & parsing
- 2 days including the architecture gaps A7–A9.

### Days 7–10: Phase 3 (revised) — Manager-worker loop
- 3–4 days including the architecture gaps A10–A14.

### Days 11–13: Phase 4 (revised) — Observability & packaging
- 2–3 days including the evaluation gaps A15–A18.

### Days 14–15: Phase 5 (revised) — Hardening & polish
- 2 days including the architecture gaps A19–A24.

### Day 16: Documentation pass + final review
- D1–D6 (overlaps with earlier days; net new effort is the "Reproducing the paper" section D2, ~30 min).

---

## What to commit first

If only one PR is to be opened today, it should be the Priority 1 repo-health batch (P1–P7). It's ~2 hours of work, it's all trivial, and it removes the most visible problems (no LICENSE, misleading status line, ADR 0002 contradiction, "minimal tools" wording). After that PR merges, the repo is in a state where a Phase 0 (revised) effort can begin without distraction.

If a second PR is to be opened this week, it should be the Priority 2 documentation batch (P8–P13). It's ~1 day of work, it closes the gap between "planning drafted" and "planning complete," and it makes the 12 architectural gaps explicit so that Phase 1 can begin with a known scope.

---

## What NOT to do

- **Do not start Phase 1 implementation before Priority 1 and Priority 2 are done.** Phase 1 without `package.json` (P3) means inventing project structure mid-implementation; Phase 1 without the gap-closure docs (P9, P10) means the 12 architectural gaps stay hidden.
- **Do not skip the §3.3 MockBuffer fix (A15, E5).** It's the single most consequential evaluation gap. A port that misses it can run a "smoke test" but cannot make any paper-comparable accuracy claim.
- **Do not defer the "no tools, period" fix (P7) to Phase 3.** It's an ADR-level fix that should land before any code is written. Phase 3 code written against the "minimal tools" wording will need to be reworked.
- **Do not add parallel workers (A24) before the sequential MVP is working.** ADR 0003 explicitly defers parallelism to a post-MVP extension. Adding it earlier risks diverging from the paper before a working baseline exists.

---

## Implementation priority verdict

The work is well-scoped and the dependencies are clear. The 12 architectural gaps map cleanly to specific phase tasks. The total effort (~12–16 days for one implementer) is dominated by the actual porting work (Phases 1–5), not by the gap-closure overhead (which adds ~3 days across all phases).

The critical path is: **Priority 1 (2 hours) → Priority 2 (1 day) → Phase 1 (revised) → Phase 2 (revised) → Phase 3 (revised) → Phase 4 (revised) → Phase 5 (revised) → documentation pass.** Each phase's revised task list is the original task list plus the architecture gaps assigned to that phase in Priority 3.

After Priority 1 + Priority 2, the repo will have earned the status line "Planning complete in-repo." After Phase 5 (revised) + the documentation pass, the repo will have earned the right to be called an implementation.
