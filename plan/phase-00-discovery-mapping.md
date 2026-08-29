# Phase 0 — Discovery & mapping

## Goals

- Understand Pi’s extension points, session model, and tool loop well enough to host a sequential manager–worker scaffold.
- Decide ledger persistence (real FS vs session-backed).
- Produce a short written mapping of paper primitives → Pi primitives.

## Background

- [`docs/architecture.md`](../docs/architecture.md)
- [`adr/0001-use-extension-not-core-fork.md`](../adr/0001-use-extension-not-core-fork.md)
- [`adr/0002-filesystem-ledger.md`](../adr/0002-filesystem-ledger.md)
- Upstream: **[slee-persis/GVS5H](https://github.com/slee-persis/GVS5H)** — especially [`multiagent.py`](https://github.com/slee-persis/GVS5H/blob/master/codebase/v2-current/escalation/multiagent.py), [`orchestrator.py`](https://github.com/slee-persis/GVS5H/blob/master/codebase/v2-current/escalation/orchestrator.py)
- Paper extract: [`raw/PAPER.md`](../raw/PAPER.md)
- Pi: `@earendil-works/pi-agent-core`, extension docs, existing multi-agent community packages

## Tasks

- [ ] Read Pi extension / skill authoring docs and one existing extension for patterns.
- [ ] Map: manager, worker (fresh context), ledger files, transcript, sample-test gate → concrete Pi APIs or new types.
- [ ] Inventory conflicting or complementary multi-agent packages (agent-team, pipeline-team, pi-kot style).
- [ ] Decide and record: real filesystem workspace vs pure session-tree virtual ledger (update ADR 0002 status if needed).
- [ ] Confirm model routing path via `@earendil-works/pi-ai`.
- [ ] Write or update `docs/architecture.md` with the final mapping table and open questions resolved.

## Exit criteria

- [ ] Architecture doc answers: how a worker gets a fresh context; where ledger lives; how sample tests are invoked.
- [ ] Persistence decision recorded in ADR 0002 (Accepted or Rejected with rationale).
- [ ] No code required beyond notes / ADR updates.

## Verification

- Peer or self review of `docs/architecture.md` against GVS5H control flow (plan → ideate → manage ↔ worker → sample tests → finalize).
