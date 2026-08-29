# Review-by-GLM — Executive Summary

**Reviewer:** GLM (Z.ai), independent audit
**Date:** 2026-08-29
**Scope:** Full audit of `MrJ55/pi-zero-shot` @ `cc5ae55` against arXiv:2608.26480 and the reference implementation `slee-persis/GVS5H` @ `6d7a143b`
**Method:** Parallel ingestion of all three sources (pi-zero-shot clone, GVS5H clone, arxiv PDF + HTML + LaTeX source). First-hand reading of every markdown file in pi-zero-shot; full read of GVS5H `multiagent.py` (643 lines), `orchestrator.py` (697 lines), and the §3.3 MockBuffer fix in `testing_util.py`; first 200 lines + targeted greps of the paper text. Twelve line-level verifications performed personally. **No other `review-*` folders consulted** — `review-by-Terra/` in pi-zero-shot was deliberately excluded per the user's instruction.

---

## Verdict: A genuinely good plan with zero execution, and 12 specific fidelity gaps that any implementer will silently inherit.

`MrJ55/pi-zero-shot` is a **planning-only repository**: 25 tracked files, ~600 lines of Markdown, **zero source code**. The only file under `src/` is `src/extension/.gitkeep`. The README's status line ("Planning complete in-repo. Implementation follows `plan/phase-*.md` in order") is misleading — Phase 0's exit criteria are all unchecked, ADR 0002 is still "Proposed," and `VERIFY-LOG.md` is empty. Planning is *drafted*, not *complete*.

The plan targets the right thing: the GVS5H v2 manager–worker scaffold (paper §3.1) ported into a Pi extension as TypeScript. The ADRs reason well. The architecture mapping table in `docs/architecture.md` is faithful to `multiagent.py` v2 in spirit and in most of its headline invariants. The phased plan is realistic (Phase 0 discovery → Phase 1 ledger primitives → Phase 2 prompts/parsing → Phase 3 loop → Phase 4 observability → Phase 5 hardening).

But a line-by-line cross-check against the actual GVS5H source (full report in `02-ARCHITECTURE-REVIEW.md` and `04-GVS5H-FEATURE-MAPPING.md`) finds **12 specific invariants the plan does not capture**. The most consequential are:

- The `infra_exhausted`/`infra_fail` flag (`orchestrator.py:336`, consumed at `multiagent.py:611-614`) — provider outage exclusion from pass@1. Without this, any provider failure during a benchmark run is scored as a model failure.
- The §3.3 MockBuffer / `readline()` fix in the LiveCodeBench evaluator (`testing_util.py:94-100`) — silently misgrades any candidate using `sys.stdin.buffer.readline()` if not vendored.
- `capmatch_q38.py` — token-exact 250k→128k truncation for the Qwen3.8-27B single arm. Without it, the Qwen3.8-27B comparison is not like-for-like with the paper's reported number.
- The paired-pass protocol (5 passes, paired t-test, per-pass Δ). The paper's headline significance claims depend on this; a single-pass comparison cannot reproduce them.
- The "no tools, period" rule on workers. ADR 0004 §5 says "prefer no / minimal tools" — GVS5H workers have **zero** tools, and "minimal" opens a door the paper closes.

---

## Key Findings

### Critical (Blocks Fidelity / Reproduction)

