# Review-by-GLM — Test Strategy

**Reviewer:** GLM (Z.ai), independent audit
**Date:** 2026-08-29
**Scope:** Test strategy for pi-zero-shot, including the §3.3 MockBuffer fix, paired-pass protocol, cap-match, and regression tests. This file specifies what to test, how to test it, and how to verify the tests themselves are faithful to GVS5H.

---

## 1. Why a test strategy now (before any code exists)

pi-zero-shot has zero source code and zero tests. The phase plan promises tests in Phase 1 (workspace bounds, rewrite behavior, sample-test parsing), Phase 2 (golden-file parser tests), and Phase 5 (regression tests for parsers and loop invariants). But there is no test runner configured, no test directory, and no CI.

A repo that promises tests in three phases but ships none has, in practice, deferred tests indefinitely. The right move is to **define the test strategy now, before Phase 1 code is written**, so that Phase 1 implementation includes tests from the first commit. This file is that strategy.

---

## 2. Test pyramid

| Level | What it tests | When it runs | Tools | Effort |
|---|---|---|---|---|
| **Unit** | Workspace primitives, parsers, sample-test runner, individual invariants from `08-INTERFACES-AND-INVARIANTS.md` | Every commit | Vitest (or Jest) | ~2 days |
| **Integration** | Control-flow loop with a mocked provider, end-to-end on synthetic problems | Every commit (or nightly) | Vitest + mock provider | ~1 day |
| **Regression** | Parser + loop invariants against GVS5H `runs/` transcripts | Nightly + on phase exit | Vitest + GVS5H fixtures | ~1 day |
| **Smoke eval** | One pass on 10 LCB problems, single vs manager | On Phase 4 completion | Real provider API keys | ~1 hour wall-clock |
| **Full eval** | 5 paired passes on 100 LCB problems, single vs manager, cap-match | Before any paper-comparable claim | Real provider API keys, ~$50–$200 cost | ~12 hours wall-clock |

Total test infrastructure effort: ~5 days. Most of this overlaps with normal Phase 1–4 implementation; net additional effort is ~2 days.

---

## 3. Unit tests — the invariant contract

Every invariant in `08-INTERFACES-AND-INVARIANTS.md` gets at least one unit test. The tests are the executable form of the contract. If a test fails, the invariant is violated.

### 3.1 Workspace tests (Phase 1)

Test file: `src/__tests__/workspace.test.ts`

| Test | Invariant | What it verifies |
|---|---|---|
| `creates workspace directory keyed by content hash` | INV-1 | Two workspaces from the same problem text get the same hash directory. |
| `creates all six workspace files` | INV-2 | After init, all seven files exist; `task.md` contains the problem text; `transcript.jsonl` is empty. |
| `resets workspace between runs of the same key` | INV-3 | Re-running the same problem starts from a clean workspace. |
| `truncates plan.md to MAX_PLAN_CHARS=4000` | INV-4 | A 10,000-char string is truncated to 4000 on write. |
| `truncates notes.md to MAX_PLAN_CHARS * 2 = 8000` | INV-5 | A 20,000-char string is truncated to 8000 on write. |
| `truncates answer.md to MAX_ANSWER_CHARS=20000` | INV-6 | A 30,000-char string is truncated to 20000 on write. |
| `notes are rewrite-not-append` | INV-7 | A second write replaces the first, not appends to it. |
| `tasks.json is write-only debug` | INV-8 | `tasks.json` is written but never read back by any role. |
| `MAX_TASKS=12 cap on live task list` | INV-9 | 20 tasks added → 12 in the live list. |
| `ANS_RE non-empty-answer guard` | INV-10 | `answer.md` only overwritten if new reply has `ANSWER:` line or file is empty. |

### 3.2 Parser tests (Phase 2)

Test file: `src/__tests__/parsers.test.ts`

| Test | Invariant | What it verifies |
|---|---|---|
| `_sections parses ### HEADER, **HEADER**, HEADER:` | INV-11 (control flow) | All three header styles parse to the same structure. |
| `_bullets parses -, *, 1., 1)` | — | All four bullet styles parse. |
| `_extract_py extracts fenced python blocks` | — | A fenced python block is extracted to the code string. |
| `_parse_tasks parses [done] / [todo] / [wip]` | — | All three status markers parse. |
| `_strip_code removes fenced blocks from ideation` | INV-24 | Ideation reply with code → code replaced with `[code omitted -- approach only]`. |
| `_strict returns true for STRICT_FORMAT=1` | INV-25 | Env knob works. |
| `_strict returns true for auto + muse model` | INV-25 | Auto detection works. |
| `_strict returns false for auto + non-muse model` | INV-25 | Auto detection does not over-trigger. |

