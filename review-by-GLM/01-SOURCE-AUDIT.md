# Review-by-GLM — Source Audit

**Reviewer:** GLM (Z.ai), independent audit
**Date:** 2026-08-29
**Sources audited:** `MrJ55/pi-zero-shot` @ `cc5ae55` · `slee-persis/GVS5H` @ `6d7a143b` · arXiv:2608.26480 (PDF + HTML + LaTeX source)
**Method:** Parallel ingestion via three general-purpose subagents. First-hand reading of every markdown file in pi-zero-shot; full read of GVS5H `multiagent.py` (643 lines) and `orchestrator.py` (697 lines); first 200 lines + targeted greps of the arxiv paper text. Twelve line-level verifications performed personally.

---

## 1. Source 1 — `MrJ55/pi-zero-shot` @ `cc5ae55`

### 1.1 Provenance

| Field | Value |
|---|---|
| URL | https://github.com/MrJ55/pi-zero-shot |
| Default branch | `main` |
| Single commit | `cc5ae55` (2026-08-29 16:39:06 +0200), message: "docs: add structured Terra architecture and implementation review" |
| License | **TBD** — README:123 says "TBD (recommended: MIT)". No `LICENSE` file present. |
| Primary language | None declared. **No source code.** `.gitignore` patterns (`node_modules/`, `dist/`, `.turbo/`) imply Node/TS. |
| Stars/forks | Unknown — GitHub REST API rate-limited (60/60 unauthenticated calls used). |
| Tracked files | 25 (4 directories). ~600 lines of Markdown, 0 lines of code. |

### 1.2 Directory tree (excluding `review-by-Terra/` per the user's instruction)

```
pi-zero-shot/
├── .gitignore
├── README.md
├── adr/
│   ├── 0001-use-extension-not-core-fork.md
│   ├── 0002-filesystem-ledger.md
│   ├── 0003-sequential-manager-worker.md
│   └── 0004-subagents-as-spawn-helper.md
├── docs/
│   ├── 00-problems-and-goals.md   (stub — 5 lines)
│   ├── 01-source-analysis.md
│   ├── 02-ecosystem-shortcuts.md
│   ├── README.md
│   ├── architecture.md
│   └── plan.md                    (redirect to ../plan/)
├── plan/
│   ├── README.md
│   ├── VERIFY-LOG.md              (empty)
│   ├── phase-00-discovery-mapping.md
│   ├── phase-01-ledger-primitives.md
│   ├── phase-02-prompts-parsing.md
│   ├── phase-03-manager-worker-loop.md
│   ├── phase-04-observability-packaging.md
│   └── phase-05-hardening.md
├── raw/
│   ├── PAPER.md                   (21-line extract)
│   └── README.md
├── scripts/
│   └── README.md                  (empty)
├── src/
│   └── extension/
│       └── .gitkeep               (1-line comment — only file under src/)
└── _upstream/
    └── GVS5H_multiagent_v2.py     (643 lines, md5-verified byte-identical to GVS5H source)
```

### 1.3 Files read first-hand

Every markdown file. The `.gitkeep` placeholder. The `.gitignore`. The vendored `_upstream/GVS5H_multiagent_v2.py`.

### 1.4 What this repo actually contains

- **README.md** (124 lines): stated goals G1–G6, non-goals, architecture diagram (ASCII art), phased plan summary, ADR index, upstream references, status line "Planning complete in-repo. Implementation follows `plan/phase-*.md` in order." (misleading — see `05-ROADMAP-AND-EXECUTION-CRITIQUE.md`).
- **Four ADRs**: 0001 (extension not core fork — Accepted), 0002 (filesystem ledger — Proposed), 0003 (sequential manager-worker — Accepted for MVP), 0004 (pi-subagents as spawn helper — Accepted).
- **Six phase plans**: Phase 0 (Discovery & mapping), Phase 1 (Core ledger primitives), Phase 2 (Role prompts & parsing), Phase 3 (Manager-worker loop as extension), Phase 4 (Observability & packaging), Phase 5 (Hardening & polish).
- **`raw/PAPER.md`**: 21-line extract. Title, authors, arxiv ID, abstract (copied verbatim from arxiv page), and a 4-row link table. Does NOT extract §3.1's four-difference list, §3.3's MockBuffer fix, the experimental setup, or any headline numbers.
- **`_upstream/GVS5H_multiagent_v2.py`**: the actual GVS5H v2 reference scaffold, vendored for cross-reference. md5 `a00572b27462b57cc88b8315482d503a` — byte-identical to GVS5H `codebase/v2-current/escalation/multiagent.py`. This is the strongest evidence that the author(s) did their homework on the source-of-truth.

