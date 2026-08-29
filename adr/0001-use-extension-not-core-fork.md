# ADR 0001: Implement as Pi Extension / Skill, not Core Fork

## Status

Accepted

## Context

Pi’s design philosophy (see CONTRIBUTING.md and RFCs) strongly prefers a minimal core that is extended via skills, prompt templates, and packages rather than growing built-in multi-agent machinery.

The GVS5H scaffold is a self-contained, training-free orchestration pattern that can be expressed as a supervisor + ledger + short-lived workers.

## Decision

Implement Zero-Shot Self-Orchestration as a **first-class Pi extension or skill** (this repository), not as a fork or PR against pi core.

## Consequences

- Positive: stays compatible with upstream Pi evolution; users opt-in; easier packaging and iteration.
- Positive: respects Pi’s “extensions over core” rule.
- Negative: some deeper integration points (e.g. perfect TUI visibility, session-tree primitives) may require more work or future core hooks.
- Negative: cannot assume core changes; must work with existing tool and session APIs.

## Alternatives Considered

- Fork pi and add built-in mode → rejected (against project philosophy, maintenance burden).
- Pure external script that shells out to pi → weaker integration and observability.
