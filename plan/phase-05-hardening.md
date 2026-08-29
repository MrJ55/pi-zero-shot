# Phase 5 — Hardening & polish

## Goals

Improve robustness across providers and models; optional extensions beyond the paper MVP.

## Background

- GVS5H `orchestrator.py` provider quirks (reasoning fields, clamp detection, temperature restrictions).
- Paper limitations (§4.x) on small models and reasoning modes.

## Tasks

- [ ] Provider-specific handling via `pi-ai` (reasoning capture, finish_reason normalization).
- [ ] Resilience to model format drift (parser fallbacks).
- [ ] Config surface aligned with paper env knobs where useful (`MAX_ITERS`, caps, strict format).
- [ ] Optional: parallel workers while preserving ledger consistency (post-MVP).
- [ ] Optional: math-problem variant (`answer.md` path).
- [ ] Tests against selected GVS5H workspace transcripts (parser + control-flow regression).
- [ ] Update ADRs / docs with final decisions and known limitations.

## Exit criteria

- [ ] Documented limitations and config reference.
- [ ] Regression tests for parsers and loop invariants.

## Verification

- Regression suite green.
- Notes in `VERIFY-LOG.md` for any intentional divergence from GVS5H.
