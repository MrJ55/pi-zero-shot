# Review-by-GLM — Roadmap and Execution Critique

**Reviewer:** GLM (Z.ai), independent audit
**Date:** 2026-08-29
**Scope:** Critique of pi-zero-shot's phased plan (Phase 0–5), exit criteria, and execution state. What's done, what's missing, what's misleading.

---

## 1. The phased plan at a glance

`plan/README.md` declares six phases executed in order:

| Phase | Name | Outcome (per README) |
|---|---|---|
| 0 | Discovery & mapping | Paper ↔ Pi primitives mapped; spawn-helper policy locked (ADR 0004) |
| 1 | Core ledger primitives | `LedgerWorkspace`, transcript, sample-test runner |
| 2 | Role prompts & parsing | Ported prompts + robust section parsers |
| 3 | Manager–worker loop | Sequential scaffold; optional pi-subagents launcher |
| 4 | Observability & packaging | TUI visibility, cost metrics, installable package |
| 5 | Hardening | Provider quirks, format drift, optional parallelism |

Each phase file (`plan/phase-0N-*.md`) contains: Goals, Background pointers, Tasks (a `- [ ]` checklist), Exit criteria (also a `- [ ]` checklist), and Verification steps.

---

## 2. Execution state — what's actually done

### 2.1 The honest answer is: nothing

`src/extension/.gitkeep` is the only file under `src/`. No source code exists. No `package.json`, no `tsconfig.json`, no lockfile. No tests. No CI. No `LICENSE` file.

### 2.2 The misleading status line

`README.md:119`:

> Planning complete in-repo. Implementation follows `plan/phase-*.md` in order.

Reality:
- Phase 0's exit criteria (3 boxes) are **all unchecked**.
- ADR 0002 status is **Proposed** (not Accepted).
- `plan/VERIFY-LOG.md` is **empty** — header row only, no entries.
- Single commit on 2026-08-29; no incremental development history.

Planning is *drafted*, not *complete*. A reader who takes the status line at face value will be misled.

### 2.3 Phase-by-phase execution state

#### Phase 0 — Discovery & mapping

**Exit criteria (from `plan/phase-00-discovery-mapping.md`):**
- [ ] Architecture doc answers: how a worker gets a fresh context; where ledger lives; how sample tests are invoked; whether pi-subagents is optional dependency or deferred.
- [ ] ADR 0002 status updated if persistence decision is final; ADR 0004 remains the spawn-helper policy.
- [ ] No production feature code required beyond notes / ADR updates.

**Status:** **All three unchecked.** The architecture doc (`docs/architecture.md`) *does* answer most of the first criterion (it covers worker fresh context, ledger location, sample-test invocation, pi-subagents optionality), but no one has ticked the box. ADR 0002 is still Proposed. `VERIFY-LOG.md` is empty.

**Verdict:** Phase 0 is drafted but not closed. The author(s) wrote the architecture doc but did not formally verify the exit criteria or update ADR 0002's status. This is the gap between "planning drafted" and "planning complete."

#### Phase 1 — Core ledger primitives

**Exit criteria:**
- [ ] Can create a workspace, write all files, rewrite notes, append transcript, run sample tests, and reset cleanly.
- [ ] Tests pass without network.

**Status:** **No code exists.** No `LedgerWorkspace`, no transcript recorder, no sample-test runner, no tests.

#### Phase 2 — Role prompts & parsing

**Exit criteria:**
- [ ] Golden-file or fixture tests parse real-looking manager/worker replies into structured status, next task, and code.
- [ ] Strict mode string matches paper intent.

**Status:** **No code exists.** No prompt library, no section parser, no task-list parser, no code extraction, no strict-format mode, no tests.

#### Phase 3 — Manager–worker loop as Pi extension

**Exit criteria:**
- [ ] User can run a coding task through the ledger scaffold inside Pi.
- [ ] Ledger files + full transcript appear for the run.
- [ ] Sample-test failures keep the loop going.
- [ ] Single-shot baseline still available.
- [ ] Path works with or without pi-subagents installed.

**Status:** **No code exists.** No extension entry point, no manager state machine, no `RoleLauncher`, no worker invocation, no sample-test feedback injection, no cutoff detection, no no-progress guard, no single-shot baseline.

#### Phase 4 — Observability & packaging

