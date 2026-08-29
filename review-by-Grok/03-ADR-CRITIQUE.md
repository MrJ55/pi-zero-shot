# 03 — ADR Critique

## ADR 0001 — Use extension, not core fork
**Status in repo:** Accepted  
**Assessment:** Correct and well-motivated. Keeping the scaffold outside Pi core preserves upgradability and matches the non-goals. No change required.

## ADR 0002 — Filesystem ledger
**Status in repo:** Proposed (Decision text already prefers real FS)  
**Assessment:** The Decision section already states a preference for a real filesystem workspace. The “Proposed” status and the Phase 0 task “decide and record” are redundant and create unnecessary ambiguity.  
**Recommendation:** Mark Accepted and remove the open decision task from Phase 0, or keep Proposed and strike the decisive language from the Decision section. Consistency matters more than the particular choice.

## ADR 0003 — Sequential manager–worker
**Status in repo:** Accepted  
**Assessment:** Correct. Matches GVS5H v2 measured path. Explicit rejection of parallel specialist teams is valuable. No change required.

## ADR 0004 — pi-subagents as spawn helper only
**Status in repo:** Accepted (strongest ADR)  
**Assessment:** Excellent scoping. The “do not use” list (builtin worker/reviewer/scout, council modes, parallel fan-out, fork-default context) is exactly the right protective language.  
**Required amendment:** §5 currently says “prefer no / minimal tools”. GVS5H workers have **zero** tools. Change to “no tools, period” and add a Phase 3 test that fails if any tool surface is exposed to a role call. This is the single highest-leverage wording change in the entire plan.

## Missing ADRs that should be added
- Validation / parsing strategy (STRICT_FORMAT, section headers, ANS_RE guard).
- Persistence schema / migration for the ledger (even if filesystem).
- Evaluation protocol (paired passes, infra_fail exclusion, evaluator pinning).
- Provider clamp / reroute budget policy.
