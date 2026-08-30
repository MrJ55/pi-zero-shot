#!/usr/bin/env python3
"""Restartable sequencer: pure LLM workers (no tools) via OpenRouter.

Manager (e.g. Grok) owns briefs, this script, and integration. Workers are
chat completions only — no repo tools.

Run from a run directory containing tasks.json, briefs/, workspace/.

Env:
  OPENROUTER_API_KEY  required
  WORKER_MODEL        default poolside/laguna-s-2.1:free
  MAX_ATTEMPTS        default 3
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

RUN = Path(__file__).resolve().parent
# Allow: python scripts/openrouter_sequencer.py with RUN= override
if os.environ.get("RUN_DIR"):
    RUN = Path(os.environ["RUN_DIR"]).resolve()

WORK = RUN / "workspace"
STATE_PATH = RUN / "state.json"
TRANSCRIPT = RUN / "transcript.jsonl"
MODEL = os.environ.get("WORKER_MODEL", "poolside/laguna-s-2.1:free")
API_URL = os.environ.get(
    "OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions"
)


def log(event: dict) -> None:
    with TRANSCRIPT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"completed": [], "attempts": {}}


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def worker_generate(prompt: str) -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise SystemExit("OPENROUTER_API_KEY not set")
    body = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a codegen worker with no tools and no repository access. "
                    "Implement only what the brief asks. Respond with exactly two sections:\n"
                    "## code\n\n```python\n# implementation\n```\n\n## notes\n\n...\n"
                    "Avoid triple-backtick sequences inside docstrings; use plain quotes."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 2048,
        "temperature": 0.2,
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/MrJ55/pi-zero-shot",
            "X-Title": "pi-zero-shot-sequencer",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def extract_code(text: str) -> str | None:
    m = re.search(r"##\s*code\s*\n(.*?)(?=\n##\s*|\Z)", text, re.S | re.I)
    if not m:
        return None
    body = m.group(1).strip()
    # Opening fence at start of body; closing at last ```
    fence = re.match(r"```(?:\w+)?\n([\s\S]*)```\s*$", body)
    if fence:
        return fence.group(1).strip()
    fence = re.search(r"```(?:\w+)?\n([\s\S]*?)```", body)
    if fence:
        return fence.group(1).strip()
    return body if body else None


def place_module(code: str, rel: str = "scripts/codegen_parse.py") -> Path:
    target = WORK / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    init = target.parent / "__init__.py"
    if not init.exists():
        init.write_text("# package\n", encoding="utf-8")
    target.write_text(code.rstrip() + "\n", encoding="utf-8")
    return target


def run_tests() -> tuple[int, str]:
    import subprocess

    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_codegen_parse.py", "-q"],
        cwd=str(WORK),
        capture_output=True,
        text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out


def main() -> int:
    tasks = json.loads((RUN / "tasks.json").read_text(encoding="utf-8"))["tasks"]
    state = load_state()
    max_attempts = int(os.environ.get("MAX_ATTEMPTS", "3"))

    for task in tasks:
        tid = task["id"]
        if tid in state["completed"]:
            print(f"skip completed {tid}")
            continue

        brief_path = RUN / "briefs" / f"{tid}.md"
        brief = brief_path.read_text(encoding="utf-8")
        attempts = int(state["attempts"].get(tid, 0))
        target_rel = task.get("target", "scripts/codegen_parse.py")

        while attempts < max_attempts:
            attempts += 1
            state["attempts"][tid] = attempts
            save_state(state)
            print(f"== worker {tid} attempt {attempts} model={MODEL}")
            try:
                raw = worker_generate(brief)
            except Exception as e:
                log({"task": tid, "attempt": attempts, "error": str(e)})
                print("worker error:", e)
                continue

            out_path = RUN / "out" / f"{tid}-a{attempts}.md"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(raw, encoding="utf-8")
            log({"task": tid, "attempt": attempts, "raw_path": str(out_path)})

            code = extract_code(raw)
            if not code:
                print("no code extracted; retry")
                continue

            place_module(code, target_rel)
            rc, tout = run_tests()
            (RUN / "out" / f"{tid}-a{attempts}-pytest.txt").write_text(
                tout, encoding="utf-8"
            )
            print(tout)
            if rc == 0:
                state["completed"].append(tid)
                save_state(state)
                print(f"PASS {tid}")
                break
            print(f"FAIL tests attempt {attempts}")
            brief = (
                brief
                + "\n\nPrevious attempt failed tests. Pytest output:\n```\n"
                + tout[-3000:]
                + "\n```\nFix the implementation. Avoid backticks inside docstrings.\n"
            )
        else:
            print(f"GAVE UP {tid}")
            return 1

    print("ALL DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
