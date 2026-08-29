# Implementation plan

Execute phases **in order** (0–5). Each phase file contains:

- Goals and exit criteria  
- Background pointers into `docs/` and `adr/`  
- **Detailed task list** suitable for a coding model  
- Verification steps  

## Phase index

| File | Phase |
|------|--------|
| [phase-00-discovery-mapping.md](./phase-00-discovery-mapping.md) | 0 Discovery & mapping |
| [phase-01-ledger-primitives.md](./phase-01-ledger-primitives.md) | 1 Core ledger primitives |
| [phase-02-prompts-parsing.md](./phase-02-prompts-parsing.md) | 2 Role prompts & parsing |
| [phase-03-manager-worker-loop.md](./phase-03-manager-worker-loop.md) | 3 Manager–worker loop as extension |
| [phase-04-observability-packaging.md](./phase-04-observability-packaging.md) | 4 Observability & packaging |
| [phase-05-hardening.md](./phase-05-hardening.md) | 5 Hardening & polish |

## Rules for implementers

1. Read the phase’s **Background** links before coding.  
2. Complete tasks in listed order unless marked parallel.  
3. Do not skip verification.  
4. Do not implement phase N+1 features in phase N.  
5. Prefer small commits per task group.  
6. Keep workers’ contexts short — inject only ledger state.  
7. Record notable deviations or verification results in `VERIFY-LOG.md`.
