#!/usr/bin/env python3
"""
Shared helpers for the Stop-event hooks (plan-persistence + output-length).

Both hooks need to inspect the session transcript (JSONL). This module
provides a minimal, fail-safe transcript walker plus the specific predicates
each hook needs. Kept self-contained (no cross-hook imports) so the Stop
hooks have no dependency on the primary-source / derive libraries.

The transcript is the session JSONL whose path arrives in the Stop hook's
stdin payload as `transcript_path`. Each line is an event dict; assistant
messages carry tool_use blocks, user messages carry the prompt or tool_result.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

_PLANS_RECORDS_FRAGMENT = "quality_reports/plans/"
_HARNESS_PLANS_FRAGMENT = "/.claude/plans/"
_WRITE_TOOLS = {"Write", "Edit", "MultiEdit"}


def iter_events(transcript_path: Path) -> Iterable[dict]:
    """Yield each JSONL event from the transcript (fail-safe)."""
    if not transcript_path.is_file():
        return
    try:
        with transcript_path.open(encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


def _content_blocks(event: dict) -> list:
    msg = event.get("message", {}) or {}
    content = msg.get("content", [])
    return content if isinstance(content, list) else []


def iter_tool_uses(transcript_path: Path) -> Iterable[tuple[str, dict]]:
    """Yield (tool_name, tool_input) for every tool_use block in the transcript."""
    for event in iter_events(transcript_path):
        for block in _content_blocks(event):
            if isinstance(block, dict) and block.get("type") == "tool_use":
                yield (block.get("name", ""), block.get("input", {}) or {})


def _is_real_user_text(event: dict) -> bool:
    """True if this event is a genuine user prompt (text), not a tool_result."""
    if event.get("type") != "user":
        return False
    content = _content_blocks(event)
    if not content:
        # String content is a plain user message.
        msg = event.get("message", {}) or {}
        return isinstance(msg.get("content"), str)
    return any(
        isinstance(b, dict) and b.get("type") == "text" for b in content
    )


# ---------------------------------------------------------------------------
# Plan-persistence predicates
# ---------------------------------------------------------------------------


def plan_mode_active(transcript_path: Path) -> bool:
    """True if plan mode was used this session.

    Signals: an ExitPlanMode tool_use, OR a write to the harness plan dir
    (~/.claude/plans/...).
    """
    for name, tool_input in iter_tool_uses(transcript_path):
        if name == "ExitPlanMode":
            return True
        if name in _WRITE_TOOLS:
            fp = (tool_input.get("file_path", "") or "")
            if _HARNESS_PLANS_FRAGMENT in fp.replace("\\", "/"):
                return True
    return False


def plan_records_written(transcript_path: Path) -> bool:
    """True if a quality_reports/plans/*.md file was written/edited this session."""
    for name, tool_input in iter_tool_uses(transcript_path):
        if name not in _WRITE_TOOLS:
            continue
        fp = (tool_input.get("file_path", "") or "").replace("\\", "/")
        if _PLANS_RECORDS_FRAGMENT in fp and fp.endswith(".md"):
            return True
    return False


# ---------------------------------------------------------------------------
# Output-length predicates
# ---------------------------------------------------------------------------


def current_turn_events(transcript_path: Path) -> list[dict]:
    """Return events since the last genuine user prompt (the current turn)."""
    events = list(iter_events(transcript_path))
    last_user = -1
    for i, ev in enumerate(events):
        if _is_real_user_text(ev):
            last_user = i
    return events[last_user + 1:] if last_user >= 0 else events


def final_assistant_text(transcript_path: Path) -> str:
    """Text of the last assistant message in the transcript."""
    last = ""
    for event in iter_events(transcript_path):
        if event.get("type") != "assistant":
            continue
        texts = [
            b.get("text", "") or ""
            for b in _content_blocks(event)
            if isinstance(b, dict) and b.get("type") == "text"
        ]
        if texts:
            last = "\n".join(texts)
    return last


def md_written_this_turn(transcript_path: Path) -> bool:
    """True if a .md file was written/edited in the current turn."""
    for ev in current_turn_events(transcript_path):
        for block in _content_blocks(ev):
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            if block.get("name") not in _WRITE_TOOLS:
                continue
            fp = ((block.get("input", {}) or {}).get("file_path", "") or "")
            if fp.replace("\\", "/").endswith(".md"):
                return True
    return False


def significant_line_count(text: str) -> int:
    """Count non-blank lines (the unit the output-length rule is written in)."""
    return sum(1 for ln in text.splitlines() if ln.strip())
