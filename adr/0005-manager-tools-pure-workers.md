# ADR 0005: Manager-Only Tools + Pure Codegen Workers

## Status

Accepted (product path)

## Context

The original GVS5H paper uses **same-model, tool-free roles** over a ledger for LiveCodeBench-style single-artifact coding. For **real repo development** on Pi, the goal is not exact paper replication but applying the concept so smaller/local models can approach stronger single-agent performance.

Proposed product shape:

- **Manager** (stronger / cloud model): only agent with repo tools (read, edit, bash, tests).
- **Workers** (smaller / local / cheaper models): pure generation — emit code text from a tight brief; no tools.
- Manager decomposes into small units, places pieces, runs gates, re-tasks on failure.
- Optional parallel workers on **independent** units after interfaces are fixed.

[pi-subagents](https://github.com/nicobailon/pi-subagents) supports `noTools: true`, per-agent `model`, and fresh context — the preferred spawn path (ADR 0004).

## Decision

1. **Product default:** manager-only tools; workers are generation-shaped (`noTools: true` or equivalent).
2. **Models:** allow asymmetric setup (stronger manager, cheaper/local workers). Same-model remains valid for ablations.
3. **Integration ownership:** manager writes files and runs verify; workers never claim to have edited the tree.
4. **Parallelism:** optional, dependency-aware; only when the manager marks units independent.
5. **Paper-faithful arm (optional):** same model, sequential, ledger-heavy — still supported for research comparison, not the primary product path.

## Consequences

### Positive

- Small models get micro-contexts instead of full agent loops.
- Safe fan-out (no concurrent file writers).
- Aligns with GVS5H workers while enabling real repos via a toolful manager.
- Fits Pi + pi-subagents without forking Pi core.

### Negative

- Manager is a bottleneck and must be good at contracts + integration.
- Under-specified briefs cause conflicting APIs; need strict brief templates.
- Pure zero-tool spawn must be verified per pi-subagents version.

### Neutral

- ADR 0001–0004 still apply for extension vs fork, ledger preference, sequential MVP, and spawn-helper scope.

## References

- [GVS5H](https://github.com/slee-persis/GVS5H) / [arXiv:2608.26480](https://arxiv.org/abs/2608.26480)
- [nicobailon/pi-subagents](https://github.com/nicobailon/pi-subagents) (`noTools`, `model`, fresh context)
- Related: ManagerWorker (arXiv:2603.26458) — strong/weak asymmetry with **inverted** tools; we deliberately invert relative to that paper for product use
- Smoke test: [`experiments/smoke-test/`](../experiments/smoke-test/)