**Exit criteria:**
- [ ] A new user can install/enable the extension and run one task with visible ledger + transcript.
- [ ] Cost/truncation summary available after a run.

**Status:** **No code exists.** No TUI surfacing, no token/cost accounting, no benchmark driver, no installable package, no usage examples.

#### Phase 5 — Hardening & polish

**Exit criteria:**
- [ ] Documented limitations and config reference.
- [ ] Regression tests for parsers and loop invariants.

**Status:** **No code exists.** No provider-specific handling, no format-drift fallbacks, no config surface, no regression tests.

---

## 3. Critique of the phase plan itself (independent of execution)

### 3.1 Phase 0 — Discovery & mapping

**What's good:**
- Correctly identifies the background reading (ADRs, GVS5H source files, pi-subagents docs).
- Correctly scopes the pi-subagents dependency ("use only as spawn helper, not builtin agents/teams").
- The exit criteria are concrete and verifiable.

**What's wrong:**
- The task list includes "Decide and record: real filesystem workspace vs pure session-tree virtual ledger (update ADR 0002 status if needed)" — but ADR 0002's Decision section already commits to real FS. This task is redundant if the ADR is Accepted; the ADR is mislabeled if the task is genuine. (See `03-ADR-CRITIQUE.md` for the ADR 0002 contradiction.)
- The task list does not include a "verify the 12 invariants" task. Phase 0 should produce a written cross-reference of plan claims to GVS5H source lines (similar to `04-GVS5H-FEATURE-MAPPING.md` in this review). Without that, Phase 1 begins with hidden fidelity gaps.

### 3.2 Phase 1 — Core ledger primitives

**What's good:**
- Correctly names all six workspace files plus `answer.md` for math.
- Correctly identifies the notes-rewrite invariant.
- Correctly identifies the sample-test runner as a subprocess.
- Promises unit tests.

**What's wrong:**
- "Hard size bounds (mirror paper `MAX_PLAN_CHARS` and notes cap)" — mentions the env name but doesn't pin the numbers (4000 for `plan.md`, 8000 for `notes.md`, 20000 for `answer.md`). A Phase 1 implementer would have to grep GVS5H to find them.
- Does not mention `MAX_TASKS=12` (`multiagent.py:72`).
- Does not mention the `wrote` guard (`multiagent.py:574` — only run sample tests when worker actually wrote code).
- Does not mention the `ANS_RE` non-empty-answer guard (`multiagent.py:192`).
- Does not mention the `infra_exhausted`/`infra_fail` flag (`orchestrator.py:336`, `multiagent.py:611-614`).
- "Atomic read/write" is mentioned but the GVS5H source uses plain `open(p).read()` / `open(p, "w")` — there's no atomicity guarantee. A faithful port should either match GVS5H (plain read/write) or add atomicity *and document the divergence*. The plan promises atomicity without specifying the mechanism or the divergence.

### 3.3 Phase 2 — Role prompts & parsing

**What's good:**
- Correctly names all 8 GVS5H functions to port: `_primary_plan`, `_ideation_worker`, `_primary_manage`, `_worker`, `_summarize_cutoff`, `_sections`, `_parse_tasks`, `_extract_py`. (Verified — all 8 exist in GVS5H `multiagent.py`.)
- Correctly identifies the strict-format mode as a config flag.
- Promises golden-file tests using snippets from GVS5H `runs/*/ws/*/transcript.jsonl`.

**What's wrong:**
- Does not mention `_strip_code` (`multiagent.py:137-140`) — the invariant that ideation's output has code stripped to prevent the manager misreading it as solved.
- "Strict-format mode (config flag) that appends the paper's 'literal headers only' rule" — does not specify the env name (`STRICT_FORMAT`), "auto" mode, or the muse/glimmer model list.
- Does not specify per-role temperatures (0.3 plan, 0.4 brainstorm, 0.2 task/curate/single).

### 3.4 Phase 3 — Manager–worker loop as Pi extension

**What's good:**
- Correctly names the control flow: "Manager state machine: plan → ideation → (manage ↔ worker + sample tests) → finalize."
- Correctly identifies the sample-test hard override: "hard override if manager says done while samples fail."
- Correctly identifies the no-progress guard: "identical re-issued task → stop."
- Correctly identifies the cut-off summarizer: "cutoff detection + summarizer call."
- Correctly identifies the single-shot baseline: "Single-shot baseline mode (one call, same model, for comparison)."
- Correctly identifies the RoleLauncher pattern with two implementations (pi-subagents + `pi-ai` fallback).