### 3.3 Sample-test runner tests (Phase 1)

Test file: `src/__tests__/sample-test-runner.test.ts`

| Test | Invariant | What it verifies |
|---|---|---|
| `runs solution.py against public stdin samples` | INV-23 | A correct solution passes; a wrong solution fails. |
| `returns structured dict, not model output` | INV-23 | Return is `{ran, passed, total, fail}`, not a string. |
| `handles timeout` | — | A solution that hangs returns `ran: false` after the timeout. |
| `handles runtime error` | — | A solution that crashes returns `ran: false, fail: <error>`. |
| `handles multi-line stdin` | INV-35 | A solution using `sys.stdin.buffer.readline()` for multi-line input is graded correctly (the §3.3 fix). |

### 3.4 Loop invariant tests (Phase 3)

Test file: `src/__tests__/loop-invariants.test.ts`

| Test | Invariant | What it verifies |
|---|---|---|
| `control flow order is plan → ideation → manage ↔ worker → finalize` | INV-11 | Transcript shows the correct role order. |
| `MAX_ITERS=10 stops infinite loop` | INV-12 | A problem that never converges stops after 10 cycles. |
| `sample-test hard override forces continue on done + fail` | INV-13 | Manager says `done`, samples fail → status overridden to `continue`. |
| `wrote guard skips sample tests when worker didn't write code` | INV-14 | Worker truncates without writing code → sample tests don't run. |
| `no-progress guard stops on re-issued task` | INV-15 | Same task twice in a row → loop stops. |
| `cut-off summarizer triggers on finish_reason=length` | INV-16 | Truncated worker → `_summarize_cutoff` called. |
| `cut-off digest never written to notes.md` | INV-17 | Truncated worker → `notes.md` not modified by cut-off path. |
| `skip-finalize-when-done optimization` | INV-18 | Manager `done` + non-empty solution → finalize skipped. |
| `single-shot baseline writes no ledger files` | INV-19 | Single baseline → only `task.md` (init) and `transcript.jsonl` (one entry). |
| `worker has no tools` | INV-22 | API call has no `tools` parameter. |
| `worker uses same model for every role` | INV-21 | All role calls in transcript use the same model id. |
| `infra_exhausted flag set on reroute exhaustion` | INV-28 | All reroute attempts fail → `infra_exhausted: True` in transcript. |
| `infra_fail excluded from pass@1` | INV-38 | `infra_fail: True` problem excluded from pass@1. |

---

## 4. Integration tests — end-to-end with a mocked provider

Test file: `src/__tests__/integration.test.ts`

Integration tests run the full control flow with a mocked provider that returns canned responses. This verifies the loop composes correctly without burning real API quota.

### 4.1 Mocked provider

The mocked provider should:
- Return canned responses based on the role (plan, ideation, manage, worker, finalize).
- Allow test cases to specify per-call responses (e.g., "first worker call truncates, second worker call succeeds").
- Track all calls in a mock transcript for verification.
- Set `finish_reason` per call (to test the cut-off summarizer path).

### 4.2 Integration test cases

| Test | What it verifies |
|---|---|
| `runs a full problem to done` | Loop completes in ≤ 10 cycles; `solution.py` is non-empty; transcript has all expected role calls. |
| `runs a full problem to max iters` | Loop stops at `MAX_ITERS=10`; `solution.py` may be empty; finalize is called. |
| `sample-test failure forces continue` | Manager says `done` but sample tests fail → loop continues. |
| `worker truncation triggers cut-off summarizer` | Worker's `finish_reason: "length"` → `_summarize_cutoff` called → digest in manager prompt, not in `notes.md`. |
| `no-progress guard stops` | Manager re-issues same task → loop stops. |
| `infra_exhausted flag set on all-fail` | All reroute attempts fail → `infra_exhausted: True` → `infra_fail: True` in `status_out`. |
| `single-shot baseline` | One call, no ledger files, transcript has one entry. |
| `math problem uses answer.md` | Math problem → `answer.md` written, `solution.py` not written. |
| `code problem uses solution.py` | Code problem → `solution.py` written, `answer.md` not written. |

