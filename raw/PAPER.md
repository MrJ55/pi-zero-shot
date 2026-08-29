# Zero-Shot Self-Orchestration with Ledger-Based Control for Improved LLM Coding Performance

**Authors:** Victor Gao, Vida Khosrowshahi, Ali Khosrowshahi, Xihao Sun, Juhyun Lee, Simon (Sang Won) Lee  
**Affiliation:** Persis Capital Inc. / Persis Holdings  
**arXiv:** [2608.26480](https://arxiv.org/abs/2608.26480) (v1, 27 Aug 2026)  
**Official artifact bundle:** [github.com/slee-persis/GVS5H](https://github.com/slee-persis/GVS5H)

## Abstract

Multi-agent large language model systems are widely reported to beat single-model baselines, but the evidence is mixed, and comparisons are usually confounded: pipelines change token budgets, tool calls, and prompts simultaneously, so an aggregate gain rarely reveals what actually helped. We investigate the effect of introducing the manager–worker scaffold over a shared filesystem workspace, with no training and no per-benchmark tuning, measured against the same model answering in a single pass. Across nine models — five open-weight, spanning 9B to ~2.8T parameters, and four frontier closed models — on the 100 latest hard LiveCodeBench problems, the scaffold’s benefit is real but conditional: large and statistically significant for some (Qwen3.8-27B +23.4, GPT-5.6-Luna +10.6 and GPT-5.6-Terra +8.0, each over five paired passes; Kimi-K3 +30.4 and Minimax-M3 +11.0 over five paired passes with reasoning off, both at p < 10⁻⁴, and +42 and +12 in a single pass at a 128k cap) and null or negative for others (Qwen3.6-35B −1 to −9 with reasoning off). With the manager, Opus-5 achieves the highest score in the study at 91% in one pass. Running a manager roughly triples the token bill, but it buys accuracy more cheaply than moving to a larger model does: GPT-5.6-Terra with a manager nearly matches Fable 5’s single-call accuracy (85.0 against 87.4, p = 0.59) at a fifth of the price ($11.71 against $61.11 per 100-problem pass, p < 10⁻⁴), and the Qwen-27B arm does it for $51.75 on weights anyone can self-host. Our transcript analysis finds several mechanisms behind the gains, of which two recur: context management, in which short worker calls and shared notes organize state and reduce truncation, and problem decomposition. Improvements are modest for large models with reasoning enabled, but larger for some models with reasoning disabled and for smaller models with reasoning enabled.

## Full text

| Format | Link |
|--------|------|
| arXiv HTML | https://arxiv.org/html/2608.26480v1 |
| arXiv PDF | https://arxiv.org/pdf/2608.26480 |
| GVS5H TeX | https://github.com/slee-persis/GVS5H/blob/master/paper/zero_shot_self_orchestration_with_ledger_based_control_for_improved_llm_coding_performance_2026-08-25.tex |
| GVS5H PDF | https://github.com/slee-persis/GVS5H/blob/master/paper/zero_shot_self_orchestration_with_ledger_based_control_for_improved_llm_coding_performance_2026-08-25.pdf |

License of the paper on arXiv: CC BY 4.0 (see arXiv page).
