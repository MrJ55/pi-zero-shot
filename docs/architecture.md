# Architecture Mapping: GVS5H → Pi

Upstream method and measured results: **[slee-persis/GVS5H](https://github.com/slee-persis/GVS5H)** · [arXiv:2608.26480](https://arxiv.org/abs/2608.26480) · extract in [`../raw/PAPER.md`](../raw/PAPER.md).

Reference implementation of the loop: [`multiagent.py` (v2)](https://github.com/slee-persis/GVS5H/blob/master/codebase/v2-current/escalation/multiagent.py).

Optional spawn helper: **[nicobailon/pi-subagents](https://github.com/nicobailon/pi-subagents)** — see [ADR 0004](../adr/0004-subagents-as-spawn-helper.md).

## Paper Primitives → Pi Equivalents

| Paper Concept | Pi Mapping | Notes |
|---------------|------------|-------|
| Shared filesystem workspace | `LedgerWorkspace` (real FS preferred) | ADR 0002 |
| Manager (primary) | **Deterministic** supervisor in pi-zero-shot (TS state machine) | Not an LLM “team coordinator” package |
| Worker / role call (fresh context) | Fresh one-shot via **pi-subagents** (`context: "fresh"`) or direct `pi-ai` / RPC | Sequential, concurrency 1; ADR 0004 |
| `plan.md` / `notes.md` / `solution.py` | Files in ledger; harness writes after parse | Hard size bounds; notes **rewrite** |
| `transcript.jsonl` | Owned by pi-zero-shot (full role calls) | Do not rely on summary-only team packages |
| Sample-test verifier | Subprocess in pi-zero-shot | Hard override on false “done” |
| Single model, zero-shot | Same model id for every role via `pi-ai` | No specialized role models |
| Env-driven config | Extension config / skill options | Mirror `MAX_ITERS`, caps, strict format |

## Control plane vs spawn helper

```text
pi-zero-shot (this repo)
  ├─ LedgerWorkspace, transcript, sample-test gate
  ├─ Paper role prompts + parsers
  ├─ Manager state machine (GVS5H v2 order)
  └─ RoleLauncher
        ├─ preferred: pi-subagents fresh sequential spawn
        └─ fallback: pi-ai or pi --mode rpc one-shot
```

**In scope for pi-subagents:** process isolation, `context: "fresh"`, wait for child result, optional observability hooks.

**Out of scope (do not use for replication):** builtin `worker`/`reviewer`/`scout` agents, council/parallel review loops, fork-default context, multi-worker teams, summary-only parent synthesis ([pi-agents-team](https://github.com/KristjanPikhof/Pi-Agents-Team) and similar).

## Recommended Extension Shape

- **Name**: `pi-zero-shot` / ledger-orchestrator skill
- **Activation**: slash command (`/ledger`, `/self-orchestrate`) or explicit mode
- **Core loop**: sequential manager → one worker → sample tests → manager (GVS5H v2)
- **Role children**: paper prompts; ledger injection only; minimal/no tools when possible
- **Observability**: ledger files + full `transcript.jsonl`
- **Baseline**: single-shot mode for fair comparison

## Control flow (v2 paper / GVS5H `multiagent_solve`)

1. Manager writes `plan.md` + seed tasks  
2. Ideation worker proposes approaches into `notes.md` (no code)  
3. Loop: manager curates tasks + picks one next task → worker executes → sample tests → manager reviews  
4. Stop on `done` (non-empty artifact; samples pass when applicable) or max iters  
5. Finalize worker if needed  

## Non-Goals (MVP)

- Changing Pi core agent loop  
- Training or learned orchestrators  
- Full multi-agent debate / MoA / parallel specialist teams as the measured path  
- Replacing Pi’s default tools for ordinary interactive use  

## Resolved design choices

1. **Ledger:** prefer real filesystem (ADR 0002; finalize status in Phase 0).  
2. **Workers:** fresh role calls (generation-shaped), not package default coding subagents (ADR 0004).  
3. **Community packages:** pi-subagents optional spawn helper only; pi-agents-team not on the replication path.  