---

## 5. Regression tests — against GVS5H transcripts

Test file: `src/__tests__/regression.test.ts`

This is the most important test layer for fidelity. GVS5H `runs/` contains real per-problem workspaces with real transcripts. A faithful port should be able to replay a GVS5H transcript and produce the same control-flow decisions.

### 5.1 What to vendor from GVS5H

GVS5H `runs/` is ~1 GB (29k files). For regression tests, vendor a curated subset:
- **10 problems** from `runs/firstparty-128k-reasoning-on-5pass/` (the §2.1 condition).
- **5 problems** from `runs/fable5-128k-reasoning-on-5pass/` (the Fable 5 single-only condition).
- **5 problems** from `runs/16k-reasoning-off-5pass/` (the §2.4 condition).

Total: 20 problems × ~6 files = ~120 files. Manageable.

For each vendored problem, include:
- `task.md` (the problem statement).
- `plan.md`, `notes.md`, `tasks.json`, `solution.py` (the final workspace state).
- `transcript.jsonl` (the full call log — this is the regression oracle).

### 5.2 Regression test cases

| Test | What it verifies |
|---|---|
| `parser handles real GVS5H manager replies` | Run `_sections`, `_bullets`, `_parse_tasks`, `_extract_py` on real GVS5H transcripts. Verify the parsed structures match the expected control-flow decisions (e.g., `STATUS: done` parses to `status = "done"`). |
| `parser handles real GVS5H worker replies` | Same, for worker calls. Verify code extraction matches the `solution.py` that was actually written. |
| `parser handles strict-format model output` | Real GVS5H transcripts from muse/glimmer models (if available in the vendored subset) parse correctly under strict-format mode. |
| `control flow matches GVS5H on replay` | Replay the GVS5H transcript: feed the same problem, mock the provider to return the same responses in the same order. Verify the loop produces the same `STATUS` decisions at each manager round. |

### 5.3 The §3.3 MockBuffer fix as a regression test

The §3.3 fix is so consequential that it deserves its own regression test:

| Test | What it verifies |
|---|---|
| `MockBuffer.readline advances position` | Construct a `MockBuffer` with multi-line input. Call `readline()` three times. Verify each call returns the next line, not line 1 every time. |
| `eval driver uses fixed MockBuffer` | Run a candidate solution that uses `sys.stdin.buffer.readline()` for multi-line input. Verify the candidate is graded correctly (not misgraded as failing on multi-line input). |
| `eval driver matches GVS5H grading` | Run the eval driver on the vendored GVS5H `*.regraded.json` files. Verify the local pass/fail matches the `passed` field in the regraded JSON. |

---

## 6. Smoke eval — sanity check, not paper-comparable

After Phase 4 completes, run a smoke eval:
- **10 LCB problems** from `lcb100_hardest_v6.json` (a 10-problem subset, not the full 100).
- **1 pass** (not 5).
- **Single vs manager**, both arms.
- **Real provider API key** for one model (e.g., GPT-5.6-Luna via OpenAI).

**Purpose:** verify the scaffold runs end-to-end with a real provider. This is *not* a paper-comparable result. A 10-problem single-pass comparison has too much variance to mean anything.

**Cost:** ~$5–$10 in API spend.

**Output:** a small table showing single pass@1 vs manager pass@1 on 10 problems, plus the transcript paths.

**What it does NOT prove:** that pi-zero-shot reproduces GVS5H's numbers. That requires the full eval (§7).

---

## 7. Full eval — paper-comparable (only if all invariants are closed)

Before any claim of "we reproduce GVS5H" or "we match the paper," run the full eval:

### 7.1 Setup

