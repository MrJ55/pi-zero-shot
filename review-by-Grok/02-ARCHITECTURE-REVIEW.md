# 02 — Architecture Review

## Target control flow (pi-zero-shot plan)

From README and `docs/architecture.md`:

```
User task
  → Manager writes plan.md + seed tasks
  → Ideation worker → notes.md
  → Loop: Manager curates → Worker (fresh context) → sample tests → Manager
  → Finalize (if needed)
```

Ledger = real filesystem workspace. Manager = deterministic TS state machine. Worker = fresh one-shot (optional pi-subagents spawn helper).

## Reference control flow (GVS5H multiagent.py)

Exact order implemented in `multiagent_solve`:

1. Clean-slate workspace reset (all artifacts cleared).
2. `_primary_plan` → plan.md (bounded) + initial tasks.
3. `_ideation_worker` → notes (code stripped) + proposals.
4. `_primary_manage` folds ideation.
5. Loop (≤ MAX_ITERS): worker → sample tests (hard override on “done”) → primary_manage.
6. Finalize only if not already done with usable artifact.
7. infra_exhausted / infra_fail flagging for empty results after provider exhaustion.

Additional invariants present in source but only partially or not at all in the plan:

- Notes are **rewritten**, never appended (with hard char bounds).
- Cut-off digests go only to manager summary, never into notes.md.
- ANS_RE non-empty guard before overwriting answer.md.
- No-progress guard (identical task re-issue aborts).
- STRICT_FORMAT auto-detection for certain model names.
- MAX_TASKS = 12 hard cap.
- Sample-test hard override of manager “done”.
- Finalize skip when primary already marked done with usable answer.
- infra_exhausted recorded on every call and used to set infra_fail.

## Gap summary

The high-level diagram matches. The plan correctly rejects parallel teams and package default roles. The missing pieces are the low-level protective invariants that make the measured results possible and the evaluation honest. These must be added to Phase 1 (ledger/transcript schema), Phase 2 (parsers + STRICT_FORMAT), Phase 3 (loop + hard gates), and Phase 4 (eval protocol) before any claim of fidelity is tenable.
