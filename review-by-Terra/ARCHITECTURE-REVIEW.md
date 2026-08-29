# Architecture review

## Comparison

| Concern | Paper / GVS5H | pi-zero-shot | Required action |
|---|---|---|---|
| Core mechanism | Zero-shot manager-worker control with shared ledger | Planned in ADRs and phases | Preserve bounded delegation and durable state |
| Shared state | Filesystem-mediated coordination | Filesystem ledger ADR | Define an explicit event contract |
| Control loop | Manager plans, dispatches, integrates, stops | Sequential loop ADR | Specify transitions and stop/recovery policy |
| Evaluation | GVS5H has orchestration, benchmark, regrade, data, runs | No source or harness | Build evaluation as a subsystem |

## Target layers

```text
Pi extension -> RunController -> ManagerPolicy -> LedgerStore
                                      -> WorkerExecutor -> ResultValidator
                                      -> Reporter / Evaluator
```

- Extension: registration, resolved configuration, cancellation, rendering.
- Core: types, transitions, budgets, retry policy; testable without Pi or model access.
- Ledger: authoritative immutable events and rebuildable derived state.
- Executor: converts a dispatch packet into raw worker output; cannot mutate state.
- Evaluator: reads retained evidence; cannot change outcomes.

## Workspace

```text
.pi-zero-shot/runs/<run-id>/
  manifest.json  events.jsonl  state.json
  tasks/  results/  raw/  artifacts/  report.json
```

Workers write task-scoped proposals only. A manager holding a lease validates and promotes results. This eliminates stale-worker overwrite and creates a replayable causal trace.

## Gaps

No ledger schema, transition contract, recovery/cancellation semantics, budget model, host adapter seam, or controlled paired evaluation exists yet. The project should optimize for inspectable bounded orchestration, not maximal agent autonomy.
