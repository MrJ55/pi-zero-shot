# pi-zero-shot

**Zero-Shot Self-Orchestration with Ledger-Based Control** for the [earendil-works/pi](https://github.com/earendil-works/pi) agent harness.

Inspired by:

> **Zero-Shot Self-Orchestration with Ledger-Based Control for Improved LLM Coding Performance**  
> arXiv: [2608.26480](https://arxiv.org/abs/2608.26480)  
> Official artifacts: **[slee-persis/GVS5H](https://github.com/slee-persis/GVS5H)**  
> Local paper extract: [`raw/PAPER.md`](./raw/PAPER.md)

**Product goal:** apply the ledger / manager–worker concept to **real repo development** on Pi so smaller or local models can approach stronger single-agent performance — not only reproduce paper tables.

**Preferred product shape ([ADR 0005](./adr/0005-manager-tools-pure-workers.md)):**

- Manager (stronger model) — **only** role with repo tools  
- Workers (cheaper / local) — **pure codegen**, no tools (`noTools` via [pi-subagents](https://github.com/nicobailon/pi-subagents))  
- Manager places code, runs gates, re-curates tasks; optional parallel independent units  

Quick experiment: **[experiments/smoke-test/](./experiments/smoke-test/)**.

Target repo: `https://github.com/MrJ55/pi-zero-shot`

---

## Problems this project addresses

1. **Confounded multi-agent gains** — Most multi-agent coding systems change prompts, tools, token budgets and orchestration at once; it is hard to isolate what actually helps.
2. **Context pressure / truncation** — Single long generations on hard coding problems frequently hit caps or lose state; short worker calls + shared state reduce that.
3. **No training-free, inspectable scaffold on Pi** — Pi is deliberately minimal; users lack a ready-made zero-shot orchestration pattern that stays outside the core.
4. **Cost vs accuracy trade-off** — Structure + smaller workers can approach stronger single-call quality at lower cost when the manager owns integration.

## Goals

| Goal | Success signal |
|------|----------------|
| **G1** Useful control flow | Manager ↔ workers, external verify, re-curation, inspectable ledger |
| **G2** Short worker contexts | Workers see only the brief (+ optional ledger snippets), not full session history |
| **G3** Inspectable state | plan/notes/tasks + transcript; repo is source of truth for code |
| **G4** Extension, not core fork | Ships as Pi extension/skill; classic Pi remains available |
| **G5** Single-shot baseline | A/B against plain single-agent Pi remains easy |
| **G6** Provider-agnostic | Uses `@earendil-works/pi-ai` / Pi models; asymmetric models allowed |
| **G7** Repo-ready workers | Product path: pure codegen workers; manager integrates (ADR 0005) |

## Non-goals (near term)

- Changing Pi core agent loop  
- Learned / trained orchestrators  
- Claiming exact paper numbers without controlled re-runs  

## Architecture (product path)

```text
User coding task
    |
    ▼
Manager (tools + stronger model)
  explore · plan · brief · place · test · re-task
    |
    ├─ Worker A (no tools, cheaper model) ──► code text
    ├─ Worker B (no tools)                 ──► code text   [optional parallel]
    └─ ...
    |
    ▼
Gates pass → done / budget stop
```

Spawn helper: [pi-subagents](https://github.com/nicobailon/pi-subagents) ([ADR 0004](./adr/0004-subagents-as-spawn-helper.md)).

## Repository layout

```text
pi-zero-shot/
├── README.md
├── docs/
├── adr/
├── plan/
├── raw/
├── experiments/smoke-test/   ← 30-min Pi experiment
├── src/                      ← extension code (to be built)
└── scripts/
```

## Phased plan (summary)

| Phase | Name | Outcome |
|-------|------|---------|
| 0 | Discovery & mapping | Primitives mapped; spawn policy locked |
| 1 | Core ledger primitives | Workspace, transcript, sample-test runner |
| 2 | Role prompts & parsing | Ported / product prompts + parsers |
| 3 | Manager–worker loop | Scaffold + RoleLauncher (pi-subagents / fallback) |
| 4 | Observability & packaging | Metrics, installable package |
| 5 | Hardening | Provider quirks, optional parallelism |

Detailed task lists: **[plan/](./plan/)**.

## Key ADRs

- [ADR 0001](./adr/0001-use-extension-not-core-fork.md) — Extension / skill, not core fork  
- [ADR 0002](./adr/0002-filesystem-ledger.md) — Prefer real filesystem ledger  
- [ADR 0003](./adr/0003-sequential-manager-worker.md) — Sequential manager + single worker for MVP  
- [ADR 0004](./adr/0004-subagents-as-spawn-helper.md) — [pi-subagents](https://github.com/nicobailon/pi-subagents) as spawn helper only  
- [ADR 0005](./adr/0005-manager-tools-pure-workers.md) — Manager-only tools; pure codegen workers  

## Upstream references

| Project | Role |
|---------|------|
| **[slee-persis/GVS5H](https://github.com/slee-persis/GVS5H)** | Paper TeX/PDF, v1/v2 scaffolds, transcripts |
| [arXiv:2608.26480](https://arxiv.org/abs/2608.26480) | Published paper |
| [earendil-works/pi](https://github.com/earendil-works/pi) | Agent harness, extensions, `pi-ai` |
| **[nicobailon/pi-subagents](https://github.com/nicobailon/pi-subagents)** | Fresh-context sequential spawn; `noTools` |

## Status

Planning + smoke-test materials in-repo. Implementation follows `plan/phase-*.md`.

## License

TBD (recommended: MIT for this port’s code, consistent with Pi where compatible). Paper content remains under the authors’ arXiv license (CC BY 4.0); see [GVS5H](https://github.com/slee-persis/GVS5H) and arXiv.
