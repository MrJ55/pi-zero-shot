# ADR 0003: Sequential Manager + Single Worker (Paper Style)

## Status

Accepted for MVP

## Context

The paper’s scaffold is deliberately sequential: the manager picks *one* next task, a fresh worker executes it, sample tests run, then the manager re-curates. Parallelism is not part of the measured design.

Pi has emerging async / multi-worker patterns (e.g. pi-kot style).

## Decision

MVP implements the **exact sequential control flow** of the paper (manager ↔ one worker at a time, up to `MAX_ITERS`). Parallel or async fan-out is a later, optional extension.

## Consequences

- Positive: faithful reproduction of the published method and results.
- Positive: simpler correctness (no concurrent ledger writes).
- Negative: does not immediately exploit Pi’s parallel worker capabilities.

## Alternatives Considered

- Jump straight to parallel workers → risks diverging from the paper before we have a working baseline.
