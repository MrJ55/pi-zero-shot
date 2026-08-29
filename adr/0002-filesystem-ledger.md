# ADR 0002: Prefer Real Filesystem Ledger

## Status

Proposed

## Context

The paper’s gains are attributed in large part to the shared filesystem workspace that keeps each worker’s context short while preserving state across turns (plan, notes, solution, task list).

Pi already has sophisticated session trees, branching, and compaction.

## Decision

Prefer a **real filesystem workspace** (content-hash or session-id keyed directory) as the primary ledger implementation for fidelity to the paper and easy human/tool inspection. Optionally layer Pi session artifacts on top for TUI integration.

## Consequences

- Positive: closest match to measured paper behavior; easy to debug and to compare against GVS5H transcripts.
- Positive: workers can be given a clean, bounded view of state.
- Negative: must manage cleanup, isolation, and multi-user/multi-session safety.
- Negative: pure “everything-in-session” purity is sacrificed.

## Alternatives Considered

- Pure virtual ledger inside Pi session tree only → better native integration but drifts from the paper’s measured mechanism and makes external inspection harder.