**What's wrong:**
- "Prefer minimal/no tools on role children (generation-shaped)" — should be "no tools, period." See ADR 0004 critique.
- Does not specify the skip-finalize-when-done optimization (`multiagent.py:592-595`).
- Does not specify the cut-off digest never-into-notes invariant (`multiagent.py:456-458`).
- Does not include a "test pi-subagents' `context: 'fresh'` semantics" task.
- Does not include a "no tools on workers, period" test that fails if any tool surface is exposed to a role call.

### 3.5 Phase 4 — Observability & packaging

**What's good:**
- Correctly identifies the observability goals: TUI visibility, cost metrics, installable package, usage examples.
- "Token / cost accounting (aggregate per problem and per role)" — matches GVS5H's per-call transcript accounting.

**What's wrong:**
- "Minimal benchmark driver (subset of LCB or local fixtures) comparing single vs manager" — does not pin the LCB `release_v6` split, the `lcb100_hardest_v6.json` id list, the §3.3 MockBuffer fix, the cap-match procedure, or the paired-pass protocol. Without these, "subset of LCB" is meaningless. (See `09-TEST-STRATEGY.md`.)
- Does not mention `regrade.py` (re-scoring stored generations against the fixed evaluator).
- Does not mention `infra_exhausted`/`infra_fail` exclusion from pass@1.

### 3.6 Phase 5 — Hardening & polish

**What's good:**
- Correctly identifies "provider quirks" as a hardening target.
- Correctly identifies "format drift" as a parser concern.
- Correctly identifies "config surface aligned with paper env knobs where useful (`MAX_ITERS`, caps, strict format)".
- Optional: parallel workers, math-problem variant — both reasonable post-MVP extensions.
- "Tests against selected GVS5H workspace transcripts (parser + control-flow regression)" — good.

**What's wrong:**
- "Provider quirks" is too vague. GVS5H `orchestrator.py:303-313` has specific clamp-detection logic; `orchestrator.py:openai_chat` has a 16-attempt reroute budget with hard wall-clock caps. Phase 5 should name these.
- "Resilience to model format drift (parser fallbacks)" — does not specify the fallback ladder.
- "Optional: parallel workers while preserving ledger consistency (post-MVP)" — parallel workers with a shared filesystem ledger require a concurrency-control mechanism (file locks, atomic writes, or a single-writer queue). The plan does not mention this.

---

## 4. The execution critique — what's actually wrong (not just incomplete)

### 4.1 The status line is misleading

`README.md:119` says "Planning complete in-repo." Phase 0's exit criteria are all unchecked. ADR 0002 is Proposed. `VERIFY-LOG.md` is empty. **Planning is drafted, not complete.**

**Fix:** Change the line to "Planning drafted; Phase 0 (Discovery & mapping) not yet started."

### 4.2 ADR 0002 contradicts Phase 0

ADR 0002's Decision section ("Prefer a real filesystem workspace… as the primary ledger implementation") reads as committed. But the ADR's Status is "Proposed." And Phase 0's task list includes "Decide and record: real filesystem workspace vs pure session-tree virtual ledger (update ADR 0002 status if needed)."

If the ADR's Decision is "prefer real FS," the Phase 0 task is redundant. If the ADR is genuinely "Proposed," the Decision section is mislabeled. Either way, this is an internal contradiction that will cost a Phase 0 implementer time.

**Fix:** Mark ADR 0002 as Accepted and delete the Phase 0 task, OR rewrite ADR 0002 to present both options neutrally and leave the Phase 0 task as the decider. (See `03-ADR-CRITIQUE.md`.)

### 4.3 "Prefer no / minimal tools" opens a door the paper closes

ADR 0004 §5: "prefer no / minimal tools so a role remains a generation, not a multi-turn edit agent." Phase 3: "Prefer minimal/no tools on role children (generation-shaped)."

GVS5H workers have **zero tools**. They are pure chat completions. The paper's "worker = single generation" invariant depends on this. The word "minimal" leaves room for "maybe one tool" — but any tool surface (even file read) breaks the invariant by allowing the worker to act as a multi-turn agent.

