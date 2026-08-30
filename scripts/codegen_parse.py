"""Parse no-tool worker markdown output into code and notes sections."""
from __future__ import annotations

import re


def parse_worker_response(text: str) -> tuple[str | None, str]:
    """Parse no-tool worker output into (code, notes).

    Expect markdown with sections:
      ## code
      optional fenced block (``` or ```python etc.)
      ## notes
      free text

    Returns:
      code: inner fence content, or raw section body if no fence;
            None if section missing or only whitespace.
      notes: notes section body stripped; "" if missing.
    """
    code = _extract_section(text, "code")
    notes = _extract_section(text, "notes")

    if code is None:
        code_value = None
    else:
        stripped = code.strip()
        if not stripped:
            code_value = None
        else:
            fenced = _extract_fenced(stripped)
            code_value = fenced if fenced is not None else stripped

    notes_value = notes.strip() if notes is not None else ""
    return code_value, notes_value


def _extract_section(text: str, header: str) -> str | None:
    pattern = rf"^##\s+{re.escape(header)}\s*$(.*?)(?=^##\s+\w+\s*$|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
    if match is None:
        return None
    return match.group(1)


def _extract_fenced(body: str) -> str | None:
    fence_match = re.search(
        r"^```[^\n]*\n(.*?)```", body, re.DOTALL | re.MULTILINE
    )
    if fence_match is None:
        return None
    return fence_match.group(1)