| # | Finding | Source | Impact |
|---|---------|--------|--------|
| C1 | **No `infra_exhausted`/`infra_fail` flag in plan** — GVS5H sets `meta["infra_exhausted"]=True` when all reroute attempts fail without usable output, then excludes that problem from pass@1. pi-zero-shot's plan (Phase 1 transcript schema, Phase 3 control flow, Phase 4 observability) does not mention this flag anywhere. | `orchestrator.py:336`, consumed at `multiagent.py:611-614` | Without this, any provider outage during a benchmark run biases pass@1 downward. Future evaluation claims become unverifiable. |
| C2 | **§3.3 MockBuffer / `readline()` fix not vendored or pinned** — Upstream LiveCodeBench's binary stdin mock returned line 1 on every `readline()` call; fixed with a `BytesIO`-backed view. GVS5H README §2 calls this out as the fix "every number in the paper is reported after fixing it." pi-zero-shot's Phase 4 says "subset of LCB or local fixtures" without specifying the fix. | `codebase/livecodebench/lcb_runner/evaluation/testing_util.py:94-100` | Local eval silently misgrades any candidate using `sys.stdin.buffer.readline()` for multi-line input. The paper itself notes the bug silently interacted with the v2 verifier. |
| C3 | **No `capmatch_q38.py` analog** — Qwen3.8-27B's single arm was generated at 250k cap, but the paper §3.2 reports it "cap-matched back to 128k so the row is like-for-like." pi-zero-shot's plan does not mention cap-match. | `codebase/v2-current/escalation/capmatch_q38.py` | Any future Qwen3.8-27B comparison with the manager arm (which ran at 128k) is not like-for-like. The paper's +23.4 delta depends on this procedure. |
| C4 | **No paired-pass protocol** — The paper's headline numbers are five paired passes with a paired t-test and per-pass Δ. pi-zero-shot's Phase 4 says "comparing single vs manager" with no commitment to passes, statistical test, or per-pass reporting. | Paper §2.1 Table 1, GVS5H `runs/firstparty-128k-reasoning-on-5pass/` (3,200 workspaces for the §2.1 condition alone) | A single-pass comparison cannot reproduce the paper's significance claims. p-values and Δ±SD will be missing. |
| C5 | **"Prefer no / minimal tools" opens a door the paper closes** — GVS5H workers have zero tools. They are pure chat completions. ADR 0004 §5 and Phase 3 task "Prefer minimal/no tools on role children" use "minimal," leaving room for "maybe one tool." Any tool surface breaks the "worker = single generation" invariant. | ADR 0004 §5; Phase 3 task list | A worker with even one tool becomes a multi-turn agent. The paper's "worker = fresh-context single generation" invariant is silently lost. |
| C6 | **Status line is misleading** — README:119 says "Planning complete in-repo." Reality: Phase 0 exit criteria all unchecked, ADR 0002 still Proposed, `VERIFY-LOG.md` empty. | `README.md:119` | A reader who takes the line at face value will be misled about the repo's state. Important for contributors, evaluators, and any future re-review. |

### Significant (Affects Architecture / Fidelity)

| # | Finding | Source | Impact |
|---|---------|--------|--------|
| S1 | **No provider clamp detection logic specified** — GVS5H compares the *actual* cap sent (`cur_max`), not the configured cap, when detecting provider clamping. Without this, a 400/context shrink mid-run makes every subsequent call unsatisfiable (16 attempts × full 104k-token generation each, ~7h per call). | `orchestrator.py:303-313` | Phase 5 mentions "provider quirks" generically but does not specify the clamp-detection logic. |
| S2 | **No reroute budget / wall-clock caps** — GVS5H `openai_chat` reroutes up to 16 attempts with hard wall-clock caps. Plan does not commit to "let pi-ai handle retries" or "implement reroute ourselves." | `orchestrator.py:openai_chat` | Silence here is a future failure mode: a flaky provider can hang the loop or inflate cost. |
| S3 | **`MAX_TASKS=12` cap not specified** — GVS5H caps the live task list at 12 (env `MULTIAGENT_MAX_TASKS`). Phase 1 (LedgerWorkspace) and Phase 2 (task parser) do not mention this. | `multiagent.py:72` | A faithful port should expose it as a config knob and enforce it; without it, the task list can grow unboundedly. |
| S4 | **`_strip_code` ideation invariant not specified** — GVS5H strips fenced code blocks from ideation worker's reply *before* the manager sees it, because "Ideation must contribute approaches in prose, never a finished program — otherwise the manager reads it as solved and skips the worker loop." | `multiagent.py:137-140` | Phase 2 mentions "code extraction from fenced blocks" but not the *negative* invariant. A naive port lets the manager misread ideation as a solved problem. |
| S5 | **Skip-finalize-when-done optimization not specified** — GVS5H skips finalize if the primary already marked done with a usable answer, because "a redundant finalize can ramble past the token cap and destroy a correct intermediate answer." | `multiagent.py:592-595` | Phase 3 says "finalize if needed" but doesn't specify the optimization. A naive port that always runs finalize will occasionally destroy correct solutions. |
| S6 | **Cut-off digest never into `notes.md` — not specified** — GVS5H routes the cut-off digest only to the manager-facing summary, *never* into `notes.md` ("appending a digest per cut-off is unbounded, and muse truncates often enough to reach ~400KB of notes that way"). | `multiagent.py:456-458` | Plan says "cutoff detection + summarizer call" but doesn't specify where the digest goes. A naive port would append and blow the notes bound. |
| S7 | **`ANS_RE` non-empty-answer guard not specified** — GVS5H only overwrites `answer.md` if the new reply has a parseable `ANSWER:` line (or the file is empty), so a rambling/truncated call cannot destroy a good prior answer. | `multiagent.py:192`, `:433` | Without this, a rambling worker can destroy a good prior answer. |
| S8 | **`STRICT_FORMAT` "auto" detection not specified** — GVS5H's strict-format mode auto-detects models with "muse" or "glimmer" in the name. Phase 2 mentions "strict-format mode (config flag)" but not the env name, auto mode, or model list. | `multiagent.py:59-61` | Without it, strict-format mode is a flag with no behavior on the models that actually need it. |
| S9 | **No LICENSE file** — README says "TBD (recommended: MIT)" but no `LICENSE` exists. A public repo without a LICENSE is "all rights reserved" by default. | `README.md:123` | Blocks legal use and contribution. Trivial fix. |
| S10 | **No build tooling despite committing to TypeScript** — ADR 0004 §1 says "deterministic TypeScript manager loop." `.gitignore` lists `node_modules/`, `dist/`, `.turbo/`. But no `package.json`, `tsconfig.json`, or lockfile exists. | ADR 0004; `.gitignore` | Phase 1 implementer must invent project structure from scratch. Inconsistent intent vs. artifact. |

