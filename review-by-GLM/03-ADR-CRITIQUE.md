# Review-by-GLM — ADR Critique

**Reviewer:** GLM (Z.ai), independent audit
**Date:** 2026-08-29
**Scope:** Detailed critique of pi-zero-shot's four ADRs (0001, 0002, 0003, 0004): what's right, what's wrong, what to change.

---

## ADR Inventory

| ADR | Title | Status | Verdict |
|---|---|---|---|
| 0001 | Use extension not core fork | Accepted | ✅ Well-reasoned, no issues |
| 0002 | Filesystem ledger | Proposed | ⚠ Internal contradiction |
| 0003 | Sequential manager-worker | Accepted for MVP | ✅ Well-reasoned |
| 0004 | Subagents as spawn helper | Accepted | ⚠ Strong but three fixable issues |

---

## ADR 0001 — Implement as Pi Extension / Skill, not Core Fork

**Status:** Accepted
**Verdict:** ✅ **Well-reasoned, no issues.**

### Context (correctly stated)

Pi's design philosophy strongly prefers a minimal core extended via skills, prompt templates, and packages rather than growing built-in multi-agent machinery. The GVS5H scaffold is a self-contained, training-free orchestration pattern that can be expressed as a supervisor + ledger + short-lived workers.

### Decision (correctly stated)

Implement Zero-Shot Self-Orchestration as a first-class Pi extension or skill (this repository), not as a fork or PR against pi core.

### Consequences (honest)

- Positive: compatible with upstream Pi evolution; users opt-in; easier packaging and iteration.
- Positive: respects Pi's "extensions over core" rule.
- Negative: some deeper integration points may require more work or future core hooks.
- Negative: cannot assume core changes; must work with existing tool and session APIs.

### Alternatives considered (correctly rejected)

- Fork pi and add built-in mode → rejected (philosophy + maintenance burden).
- Pure external script that shells out to pi → weaker integration and observability.

### Critique

