# Paper Ingestion Analysis — arXiv 2608.26480

> **Source provenance.** This analysis is built primarily from the LaTeX source
> mirrored by Task ID 4 at `/home/z/my-project/review-by-GLM/sources/GVS5H/paper/zero_shot_self_orchestration_with_ledger_based_control_for_improved_llm_coding_performance_2026-08-25.tex`
> (1434 lines) plus its seven `fig-*.tex` inputs. It was cross-checked against the
> arXiv-served PDF and HTML, both freshly fetched during this retry and **byte-identical**
> to the files already sitting in `arxiv/` from the prior attempt:
>
> | file | md5 | size | source |
> |---|---|---|---|
> | `arxiv/paper.pdf`  | `52576a74f3278a57b39fa2d7b97cde0d` | 1,452,876 B | arXiv `pdf/2608.26480` (HTTP 200) |
> | `arxiv/paper.html` | `ece8ec6a65cbb1f601b6119d74b8291a` |   286,907 B | arXiv `html/2608.26480` (HTTP 200) |
> | `arxiv/paper.txt`  | (pdftotext -layout of the above)    |    86,082 B / 1,119 lines | regenerated and diffed identical |
> | `arxiv/abs.html`   | freshly fetched this run             |    44,439 B | arXiv `abs/2608.26480` (HTTP 200) |
>
> The GVS5H bundle's own `...2026-08-25.pdf` (the authors' local compile of the same `.tex`)
> was used only to confirm there is no divergence between the authors' bundle and the
> arXiv submission; both render the same content.

---

## A. Bibliographic Info

| field | value |
|---|---|
| **Title** | Zero-Shot Self-Orchestration with Ledger-Based Control for Improved LLM Coding Performance |
| **arXiv ID** | 2608.26480v1 [cs.MA] |
| **Submission date** | 27 Aug 2026 (confirmed by `citation_date` meta and PDF cover page "arXiv:2608.26480v1 [cs.MA] 27 Aug 2026") |
| **Authors** | Victor Gao¹; Vida Khosrowshahi¹; Ali Khosrowshahi¹; Xihao Sun¹; Juhyun Lee; Simon (Sang Won) Lee¹† |
| **Affiliation** | Persis Capital Inc. (the `¹` mark) |
| **Equal contribution** | "These authors contributed equally to this work." (the `1` mark on Gao, V. Khosrowshahi, A. Khosrowshahi) |
| **Corresponding author** | Simon (Sang Won) Lee, Ph.D. — `slee@persisholdings.com` |
| **Pages (PDF)** | 27 |
| **PDF Creator / Producer** | `arXiv GenPDF (tex2pdf:4af3385)` / `pikepdf 8.15.1` |
| **Code link (in paper)** | None in the body. The paper references Anthropic / OpenAI / Qwen / MiniMax / Moonshot model docs and the LiveCodeBench paper, but **does not cite a code release**. The authors' implementation bundle is `github.com/slee-persis/GVS5H` (discovered externally by Task ID 4; repo owner `slee-persis` = corresponding author Simon Lee). |
| **License** | Not stated in the paper; Task ID 4 confirmed the GVS5H bundle has **no top-level LICENSE file**. |
| **Funding / acknowledgements** | None stated. |
| **Subject class** | `cs.MA` (Multi-Agent Systems) |

---

## B. Problem & Motivation

The paper opens (§1) by stating the gap it targets:

> "Multi-agent pipelines usually change several factors at once, including token
> budgets, tool calls, prompts, and retrieval, so an aggregate gain over a single
> call rarely identifies which factor helped."

Two specific prior findings motivate the design:

