# Smoke test: manager tools + pure codegen workers (Pi)

~30-minute experiment for the product path in [ADR 0005](../../adr/0005-manager-tools-pure-workers.md).

Uses **[pi-subagents](https://github.com/nicobailon/pi-subagents)** to spawn a **no-tool** worker while the parent Pi session acts as manager.

## Prerequisites

1. [Pi](https://github.com/earendil-works/pi) installed and a cloud (or local) model configured.
2. Install subagents extension, e.g.:

   ```bash
   pi install npm:pi-subagents
   ```

   (Package name may vary by fork; use the nicobailon extension or equivalent that supports `noTools` / tool allowlists and per-agent `model`.)

3. Copy the agent definition into a project Pi agents dir:

   ```bash
   mkdir -p .pi/agents
   cp experiments/smoke-test/agents/codegen-worker.md .pi/agents/
   ```

   Or symlink from this repo if you are developing inside it.

4. Optional: set a **cheaper** model on the worker frontmatter (`model: ...`) and keep a **stronger** model on the parent session.

## Run (manual)

1. Open Pi in a **small real or toy repo** (not a huge monorepo for the first try).
2. Parent session = manager. Keep [MANAGER-CHECKLIST.md](./MANAGER-CHECKLIST.md) visible.
3. Pick a tiny goal, e.g. “add `formatGreeting(name: string): string` in `src/greet.ts` with a unit test.”
4. Manager explores (tools), writes a brief from the template, spawns **codegen-worker** with that brief only.
5. Manager places `## code`, runs tests, retries or splits on failure.
6. Compare once to **single-shot** parent-only (no subagent) on the same goal.

## Success criteria for the smoke test

| Check | Pass if |
|-------|--------|
| Spawn | Worker runs with **no tools** (confirm in UI / logs) |
| Asymmetry | Worker model ≠ manager model (if configured) |
| Integration | Only parent wrote files |
| Gate | At least one test or typecheck run by parent |
| Quality | Task completes or fails with a clear brief/integration lesson |

## Files

| Path | Role |
|------|------|
| [agents/codegen-worker.md](./agents/codegen-worker.md) | pi-subagents agent definition |
| [MANAGER-CHECKLIST.md](./MANAGER-CHECKLIST.md) | Parent session discipline |

## Next after smoke test

- Encode the loop in pi-zero-shot (ledger + task graph + RoleLauncher).
- Add a second worker type (e.g. pure test-author) still without tools.
- Try parallel independent units with concurrency 2.
