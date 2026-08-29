# pi-zero-shot

**Zero-Shot Self-Orchestration with Ledger-Based Control** for the [earendil-works/pi](https://github.com/earendil-works/pi) agent harness.

Port of the manager–worker scaffold from:

> **Zero-Shot Self-Orchestration with Ledger-Based Control for Improved LLM Coding Performance**  
> arXiv: [2608.26480](https://arxiv.org/abs/2608.26480)  
> Official artifacts: **[slee-persis/GVS5H](https://github.com/slee-persis/GVS5H)**  
> Local paper extract: [`raw/PAPER.md`](./raw/PAPER.md)

to Pi’s extensible architecture (extension / skill), preserving the training-free, zero-shot, shared-filesystem-ledger design.

Target repo: `https://github.com/MrJ55/pi-zero-shot`

---

## Problems this project addresses

1. **Confounded multi-agent gains** — Most multi-agent coding systems change prompts, tools, token budgets and orchestration at once; it is hard to isolate what actually helps.
2. **Context pressure / truncation** — Single long generations on hard coding problems frequently hit caps or lose state; the paper shows a manager–worker ledger reduces empty/truncated solutions.
3. **No training-free, inspectable scaffold on Pi** — Pi is deliberately minimal; users lack a ready-made, paper-validated zero-shot orchestration pattern that stays outside the core.
4. **Cost vs accuracy trade-off** — The paper shows a cheaper model + manager can approach a much more expensive single-call frontier model; Pi users need that pattern as an opt-in extension.

## Goals

| Goal | Success signal |
|------|----------------|
| **G1** Faithful control flow | Sequential manager ↔ one worker, sample-test gate, finalize, same invariants as [GVS5H](https://github.com/slee-persis/GVS5H) v2 |
| **G2** Short worker contexts | Workers see only ledger state (plan/notes/solution/task), not full Pi session history |
| **G3** Inspectable ledger | `task.md`, `plan.md`, `notes.md`, `solution.py`, `tasks.json`, `transcript.jsonl` produced and visible |
| **G4** Extension, not core fork | Ships as Pi extension/skill; classic Pi remains available |
| **G5** Single-shot baseline | A/B comparison against plain single-call remains easy |
| **G6** Provider-agnostic | Uses `@earendil-works/pi-ai`; no hard dependency on one vendor |

## Non-goals (near term)

- Changing Pi core agent loop  
- Learned / trained orchestrators  
- Full multi-agent debate or Mixture-of-Agents  
- Claiming exact paper numbers without re-running under controlled conditions  

## Architecture (one picture)

```text
User coding task
    |
    ▼
Manager (plan) ──► plan.md + seed tasks
    |
    ▼
Ideation worker ──► notes.md (approaches only)
    |
    ▼
┌─ Manager manage ◄── sample-test verdict ──────────────┐
│         │                                              │
│         ▼                                              │
│   Worker (fresh context) ──► solution.py + notes.md    │
│         │                                              │
│         └────────────── loop until done / max iters ───┘
    |
    ▼
Finalize (if needed) ──► graded artifact + transcript.jsonl
```

- **Ledger** = shared filesystem workspace (content-hash / session keyed)  
- **Manager** = owns task list and stop decision  
- **Worker** = one short-context execution per round  
- **Pi** = harness, providers, TUI, extension host  

Control flow matches [GVS5H `multiagent.py` (v2)](https://github.com/slee-persis/GVS5H/blob/master/codebase/v2-current/escalation/multiagent.py).

## Repository layout

```text
pi-zero-shot/
├── README.md                 ← you are here
├── docs/                     ← background & architecture
├── adr/                      ← architecture decision records
├── plan/                     ← phased implementation (task lists for implementers)
├── raw/                      ← paper extract + links to GVS5H / arXiv
├── src/                      ← extension code (to be built)
└── scripts/                  ← helpers / launchers
```

## Phased plan (summary)

| Phase | Name | Outcome |
|-------|------|---------|
| 0 | Discovery & mapping | Paper ↔ Pi primitives mapped; persistence decision recorded |
| 1 | Core ledger primitives | `LedgerWorkspace`, transcript, sample-test runner |
| 2 | Role prompts & parsing | Ported prompts + robust section parsers |
| 3 | Manager–worker loop | Sequential scaffold as Pi extension/skill |
| 4 | Observability & packaging | TUI visibility, cost metrics, installable package |
| 5 | Hardening | Provider quirks, format drift, optional parallelism |

Detailed task lists: **[plan/](./plan/)**.

## Key ADRs

- [ADR 0001](./adr/0001-use-extension-not-core-fork.md) — Extension / skill, not core fork  
- [ADR 0002](./adr/0002-filesystem-ledger.md) — Prefer real filesystem ledger  
- [ADR 0003](./adr/0003-sequential-manager-worker.md) — Sequential manager + single worker for MVP  

## Upstream references

| Project | Role |
|---------|------|
| **[slee-persis/GVS5H](https://github.com/slee-persis/GVS5H)** | Paper TeX/PDF, v1/v2 scaffolds, full `runs/` transcripts |
| [arXiv:2608.26480](https://arxiv.org/abs/2608.26480) | Published paper |
| [earendil-works/pi](https://github.com/earendil-works/pi) | Agent harness, extensions, `pi-ai` |

## Status

Planning complete in-repo. Implementation follows `plan/phase-*.md` in order.

## License

TBD (recommended: MIT for this port’s code, consistent with Pi where compatible). Paper content remains under the authors’ arXiv license (CC BY 4.0); see [GVS5H](https://github.com/slee-persis/GVS5H) and arXiv.
