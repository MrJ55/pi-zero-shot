# Architecture Mapping: GVS5H → Pi

## Paper Primitives → Pi Equivalents

| Paper Concept | Pi Mapping | Notes |
|---------------|------------|-------|
| Shared filesystem workspace | `LedgerWorkspace` (real FS or Pi session-backed virtual FS) | Prefer real FS for fidelity + easy inspection |
| Manager (primary) | Supervisor agent / skill mode | Owns loop and task list |
| Worker (fresh context) | Short-lived agent turn or sub-agent with isolated context | Must not inherit long history |
| `plan.md` / `notes.md` / `solution.py` | Files in ledger + optional Pi session artifacts | Hard size bounds required |
| `transcript.jsonl` | Structured log + Pi session events | Capture reasoning / tokens / finish_reason |
| Sample-test verifier | Tool or subprocess called by manager | Hard override on “done” |
| Single model, zero-shot | Any model via `@earendil-works/pi-ai` | No training, no per-benchmark tuning |
| Env-driven config | Extension config / skill options | Mirror key paper knobs (`MAX_ITERS`, etc.) |

## Recommended Extension Shape

- **Name**: `pi-zero-shot` or `ledger-orchestrator` skill/extension
- **Activation**: slash command (`/ledger`, `/self-orchestrate`) or mode switch
- **Core loop**: sequential manager → one worker → sample tests → manager (paper style)
- **Observability**: ledger files visible in TUI / session viewer; full transcript retained
- **Baseline**: single-shot mode for fair comparison

## Non-Goals (MVP)

- Changing Pi core agent loop
- Training or learned orchestrators
- Full multi-agent debate / MoA style aggregation
- Replacing Pi’s existing tools (Read/Write/Edit/Bash)

## Open Questions

1. Real filesystem vs. pure session-tree virtual ledger?
2. How tightly to integrate with existing community multi-agent packages?
3. Should workers be true Pi sub-agents or pure prompt calls with ledger injection?
