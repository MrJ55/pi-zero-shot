# 07 — Implementation Priority

## Critical path (must be solid before any evaluation claim)

1. **Phase 0 hygiene** (½ day)  
   Resolve ADR 0002 status, fix README status line, initialise VERIFY-LOG.

2. **Phase 1 — Ledger + transcript** (2–3 days)  
   LedgerWorkspace, clean-slate reset, transcript schema including `infra_exhausted`, hard size bounds, ANS_RE guard.

3. **Phase 2 — Prompts & parsers** (1–2 days)  
   Port role prompts, STRICT_FORMAT, section parsing, ideation `_strip_code`.

4. **Phase 3 — Manager–worker loop** (3–4 days)  
   Deterministic TS state machine, sample-test hard override, finalize-skip, no-progress guard, MAX_TASKS, zero-tool invariant, optional pi-subagents spawn.

5. **Phase 4 — Evaluation driver** (2–3 days)  
   Paired-pass harness, infra_fail exclusion, MockBuffer pin, cap-match if needed, single-shot baseline.

6. **Phase 5 — Hardening & packaging** (2 days)  
   Provider clamp detection, cost metrics, installable extension, TUI visibility.

## Quick wins (do first)
- README status line + LICENSE.
- ADR 0004 wording change (“no tools, period”).
- Add empty VERIFY-LOG rows for Phase 0 exit criteria.

## Estimated core effort
~12–15 focused days to a minimal faithful vertical slice that can run the single-shot vs manager comparison under controlled conditions. Full paper-level statistical protocol adds the evaluation work above.
