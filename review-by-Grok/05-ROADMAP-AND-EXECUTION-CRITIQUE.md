# 05 — Roadmap and Execution Critique

## Current execution state
- Phase 0 exit criteria: all unchecked.
- `plan/VERIFY-LOG.md`: empty header only.
- ADR 0002 still Proposed.
- `src/`: only `.gitkeep`.
- README status line claims “Planning complete in-repo” — inaccurate.

## Phase-by-phase notes

**Phase 0 (Discovery & mapping)**  
Still open. The architecture doc is already good enough to close most items; the remaining work is status hygiene and the final ledger decision.

**Phase 1 (Ledger primitives)**  
Must include: transcript schema with `infra_exhausted`, hard size bounds on plan/notes, clean-slate workspace reset, and the ANS_RE / non-empty guards.

**Phase 2 (Prompts & parsing)**  
Must include STRICT_FORMAT (with auto mode), section-header enforcement, and `_strip_code` for ideation.

**Phase 3 (Manager–worker loop)**  
Must harden: no tools on workers, sample-test hard override, finalize-skip, no-progress guard, MAX_TASKS, cut-off digest routing.

**Phase 4 (Observability & packaging)**  
Must add: paired-pass protocol, infra_fail exclusion from pass@1, MockBuffer/readline pin, cap-match for any Qwen3.8 arm.

**Phase 5 (Hardening)**  
Provider clamp detection (compare actual vs configured cap) and reroute budget should be specified here, not left as “provider quirks”.

## Recommendation
Treat the current documents as a solid draft, not a completed plan. Update the README status line immediately and begin Phase 0/1 with the missing invariants listed above.
