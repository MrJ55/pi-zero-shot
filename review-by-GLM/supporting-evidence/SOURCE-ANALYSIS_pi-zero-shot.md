# Ingestion Analysis — `MrJ55/pi-zero-shot`

> Prepared by Task ID 2 (general-purpose ingestion agent). The parent agent
> will use this as grounding for a critical, code-grounded review.
>
> **Independence note:** No `review-*` directories were read or listed, in
> this repo or in the working tree. The repo *contains* a `review-by-Terra/`
> directory; per the hard constraint, it was excluded from enumeration,
> cloning, and analysis entirely.

---

## A. Repo Overview

| Field | Value |
|-------|-------|
| Repo | `MrJ55/pi-zero-shot` |
| URL | https://github.com/MrJ55/pi-zero-shot |
| Default branch | `main` |
| License | **TBD** — README states "TBD (recommended: MIT …)" (`README.md:123`). No `LICENSE` file present. |
| Primary language | None declared in code — there is **no source code**. `.gitignore` suggests a Node/TS project (`node_modules/`, `dist/`, `.turbo/`). |
| Stars / forks / watchers | **Unknown** — GitHub REST API returned `403 rate limit exceeded` for this sandbox IP (60/60 unauthenticated requests used; reset window not waited out). Could not be retrieved. |
| Created / last push | Single commit dated **2026-08-29 16:39:06 +0200** (see §H). `git log` is the only history available; API metadata fields unavailable. |
| Repo size (clone) | 25 tracked files, 4 directories; total source ~600 lines of Markdown, ~0 lines of code. |
| Open issues / PRs | **Unknown** — GitHub API rate-limited. `git log` shows no branch/PR metadata (single commit, shallow clone). No `ISSUES`/`PR` artifacts in-tree. |

### Top-level directory tree (actual, excluding `review-by-Terra/` per constraint)

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
│   ├── 00-problems-and-goals.md
│   ├── 01-source-analysis.md
│   ├── 02-ecosystem-shortcuts.md
│   ├── README.md
│   ├── architecture.md
│   └── plan.md
├── plan/
│   ├── README.md
│   ├── VERIFY-LOG.md
│   ├── phase-00-discovery-mapping.md
│   ├── phase-01-ledger-primitives.md
│   ├── phase-02-prompts-parsing.md
│   ├── phase-03-manager-worker-loop.md
│   ├── phase-04-observability-packaging.md
│   └── phase-05-hardening.md
├── raw/
│   ├── PAPER.md
│   └── README.md
├── scripts/
│   └── README.md            (placeholder only, 3 lines)
└── src/
    ├── README.md            (suggested layout, no code)
    └── extension/
        └── .gitkeep         (1 line: "# Placeholder for Pi extension entry point")
