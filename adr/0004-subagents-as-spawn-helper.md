# ADR 0004: pi-subagents as Spawn Helper Only

## Status

Accepted

## Context

Faithfulness to [GVS5H](https://github.com/slee-persis/GVS5H) / [arXiv:2608.26480](https://arxiv.org/abs/2608.26480) is paramount: sequential manager ↔ one worker, fresh context every role call, shared filesystem ledger, sample-test hard override, same model and fixed role prompts, workers as single generations (not multi-turn tool-using coding agents).

Pi already has mature packages for spawning isolated children. Two were compared for Option A (reuse infrastructure without replacing the paper loop):

| Package | Fit for exact replication |
|---------|---------------------------|
| **[nicobailon/pi-subagents](https://github.com/nicobailon/pi-subagents)** | Strong: first-class `context: "fresh"`, sequential parent control, lighter opinions |
| [KristjanPikhof/Pi-Agents-Team](https://github.com/KristjanPikhof/Pi-Agents-Team) (`pi-agents-team`) | Weak for fidelity: parallel teams, role profiles, summary-only parent view, worker reuse |

We still need to implement ledger, paper prompts, parsers, sample-test gate, and the manager state machine ourselves. The open question is only whether to invent process spawn / isolation or reuse an existing helper.

## Decision

1. **pi-zero-shot owns the control flow** — deterministic TypeScript manager loop matching GVS5H v2 (`plan → ideation → manage ↔ worker + sample tests → finalize`).
2. **Optional dependency on [pi-subagents](https://github.com/nicobailon/pi-subagents)** solely as a **spawn helper** for fresh, sequential role calls when that reduces implementation cost.
3. **Do not** use pi-subagents builtin agents (`worker`, `reviewer`, `scout`, …), team/council modes, parallel fan-out, or fork-default context as the paper loop.
4. **Do not** adopt pi-agents-team (or similar team orchestrators) for the replication path.
5. Each paper role launch must satisfy:
   - `context: "fresh"` (or equivalent isolated one-shot)
   - concurrency = 1
   - same model for every role
   - paper system prompt + user message = ledger injection only
   - prefer no / minimal tools so a role remains a generation, not a multi-turn edit agent
6. Sample tests remain an **external subprocess** owned by pi-zero-shot, not a “verifier agent.”
7. If pi-subagents cannot preserve these invariants, fall back to direct `@earendil-works/pi-ai` (or bare `pi --mode rpc` one-shots) without blocking the port.

## Consequences

### Positive

- Fresh-context child management, wait-for-result, and basic observability can be borrowed instead of reimplemented.
- Clear boundary: package = process plumbing; paper semantics stay in this repo.
- Still compatible with a pure `pi-ai` path if the dependency is undesirable or drifts.

### Negative

- Optional peer dependency and version alignment with pi-subagents / Pi.
- Implementers must resist using package defaults that would confound replication (fork context, tool-heavy workers, parallel teams).

### Neutral

- ADR 0001–0003 unchanged: extension not core fork; filesystem ledger preferred; sequential single worker for MVP.

## Alternatives considered

- **pi-agents-team as host** — rejected for exact replication (parallel team model, summary-only transcripts, role specialization).
- **pi-workflows / pi-extensible-workflows as primary loop** — useful graphs, but easy to lose paper isolation and single-worker sequential semantics; not the MVP control plane.
- **No external spawn helper** — valid and still supported; slightly more work for process lifecycle.

## References

- [nicobailon/pi-subagents](https://github.com/nicobailon/pi-subagents) — especially `context: "fresh"` in [docs/tool-reference.md](https://github.com/nicobailon/pi-subagents/blob/main/docs/tool-reference.md)
- [slee-persis/GVS5H `multiagent.py` (v2)](https://github.com/slee-persis/GVS5H/blob/master/codebase/v2-current/escalation/multiagent.py)
- ADR 0001, 0002, 0003