### 1.5 What this repo does NOT contain

- Source code (no `.ts`, `.js`, `.py` files under `src/`).
- `package.json`, `tsconfig.json`, lockfile.
- `LICENSE` file.
- `pyproject.toml`/`requirements.txt` (would apply if this were Python — it isn't).
- Tests, test runner, test fixtures.
- `.github/workflows/` (no CI).
- `CHANGELOG.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
- Any dependency pin (`@earendil-works/pi-ai`, `@earendil-works/pi-agent-core`, `nicobailon/pi-subagents` versions all unspecified).
- Issues, PRs (rate-limited from retrieval).

### 1.6 Notable observations

- The single commit added the entire repo *and* a `review-by-Terra/` artifact (not inspected, per the user's instruction). This is an unusual independence signal: the planning repo and a parallel review artifact were created in the same commit, suggesting a parallel review effort rather than iterative development.
- The repo was created 2 days after the paper's arxiv date (paper 2026-08-27, repo 2026-08-29). Consistent with a same-week porting attempt.
- `docs/00-problems-and-goals.md` is a 5-line stub saying "See the root README.md for the canonical list." It notes the file exists to "follow the same numbered-background pattern as Pi-Lisptc." This indicates the docs structure was copied from another project rather than designed for this one. Not wrong, but worth noting.

---

## 2. Source 2 — `slee-persis/GVS5H` @ `6d7a143b`

### 2.1 Provenance

| Field | Value |
|---|---|
| URL | https://github.com/slee-persis/GVS5H |
| Single commit | `6d7a143b` (2026-08-27 16:39:11 -0400), message: "Enhance README with Fable 5 pricing and GPU info" |
| Author | `slee-persis <slee@persisholdings.com>` — matches corresponding author Simon (Sang Won) Lee's email in the paper |
| License | **No top-level LICENSE.** The bundled `codebase/livecodebench/LICENSE` is MIT (Copyright (c) 2024 LiveCodeBench). Paper bundle code itself (everything under `codebase/v1-be9dfa2/`, `codebase/v2-current/`, `paper/`) ships with no license grant. |
| Primary language | Python (scaffold + benchmark harness), LaTeX (paper), Bash (run drivers), JSON (frozen problem IDs and graded results). |
| Tracked files | 29,395 (~1 GB; ~29k of these are per-problem workspace files under `runs/`). |
| Local mirror | 117 files at `/home/z/my-project/review-by-GLM/sources/GVS5H/` (everything except the bulk `runs/` tree). |

### 2.2 Directory tree (what was mirrored)

```
GVS5H/
├── README.md                                   (217 lines — the most informative doc)
├── .gitignore
├── codebase/
│   ├── v1-be9dfa2/escalation/                  (original scaffold, §2.4 OpenRouter set)
│   │   ├── multiagent.py                       (397 lines)
│   │   ├── orchestrator.py                     (349 lines)
│   │   └── run_bench.py                         (582 lines)
│   ├── v2-current/escalation/                  (updated scaffold, §2.1-§2.3 first-party arms)
│   │   ├── multiagent.py                       (643 lines — THE primary reference)
│   │   ├── orchestrator.py                     (697 lines — provider routing, clamp detection)
│   │   ├── run_bench.py                         (601 lines)
│   │   ├── regrade.py                           (130 lines — §3.3 fix rescore)
│   │   ├── capmatch_q38.py                      (127 lines — 250k→128k truncation)
│   │   ├── lcb100_hardest_v6.json               (100 pinned question_ids)
│   │   ├── lcb100_5pass_table.md               (raw pass@1 table)
│   │   └── run_bench_script/                    (plot scripts + run drivers)
│   └── livecodebench/                          (vendored benchmark harness)
│       ├── lcb_runner/evaluation/testing_util.py  (THE §3.3 MockBuffer fix — lines 94-100)
│       ├── lcb_runner/runner/                     (provider runners)
│       ├── lcb_runner/prompts/                    (code generation prompts)
│       └── lcb_runner/benchmarks/                 (code_generation, etc.)
├── paper/                                       (20 files: TeX, PDF, 7 fig-*.tex, plots/*.png)
│   └── zero_shot_self_orchestration_..._2026-08-25.tex  (1434 lines — the .tex source)
└── runs/                                        (NOT bulk-mirrored; ~1 GB)
    ├── firstparty-128k-reasoning-on-5pass/      (3,200 workspaces — §2.1)
    ├── fable5-128k-reasoning-on-5pass/         (500 workspaces — Fable 5 single-only)
    ├── 16k-reasoning-off-5pass/                (4,500 workspaces — §2.4)
    ├── 128k-reasoning-off-1pass/               (800 workspaces — §2.4)
    ├── 128k-reasoning-on-1pass/                (901 workspaces — §2.4)
    └── q9-reasoning-on-archived/               (limitation evidence — §4.5)
```

### 2.3 What GVS5H is, and what it isn't

**GVS5H is NOT a training repo.** There are no trained weights, no checkpoints, no loss functions, no DDP/FSDP/DeepSpeed. The "model" in this paper is a **manager–worker prompt + control-flow scaffold** over hosted LLMs (Qwen3.8-Max via DashScope, GPT-5.6-Luna/Terra via OpenAI, Claude Opus 5 + Fable 5 via Anthropic). It is a *research-artifact bundle*: the paper .tex/.pdf, two versions of the scaffold (v1-be9dfa2 and v2-current), the vendored LiveCodeBench harness with the §3.3 fix, 73 graded `*.regraded.json` files per condition, ~11k per-problem workspace files per condition, and the plot scripts that recompute every figure from those JSONs.

This matters for pi-zero-shot: any port of GVS5H is, by construction, a port of `multiagent.py` + `orchestrator.py` + the LiveCodeBench harness — not a port of model code. The "zero-shot" in the paper title means exactly that: zero training, no fine-tuning, no per-benchmark tuning.

### 2.4 Files read first-hand (from GVS5H)

- **`codebase/v2-current/escalation/multiagent.py`** — full 643-line read plus targeted greps. This is the single most important file for the pi-zero-shot review.
- **`codebase/v2-current/escalation/orchestrator.py`** — targeted reads (provider dispatch at `:487-542`, clamp detection at `:303-313`, infra-exhausted flag at `:336`).
- **`codebase/livecodebench/lcb_runner/evaluation/testing_util.py`** — targeted grep verifying the §3.3 MockBuffer fix at lines 94-100 (`BytesIO`-backed, comment says "upstream's readline returned line 1 every call").
- **`codebase/v2-current/escalation/lcb100_hardest_v6.json`** — verified to be the 100-question frozen id list.
- **`README.md`** — 217 lines, the most informative single document. Confirms the v1→v2 four-difference table matches paper §3.1 verbatim. Confirms the §3.3 fix. Confirms the cap-match procedure for Qwen3.8-27B. Confirms every figure is recomputed from `*.regraded.json`.
- **`_meta/sample_workspace/{task,plan,notes,tasks,solution}.md/json`** — real per-problem workspace files (the Fenwick-tree problem). Confirms the workspace file format pi-zero-shot's plan describes.

### 2.5 Twelve first-hand line-level verifications

Performed personally (not just trusting subagent summaries):

1. **Vendored copy is byte-identical.** md5 `a00572b27462b57cc88b8315482d503a` for both `_upstream/GVS5H_multiagent_v2.py` and `codebase/v2-current/escalation/multiagent.py`.
2. **`MAX_ITERS=10`.** `multiagent.py:42` (env `MULTIAGENT_MAX_ITERS`, default `"10"`).
3. **`MAX_PLAN_CHARS=4000`.** `multiagent.py:197`.
4. **`MAX_ANSWER_CHARS=20000`.** `multiagent.py:194`.
5. **Notes REWRITE-not-append.** `multiagent.py:18-20` (comment) + `:450` (`_write`, not `_append`).
6. **Notes bound = `MAX_PLAN_CHARS * 2 = 8000`.** `multiagent.py:281` and `:450`.
7. **Sample-test hard override.** `multiagent.py:581-587` — the code does *not* merely instruct the manager; it *overrides* a `"done"` verdict when samples fail.
8. **No-progress guard.** `multiagent.py:558-563` — re-issuing the same task ends the loop.
9. **Cut-off summarizer.** `multiagent.py:353-371` (`_summarize_cutoff`).
10. **Single-shot baseline.** `multiagent.py:622-643` (`single_solve`).
11. **`infra_exhausted` flag.** `orchestrator.py:336` (set), `multiagent.py:611-614` (consumed as `infra_fail`).
12. **Provider clamp detection.** `orchestrator.py:303-313` — compares against `cur_max` (cap actually sent), not `CLOUD_MAX_TOKENS`.
13. **§3.3 MockBuffer fix.** `testing_util.py:94-100` — `BytesIO`-backed so reads advance position.
14. **Control-flow order.** `multiagent.py:547-595` (`multiagent_solve`) — plan → ideation → manage ↔ worker (+ sample tests) → finalize.

### 2.6 GVS5H's own reproducibility weaknesses (which pi-zero-shot does NOT inherit but does NOT address either)

- No top-level LICENSE.
- No `pyproject.toml`/`requirements.txt` for the scaffold.
- No tests/linting/CI for the scaffold.
- Hardcoded `/home/persis/model-test` paths in every run driver.
- Default `--ids-file` points to a non-existent `hard100.json` (the real one is `lcb100_hardest_v6.json`).
- Single commit on default branch — no incremental history.
- Transcripts git-ignored (~1.4 GB, not vendored).

pi-zero-shot's plan does not call out any of these. A faithful port would either inherit them (bad) or explicitly fix them (good). Currently it does neither.

---

## 3. Source 3 — arXiv:2608.26480

### 3.1 Bibliographic info

| Field | Value |
|---|---|
| Title | Zero-Shot Self-Orchestration with Ledger-Based Control for Improved LLM Coding Performance |
| arXiv ID | 2608.26480v1 [cs.MA] |
| Submission date | 27 Aug 2026 |
| Authors | Victor Gao¹; Vida Khosrowshahi¹; Ali Khosrowshahi¹; Xihao Sun¹; Juhyun Lee; Simon (Sang Won) Lee¹† |
| Affiliation | ¹ Persis Capital Inc. |
| Corresponding author | Simon (Sang Won) Lee, Ph.D. — slee@persisholdings.com (matches GVS5H owner `slee-persis`) |
| Code link | https://github.com/slee-persis/GVS5H |
| Paper license | CC BY 4.0 (per arXiv page) |

### 3.2 Files ingested first-hand

| File | Source | Size | md5 |
|---|---|---|---|
| `paper.pdf` | arXiv `pdf/2608.26480` (HTTP 200) | 1,452,876 B | `52576a74f3278a57b39fa2d7b97cde0d` |
| `paper.html` | arXiv `html/2608.26480` (HTTP 200) | 286,907 B | `ece8ec6a65cbb1f601b6119d74b8291a` |
| `paper.txt` | `pdftotext -layout` of the above | 86,082 B / 1,119 lines | regenerated, diffed identical |
| `abs.html` | arXiv `abs/2608.26480` (fresh fetch) | 44,439 B | — |
| `.tex source` | Task ID 4 mirror at `sources/GVS5H/paper/..._2026-08-25.tex` | 1,434 lines | cross-checked against PDF — byte-identical content |

### 3.3 Core method (paper §1.2 + §3.1)

A **zero-shot, training-free** manager–worker scaffold. No checkpoints, no fine-tuning, no per-benchmark tuning. State lives in five shared filesystem files: `task.md`, `plan.md`, `tasks.json`, `notes.md`, `solution.py` (or `answer.md` for math).

Six-step control flow:
1. Manager writes plan + seed tasks.
2. First worker brainstorms (no code, appends to `notes.md`).
3. Manager curates task list.
4. Fresh worker executes one task and rewrites `solution.py`.
5. **Verifier runs public sample tests** — pass/fail verdict is ground truth; a failing run overrides a "done" verdict and forces a fix-or-switch task.
6. Finalizer emits definitive solution only if loop ends without a clean sign-off.

Guards: `MAX_ITERS=10`, no-progress guard, cut-off summarizer, size-bounded workspace feeds.

Temperatures: 0.3 plan, 0.4 brainstorm, 0.2 task/curate/single-baseline.

### 3.4 The four v1→v2 named differences (§3.1 — verbatim)

| | v1 | v2 |
|---|---|---|
| `MULTIAGENT_MAX_ITERS` | 4 | 10 |
| Sample-test verifier (§3.1 step 5) | absent | present |
| Cut-off summarizer | absent | present |
| Size bounds on workspace files | absent | present |

All four apply only to the manager arm. The single-call baseline is one call under either version, so v1-vs-v2 deltas are *not* strictly comparable — which is why the paper reports the OpenRouter model set as its own condition (§2.4) rather than pooling with §2.1.

### 3.5 §3.3 MockBuffer / `readline()` fix

The LiveCodeBench harness executes candidates *in-process* with `sys.stdin` mocked. Upstream's binary view implemented `readline()` as the stateless expression `inputs.split(b"\n")[0]` — returns line 1 every call. Fixed by replacing it with a `BytesIO`-backed view so reads advance position. Every stored generation was re-scored (no model re-run). Only one §2.4 cell moves (Kimi 82 → 83).

**Critical interaction:** this bug *silently poisoned the v2 verifier's external signal* — the verifier runs the candidate as a real subprocess where `readline()` works correctly, so the manager was told "passed" for programs the hidden grader marked wrong. The fix means every paper number is reported *after* the correction.

### 3.6 Headline results

| Model | Serving | Single | Manager | Δ | Per-pass Δ (5 passes) |
|---|---|---|---|---|---|
| Claude Fable 5 | Anthropic | 87.4 ± 1.1 | (single-only) | — | — |
| GPT-5.6-Terra | OpenAI | 77.0 ± 1.0 | 85.0 ± 1.0 | +8.0 ± 0.0 | +8, +8, +8, +8, +8 |
| GPT-5.6-Luna | OpenAI | 67.2 ± 4.3 | 77.8 ± 2.0 | +10.6 ± 5.1 | +17, +7, +13, +4, +12 |
| Qwen3.8-27B | local vLLM | 63.0 ± 4.1 | 86.4 ± 2.7 | +23.4 ± 6.6 | +15, +20, +29, +22, +31 |

Opus-5 with manager: 91% (the highest score in the study, 1 pass). Manager roughly triples the bill but buys accuracy more cheaply than upgrading models: GPT-5.6-Terra + manager (85.0) ≈ Fable 5 single (87.4, p=0.59) at 1/5 the price ($11.71 vs $61.11 per 100-problem pass, p < 10⁻⁴).

### 3.7 The paper is a map, not a spec

The paper is a sufficient *map* but not a sufficient *spec*. Things a reimplementer must read the GVS5H code to nail:

- Exact size limits on workspace feeds (paper says "size-bounded"; actual `MAX_PLAN_CHARS=4000` is in code).
- The four sections of the worker's output contract.
- The cut-off summarizer's call budget.
- Per-call `max_tokens` for manager-side calls.
- RNG seeds (not stated).
- Hardware/cluster size (not stated).
- The "subagent preamble" wrapping.

pi-zero-shot's plan correctly disclaims paper-number reproduction in its non-goals ("Claiming exact paper numbers without re-running under controlled conditions"). It does not, however, vendor the code that resolves these gaps — which is what a faithful port needs to do.

---

## 4. Source audit verdict

The three sources together tell a clear story: pi-zero-shot is a planning attempt to port a real, well-defined reference implementation (`slee-persis/GVS5H` v2) of a real, well-defined paper (arXiv:2608.26480) into a TypeScript Pi extension. The plan is grounded in the right source (the vendored `multiagent.py` is byte-identical to GVS5H's). The plan captures the right headline invariants. The plan misses 12 specific subtler invariants that any faithful port must preserve.

The next section (`02-ARCHITECTURE-REVIEW.md`) details those 12 gaps with file:line citations.
