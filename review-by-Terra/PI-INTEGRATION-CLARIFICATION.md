# Pi integration clarification

## Boundary

```text
Core ManagerPolicy -> WorkerExecutor <- PiSubagentExecutor
```

The Pi extension owns command registration, configuration, subagent invocation, cancellation wiring, and host usage extraction. Core owns task packets, ledger transitions, validation, budgets, and policy. Core must not import Pi types or depend on internal Pi conversation state.

## Adapter obligations

- Carry stable run/task/attempt/correlation identifiers.
- Send only the persisted, bounded dispatch packet and declared tool policy.
- Return raw output, trace refs, timing, host model metadata, and available usage.
- Propagate cancellation.
- Never mutate ledger files directly.
- Record missing usage/cancellation capability honestly; exclude unknown cost data from comparisons.

## v0 constraints

One worker invocation per manager dispatch; workers cannot spawn workers. Snapshot resolved config into the run manifest. Display stable run id, state, active task, budget consumption, and report path. Keep all host calls inside `src/extension` and cover the adapter with the same contract tests as the fake executor.