- **100 LCB problems** from `lcb100_hardest_v6.json` (the full frozen id list).
- **5 paired passes** (manager and single on the same 100 problems, 5 times).
- **Same model** for manager and single arms (per INV-21).
- **Same provider** for both arms (per the paper's §2.1 pinned-backend setup).
- **128k cap, reasoning on** (per the paper's §2.1 condition).
- **§3.3 MockBuffer fix** vendored (per INV-35).
- **`infra_fail` excluded from pass@1** (per INV-38).
- **`capmatch` for Qwen3.8-27B** if Qwen3.8-27B is used (per INV-37).

### 7.2 Metrics to report

| Metric | What it is | Paper source |
|---|---|---|
| Single pass@1 (mean ± SD across 5 passes) | Per-pass accuracy on the 100 problems, averaged. | Table 1, "Single" column. |
| Manager pass@1 (mean ± SD across 5 passes) | Per-pass accuracy on the 100 problems, averaged. | Table 1, "Manager" column. |
| Δ = manager − single (mean ± SD across 5 passes) | Paired per-pass difference. | Table 1, "∆" column. |
| Per-pass Δ (5 values) | The Δ for each of the 5 passes. | Table 1, "Per-pass ∆" column. |
| Paired t-test p-value | Significance of Δ. | Table 1, footnote c. |
| Cost per 100-problem pass ($, single vs manager) | Total token cost. | §2.2 cost table. |
| Cost ratio (manager / single) | How much the manager increases the bill. | §2.2. |

### 7.3 What "reproduces GVS5H" means

A claim of "we reproduce GVS5H" should mean:
- The same model, on the same 100 problems, with the same 5 paired passes, produces a Δ within the paper's reported ± SD.
- The paired t-test p-value is in the same significance band.
- The cost ratio is in the same range.

For GPT-5.6-Terra (the most-likely first replication target, since it's a first-party API and doesn't need vLLM):
- Paper reports: Single 77.0 ± 1.0, Manager 85.0 ± 1.0, Δ = +8.0 ± 0.0, per-pass Δ = +8, +8, +8, +8, +8.
- A faithful reproduction should land within ±2 points of 85.0 manager and +8.0 Δ, with the per-pass Δs all positive.

If the reproduction lands outside this band, the divergence should be documented in `VERIFY-LOG.md` with a root-cause analysis (which invariant was missed? which provider quirk was different?).

### 7.4 Cost

Full eval cost (rough estimate, 5 paired passes, 100 problems, GPT-5.6-Terra):
- Single arm: ~$11.71 per pass × 5 = ~$58.55.
- Manager arm: ~$35.13 per pass (3× the single arm) × 5 = ~$175.65.
- Total: ~$234.20.

For Qwen3.8-27B (self-hosted on vLLM): API cost is zero, but compute cost is non-trivial (the paper reports running on a single GPU; ~12–24 hours wall-clock per pass).

---

## 8. CI configuration

`.github/workflows/ci.yml`:

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run typecheck
      - run: npm test
      - run: npm run lint
  markdown-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npx markdownlint-cli2 '**/*.md' '!node_modules' '!_upstream'
```

`package.json` scripts:

```json
{
  "scripts": {
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "test:watch": "vitest",
    "lint": "eslint src --ext .ts",
    "eval:smoke": "tsx scripts/eval-smoke.ts",
    "eval:full": "tsx scripts/eval-full.ts"
  }
}
```

`eval:smoke` and `eval:full` are NOT run in CI (they need real API keys). They are documented here for the implementer.

---

## 9. Test strategy verdict

The test strategy is dominated by the **silent fidelity regression** risk (R1, R2, R3, R4 in `06-RISK-REGISTER.md`). The tests that matter most are:

1. **`MockBuffer.readline advances position`** (§5.3) — catches the §3.3 fix regression.
2. **`sample-test hard override forces continue on done + fail`** (§3.4) — catches the hard-override regression.
3. **`worker has no tools`** (§3.4) — catches the "minimal tools" wording regression.
4. **`infra_exhausted flag set on reroute exhaustion`** (§3.4) — catches the provider outage regression.
5. **`control flow matches GVS5H on replay`** (§5.2) — catches any control-flow drift.

These five tests are the minimum fidelity gate. A port that passes all five is likely faithful; a port that fails any is not.

The regression test layer (§5) is the most important and the most under-specified in the current plan. Phase 5's "Tests against selected GVS5H workspace transcripts" promise is the right instinct, but it should be expanded: vendor 20 GVS5H problems (§5.1) and write replay tests that verify the loop produces the same control-flow decisions on the same inputs.

The full eval (§7) is expensive (~$234 for GPT-5.6-Terra, ~12–24 hours wall-clock per pass for Qwen3.8-27B) and should only be run before any paper-comparable claim. The smoke eval (§6) is the right sanity check after Phase 4.

The total test infrastructure effort is ~5 days, most of which overlaps with normal Phase 1–4 implementation. The net additional effort is ~2 days, and it pays for itself the first time a regression test catches a silent fidelity bug.
