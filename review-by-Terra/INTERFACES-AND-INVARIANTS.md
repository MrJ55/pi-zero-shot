# Interfaces and invariants

## Records

Version all boundary records: `RunManifest`, `Task`, `LedgerEvent`, `WorkerResult`, `Decision`, and `Budget`. Include run/entity ids, UTC timestamp, producer, schema version, correlation id, and artifact references.

## State machine

```text
INIT -> PLAN -> DISPATCH -> COLLECT -> INTEGRATE -> VERIFY
VERIFY -> DONE | PLAN | FAILED
non-terminal -> CANCELLED
```

Only the manager may transition state, and only with the current ledger lease/revision. Workers propose results; they never set terminal state.

## Ports

```ts
interface LedgerStore { append(expectedRevision:number,event:LedgerEvent):Promise<number>; read(runId:string):Promise<Run>; recover(runId:string):Promise<Run>; }
interface WorkerExecutor { execute(packet:DispatchPacket, signal:AbortSignal):Promise<RawWorkerResponse>; }
interface ResultValidator { normalize(raw:RawWorkerResponse, task:Task):ValidationResult<WorkerResult>; }
```

## Invariants

1. Events are append-only; corrections are compensating events.
2. Appends use expected revision; conflicts are never overwritten.
3. Manager lease is required for integration and finalization.
4. Worker write scope is restricted to its task.
5. Dispatch/callback/recovery are idempotent by correlation key.
6. Preserve raw output separately from validated normalized result.
7. Reserve budget before a dispatch or repair.
8. Every final artifact traces to tasks, results, decisions, revisions, and manifest.
9. Dispatch packets declare all provided context.
10. Terminal states are immutable.

Malformed output is preserved and emits `RESULT_REJECTED`; allow one bounded repair then fail the task. Restart rebuilds from events and reconciles in-flight tasks by idempotency key.
