# Architecture Mapping: GVS5H → Pi

Upstream method and measured results: **[slee-persis/GVS5H](https://github.com/slee-persis/GVS5H)** · [arXiv:2608.26480](https://arxiv.org/abs/2608.26480) · extract in [`../raw/PAPER.md`](../raw/PAPER.md).

Reference implementation of the loop: [`multiagent.py` (v2)](https://github.com/slee-persis/GVS5H/blob/master/codebase/v2-current/escalation/multiagent.py).

## Paper Primitives → Pi Equivalents

| Paper Concept | Pi Mapping | Notes |
|---------------|------------|-------|
| Shared filesystem workspace | `LedgerWorkspace` (real FS or Pi session-backed virtual FS) | Prefer real FS for fidelity + easy inspection (ADR 0002) |
| Manager (primary) | Supervisor in extension/skill mode | Owns loop and task list |
| Worker (fresh context) | Short-lived agent turn or isolated sub-call | Must not inherit long Pi session history |
| `plan.md` / `notes.md` / `solution.py` | Files in ledger + optional Pi session artifacts | Hard size bounds required |
| `transcript.jsonl` | Structured log + optional Pi session events | Capture reasoning / tokens / finish_reason |
| Sample-test verifier | Tool or subprocess invoked by manager | Hard override on “done” |
| Single model, zero-shot | Any model via `@earendil-works/pi-ai` | No training, no per-benchmark tuning |
| Env-driven config | Extension config / skill options | Mirror key paper knobs (`MAX_ITERS`, etc.) |

## Recommended Extension Shape

- **Name**: `pi-zero-shot` / ledger-orchestrator skill
- **Activation**: slash command (`/ledger`, `/self-orchestrate`) or explicit mode
- **Core loop**: sequential manager → one worker → sample tests → manager (paper style; GVS5H v2)
- **Observability**: ledger files visible; full transcript retained
- **Baseline**: single-shot mode for fair comparison

## Control flow (v2 paper / GVS5H `multiagent_solve`)

1. Manager writes `plan.md` + seed tasks  
2. Ideation worker proposes approaches into `notes.md` (no code)  
3. Loop: manager curates tasks + picks one next task → worker executes → sample tests → manager reviews  
4. Stop on `done` (with non-empty artifact and passing samples when applicable) or max iters  
5. Finalize worker if needed  

## Non-Goals (MVP)

- Changing Pi core agent loop  
- Training or learned orchestrators  
- Full multi-agent debate / MoA  
- Replacing Pi’s Read/Write/Edit/Bash tools  

## Open Questions

1. Real filesystem vs pure session-tree virtual ledger? → see ADR 0002  
2. Workers as pure prompt calls vs full Pi sub-agents?  
3. How much to integrate with existing community multi-agent packages?  
