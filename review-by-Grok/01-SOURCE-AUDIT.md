# 01 — Source Audit

## pi-zero-shot @ bd63bf9562a92274c8c10f4616df240a7970bd4a

**Nature:** Planning-only repository.  
**Implementation status:** `src/extension/.gitkeep` is the only file under `src/`. Zero executable code.

### Inventory (key files)

| Path | Size | Notes |
|------|------|-------|
| README.md | 6.3 KB | Goals, architecture diagram, phased plan summary, upstream links |
| adr/0001-use-extension-not-core-fork.md | 1.1 KB | Accepted |
| adr/0002-filesystem-ledger.md | 1.1 KB | Still “Proposed” |
| adr/0003-sequential-manager-worker.md | 0.9 KB | Accepted |
| adr/0004-subagents-as-spawn-helper.md | 4.0 KB | Accepted; strongest document |
| docs/architecture.md | 3.8 KB | Paper → Pi mapping table |
| docs/00-problems-and-goals.md … 02-ecosystem-shortcuts.md | small | Background |
| plan/phase-00 … phase-05 | 0.9–3.9 KB | Task lists; Phase 0 exit criteria unchecked |
| plan/VERIFY-LOG.md | 210 B | Header only, empty |
| raw/PAPER.md | 2.9 KB | Abstract + link table only |
| src/README.md + src/extension/.gitkeep | — | Placeholder |

**Observation:** README status line “Planning complete in-repo” is not supported by the contents of `plan/` or the ADRs.

## GVS5H @ 6d7a143bd4e4c4343179b4386fc0d906ae9af118

Key control-flow files examined:

- `codebase/v2-current/escalation/multiagent.py` (full read) — authoritative source of the manager–worker loop, sample-test hard override, notes rewrite, finalize skip, infra_exhausted, MAX_TASKS, STRICT_FORMAT, etc.
- Presence confirmed: `orchestrator.py`, `capmatch_q38.py`, `lcb100_hardest_v6.json`, `run_bench.py`.

## Paper (arXiv:2608.26480)

Abstract and high-level claims recovered from `raw/PAPER.md` and GVS5H README references. Headline results rely on five paired passes and the v2 scaffold invariants.

## Independence statement

No content from any `review-by-*` folder was opened or used.
