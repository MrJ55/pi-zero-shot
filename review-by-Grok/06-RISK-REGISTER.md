# 06 — Risk Register

| ID | Severity | Probability | Description | Mitigation | Owner |
|----|----------|-------------|-------------|------------|-------|
| R1 | Critical | High | Missing infra_fail causes provider outages to be scored as model failures | Add flag to transcript + grader; exclude from pass@1 | Phase 1 / 4 |
| R2 | Critical | High | Worker acquires tools → multi-turn agent, breaks measured invariant | Change ADR 0004 to “no tools”; add test | Phase 3 |
| R3 | Critical | Medium | Local eval uses unfixed LiveCodeBench MockBuffer | Vendor the §3.3 fix and pin id list | Phase 4 |
| R4 | High | High | No paired-pass protocol → cannot support paper significance claims | Specify 5-pass + paired t-test in Phase 4 | Phase 4 |
| R5 | High | Medium | Notes grow unbounded (append or cut-off digests) | Enforce rewrite + hard bounds + digest routing | Phase 1 / 3 |
| R6 | High | Medium | Finalize always runs and destroys good intermediate answer | Implement finalize-skip | Phase 3 |
| R7 | Medium | High | Status line misleads contributors | Fix README + VERIFY-LOG | Immediate |
| R8 | Medium | Medium | ADR 0002 status inconsistency wastes Phase 0 time | Resolve Accepted vs Proposed | Phase 0 |
| R9 | Medium | Medium | No MAX_TASKS → unbounded task list | Add config + enforcement | Phase 1 / 3 |
| R10 | Low | Medium | No LICENSE | Add MIT (or chosen) LICENSE | Immediate |

Critical risks block any claim of faithful reproduction or trustworthy evaluation numbers.
