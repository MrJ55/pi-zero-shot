# GVS5H Reference Implementation — Analysis Report

**Source repository:** https://github.com/slee-persis/GVS5H
**Head commit (only commit on default branch):** `6d7a143bd4e4c4343179b4386fc0d906ae9af118`
**Author of head commit:** slee-persis <slee@persisholdings.com>  ·  **AuthorDate:** 2026-08-27 16:39:11 -0400
**Commit message:** "Enhance README with Fable 5 pricing and GPU info"
**Clone method:** `git clone --depth 1 https://github.com/slee-persis/GVS5H.git` (GitHub REST API was rate-limited from this host; metadata endpoints `/repos/...`, `/issues`, `/pulls`, stars/forks counts were NOT retrievable. The clone is complete and authoritative.)
**Local mirror root:** `/home/z/my-project/review-by-GLM/sources/GVS5H/`
**Total tracked files in repo:** 29,395 (`_meta/all_tracked_files.txt`)

---

## A. Repo Overview

- **Name:** GVS5H (tagline: "Five Qwen3.8-27B Models Match Claude Fable 5 on LiveCodeBench Hard — Fable 5 Level Coding for a Fifth the Price - or on a Single GPU").
- **License:** NO top-level LICENSE file. The bundled `codebase/livecodebench/LICENSE` is MIT (Copyright (c) 2024 LiveCodeBench). The paper-bundle code itself (everything under `codebase/v1-be9dfa2/`, `codebase/v2-current/`, `paper/`) ships with no license grant; reuse rights are unspecified.
- **Stars/forks:** Could not be retrieved (GitHub API rate-limited from this host). The repo is the artifact bundle for an academic paper authored by a Persis Capital Inc. team; given the single commit and the user `slee-persis` matching corresponding author Simon Lee, low traffic is plausible but unverified.
- **Last commit date:** 2026-08-27 (single commit; the entire repo was pushed in one commit per `git log`).
- **Primary language:** Python (the scaffold + benchmark harness); LaTeX (the paper); Bash (run drivers); JSON (frozen problem IDs and graded results).
- **Top-level tree:**

```
GVS5H/
├── .gitignore               1 file
├── README.md                1 file  (217 lines)
├── codebase/               81 files
│   ├── livecodebench/      58 files  (vendored benchmark harness, MIT)
│   ├── v1-be9dfa2/          3 files  (the "original scaffold", used for OpenRouter arm set)
│   └── v2-current/         20 files  (the "updated scaffold", used for first-party arms; the
│                                     paper's main scaffold. `escalation/runs` is a symlink to
│                                     ../../../runs so plot scripts find results unmodified)
├── paper/                  20 files  (.tex, .pdf, fig-*.tex, plots/*.png)
└── runs/               29,292 files  (graded results JSON + per-problem workspaces)
                              1 file  per_problem_tokens.json
                            511 files  fable5-128k-reasoning-on-5pass/
                          11,273 files  firstparty-128k-reasoning-on-5pass/
                          12,521 files  16k-reasoning-off-5pass/
                           2,565 files  128k-reasoning-on-1pass/
                           2,399 files  128k-reasoning-off-1pass/
                             16 files  q9-reasoning-on-archived/
```

The `runs/` directory is dominated by per-problem workspace files (six small markdown/json/python files per workspace × 100 problems × many passes × many arms ≈ ~29k files).

---

## B. Stated Goals

Direct quote from `README.md` (lines 1–17, lightly wrapped):

> # GVS5H: Five Qwen3.8-27B Models Match Claude Fable 5 on LiveCodeBench Hard
>
> **Fable 5 Level Coding for a Fifth the Price - or on a Single GPU**
>
> Everything behind the paper's numbers: the paper itself, both versions of the
> manager–worker scaffold, the benchmark harness they call, and the complete transcripts and
> workspaces of every run the paper reports.
>
> Every figure in the paper was recomputed from the copies in `runs/` before this bundle was
> written, and reproduces exactly — see §4.
>
> **No credentials are included.** `escalation/.env`, `.env.groq` and `.env.openrouter` are
> excluded, as are any `*.key` / `.credentials*` files, and the tree was scanned for
> key-shaped strings before packing. Model routing, caps and reasoning mode are all
> environment-driven; supply your own keys.

The paper's title (from `paper/zero_shot_self_orchestration_…_2026-08-25.tex`, line 62):

> Zero-Shot Self-Orchestration with Ledger-Based Control for Improved LLM Coding Performance

The paper's abstract (`paper/…tex`, lines 118–138) states the central claim:

> Multi-agent large language model systems are widely reported to beat single-model baselines, but the evidence is mixed … We investigate the effect of introducing the manager–worker scaffold over a shared filesystem workspace, with no training and no per-benchmark tuning, measured against the *same* model answering in a single pass. Across nine models — five open-weight, spanning 9B to ~2.8T parameters, and four frontier closed models — on the 100 latest *hard* LiveCodeBench problems, the scaffold's benefit is real but conditional: large and statistically significant for some (Qwen3.8-27B +23.4, GPT-5.6-Luna +10.6 and GPT-5.6-Terra +8.0, each over five paired passes …). With the manager, Opus-5 achieves the highest score in the study at 91% in one pass. Running a manager roughly triples the token bill, but it buys accuracy more cheaply than moving to a larger model does: GPT-5.6-Terra with a manager nearly matches Fable 5's single-call accuracy (85.0 against 87.4, p = 0.59) at a fifth of the price …

**Is this the official authors' implementation?** YES. The repo's author handle is `slee-persis`; the paper's corresponding author is "Simon (Sang Won) Lee, Ph.D. <slee@persisholdings.com>" (paper .tex lines 88–93); all co-authors are affiliated with Persis Capital Inc. The email domain matches. The README refers to the repo as the artifact bundle ("Everything behind the paper's numbers") and §4 of the README documents the exact `uv run … plot_*.py` commands that regenerate each figure from `runs/`.

---

## C. Architecture

### C.1 Directory layout & module responsibilities

The repo is structured as a **research-artifact bundle**, not as an installable package:

