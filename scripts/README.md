# scripts/

Helpers and experimental harnesses for pi-zero-shot.

| Path | Role |
|------|------|
| `codegen_parse.py` | Parse no-tool worker markdown (`## code` / `## notes`) |
| `openrouter_sequencer.py` | Restartable sequencer: OpenRouter completion workers (no tools), place code, pytest gate |

## codegen_parse

```python
from scripts.codegen_parse import parse_worker_response
code, notes = parse_worker_response(raw_worker_text)
```

Tests: [`../tests/test_codegen_parse.py`](../tests/test_codegen_parse.py).

## openrouter_sequencer

Manager-owned loop (Grok or human writes briefs). Workers are HTTP chat completions only.

```bash
export OPENROUTER_API_KEY=...
export RUN_DIR=/path/to/run   # contains tasks.json, briefs/, workspace/
export WORKER_MODEL=poolside/laguna-s-2.1:free
python scripts/openrouter_sequencer.py
```

See sandbox experiment notes under local `artifacts` runs; pattern matches ADR 0005 (manager tools + pure workers).
