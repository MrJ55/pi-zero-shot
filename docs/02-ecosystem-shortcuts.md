# Ecosystem shortcuts (Pi packages)

Faithfulness to **[slee-persis/GVS5H](https://github.com/slee-persis/GVS5H)** is the primary goal. Some Pi packages can still **expedite** implementation if used narrowly.

## Adopted (optional)

| Package | Role in pi-zero-shot |
|---------|----------------------|
| **[nicobailon/pi-subagents](https://github.com/nicobailon/pi-subagents)** | Optional **spawn helper** for sequential `context: "fresh"` role children. Not the manager, not builtin agents/teams. Policy: [ADR 0004](../adr/0004-subagents-as-spawn-helper.md). |

Install (when used): `pi install npm:pi-subagents` — still implement ledger + prompts + loop in this repo.

Useful upstream docs:

- [README](https://github.com/nicobailon/pi-subagents/blob/main/README.md)
- [Tool reference](https://github.com/nicobailon/pi-subagents/blob/main/docs/tool-reference.md) (`context: "fresh"`)
- [Workflows](https://github.com/nicobailon/pi-subagents/blob/main/docs/workflows.md) (read for patterns; do not adopt parallel review loops for the paper arm)

## Explicitly not on the replication path

| Package | Why |
|---------|-----|
| [pi-agents-team](https://github.com/KristjanPikhof/Pi-Agents-Team) | Parallel team coordinator; summary-only parent; worker reuse and specialized roles confound zero-shot same-prompt design |
| [pi-workflows](https://github.com/osolmaz/pi-workflows) / [pi-extensible-workflows](https://github.com/vekexasia/pi-extensible-workflows) | Powerful graphs; default shared-conversation or product workflows diverge from GVS5H unless heavily constrained — not MVP control plane |
| [pinot-pi](https://github.com/jbstavers/pinot-pi) | Useful role/test ideas later; not the paper ledger loop |
| [paseo](https://github.com/getpaseo/paseo) | Multi-harness UI; orthogonal to scaffold fidelity |

## Fallback

No hard dependency: role calls may use `@earendil-works/pi-ai` or `pi --mode rpc` one-shots with the same paper prompts and ledger injection.
