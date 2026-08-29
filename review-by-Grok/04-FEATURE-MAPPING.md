# 04 — Feature Mapping (pi-zero-shot plan vs GVS5H v2)

| Feature / Invariant | GVS5H source | Plan status | Notes |
|---------------------|--------------|-------------|-------|
| Sequential manager ↔ single worker | multiagent.py loop | ✅ Planned | ADR 0003 |
| Fresh context every role call | every `_chat` | ✅ Planned | ADR 0004 |
| Shared filesystem ledger | WS_ROOT + _read/_write | ✅ Planned | ADR 0002 |
| plan.md bounded on write | MAX_PLAN_CHARS | ⚠ Partial | Bound mentioned in spirit, not numeric |
| notes.md rewrite (not append) | _worker NOTES handling | ⚠ Partial | “rewrite” mentioned; hard bounds + cut-off exclusion missing |
| Ideation code stripping | _strip_code | ❌ Missing | Critical to prevent manager treating ideation as solved |
| Sample-test hard override of “done” | after _run_samples | ✅ Planned | Good |
| Finalize skip when already done + usable artifact | multiagent_solve end | ❌ Missing | Prevents destroying good intermediate answers |
| infra_exhausted / infra_fail | _record + status_out | ❌ Missing | Evaluation hygiene |
| MAX_TASKS = 12 | multiagent.py | ❌ Missing | Unbounded task list risk |
| STRICT_FORMAT auto | _strict() | ❌ Missing | Needed for certain models |
| No-progress guard (identical task) | loop | ❌ Missing | Cost control |
| Cut-off digest only to manager | _summarize_cutoff | ❌ Missing | Notes-size control |
| ANS_RE non-empty guard | answer.md write | ❌ Missing | Answer protection |
| Zero tools on workers | pure chat | ⚠ Weak | “prefer minimal” → must be “none” |
| Paired-pass evaluation | paper + runs/ | ❌ Missing | Statistical claims |
| MockBuffer / readline fix | testing_util.py | ❌ Missing | Evaluator correctness |
| capmatch_q38 | capmatch_q38.py | ❌ Missing | Like-for-like comparison |

Legend: ✅ fully captured · ⚠ partially captured · ❌ absent