### Moderate (Quality / Process)

| # | Finding | Source |
|---|---------|--------|
| M1 | No tests, no test runner, no CI (no `.github/` directory) — yet Phase 1, 2, 5 all promise tests. | Entire repo |
| M2 | No dependency pinning (`@earendil-works/pi-ai`, `@earendil-works/pi-agent-core`, pi-subagents versions all unspecified). | ADR 0004, Phase 3 |
| M3 | ADR 0002 status contradicts its Decision section (Proposed vs. "Prefer a real filesystem workspace… as the primary ledger implementation") and Phase 0 has a redundant task to "decide and record: real FS vs virtual ledger." | `adr/0002-filesystem-ledger.md`; `plan/phase-00-discovery-mapping.md` |
| M4 | `raw/PAPER.md` is a 21-line extract — abstract + link table only. Does not include the §3.1 four-difference list, §3.3 MockBuffer fix, or any headline numbers. The least faithful document in the repo. | `raw/PAPER.md` |
| M5 | `VERIFY-LOG.md` (the only progress-tracking mechanism) is empty — header row only. No phase exit criteria checked. | `plan/VERIFY-LOG.md` |
| M6 | Single-commit history (2026-08-29, "docs: add structured Terra architecture and implementation review"). No `CHANGELOG.md`. Looks abandoned even if it isn't. | `git log` |
| M7 | Per-role temperatures (0.3 plan, 0.4 brainstorm, 0.2 task/curate/single) not specified anywhere in plan. | `multiagent.py:_primary_plan`, `_ideation_worker`, `_worker`, `single_solve` |
| M8 | No `finish_reason` string normalization spec across providers — the cut-off summarizer depends on `finish_reason == "length"`. | `multiagent.py:447`, `:453`; `orchestrator.py` |

---

## What's Done Well

1. **The plan targets the right thing.** GVS5H v2 (not v1), correct control flow (plan → ideation → manage ↔ worker + sample tests → finalize), correct headline invariants (`MAX_ITERS=10`, sample-test hard override, notes-rewrite, size bounds, no-progress guard, cut-off summarizer, single-shot baseline). The author(s) clearly read `multiagent.py` carefully.

2. **ADR discipline is strong.** Four ADRs with clear context/decision/consequences. ADR 0001 (extension, not core fork) and ADR 0003 (sequential, single worker) are well-reasoned and well-stated. ADR 0004's "do not use" list (builtin `worker`/`reviewer`/`scout`, council modes, parallel fan-out, fork-default context) shows real understanding of the fidelity risk.

3. **Architecture mapping is faithful in spirit.** `docs/architecture.md` lines 9–20 correctly map paper primitives to Pi equivalents (workspace → `LedgerWorkspace`, manager → deterministic TS supervisor, worker → fresh one-shot, transcript.jsonl → owned by pi-zero-shot, sample-test verifier → subprocess).

4. **The pi-subagents dependency question is correctly framed.** "Package = plumbing, paper semantics stay in this repo" is exactly right. The fallback to direct `pi-ai`/RPC one-shots is sensible.

5. **Non-goals are clearly stated.** "Claiming exact paper numbers without re-running under controlled conditions" is explicitly out of scope. This is honest.

6. **Vendored reference is byte-identical.** `_upstream/GVS5H_multiagent_v2.py` md5-matches GVS5H `codebase/v2-current/escalation/multiagent.py` (`a00572b27462b57cc88b8315482d503a`). The author(s) did their homework on the source-of-truth copy.

---

