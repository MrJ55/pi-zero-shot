# Source analysis (GVS5H)

## Repository

Primary upstream for this port:

**https://github.com/slee-persis/GVS5H**

Paper: [arXiv:2608.26480](https://arxiv.org/abs/2608.26480) · local extract: [`../raw/PAPER.md`](../raw/PAPER.md)

## Important paths (inside GVS5H)

| Path | Role |
|------|------|
| [`paper/`](https://github.com/slee-persis/GVS5H/tree/master/paper) | TeX, PDF, figures |
| [`codebase/v2-current/escalation/multiagent.py`](https://github.com/slee-persis/GVS5H/blob/master/codebase/v2-current/escalation/multiagent.py) | v2 manager–worker scaffold (paper §2.1–§2.3) |
| [`codebase/v2-current/escalation/orchestrator.py`](https://github.com/slee-persis/GVS5H/blob/master/codebase/v2-current/escalation/orchestrator.py) | Multi-provider chat + retry/reroute |
| [`codebase/v1-be9dfa2/escalation/`](https://github.com/slee-persis/GVS5H/tree/master/codebase/v1-be9dfa2/escalation) | Original scaffold (OpenRouter set, §2.4) |
| [`codebase/livecodebench/`](https://github.com/slee-persis/GVS5H/tree/master/codebase/livecodebench) | Benchmark harness + evaluator fix |
| [`runs/`](https://github.com/slee-persis/GVS5H/tree/master/runs) | Full transcripts and workspaces for every reported condition |

## v1 vs v2 (manager arm only)

| | v1 | v2 |
|---|---|---|
| `MULTIAGENT_MAX_ITERS` | 4 | 10 |
| Sample-test verifier | absent | present |
| Cut-off summarizer | absent | present |
| Size bounds on workspace files | absent | present |

Single-call baseline is one call under both; deltas are not strictly pooled across the two sets in the paper.

## Workspace layout (per problem)

```text
<hash>/task.md
<hash>/plan.md
<hash>/tasks.json
<hash>/notes.md
<hash>/solution.py
<hash>/transcript.jsonl
```

See also GVS5H README §3 for how run directories map to paper sections.
