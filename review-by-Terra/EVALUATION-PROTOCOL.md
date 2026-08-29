# Evaluation protocol

## Conditions

| Condition | Definition |
|---|---|
| Baseline | Direct solve under the selected task, model, tool, output, and global-budget policy |
| Scaffold | Ledgered sequential manager-worker solve under equivalent externally relevant caps |

The orchestration policy is the only intended difference.

## Frozen manifest

Pin repository revision, task ids/content hashes, implementation version, provider/model/version, reasoning and sampling settings, tool policy, prompts, token/time/spend caps, pass count, seed where available, grader/regrader versions, and redaction policy. Hash it into every report.

## Procedure

1. Predeclare tasks and exclusions.
2. Run paired/interleaved baseline and scaffold executions.
3. Retain redacted raw transcript, normalized answer, artifact, usage, retries, failure status, and grader data.
4. Grade with the same frozen grader; regrade both sides if needed.
5. Report paired task deltas, aggregate outcome, cost, latency, and reliability.

No cross-run memory, selective manual repair, post-outcome task replacement, unmatched settings, or silent exclusions in benchmark mode. A positive quality delta without cost and latency is incomplete.
