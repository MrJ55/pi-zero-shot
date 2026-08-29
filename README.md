# pi-zero-shot

**Zero-Shot Self-Orchestration with Ledger-Based Control** — implemented as an extension for the [earendil-works/pi](https://github.com/earendil-works/pi) agent harness.

This repository ports the manager–worker scaffold from the paper:

> **Zero-Shot Self-Orchestration with Ledger-Based Control for Improved LLM Coding Performance**  
> arXiv:2608.26480  
> Source artifacts: [slee-persis/GVS5H](https://github.com/slee-persis/GVS5H)

to Pi’s extensible architecture (skills / extensions), preserving the training-free, zero-shot, shared-filesystem-ledger design.

## Status

Early design & planning stage. See:

- [docs/plan.md](docs/plan.md) — full phased implementation plan + task list
- [docs/architecture.md](docs/architecture.md) — high-level mapping of paper primitives → Pi
- [adr/](adr/) — Architecture Decision Records

## Quick links

| Resource | Link |
|----------|------|
| Paper (HTML) | https://arxiv.org/html/2608.26480v1 |
| Paper artifacts (code + runs) | https://github.com/slee-persis/GVS5H |
| Pi agent harness | https://github.com/earendil-works/pi |
| Pi site | https://pi.dev |

## License

TBD (planned MIT, matching both source projects where possible).
