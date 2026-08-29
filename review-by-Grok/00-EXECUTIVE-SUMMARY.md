# Review-by-Grok — Executive Summary

**Reviewer:** Grok (xAI), independent audit driven by FSM orchestrator  
**Date:** 2026-08-29  
**Scope:** Full audit of `MrJ55/pi-zero-shot` @ `bd63bf9562a92274c8c10f4616df240a7970bd4a` against arXiv:2608.26480 and reference implementation `slee-persis/GVS5H` @ `6d7a143bd4e4c4343179b4386fc0d906ae9af118`  
**Method:** GitHub connector tree + file fetches for all three sources. First-hand reading of every planning/ADR/phase document in pi-zero-shot; full read of GVS5H `multiagent.py` (control flow, invariants, sample-test gate, infra_exhausted, notes rewrite, finalize skip, etc.). No other `review-*` folders consulted.

---

## Verdict

`pi-zero-shot` is a **strong, well-reasoned planning repository** that correctly targets GVS5H v2 sequential manager–worker + shared filesystem ledger semantics as a Pi extension. The ADRs (especially 0001, 0003, 0004) show clear understanding of the fidelity risks of adopting heavier multi-agent packages.  

However it is **zero-execution**: `src/extension/` contains only `.gitkeep`. Phase 0 exit criteria are unchecked, `VERIFY-LOG.md` is empty, and several high-impact invariants present in `multiagent.py` are not yet captured in the plan (infra_exhausted / infra_fail, strict “no tools period” on workers, paired-pass evaluation protocol, MockBuffer / readline fix, cap-match for Qwen3.8, finalize-skip optimization, notes rewrite bounds, etc.).  

The plan is a good foundation; an implementer who follows only the current documents will silently lose several of the paper’s measured advantages and evaluation hygiene.

---

## Critical Fidelity Gaps (must fix before claiming reproduction)

| # | Gap | Evidence | Impact |
|---|-----|----------|--------|
| C1 | No `infra_exhausted` / `infra_fail` handling | GVS5H `multiagent.py` records `infra_exhausted` on provider exhaustion and sets `status_out["infra_fail"]` so empty results are excluded from pass@1 | Provider outages scored as model failures; evaluation claims become unverifiable |
| C2 | “Prefer no / minimal tools” (ADR 0004 §5) is weaker than the paper | GVS5H workers are pure chat completions with **zero** tools | Any tool surface turns the worker into a multi-turn agent and breaks the measured “single generation” invariant |
| C3 | No paired-pass / statistical protocol | Paper reports 5 paired passes + paired t-test + per-pass Δ | Single-pass comparisons cannot support the paper’s significance claims |
| C4 | No MockBuffer / `readline()` fix or LiveCodeBench evaluator pinning | GVS5H documents the §3.3 fix as required for every reported number | Local eval silently misgrades multi-line stdin solutions |
| C5 | No `capmatch_q38.py` analog | Present in GVS5H escalation/ | Qwen3.8 single-arm comparison is not like-for-like |
| C6 | Status line “Planning complete” is inaccurate | `plan/VERIFY-LOG.md` empty; Phase 0 checkboxes unchecked; ADR 0002 still Proposed | Misleading for contributors and future reviewers |

---

## What’s Done Well

- Correct target: GVS5H v2 control flow (plan → ideation → manage ↔ worker + sample tests → finalize).
- ADR discipline is high; 0004’s explicit “do not use” list for package defaults is excellent.
- Architecture mapping in `docs/architecture.md` is faithful in spirit.
- Clear non-goals (no core fork, no claiming paper numbers without re-runs).
- Optional pi-subagents scoped strictly as spawn helper.

---

## Top 5 Recommendations

1. **Harden worker invariant** — Change ADR 0004 §5 and Phase 3 language from “prefer no / minimal tools” to “no tools, period”. Add a Phase 3 test that fails if any tool is exposed to a role call.
2. **Add infra_fail to transcript schema + grader** (Phase 1 + Phase 4). Propagate the flag exactly as GVS5H does.
3. **Vendor / pin the §3.3 MockBuffer fix** and the LCB hardest-id list in the Phase 4 evaluation driver.
4. **Commit to paired-pass protocol** in Phase 4 (5 passes, paired t-test, per-pass Δ reported).
5. **Fix status messaging** — Change README status line to “Planning drafted; Phase 0 not yet started” and mark ADR 0002 Accepted (or keep Proposed and remove the contradictory Decision text).

---

## Numerical Scorecard

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Plan quality | 7.5/10 | Clear ADRs, correct high-level control flow, good non-goals |
| Implementation readiness | 0/10 | Zero source code under `src/` |
| Paper / GVS5H fidelity | 5.5/10 | Right target, missing several measured invariants and eval hygiene |
| Public-repo hygiene | 3/10 | No LICENSE, empty VERIFY-LOG, misleading status line |
| **Overall** | **4.5/10** | Excellent planning foundation that has not yet started executing |

---

## Document Index

| File | Contents |
|------|----------|
| 00-EXECUTIVE-SUMMARY.md | This document |
| 01-SOURCE-AUDIT.md | Inventory of all three sources |
| 02-ARCHITECTURE-REVIEW.md | Control-flow comparison + gap analysis |
| 03-ADR-CRITIQUE.md | Per-ADR strengths and required amendments |
| 04-FEATURE-MAPPING.md | Feature-by-feature status vs GVS5H |
| 05-ROADMAP-AND-EXECUTION-CRITIQUE.md | Phase exit-criteria status |
| 06-RISK-REGISTER.md | Ranked risks with mitigations |
| 07-IMPLEMENTATION-PRIORITY.md | Critical path and effort order |
| 08-INTERFACES-AND-INVARIANTS.md | Hard invariants a faithful port must keep |
| 09-TEST-STRATEGY.md | Unit, fidelity, and statistical protocol |

*Generated under FSM orchestrator control. Independent of all other review-* folders.*