```

**There are zero `.py`, `.ts`, `.js`, `.json`, `.yaml`, `.toml`, `.cfg`,
`requirements.txt`, `package.json`, `pyproject.toml`, `setup.py`,
`Dockerfile`, `Makefile`, or `.github/workflows/*` files in the repo.**

The only "binary"-ish asset is `.gitkeep`. No checkpoints, no configs, no
scripts.

---

## B. Stated Goals

The README (`README.md:1-3`) defines the project as:

> **"pi-zero-shot — Zero-Shot Self-Orchestration with Ledger-Based Control**
> for the [earendil-works/pi](https://github.com/earendil-works/pi) agent
> harness. Port of the manager–worker scaffold from: *Zero-Shot
> Self-Orchestration with Ledger-Based Control for Improved LLM Coding
> Performance*, arXiv: 2608.26480 … to Pi's extensible architecture
> (extension / skill), preserving the training-free, zero-shot,
> shared-filesystem-ledger design."

Six explicit goals are listed (`README.md:27-34`):

> | Goal | Success signal |
> |------|----------------|
> | **G1** Faithful control flow | Sequential manager ↔ one worker, sample-test gate, finalize, same invariants as GVS5H v2 |
> | **G2** Short worker contexts | Workers see only ledger state (plan/notes/solution/task), not full Pi session history |
> | **G3** Inspectable ledger | `task.md`, `plan.md`, `notes.md`, `solution.py`, `tasks.json`, `transcript.jsonl` produced and visible |
> | **G4** Extension, not core fork | Ships as Pi extension/skill; classic Pi remains available |
> | **G5** Single-shot baseline | A/B comparison against plain single-call remains easy |
> | **G6** Provider-agnostic | Uses `@earendil-works/pi-ai`; no hard dependency on one vendor |

Stated status (`README.md:117-119`):

> "Planning complete in-repo. Implementation follows `plan/phase-*.md` in
> order."

Non-goals (`README.md:36-41`) explicitly disclaim: changing Pi core agent
loop, learned/trained orchestrators, full multi-agent debate/MoA, and
"Claiming exact paper numbers without re-running under controlled
conditions."

---

## C. Architecture

### Directory layout & module responsibilities

The repo is **planning-only**. There is no executable architecture — only
a *planned* one:

- **`README.md`** — Project charter, problem statement, goal table, ASCII
  control-flow diagram, repo layout, phased plan summary, upstream
  references.
- **`adr/`** — Four Architecture Decision Records (0001–0004) recording
  design choices: extension-not-fork, filesystem ledger, sequential
  manager+worker, pi-subagents as optional spawn helper.
- **`docs/`** — Background docs: problems/goals pointer, GVS5H source
  analysis, ecosystem shortcut survey, paper→Pi primitive mapping, plan
  pointer.
- **`plan/`** — Six-phase implementation plan (phase-00 through phase-05)
  with goals, background, task checklists, exit criteria, verification.
  Plus an empty `VERIFY-LOG.md` (table header only, no rows).
- **`raw/`** — Local extract of the paper (abstract + metadata) and
  README pointing to upstream `slee-persis/GVS5H` artifacts.
- **`scripts/`** — 3-line placeholder README; no scripts.
- **`src/`** — 14-line README describing a *suggested* future layout
  (`extension/`, `ledger/`, `prompts/`, `parse/`, `loop/`). The only
  actual file is `src/extension/.gitkeep` containing the comment
  `"# Placeholder for Pi extension entry point"`.

### Planned module responsibilities (from `src/README.md:7-14`)

```
src/
├── extension/          # Pi extension entry
├── ledger/             # LedgerWorkspace, transcript, sample tests
├── prompts/            # Role system prompts
├── parse/              # Section / task / code parsers
└── loop/               # Manager–worker state machine
```

None of these directories exist beyond the placeholder.

### Planned data flow (from `README.md:45-64`, `docs/architecture.md:47-54`)

```
User coding task
  → Manager writes plan.md + seed tasks
  → Ideation worker writes notes.md (approaches only, no code)
  → Loop: manager curates tasks → worker executes (fresh context) → sample tests → manager reviews
  → Stop on "done" (non-empty artifact + samples pass) or MAX_ITERS
  → Finalize worker if needed → graded artifact + transcript.jsonl
```

### Frameworks / libraries (planned, not present)

The docs repeatedly reference but never install:

- **`@earendil-works/pi-ai`** — Pi's provider abstraction (`README.md:34`,
  `docs/architecture.md:15`, `adr/0004-subagents-as-spawn-helper.md:33`).
- **`@earendil-works/pi-agent-core`** — Pi core agent (`plan/phase-00-discovery-mapping.md:20`).
- **`nicobailon/pi-subagents`** — Optional spawn helper, install via
  `pi install npm:pi-subagents` (`docs/02-ecosystem-shortcuts.md:11`).
- Implementation language is **TypeScript** per ADR 0004
  (`adr/0004-subagents-as-spawn-helper.md:22` "deterministic TypeScript
  manager loop") and `plan/phase-01-ledger-primitives.md:15`
  ("`LedgerWorkspace` (TypeScript)"). The `.gitignore` (`node_modules/`,
  `dist/`, `.turbo/`) corroborates a TS/Node toolchain.

**There is no `package.json`, `tsconfig.json`, `pnpm-lock.yaml`, or any
other dependency manifest.** No dependency is pinned, declared, or
installed.

### Checkpoint vs. code

There is **no model checkpoint** (the paper itself is training-free, so
none is expected). There is also **no code**. There is only a `.gitkeep`
placeholder under `src/extension/`.

### Separation of training vs. inference

N/A — the underlying paper is training-free ("zero-shot
self-orchestration"), and the port is purely an inference-time
orchestration scaffold. The plan does describe a clear separation
between the **manager state machine** (deterministic, owned by
pi-zero-shot) and the **role calls** (LLM generations via pi-subagents
or pi-ai) — see `docs/architecture.md:24-36`.

---

## D. Key Files & Code Snippets

There are **no source code files** in this repo. Every file is Markdown
or a `.gitkeep` placeholder. For each significant file, the "key
functions/classes" columns are necessarily empty; instead I report
notable structural content and any concrete identifiers (function names,
constants, file paths) that the docs commit to.

### `README.md` (123 lines)
- **Purpose:** Project charter.
- **Key identifiers committed:** `LedgerWorkspace` (`README.md:91`),
  `pi-zero-shot state machine` (`README.md:67`), `context: "fresh"` spawn
  mode (`README.md:68`), `GVS5H multiagent.py (v2)` reference
  (`README.md:71`).
- **Notable:** ASCII architecture diagram (`README.md:45-64`); goal table
  G1–G6 (`README.md:27-34`); phased plan summary (`README.md:86-96`);
  license field explicitly "TBD" (`README.md:123`).

### `adr/0001-use-extension-not-core-fork.md` (27 lines)
- **Purpose:** Justify shipping as a Pi extension rather than forking Pi core.
- **Status:** Accepted.
- **Notable:** "Pure external script that shells out to pi → weaker
  integration and observability" listed as rejected alternative.

### `adr/0002-filesystem-ledger.md` (26 lines)
- **Purpose:** Prefer real filesystem workspace over Pi session-tree-only virtual ledger.
- **Status:** **Proposed** (not yet Accepted) — `adr/0002-filesystem-ledger.md:5`.
- **Notable:** Finalize status deferred to Phase 0; `plan/phase-00-discovery-mapping.md:40`
  says "update ADR 0002 status if needed."

### `adr/0003-sequential-manager-worker.md` (25 lines)
- **Purpose:** Lock the MVP to sequential manager + single worker (paper style).
- **Status:** "Accepted for MVP" (`adr/0003-sequential-manager-worker.md:5`).

### `adr/0004-subagents-as-spawn-helper.md` (62 lines, longest ADR)
- **Purpose:** Scope `pi-subagents` to spawn-helper-only.
- **Status:** Accepted.
- **Key invariants committed** (`adr/0004-subagents-as-spawn-helper.md:26-32`):
  - `context: "fresh"` per role call
  - concurrency = 1
  - same model for every role
  - paper system prompt + user message = ledger injection only
  - prefer no/minimal tools (generation, not multi-turn edit agent)
  - sample tests = external subprocess, not a "verifier agent"
- **Notable:** Explicitly bans `pi-agents-team`, `pi-workflows`,
  `pi-extensible-workflows`, `pinot-pi`, `paseo` from the replication path
  (also `docs/02-ecosystem-shortcuts.md:20-26`).
- **Key quote — the only "implementation language" commitment in the repo:**
  > "pi-zero-shot owns the control flow — deterministic TypeScript manager
  > loop matching GVS5H v2 (`plan → ideation → manage ↔ worker + sample
  > tests → finalize`)." — `adr/0004-subagents-as-spawn-helper.md:22`

### `docs/01-source-analysis.md` (44 lines)
- **Purpose:** Map upstream GVS5H paths to roles.
- **Key claims (verifiable against upstream):**
  - `codebase/v2-current/escalation/multiagent.py` = v2 scaffold (paper §2.1–§2.3)
  - `codebase/v2-current/escalation/orchestrator.py` = multi-provider chat
  - `codebase/v1-be9dfa2/escalation/` = v1 scaffold
  - `codebase/livecodebench/` = benchmark harness
  - `runs/` = full transcripts
- **v1 vs v2 differences (`docs/01-source-analysis.md:22-31`):**
  - `MULTIAGENT_MAX_ITERS`: v1=4, v2=10
  - v2 adds: sample-test verifier, cut-off summarizer, size bounds on workspace files
- **Per-problem workspace layout:** `<hash>/{task.md,plan.md,tasks.json,notes.md,solution.py,transcript.jsonl}`
  (`docs/01-source-analysis.md:35-42`).

### `docs/architecture.md` (66 lines)
- **Purpose:** Paper primitive → Pi primitive mapping.
- **Mapping table** (`docs/architecture.md:11-20`) commits to:
  - `LedgerWorkspace` (real FS preferred) for shared workspace
  - "Deterministic supervisor in pi-zero-shot (TS state machine)" for manager
  - `pi-subagents context:"fresh"` OR direct `pi-ai` / RPC for worker role calls
  - Hard size bounds; notes **rewrite** semantics
  - Sample-test verifier as subprocess
- **Control-flow pseudocode** (`docs/architecture.md:47-54`) restates
  GVS5H `multiagent_solve`.

### `plan/phase-01-ledger-primitives.md` (34 lines)
- **Purpose:** First phase that would write real code.
- **Concrete types/tasks committed** (`plan/phase-01-ledger-primitives.md:15-23`):
  - `LedgerWorkspace` (TypeScript)
  - Atomic read/write for `task.md`, `plan.md`, `notes.md`, `solution.py`/`answer.md`, `tasks.json`, `transcript.jsonl`
  - Hard size bounds (mirror paper `MAX_PLAN_CHARS` and notes cap)
  - Notes **rewrite** semantics (not pure append)
  - Transcript recorder: JSONL with role, request, response, reasoning, tokens, finish_reason, provider metadata
  - Sample-test runner: subprocess, returns `{ran, passed, total, fail}`
- **Notable hardcoded constant reference:** `MAX_PLAN_CHARS` is cited
  from the upstream paper; upstream `multiagent.py:197` defines
  `MAX_PLAN_CHARS = 4000` (verified against the upstream file fetched
  for cross-check).

### `plan/phase-02-prompts-parsing.md` (30 lines)
- **Purpose:** Port paper prompts + parsers.
- **Concrete functions to port** (`plan/phase-02-prompts-parsing.md:9`):
  `_primary_plan`, `_ideation_worker`, `_primary_manage`, `_worker`,
  `_summarize_cutoff`, `_sections`, `_parse_tasks`, `_extract_py`.
- All eight of these function names were verified to exist in the
  upstream `multiagent.py` (functions at lines 224, 254, 287, 371, 353,
  143, 176, 171 respectively — see `_upstream/GVS5H_multiagent_v2.py`
  mirrored alongside this analysis).

### `plan/phase-03-manager-worker-loop.md` (42 lines)
- **Purpose:** Ship the actual extension.
- **Config knobs planned** (`plan/phase-03-manager-worker-loop.md:17`):
  model, max iters, workspace root, sample-test enable, strict format,
  `usePiSubagents: true|false`.
- **RoleLauncher interface** with two implementations (pi-subagents vs
  pi-ai/RPC fallback) (`plan/phase-03-manager-worker-loop.md:19-22`).
- **Hard-override rule** (`plan/phase-03-manager-worker-loop.md:24`):
  "Sample-test feedback injected into manager prompt; hard override if
  manager says done while samples fail."

### `plan/phase-04-observability-packaging.md` (28 lines)
- **Purpose:** TUI visibility, cost accounting, packaging.
- **Notable:** "Minimal benchmark driver (subset of LCB or local
  fixtures) comparing single vs manager" (`plan/phase-04-observability-packaging.md:16`)
  — this is the *only* place in the repo that mentions actually
  reproducing paper numbers, and it's scoped to "minimal/subset," not
  the paper's full 100-problem LiveCodeBench hard set.

### `plan/phase-05-hardening.md` (30 lines)
- **Purpose:** Provider quirks, parser fallbacks, optional parallelism.
- **Notable deferred items:** parallel workers (post-MVP),
  math-problem `answer.md` variant — both explicitly optional
  (`plan/phase-05-hardening.md:17-18`).

### `raw/PAPER.md` (21 lines)
- **Purpose:** Local extract of the paper (title, authors, abstract,
  links).
- **Notable bibliographic claims** (`raw/PAPER.md:3-6`):
  - Authors: Victor Gao, Vida Khosrowshahi, Ali Khosrowshahi, Xihao Sun,
    Juhyun Lee, Simon (Sang Won) Lee
  - Affiliation: Persis Capital Inc. / Persis Holdings
  - arXiv 2608.26480, v1, 27 Aug 2026
  - Official bundle: `slee-persis/GVS5H`
- **Verification:** These claims were independently confirmed by fetching
  `https://arxiv.org/abs/2608.26480` — the page returns matching
  `citation_title`, `citation_author`, `citation_date=2026/08/27`,
  `citation_arxiv_id=2608.26480`, and the verbatim abstract. The paper
  is real (in the sandbox's 2026 timeline). The abstract references model
  names ("Qwen3.8-27B", "GPT-5.6-Luna", "GPT-5.6-Terra", "Kimi-K3",
  "Minimax-M3", "Qwen3.6-35B", "Opus-5", "Fable 5") that are future
  relative to general training data; reviewers should treat them as
  real in this environment's timeline but unverifiable from general
  world knowledge.

### `src/extension/.gitkeep` (1 line)
- **Content:** `# Placeholder for Pi extension entry point`
- This is the closest thing to "source code" in the entire repo.

### Upstream reference (mirrored for grounding): `_upstream/GVS5H_multiagent_v2.py` (643 lines)
- Not part of `MrJ55/pi-zero-shot`, but fetched from
  `slee-persis/GVS5H:master/codebase/v2-current/escalation/multiagent.py`
  to validate the port plan's references. Confirmed: all eight cited
  function names exist; `MAX_PLAN_CHARS = 4000` (line 197); the file
  contains the actual `multiagent_solve` and `single_solve` entry points
  (lines 526, 622). This is the file the entire MrJ55 plan is a port-of.

### Quote of the "most critical code" available
There is no project code. The closest critical reference is the
upstream `multiagent_solve` signature, quoted here so the parent
reviewer has something concrete:

```python
# From upstream GVS5H multiagent.py (NOT this repo) — lines 526-527
def multiagent_solve(problem_text, spec, log=None, status_out=None, tests=None):
    ...
# From upstream GVS5H multiagent.py — line 622
def single_solve(problem_text, spec, log=None, status_out=None, tests=None):
    ...
# From upstream GVS5H multiagent.py — line 197
MAX_PLAN_CHARS = 4000
```

The MrJ55 repo **does not** contain any equivalent of these. Every
mention is in a Markdown task checklist ("[ ] Port system prompts …",
`plan/phase-02-prompts-parsing.md:15`) — the boxes are all unchecked.

---

## E. Implementation Decisions

Because there is no code, every "decision" below is a *planned* decision
captured in prose, not an executed one. Citations are to the planning
docs that commit to each choice.

| Dimension | Planned decision | Source |
|-----------|-------------------|--------|
| **Architecture / backbone** | Sequential manager (deterministic TS state machine) + one fresh-context worker per round + sample-test subprocess gate + finalize. No training. | `adr/0003-sequential-manager-worker.md:13-15`; `adr/0004-subagents-as-spawn-helper.md:22`; `docs/architecture.md:47-54` |
| **Implementation language** | TypeScript (Pi extension) | `adr/0004-subagents-as-spawn-helper.md:22`; `plan/phase-01-ledger-primitives.md:15`; `.gitignore` |
| **Worker spawn** | Preferred: `pi-subagents` with `context: "fresh"`, concurrency=1. Fallback: `@earendil-works/pi-ai` or `pi --mode rpc` one-shots. | `adr/0004-subagents-as-spawn-helper.md:23-33`; `docs/architecture.md:24-32` |
| **Ledger** | Real filesystem workspace keyed by content hash / session id; files `task.md`, `plan.md`, `notes.md`, `solution.py`, `tasks.json`, `transcript.jsonl`; hard size bounds; notes rewrite semantics. | `adr/0002-filesystem-ledger.md:13-15`; `plan/phase-01-ledger-primitives.md:15-19` |
| **Max iters** | v2 = 10 (mirrors upstream `MULTIAGENT_MAX_ITERS` v2). | `docs/01-source-analysis.md:26` |
| **Plan size cap** | Mirror paper `MAX_PLAN_CHARS` (upstream = 4000 chars). | `plan/phase-01-ledger-primitives.md:18`; upstream `multiagent.py:197` |
| **Role prompts** | Port upstream `_primary_plan`, `_ideation_worker`, `_primary_manage`, `_worker`, `_summarize_cutoff` verbatim into a TS prompt library. | `plan/phase-02-prompts-parsing.md:9,15` |
| **Parsers** | `_sections`, `_parse_tasks`, `_extract_py` ported; robust to `### HEADER`, `**HEADER**`, `HEADER:` styles; strict-format config flag. | `plan/phase-02-prompts-parsing.md:16-19` |
| **Sample-test gate** | External subprocess, returns `{ran, passed, total, fail}`; hard override if manager declares done while samples fail. | `plan/phase-01-ledger-primitives.md:21`; `plan/phase-03-manager-worker-loop.md:24` |
| **No-progress guard** | Identical re-issued task → stop. | `plan/phase-03-manager-worker-loop.md:26` |
| **Single-shot baseline** | Same model, one call, kept available for A/B. | `plan/phase-03-manager-worker-loop.md:27`; `README.md:33` (G5) |
| **Optimizer / scheduler / loss** | N/A — training-free port. | `README.md:38-39` (non-goals) |
| **Evaluation metric** | (Planned) "minimal benchmark driver (subset of LCB or local fixtures) comparing single vs manager." | `plan/phase-04-observability-packaging.md:16` |
| **Hardware assumptions** | None stated. No batch size, dtype, or device assumptions (consistent with a training-free inference scaffold). | — |
| **Random seeds** | None set or discussed. | — |
| **Cost / token accounting** | Per-problem and per-role aggregate; "running a manager roughly triples the token bill" cited from paper. | `plan/phase-04-observability-packaging.md:15`; `raw/PAPER.md:10` |
| **Packaging** | "Installable Pi extension/skill (README usage, config example)." | `plan/phase-04-observability-packaging.md:17` |
| **Provider quirks** | Deferred to Phase 5: reasoning capture, finish_reason normalization, temperature restrictions, clamp detection. | `plan/phase-05-hardening.md:14`; `docs/01-source-analysis.md:17` |

---

## F. Fidelity to Paper

The paper is "Zero-Shot Self-Orchestration with Ledger-Based Control for
Improved LLM Coding Performance" (arXiv:2608.26480, v1, 27 Aug 2026).
The repo claims to be a **port** of the paper's GVS5H v2 scaffold *into
the Pi extension ecosystem*, not an independent re-implementation. So
"fidelity to paper" is best read as "fidelity to GVS5H v2
`multiagent.py`."

| Claim | Assessment | Citation / evidence |
|-------|------------|---------------------|
| Cites the correct paper (title, authors, arxiv id, abstract) | **CONFIRMED** | `raw/PAPER.md:1-10`; independently verified against `https://arxiv.org/abs/2608.26480` metadata |
| Cites the correct official artifact repo (`slee-persis/GVS5H`) | **CONFIRMED** | `README.md:9`; `git ls-remote https://github.com/slee-persis/GVS5H` returned HEAD `6d7a143b…` |
| Identifies the correct reference file (`codebase/v2-current/escalation/multiagent.py`) | **CONFIRMED** | `docs/01-source-analysis.md:16`; `curl -sI https://raw.githubusercontent.com/slee-persis/GVS5H/master/codebase/v2-current/escalation/multiagent.py` returned HTTP 200 |
| Names all 8 upstream functions to be ported (`_primary_plan`, `_ideation_worker`, `_primary_manage`, `_worker`, `_summarize_cutoff`, `_sections`, `_parse_tasks`, `_extract_py`) | **CONFIRMED** | `plan/phase-02-prompts-parsing.md:9`; all 8 verified present in upstream file |
| Captures v1→v2 differences (`MULTIAGENT_MAX_ITERS` 4→10, sample-test verifier added, cutoff summarizer added, size bounds added) | **CONFIRMED** (as a doc claim) | `docs/01-source-analysis.md:22-31`; upstream `multiagent.py` contains `_run_samples` (line 473) and `_summarize_cutoff` (line 353) |
| Reproduces the paper's per-problem workspace layout (`task.md`, `plan.md`, `notes.md`, `solution.py`, `tasks.json`, `transcript.jsonl`) | **PARTIAL** — layout is committed in docs but **no code creates or reads these files**. | `README.md:31` (G3), `docs/01-source-analysis.md:35-42`, `plan/phase-01-ledger-primitives.md:16-17` |
| Defines the model the paper describes (manager + fresh worker + ledger) | **MISSING** — no `LedgerWorkspace`, no manager state machine, no `RoleLauncher` code exists. Only `.gitkeep`. | `src/extension/.gitkeep` (1 line) |
| Implements the loss / training procedure the paper describes | N/A — paper is training-free. The repo correctly disclaims training as a non-goal. | `README.md:38` |
| Uses the datasets the paper uses (LiveCodeBench hard, 100 latest problems) | **PARTIAL / DEFERRED** — paper's full LCB-100 protocol is *not* committed; Phase 4 only promises a "minimal benchmark driver (subset of LCB or local fixtures)." | `plan/phase-04-observability-packaging.md:16`; contrast with `raw/PAPER.md:10` ("100 latest hard LiveCodeBench problems") |
| Reproduces the paper's evaluation protocol (paired passes, p-values, 5-pass, 128k cap conditions) | **MISSING** — no eval harness, no paired-pass runner, no statistics code. README explicitly disclaims "Claiming exact paper numbers without re-running under controlled conditions." | `README.md:41`; `plan/phase-04-observability-packaging.md:16` |
| Ports the paper's prompts verbatim | **MISSING** — task is unchecked. | `plan/phase-02-prompts-parsing.md:15` (`- [ ] Port system prompts …`) |
| Implements the sample-test hard-override | **MISSING** — task is unchecked. | `plan/phase-03-manager-worker-loop.md:24` (unchecked) |
| Preserves same-model-for-all-roles invariant | **PLANNED, NOT ENFORCED** — stated as invariant in ADR 0004 but no code enforces it. | `adr/0004-subagents-as-spawn-helper.md:29` |
| `MAX_PLAN_CHARS = 4000` fidelity | **PLANNED** — repo says "mirror paper `MAX_PLAN_CHARS`"; upstream value confirmed 4000. | `plan/phase-01-ledger-primitives.md:18`; upstream `multiagent.py:197` |
| Sequential, concurrency=1, fresh context | **PLANNED** — ADR 0003 + 0004 commit; no code. | `adr/0003-sequential-manager-worker.md:13`; `adr/0004-subagents-as-spawn-helper.md:28` |

**Net assessment:** the repo is a **faithful and accurate *map*** of the
paper's GVS5H v2 scaffold into Pi-extension terms. Every cited upstream
identifier (file paths, function names, constants, v1/v2 deltas,
workspace filenames) checks out against the real upstream repo. The
fidelity of *intent* is high. The fidelity of *implementation* is **zero**:
none of the mapped code exists. The repo is, by its own status line
(`README.md:117-119`), "Planning complete in-repo. Implementation
follows `plan/phase-*.md` in order" — i.e., **planning is the deliverable
so far**.

---

## G. Execution / Reproducibility

**Can a third party clone this repo and run it?** **No.** There is
nothing to run.

| Reproducibility axis | Status | Evidence |
|----------------------|--------|----------|
| Dependencies pinned | **FAIL** — no `package.json`, `tsconfig.json`, `requirements.txt`, `pyproject.toml`, `environment.yml`, `Dockerfile`, `Makefile`, or lockfile exists. | `find` over clone; tree in §A |
| Hardcoded paths / API keys | None present (no code to hardcode them). `.gitignore` correctly excludes `.env`, `*.key`, `.credentials*`. | `.gitignore:4-7` |
| Missing checkpoints | N/A — training-free port, no checkpoint expected. | `README.md:38` |
| CLI / main entry point | **MISSING** — `src/extension/` contains only `.gitkeep`. Planned slash commands `/ledger`, `/self-orchestrate` are *mentioned* in docs but not implemented. | `src/extension/.gitkeep`; `docs/architecture.md:41` |
| Tests | **MISSING** — no test files. `plan/phase-01-ledger-primitives.md:23` lists "Unit tests …" as an unchecked task. | `find` over clone |
| Linting / formatting | **MISSING** — no eslint/prettier/biome config. | — |
| CI | **MISSING** — no `.github/` directory at all. | `find` over clone |
| Random seeds set | N/A (no code). Not discussed in docs. | — |
| Data download scripts | **MISSING** — `scripts/` contains only a 3-line placeholder README. LiveCodeBench fetch is mentioned as a future "subset" run. | `scripts/README.md`; `plan/phase-04-observability-packaging.md:16` |
| Build instructions | **MISSING** — no build/install/run docs beyond the planned slash commands. | — |
| Verification log | **EMPTY** — `plan/VERIFY-LOG.md` has only a table header; no phase has been verified. | `plan/VERIFY-LOG.md:5-7` |

**A reviewer cloning this repo receives only Markdown planning
documents.** Nothing executes. There is no `npm install`, no `pi
install`, no entry point, no test, no CI.

---

## H. Open Issues / TODOs

- **GitHub Issues / PRs:** Could not be retrieved — GitHub REST API
  returned `403 rate limit exceeded` (60/60 unauthenticated calls used)
  for this sandbox IP. `git log` shows only the single commit `cc5ae55`,
  so there is no in-tree evidence of PRs. **Recommend the parent reviewer
  retry `https://api.github.com/repos/MrJ55/pi-zero-shot/issues?state=all`
  once the rate window resets**, or check the GitHub web UI directly.
- **In-tree TODOs:** Every implementation task across
  `plan/phase-00` through `plan/phase-05` is an unchecked checkbox
  (`- [ ]`). Notable empty checkboxes:
  - `plan/phase-00-discovery-mapping.md:36-42` — 7 unchecked discovery tasks
  - `plan/phase-01-ledger-primitives.md:15-23` — 5 unchecked ledger tasks
  - `plan/phase-02-prompts-parsing.md:15-21` — 6 unchecked prompt/parser tasks
  - `plan/phase-03-manager-worker-loop.md:17-28` — 11 unchecked loop tasks
  - `plan/phase-04-observability-packaging.md:15-18` — 4 unchecked tasks
  - `plan/phase-05-hardening.md:14-20` — 7 unchecked tasks
- **`plan/VERIFY-LOG.md` is empty** (header row only, no entries) —
  no phase has been verified yet.
- **ADR 0002 status is "Proposed," not "Accepted"** (`adr/0002-filesystem-ledger.md:5`)
  — the ledger-persistence decision is officially still open per the
  repo's own ADR discipline, even though the rest of the docs assume it.
- **License is "TBD"** (`README.md:123`) — no `LICENSE` file. Third parties
  cannot legally reuse the (currently non-existent) code.
- **No commit history beyond a single commit** — the entire repo
  (docs, ADRs, plan, raw extract, placeholders) was added in one shot on
  2026-08-29 (`git log --reverse` shows only `cc5ae55 2026-08-29`).
  There is no incremental development signal.
- **Single-commit message:** `cc5ae55 docs: add structured Terra
  architecture and implementation review` — note the commit message
  references "Terra architecture and implementation review," but the
  actual added file carrying that name lives under the `review-by-Terra/`
  directory, which per the hard constraint was not inspected. The
  commit *also* added every other file in the repo (docs/, adr/, plan/,
  raw/, src/, scripts/, README, .gitignore) — i.e., the whole repo was
  born in the same commit as a review artifact from a different agent.
  This is an unusual provenance signal worth flagging to the parent
  reviewer.

---

## I. Notable Strengths

1. **Accurate upstream mapping.** Every cited upstream identifier
   (arxiv id, paper title, authors, GVS5H file paths, function names,
   `MAX_PLAN_CHARS` constant, v1/v2 differences, workspace filenames)
   was independently verified to match the real upstream
   `slee-persis/GVS5H` repo and the real arxiv record. The port plan is
   not hand-waving — it points at the right code (`docs/01-source-analysis.md`,
   `plan/phase-02-prompts-parsing.md:9`).

2. **Disciplined ADR practice.** Four ADRs with explicit Status /
   Context / Decision / Consequences / Alternatives sections. ADR 0004
   in particular (62 lines) articulates a sharp, falsifiable invariant
   set for role calls (`adr/0004-subagents-as-spawn-helper.md:26-32`):
   `context:"fresh"`, concurrency=1, same-model, ledger-only injection,
   minimal tools, sample-test-as-subprocess. This is exactly the kind
   of invariant a reviewer can later check the implementation against.

3. **Honest scoping.** Non-goals explicitly disclaim changing Pi core,
   learned orchestrators, MoA, and "Claiming exact paper numbers without
   re-running under controlled conditions" (`README.md:36-41`). The plan
   does not overpromise the paper's headline numbers.

4. **Clear separation of control plane vs. spawn helper**
   (`docs/architecture.md:24-36`). The plan correctly isolates the
   deterministic manager state machine (owned by pi-zero-shot) from
   pluggable worker spawn mechanisms (pi-subagents preferred, pi-ai/RPC
   fallback). This avoids over-coupling to a single Pi package.

5. **Explicit "do not use" list** (`docs/02-ecosystem-shortcuts.md:20-26`)
   naming five community packages that would confound the paper's
   zero-shot same-prompt design. This is unusually rigorous
   anti-footgun guidance for a port plan.

6. **Paper abstract is reproduced verbatim** (`raw/PAPER.md:10`),
   matching the arxiv citation abstract byte-for-byte (verified).

---

## J. Notable Weaknesses / Risks

1. **There is no code.** The single most important fact for the parent
   reviewer: `src/extension/.gitkeep` (1 line: `# Placeholder for Pi
   extension entry point`) is the entirety of the implementation. The
   repo's stated status (`README.md:117-119`) admits this: "Planning
   complete in-repo. Implementation follows `plan/phase-*.md` in order."
   A "critical, code-grounded review" of this repo is, by construction, a
   review of **planning prose, not code**. The parent reviewer should
   calibrate expectations accordingly.

2. **No dependency manifest.** No `package.json`, `tsconfig.json`, or
   lockfile. ADR 0004 commits to TypeScript (`adr/0004-subagents-as-spawn-helper.md:22`)
   but the toolchain is not declared anywhere. A new contributor cannot
   `npm install` or `pnpm install`. No Node/TS version pin.

3. **No license.** `README.md:123` says "TBD (recommended: MIT …)" but
   no `LICENSE` file exists. Until a license is added, the repo is
   legally "all rights reserved" by default in most jurisdictions — a
   barrier to the very "installable Pi extension/skill" outcome Phase 4
   promises (`plan/phase-04-observability-packaging.md:17`).

4. **ADR 0002 is still "Proposed," not "Accepted"** (`adr/0002-filesystem-ledger.md:5`).
   Yet the entire plan assumes a real-FS ledger (e.g.,
   `plan/phase-01-ledger-primitives.md:15-19` instructs building
   `LedgerWorkspace` with directory-keyed atomic files). The repo has
   not closed its own decision process.

5. **No tests, no CI, no verification entries.** `plan/VERIFY-LOG.md`
   contains only a table header (`plan/VERIFY-LOG.md:5-7`). Every "Unit
   tests …" task is unchecked (`plan/phase-01-ledger-primitives.md:23`,
   `plan/phase-02-prompts-parsing.md:21`, `plan/phase-05-hardening.md:19`).
   There is no `.github/workflows/` directory. There is no regression
   harness against GVS5H transcripts, despite Phase 5 promising one.

6. **No evaluation harness for paper claims.** The paper's headline
   results (paired 5-pass on 100 LCB-hard problems, p-values, 128k-cap
   conditions, 9 models) have *no* planned reproduction in this repo.
   Phase 4 only commits to "Minimal benchmark driver (subset of LCB or
   local fixtures)" (`plan/phase-04-observability-packaging.md:16`).
   README explicitly disclaims reproducing paper numbers
   (`README.md:41`). So a reviewer cannot, from this repo alone,
   validate or refute any paper claim — the repo provides neither the
   implementation nor the eval to do so.

7. **Single-commit provenance.** `git log` shows exactly one commit
   (`cc5ae55`, 2026-08-29 16:39:06 +0200) titled "docs: add structured
   Terra architecture and implementation review." This single commit
   added *every* file in the repo — README, ADRs, plan, raw, src/.gitkeep
   — simultaneously with a review artifact that lives in a
   `review-by-Terra/` directory (not inspected per the hard constraint).
   Implications worth flagging to the parent reviewer:
   - There is no iterative development history to inspect.
   - The repo's "planning complete" status was achieved in one shot, not
     through the phased process the plan itself prescribes.
   - The repo and a sibling agent's review were committed together,
     which complicates the independence narrative the parent reviewer
     is being asked to produce.

8. **Paper and model timeline.** The paper is dated 2026-08-27
   (`raw/PAPER.md:5`); the repo was created 2026-08-29 — **two days
   later**. The abstract references model names (e.g.,
   "GPT-5.6-Luna", "GPT-5.6-Terra", "Qwen3.8-27B", "Kimi-K3",
   "Minimax-M3", "Opus-5", "Fable 5") that are *future* relative to
   general public training data. The arxiv metadata was independently
   verified to match what the repo quotes, so within this environment's
   timeline the paper is real. But a reviewer relying on general world
   knowledge cannot corroborate these model names or the reported
   numbers. **The parent reviewer should treat the paper's quantitative
   claims as unverifiable from general knowledge and focus the review on
   the repo's planning fidelity rather than on re-deriving paper
   numbers.**

9. **External dependency on `earendil-works/pi` and `pi-subagents`.**
   The port's value depends entirely on the existence and stability of
   two external repos. Both were verified to exist (`git ls-remote`
   returned HEADs for `earendil-works/pi` and `nicobailon/pi-subagents`),
   but neither is pinned to a version anywhere in this repo. Any
   breaking change in `pi-ai`'s API or `pi-subagents`' `context:"fresh"`
   semantics would silently invalidate the port plan's invariants.

10. **Phase 0 still has unchecked discovery tasks**
    (`plan/phase-00-discovery-mapping.md:36-42`): "Read Pi extension /
    skill authoring docs and one existing extension for patterns,"
    "Confirm fallback path without pi-subagents," "Decide and record:
    real filesystem workspace vs pure session-tree virtual ledger."
    Phase 0's *exit criteria* are themselves unchecked
    (`plan/phase-00-discovery-mapping.md:46-48`). The repo is, by its
    own phase plan, **not even past Phase 0**, let alone at a runnable
    state.

11. **No contribution/development guide.** No `CONTRIBUTING.md`, no
    `CODE_OF_CONDUCT.md`, no security policy. Given Phase 4's
    "installable by others" goal, this is a gap.

---

## K. Raw Manifest

Local mirror root: `/home/z/my-project/review-by-GLM/sources/pi-zero-shot/`

Every file fetched and saved (all via `git clone --depth 1
https://github.com/MrJ55/pi-zero-shot.git`; the GitHub REST API was
unavailable due to rate limiting):

| # | Local path | Origin | Lines |
|---|-----------|--------|-------|
| 1 | `README.md` | repo root | 123 |
| 2 | `.gitignore` | repo root | 12 |
| 3 | `adr/0001-use-extension-not-core-fork.md` | repo `adr/` | 27 |
| 4 | `adr/0002-filesystem-ledger.md` | repo `adr/` | 26 |
| 5 | `adr/0003-sequential-manager-worker.md` | repo `adr/` | 25 |
| 6 | `adr/0004-subagents-as-spawn-helper.md` | repo `adr/` | 62 |
| 7 | `docs/README.md` | repo `docs/` | 15 |
| 8 | `docs/00-problems-and-goals.md` | repo `docs/` | 5 |
| 9 | `docs/01-source-analysis.md` | repo `docs/` | 44 |
| 10 | `docs/02-ecosystem-shortcuts.md` | repo `docs/` | 30 |
| 11 | `docs/architecture.md` | repo `docs/` | 66 |
| 12 | `docs/plan.md` | repo `docs/` | 6 |
| 13 | `plan/README.md` | repo `plan/` | 29 |
| 14 | `plan/VERIFY-LOG.md` | repo `plan/` | 7 |
| 15 | `plan/phase-00-discovery-mapping.md` | repo `plan/` | 53 |
| 16 | `plan/phase-01-ledger-primitives.md` | repo `plan/` | 34 |
| 17 | `plan/phase-02-prompts-parsing.md` | repo `plan/` | 30 |
| 18 | `plan/phase-03-manager-worker-loop.md` | repo `plan/` | 42 |
| 19 | `plan/phase-04-observability-packaging.md` | repo `plan/` | 28 |
| 20 | `plan/phase-05-hardening.md` | repo `plan/` | 30 |
| 21 | `raw/PAPER.md` | repo `raw/` | 21 |
| 22 | `raw/README.md` | repo `raw/` | 17 |
| 23 | `scripts/README.md` | repo `scripts/` | 3 |
| 24 | `src/README.md` | repo `src/` | 14 |
| 25 | `src/extension/.gitkeep` | repo `src/extension/` | 1 |

**Cross-reference artifacts (NOT part of `MrJ55/pi-zero-shot`; fetched
for grounding):**

| # | Local path | Origin | Lines |
|---|-----------|--------|-------|
| 26 | `_upstream/GVS5H_multiagent_v2.py` | `slee-persis/GVS5H:master/codebase/v2-current/escalation/multiagent.py` (via `raw.githubusercontent.com`) | 643 |
| 27 | `_analysis.md` | This report (Task ID 2 output) | — |

**Directories excluded by hard constraint:**
- `review-by-Terra/` — present in the repo, **not** enumerated, read, or
  mirrored.

**External resources verified (not saved to disk, only checked for
existence):**
- `https://arxiv.org/abs/2608.26480` — HTTP 200, citation metadata
  matches `raw/PAPER.md`.
- `https://github.com/slee-persis/GVS5H` — `git ls-remote` returned HEAD
  `6d7a143bd4e4c4343179b4386fc0d906ae9af118`.
- `https://github.com/earendil-works/pi` — `git ls-remote` returned HEAD
  `853a80d26c90a14c1886f0ebb8ffaae133ca2185` (plus many branches).
- `https://github.com/nicobailon/pi-subagents` — `git ls-remote`
  returned HEAD `35cfcafbf42cfb177dd2ca2d68b496dc43d48dde`.
- Upstream `multiagent.py` and `orchestrator.py` and paper TeX paths —
  `curl -sI https://raw.githubusercontent.com/slee-persis/GVS5H/master/...`
  returned HTTP 200 for all three.

**Resources that could NOT be retrieved (rate limit):**
- GitHub REST API: `repos/MrJ55/pi-zero-shot` (stars/forks/watchers/
  created/updated/license) — `403 rate limit exceeded`.
- GitHub REST API: `repos/MrJ55/pi-zero-shot/issues?state=all` —
  same `403`.
- GitHub REST API: `repos/MrJ55/pi-zero-shot/commits` — same `403`.
- GitHub REST API: `repos/MrJ55/pi-zero-shot/git/trees/main?recursive=1`
  — same `403`. (The `git clone --depth 1` was used instead and yielded
  the complete file tree.)

The commit history was recovered from the cloned `.git` instead:
single commit `cc5ae55` dated `2026-08-29 16:39:06 +0200`, message
"docs: add structured Terra architecture and implementation review."

---

*End of analysis. The parent reviewer should treat every "code-grounded"
claim above as grounded in the mirrored files at
`/home/z/my-project/review-by-GLM/sources/pi-zero-shot/` (the 25 in-repo
files) plus the cross-reference file
`/home/z/my-project/review-by-GLM/sources/pi-zero-shot/_upstream/GVS5H_multiagent_v2.py`
(643-line upstream reference, clearly labeled as not part of the
reviewed repo).*