- `codebase/v2-current/escalation/` — the **paper's main scaffold** (v2). The paper §3.1 names four differences between v1 and v2, all on the manager arm:
  1. `MULTIAGENT_MAX_ITERS` raised from 4 → 10 (`multiagent.py:42`).
  2. Sample-test verifier added (v2 `_run_samples` / `_sample_feedback`, `multiagent.py:473–521`).
  3. Cut-off summarizer added (v2 `_summarize_cutoff`, `multiagent.py:353–368`).
  4. Size bounds on workspace files added (v2 `MAX_PLAN_CHARS = 4000`, `MAX_ANSWER_CHARS = 20000`, `multiagent.py:194–197`; the worker's NOTES section is a REWRITE not an append).

- `codebase/v1-be9dfa2/escalation/` — the **original scaffold** (v1), used only for the OpenRouter-served model set (§2.4 of the paper). Differs from v2 in the four ways above, plus two:
  - v1 selects "latest 100 hard" at run time (`--lcb 100`); v2 has frozen id-pinning via `lcb100_hardest_v6.json` (README §2).
  - v2's `orchestrator.py` adds a post-paper fix comparing the suspected provider clamp against the cap actually sent (README §2, line 68–71 of README).

- `codebase/livecodebench/` — vendored copy of the **LiveCodeBench** benchmark harness (the official `LiveCodeBench/LiveCodeBench` repo). This copy carries the §3.3 evaluator fix: `lcb_runner/evaluation/testing_util.py:94–116` (`MockBuffer.readline()` now uses `self._bytesio.readline(*args)`, stateful; upstream's was a stateless expression that returned line 1 on every call).

- `paper/` — the paper sources: `zero_shot_self_orchestration_…_2026-08-25.tex`, the PDF built from it, `fig-*.tex` (auto-generated by `run_bench_script/make_figures_tex.py`), and `paper/plots/*.png` (light-theme chart variants only).

- `runs/` — every graded run the paper reports. Each `<condition>/results/` contains graded JSON files named `<arm>_<engine>_p<pass>.json`, plus `.regraded.json` twins (re-scored on the fixed evaluator) and, for Qwen3.8-27B's single arm, `.cap128k.json`/`.cap128k.regraded.json` twins (the 128k cap-matched replay of a 250k generation). Each `<condition>/ws/<arm>_<pass>/<hash>/` holds the per-problem workspace: `task.md`, `plan.md`, `tasks.json`, `notes.md`, `solution.py`, `answer.md`. (`transcript.jsonl` is git-ignored at the repo root — see `.gitignore:6–8` — because raw transcripts total ~1.4 GB across ~9.9k files.)

### C.2 Module responsibilities

| File | Role | Lines |
|---|---|---|
| `codebase/v2-current/escalation/multiagent.py` | **Manager–worker scaffold** (`multiagent_solve`) and the single-shot baseline (`single_solve`). Defines the workspace file schema, the prompts for PRIMARY/IDEATION/WORKER/FINALIZE roles, the parsing of `### HEADER` sections, the sample-test gate, the cut-off summarizer, and the not-cur invariant. | 644 |
| `codebase/v2-current/escalation/orchestrator.py` | **Model routing + transport**. Dispatches `chat(model, messages, …)` to `ollama_chat` / `openai_chat` (Groq, OpenRouter, OpenAI, DashScope) / `claude_cli_chat` (Claude Code CLI) / `anthropic_chat` (Anthropic Messages API). Also defines the per-benchmark `*_SPEC` prompt templates (CODE_SPEC, MATH_SPEC, MATH500_SPEC, GPQA_SPEC, HLE_SPEC) and the `escalate` ladder engine (a separate solve↔critic loop over a model ladder; not used by the paper's main results). | 698 |
| `codebase/v2-current/escalation/run_bench.py` | **CLI entry point / benchmark driver**. `python escalation/run_bench.py --engine {escalate,multiagent,single} --only lcb --lcb 100 --ids-file … --parallel N --out results.json`. Loads the LiveCodeBench dataset (`load_code_generation_dataset`), runs `SOLVE` over each problem in a thread pool (`BENCH_PARALLEL`), extracts the code, calls `codegen_metrics`, writes the graded JSON. Also implements AIME / MATH-500 / GPQA / HLE benchmarks (not the paper's focus). | 601 |
| `codebase/v2-current/escalation/regrade.py` | **Re-grading tool**. Re-scores existing `code` fields against the fixed evaluator without re-running models. Writes `<name>.regraded.json` beside each input; keeps `passed_before_regrade` and `pass@1_before_regrade` for auditability. | 130 |
| `codebase/v2-current/escalation/capmatch_q38.py` | **Cap-matching tool** for Qwen3.8-27B's single arm: replays each 250k-capped generation truncated to 128,000 output tokens (token-exact via vLLM's `/tokenize` and `/detokenize` endpoints using `Qwen/Qwen3.8-27B-FP8`'s tokenizer), re-extracts the code, writes `<name>.cap128k.json`. | 127 |
| `codebase/v2-current/escalation/lcb100_hardest_v6.json` | **Frozen problem set**: 100 `question_id` strings (e.g. `arc196_b`, `arc196_c`, `abc400_e`, …, `abc383_e`) — the "100 latest-hard" LCB problems as of release_v6. | 100 entries |
| `codebase/v2-current/escalation/lcb100_5pass_table.md` | A 5-pass summary table of pass@1 across models × {OFF·16k, OFF·128k, ON·128k}. | human-readable table |
| `codebase/v2-current/escalation/run_bench_script/*.py` | **Plot scripts** that read `runs/.../*.regraded.json` (and `*.cap128k.regraded.json` for Qwen3.8-27B's single arm) and produce the paper's figures (Figure 1 = `plot_4new_5pass_reason_on.py` + `plot_bars.py`; Figure 2 = `plot_cost_5_pass.py`; Figure 3 = `plot_cost_vs_score.py`; Figures 4–6 = `plot_128k_reason_on_1_pass.py` / `plot_16k_reason_off_5_pass.py` / `plot_128k_reason_off_1_pass.py` + `plot_bars.py`; Figure 7 = `plot_agent_loop_flowchart.py`). `make_figures_tex.py` generates `paper/fig-*.tex`. `extract_tokens.py` rebuilds `runs/per_problem_tokens.json`. | ~3,364 LOC |
| `codebase/v2-current/escalation/run_bench_script/run_4models_1pass_reason_on.sh` | **Driver script** for the three first-party 128k × 5-pass arms (Qwen3.8-27B via DashScope; GPT-5.6-Luna via OpenAI; GPT-5.6-Terra via OpenAI; Opus 5 via Anthropic is gated on `ANTHROPIC_API_KEY`). | 176 lines |
| `codebase/v2-current/escalation/run_bench_script/run_fable5_5pass_single.sh` | **Driver script** for Claude Fable 5, single-call arm only, 5 pipelined passes. | 150 lines |
| `codebase/v1-be9dfa2/escalation/multiagent.py` | v1 of the manager–worker scaffold (the 4 deltas listed above are absent). | 397 |
| `codebase/v1-be9dfa2/escalation/orchestrator.py` | v1 of the routing layer (no OpenAI / DashScope / Anthropic first-party branches; only Groq + OpenRouter + ollama). | 349 |
| `codebase/v1-be9dfa2/escalation/run_bench.py` | v1 of the benchmark driver (no `infra` status classification, no `ws` field on records). | 582 |
| `codebase/livecodebench/lcb_runner/` | The vendored LiveCodeBench runner. The paper's `run_bench.py` only uses `benchmarks.code_generation.load_code_generation_dataset`, `evaluation.compute_code_generation_metrics.codegen_metrics`, `utils.extraction_utils.extract_code`, and `lm_styles.LMStyle.ClaudeCode`. The rest is carried in the vendored copy for completeness. | (vendored) |

### C.3 Data flow from input to output (manager arm)

1. **`run_bench.py::main()`** parses `--engine multiagent --only lcb --lcb 100 --ids-file lcb100_hardest_v6.json --parallel N --out results.json`. Sets `SOLVE = multiagent_solve` (lines 560–564).
2. **`run_bench.py::run_lcb(100, ids_file)`** (line 108):
   - Loads `load_code_generation_dataset(release_version="release_v6")` (env `LCB_RELEASE`).
   - Filters to the 100 pinned `question_id`s from `lcb100_hardest_v6.json`.
   - Builds the prompt via `build_code_prompt(problem)` (line 98–105) — Question + "### Format: stdin / starter code" instructions.
   - Calls `_parallel_map(_solve_lcb, picked)` with `BENCH_PARALLEL` workers (each problem gets a thread; each call to `multiagent_solve` then makes its own serial sequence of model calls).
   - `_solve_lcb` calls `SOLVE(prompt, CODE_SPEC, log=…, status_out=status, tests=prob.public_test_cases)`.
3. **`multiagent.py::multiagent_solve(problem_text, spec, log, status_out, tests)`** (line 526):
   - Creates a workspace directory `WS_ROOT / md5(problem_text)[:12]` (line 533) and resets it (lines 540–542: `task.md`, `notes.md`, `transcript.jsonl`, `plan.md`, `solution.py`, `answer.md`, `tasks.json` truncated to empty so a re-run never inherits a prior solution).
   - `_primary_plan` → 1 model call → writes `plan.md` (bounded to `MAX_PLAN_CHARS = 4000` chars, line 247) and seeds the initial `tasks` list (line 547).
   - `_ideation_worker` → 1 model call → appends `## ideation` to `notes.md` (with `_strip_code` to prevent a finished program from being mistaken for an approach) and returns proposed approaches (line 548).
   - `_primary_manage` → 1 model call → folds plan + ideation into a curated `tasks` list and decides `status` (done|continue) + `next_desc` (line 550).
   - **Loop** (line 557, max `MAX_ITERS = 10` iterations):
     - No-progress guard: if the manager re-issues the same task as last round, break (line 561–563).
     - `_worker(...)` → 1 model call → writes `solution.py` (or `answer.md`), **rewrites** (not appends) `notes.md` with the curated replacement, returns `status`, `nexts`, `summary`, and a `wrote` flag (line 567).
     - If `spec["kind"] == "code" and tests and wrote`: run the public stdin sample tests as a real subprocess (`_run_samples` via `sys.executable solution.py`, line 494) and prepend the pass/fail verdict to `summary` (lines 574–578).
     - `_primary_manage` again with the new summary (line 579).
     - **Hard gate** (line 583): if the samples fail and the manager says "done", override to `continue` and force a fix/different-approach task.
   - If status == done and `_has_answer(ws, spec)`: skip finalize (line 592). Else: one final `_worker(..., finalize=True)` call.
   - Returns `f"```python\n{code}\n```"` (line 618) for grading.
4. **`run_bench.py::run_lcb`** then calls `extract_code(raw, LMStyle.ClaudeCode)` and `codegen_metrics(samples, generations, k_list=[1], num_process_evaluate=8)` to grade each generated code against the problem's hidden test suite (the fixed `MockBuffer` in `testing_util.py` is what's used inside `codegen_metrics`).
5. **Records** are written to disk: `{engine, model, lcb: {benchmark, pass@1, records: [{question_id, code, status, finish_reason, completion_tokens, truncated_calls, n_calls, ws, passed}]}}`.
6. **`regrade.py`** then re-grades the stored `code` fields against the same fixed evaluator, writing `<name>.regraded.json` with `passed_before_regrade` preserved.
7. **`capmatch_q38.py`** separately truncates the 250k-capped `q38_single` generations to 128k (token-exact), re-extracts code, writes `<name>.cap128k.json`, then `regrade.py` produces the `.cap128k.regraded.json` files the paper reads.
8. **Plot scripts** in `run_bench_script/` read `*.regraded.json` (and `*.cap128k.regraded.json` for the Qwen3.8-27B single arm) and emit the paper's figures.

### C.4 Frameworks / libraries

- **No deep-learning frameworks are used** — this is *not* a training repo. The "model" in this paper is a **prompt + control flow over a hosted LLM**, not a trained network.
- **LiveCodeBench harness dependencies** (`codebase/livecodebench/pyproject.toml`): `anthropic>=0.42.0`, `openai>=1.59.6`, `datasets>=3.2.0`, `pebble>=5.1.0`, `torch>=2.3.0`, `vllm>=0.5.0.post1`, `together>=0.21.0`, `cohere>=5.13.6`, `mistralai==0.4.2`, `google-genai>=0.6.0`. Python ≥ 3.10. The paper's scaffold itself imports none of these directly except via the LCB import path it adds in `run_bench.py:18–19` — it uses only stdlib (`os`, `re`, `sys`, `time`, `json`, `hashlib`, `subprocess`, `threading`, `urllib`, `argparse`, `traceback`, `ast`, `signal`, `faulthandler`, `decimal`, `csv`, `random`, `importlib`) plus optionally `anthropic` (lazily, `orchestrator.py:439`) and `numpy` (only via the LCB `codegen_metrics` call site, `run_bench.py:165`) and `datasets` (only for AIME/MATH500/HLE; not used by the LCB code path).
- Plot scripts add `matplotlib`, `numpy`, `scipy` (invoked via `uv run --with matplotlib --with numpy --with scipy python plot_*.py`).
- The README §4 shows the canonical invocation: `uv run --project /home/persis/model-test python escalation/run_bench.py …` (a uv project named `model-test` rooted at `/home/persis/model-test` is the runner's environment — note this is the author's machine path, NOT a portable path).

### C.5 Released checkpoints?

- **No trained checkpoints are released**, because nothing is trained. The "model" is the scaffold + the routed model id (e.g. `dashscope:qwen3.8-max` or `openai:gpt-5.6-luna`).
- Released artifacts: 73 graded JSON files in `runs/firstparty-128k-reasoning-on-5pass/results/`, plus `*.regraded.json` twins (and `*.cap128k.*` for Qwen3.8-27B's single arm) and 11,200 per-problem workspace files in `runs/firstparty-128k-reasoning-on-5pass/ws/`. Plus equivalent trees for the other 5 conditions.
- The Qwen3.8-27B weights themselves are NOT in this repo — `capmatch_q38.py:36` names the HuggingFace id `Qwen/Qwen3.8-27B-FP8` and assumes a local vLLM serving stack on `http://localhost:8215` for tokenization.

### C.6 Separation of training vs inference

There is no training. **Inference and evaluation are cleanly separated**:
- The manager/worker code in `multiagent.py` is pure inference (model calls + filesystem workspace).
- Evaluation is delegated to the vendored LiveCodeBench `codegen_metrics` (run inside the same Python process but in a separate `pebble` multiprocessing pool — see `compute_code_generation_metrics.py`).
- The `regrade.py` tool re-runs evaluation independently against stored generations, decoupling "produce a generation" from "score it". This is what allows the §3.3 evaluator bugfix to land without re-running models.
- The `capmatch_q38.py` tool re-simulates a different output cap against stored transcripts, decoupling "produce at cap X" from "score what cap Y would have produced".

---

## D. Key Files & Code Snippets

### D.1 `codebase/v2-current/escalation/multiagent.py` — the scaffold (644 LOC)

**Purpose:** Implements the manager–worker orchestration loop and the single-call baseline. This is the "model" the paper evaluates.

**Key functions / classes:**

```
MODEL = os.environ.get("MULTIAGENT_MODEL", "groq:qwen/qwen3.6-27b")  # line 41
MAX_ITERS = int(os.environ.get("MULTIAGENT_MAX_ITERS", "10"))        # line 42
STRICT_FORMAT = os.environ.get("MULTIAGENT_STRICT_FORMAT", "auto")   # line 56
MAX_TASKS = int(os.environ.get("MULTIAGENT_MAX_TASKS", "12"))         # line 72
WS_ROOT = os.environ.get("MULTIAGENT_WS", <default to ws/ beside this file>)  # line 73
MAX_ANSWER_CHARS = 20000  # line 194
MAX_PLAN_CHARS = 4000     # line 197

def _strict():              # line 59 — auto-detect muse/glimmer, else STRICT_FORMAT flag
def _format_rule(first, *rest):  # line 64 — mandatory-format addendum
def _slug(text):            # line 78 — md5(text)[:12] for workspace dir naming
def _read(ws, name):        # line 82
def _write(ws, name, content):   # line 87
def _append(ws, name, content): # line 92
def _record(ws, rec):       # line 102 — append to transcript.jsonl
def _chat(ws, role, messages, temperature, meta=None):  # line 107 — wraps orchestrator.chat, transcripts
def _strip_think(text):     # line 133 — strip <think>…</think>
def _strip_code(text):      # line 137 — replace fenced code with "[code omitted -- approach only]"
def _sections(text):        # line 143 — parse ### HEADER sections
def _bullets(text):         # line 162
def _extract_py(text):      # line 171 — pull code out of ```python fence
def _parse_tasks(text):     # line 176 — parse "[done] desc" / "[todo] desc" bullets
def _has_answer(ws, spec):  # line 200 — is there a usable final artifact?
def _save_tasks(ws, tasks): # line 209
def _add_tasks(tasks, descs):  # line 213 — dedup + cap to MAX_TASKS
def _primary_plan(problem, spec, ws, log):    # line 224 — manager writes plan.md + initial tasks
def _ideation_worker(problem, spec, ws, log): # line 254 — first worker proposes approaches
def _primary_manage(problem, spec, ws, tasks, proposals, last_summary, log):  # line 287 — manager curates + decides done/continue
def _summarize_cutoff(ws, reply, task_desc):  # line 353 — summarize a cut-off worker attempt
def _worker(problem, spec, ws, task, log, finalize=False):  # line 371 — worker writes code/answer + rewrites notes
def _run_samples(ws, tests):  # line 473 — run solution.py against public stdin tests in subprocess
def _sample_feedback(res):   # line 510 — turn sample results into a sentence for the manager
def multiagent_solve(problem_text, spec, log=None, status_out=None, tests=None):  # line 526 — PUBLIC ENTRY
def single_solve(problem_text, spec, log=None, status_out=None, tests=None):     # line 622 — single-call baseline
```

**Critical snippet — the manager–worker loop** (`multiagent.py:547–595`):

```python
    tasks = _primary_plan(problem_text, spec, ws, log)
    proposals = _ideation_worker(problem_text, spec, ws, log)
    # Primary folds the plan + ideation into one curated list and picks the first task.
    status, next_desc, tasks = _primary_manage(
        problem_text, spec, ws, tasks, proposals, "ideation complete", log)
    _save_tasks(ws, tasks)

    # Primary manages the loop: worker does the chosen task, then the primary reviews
    # progress, re-curates the list, and decides whether the problem is done.
    iters, prev_desc = 0, None
    while status == "continue" and next_desc and iters < MAX_ITERS:
        if prev_desc is not None and next_desc.strip().lower() == prev_desc.strip().lower():
            log(f"    [primary] reissued the same task; no progress, stopping after {iters} iters")
            break
        prev_desc = next_desc
        iters += 1
        task = {"id": iters, "desc": next_desc, "status": "in_progress", "result": ""}
        _, nexts, summary, wrote = _worker(problem_text, spec, ws, task, log)
        res = None
        if spec["kind"] == "code" and tests and wrote:
            res = _run_samples(ws, tests)
            if res.get("ran"):
                summary = _sample_feedback(res) + summary
                log(f"    [samples] {res['passed']}/{res['total']} public tests passed")
        status, next_desc, tasks = _primary_manage(
            problem_text, spec, ws, tasks, nexts, summary, log)
        # Hard guard: never accept a solution that fails the public samples, no matter what
        # the manager said -- keep iterating (fix / different approach) until they pass.
        if res and res.get("ran") and res["passed"] < res["total"] and status == "done":
            status = "continue"
            if not next_desc:
                next_desc = "The solution fails the public sample tests; fix it or try a different approach."
            log("    [primary-manage] overriding 'done' -- sample tests still failing")
        _save_tasks(ws, tasks)

    if status == "done" and _has_answer(ws, spec):
        log("    [finalize] skipped (primary marked done)")
    else:
        _worker(problem_text, spec, ws, {"id": 0, "desc": "finalize"}, log, finalize=True)
```

**Critical snippet — the sample-test gate** (`multiagent.py:473–521`):

```python
def _run_samples(ws, tests):
    code = _read(ws, "solution.py")
    stdin_tests = [t for t in (tests or [])
                   if "stdin" in str(getattr(t, "testtype", "")).lower()]
    if not code.strip() or not stdin_tests:
        return {"ran": False}
    sol = os.path.join(ws, "solution.py")
    passed, fail = 0, None
    for t in stdin_tests:
        inp = getattr(t, "input", "") or ""
        exp = (getattr(t, "output", "") or "").strip()
        try:
            # sys.executable, NOT bare "python3": the gate's verdict is only useful if it is
            # computed in the SAME interpreter that grades. /usr/bin/python3 here has neither
            # numpy nor numba, while the project venv has numpy -- so a bare "python3" made
            # every numpy solution "fail" its samples, which flipped the manager's hard gate
            # and made it burn all 10 rounds fixing code that was already correct.
            r = subprocess.run([sys.executable, sol], input=inp, capture_output=True,
                               text=True, timeout=10)
            got = (r.stdout or "").strip()
            if r.returncode != 0 and not got:
                got = f"<runtime error: {(r.stderr or '')[:200]}>"
        except subprocess.TimeoutExpired:
            got = "<timed out (>10s)>"
        except Exception as e:  # noqa: BLE001
            got = f"<error: {e}>"
        if got == exp:
            passed += 1
        elif fail is None:
            fail = {"input": inp[:600], "expected": exp[:400], "got": got[:400]}
    return {"ran": True, "passed": passed, "total": len(stdin_tests), "fail": fail}
```

**Critical snippet — the single-call baseline** (`multiagent.py:622–643`):

```python
def single_solve(problem_text, spec, log=None, status_out=None, tests=None):
    """Single-shot baseline: one model call, no orchestration. Same signature as
    escalate()/multiagent_solve() (`tests` accepted for interface parity, unused here);
    transcripts each problem like the multi-agent path.
    If `status_out` (a dict) is passed, it gets {finish_reason, completion_tokens} of the call."""
    log = log or (lambda *a, **k: None)
    ws = os.path.join(WS_ROOT, _slug(problem_text))
    os.makedirs(ws, exist_ok=True)
    _write(ws, "task.md", problem_text)
    _write(ws, "transcript.jsonl", "")
    _record(ws, {"_meta": True, "t": time.time(), "model": MODEL,
                 "kind": spec["kind"], "engine": "single", "problem": problem_text})
    meta = {}
    answer = _chat(ws, "single", [
        {"role": "system", "content": spec["solver_system"]},
        {"role": "user", "content": problem_text},
    ], temperature=0.2, meta=meta)
    if status_out is not None:
        status_out.update(meta)
        status_out["ws"] = ws
    log(f"    [single] {len(answer)} chars  finish={meta.get('finish_reason')}")
    return answer
```

**Notable hardcoded constants:**
- Workspace dir is keyed by `md5(problem_text)[:12]` — re-running the same problem reuses the workspace dir, which is why `multiagent_solve` line 540–542 hard-resets every file (otherwise a stale `solution.py` from a prior run would be returned as this run's answer).
- `MAX_PLAN_CHARS = 4000` (line 197) — caps `plan.md`, which is injected into every later prompt; a 128k-token plan that truncated to no parseable section previously produced a ~205KB plan.md (see comment lines 243–247).
- `MAX_ANSWER_CHARS = 20000` (line 194) — a "genuine final answer is short. Anything longer is a reasoning dump, not an answer."
- `MAX_TASKS = 12` (line 72), `MAX_ITERS = 10` (line 42).
- The sample-test subprocess uses `sys.executable` (NOT `python3`), with `timeout=10` seconds (line 494–495).
- Worker NOTES is bounded to `MAX_PLAN_CHARS * 2 = 8000` chars on write (line 450).
- The `_chat` meta records `reasoning`, `thinking_blocks`, `reasoning_is_summary`, `attempts`, `discarded`, `infra_exhausted` — for full transcript reconstruction.

### D.2 `codebase/v2-current/escalation/orchestrator.py` — model routing (698 LOC)

**Purpose:** A single `chat(model, messages, …)` function that dispatches by model-name prefix to the right cloud provider, with provider rerouting, hard wall-clock caps, and per-attempt transcript bookkeeping.

**Key constants (`orchestrator.py:24–106`):**

```python
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = os.environ.get("ESCALATION_OPENAI_BASE", "https://api.groq.com/openai/v1/chat/completions")
GROQ_REASONING = os.environ.get("ESCALATION_GROQ_REASONING", "none")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_REASONING = os.environ.get("ESCALATION_OR_REASONING", "none")
OPENROUTER_PROVIDERS = [p.strip() for p in os.environ.get("ESCALATION_OR_PROVIDERS", "").split(",") if p.strip()]
LADDER = os.environ.get("ESCALATION_LADDER", "qwen3.5:2b,qwen3.5:9b,qwen3.5:35b,qwen3.5:122b").split(",")
MAX_ROUNDS = int(os.environ.get("ESCALATION_MAX_ROUNDS", "2"))
THINK = os.environ.get("ESCALATION_THINK", "0") == "1"
REQUEST_TIMEOUT = int(os.environ.get("ESCALATION_TIMEOUT", "1200"))
CLOUD_TIMEOUT = int(os.environ.get("ESCALATION_CLOUD_TIMEOUT", "120"))
CLOUD_MAX_TOKENS = int(os.environ.get("ESCALATION_CLOUD_MAX_TOKENS", "8000"))
CLAUDE_TIMEOUT = int(os.environ.get("ESCALATION_CLAUDE_TIMEOUT", "1800"))
CLAUDE_ATTEMPTS = int(os.environ.get("ESCALATION_CLAUDE_ATTEMPTS", "3"))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_REASONING = os.environ.get("ESCALATION_OPENAI_REASONING", "")
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
DASHSCOPE_URL = os.environ.get("ESCALATION_DASHSCOPE_BASE", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions")
DASHSCOPE_THINKING_BUDGET = int(os.environ.get("ESCALATION_DASHSCOPE_THINKING_BUDGET", "0"))
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MAX_OUTPUT = 128000
ANTHROPIC_EFFORT = "high"
```

**Key functions:**

```
def ollama_chat(model, messages, temperature=0.2, num_ctx=16384, meta=None):  # line 109
def openai_chat(url, api_key, model, messages, temperature=0.2, extra=None, meta=None,
                token_param="max_tokens", send_temperature=True):  # line 142 — the OpenAI-compat path
def claude_cli_chat(model, messages, temperature=0.2, meta=None):  # line 340 — claude -p CLI
def anthropic_chat(model, messages, temperature=0.2, meta=None):  # line 418 — first-party Anthropic Messages API
def chat(model, messages, temperature=0.2, num_ctx=16384, meta=None):  # line 487 — DISPATCH by prefix
def _is_approved(critique):  # line 633
def solve_layer(model, problem_text, spec, prior_answer=None, temperature=0.2, log=None):  # line 637 — solve↔critic loop (used only by the `escalate` engine, not by `multiagent`)
def escalate(problem_text, spec, ladder=None, log=None, status_out=None, tests=None):  # line 687 — ladder engine
```

The 5 `*_SPEC` dicts (lines 548–630) are the per-benchmark prompt templates (CODE_SPEC, MATH_SPEC, MATH500_SPEC, GPQA_SPEC, HLE_SPEC).

**Critical snippet — the dispatcher** (`orchestrator.py:487–542`):

```python
def chat(model, messages, temperature=0.2, num_ctx=16384, meta=None):
    if model.startswith("groq:"):
        if not GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY not set but ladder uses a groq: model")
        extra = {"reasoning_effort": GROQ_REASONING} if GROQ_REASONING else None
        return openai_chat(GROQ_URL, GROQ_API_KEY, model[len("groq:"):], messages, temperature, extra, meta)
    if model.startswith("claude:"):  # subscription auth via the Claude Code CLI
        return claude_cli_chat(model[len("claude:"):], messages, temperature, meta)
    if model.startswith("openai:"):  # OpenAI first-party
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY not set but model uses an openai: prefix")
        name = model[len("openai:"):]
        gpt5 = name.startswith("gpt-5")
        extra = {"reasoning_effort": OPENAI_REASONING} if OPENAI_REASONING else None
        return openai_chat(OPENAI_URL, OPENAI_API_KEY, name, messages, temperature, extra, meta,
                           token_param="max_completion_tokens" if gpt5 else "max_tokens",
                           send_temperature=not gpt5)
    if model.startswith("dashscope:"):  # Alibaba Model Studio, OpenAI-compatible
        if not DASHSCOPE_API_KEY:
            raise RuntimeError("DASHSCOPE_API_KEY not set but model uses a dashscope: prefix")
        extra = {"thinking_budget": DASHSCOPE_THINKING_BUDGET} if DASHSCOPE_THINKING_BUDGET else None
        if not extra:
            print("    [dashscope] WARNING: ESCALATION_DASHSCOPE_THINKING_BUDGET is unset ...")
        return openai_chat(DASHSCOPE_URL, DASHSCOPE_API_KEY, model[len("dashscope:"):], messages, temperature, extra, meta)
    if model.startswith("anthropic:"):  # Anthropic first-party Messages API
        if not ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY not set but model uses an anthropic: prefix")
        return anthropic_chat(model[len("anthropic:"):], messages, temperature, meta)
    if model.startswith("openrouter:"):
        if not OPENROUTER_API_KEY:
            raise RuntimeError("OPENROUTER_API_KEY not set but model uses an openrouter: prefix")
        prov = {"sort": "throughput"}
        if OPENROUTER_PROVIDERS:
            prov["only"] = OPENROUTER_PROVIDERS
        extra = {"provider": prov}
        if OPENROUTER_REASONING == "none":
            extra["reasoning"] = {"enabled": False}
        elif OPENROUTER_REASONING in ("low", "medium", "high"):
            extra["reasoning"] = {"effort": OPENROUTER_REASONING}
        elif OPENROUTER_REASONING.startswith("budget:"):
            extra["reasoning"] = {"max_tokens": int(OPENROUTER_REASONING.split(":", 1)[1])}
        return openai_chat(OPENROUTER_URL, OPENROUTER_API_KEY, model[len("openrouter:"):], messages, temperature, extra, meta)
    return ollama_chat(model, messages, temperature=temperature, num_ctx=num_ctx, meta=meta)
```

**Critical snippet — the `openai_chat` rerouting loop with provider clamp detection** (`orchestrator.py:303–328`):

```python
        # A provider clamping output below our cap is an infra cutoff, not the model's doing.
        # Compare against cur_max -- the cap ACTUALLY SENT -- not CLOUD_MAX_TOKENS. After the
        # 400/context shrink above lowers cur_max (e.g. 128000 -> 104000), a reply that fills
        # the reduced budget is a legitimate truncation, but against the original cap it looks
        # clamped (104000 < 0.9*128000) and gets discarded and retried. That made every call
        # after a shrink unsatisfiable: 16 attempts x a full 104k-token generation each, ~7h
        # per call. Cost muse's manager p3 sixteen hours on a single problem (arc191_c, 15 of
        # 16 attempts discarded as "clamped"), while luna and terra -- which never shrink,
        # having context to spare -- were untouched.
        cap_used = cur_max or CLOUD_MAX_TOKENS
        clamped = finish == "length" and cap_used and (ntok or 0) < 0.9 * cap_used
        if content.strip() and not clamped:
            return content  # genuine completion (correct or not) -- this is what gets graded
        why = f"clamped at {ntok} tok (< cap)" if clamped else f"empty reply (finish={finish})"
        print(f"    [cloud] {why} from {served}; rerouting to another provider (attempt {attempt + 1})", file=sys.stderr, flush=True)
        if meta is not None:
            meta.setdefault("discarded", []).append(
                {"attempt": attempt + 1, "provider": served, "why": why, "finish_reason": finish,
                 "completion_tokens": ntok, "content": content, "reasoning": reasoning})
        last = content or last
        if served:
            ignore.append(served)
        time.sleep(1)
```

**Notable hardcoded constants / decisions:**
- `ATTEMPTS = 16` reroutes per call (`orchestrator.py:189`).
- Hard wall-clock cap per attempt: `CLOUD_TIMEOUT + 5` seconds; a stalled provider is abandoned (line 211–217) and daemon thread is leaked.
- A 400 whose body matches `{"context", "maximum context length", "too long", "exceeds", "max_model_len"}` triggers a stepwise shrink of `cur_max` down by 24,000 per step, floored at 40,000 (lines 234–242).
- Any other 400/401/402/403/404 is fatal and aborts (lines 254–257) — comments cite litellm's "No connected db." auth-failure 400 and GPT-5's `max_tokens` 400 as concrete cases.
- The Anthropic path clamps output to `min(CLOUD_MAX_TOKENS, ANTHROPIC_MAX_OUTPUT=128000)` and records `cap_clamped_to` if the request was larger (lines 445–446, 475–476).
- The Claude CLI path uses `claude -p --output-format stream-json --verbose --no-session-persistence --tools "" --model <model>`; raw thinking text is NOT exposed, only block count + (sometimes empty) `thinking` field (lines 374–386).

### D.3 `codebase/v2-current/escalation/run_bench.py` — benchmark driver (601 LOC)

**Purpose:** Argparse CLI + per-benchmark run-and-grade. The benchmark the paper actually uses is `lcb` (LiveCodeBench code generation).

**Key constants:**
- `PARALLEL = int(os.environ.get("BENCH_PARALLEL", "1"))` (line 29) — 1 by default; the run drivers set 4–50 per arm.
- `HARDEST = os.environ.get("BENCH_HARDEST", "0") == "1"` (line 31).
- `HLE_JUDGE_MODEL`, `HLE_TEXT_ONLY`, `HLE_PARQUET`, `HLE_MCQ_ONLY` (lines 35–45) — HLE-only; not used by the LCB code path.

**Key functions:**

```
def _parallel_map(fn, items):           # line 52 — ThreadPoolExecutor when PARALLEL > 1
def _classify_status(parseable, status): # line 68 — returns one of {ok, infra, error, truncated, empty_stop}
def build_code_prompt(problem):          # line 98 — Question + Format block
def run_lcb(n, ids_file):                # line 108 — main LCB runner; returns {benchmark, pass@1, records, n_graded, n_infra}
def extract_answer_int(text):            # line 192 — AIME
def run_aime(n):                         # line 206
def _strip_boxed(s), def _norm(s), def extract_answer_text(text), def _answer_match(pred, gold):  # MATH-500 / GPQA / HLE helpers
def run_math500(n):                      # line 329
def run_gpqa(n):                         # line 342 — uses csv (no HF token); seeded Random(42) for option shuffle
def run_hle(n):                          # line 476 — Humanity's Last Exam; uses LLM judge for free-form + letter match for MCQ
def main():                              # line 545 — argparse; sets SOLVE; runs --only or default lcb+aime
```

**Critical snippet — the LCB grading path with infra exclusion** (`run_bench.py:151–186`):

```python
    solved = _parallel_map(_solve_lcb, picked)
    codes = [c for c, _ in solved]
    samples = [p.get_evaluation_sample() for p in picked]
    generations = [[c] for c in codes]
    records = [{"question_id": p.question_id, "code": c, "status": s.get("class"),
                "finish_reason": s.get("finish_reason"), "completion_tokens": s.get("completion_tokens"),
                "truncated_calls": s.get("truncated_calls"), "n_calls": s.get("n_calls"),
                "ws": s.get("ws")}
               for p, (c, s) in zip(picked, solved)]

    metrics, results, _ = codegen_metrics(samples, generations, k_list=[1], num_process_evaluate=8)
    import numpy as np

    def _passed(res0):
        if isinstance(res0, (list, tuple)):
            return bool(np.all(np.array(res0) > 0)) and len(res0) > 0
        return bool(res0)

    passed = [_passed(results[idx][0]) for idx in range(len(picked))]
    for rec, p in zip(records, passed):
        rec["passed"] = bool(p)
        log(f"  {rec['question_id']}: {'PASS' if p else 'FAIL'}")
    # Exclude infra failures (provider gave up -> no attempt) from pass@1: they are not the
    # model answering wrong. Report both the graded rate and the count set aside.
    graded = [r for r in records if r.get("status") != "infra"]
    n_infra = len(records) - len(graded)
    npass = sum(r["passed"] for r in graded)
    passk = 100.0 * npass / max(1, len(graded))
    log(f"LiveCodeBench pass@1 = {passk:.1f}%  ({npass}/{len(graded)}"
        + (f"; {n_infra} infra-excluded of {len(records)}" if n_infra else "") + ")")
    log(f"  status breakdown: {_status_counts(records)}")
    return {"benchmark": "livecodebench", "pass@1": passk, "records": records,
            "n_graded": len(graded), "n_infra": n_infra}
```

### D.4 `codebase/v2-current/escalation/regrade.py` (130 LOC)

**Purpose:** Re-grade stored `code` fields against the fixed evaluator without re-running models. Pools every input file's records into ONE `codegen_metrics` call (so slow tail-of-distribution problems overlap across files instead of paying the tail 62 times). Writes `<name>.regraded.json`; preserves `passed_before_regrade` and `pass@1_before_regrade` for auditability.

**Critical snippet** (`regrade.py:36–105`):

```python
def regrade_all(paths, problems):
    kept = []
    for path in paths:
        blob = json.load(open(path))
        if "lcb" not in blob or not blob["lcb"].get("records"):
            print(f"  skip (no records): {os.path.basename(path)}")
            continue
        kept.append((path, blob))
    paths = [p for p, _ in kept]

    blobs, index = [], []
    samples, generations = [], []
    for bi, (path, blob) in enumerate(kept):
        blobs.append(blob)
        for ri, r in enumerate(blob["lcb"]["records"]):
            if not (r.get("code") or "").strip():
                r["passed_before_regrade"] = bool(r.get("passed"))
                r["passed"] = False
                continue
            qid = r["question_id"]
            if qid not in problems:
                raise SystemExit(f"{path}: id {qid!r} is not in the loaded dataset")
            index.append((bi, ri))
            samples.append(problems[qid].get_evaluation_sample())
            generations.append([r["code"]])

    nproc = int(os.environ.get("REGRADE_PROCS", min(96, max(8, (os.cpu_count() or 8) // 2))))
    print(f"grading {len(generations)} generations from {len(paths)} files with {nproc} workers", flush=True)
    _, results, _ = codegen_metrics(samples, generations, k_list=[1], num_process_evaluate=nproc)

    for n, (bi, ri) in enumerate(index):
        rec = blobs[bi]["lcb"]["records"][ri]
        rec["passed_before_regrade"] = bool(rec.get("passed"))
        rec["passed"] = _passed(results[n][0])

    out = []
    for path, blob in zip(paths, blobs):
        recs = blob["lcb"]["records"]
        graded = [r for r in recs if r.get("status") != "infra"]
        npass = sum(bool(r["passed"]) for r in graded)
        old = blob["lcb"]["pass@1"]
        blob["lcb"]["pass@1_before_regrade"] = old
        blob["lcb"]["pass@1"] = 100.0 * npass / max(1, len(graded))
        dst = path.replace(".json", ".regraded.json")
        json.dump(blob, open(dst, "w"))
        flips = [(r["question_id"], r["passed_before_regrade"], r["passed"])
                for r in recs if "passed_before_regrade" in r
                and r["passed_before_regrade"] != r["passed"]]
        out.append((path, old, blob["lcb"]["pass@1"], flips))
    return out
```

### D.5 `codebase/v2-current/escalation/capmatch_q38.py` (127 LOC)

**Purpose:** Truncate each 250k-capped Qwen3.8-27B single-call generation to 128,000 output tokens, token-exact (via vLLM's `/tokenize` and `/detokenize` on `Qwen/Qwen3.8-27B-FP8`), then re-extract the code. Writes `<name>.cap128k.json` (pass@1 cleared, recomputed by `regrade.py`).

**Critical snippet — token-exact truncation** (`capmatch_q38.py:70–91`):

```python
def truncated_answer(call):
    reasoning = call.get("reasoning") or ""
    response = call.get("response") or ""
    if reasoning and reasoning == response:
        # openai_chat's empty-content fallback stores ONE stream in both fields (142 of the
        # 500 records here), so tokenizing both and adding would double its length.
        ids = tokens(response)
        return None if len(ids) <= CAP else detokenize(ids[:CAP])
    r_ids = tokens(reasoning) if reasoning else []
    c_ids = tokens(response) if response else []
    if len(r_ids) + len(c_ids) <= CAP:
        return None
    if len(r_ids) >= CAP:
        # The cut lands inside the reasoning: no answer was ever emitted, so the harness
        # falls back to the reasoning text (orchestrator.openai_chat does this when
        # content is empty).
        return detokenize(r_ids[:CAP])
    return detokenize(c_ids[:CAP - len(r_ids)])
```

### D.6 `codebase/livecodebench/lcb_runner/evaluation/testing_util.py` — the §3.3 fix

The whole `MockBuffer` class (lines 94–116) is the corrected version. The class docstring explicitly says: *"upstream's readline returned line 1 every call"*. The stateful `self._bytesio = BytesIO(self.inputs)` and `readline` returning `self._bytesio.readline(*args)` is what makes multi-line stdin solutions grade correctly.

### D.7 `codebase/v2-current/escalation/lcb100_hardest_v6.json` — frozen problem set

A JSON array of 100 `question_id` strings: `arc196_b`, `arc196_c`, `arc196_a`, `arc196_d`, `3777`, `abc400_e`, `abc400_g`, `3717`, `3765`, …, `arc189_b`, `3680`, `abc383_e`. This is the exact set the paper's §2.1–§2.3 figures read.

### D.8 `codebase/v2-current/escalation/lcb100_5pass_table.md` — raw pass@1 table

Human-readable summary table. Excerpt:

```
| Model | Engine | OFF · 16k | OFF · 128k | ON · 128k |
|---|---|--:|--:|--:|
| **opus**   | single   | 40 | —¹ | **85** |
|            | manager  | —  | —¹ | **91** |
| **kimi**   | single   | 32 | 32 | **82** |
|            | manager  | 63 | 74 | **82** |
| **mm3**    | single   | 21 | 25 | **60** |
|            | manager  | 32 | 37 | **66** |
| **q35**    | single   | 28 | 35 | **25** |
|            | manager  | 27 | 26 | **43** |
| **q9**     | single   | 15 | 17 | *unusable*² |
|            | manager  | 22 | 20 | *unusable*² |
```

(¹ OFF·128k opus was never run; ² q9 with thinking on returns reasoning-only replies.)

---

## E. Implementation Decisions (concrete engineering choices)

### E.1 Model architecture / backbone

**There is no trained backbone.** The "model" is the **manager–worker scaffold** in `multiagent.py`, evaluated against hosted LLMs via prefix routing in `orchestrator.py`. The paper's reported models and their routing (from `run_4models_1pass_reason_on.sh:5–10` and `run_fable5_5pass_single.sh:3`):

| Tag (in run scripts) | Model | Route prefix | Provider | Reasoning control | Open weights? |
|---|---|---|---|---|---|
| `muse` (q36l) | Qwen3.6-27B (local vLLM behind litellm :8216) | `groq:small-model` (litellm) | local vLLM | on by default (chat template) — `ESCALATION_GROQ_REASONING=""` (do not send) | yes |
| `luna` | GPT-5.6-Luna | `openai:gpt-5.6-luna` | OpenAI first-party | default (no `reasoning_effort` sent) | no |
| `terra` | GPT-5.6-Terra | `openai:gpt-5.6-terra` | OpenAI first-party | default | no |
| `q38` (single + manager) | Qwen3.8-Max (DashScope `qwen3.8-max`, 2.4T-param MoE ~95B active, $2/$6 per MTok) | `dashscope:qwen3.8-max` | Alibaba Model Studio | `ESCALATION_DASHSCOPE_THINKING_BUDGET=100000` (mandatory — see below) | no |
| `q38` (capmatch target) | Qwen3.8-27B (open-weights) | — (offline tokenizer via vLLM `/tokenize` on `Qwen/Qwen3.8-27B-FP8`) | n/a | n/a | yes (HF: `Qwen/Qwen3.8-27B-FP8`) |
| `opus5` | Claude Opus 5 | `anthropic:claude-opus-5` | Anthropic first-party | `ANTHROPIC_EFFORT="high"` (pinned), `thinking:{type:adaptive,display:summarized}` | no |
| `fable5` | Claude Fable 5 | `anthropic:claude-fable-5` | Anthropic first-party | same adaptive thinking, effort=high | no |
| `kimi` | Kimi-K3 | `openrouter:kimi-k3` (likely) | OpenRouter | depends on `ESCALATION_OR_REASONING` | yes (open weights) |
| `mm3` | Minimax-M3 | (OpenRouter) | OpenRouter | depends on `ESCALATION_OR_REASONING` | yes (open weights) |
| `nem` | Nemotron | (OpenRouter) | OpenRouter | depends | yes (open weights) |
| `q35` | Qwen3.5-35B | (OpenRouter) | OpenRouter | depends | yes (open weights) |
| `q9` | Qwen3.5-9B | (OpenRouter) | OpenRouter | depends | yes (open weights) — §4.5 reports thinking-on as unusable on OpenRouter |

### E.2 Training hyperparameters

**N/A — no training is performed.** The paper's title literally begins "Zero-Shot Self-Orchestration …" (paper .tex, line 62).

### E.3 Inference hyperparameters (the closest analogue)

| Setting | Value | Source |
|---|---|---|
| Manager max iterations (`MAX_ITERS`) | **10** primary↔worker cycles (v2 default) | `multiagent.py:42`, `run_4models_1pass_reason_on.sh:33` |
| Max tasks in live list (`MAX_TASKS`) | 12 | `multiagent.py:72`, `run_4models_1pass_reason_on.sh:34` |
| Manager temperature | **0.2** for manage / **0.3** for plan / **0.4** for ideation / **0.2** for worker | `multiagent.py:239, 271, 333, 415` |
| Single-call temperature | **0.2** | `multiagent.py:638` |
| Output token cap (`ESCALATION_CLOUD_MAX_TOKENS`) | **128,000** (the common cap; Fable 5 hard-caps at 128K, so 128K is the only like-for-like setting across all four first-party arms) | `run_4models_1pass_reason_on.sh:36`, `orchestrator.py:101` |
| Qwen3.8-27B single arm as-generated cap | **250,000** (then cap-matched back to 128K via `capmatch_q38.py`) | README §3.2, `capmatch_q38.py:35` |
| Anthropic effort | **"high"** (pinned explicitly) | `orchestrator.py:106` |
| DashScope thinking budget | **100,000** tokens (mandatory — see warning at `orchestrator.py:90–96` and `:513–516`) | `run_4models_1pass_reason_on.sh:156` |
| Wall-clock cap per cloud call (`ESCALATION_CLOUD_TIMEOUT`) | **7,200 s** (2 h) per run driver | `run_4models_1pass_reason_on.sh:113, 130, 157, 169` |
| Cloud rerouting attempts (`ATTEMPTS`) | **16** | `orchestrator.py:189` |
| Sample-test subprocess timeout | **10 s** | `multiagent.py:495` |
| Worker notes size bound (`MAX_PLAN_CHARS * 2`) | **8,000 chars** | `multiagent.py:450` |
| Plan size bound (`MAX_PLAN_CHARS`) | 4,000 chars | `multiagent.py:197` |
| Answer size bound (`MAX_ANSWER_CHARS`) | 20,000 chars | `multiagent.py:194` |
| Concurrency per arm (`--parallel`) | 4 (q38), 32 (luna), 50 (fable5), 48 (muse local vLLM) | run scripts |

### E.4 Data preprocessing / tokenization

- **Prompt assembly** (`run_bench.py:98–105`): `build_code_prompt(problem)` returns `"### Question\n{question_content}\n\n### Format: {_FMT_STARTER or _FMT_STDIN}\n"` (the `_FMT_*` strings are inlined from `lcb_runner.prompts.code_generation.PromptConstants` to avoid the cwd-relative few-shot file load that an `import` would trigger — `run_bench.py:88–95`).
- **Code extraction** (`run_bench.py:146`): `extract_code(raw, LMStyle.ClaudeCode)` from the vendored LCB harness. The scaffold itself wraps its returned code in a ```python fenced block (`multiagent.py:618`), so the LCB extractor pulls the fenced block.
- **Section parsing** (`multiagent.py:143–159`): model replies are split on lines matching `^#{1,3}\s*([A-Za-z_]+)\s*$` OR `^\*\*([A-Za-z_]+)\*\*\s*:?\s*$` OR `^([A-Z_]{3,})\s*:\s*$`. Strict-format mode (`STRICT_FORMAT=1`) prepends an explicit `"THE FORMAT IS MANDATORY … Begin your reply with the literal line '### {first}'…"` addendum (lines 64–71) to force models that would otherwise solve the problem directly to use the manager's response format.
- **Thinking stripping** (`multiagent.py:133–` blocks are removed before parsing sections (this is for models that emit CoT outside the `reasoning` field).
- **No tokenization at the orchestrator layer** for normal paths — tokenization is delegated to the provider's API. The only explicit tokenization is in `capmatch_q38.py:50–55`, which calls a vLLM `/tokenize` endpoint on `Qwen/Qwen3.8-27B-FP8` to do token-exact truncation.

### E.5 Loss function

**N/A — no training.** The closest analogue is the **grading metric**: pass@1 on the LiveCodeBench hidden test suite. `_passed(res0)` (`run_bench.py:167–170`): if the result is a list/tuple, every element must be `> 0` and the list must be non-empty; else the result must be truthy. `codegen_metrics` runs the solution against the problem's hidden tests via the fixed `MockBuffer` `testing_util.py`.

### E.6 Evaluation metrics

- **Primary metric**: pass@1 on the 100-problem LiveCodeBench Hard subset (`release_v6`, ids pinned via `lcb100_hardest_v6.json`), with `num_process_evaluate=8` (or up to 96 in `regrade.py`) parallel grading workers.
- **Status classification** (`run_bench.py:68–82`): `ok` (parseable answer) / `infra` (gateway gave up; EXCLUDED from pass@1) / `error` (Python exception) / `truncated` (finish_reason=length or any truncated call) / `empty_stop` (finished cleanly, no parseable answer or refusal).
- **Cost accounting**: `runs/per_problem_tokens.json` holds per-problem, per-pass token counts (input + output, including discarded retries); `run_bench_script/extract_tokens.py` rebuilds it. Cost figures in §2.2 use list rates from `paper/fig-cost-tables.tex` (Qwen3.8-27B \$0.35/\$2.75 per MTok in/out; GPT-5.6-Luna \$0.20/\$1.20; GPT-5.6-Terra \$2/\$12; Fable 5 \$10/\$50).
- **Statistical tests** (plot scripts): paired sign-flip permutation tests, unit = problem (n = 100), Holm-corrected within each family of 3; 95% CI across the 5 passes via `pass_ci` (imported from `plot_16k_reason_off_5_pass.py`). See `plot_4new_5pass_reason_on.py:6–17` and `fig-4new-5pass.tex` for the exact p-values reported.

### E.7 Hardware assumptions

- **No GPUs are required to run the scaffold** — the paper's headline "or on a Single GPU" refers to the self-hosted Qwen3.8-27B vLLM arm, which the author ran on their own hardware (`http://localhost:8216` per `run_4models_1pass_reason_on.sh:88–119`). The script comments mention `~3,065 tok/s` at `--parallel 48` and `772,065 KV tokens per replica across 3 replicas` (lines 92–100) — i.e. 3× vLLM replicas behind litellm.
- The four first-party arms are remote-API arms (OpenAI, Anthropic, DashScope); the only local hardware is for the `muse` (Qwen3.6-27B-vllm) arm and for the `capmatch_q38.py` tokenizer (vLLM on :8215 with `Qwen/Qwen3.8-27B-FP8`).
- The README header (the 2026-08-27 commit's only diff) added a tagline emphasising "Single GPU" usage; this is marketing copy referring to the open-weights Qwen3.8-27B arm, not a hardware requirement of the scaffold itself.
- No dtype is specified anywhere in the scaffold — dtype is delegated to the vLLM serving stack.

### E.8 Distributed training setup

**N/A — no training.** The scaffold is single-process Python with a `ThreadPoolExecutor` of `BENCH_PARALLEL` workers (one per problem, each problem's multi-agent loop is serial within its thread). The grading step (`codegen_metrics`) uses `pebble`'s multiprocessing pool with `num_process_evaluate=8` (or up to 96 in `regrade.py`). No DDP/FSDP/DeepSpeed/accelerate.

---

## F. Fidelity to Paper

The paper is `paper/zero_shot_self_orchestration_with_ledger_based_control_for_improved_llm_coding_performance_2026-08-25.tex` (the `.pdf` is also vendored). Section numbers below refer to the paper.

| Aspect | Status | Citation |
|---|---|---|
| **Manager–worker scaffold over shared filesystem workspace** | **CONFIRMED** — `multiagent.py:526–619` implements exactly the loop described in paper §3.1 step 1–7. The shared workspace files (task.md, plan.md, notes.md, solution.py/answer.md, transcript.jsonl, tasks.json) match paper §3.1's description. | `multiagent.py:526–619` |
| **Same model in every role, fresh context each call** | **CONFIRMED** — every role calls `_chat(ws, role, [...], temperature=…)` which calls `orchestrator.chat(MODEL, …)`; the model is a single global `MODEL = os.environ.get("MULTIAGENT_MODEL", …)` (`multiagent.py:41`); each call's `messages` list is built from scratch each time. | `multiagent.py:41, 107–128, 236–239, 268–271, 325–333, 408–415, 635–638` |
| **Round budget 10 (v2) vs 4 (v1)** | **CONFIRMED** — `MAX_ITERS = int(os.environ.get("MULTIAGENT_MAX_ITERS", "10"))` in v2 (`multiagent.py:42`), default 4 in v1 (`codebase/v1-be9dfa2/escalation/multiagent.py:33`). | `multiagent.py:42` |
| **Sample-test verifier (v2 only)** | **CONFIRMED** — `_run_samples` (`multiagent.py:473–507`) runs `solution.py` against `prob.public_test_cases`'s stdin tests in a subprocess; `_sample_feedback` (`multiagent.py:510–521`) turns the result into a sentence; the loop wires the verdict into `summary` (`multiagent.py:574–578`) and the hard gate (`multiagent.py:583–587`) overrides `done` when samples fail. v1 has none of this. | `multiagent.py:473–521, 574–587` |
| **Cut-off summarizer (v2 only)** | **CONFIRMED** — `_summarize_cutoff` (`multiagent.py:353–368`) is called only when `wmeta.get("finish_reason") == "length"` (`multiagent.py:453–465`). v1 has no equivalent. | `multiagent.py:353–368, 453–465` |
| **Size bounds on workspace files (v2 only)** | **CONFIRMED** — `MAX_PLAN_CHARS = 4000` (line 197), `MAX_ANSWER_CHARS = 20000` (line 194); plan.md is bounded on write (line 247), notes.md is bounded on write (lines 281, 450), the worker's NOTES section is REWRITTEN not appended (lines 436–450, comment 437–442). v1's `_worker` appends (`codebase/v1-be9dfa2/escalation/multiagent.py:305`) and `_primary_plan` writes the entire reply (`v1:177`). | `multiagent.py:194–197, 247, 281, 436–450` |
| **Frozen problem id pinning (v2 only)** | **CONFIRMED** — `codebase/v2-current/escalation/lcb100_hardest_v6.json` is the pinned list of 100 ids; `run_bench.py:130–133` reads it; `run_4models_1pass_reason_on.sh:51–61` `check()` function verifies `got == want` exactly (order included). v1 selects "latest 100 hard" at run time (`run_bench.py:117–128`); the pinned file is only under `v2-current/`. | `lcb100_hardest_v6.json`, `run_bench.py:130–133`, `run_4models_1pass_reason_on.sh:51–61` |
| **§3.3 evaluator fix (stateful `MockBuffer.readline`)** | **CONFIRMED** — `codebase/livecodebench/lcb_runner/evaluation/testing_util.py:94–116` rewrites `MockBuffer` with `self._bytesio = BytesIO(self.inputs)` and `readline` returning `self._bytesio.readline(*args)` (stateful). The class docstring explicitly says "upstream's readline returned line 1 every call". README §2 ("This copy carries the evaluator fix of §3.3") confirms intent. | `testing_util.py:94–116` |
| **§3.2 cap-matching for Qwen3.8-27B single arm** | **CONFIRMED** — `codebase/v2-current/escalation/capmatch_q38.py` truncates the 250k-capped single generations to 128k token-exact using vLLM's `/tokenize` and `/detokenize` endpoints; `CAP = 128_000` (line 35); `MODEL = "Qwen/Qwen3.8-27B-FP8"` (line 36). The plot script `plot_4new_5pass_reason_on.py:65` reads `q38_single_p%d.cap128k.regraded.json` for the Qwen3.8-27B single arm. | `capmatch_q38.py:35–91`, `plot_4new_5pass_reason_on.py:65` |
| **§3.3 regrade path** | **CONFIRMED** — `codebase/v2-current/escalation/regrade.py` re-grades stored `code` fields against the fixed evaluator; writes `<name>.regraded.json`; preserves `passed_before_regrade` and `pass@1_before_regrade` (lines 88, 97). README §3 ("Every figure and table in the paper reads the `.regraded.json` files") confirms. | `regrade.py:88–105` |
| **Manager ≈ 3× the token bill of single** | **CONFIRMED via the cost table** — `paper/fig-cost-tables.tex` lists Qwen3.8-27B: single \$20.44/pass, manager \$51.75/pass (2.5×); GPT-5.6-Luna: \$0.41 vs \$1.50 (3.7×); GPT-5.6-Terra: \$3.41 vs \$11.71 (3.4×); Fable 5 single \$61.11 (no manager). The abstract's "roughly triples" is consistent with these. | `paper/fig-cost-tables.tex` |
| **Qwen3.8-27B +23.4, GPT-5.6-Luna +10.6, GPT-5.6-Terra +8.0 deltas** | **PARTIAL** — The deltas themselves are computed in `plot_4new_5pass_reason_on.py` and printed to stdout before the PNG is written. The paper abstract quotes them as the headline result. I did not re-run the plot script to verify the exact printed numbers (would require `uv` + matplotlib + numpy + scipy + the runs/ tree mounted at the symlink path the script expects). The `lcb100_5pass_table.md` summary matches the abstract's magnitudes (e.g. `q35 -1 to -9` matches the abstract's "Qwen3.6-35B -1 to -9 with reasoning off"). | `paper/…tex:130–135`, `plot_4new_5pass_reason_on.py:65–77`, `lcb100_5pass_table.md` |
| **Opus 5 + manager = 91% in one pass** | **CONFIRMED** — `runs/128k-reasoning-on-1pass/results/opus_multiagent.json` exists (and `opus_single.json`); the `lcb100_5pass_table.md` shows `opus manager ON·128k = 91`. | `runs/128k-reasoning-on-1pass/results/opus_multiagent.json`, `lcb100_5pass_table.md` |
| **Qwen3.5-9B with reasoning on unusable (§4.5 limitation)** | **CONFIRMED** — `runs/q9-reasoning-on-archived/` exists with 16 files (attempts archived rather than graded); `lcb100_5pass_table.md` footnote ² says "q9 (qwen3.5-9b) with thinking on returns reasoning-only replies (content=null, `finish=error`) on OpenRouter — no token/effort setting fixes it." | `runs/q9-reasoning-on-archived/` (16 files), `lcb100_5pass_table.md` footnote ² |
| **GPT-5.6-Terra with manager nearly matches Fable 5 single (85.0 vs 87.4, p=0.59)** | **PARTIAL** — the plot script `plot_4new_5pass_reason_on.py` computes the bracket and p-value; the abstract quotes the numbers; I did not re-run the plot to verify the printed p-value, but the file paths the script reads (`terra_multiagent_p%d.regraded.json` for the manager; `fable5_single_p%d.regraded.json` for Fable 5 single) all exist in `runs/`. | `paper/…tex:135–137`, `plot_4new_5pass_reason_on.py:64–72` |
| **No training, no per-benchmark tuning** | **CONFIRMED** — the scaffold is entirely prompt + control-flow; the only "tuning" is the prompt templates in `orchestrator.py:548–630`, which are reused across all benchmarks (LCB, AIME, MATH-500, GPQA, HLE) without per-benchmark prompt modification. The benchmark-specific differences are the answer-extraction regexes in `run_bench.py` (e.g. `extract_answer_int` for AIME, `_MCQ_RE` for HLE MCQ), which are post-hoc parsing, not model tuning. | `orchestrator.py:548–630`, `run_bench.py:192–300, 460–542` |

### Notable gap

- **CONTRADICTS (mild)** — The README §2 says of v2: "One post-paper fix is present in v2. `orchestrator.py` now compares a suspected provider clamp against the cap actually sent rather than the configured cap." This is the `cap_used = cur_max or CLOUD_MAX_TOKENS` fix at `orchestrator.py:312`. The fix is *post-paper* — it did not affect the plotted runs (it only bites when a 400/context error shrinks the cap mid-run, which happened to a model not in the paper, per README). So the code in the repo at HEAD is one small fix ahead of the code that produced the paper's numbers. This is **explicitly disclosed** in the README, so it's not a hidden contradiction — but a third-party re-run from HEAD could in principle diverge from the paper's numbers on exactly the affected model.

---

## G. Execution / Reproducibility

### G.1 Pinned dependencies?

- The vendored LiveCodeBench has `codebase/livecodebench/pyproject.toml` with `anthropic>=0.42.0`, `openai>=1.59.6`, `datasets>=3.2.0`, `pebble>=5.1.0`, `torch>=2.3.0`, `vllm>=0.5.0.post1`, etc. — `>=` bounds, not pinned; `uv.lock` and `poetry.lock` are present but unlocked.
- The paper's scaffold (`codebase/v2-current/escalation/*.py`) has **NO `pyproject.toml`, `setup.py`, `requirements.txt`, or `environment.yml` of its own**. The README §4 invocation `uv run --project /home/persis/model-test python escalation/run_bench.py` implies the dependencies live in a uv project rooted at `/home/persis/model-test` (the author's machine path). That project file is NOT in this repo.
- Plot scripts assume `uv run --with matplotlib --with numpy --with scipy python plot_*.py` (no `--project`), so matplotlib/numpy/scipy are ad-hoc.
- **The Qwen3.8-27B weights are referenced by HF id `Qwen/Qwen3.8-27B-FP8`** in `capmatch_q38.py:36` but NOT vendored — a third party must download them and stand up a vLLM `/tokenize` endpoint at `http://localhost:8215`.

### G.2 Hardcoded paths or keys?

- `/home/persis/model-test` is hardcoded in:
  - `run_bench.py:5` (the docstring's usage line)
  - `run_4models_1pass_reason_on.sh:29` (`cd /home/persis/model-test`)
  - `run_fable5_5pass_single.sh:38` (`cd /home/persis/model-test`)
  - `regrade.py:12` (docstring)
  - `capmatch_q38.py:21` (docstring)
  - `run_4models_1pass_reason_on.sh:88` (`/home/persis/litellm/config.yaml` for the litellm master_key)
  - Sample records (`_meta/sample_q38_single_p1.json` records carry `"ws": "/home/persis/model-test/escalation/runs/4models-1pass-reason-on/ws/q38_single_p1/..."` per problem).
  These are author-machine paths. They will NOT work on a third-party machine without editing the run scripts and the `WS_ROOT` env var. The README does NOT mention this — a third party has to discover it by trying.
- No API keys are present (verified by `.gitignore:1–4` excluding `.env*`, `*.key`, `.credentials*`; the README top says the tree was scanned for key-shaped strings before packing).
- `HF_HOME=/storage/persis/hf_cache` is set in both run scripts (`run_4models_1pass_reason_on.sh:32`, `run_fable5_5pass_single.sh:41`) — another author-machine path.

### G.3 CLI entry points

- **`python escalation/run_bench.py --engine {escalate,multiagent,single} --only {lcb,aime,math500,gpqa,hle} --lcb N --ids-file PATH --parallel N --out results.json`** — `run_bench.py:545–597`. The default `--ids-file` is `os.path.join(ROOT, "hard100.json")` which does NOT exist in this repo (line 553) — the run drivers override this to `escalation/lcb100_hardest_v6.json`.
- **`python escalation/regrade.py <results.json> ...`** — `regrade.py:108–125`.
- **`python escalation/capmatch_q38.py`** — `capmatch_q38.py:94–122`.
- **`uv run --with matplotlib --with numpy --with scipy python escalation/run_bench_script/plot_<X>.py`** — six plot scripts, one per figure.
- **`bash escalation/run_bench_script/run_4models_1pass_reason_on.sh`** and **`bash escalation/run_bench_script/run_fable5_5pass_single.sh`** — the two top-level run drivers.

### G.4 Tests? Linting? CI?

- **No tests** are present anywhere in the repo. No `tests/`, `test_*.py`, or `conftest.py`.
- **No linting config** (no `.flake8`, `ruff.toml`, `.pylintrc`, `mypy.ini`).
- **No CI**: no `.github/workflows/`, no `Makefile`, no `Dockerfile`, no `tox.ini`. (Verified via `_meta/all_tracked_files.txt` — none of those paths appear.)
- The README §4 documents the reproduce-the-figures commands but does NOT document a `pytest`/lint/test step.

### G.5 Random seeds?

- `run_bench.py::run_gpqa` uses `random.Random(42)` for option shuffle (line 358) — seeded.
- `run_bench.py::run_hle` uses `random.Random(42).sample(...)` for subset selection (line 505) — seeded.
- The manager's `temperature=0.2–0.4` calls are NOT seeded (the OpenAI / Anthropic / Groq APIs do not accept a seed parameter in the path used here; the scaffold does not set one). Pass-to-pass variance is therefore real — the paper explicitly uses 5 passes and 95% CIs across them, treating ~3pp deltas as noise (see `lcb100_5pass_table.md` "Pass-to-pass noise on this set is ~3.0pp, so treat deltas < ~4pp as noise").
- `extract_tokens.py` and the plot scripts are deterministic given the `runs/` tree.

### G.6 Data download scripts?

- **No explicit data-download scripts**. The `livecodebench` harness loads its dataset via `load_code_generation_dataset(release_version=os.environ.get("LCB_RELEASE", "release_v1"))` (`run_bench.py:114`), which fetches from the HuggingFace Hub (the README §4 says `LCB_RELEASE=release_v6` for the paper's runs). The run scripts set `LCB_RELEASE=release_v6` and `HF_HOME=/storage/persis/hf_cache`, but they do NOT pre-fetch the dataset; the first run will download it on demand (HF cache miss).
- For AIME / MATH-500 / HLE: `datasets.load_dataset(...)` is called inline (`run_bench.py:210, 331, 486`); HLE is gated on the Hub (`cais/hle` requires terms acceptance).
- For GPQA: `csv.DictReader(open(path))` reads a local CSV at `data/gpqa_diamond.csv` (`run_bench.py:347`), which is NOT vendored in this repo (the path is `os.path.join(HERE, "data", "gpqa_diamond.csv")` and no such file appears in `_meta/all_tracked_files.txt`).

### G.7 Pretrained checkpoints referenced?

- `Qwen/Qwen3.8-27B-FP8` (HF id) — `capmatch_q38.py:36`, used ONLY for tokenization (offline).
- The routed model ids (`gpt-5.6-luna`, `gpt-5.6-terra`, `claude-opus-5`, `claude-fable-5`, `qwen3.8-max`, `qwen3.6-27b-vllm`) are provider-side identifiers; the weights themselves are not vendored or downloaded by this repo.

---

## H. Open Issues / TODOs / Code Comments

- **GitHub Issues / PRs**: Not retrievable (GitHub API rate-limited from this host). The clone shows a single commit on the default branch, suggesting the repo was pushed once and not iterated. The README §5 explicitly lists what was *deliberately left out* (credentials, `.gitignore`, one-off `aggregate_big.py` and `run_big.sh`, superseded reruns like `.clampbug`/`.pre-notesfix`/`.pre-planfix`, `LiveCodeBench/output/` and `LiveCodeBench/claude_transcripts/` from a separate experiment, and dark-theme chart variants).
- **Code comments / TODOs**: The scaffold has *extensive* post-mortem comments (NOT `# TODO` markers, but inline history notes). Notable examples:
  - `multiagent.py:43–55` — documents the `STRICT_FORMAT` "auto" detection being insufficient for litellm routes whose name says nothing about the underlying weights, leading to manager collapse on `muse`.
  - `multiagent.py:243–247` — "Measured 2026-08-13 on muse: two problems carried a 205KB and a 483KB plan.md, overflowed the window on every later call, and produced no code at all."
  - `multiagent.py:437–446` — "append-only growth is what pushed manager prompts past ~91k tokens against a 131,072 window — the point where no max_tokens shrink can make the request fit and the call fails outright (8 problems, 26 exhausted calls, in the 2026-08-12 muse manager run)."
  - `multiagent.py:487–493` — explains why the sample-test subprocess uses `sys.executable` rather than bare `python3` (a bare `python3` made every numpy solution "fail" its samples, flipping the manager's hard gate).
  - `orchestrator.py:303–311` — "Cost muse's manager p3 sixteen hours on a single problem (arc191_c, 15 of 16 attempts discarded as 'clamped'), while luna and terra — which never shrink, having context to spare — were untouched." This is the post-paper fix the README §2 discloses.
  - `orchestrator.py:90–96` — DashScope warning: "max_tokens does not bound thinking on this provider … measured: max_tokens=100 generated for 5 minutes and never returned; a real prompt ran past 72 min."
- **`codebase/livecodebench/lcb_runner/runner/main.py:132–144`** — a commented-out block (dead code) that would have re-extracted code with `LMStyle.Gemini` if `"def solve()"` was found. The comment block is intact but unused.
- **No `# TODO` / `# FIXME` / `# XXX` markers** are present in the escalation code (verified by reading every line of the 5 v2-current Python files).

---

## I. Notable Strengths

1. **Reproducibility by construction**: every figure in the paper is recomputed from `runs/*.regraded.json` (and `*.cap128k.regraded.json` for the Qwen3.8-27B single arm) by `uv run --with matplotlib --with numpy --with scipy python run_bench_script/plot_<X>.py`. The README §4 lists the exact command per figure. The `lcb100_hardest_v6.json` pinning + the `check()` function in the run scripts (`run_4models_1pass_reason_on.sh:51–61`) means any drift from the pinned 100 ids fails loudly.
2. **Auditability**: `regrade.py` preserves `passed_before_regrade` and `pass@1_before_regrade` on every record and on the file-level summary, so the §3.3 evaluator-bug fix is auditable rather than silent. `capmatch_q38.py` clears pass@1 on the files it writes so a stale value cannot be read; `regrade.py` recomputes it on the fixed evaluator.
3. **Transparency about infrastructure failure**: the `infra` status class (`run_bench.py:73–77`) is excluded from pass@1, with both the graded rate and the count set aside reported (line 178–183). This prevents silent pass@1 inflation from a provider that gave up.
4. **Transparency about model behaviour**: every model call is transcripted (`multiagent.py:107–128`); the transcript records `reasoning`, `reasoning_is_summary`, `thinking_blocks`, `attempts`, `discarded`, `infra_exhausted`, so a third party can reconstruct exactly what was sent, what came back, what was rerouted away, and whether the recorded "reasoning" is the real chain of thought (vLLM/DashScope) or Anthropic's summary (Anthropic/Fable 5/Opus 5).
5. **Engineering rigour in the comments**: every non-obvious decision in `multiagent.py` and `orchestrator.py` has a comment explaining what failure mode it prevents, with concrete dated examples from prior runs (e.g. the 2026-08-12 muse manager run with 26 exhausted calls across 8 problems). This is rare in research code.
6. **Honest handling of Fable 5's quirks**: `run_fable5_5pass_single.sh:14–36` documents in detail that Fable 5 cannot disable thinking (400 on `thinking:{type:disabled}`), cannot have a thinking budget (400 on `thinking:{type:enabled,budget_tokens:N}`), caps output at 128K (the model's ceiling, not a choice), and refuses some requests (HTTP 200, `stop_reason=refusal`) — and that refusals are *scored, not retried, and not fallen back*, because "a benchmark cell labelled Fable 5 must contain Fable 5's outcome".
7. **The §3.3 evaluator fix is contributed back to the vendored LiveCodeBench copy**: `codebase/livecodebench/lcb_runner/evaluation/testing_util.py:94–116` `MockBuffer.readline()` is now stateful, so solutions reading multi-line input via `sys.stdin.buffer.readline()` grade correctly. The README §2 explicitly calls this out and `regrade.py` makes the fix measurable against the numbers it replaces.
8. **Pass-to-pass noise is acknowledged**: `lcb100_5pass_table.md` explicitly says "Pass-to-pass noise on this set is ~3.0pp, so treat deltas < ~4pp as noise" — and the plot scripts compute paired permutation tests with Holm correction rather than reporting bare mean deltas.
9. **No contamination**: the paper selects the "100 latest hard" LCB problems (`release_v6`), which the README §2 and the LCB README ("continuously collects new problems over time from contests … May 2023 and March 2024") position as contamination-free.

---

## J. Notable Weaknesses / Risks

1. **No top-level LICENSE file**: the only license in the repo is `codebase/livecodebench/LICENSE` (MIT, Copyright 2024 LiveCodeBench). The paper-bundle code (`codebase/v2-current/`, `codebase/v1-be9dfa2/`, `paper/`) ships with no license grant. A third party has no clear legal right to reproduce, modify, or redistribute the scaffold. **(No file path: this is an *absent* file.)**
2. **Hardcoded author-machine paths everywhere**:
   - `run_4models_1pass_reason_on.sh:29` `cd /home/persis/model-test`
   - `run_fable5_5pass_single.sh:38` `cd /home/persis/model-test`
   - `run_bench.py:5` `uv run --project /home/persis/model-test python …`
   - `run_4models_1pass_reason_on.sh:32` `export HF_HOME=/storage/persis/hf_cache`
   - `run_4models_1pass_reason_on.sh:88` `LITELLM_KEY=… grep -m1 'master_key:' /home/persis/litellm/config.yaml …`
   - `regrade.py:12` and `capmatch_q38.py:21` repeat the `/home/persis/model-test` path in their docstrings.
   The README §4 reproduce commands do NOT mention these — a third party must discover and edit them by hand.
3. **No `pyproject.toml` / `requirements.txt` / `environment.yml` for the scaffold**: the vendored LiveCodeBench has one, but the paper's scaffold (the actual research artefact) does not. A third party must reverse-engineer the dependencies from imports. The README §4 invocation `uv run --project /home/persis/model-test` references an unvendored uv project.
4. **No tests, no linting, no CI**: there is no `tests/`, `test_*.py`, `pytest.ini`, `.flake8`, `ruff.toml`, `mypy.ini`, `.github/workflows/`, `Makefile`, or `Dockerfile` anywhere in the repo. (Verified via `_meta/all_tracked_files.txt`.) A regression in the scaffold would not be caught.
5. **Default `--ids-file` is missing**: `run_bench.py:553` defaults to `os.path.join(ROOT, "hard100.json")`, which does NOT exist in the repo. A third party who runs `python escalation/run_bench.py --only lcb` without `--ids-file` gets a `FileNotFoundError`. The README §4 example always passes `--ids-file escalation/lcb100_hardest_v6.json`, masking this.
6. **Single commit on the default branch**: the entire repo was pushed in one commit (`6d7a143b`, 2026-08-27). There is no git history of how the scaffold evolved; the v1-vs-v2 differences are visible only as two parallel directories, not as a diff. The README §2 explains the four named differences but does not provide a `diff v1 v2` script.
7. **The `escalate` engine is dead code in the paper's narrative**: `orchestrator.py:637–697` (`solve_layer` + `escalate`) implements a separate solve↔critic ladder that is NOT used by any of the paper's reported runs (all use `--engine multiagent` or `--engine single`). It's carried in the file because `run_bench.py` imports `escalate` as the default `SOLVE` and overwrites it only when `--engine` is set. A third party might miss that the ladder is not part of the paper's results.
8. **`HLE_SPEC`, `MATH_SPEC`, `MATH500_SPEC`, `GPQA_SPEC` are unused by the paper**: the paper is LCB-only. These four specs and the corresponding `run_aime` / `run_math500` / `run_gpqa` / `run_hle` functions in `run_bench.py` are present (lines 192–542) but irrelevant to the paper's claims. They inflate the file by ~400 lines.
9. **`runs/128k-reasoning-off-1pass/results/mm3_multiagent.json.corrupt.bak` is tracked**: a `.corrupt.bak` backup file is committed (visible in `_meta/all_tracked_files.txt`). This signals a file was corrupt at some point and was hand-recovered; the `.bak` should not be in version control.
10. **The post-paper fix in v2 (`orchestrator.py:312`) means HEAD is one fix ahead of the paper's runs**: per README §2, this fix did not affect the plotted runs (it only bites when a 400/context error shrinks the cap mid-run, which happened to a model not in the paper). The fix is *explicitly disclosed*, so this is a *mild* risk, but a third party re-running from HEAD could in principle diverge from the paper on exactly the affected model.
11. **`codebase/v2-current/escalation/runs` is a symlink to `../../../runs`**: it works on the author's machine where the symlink target resolves to the repo's own `runs/`, but the symlink is preserved by `cp -r` *only if the copy tool preserves symlinks*. A naive `tar` or `cp -rL` will break it. The README §3 warns: "extract with a tool that preserves symlinks, or re-point the paths at the top of each script."
12. **The plot scripts depend on the symlink resolving**: `plot_4new_5pass_reason_on.py:54–58` uses `ESC = os.path.dirname(HERE)` and `R4 = f"{ESC}/runs/4models-1pass-reason-on/results"`, which works ONLY if `codebase/v2-current/escalation/runs` (the symlink) resolves to `runs/` at the repo root. A third party who relocates the repo or extracts without preserving symlinks must hand-patch the path constants at the top of each plot script.
13. **Transcript files (`transcript.jsonl`) are git-ignored**: `.gitignore:6–8` ignores `transcript.jsonl` (~1.4 GB across ~9.9k files per the comment). This means the *rawest* evidence of what the model said is NOT in the repo — only the curated workspace files (`task.md`, `plan.md`, `notes.md`, `solution.py`, `answer.md`, `tasks.json`) and the graded `results/*.json` are. A third party cannot replay a transcript to verify the `code` field in `results/<name>.json` matches what the model actually produced. `capmatch_q38.py:60–67` reads `transcript.jsonl` from the workspace path stored in the record's `ws` field, so cap-matching REQUIRES the transcripts to have been preserved on the author's machine — which they were, but they are not in this repo.

---

## K. Raw Manifest

Local mirror root: `/home/z/my-project/review-by-GLM/sources/GVS5H/`

### Top-level (3 files)

| Local path | Source path | Type | Notes |
|---|---|---|---|
| `README.md` | `README.md` | text | 217 lines; bundle overview, §1–§5 |
| `.gitignore` | `.gitignore` | text | 31 lines; ignores `.env*`, `*.key`, `.credentials*`, `transcript.jsonl`, Python build, LaTeX build |
| `_meta/repo_meta.json` | (GitHub API) | JSON | Saved the API's rate-limit-error response — actual repo metadata was NOT retrievable. |

### `codebase/v2-current/escalation/` (the paper's main scaffold; 20 files)

| Local path | Source path | Type | LOC |
|---|---|---|---|
| `codebase/v2-current/escalation/multiagent.py` | same | Python | 644 |
| `codebase/v2-current/escalation/orchestrator.py` | same | Python | 698 |
| `codebase/v2-current/escalation/run_bench.py` | same | Python | 601 |
| `codebase/v2-current/escalation/regrade.py` | same | Python | 130 |
| `codebase/v2-current/escalation/capmatch_q38.py` | same | Python | 127 |
| `codebase/v2-current/escalation/lcb100_hardest_v6.json` | same | JSON | 100 ids |
| `codebase/v2-current/escalation/lcb100_5pass_table.md` | same | Markdown | summary table |
| `codebase/v2-current/escalation/run_bench_script/extract_tokens.py` | same | Python | 75 |
| `codebase/v2-current/escalation/run_bench_script/make_figures_tex.py` | same | Python | 259 |
| `codebase/v2-current/escalation/run_bench_script/plot_128k_reason_off_1_pass.py` | same | Python | 202 |
| `codebase/v2-current/escalation/run_bench_script/plot_128k_reason_on_1_pass.py` | same | Python | 242 |
| `codebase/v2-current/escalation/run_bench_script/plot_16k_reason_off_5_pass.py` | same | Python | 640 |
| `codebase/v2-current/escalation/run_bench_script/plot_4new_5pass_reason_on.py` | same | Python | 356 |
| `codebase/v2-current/escalation/run_bench_script/plot_agent_loop_flowchart.py` | same | Python | 328 |
| `codebase/v2-current/escalation/run_bench_script/plot_bars.py` | same | Python | 193 |
| `codebase/v2-current/escalation/run_bench_script/plot_cost_5_pass.py` | same | Python | 507 |
| `codebase/v2-current/escalation/run_bench_script/plot_cost_vs_score.py` | same | Python | 225 |
| `codebase/v2-current/escalation/run_bench_script/plot_q38_vs_fable5_5_pass.py` | same | Python | 337 |
| `codebase/v2-current/escalation/run_bench_script/run_4models_1pass_reason_on.sh` | same | Bash | 176 |
| `codebase/v2-current/escalation/run_bench_script/run_fable5_5pass_single.sh` | same | Bash | 150 |
| `codebase/v2-current/escalation/runs` | same | **symlink** to `../../../runs` | preserved as symlink; resolves to repo-root `runs/` if the repo's tree is intact |

### `codebase/v1-be9dfa2/escalation/` (the original scaffold; 3 files)

| Local path | Source path | Type | LOC |
|---|---|---|---|
| `codebase/v1-be9dfa2/escalation/multiagent.py` | same | Python | 397 |
| `codebase/v1-be9dfa2/escalation/orchestrator.py` | same | Python | 349 |
| `codebase/v1-be9dfa2/escalation/run_bench.py` | same | Python | 582 |

### `codebase/livecodebench/` (vendored benchmark harness; 58 files)

Selected key files (full list in `_meta/all_tracked_files.txt`):

| Local path | Source path | Type | Notes |
|---|---|---|---|
| `codebase/livecodebench/README.md` | same | Markdown | LCB README |
| `codebase/livecodebench/ERRATA.md` | same | Markdown | known LCB issues |
| `codebase/livecodebench/LICENSE` | same | text | MIT, Copyright (c) 2024 LiveCodeBench |
| `codebase/livecodebench/pyproject.toml` | same | TOML | dependencies |
| `codebase/livecodebench/poetry.lock` | same | text | (vendored) |
| `codebase/livecodebench/uv.lock` | same | text | (vendored) |
| `codebase/livecodebench/lcb_sky.yml` | same | YAML | (vendored) |
| `codebase/livecodebench/lcb_runner/evaluation/testing_util.py` | same | Python | **§3.3 fix: stateful MockBuffer** |
| `codebase/livecodebench/lcb_runner/evaluation/compute_code_generation_metrics.py` | same | Python | `codegen_metrics` (called by `run_bench.py` and `regrade.py`) |
| `codebase/livecodebench/lcb_runner/benchmarks/code_generation.py` | same | Python | `load_code_generation_dataset` (called by `run_bench.py` and `regrade.py`) |
| `codebase/livecodebench/lcb_runner/utils/extraction_utils.py` | same | Python | `extract_code` |
| `codebase/livecodebench/lcb_runner/lm_styles.py` | same | Python | `LMStyle.ClaudeCode` (the extraction style `run_bench.py:146` uses) |
| `codebase/livecodebench/lcb_runner/runner/main.py` | same | Python | the upstream LCB runner (not used by the paper's main path) |
| `codebase/livecodebench/lcb_runner/runner/*.py` | (16 other runner modules) | Python | upstream LCB per-provider runners (not used by the paper's main path) |
| `codebase/livecodebench/lcb_runner/evaluation/*.py` | (5 other eval modules) | Python | upstream LCB eval helpers |
| `codebase/livecodebench/lcb_runner/benchmarks/*.py` | (2 other benchmark modules) | Python | upstream LCB benchmark loaders |
| `codebase/livecodebench/lcb_runner/prompts/*.py` | (4 prompt modules) | Python | upstream LCB prompts |
| `codebase/livecodebench/lcb_runner/prompts/few_shot_examples/generation/*.json` | (2 few-shot files) | JSON | few-shot examples (not used by the paper) |
| `codebase/livecodebench/assets/images/*.png` | (6 images) | PNG | LCB README images |

### `paper/` (the paper; 20 files)

| Local path | Source path | Type | Notes |
|---|---|---|---|
| `paper/zero_shot_self_orchestration_with_ledger_based_control_for_improved_llm_coding_performance_2026-08-25.tex` | same | LaTeX | the paper source |
| `paper/zero_shot_self_orchestration_with_ledger_based_control_for_improved_llm_coding_performance_2026-08-25.pdf` | same | PDF | the built paper |
| `paper/fig-4new-5pass.tex` | same | LaTeX | auto-generated by `make_figures_tex.py` |
| `paper/fig-cost-tables.tex` | same | LaTeX | auto-generated |
| `paper/fig-cost-vs-score.tex` | same | LaTeX | auto-generated |
| `paper/fig-cost.tex` | same | LaTeX | auto-generated |
| `paper/fig-128k-reason-on.tex` | same | LaTeX | auto-generated |
| `paper/fig-128k-reason-off.tex` | same | LaTeX | auto-generated |
| `paper/fig-16k-reason-off.tex` | same | LaTeX | auto-generated |
| `paper/plots/*.png` | (11 PNGs) | PNG | light-theme chart variants only (dark variants excluded per README §5) |

### `runs/` (the graded results + workspaces; 29,292 files)

This directory was NOT bulk-copied (29k files; ~1 GB). What was captured:

| Local path | Source path | Type | Notes |
|---|---|---|---|
| `_meta/all_tracked_files.txt` | `git ls-files` | text | full 29,395-line listing of every tracked file |
| `_meta/top_level_file_counts.txt` | `git ls-files \| awk …` | text | counts per top-level dir |
| `_meta/runs_subdir_counts.txt` | `git ls-files \| awk …` | text | counts per `runs/<condition>/` |
| `_meta/sample_q38_single_p1.json` | `runs/firstparty-128k-reasoning-on-5pass/results/q38_single_p1.json` | JSON | sample results file (1,111 lines; records the `q38_single` arm at the 250k cap) |
| `_meta/sample_run_config_luna.txt` | `runs/firstparty-128k-reasoning-on-5pass/results/run_config_luna.txt` | text | run config for the Luna arm |
| `_meta/sample_run_config_fable5.txt` | `runs/fable5-128k-reasoning-on-5pass/results/run_config.txt` | text | run config for Fable 5 |
| `_meta/sample_workspace/{task.md, plan.md, tasks.json, notes.md, solution.py, answer.md}` | `runs/firstparty-128k-reasoning-on-5pass/ws/q38_multiagent_p1/1380abfd7a16/*` | text | one full sample workspace |

### `_meta/` (provenance; 8 files)

| Local path | Source | Notes |
|---|---|---|
| `_meta/repo_meta.json` | GitHub API `/repos/slee-persis/GVS5H` | captured the rate-limit error response — actual metadata NOT retrieved |
| `_meta/HEAD_commit.txt` | `git log -1 --pretty=fuller` | the single commit's full metadata |
| `_meta/all_tracked_files.txt` | `git ls-files` | complete file listing |
| `_meta/top_level_file_counts.txt` | `git ls-files \| awk` | file counts per top-level dir |
| `_meta/runs_subdir_counts.txt` | `git ls-files \| awk` | file counts per `runs/<condition>/` |
| `_meta/sample_q38_single_p1.json` | (sample run record) | one graded results file |
| `_meta/sample_run_config_luna.txt` | (sample run config) | Luna arm run config |
| `_meta/sample_run_config_fable5.txt` | (sample run config) | Fable 5 arm run config |
| `_meta/sample_workspace/*` | (sample workspace) | one full per-problem workspace |

---

**End of analysis.** Parent agent: please use this report for comparison against `MrJ55/pi-zero-shot`. The two repos are fundamentally different in kind — GVS5H is an LLM-agent orchestration scaffold (no training), evaluated on LiveCodeBench Hard; if `pi-zero-shot` is a training repo, the comparison will mostly be architectural (orchestrator-vs-trainer) rather than code-equivalent. If `pi-zero-shot` is *also* an LLM-orchestration scaffold, the comparison should focus on (a) the manager–worker loop design (single manager + workers, shared filesystem workspace, REWRITE-not-append notes, sample-test gate, cut-off summarizer), (b) the model-routing layer (prefix dispatch to OpenAI/Groq/Anthropic/DashScope/OpenRouter/ollama with rerouting + clamp detection + infra-exhausted flag), (c) the audit trail (`*.regraded.json` + `*.cap128k.json` twins; `passed_before_regrade` preserved), and (d) the §3.3 evaluator fix in `testing_util.py:MockBuffer`.
