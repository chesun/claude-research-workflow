#!/usr/bin/env python3
"""
Output-Length advisory Stop hook (NON-BLOCKING).

Enforces `.claude/rules/output-length.md` (>15 lines → write to a .md file)
with the one thing the prose rule lacked: a deterministic trigger. At
turn-end, if the final assistant message exceeds the line threshold AND no
.md file was written this turn, it INJECTS a reminder (via
hookSpecificOutput.additionalContext) — it never blocks. The win over the
prose rule is that the reminder actually reaches the model's next turn
instead of being ignored mid-context.

Respects `stop_hook_active` (fires at most once per turn). Fail-open.

Install (in .claude/settings.json, Stop):
    python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/output-length-check.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

# The rule's own threshold. Tune here if it proves noisy.
LINE_THRESHOLD = 15


def _load_lib():
    p = Path(__file__).resolve().parent / "stop_hooks_lib.py"
    spec = importlib.util.spec_from_file_location("stop_hooks_lib", p)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {p}")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _emit(additional_context: str) -> None:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": additional_context,
        },
        "suppressOutput": True,
    }
    sys.stdout.write(json.dumps(payload))
    sys.stdout.flush()


def main() -> None:
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    if hook_input.get("stop_hook_active"):
        sys.exit(0)

    transcript_path_str = hook_input.get("transcript_path", "") or ""
    if not transcript_path_str:
        sys.exit(0)
    transcript_path = Path(transcript_path_str)

    lib = _load_lib()

    text = lib.final_assistant_text(transcript_path)
    n = lib.significant_line_count(text)
    if n <= LINE_THRESHOLD:
        sys.exit(0)

    # A turn that wrote a .md already exported its long content — exempt it.
    if lib.md_written_this_turn(transcript_path):
        sys.exit(0)

    _emit(
        f"OUTPUT-LENGTH: your final response was ~{n} non-blank lines "
        f"(> {LINE_THRESHOLD}). Per .claude/rules/output-length.md, long "
        "structured output (reports, summaries, tables, reviews) should be "
        "written to a .md file with a short pointer inline, so it survives in "
        "the project record instead of scrolling out of the terminal. If this "
        "was a genuinely conversational answer, no action needed."
    )
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
