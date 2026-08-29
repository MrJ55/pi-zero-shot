# Phase 2 — Role prompts & parsing

## Goals

Port the paper’s role prompts and make their structured outputs reliably parseable.

## Background

- GVS5H `multiagent.py`: `_primary_plan`, `_ideation_worker`, `_primary_manage`, `_worker`, `_summarize_cutoff`, `_sections`, `_parse_tasks`, `_extract_py`.
- Paper’s mandatory section headers and strict-format mode for some models.

## Tasks

- [ ] Port system prompts (plan, ideation, manage, worker, finalize, cutoff-summary) into a prompt library (TS constants or Pi prompt templates).
- [ ] Implement section parser robust to `### HEADER`, `**HEADER**`, `HEADER:` styles.
- [ ] Implement bullet / task-list parser (`[done]` / `[todo]`).
- [ ] Code extraction from fenced blocks.
- [ ] Strict-format mode (config flag) that appends the paper’s “literal headers only” rule.
- [ ] Invariants: cannot mark done with empty artifact; sample-test failure forces continue.
- [ ] Unit tests using snippets from GVS5H `runs/*/ws/*/transcript.jsonl` where possible.

## Exit criteria

- [ ] Golden-file or fixture tests parse real-looking manager/worker replies into structured status, next task, and code.
- [ ] Strict mode string matches paper intent.

## Verification

- Parser tests pass on both clean and slightly messy model outputs.
