# Execution roadmap

## P0: contracts and offline proof

- Define JSON Schemas and typed records; reject illegal transitions.
- Implement append-only `LedgerStore`, revisions, lease, projection, and recovery.
- Implement scripted fake executor for success, malformed output, timeout, cancellation, duplicate callback.
- Implement manager state machine with event-sequence tests.

## P1: vertical slice and Pi seam

- Register extension command; create per-run workspace from resolved config.
- Run a two-task fixture: plan, dispatch, validate, integrate, verify, report.
- Emit JSONL trace and terminal report with manifest, outcomes, budgets, usage, artifacts.
- Implement Pi-subagent `WorkerExecutor` adapter and shared contract tests.

## P2: reliability

Add cancellation, restart, stale lease, artifact validation, context limits, budget accounting, redaction, workspace containment, documentation, and smoke command.

## P3: evaluation

Add frozen manifests, paired baseline/scaffold runner, common grading/regrading, retained evidence, and per-task outcome/cost/latency reporting.

## Release gate

A user can execute, cancel, resume, replay, and inspect a bounded run with an offline deterministic test suite.