1. **Mixed evidence on multi-agent gains.** Citing Wang et al. 2024 (`wangq2024`,
   "Rethinking the bounds of LLM reasoning") and Tran & Kiela 2026 (`tran2026`,
   "Single-agent LLMs outperform multi-agent systems on multi-hop reasoning under
   equal thinking token budgets") — both report that multi-agent gains often
   **vanish** once test-time compute is held constant.
2. **Confounders in existing comparisons.** Tran & Kiela's "Data Processing
   Inequality" argument: routing information through additional agents cannot
   *add* information. They predict multi-agent systems become competitive only
   when (a) a single agent's effective context utilization is degraded, or (b)
   more compute is expended. The paper explicitly picks option (b) and **does
   not** attempt an equal-token comparison: "the manager–worker loop necessarily
   spends more tokens than the single-agent baseline, and we ask whether that
   additional spend buys better solutions — not whether orchestration is more
   information-efficient per token" (§1 Related work, paragraph (d)).

The hard part is therefore **attribution**: prior multi-agent comparisons change
N variables simultaneously (token budget, tool calls, prompts, retrieval). The
paper's design **isolates the orchestration scaffold** as the single difference,
holding model, problem set, temperature, and (where possible) the per-call
output cap fixed.

---

## C. Key Claims / Contributions

1. **A zero-shot, training-free manager–worker scaffold** over a shared
   filesystem workspace, with **no per-benchmark tuning**, improves pass@1 over
   the same model in a single call. (Abstract; §1.2; §3.)
2. The scaffold is **conditional, not universal**: large and statistically
   significant gains for some models (Qwen3.8-27B +23.4, GPT-5.6-Luna +10.6,
   GPT-5.6-Terra +8.0 over five paired passes; Kimi-K3 +30.4 and Minimax-M3 +11.0
   over five paired passes with reasoning off, p<10⁻⁴; Kimi +42 and Minimax +12
   in a single 128k pass); null or negative for others (Qwen3.6-35B −1 to −9
   with reasoning off). (Abstract; §2.1; §2.4.)
3. **With the manager, Opus-5 reaches 91% in one pass** — the highest score in
   the study. (Abstract; §2.4; Conclusion.)
4. **Running a manager roughly triples the token bill** (cost table shows
   +153% on Qwen3.8-27B, +266% on GPT-5.6-Luna, +244% on GPT-5.6-Terra — i.e.
   2.5×–3.7×).
5. The scaffold buys accuracy **more cheaply than moving to a larger model**:
   - GPT-5.6-Terra + manager nearly matches Fable 5's single-call accuracy
     (85.0 vs 87.4, p=0.59) at a fifth of the price ($11.71 vs $61.11 per
     100-problem pass, p<10⁻⁴).
   - Qwen3.8-27B + manager reaches 86.4 (vs Fable 5's 87.4) for $51.75 a pass,
     on weights anyone can self-host.
   - GPT-5.6-Luna + manager matches GPT-5.6-Terra's single call (77.8 vs 77.0)
     at 44% of the price ($1.50 vs $3.41).
6. **Two recurring mechanisms** behind the gains, identified by transcript
   analysis: (a) *context management* — short worker calls and shared notes
   reduce truncation; (b) *problem decomposition*. (§4.1, §4.2.)
7. **A bug discovered in the LiveCodeBench harness itself** — a stateless
   `readline()` in the mock `sys.stdin` binary view — and a one-line fix
   (BytesIO-backed view). Every reported number in §2.1–§2.3 is re-scored after
   the fix; the §2.4 numbers are re-scored as well (only one cell moves). (§3.3.)
8. **Negative results are reported**: Qwen3.6-35B loses 1.2 (16k off) and 9
   (128k off); the paper analyzes the regression mechanism in §4.4.
9. **Statistical rigor**: paired sign-flip permutation tests (n=100 problems,
   2×10⁵ resamples), Holm-corrected across model families; 95% t-intervals
   across the five independent passes (df=4); exact McNemar on pooled
   discordants. (§3.2 Statistics.)
10. The scaffold's gains are **not primarily truncation rescue**: even where
    the manager rescues no-code cells (25/35 on Qwen3.8-27B single, worth
    ~5 of the +23.4 points), most of the gain comes from genuine
    problem-solving. The OpenAI arms have zero truncation and zero empty
    solutions across all 2,000 problem-passes, yet still gain +8.0 and +10.6.
    (§2.3.)

---

## D. Method: GVS5H

### Task formulation

Single-call baseline: the same model, at temperature 0.2, given the problem in
exactly one call — no shared workspace, no loop, no other role in the prompt,
receiving only the solver system prompt verbatim (§3.1, paragraph after the
figure). Manager arm: the same model invoked in a series of fresh contexts
(= "agents"), each with a distinct role, coordinating only through shared
filesystem files. **Every role uses the same underlying model.** (§1.2; §3.1.)

### Model architecture — the manager–worker scaffold (v2, §3.1)

The "architecture" is a **prompt-and-control-flow scaffold** with **no trained
weights**. Five workspace files form the shared ledger:

| file | contents |
|---|---|
| `<ws>/task.md`      | the problem statement |
| `<ws>/plan.md`      | the manager's overarching plan |
| `<ws>/tasks.json`   | the task list `[{id, desc, status, result}]` |
| `<ws>/notes.md`     | accumulated ideas / findings / partial proofs |
| `<ws>/solution.py`  | current best code |

Control flow (Figure 7), six numbered steps:

1. **Manager — plan.** The manager reads the problem and writes a **3–6 sentence
   strategy plus 3–6 concrete seed tasks**.
2. **Worker — brainstorm (ideation).** The first worker **does not write a
   solution**; it identifies the core difficulty, lists candidate approaches
   and pitfalls, and **appends them to `notes.md`**, proposing next steps.
3. **Manager — manage (loop).** The manager **folds the plan and the brainstorm
   into one curated task list** (merging duplicates, marking done items, adding
   only genuinely new sub-tasks), then either declares the problem done or
   names the single next task.
4. **Worker — do the task.** A fresh worker executes that one task, **rewrites
   `solution.py`**, appends what it did to `notes.md`, and proposes remaining
   steps.
5. **Verifier — run the sample tests** *(absent from the original scaffold)*.
   Whenever the round's worker produced a fresh candidate, the program is
   executed against the problem's **public sample tests** — the stdin-format
   tests, which cover 73 of the pinned 100 problems; the 27 LeetCode-style
   problems carry functional/call-based public tests the engine does not
   execute, so they are checked only by the hidden-test grader. The
   pass/fail verdict, with the first failing case, is fed back to the manager
   and **treated as ground truth: a failing run overrides a done verdict**,
   forcing the loop to continue with a fix-or-switch task. Control returns to
   the manager (step 3).
6. **Finalizer.** A finalization worker emits the definitive solution whenever
   the loop ends **without** a clean sign-off — the round budget is spent, the
   manager reissues a task it just handed out, or it names no task at all. The
   call is **skipped** when the manager declares the problem done and a usable
   solution is already on disk, so a redundant final pass cannot overwrite a
   correct answer.

**Guards** (§3.1, paragraph after Figure 7):
- Round budget: **`MAX_ITERS` = 10 manager→worker cycles** (v2; 4 in the
  original scaffold).
- **No-progress guard**: if the manager reissues the exact task it just handed
  out, the loop stops.
- **Cut-off summarizer**: a worker that hits the token cap mid-attempt has its
  partial thinking summarized by a fresh short call so its ideas still reach the
  manager.

### Input / output formats — size limits

The paper explicitly states that, in v2, **"Workspace files feeding a prompt"**
are **size-bounded** (vs unbounded in the original scaffold). The exact size
limits (e.g. `MAX_PLAN_CHARS`, `MAX_NOTES_CHARS`, `MAX_TASKS_CHARS`,
`MAX_SOLUTION_CHARS`) **are not printed in the paper** — they live in the code
(`codebase/v2-current/escalation/multiagent.py` per Task ID 4: `MAX_PLAN_CHARS
= 4000` at line 197). The paper refers the reader to Figure 7
(`plot_agent_loop_flowchart.py`) for the loop diagram and to §3 for the
scaffold details.

The worker's user message "additionally carries the plan, the accumulated
notes and the current artifact" (§3.1, paragraph after Figure 7). The worker
receives the solver system prompt "wrapped in a subagent preamble and a
four-section output contract" (same paragraph). The four sections are not
enumerated in the paper; they are in the code.

### Training objective / loss — **NONE (zero-shot)**

The paper is explicit and repeatable on this point:

> "We investigate the effect of introducing the manager–worker scaffold over a
> shared filesystem workspace, **with no training and no per-benchmark
> tuning**" (Abstract).

> "**No training, no per-benchmark tuning.** Every role is the *same* model
> invoked in a fresh context with a short generic prompt. As a zero-shot
> orchestrator, nothing is trained or hand-tuned against the problem set."
> (§1.2)

> "We call this zero-shot self-orchestration: inference-time orchestration in
> which the orchestrator is neither trained for orchestration nor provided
> task-specific demonstrations of how to decompose or coordinate the problem."
> (§1.2)

**Confirmed: NO training, NO loss, NO fine-tuning, NO RL, NO demonstrations.
Pure inference-time prompt + control-flow scaffold over hosted LLM APIs.**

### Training data — **NONE**

No training data. No checkpoints. No weights to release. (Confirmed across
Abstract, §1.2, §3, §5 Reproducibility-adjacent discussion.)

### Eval data

**LiveCodeBench** (`jain2024`, arXiv:2403.07974), **`release_v6`** split,
**hard** difficulty, **100 latest problems by contest date**. Using the latest
problems reduces training-data contamination (LiveCodeBench's own
contamination-free argument). Solutions are graded by **LiveCodeBench's own
hidden-test evaluator**. (§3.2 Benchmark.)

The 100 problem IDs are pinned in
`codebase/v2-current/escalation/lcb100_hardest_v6.json` (Task ID 4 confirmed
this file exists with 100 pinned ids). Of those 100 problems, **73 are
stdin-format** (executable by the v2 verifier's sample-test step) and **27 are
LeetCode-style functional/call-based** (not executable by the sample-test
verifier; checked only by the hidden-test grader). (§3.1 step 5.)

### Models compared (9 total)

| model | params | serving | scaffold | arms |
|---|---|---|---|---|
| Qwen3.5-9B        | 9B                  | OpenRouter | original (v1) | both, OFF only (ON unusable) |
| Qwen3.6-35B-A3B   | 35B total / 3B active | OpenRouter | original (v1) | both, all 3 conditions |
| Qwen3.8-27B       | 27B (open, FP8, local vLLM) | pinned backend | v2 | both (single cap-matched from 250k) |
| Minimax-M3        | ~428B total / ~23B active | OpenRouter | original (v1) | both, all 3 conditions |
| Kimi-K3           | ~2.8T total / ~16 active of 896 experts | OpenRouter | original (v1) | both, all 3 conditions |
| Opus-5            | size undisclosed | OpenRouter | original (v1) | both, 128k ON ×1 only |
| GPT-5.6-Terra     | size undisclosed | OpenAI API (pinned) | v2 | both, 128k ON ×5 |
| GPT-5.6-Luna      | size undisclosed | OpenAI API (pinned) | v2 | both, 128k ON ×5 |
| Claude Fable 5    | size undisclosed | Anthropic Messages API (pinned) | v2 | **single only** (no manager arm) |

The serving split separates §2.1 (pinned-backend, 4 models, v2, 128k ON ×5)
from §2.4 (OpenRouter, 5 models, v1, 3 conditions). The split exists because
"gateway routing proved to be the dominant source of run-to-run noise" (§3.2
Models; §4.5 Limitations).

### Inference / decoding procedure

- **`MAX_ITERS` = 10** manager→worker cycles (v2); 4 in original (§3.1 table).
- **No-progress guard**: reissuing the same task ends the loop (§3.1).
- **Cut-off summarizer**: a fresh short call summarizes a worker's partial
  thinking when it hit the token cap (§3.1).
- **Sample-test gate**: a failing public-sample run overrides a "done" verdict
  and forces a fix-or-switch task (§3.1 step 5).
- **Finalizer**: a finalization worker runs only when the loop ends without a
  clean sign-off; it is skipped if the manager declared done and a usable
  solution is already on disk (§3.1 step 6).
- **Temperatures** (§3.1, paragraph after Figure 7):
  - 0.3 to write the plan
  - 0.4 to brainstorm
  - 0.2 for task execution
  - 0.2 for curating the task list
  - 0.2 for the single-call baseline
  - These settings are identical in both scaffold versions.
- **Per-call `max_tokens` (the cap)**: 128k for the §2.1 pinned-backend arms
  (also a hard ceiling on Opus-5, Fable 5, and the GPT-5.6 family — §3.2
  Conditions); 16k or 128k for the §2.4 OpenRouter set; 250k for Qwen3.8-27B's
  single arm (cap-matched back to 128k post-hoc by token-exact truncation, §3.2
  Cap-matching).
- **Thinking**:
  - Qwen3.8-27B: no `reasoning_effort` sent (Qwen chat template leaves thinking
    on and unbudgeted; only `max_tokens=128k` bounds it).
  - GPT-5.6-Terra / GPT-5.6-Luna: no `reasoning_effort` sent (OpenAI default).
  - Fable 5: `thinking=adaptive`, `display:summarized`, `output_config.effort=high`
    (the API default).
  - §2.4 OpenRouter set: 128k ON uses native `reasoning_effort` for models that
    support it, and a bounded 20k reasoning budget for open models that do not
    (which providers often did not honour).

### Evaluation metrics

- **pass@1**, five independent passes for the §2.1 arms (with sample SD, divisor
  n−1=4) and for the §2.4 16k-OFF condition; one pass for the §2.4 128k-ON and
  128k-OFF conditions.
- **Per-problem agreement** (manager-only / single-only / both / neither) over
  500 problem-passes per model, with **exact McNemar** on the pooled
  discordants (§2.1 table 2).
- **Significance**: paired sign-flip permutation test on per-problem mean Δ
  (n=100 problems; 2×10⁵ resamples), Holm-corrected across families of models;
  95% t-intervals for the mean pass@1 across the five independent passes (df=4).
  Cost comparisons use Welch per-run (n=5 vs 5) and paired sign-flip per
  problem (n=100), Holm-corrected across the seven cost comparisons (§3.2
  Statistics; fig-cost.tex caption).
- **Tukey HSD** for cross-model separation (Figures 4–6 captions).

---

## E. Experimental Setup

| axis | value |
|---|---|
| **Benchmark** | LiveCodeBench code-generation, `release_v6`, hard split, **100 latest problems by contest date** (LCB-100). |
| **Splits used** | hard only (math/knowledge benchmarks — AIME, MATH-500, GPQA, HLE — were run exploratory but not reported; frontier models at/near ceiling, §4.5). |
| **Pinned-backend arms (§2.1)** | GPT-5.6-Terra, GPT-5.6-Luna (OpenAI API); Qwen3.8-27B (local vLLM, FP8); Claude Fable 5 (Anthropic Messages API, **single-only**). 128k output cap, reasoning on, ×5 passes, **v2 scaffold**. |
| **OpenRouter arms (§2.4)** | Opus-5, Kimi-K3 (~2.8T MoE), Minimax-M3 (428B), Qwen3.6-35B-A3B, Qwen3.5-9B. Three conditions: (i) 128k ON ×1, (ii) 16k OFF ×5, (iii) 128k OFF ×1. **Original (v1) scaffold.** |
| **Baselines** | single call (same model, same temp 0.2, one call, no workspace, no loop, no other role). |
| **Scaffold versions compared** | v1 (original, OpenRouter set) vs v2 (current, pinned-backend set) — see §3.1 table and Section M below. |
| **Metrics** | pass@1; per-problem agreement + exact McNemar; paired sign-flip permutation test (n=100, 2×10⁵ resamples, Holm-corrected); 95% t-intervals (df=4); Tukey HSD for cross-model separation. |
| **Hardware (compute)** | Not stated in the paper. Task ID 4 confirmed the GVS5H bundle's `run_4models_1pass_reason_on.sh` and `run_fable5_5pass_single.sh` scripts and the README mention that "Qwen3.8-27B is served locally in FP8" on the authors' own vLLM. The README (per Task ID 4) gives Fable 5 pricing and GPU info but no explicit cluster size. |
| **Seeds** | **Not stated.** The paper reports SD across the 5 passes and treats pass-to-pass variation as the noise model; no explicit RNG seed is named. |
| **Number of runs** | §2.1: 5 passes × 4 models × 2 arms (minus Fable 5's missing manager arm) = ~35 arm-passes over 100 problems. §2.4: 1 or 5 passes × 5 models × 2 arms × 3 conditions. |
| **Model routing details** | §2.1 = pinned backend per model; §2.4 = OpenRouter gateway (single OpenAI-compatible endpoint). The §2.4 path had provider-side stalls, mid-stream drops (IncompleteRead), 5xx/504s, output clamping below the requested cap (e.g. 32k clamps while advertising 262k), and `content=null` reasoning-only replies — all scored as failures, making absolute levels a conservative lower bound (§4.5). |
| **Cap-matching** | Qwen3.8-27B's single arm was generated at 250k (124/500 hit `finish_reason=length`); replayed at 128k by **token-exact truncation using the serving stack's own tokenizer** (not a character-count approximation), re-extracting the solution from that prefix, re-scoring on the corrected evaluator. The cap is invisible to the model (vLLM `max_tokens` is server-side), so the replay is exact (§3.2 Cap-matching). |
| **Instrumentation** | In the 128k conditions, every model call's `finish_reason` and completion-token count is logged, and each problem's final record carries a status in `{ok, truncated, empty_stop, empty, error}`. The 16k × 5-pass runs predate this instrumentation (§3.2 Instrumentation). |

---

## F. Results — headline numbers per benchmark per model

### §2.1 — LCB-100 pass@1 (%), 128k, reasoning on, ×5 passes, v2 scaffold, pinned backends

| Model | Serving | Single | Manager | Δ | Per-pass Δ |
|---|---|---|---|---|---|
| Claude Fable 5    | Anthropic    | **87.4 ± 1.1** | — (single-only) | — | — |
| GPT-5.6-Terra     | OpenAI       | 77.0 ± 1.0 | **85.0 ± 1.0** | **+8.0 ± 0.0** | +8, +8, +8, +8, +8 |
| GPT-5.6-Luna      | OpenAI       | 67.2 ± 4.3 | **77.8 ± 2.0** | **+10.6 ± 5.1** | +17, +7, +13, +4, +12 |
| Qwen3.8-27B       | local vLLM   | 63.0 ± 4.1 (cap-matched from 250k) | **86.4 ± 2.7** | **+23.4 ± 6.6** | +15, +20, +29, +22, +31 |

Notes from the table:
- Qwen3.8-27B single arm ran at 250k natively (65.6 ± 4.6, Δ = +20.8 ± 7.0); the
  128k cap-matched figure is 63.0 ± 4.1.
- Fable 5 per-pass scores: 86, 87, 87, 88, 89 (no manager arm).
- Terra's zero SD is a coincidence of aggregates, not a fixed set of problems:
  29 distinct problems are manager-only in at least one pass, only one in all
  five.

### §2.1 — Per-problem agreement (manager only / single only / both / neither, out of 500)

| Model | Manager only | Single only | Both | Neither | Exact McNemar p |
|---|---|---|---|---|---|
| Qwen3.8-27B (cap-matched 128k) | **125** | 8  | 307 | 60 | **4×10⁻²⁸** |
| GPT-5.6-Luna                  | **71**  | 18 | 318 | 93 | **1×10⁻⁸**  |
| GPT-5.6-Terra                 | **51**  | 11 | 374 | 64 | **3×10⁻⁷**  |

### §2.2 — What the scaffold costs (per 100-problem pass, list rate × tokens consumed)

| Arm | Rate $/MTok in/out | In (MTok) | Out (MTok) | $/pass | $/solved |
|---|---|---|---|---|---|
| Qwen3.8-27B single   | $0.35 / $2.75   | 0.0753 | 7.4247 | $20.44 | $0.32 |
| Qwen3.8-27B manager  | $0.35 / $2.75   | 1.5053 | 18.6277| $51.75 | $0.60 |
| GPT-5.6-Luna single  | $0.20 / $1.20   | 0.0661 | 0.3299 | $0.41  | $0.006 |
| GPT-5.6-Luna manager | $0.20 / $1.20   | 1.1686 | 1.0522 | $1.50  | $0.019 |
| GPT-5.6-Terra single | $2 / $12        | 0.0661 | 0.2728 | $3.41  | $0.044 |
| GPT-5.6-Terra manager| $2 / $12        | 1.1098 | 0.7911 | $11.71 | $0.14 |
| Fable 5 single       | $10 / $50       | 0.0899 | 1.2043 | $61.11 | $0.70 |

Cost-delta tests: manager − single +$31.31 (Qwen, p=8.7×10⁻⁵ per pass), +$1.09
(Luna, p=4.3×10⁻⁵), +$8.30 (Terra, p=8.7×10⁻⁵); all per-problem p<3.5×10⁻⁵.
Fable 5 single − Qwen3.8-27B manager +$9.36 (p=0.0051 per pass, p=0.20 per
problem); Fable 5 − Terra manager +$49.40 (p=1.3×10⁻⁸); Fable 5 − Luna manager
+$59.61 (p=9.5×10⁻⁷); Terra single − Luna manager +$1.91 (p=2.1×10⁻⁷).

### §2.3 — Truncation channel (cap hits and empty solutions per 500 problem-passes)

| Model | Cap hits s/m | No code s/m | of which refusals | Cap |
|---|---|---|---|---|
| GPT-5.6-Terra  | 0 / 0   | 0 / 0   | 0 | 128k (hard) |
| GPT-5.6-Luna   | 0 / 0   | 0 / 0   | 0 | 128k (hard) |
| Qwen3.8-27B    | **150 / 5** | **35 / 0** | 0 | 128k (cap-matched) |
| Claude Fable 5 | 3 / —   | 9 / —   | **6** | 128k (hard) |

- Qwen3.8-27B single at 250k vs 128k: 65.6±4.6 vs 63.0±4.1 (the 128k cut hides
  2.6 points, all in the tail — 124 vs 150 cap hits, 21 vs 35 no-code).
- Manager "rescue": of Qwen3.8-27B single's 35 no-code cells, the manager passed
  25, failed 10, left none empty → 25/500 = 5.0 points, about a fifth of the
  +23.4.
- Fable 5 refusals: 6/9 empty cells are safety refusals on three ordinary
  competitive-programming problems (3739 refused in 3/5 passes, 3682 in 2/5,
  abc393_e in 1/5). Scored as failures; ~1.2 points of penalty no other arm pays.
- OpenAI arms: **zero truncation, zero empty solutions across all 2,000
  problem-passes** → no rescue component in their +8.0 and +10.6 deltas.

### §2.4 — OpenRouter-served set (original / v1 scaffold)

| Model | Params | 128k·ON (1 pass) | 128k·OFF (1 pass) | 16k·OFF (×5) |
|---|---|---|---|---|
| Opus-5      | n/a     | 85 → 91 (**+6**) | — | — |
| Kimi-K3     | ~2.8T   | 83 → 82 (−1)    | 32 → 74 (**+42**) | 32.2 → 62.6 (**+30.4***) |
| Minimax-M3  | 428B    | 60 → 66 (+6)    | 25 → 37 (**+12**) | 21.2 → 32.2 (**+11.0***) |
| Qwen3.6-35B | 35B     | 25 → 43 (**+18**) | 35 → 26 (−9)   | 27.8 → 26.6 (−1.2 n.s.) |
| Qwen3.5-9B  | 9B      | *unusable*      | 17 → 20 (+3)   | 14.6 → 21.8 (**+7.2***) |

Significance over 5 paired 16k passes (Holm-corrected across 4 models): Kimi
+30.4 p<2×10⁻⁵, Minimax +11.0 p=6×10⁻⁵, Qwen3.5-9B +7.2 p=4×10⁻⁴, Qwen3.6-35B
−1.2 p=0.7 (n.s.).

---

## G. Ablations

The paper does **not** run a traditional hyperparameter ablation (no sweep over
`MAX_ITERS`, no temperature ablation, no removal-of-components table). What it
**does** offer:

### G.1 The v1 → v2 scaffold comparison (§3.1, the only "ablation")

> "An original version produced the OpenRouter-served set of §2.4. It is the same
> loop and the same prompts, with **four things absent**, all of them on the
> manager arm."

| | **v2 (§3.1, §2.1)** | **original (§2.4)** |
|---|---|---|
| Round budget (`MAX_ITERS`) | 10 manager→worker cycles | 4 |
| Sample-test verifier (step 5) | yes | absent |
| Cut-off summarizer | yes | absent |
| Workspace files feeding a prompt | size-bounded | unbounded |

> "Because the single-call baseline is one call under either version, the
> difference touches only the manager arm — so manager-minus-single deltas are
> not strictly comparable across the two groups, and we report them as separate
> conditions rather than pooling them into one table." (§3 intro)

This is the closest thing to an ablation in the paper, but it is **confounded
with serving path** (v2 = pinned backend, v1 = OpenRouter gateway) and with
model set (v2 = GPT-5.6 pair, Qwen3.8-27B, Fable 5; v1 = Opus-5, Kimi, Minimax,
Qwen3.6, Qwen3.5). The paper acknowledges this confound explicitly.

### G.2 The cap as an "ablation" (§2.3)

Qwen3.8-27B's single arm is run at 250k and re-scored at 128k — a within-arm
"cap ablation" showing the cap is worth 2.6 points (250k 65.6 → 128k 63.0) on
this model. The 128k cap is a **hard ceiling** for the GPT-5.6 family, Opus-5,
and Fable 5 (provider-imposed), so this ablation cannot be run on them.

### G.3 Thinking on/off as an "ablation" (§2.4)

For the OpenRouter set, the same model is run with reasoning on (128k ×1) and
reasoning off (128k ×1, 16k ×5), giving an "internal-planning" ablation. The
finding: the manager provides the largest benefit when the base model is least
effective at self-organizing its own reasoning — either no internal planning
stage (thinking off: Kimi +42, Minimax +12) or thinking that runs away
(Qwen3.6-35B 48/100 single calls cut off mid-thought at the provider's 32k
clamp, +18 with manager) (§4.3).

### G.4 What was *learned* from ablations

- The scaffold helps most where the base model is weakest (§2.1, §4.3): the
  smaller the model (with reasoning on), the larger the manager's gain
  (+23.4 on 27B Qwen > +10.6 on Luna > +8.0 on Terra). The managed arms converge
  into a band a few points below the best single call (Fable 5) rather than
  passing it.
- The scaffold can **hurt** when deliberation produces a worse plan than the
  model's initial approach (Qwen3.6-35B −9 at 128k-off, LCB 3765 example in §4.4).
- Truncation rescue is real but minor: only ~5 of Qwen3.8-27B's +23.4 is the
  no-code rescue channel; the OpenAI arms gain +8.0/+10.6 with **zero**
  truncation, so most of the gain is genuine problem-solving (§2.3).

---

## H. Limitations (acknowledged by the paper itself, §4.5)

1. **Serving-provider reliability (OpenRouter), §2.4 only.** Time-varying
   confound: stalls, mid-stream drops, error objects, output clamping below
   the requested cap, reasoning-only replies. Infrastructure failures are
   scored as wrong, making absolute levels a conservative lower bound; exact
   numbers are not perfectly reproducible. The relative single-vs-manager
   comparison is less sensitive (both arms use the same provider pool).
2. **Provider-served weights may vary (§2.4 only).** OpenRouter does not
   guarantee a single quantization or build per model. The §2.1 pinned-backend
   arms (and the locally served Qwen3.8-27B FP8 checkpoint) are exempt.
3. **Single pass in §2.4.** Thinking-on/off comparisons in §2.4 are 1 pass per
   condition (to limit API cost). Per-model significance rests on the 16k
   five-pass runs; point estimates should be read within ~4.5pp pass-to-pass
   variation. This is why §2.1 repeats every condition five times, and why
   Opus-5's 85→91 — the highest score in the paper — remains a single-pass
   point estimate rather than a measured effect.
4. **Fable 5 has no manager arm.** The strongest single-call result is also the
   one condition where the scaffold's effect cannot be measured.
5. **Refusals are scored as failures, and only one arm can incur them.** Fable
   5 returned `stop_reason=refusal` on 6/500 problem-passes; no fallback model
   is configured. Comparisons against Fable 5 are mildly conservative in its
   disfavour.
6. **Qwen3.8's 128k single arm is a replay, not an independent run.** Those
   generations were produced at 250k and truncated to 128k post-hoc; this
   cannot capture ways the model might have budgeted reasoning differently had
   it known the smaller limit up front. The as-generated 250k reading is
   reported alongside throughout.
7. **A 9B model with thinking on was untestable.** Qwen3.5-9B with reasoning
   enabled could not be evaluated in any configuration tried (OpenRouter:
   reasoning-only replies / truncations; local ollama: refused batching). It
   bounds how small a "thinking" model this scaffold can be applied to.
8. **One benchmark family.** All reported results are competitive-programming
   code generation. Math and knowledge benchmarks (AIME, MATH-500, GPQA, HLE)
   were run exploratory but not reported; frontier models sit at/near ceiling
   (Opus-5 100% on AIME, GPQA, MATH-500), leaving no headroom to measure a
   scaffold effect.

---

## I. Reproducibility Checklist

| item | state |
|---|---|
| **Architecture details (enough to code it?)** | **Partially.** The paper gives the 6-step loop, the 5 workspace files, the guards (MAX_ITERS=10, no-progress, cut-off summarizer), the temperatures (0.2/0.3/0.4), and the sample-test gate semantics. **Missing**: the exact size limits on the workspace files ("size-bounded" is mentioned but no number given — Task ID 4 found `MAX_PLAN_CHARS=4000` in code); the four sections of the worker's output contract; the verbatim system prompts; the exact "subagent preamble" wrapping. A reimplementer would need to read the GVS5H code to nail these. |
| **Hyperparameters (all specified?)** | **Mostly.** MAX_ITERS=10 ✓; temperatures 0.2/0.3/0.4 ✓; 128k/16k/250k caps ✓; thinking settings (effort=high for Fable 5; native reasoning_effort for Kimi/Opus; 20k reasoning budget for Qwen/Minimax that providers often ignored) ✓; pass counts 1 or 5 ✓. **Missing**: RNG seeds (not stated); per-call `max_tokens` for the manager's plan/brainstorm/curate/finalizer calls (not stated); the "fresh short call" budget for the cut-off summarizer (not stated). |
| **Data (released? need to scrape?)** | The benchmark is **LiveCodeBench `release_v6`** (public). The pinned 100 problem IDs are in `codebase/v2-current/escalation/lcb100_hardest_v6.json` (Task ID 4 confirmed). No proprietary data. |
| **Checkpoints (released? or N/A?)** | **N/A — zero-shot, no training, no checkpoints.** This is the cleanest part of reproducibility. |
| **Compute budget (stated?)** | **Not stated in the paper.** Task ID 4 noted the GVS5H README has "Fable 5 pricing and GPU info" but no cluster size. The cost tables (§2.2) give per-pass dollar costs ($0.41–$61.11) but not total compute hours or hardware. |
| **Random seeds (stated?)** | **No.** The paper relies on pass-to-pass variation (SD across 5 passes) as the noise model. |
| **Provider API access (which keys needed?)** | To reproduce §2.1 pinned-backend: **OpenAI API** (GPT-5.6-Terra, GPT-5.6-Luna), **Anthropic Messages API** (Claude Fable 5 — single-only), and a **local vLLM** serving `Qwen/Qwen3.8-27B-FP8` on capable hardware. To reproduce §2.4: an **OpenRouter** API key (or direct keys for Opus-5, Kimi-K3, Minimax-M3, Qwen3.6, Qwen3.5). |
| **Regrading / re-scoring** | Every §2.1–§2.4 number is re-scored on the **corrected evaluator** (§3.3). Stored generations are preserved (`*.regraded.json` twins per Task ID 4), so re-scoring is possible without re-running models. |
| **Plot / figure regen** | Every figure regenerates from `*.regraded.json` via `escalation/run_bench_script/plot_*.py` (Task ID 4 confirmed all 8 plot scripts + `make_figures_tex.py`). |

---

## J. Internal Consistency

### Consistent / tightly tied
- The abstract numbers, the §2.1 table, the §2.2 cost tables, the §2.3 truncation
  table, and the Conclusion all agree to the decimal.
- The v1→v2 table (§3 intro) matches the §3.1 prose ("the original scaffold ran
  the same no-progress guard, but with the budget at 4 and no summarizer") and
  Figure 7's caption ("the same loop with the round budget at 4 and without the
  two steps v2 adds: the sample-test verifier (step 5) and the cut-off
  summarizer").
- The §3.3 MockBuffer fix description matches what Task ID 4 found in
  `codebase/livecodebench/lcb_runner/evaluation/testing_util.py:MockBuffer.readline()`
  (stateful BytesIO vs upstream's stateless line-1-every-call).
- The §3.2 cap-matching procedure matches `capmatch_q38.py` (Task ID 4: 127
  LOC, token-exact 250k→128k truncation using vLLM's own tokenizer).

### Contradictions / vague spots a reimplementer would have to guess
1. **Size limits on workspace files feeding a prompt.** The §3.1 table says v2
   is "size-bounded" vs v1 "unbounded", but **no number is printed in the
   paper**. A reimplementer must read the code (Task ID 4 found
   `MAX_PLAN_CHARS=4000` at line 197 of `multiagent.py`; the other limits are
   presumably nearby but the paper does not list them).
2. **"3–6 sentence strategy plus 3–6 concrete seed tasks"** (§3.1 step 1) is a
   soft spec. Does the manager get to write 7 sentences if the problem needs
   it? The code presumably enforces a hard cap, but the paper does not say.
3. **The four sections of the worker's output contract.** The paper says the
   worker receives the solver system prompt "wrapped in a subagent preamble
   and a four-section output contract" (§3.1 paragraph after Figure 7) but
   does not enumerate the four sections.
4. **The cut-off summarizer's "fresh short call"** — how short? The paper
   says only "summarized by a fresh short call so its ideas still reach the
   manager" (§3.1). No `max_tokens` is given for this summarizer call.
5. **Per-call `max_tokens` for manager-side calls** (plan, brainstorm, curate,
   finalizer). The paper says the cap is "a per-call `max_tokens` bound on
   generation" (§3.2 Conditions), but it is unclear whether the cap is the
   same 128k for every role's call or whether smaller per-role caps are set.
   Task ID 4's reading of `multiagent.py` would resolve this; the paper alone
   does not.
6. **The §2.1 "round budget" of 10 manager→worker cycles** vs the actual count
   of model calls per problem. §2.3 says "108 of its 3,235 calls across the
   five passes hit the cap, 95 of them workers, touching 75 of the 500
   problem-passes" — i.e. ~6.5 calls per problem-pass on Qwen3.8-27B's manager
   arm. A reader might expect 10 worker rounds × 5 calls = many more; the
   paper does not give the formula (plan + brainstorm + N × (manage + worker +
   verifier) + finalizer).
7. **The "subagent preamble" wrapping.** The paper mentions it but does not
   quote it.
8. **RNG seeds.** Not stated anywhere. The 5 passes are presumably independent
   samples at temperature ≥0.2, but no seed is published.
9. **"The 27 LeetCode-style problems … are checked only by the hidden-test
   grader"** (§3.1 step 5). For those 27, the sample-test gate is a no-op, so
   the manager has no external signal — the paper does not discuss whether
   this affects per-problem-type Δ.
10. **Fable 5's "single-only" rationale.** The paper says "Fable 5 was run
    single-only, so it contributes a single-call figure and no manager delta"
    (§3.2 Models) but does not state *why* (cost? API limit? refusal rate?).

These are all things a reimplementer must read the GVS5H code to nail down;
the paper alone is insufficient as a reimplementation spec, though it is
sufficient as a *map* of the design.

---

## K. Quotes (the 5–15 most important sentences for a code reviewer)

> **Q1 (Abstract).** "We investigate the effect of introducing the
> manager–worker scaffold over a shared filesystem workspace, **with no
> training and no per-benchmark tuning**, measured against the *same* model
> answering in a single pass."

> **Q2 (§1.2).** "We call this **zero-shot self-orchestration**: inference-time
> orchestration in which the orchestrator is neither trained for orchestration
> nor provided task-specific demonstrations of how to decompose or coordinate
> the problem."

> **Q3 (§1.2, list item 2).** "A *manager* instance reads the problem, writes an
> overarching plan, and then runs a loop: it inspects progress, curates the
> task list, spawns a fresh *worker* to do the single most valuable next task,
> and verifies the output against the sample cases (**in the v2 scaffold,
> §3**), repeating until it judges the problem solved or a small round budget
> is exhausted. There is no fixed pipeline — the manager decides, per problem,
> what happens next."

> **Q4 (§3.1 step 1).** "Manager — plan. The manager reads the problem and
> writes a **3–6 sentence strategy plus 3–6 concrete seed tasks**."

> **Q5 (§3.1 step 2).** "Worker — brainstorm (ideation). The first worker
> **does not write a solution**; it identifies the core difficulty, lists
> candidate approaches and pitfalls, and **appends them to `notes.md`**,
> proposing next steps."

> **Q6 (§3.1 step 4).** "Worker — do the task. A fresh worker executes that
> one task, **rewrites `solution.py`**, appends what it did to `notes.md`, and
> proposes remaining steps."

> **Q7 (§3.1 step 5).** "Verifier — run the sample tests *(absent from the
> original scaffold, §3)*. … The pass/fail verdict, with the first failing
> case, is fed back to the manager and **treated as ground truth: a failing
> run overrides a done verdict**, forcing the loop to continue with a
> fix-or-switch task."

> **Q8 (§3.1, paragraph after Figure 7).** "Guards keep the loop cheap and
> safe: a round budget of **10 manager→worker cycles (`MAX_ITERS`)**; a
> **no-progress guard** (if the manager reissues the exact task it just
> handed out, the loop stops); and a **cut-off summarizer** — a worker that
> hits the token cap mid-attempt has its partial thinking summarized by a
> fresh short call so its ideas still reach the manager. The original scaffold
> ran the same no-progress guard, but with the budget at 4 and no summarizer."

> **Q9 (§3.1, paragraph after Figure 7).** "The single-call baseline is the
> same model, at the **same temperature as the manager arm's workers (0.2)**,
> given the same problem in exactly one call — no shared workspace, no loop,
> and no other role in the prompt. The manager's generative calls use slightly
> higher temperatures, where the work is generative rather than executive:
> **0.3 to write the plan and 0.4 to brainstorm, against 0.2 for task
> execution and for curating the task list**. These settings are identical in
> both scaffold versions."

> **Q10 (§3.1, paragraph after Figure 7).** "It receives the solver system
> prompt verbatim; the manager arm's workers receive that same prompt wrapped
> in a **subagent preamble and a four-section output contract**, and their
> user message additionally carries the plan, the accumulated notes and the
> current artifact. The two conditions differ only in that scaffold."

> **Q11 (§3.2 Benchmark).** "LiveCodeBench code-generation, **release_v6**.
> We take the **100 latest problems in the hard split** (by contest date).
> Using the latest problems reduces training-data contamination. Solutions
> are graded by LiveCodeBench's own hidden-test evaluator."

> **Q12 (§3.1 step 5).** "the program is executed against the problem's
> public sample tests — the stdin-format tests, which cover **73 of the
> pinned 100 problems**; the **27 LeetCode-style problems** carry
> functional/call-based public tests the engine does not execute, so they are
> checked only by the hidden-test grader."

> **Q13 (§3.2 Cap-matching).** "Truncation is **token-exact, using the
> serving stack's own tokenizer**, not a character-count approximation. …
> What is truncated is the **whole output stream, reasoning then answer**,
> because that is what the original cap bounded. … The cap is **invisible to
> the model, which is what makes the replay exact**. This arm ran on our own
> vLLM, where `max_tokens` is a parameter the server enforces: it never
> enters the prompt and does not affect the model's output."

> **Q14 (§3.3).** "The evaluator does not run a candidate as a subprocess; it
> executes it in-process with `sys.stdin` replaced by a mock. That mock's
> binary view implemented `readline()` as `inputs.split(b"\n")[0]` — a
> **stateless** expression that returns the first line on every call. … We
> replaced the mock's binary view with one backed by a `BytesIO` so that
> reads advance a position, and re-scored every stored generation; **no model
> was re-run**."

> **Q15 (§3.3).** "it interacts badly with the v2 verifier: that step runs
> the candidate as a *real* subprocess (§3.1, step 5), where
> `buffer.readline()` works correctly, so the manager was told its solution
> passed the public samples for programs the grader then marked wrong — the
> one signal in the loop meant to be external and trustworthy, certifying the
> wrong answer."

> **Q16 (§4.4, the regression mechanism).** "In practice, the scaffold can
> backfire when deliberation produces a worse plan than the model's initial
> approach and the manager fails to detect the regression."

> **Q17 (§5 Conclusion).** "Holding the underlying model fixed, a lightweight
> manager–worker scaffold over a shared workspace with no training or
> task-specific tuning improves all three models measured with both arms on a
> pinned backend and the verifier-gated v2 scaffold, over five paired passes
> each: Qwen3.8-27B by +23.4, GPT-5.6-Luna by +10.6 and GPT-5.6-Terra by +8.0
> points."

---

## L. Section §3.3 — MockBuffer / readline fix

The paper's §3.3 ("A correction to the evaluator") is short (one paragraph of
prose + two paragraphs of consequence) and is the only place this fix is
described. Verbatim from the .tex source (lines 950–980):

> "While inspecting transcripts for §4.1 we found a defect in the LiveCodeBench
> harness itself, and every number in §2.1–§2.3 is reported after fixing it.
> The evaluator does not run a candidate as a subprocess; it executes it
> **in-process with `sys.stdin` replaced by a mock**. That mock's binary view
> implemented `readline()` as `inputs.split(b"\n")[0]` — a **stateless**
> expression that returns the first line on every call. A program reading
> multi-line input through `sys.stdin.buffer.readline()` therefore read line
> 1 repeatedly and scored wrong no matter how correct it was. The text-mode
> `sys.stdin.readline` was patched to a proper iterator and behaved correctly,
> and `buffer.read()` returns the whole payload and was also unaffected, which
> is why the common `sys.stdin.buffer.read().split()` idiom never exposed it.
> We **replaced the mock's binary view with one backed by a `BytesIO`** so that
> reads advance a position, and **re-scored every stored generation; no model
> was re-run**."

Two consequences the paper calls out:

1. **Interaction with the v2 verifier.** The v2 sample-test verifier (step 5)
   runs the candidate as a *real* subprocess where `buffer.readline()` works
   correctly, so the manager was told its solution passed the public samples
   for programs the grader then marked wrong — the one signal in the loop meant
   to be external and trustworthy was certifying the wrong answer. So the bug
   **silently poisoned the v2 manager loop's external signal**.
2. **Uneven exposure across models.** 311 of the 3,456 §2.1 outputs containing
   code use the `buffer.readline()` idiom, and 97% of those were scored wrong
   vs 20% for the outputs that do not. Fable 5 never uses it and its scores are
   unchanged to the decimal. The §2.4 model set reaches for it once in 5,012
   generations (Kimi-K3's single call on `abc396_g` binds `sys.stdin.buffer` to
   a name and calls `readline()` on that — through an alias). Every §2.4 number
   is re-scored on the fixed evaluator; exactly one cell moves (Kimi's 128k
   thinking-on single arm, from 82 to 83). "Because usage of the idiom is a
   property of a model's coding style, a harness bug of this shape is not a wash
   across a leaderboard — it silently penalises the models whose style happens
   to trip it."

**Reimplementation implication.** A reimplementation of GVS5H that does not
also fix `testing_util.py:MockBuffer` will produce silently wrong scores for
any worker that reads multi-line input via `sys.stdin.buffer.readline()`. The
fix is a one-liner (replace the stateless `inputs.split(b"\n")[0]` expression
with a `BytesIO`-backed view that advances position). Task ID 4 confirmed this
is exactly what `codebase/livecodebench/lcb_runner/evaluation/testing_util.py`
contains.

---

## M. The four v1 → v2 named differences (§3.1) — verbatim

From §3 intro (lines 723–747 of the .tex source). These are the four
**named, table-formatted** differences between the original scaffold (used for
the §2.4 OpenRouter-served set) and the current v2 scaffold (used for the §2.1
pinned-backend set). **All four differences apply only to the manager arm**;
the single-call baseline is one call under either version.

> "An original version produced the OpenRouter-served set of §2.4. It is the
> same loop and the same prompts, with four things absent, all of them on the
> manager arm:
>
> | | v2 (§3.1, §2.1) | original (§2.4) |
> |---|---|---|
> | **Round budget (`MAX_ITERS`)** | **10 manager→worker cycles** | **4** |
> | **Sample-test verifier (step 5)** | **yes** | **absent** |
> | **Cut-off summarizer** | **yes** | **absent** |
> | **Workspace files feeding a prompt** | **size-bounded** | **unbounded** |

Spelled out:

1. **Round budget (`MAX_ITERS`)**: v2 = **10** manager→worker cycles; v1 = **4**.
   This is the single most consequential difference — a 2.5× larger iteration
   budget per problem.
2. **Sample-test verifier (step 5)**: v2 = **yes** (the manager runs the
   candidate against the problem's public sample tests after each worker round;
   a failing run overrides a "done" verdict and forces a fix-or-switch task);
   v1 = **absent** (no public-sample test execution inside the loop, no
   ground-truth signal fed back to the manager).
3. **Cut-off summarizer**: v2 = **yes** (a fresh short call summarizes a
   worker's partial thinking when it hit the token cap, so its ideas still
   reach the manager); v1 = **absent** (a capped worker's ideas are lost).
4. **Workspace files feeding a prompt**: v2 = **size-bounded** (the plan,
   notes, tasks, and current solution that get fed into a worker's prompt are
   truncated to a fixed size budget); v1 = **unbounded** (the workspace files
   are fed into the prompt at full length, which can blow out the context
   window or hit the per-call `max_tokens` before the worker finishes).

**Important caveat the paper itself states**: "Because the single-call
baseline is one call under either version, the difference touches only the
manager arm — so manager-minus-single deltas are **not strictly comparable
across the two groups**, and we report them as separate conditions rather than
pooling them into one table." The v1 set is also confounded with the
OpenRouter serving path and a different model set, so the four differences
above are not isolated ablations.

---

## Cross-reference note for the parent agent

This paper ingestion was built directly from the arXiv-submitted PDF (md5
`52576a74...`, byte-identical to the authors' bundle PDF in
`sources/GVS5H/paper/`) and the verbatim `.tex` source mirrored by Task ID 4.
The four v1→v2 differences in Section M above match the §3.1 table in the
.tex source **character-for-character**; the §3.3 MockBuffer description
matches the .tex source verbatim. Task ID 4's `_analysis.md` (at
`sources/GVS5H/_analysis.md`) already verified at file:line level that the
GVS5H codebase implements each of these: `MAX_ITERS=10`, the sample-test
verifier (step 5), the cut-off summarizer, the size-bounded workspace feeding
(`MAX_PLAN_CHARS=4000` at line 197 of `multiagent.py`), the
`testing_util.py:MockBuffer.readline()` BytesIO fix, and the
`capmatch_q38.py` token-exact 250k→128k truncation. Any reimplementation
claiming fidelity to this paper must reproduce all four v1→v2 differences plus
the §3.3 evaluator fix; otherwise its numbers are not comparable to the
paper's.
