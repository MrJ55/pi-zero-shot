"""Contract tests for scripts.codegen_parse."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.codegen_parse import parse_worker_response


def test_basic_python_fence():
    text = """
## code

```python
def hello():
    return 1
```

## notes

none
"""
    code, notes = parse_worker_response(text)
    assert code is not None
    assert "def hello()" in code
    assert "return 1" in code
    assert notes.strip().lower() == "none"


def test_code_without_lang_tag():
    text = """
## code

```
x = 2
```

## notes

simple assignment
"""
    code, notes = parse_worker_response(text)
    assert code is not None
    assert code.strip() == "x = 2"
    assert "simple" in notes.lower()


def test_blocked_no_code():
    text = """
## code

## notes

BLOCKED: insufficient context
"""
    code, notes = parse_worker_response(text)
    assert code is None or code.strip() == ""
    assert "BLOCKED" in notes


def test_missing_notes_defaults():
    text = """
## code

```python
ok = True
```
"""
    code, notes = parse_worker_response(text)
    assert code is not None
    assert "ok = True" in code
