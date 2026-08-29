# Phase 3 — Manager–worker loop as Pi extension

## Goals

Ship a working sequential zero-shot scaffold as a Pi extension or skill.

## Background

- `adr/0001-use-extension-not-core-fork.md`
- `adr/0003-sequential-manager-worker.md`
- GVS5H `multiagent_solve` control flow.
- Pi extension entry points / skill registration.

## Tasks

- [ ] Extension/skill entry point + configuration (model, max iters, workspace root, sample-test enable, strict format).
- [ ] Manager state machine: plan → ideation → (manage ↔ worker + sample tests) → finalize.
- [ ] Worker invocation with **fresh context** and ledger injection only.
- [ ] Sample-test feedback injected into manager prompt; hard override if manager says done while samples fail.
- [ ] Cutoff detection + summarizer call.
- [ ] No-progress guard (identical re-issued task → stop).
- [ ] Single-shot baseline mode (one call, same model, for comparison).
- [ ] Extract final `solution.py` / answer for the user / grader.

## Exit criteria

- [ ] User can run a coding task through the ledger scaffold inside Pi.
- [ ] Ledger files + transcript appear for the run.
- [ ] Sample-test failures keep the loop going.
- [ ] Single-shot baseline still available.

## Verification

- End-to-end on 1–3 synthetic or LiveCodeBench-style problems.
- Inspect transcript roles order matches paper (primary_plan, ideation, primary_manage, worker, …).
