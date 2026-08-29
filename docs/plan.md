# Implementation Plan: Zero-Shot Self-Orchestration on Pi

Port of the GVS5H / arXiv:2608.26480 manager–worker ledger scaffold to the earendil-works/pi agent harness, preferably as a first-class extension or skill.

## Source Analysis Summary

### Core Design (from `codebase/v2-current/escalation/multiagent.py`)

- **Shared filesystem ledger** (per-problem content-hashed workspace):
  - `task.md` — problem statement
  - `plan.md` — short manager strategy (hard-capped)
  - `tasks.json` — curated task list (debug dump)
  - `notes.md` — curated / rewritten findings (not pure append)
  - `solution.py` / `answer.md` — current best artifact
  - `transcript.jsonl` — full call log with roles, tokens, finish_reason, reasoning

- **Roles** (same model, fresh context every call):
  1. Manager – plan (writes plan + seeds tasks)
  2. Ideation worker (proposes distinct approaches, no code)
  3. Manager loop (`_primary_manage`): reviews progress + sample-test verdict, curates list, picks *one* next task or declares `done`
  4. Worker: executes one task, rewrites solution/notes, proposes next steps
  5. Sample-test verifier (v2): runs public stdin samples; hard override if manager marks failing code “done”
  6. Cutoff summarizer (if worker hits token limit)
  7. Finalize worker (if needed)

- **Controls**: `MULTIAGENT_MAX_ITERS` (default 10), file size bounds, strict format mode, no-progress guard, sample-test gate.

### Target Platform

[earendil-works/pi](https://github.com/earendil-works/pi) — minimal TypeScript coding-agent harness with:
- `@earendil-works/pi-ai` (unified multi-provider LLM API)
- `@earendil-works/pi-agent-core` (agent loop, tools, sessions)
- `@earendil-works/pi-coding-agent` (CLI + TUI)
- Strong preference for **extensions / skills** over core changes.

Related: existing community multi-agent packages and the `pi-kot-async-orchestration` skill pattern (event-driven, non-polling supervisor).

---

## Phased Plan

### Phase 0: Discovery & Mapping (1–2 days)

- Map Pi’s agent loop, session state, tool-calling, extension points, and session backends.
- Decide persistence model: real filesystem workspace (closest to paper) vs. Pi session/branching + virtual ledger.
- Inventory existing multi-agent extensions for reuse / conflict avoidance.
- Confirm model routing via `pi-ai`.

**Deliverable**: Short design note comparing paper primitives → Pi primitives (see also `docs/architecture.md`).

### Phase 1: Core Ledger Primitives (2–3 days)

1. `LedgerWorkspace` class:
   - Create/reset per-problem directory (content-hash or session-id keyed).
   - Atomic read/write for all ledger files.
   - Hard size bounds (mirror paper’s `MAX_PLAN_CHARS` etc.).
   - Notes rewrite semantics (workers rewrite, do not pure-append).
2. Transcript recorder (every model call: role, messages, response, reasoning, tokens, finish_reason).
3. Sample-test runner (Python subprocess against public stdin tests; structured pass/fail + first failure).

**Tasks**:
- [ ] `LedgerWorkspace` API + unit tests
- [ ] Transcript schema + append-only writer
- [ ] Sample-test harness
- [ ] Cleanup / isolation guarantees

### Phase 2: Role Prompts & Parsing (1–2 days)

1. Port exact system prompts from `multiagent.py` (plan, ideation, manage, worker, finalize, cutoff-summary) into TypeScript constants or Pi prompt templates.
2. Robust section parsers (`_sections`, `_bullets`, `_parse_tasks`, code extraction).
3. Strict-format mode (config flag) for models that ignore headers.
4. Status / next-task extraction + invariants (cannot be “done” with empty artifact; sample-test hard override).

**Tasks**:
- [ ] Prompt library
- [ ] Robust parsers + fallbacks
- [ ] Unit tests against real transcript snippets from GVS5H `runs/`

### Phase 3: Manager–Worker Loop as Pi Extension (3–5 days)

1. Register a new mode or skill (e.g. `/ledger` or “self-orchestrate” mode).
2. Supervisor that:
   - Owns the ledger.
   - Issues short, self-contained worker prompts (fresh context).
   - Receives results and runs manage → worker → sample-test → manage up to `MAX_ITERS`.
3. Prefer event-driven / non-polling style (align with `pi-kot-async-orchestration` where possible). Paper is sequential (one worker at a time).
4. Finalize step + clean artifact extraction.
5. Single-shot baseline mode for A/B comparison.

**Tasks**:
- [ ] Extension entry point + configuration (model, max iters, workspace root, sample-test enable)
- [ ] Manager state machine
- [ ] Worker invocation (fresh context + ledger injection)
- [ ] Sample-test feedback injection
- [ ] Cutoff detection + summarizer
- [ ] No-progress guard
- [ ] Optional integration with Pi session tree / branching for inspection

### Phase 4: Integration, Observability & Benchmarking (2–3 days)

1. Expose ledger files and transcript in Pi TUI / session viewer.
2. Token/cost accounting.
3. Driver for LiveCodeBench-style (or any coding) tasks through the scaffold vs. plain Pi agent.
4. Reproduce a small subset of the paper’s conditions for validation.
5. Documentation + packaging as installable Pi extension/skill.

**Tasks**:
- [ ] TUI / session visibility for ledger state
- [ ] Cost & truncation telemetry
- [ ] Minimal benchmark harness
- [ ] README + usage examples
- [ ] Package as installable extension

### Phase 5: Hardening & Polish (ongoing)

- Provider-specific quirks (reasoning fields, clamp detection, temperature restrictions).
- Robustness to model format drift.
- Optional parallel workers while preserving ledger consistency.
- Config surface matching paper env vars where sensible.
- Tests against the paper’s own workspace transcripts.

---

## Prioritized Task List (MVP first)

**Must-have for usable MVP**
1. LedgerWorkspace + transcript
2. Ported prompts + parsers
3. Sequential manager–worker loop with sample-test gate
4. Pi extension that activates the loop for a coding task
5. Artifact extraction + single-shot baseline

**High-value next**
6. Full observability in TUI
7. Cost/truncation metrics
8. Cutoff summarizer + strict format mode
9. Packaging + docs

**Nice-to-have**
10. Async / parallel worker support (using pi-kot patterns)
11. Math-problem variant
12. Automated comparison runner against paper’s frozen LCB-100 ids

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Context management (paper’s main win is short worker contexts) | Ensure workers receive only ledger state, not full Pi session history |
| Tool-centric vs pure-prompt design | Prefer filesystem (or dedicated ledger tool) over forcing every step through Read/Write if it adds noise |
| Model routing complexity | Leverage `pi-ai` fully; avoid re-implementing GVS5H’s retry/reroute unless necessary |
| Evaluation fidelity | Use same sample tests + fixed LiveCodeBench evaluator for any “matching the paper” claims |

---

## Success Criteria (MVP)

- A user can enable the ledger scaffold on a coding task inside Pi.
- The manager–worker loop runs with the same control flow and invariants as the paper’s v2 scaffold.
- Ledger files and a transcript are produced and inspectable.
- Sample-test feedback influences the manager’s decisions.
- Single-shot baseline remains available for comparison.