**Fix:** Change "prefer no / minimal tools" to "no tools, period." (See ADR 0004 critique.)

### 4.4 No LICENSE file

README line 123: "TBD (recommended: MIT for this port's code, consistent with Pi where compatible)." A public repo without a LICENSE is, by default, "all rights reserved" — meaning nobody can legally use, copy, or contribute to the code. Since the *stated intent* is MIT, ship the MIT LICENSE. It's a 21-line file.

### 4.5 No build tooling despite committing to TypeScript

`.gitignore` lists `node_modules/`, `dist/`, `.turbo/` (implying a Node/TS/Turbo project). ADR 0004 §1 commits to a "deterministic TypeScript manager loop." But there is no `package.json`, `tsconfig.json`, or lockfile. A Phase 1 implementer would have to invent the project structure from scratch.

### 4.6 No tests, no CI

Phase 1 promises "Unit tests for workspace bounds, rewrite behavior, and sample-test parsing." Phase 2 promises "Golden-file or fixture tests parse real-looking manager/worker replies." Phase 5 promises "Regression tests for parsers and loop invariants." But there is no test runner configured, no test directory, no `.github/workflows/` CI. A repo that promises tests in three phases but ships none has, in practice, deferred tests indefinitely.

### 4.7 No dependency pinning

`@earendil-works/pi-ai`, `@earendil-works/pi-agent-core`, and (optionally) `pi-subagents` versions are all unspecified. The plan's G6 ("Provider-agnostic — uses `@earendil-works/pi-ai`") commits to a dependency without pinning a version. pi-subagents in particular is an evolving community package — its `context: "fresh"` semantics could change between minor versions. Without a lockfile, a future `npm install` may pull a breaking version.

### 4.8 `VERIFY-LOG.md` is empty

The plan/README.md §7 says "Record notable deviations or verification results in `VERIFY-LOG.md`." The file exists but is empty (a header row only). No phase exit criteria have been checked. This is the *only* mechanism the plan provides for tracking progress, and it's blank.

### 4.9 Single-commit history

