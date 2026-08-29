# Phase 4 — Observability & packaging

## Goals

Make the scaffold observable in the Pi UX and installable by others.

## Background

- Paper’s emphasis on transcripts and per-call token accounting.
- Pi TUI / session viewer capabilities.

## Tasks

- [ ] Surface ledger files and transcript path in TUI or session metadata.
- [ ] Token / cost accounting (aggregate per problem and per role).
- [ ] Minimal benchmark driver (subset of LCB or local fixtures) comparing single vs manager.
- [ ] Package as installable Pi extension/skill (README usage, config example).
- [ ] Usage examples in root README or `docs/`.

## Exit criteria

- [ ] A new user can install/enable the extension and run one task with visible ledger + transcript.
- [ ] Cost/truncation summary available after a run.

## Verification

- Fresh clone / install path works.
- Manual walkthrough of TUI visibility.