This ADR is the strongest of the four. The context is correctly stated (Pi's "extensions over core" philosophy). The decision follows. The consequences are honest about both positives and negatives. The alternatives are correctly rejected. No changes needed.

One small note: the ADR could cite a specific Pi document or extension example to ground the "Pi's design philosophy" claim. As written, it's a paraphrase. But this is a stylistic preference, not a defect.

---

## ADR 0002 — Prefer Real Filesystem Ledger

**Status:** Proposed
**Verdict:** ⚠ **Internal contradiction — the ADR and Phase 0 contradict each other.**

### Context (correctly stated)

The paper's gains are attributed in large part to the shared filesystem workspace that keeps each worker's context short while preserving state across turns. Pi already has sophisticated session trees, branching, and compaction.

### Decision (committed in tone, Proposed in status)

> Prefer a **real filesystem workspace** (content-hash or session-id keyed directory) as the primary ledger implementation for fidelity to the paper and easy human/tool inspection. Optionally layer Pi session artifacts on top for TUI integration.

The Decision section reads as committed ("Prefer… as the primary ledger implementation"). But the Status is "Proposed" — meaning the decision is *not yet committed*.

### Consequences (honest)

- Positive: closest match to measured paper behavior; easy to debug and to compare against GVS5H transcripts.
- Positive: workers can be given a clean, bounded view of state.
- Negative: must manage cleanup, isolation, and multi-session safety.
- Negative: pure "everything-in-session" purity is sacrificed.

### Alternatives considered

- Pure virtual ledger inside Pi session tree only → better native integration but drifts from the paper's measured mechanism and makes external inspection harder.

### The contradiction

Phase 0's task list (`plan/phase-00-discovery-mapping.md`) includes:

> - [ ] Decide and record: real filesystem workspace vs pure session-tree virtual ledger (update ADR 0002 status if needed).

If the ADR's Decision is "prefer real FS," then Phase 0's task is redundant — the decision is already made. A Phase 0 implementer reading the ADR will assume the decision is made and skip the Phase 0 task. A reviewer will then reject the Phase 0 exit criteria for not having done the task.

If the ADR is genuinely "Proposed" (status) then the Decision section is mislabeled — it should present both options neutrally, not commit to one.

### Critique

Either:
1. **Mark ADR 0002 as Accepted** and delete the Phase 0 task — the decision is already made. OR
2. **Rewrite ADR 0002** to actually present both options neutrally, leave Status as Proposed, and let Phase 0 settle it.

Currently the ADR and the Phase 0 task contradict each other. This is a documentation bug, but it has a real cost: a Phase 0 implementer reading the ADR will assume the decision is made and skip the Phase 0 task, then a reviewer will reject the Phase 0 exit criteria for not having done the task.

### What the ADR also misses

The ADR frames the choice as "real FS vs. pure session-tree virtual ledger." This is a real choice, but the ADR does not cite the GVS5H source of truth. The reference implementation uses real FS (`multiagent.py:78-79` `_slug` for content-hash workspace naming; `:540-543` workspace init). A faithful port should cite this.

The ADR also does not mention cleanup/isolation/multi-session safety as concrete invariants. GVS5H `multiagent.py:540-543` resets all workspace files at the start of each problem. A faithful port needs the same reset semantics.

### Recommendation

Rewrite ADR 0002 to:
1. Cite GVS5H `multiagent.py:78-79` and `:540-543` as the source of truth.
2. State the workspace reset invariant (all files cleared at the start of each problem).
3. Pick one of the two paths above (mark Accepted OR rewrite neutrally) and resolve the Phase 0 contradiction.

---

## ADR 0003 — Sequential Manager + Single Worker (Paper Style)

**Status:** Accepted for MVP
**Verdict:** ✅ **Well-reasoned, no issues.**

### Context (correctly stated)

The paper's scaffold is deliberately sequential: the manager picks *one* next task, a fresh worker executes it, sample tests run, then the manager re-curates. Parallelism is not part of the measured design.

Pi has emerging async / multi-worker patterns.

### Decision (correctly stated)

MVP implements the **exact sequential control flow** of the paper (manager ↔ one worker at a time, up to `MAX_ITERS`). Parallel or async fan-out is a later, optional extension.

### Consequences (honest)

- Positive: faithful reproduction of the published method.
- Positive: simpler correctness (no concurrent ledger writes).
- Negative: does not immediately exploit Pi's parallel worker capabilities.

### Alternatives considered (correctly rejected)

- Jump straight to parallel workers → risks diverging from the paper before a working baseline exists.

### Critique

Well-reasoned. The context correctly identifies that the paper's scaffold is sequential (matches `multiagent.py:547-595`). The decision to match the paper for MVP is correct — diverging from the paper before a working baseline exists would make fidelity claims unverifiable. The "Accepted for MVP" status is appropriate — it leaves the door open for a future ADR to revisit parallelism.

One small enhancement: the ADR could cite the GVS5H source of the `MAX_ITERS` invariant (`multiagent.py:42`, env `MULTIAGENT_MAX_ITERS`, default `"10"`) to ground the claim. As written, `MAX_ITERS` is referenced by name but not by source.

---

## ADR 0004 — pi-subagents as Spawn Helper Only

**Status:** Accepted
**Verdict:** ⚠ **Strong ADR with three fixable issues.**

### Context (correctly stated)

Faithfulness to GVS5H / arXiv:2608.26480 is paramount: sequential manager ↔ one worker, fresh context every role call, shared filesystem ledger, sample-test hard override, same model and fixed role prompts, workers as single generations (not multi-turn tool-using coding agents).

Pi already has mature packages for spawning isolated children. Two were compared for Option A (reuse infrastructure without replacing the paper loop):

| Package | Fit for exact replication |
|---|---|
| nicobailon/pi-subagents | Strong: first-class `context: "fresh"`, sequential parent control, lighter opinions |
| KristjanPikhof/Pi-Agents-Team (`pi-agents-team`) | Weak for fidelity: parallel teams, role profiles, summary-only parent view, worker reuse |

### Decision (correctly framed)

1. **pi-zero-shot owns the control flow** — deterministic TypeScript manager loop matching GVS5H v2 (plan → ideation → manage ↔ worker + sample tests → finalize).
2. **Optional dependency on pi-subagents** solely as a spawn helper for fresh, sequential role calls.
3. **Do not** use pi-subagents builtin agents (`worker`, `reviewer`, `scout`, …), team/council modes, parallel fan-out, or fork-default context as the paper loop.
4. **Do not** adopt pi-agents-team for the replication path.
5. Each paper role launch must satisfy:
   - `context: "fresh"` (or equivalent isolated one-shot)
   - concurrency = 1
   - same model for every role
   - paper system prompt + user message = ledger injection only
   - **prefer no / minimal tools** so a role remains a generation, not a multi-turn edit agent
6. Sample tests remain an external subprocess owned by pi-zero-shot, not a "verifier agent."
7. If pi-subagents cannot preserve these invariants, fall back to direct `@earendil-works/pi-ai` (or bare `pi --mode rpc` one-shots) without blocking the port.

### Consequences (honest)

- Positive: Fresh-context child management can be borrowed instead of reimplemented. Clear boundary: package = plumbing; paper semantics stay in this repo. Compatible with a pure `pi-ai` path.
- Negative: Optional peer dependency and version alignment with pi-subagents / Pi. Implementers must resist using package defaults that would confound replication.
- Neutral: ADR 0001–0003 unchanged.

### Critique — three fixable issues

#### Issue 1 — "Prefer no / minimal tools" should be "no tools, period"

ADR 0004 §5 says "prefer no / minimal tools so a role remains a generation, not a multi-turn edit agent."

GVS5H workers have **zero tools**. They are pure chat completions. The paper's "worker = single generation" invariant depends on this. The word "minimal" leaves room for "maybe one tool" — but any tool surface (even file read) breaks the invariant by allowing the worker to act as a multi-turn agent.

**Fix:** Change "prefer no / minimal tools" to "no tools, period" in both ADR 0004 §5 and Phase 3's "Prefer minimal/no tools on role children (generation-shaped)" task.

This is the single most important ADR-level fix. It's a one-line change with disproportionate impact on fidelity.

#### Issue 2 — No version pin

ADR 0004 commits to an optional dependency on pi-subagents and a fallback to `@earendil-works/pi-ai`, but does not pin versions of either. pi-subagents is an evolving community package — its `context: "fresh"` semantics could change between minor versions. Without a lockfile, a future `npm install` may pull a breaking version.

**Fix:** Add a "Dependency pinning" subsection to ADR 0004:
- Pin pi-subagents to a specific version (or commit SHA) in `package.json`.
- Pin `@earendil-works/pi-ai` and `@earendil-works/pi-agent-core` to specific versions.
- Document the fallback path: if pi-subagents breaks the invariants, switch to the `pi-ai` fallback and pin that instead.

#### Issue 3 — "Context: fresh" asserted, not verified

ADR 0004 §1 asserts "fresh context every role call." But pi-subagents' actual `context: "fresh"` semantics are not tested against GVS5H's invariant. A "fresh" context that still inherits parent tools or system prompts would silently break the worker = single-generation invariant.

**Fix:** Add a Phase 3 task: "Test pi-subagents' `context: 'fresh'` against GVS5H's role-call shape." Specifically:
- Verify no parent session history is inherited.
- Verify no tools are inherited from the parent.
- Verify the worker receives only the system prompt + the ledger-injected user message.
- Add a regression test that asserts these invariants after every pi-subagents version bump.

### What the ADR gets right (worth keeping)

1. **The "do not use" list is comprehensive and shows real understanding.** Builtin `worker`/`reviewer`/`scout`, council modes, parallel fan-out, fork-default context — all correctly rejected. pi-agents-team correctly rejected for the replication path.

2. **The fallback path is sensible.** "If pi-subagents cannot preserve these invariants, fall back to direct `pi-ai`" is exactly the right escape hatch.

3. **The control-plane-vs-spawn-helper distinction is clear.** `docs/architecture.md` lines 24-32 capture it well: pi-zero-shot owns the ledger, prompts, parsers, sample-test gate, and manager state machine; pi-subagents is plumbing only.

4. **The non-goals are correctly stated.** Builtin agents, council modes, parallel fan-out are all explicitly out.

---

## Summary of ADR-level recommendations

| ADR | Recommendation | Effort |
|---|---|---|
| 0001 | None needed. | 0 |
| 0002 | Resolve the status-vs-Decision contradiction. Cite GVS5H `multiagent.py:78-79`, `:540-543`. State the workspace reset invariant. | 30 min |
| 0003 | Optional: cite GVS5H `multiagent.py:42` for the `MAX_ITERS` invariant. | 5 min |
| 0004 | (1) Change "prefer no / minimal tools" to "no tools, period". (2) Add a "Dependency pinning" subsection. (3) Add a Phase 3 task to verify `context: "fresh"` semantics. | 1 hour |

The ADRs are, on the whole, well-written. ADR 0001 and ADR 0003 need no changes. ADR 0002 has a real internal contradiction that must be fixed. ADR 0004 is strong but has three fixable issues, of which the "no tools, period" fix is the most consequential for paper fidelity.
