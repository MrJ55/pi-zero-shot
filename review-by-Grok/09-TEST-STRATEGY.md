# 09 — Test Strategy

## Levels

1. **Unit** — parsers (sections, bullets, tasks, code extraction, STRICT_FORMAT), size bounds, ANS_RE guard, clean-slate reset.
2. **Loop invariants** — sample-test hard override, finalize-skip, no-progress guard, MAX_TASKS, zero-tool assertion on role launches.
3. **Transcript / infra** — infra_exhausted propagation and infra_fail exclusion from pass@1.
4. **Fidelity / offline** — deterministic vertical slice with fake workers that exercise the full manager state machine against recorded fixtures.
5. **Evaluation protocol** — 5 paired passes (manager vs single-shot), paired t-test, per-pass Δ reported; MockBuffer/readline fix vendored; LCB hardest-id list pinned; cap-match applied when comparing Qwen3.8 arms.
6. **Regression** — any change that re-introduces tools on workers, append-only notes, or always-on finalize must fail CI.

## Minimum viable evaluation gate
Before any public claim of “we reproduce GVS5H results”:
- infra_fail rows excluded,
- evaluator contains the §3.3 fix,
- statistical protocol matches the paper (5 paired passes),
- single-shot baseline uses the identical model and token cap.

## Exit criterion for Phase 4
A green run of the paired-pass harness on a small held-out set with the above guards active.