The entire repo was pushed in one commit at 2026-08-29 16:39:06 +0200, with the message "docs: add structured Terra architecture and implementation review." The commit message references "Terra" — consistent with the existence of a `review-by-Terra/` directory (which we did not inspect, per the user's instruction). The repo was created two days after the paper's arxiv date (2026-08-27). This is consistent with a parallel review effort, not iterative development. There is no `CHANGELOG.md`, no `CONTRIBUTING.md`, no `CODE_OF_CONDUCT.md`.

### 4.10 `raw/PAPER.md` is thin

The paper extract at `raw/PAPER.md` is 21 lines: title, authors, arxiv ID, abstract (one paragraph, copied from the arxiv page), and a link table. It does not extract the method section, the §3.1 four-difference list, the §3.3 MockBuffer fix, the experimental setup, or any of the headline numbers. For a repo whose primary goal is "faithful to GVS5H v2," the paper extract is the *least* faithful document in the repo. A faithful extract would include at least the §3.1 list and the §3.3 fix description verbatim.

---

## 5. What a revised roadmap should look like

Based on the critique above, here's a revised phase structure that closes the 12 gaps and fixes the execution issues. Effort estimates assume one full-time implementer.

### Phase 0 (revised) — Discovery, mapping, and gap closure (1–2 days)

Original Phase 0 + the following:
- **NEW:** Produce a "Plan claims → GVS5H source lines" cross-reference (similar to `04-GVS5H-FEATURE-MAPPING.md` in this review).
- **NEW:** Resolve ADR 0002's status-vs-Decision contradiction.
- **NEW:** Add a "Known divergences from GVS5H" doc listing the 12 gaps from §3 of `02-ARCHITECTURE-REVIEW.md` and how each will be closed in later phases.
- **NEW:** Update `raw/PAPER.md` to include §3.1 four-difference list and §3.3 MockBuffer fix description verbatim.
- **NEW:** Add a `LICENSE` file (MIT).
- **NEW:** Add `package.json`, `tsconfig.json`, lockfile.
- **NEW:** Add `.github/workflows/ci.yml` (placeholder: `tsc --noEmit` only, until tests exist).

Exit criteria:
- [ ] All original Phase 0 exit criteria.
- [ ] Cross-reference doc exists and every ❌ and ⚠ gap has an assigned closing phase.
- [ ] ADR 0002 status resolved.
- [ ] LICENSE file exists.
- [ ] `package.json` + `tsconfig.json` + lockfile exist; `npm install` works.
- [ ] CI workflow exists; `tsc --noEmit` passes (on an empty `src/`).

### Phase 1 (revised) — Core ledger primitives (2–3 days)

Original Phase 1 + the following:
- **NEW:** Pin the size bound numbers: `MAX_PLAN_CHARS=4000`, `MAX_NOTES_CHARS=8000`, `MAX_ANSWER_CHARS=20000`, `MAX_TASKS=12`. Expose all four as config knobs.
- **NEW:** Implement the `wrote` guard: only run sample tests when worker actually wrote code.
- **NEW:** Implement the `ANS_RE` non-empty-answer guard.
- **NEW:** Add `infra_exhausted`/`infra_fail` to the transcript schema (one extra field on `_record`).
- **NEW:** Implement workspace reset semantics (all files cleared at the start of each problem — matches `multiagent.py:540-543`).
- **NEW:** Document the atomicity choice (match GVS5H plain read/write OR add atomicity with documented divergence).

### Phase 2 (revised) — Role prompts & parsing (2 days)

Original Phase 2 + the following:
- **NEW:** Port `_strip_code` and document the negative invariant (ideation output must have code stripped).
- **NEW:** Implement `STRICT_FORMAT` env knob with "auto" mode and muse/glimmer model list.
- **NEW:** Specify per-role temperatures (0.3 plan, 0.4 brainstorm, 0.2 task/curate/single) as config knobs.

### Phase 3 (revised) — Manager–worker loop as Pi extension (3–4 days)

Original Phase 3 + the following:
- **NEW:** Change "Prefer minimal/no tools on role children" to "No tools on role children, period."
- **NEW:** Add a test that fails if any tool surface is exposed to a role call.
- **NEW:** Implement the skip-finalize-when-done optimization.
- **NEW:** Implement the cut-off digest never-into-notes invariant.
- **NEW:** Add a task to test pi-subagents' `context: "fresh"` semantics against GVS5H's role-call shape.
- **NEW:** Propagate `infra_exhausted` through `status_out` and consume it in the grader.

### Phase 4 (revised) — Observability & packaging (2–3 days)

Original Phase 4 + the following:
- **NEW:** Vendor or pin the §3.3 MockBuffer fix in the eval driver.
- **NEW:** Pin the LCB `release_v6` split + `lcb100_hardest_v6.json` id list.
- **NEW:** Commit to a paired-pass protocol (5 passes, paired t-test, per-pass Δ).
- **NEW:** Implement `infra_fail` exclusion from pass@1 in the grader.

### Phase 5 (revised) — Hardening & polish (2 days)

Original Phase 5 + the following:
- **NEW:** Specify provider clamp detection logic (or document that `pi-ai` handles it).
- **NEW:** Specify reroute budget and wall-clock caps (or document that `pi-ai` handles retries).
- **NEW:** Specify `finish_reason` string normalization across providers.
- **NEW:** Specify reasoning capture per provider.
- **NEW:** If parallel workers are added, specify the concurrency-control mechanism (file locks, atomic writes, or single-writer queue).
- **NEW:** Implement `capmatch_q38.py` analog (or document that the local Qwen arm won't be cap-matched).

### Total revised effort

~12–16 days for one full-time implementer, assuming the 12 gaps are closed during the relevant phases (not deferred to a "Phase 6 cleanup").

---

## 6. Roadmap verdict

The phased plan is well-structured and the phase ordering is correct. The phase exit criteria are mostly concrete and verifiable. The plan's weakness is **not** in its structure but in its **content**: each phase omits specific invariants from GVS5H that any faithful port must preserve. The 12 gaps in `02-ARCHITECTURE-REVIEW.md` map directly to specific tasks that should be added to specific phases (see §5 above).

The execution state is the more pressing problem: zero source code, no LICENSE, no build tooling, no tests, no CI, ADR 0002 still Proposed, Phase 0 exit criteria all unchecked, `VERIFY-LOG.md` empty, and a misleading "Planning complete in-repo" status line. Closing the execution gap is a 1–2 week exercise for a single implementer, *if* the 12 architectural gaps are addressed in the plan first.
