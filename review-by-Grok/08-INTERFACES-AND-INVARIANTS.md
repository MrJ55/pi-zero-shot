# 08 — Interfaces and Invariants

## Hard invariants a faithful port must preserve

1. **Worker = single generation**  
   Zero tools. Fresh context. Same model as manager. Paper system prompt + ledger injection only.

2. **Sample-test hard override**  
   If public samples fail, manager “done” is overridden to “continue”.

3. **Notes rewrite, not append**  
   Worker returns a complete replacement; cut-off digests never enter notes.md; hard character bound.

4. **Finalize skip**  
   If primary already marked done and a usable artifact exists, do not run finalize.

5. **infra_fail exclusion**  
   Empty final artifact + any infra_exhausted in the transcript → exclude from pass@1.

6. **Clean-slate workspace**  
   Every problem starts with empty plan/notes/solution/answer/transcript/tasks.

7. **Bounded plan**  
   plan.md truncated on write (GVS5H uses ~4 k chars).

8. **No-progress guard**  
   Identical task re-issued → abort loop.

9. **MAX_TASKS**  
   Live task list hard-capped (default 12).

10. **ANS_RE / non-empty guard**  
    Do not overwrite a good prior answer with a rambling or empty response.

## Suggested TypeScript shapes (illustrative)

```ts
interface TranscriptRecord {
  t: number;
  role: string;
  request: unknown;
  response: string;
  finish_reason?: string;
  infra_exhausted?: boolean;
  // ...
}

interface StatusOut {
  ws: string;
  finish_reason?: string;
  truncated_calls: number;
  n_calls: number;
  infra_fail?: boolean;
}
```

These invariants are the difference between “looks like the paper” and “reproduces the paper’s measured behaviour”.
