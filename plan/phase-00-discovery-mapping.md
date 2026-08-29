# Phase 0 — Discovery & mapping

## Goals

- Understand Pi’s extension points, session model, and tool loop well enough to host a sequential manager–worker scaffold.
- Decide ledger persistence (real FS vs session-backed).
- Produce a short written mapping of paper primitives → Pi primitives.
- Confirm how optional [pi-subagents](https://github.com/nicobailon/pi-subagents) is used **only** as a spawn helper (ADR 0004).

## Background

- [`docs/architecture.md`](../docs/architecture.md)
- [`adr/0001-use-extension-not-core-fork.md`](../adr/0001-use-extension-not-core-fork.md)
- [`adr/0002-filesystem-ledger.md`](../adr/0002-filesystem-ledger.md)
- [`adr/0003-sequential-manager-worker.md`](../adr/0003-sequential-manager-worker.md)
- [`adr/0004-subagents-as-spawn-helper.md`](../adr/0004-subagents-as-spawn-helper.md) — **Accepted**
- Upstream method: **[slee-persis/GVS5H](https://github.com/slee-persis/GVS5H)** — especially [`multiagent.py`](https://github.com/slee-persis/GVS5H/blob/master/codebase/v2-current/escalation/multiagent.py), [`orchestrator.py`](https://github.com/slee-persis/GVS5H/blob/master/codebase/v2-current/escalation/orchestrator.py)
- Paper extract: [`raw/PAPER.md`](../raw/PAPER.md)
- Optional spawn helper: **[nicobailon/pi-subagents](https://github.com/nicobailon/pi-subagents)** (`context: "fresh"`, sequential only; not builtin roles/teams)
- Pi: `@earendil-works/pi-agent-core`, `@earendil-works/pi-ai`, extension docs

## Phase 0 note — ecosystem shortcut (non-conflicting)

Faithfulness to GVS5H remains the primary goal. Among existing Pi packages, **pi-subagents** is the only practical accelerator that does not force a different multi-agent product model:

- Use it (optionally) to spawn **fresh, sequential** role children and wait for a result.
- Keep the **manager state machine, ledger, prompts, parsers, and sample-test gate** in pi-zero-shot.
- Do **not** use pi-subagents builtin `worker`/`reviewer`/`scout` agents, council modes, or parallel fan-out for the paper loop.
- Prefer **no / minimal tools** on role children so each call stays a generation (paper shape), not a multi-turn coding agent.
- If invariants cannot be met, fall back to direct `pi-ai` / RPC one-shots with no package dependency.

`pi-agents-team` and heavy workflow graphs remain out of the replication path (see ADR 0004).

## Tasks

- [ ] Read Pi extension / skill authoring docs and one existing extension for patterns.
- [ ] Map: manager, worker (fresh context), ledger files, transcript, sample-test gate → concrete Pi APIs or new types.
- [ ] Skim [pi-subagents tool reference](https://github.com/nicobailon/pi-subagents/blob/main/docs/tool-reference.md) for `context: "fresh"`, concurrency, and custom agent definition — record spawn API notes in `docs/architecture.md`.
- [ ] Confirm fallback path without pi-subagents (`pi-ai` or `pi --mode rpc` one-shot).
- [ ] Decide and record: real filesystem workspace vs pure session-tree virtual ledger (update ADR 0002 status if needed).
- [ ] Confirm model routing path via `@earendil-works/pi-ai` (same model for all roles).
- [ ] Write or update `docs/architecture.md` with the final mapping table; resolve open questions (workers = fresh role calls; package scope = spawn helper only).

## Exit criteria

- [ ] Architecture doc answers: how a worker gets a fresh context; where ledger lives; how sample tests are invoked; whether pi-subagents is optional dependency or deferred.
- [ ] ADR 0002 status updated if persistence decision is final; ADR 0004 remains the spawn-helper policy.
- [ ] No production feature code required beyond notes / ADR updates.

## Verification

- Peer or self review of `docs/architecture.md` against GVS5H control flow (plan → ideate → manage ↔ worker → sample tests → finalize).
- Confirm no design step depends on parallel teams, summary-only parent context, or package default role prompts.
