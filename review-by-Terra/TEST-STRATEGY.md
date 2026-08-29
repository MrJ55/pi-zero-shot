# Test strategy

| Layer | Validate |
|---|---|
| Unit/schema | records, transition guards, budget math, projection replay |
| Ledger integration | atomic writes, conflicts, stale lease, restart |
| Manager integration | plan/dispatch/collect/integrate, repair, exhaustion |
| Executor contract | cancellation, correlation, usage, raw capture |
| Extension smoke | config, workspace, lifecycle, report |
| Evaluation checks | matching manifests, inputs, grader, no hidden memory/retry |

## Required fault injection

- Stop after raw worker response but before promotion: recovery ingests once.
- Malformed worker output: retain raw response, bounded repair, typed failure.
- Duplicate callback: idempotent ingestion.
- Lease expiry: no old-holder promotion.
- Budget excess: deny before external work.
- Cancellation: propagate abort and record terminal state.
- Path traversal artifact: reject before filesystem escape.

Every test should assert event sequence or rebuilt projection, not only text output. CI should run typecheck, schemas, unit/integration suites, secret/path checks, and the deterministic smoke slice; live-provider tests remain opt-in.