## Top 5 Recommendations

1. **Vendor the §3.3 MockBuffer fix in the Phase 4 eval driver.** Pin the LiveCodeBench `release_v6` split, the `lcb100_hardest_v6.json` id list, and the `testing_util.py` `MockBuffer` fix as dependencies of any local benchmark driver. Without this, any future evaluation claim is unverifiable. (See `09-TEST-STRATEGY.md`.)

2. **Specify the `infra_exhausted`/`infra_fail` flag in the transcript schema and the grader.** Add it to Phase 1's transcript recorder (one extra field on `_record`), Phase 3's control flow (propagate it through `status_out`), and Phase 4's grader (exclude `infra_fail` rows from pass@1). This is the single most consequential gap for any future evaluation. (See `08-INTERFACES-AND-INVARIANTS.md`.)

3. **Change "prefer no / minimal tools" to "no tools, period" on workers.** Hard-code the invariant. Add a Phase 3 test that fails if any tool surface is exposed to a role call. This is a one-line change to ADR 0004 §5 with disproportionate impact on fidelity. (See `03-ADR-CRITIQUE.md`.)

4. **Mark ADR 0002 as Accepted (or rewrite it to actually be Proposed) and fix the README status line.** The current ADR-vs-Phase-0 contradiction will cost a Phase 0 implementer time. The status line "Planning complete in-repo" should read "Planning drafted; Phase 0 not yet started." (See `03-ADR-CRITIQUE.md` and `05-ROADMAP-AND-EXECUTION-CRITIQUE.md`.)

5. **Commit to a paired-pass protocol in Phase 4.** Five paired passes, paired t-test, per-pass Δ = manager − single, per-pass Δ reported alongside the aggregate. The paper's headline numbers depend on this; without it, no future claim of "we reproduce GVS5H" is meaningful. (See `09-TEST-STRATEGY.md`.)

---

## Numerical Verdict

| Dimension | Score | Justification |
|---|---|---|
| As a planning document | **7/10** | ADRs reason well; phased plan realistic; architecture mapping faithful in spirit. Misses 12 specific invariants. |
| As an implementation | **0/10** | Zero source code. Only `src/extension/.gitkeep` under `src/`. |
| As a public repo | **3/10** | No LICENSE, no tests, no CI, no package, no release. Status line misleading. |
| As a paper-fidelity claim | **5/10** | Correctly targets v2, disclaims paper-number reproduction. Misses §3.1 four-difference checklist, §3.3 fix, `infra_exhausted`, `capmatch_q38.py`, paired-pass protocol. |
| **Overall** | **4/10** | A strong plan that hasn't started executing. Earns its keep as a planning artifact but is not yet an implementation. |

---

## How to Read This Review

This review is segmented into 10 files mirroring the structure used in `MrJ55/Pi-Lisptc/review-by-GLM`. Read in order, or jump to the section you need:

| # | File | What's in it |
|---|---|---|
| 00 | `00-EXECUTIVE-SUMMARY.md` | This file. Verdict, key findings, top 5 recommendations, numerical score. |
| 01 | `01-SOURCE-AUDIT.md` | First-hand audit of all three sources: pi-zero-shot (25 files), GVS5H (117 mirrored files), arxiv paper (PDF + HTML + LaTeX). |
| 02 | `02-ARCHITECTURE-REVIEW.md` | Architecture of pi-zero-shot's plan, the control-flow diagram, and the 12-line gap table against GVS5H v2. |
| 03 | `03-ADR-CRITIQUE.md` | Detailed critique of ADRs 0001–0004: what's right, what's wrong, what to change. |
| 04 | `04-GVS5H-FEATURE-MAPPING.md` | Feature-by-feature mapping: every plan claim → GVS5H source line, with status (✅/⚠/❌/🚫). |
| 05 | `05-ROADMAP-AND-EXECUTION-CRITIQUE.md` | Critique of the phased plan, exit criteria, and execution state. What's done, what's missing. |
| 06 | `06-RISK-REGISTER.md` | Risks with mitigations, ranked by impact × probability. |
| 07 | `07-IMPLEMENTATION-PRIORITY.md` | Recommended execution order with effort estimates. |
| 08 | `08-INTERFACES-AND-INVARIANTS.md` | The hard invariants a faithful port must preserve, with GVS5H source citations. |
| 09 | `09-TEST-STRATEGY.md` | Test strategy including the §3.3 fix, paired-pass protocol, cap-match, and regression tests. |

Supporting evidence (per-source ingestion analyses produced by parallel subagents) is in `supporting-evidence/`.
