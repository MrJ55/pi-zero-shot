# Phase 3 — Manager–worker loop as Pi extension

## Goals

Ship a working sequential zero-shot scaffold as a Pi extension or skill, faithful to GVS5H v2.

## Background

- [`adr/0001-use-extension-not-core-fork.md`](../adr/0001-use-extension-not-core-fork.md)
- [`adr/0003-sequential-manager-worker.md`](../adr/0003-sequential-manager-worker.md)
- [`adr/0004-subagents-as-spawn-helper.md`](../adr/0004-subagents-as-spawn-helper.md)
- GVS5H [`multiagent_solve`](https://github.com/slee-persis/GVS5H/blob/master/codebase/v2-current/escalation/multiagent.py)
- Optional: [pi-subagents](https://github.com/nicobailon/pi-subagents) for `context: "fresh"` sequential spawns only

## Tasks

- [ ] Extension/skill entry point + configuration (model, max iters, workspace root, sample-test enable, strict format, `usePiSubagents: true|false`).
- [ ] Manager state machine: plan → ideation → (manage ↔ worker + sample tests) → finalize.
- [ ] `RoleLauncher` interface:
  - [ ] Implementation A: pi-subagents fresh sequential spawn (no builtin agents).
  - [ ] Implementation B: direct `pi-ai` / RPC one-shot fallback.
- [ ] Worker invocation with **fresh context** and ledger injection only; concurrency 1; same model.
- [ ] Prefer minimal/no tools on role children (generation-shaped).
- [ ] Sample-test feedback injected into manager prompt; hard override if manager says done while samples fail.
- [ ] Cutoff detection + summarizer call.
- [ ] No-progress guard (identical re-issued task → stop).
- [ ] Single-shot baseline mode (one call, same model, for comparison).
- [ ] Extract final `solution.py` / answer for the user / grader.

## Exit criteria

- [ ] User can run a coding task through the ledger scaffold inside Pi.
- [ ] Ledger files + full transcript appear for the run.
- [ ] Sample-test failures keep the loop going.
- [ ] Single-shot baseline still available.
- [ ] Path works with or without pi-subagents installed.

## Verification

- End-to-end on 1–3 synthetic or LiveCodeBench-style problems.
- Inspect transcript roles order matches paper / GVS5H (primary_plan, ideation, primary_manage, worker, …).
- Confirm no fork-context or parallel team behavior on the manager arm.
