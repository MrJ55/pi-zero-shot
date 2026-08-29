# ADR recommendations

## ADR-0005 — Event-sourced per-run ledger
Use immutable JSONL events as truth and `state.json` as a rebuildable projection. This supplies recovery, replay, and inspectable evidence.

## ADR-0006 — Framework-independent core
Manager depends on a narrow `WorkerExecutor` port, not Pi APIs. Pi supplies an adapter; offline tests use fakes.

## ADR-0007 — Bounded sequential v0
One manager and one active worker dispatch, with fixed action, worker, retry, context, time, and spend ceilings. Parallelism requires separate evaluation.

## ADR-0008 — Strict worker envelope
Require versioned JSON results and artifact references. Preserve raw output; reject invalid normalized output after one bounded repair.

## ADR-0009 — Evaluation isolation
Use immutable manifests and separate workspaces. Baseline and scaffold must share inputs, model identity, tool policy, caps, task set, and grader revision.

## ADR-0010 — Trace safety
Retain redacted evidence, restrict paths to the run root, and treat worker-produced artifacts as untrusted until validated.
