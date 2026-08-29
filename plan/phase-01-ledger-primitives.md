# Phase 1 — Core ledger primitives

## Goals

Implement the shared workspace and supporting utilities that every later phase depends on.

## Background

- [GVS5H `multiagent.py`](https://github.com/slee-persis/GVS5H/blob/master/codebase/v2-current/escalation/multiagent.py) workspace helpers (`_read`, `_write`, `_append`, size caps, notes rewrite).
- [`adr/0002-filesystem-ledger.md`](../adr/0002-filesystem-ledger.md)
- Paper §3.1 (shared filesystem workspace) — see [`raw/PAPER.md`](../raw/PAPER.md) and [arXiv HTML](https://arxiv.org/html/2608.26480v1).

## Tasks

- [ ] Create `LedgerWorkspace` (TypeScript):
  - Create/reset directory keyed by content hash or session id.
  - Atomic read/write for: `task.md`, `plan.md`, `notes.md`, `solution.py` / `answer.md`, `tasks.json`, `transcript.jsonl`.
  - Hard size bounds (mirror paper `MAX_PLAN_CHARS` and notes cap).
  - Notes **rewrite** semantics (not pure append).
- [ ] Transcript recorder: append JSONL records with role, request, response, reasoning, tokens, finish_reason, provider metadata.
- [ ] Sample-test runner: run `solution.py` against public stdin samples (subprocess); return `{ran, passed, total, fail}`.
- [ ] Cleanup / isolation: reset workspace between runs of the same key; document multi-session safety.
- [ ] Unit tests for workspace bounds, rewrite behavior, and sample-test parsing.

## Exit criteria

- [ ] Can create a workspace, write all files, rewrite notes, append transcript, run sample tests, and reset cleanly.
- [ ] Tests pass without network.

## Verification

- Unit tests green.
- Manual: create workspace from a sample LiveCodeBench-style problem statement and inspect files on disk.
- Optional: compare file roles to a GVS5H workspace under [`runs/`](https://github.com/slee-persis/GVS5H/tree/master/runs).
