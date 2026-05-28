#!/usr/bin/env python3
"""
Unit tests for stop_hooks_lib.py (plan-persistence + output-length predicates).

Run:  python3 -m pytest .claude/hooks/test_stop_hooks_lib.py -q
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

_LIB = Path(__file__).resolve().parent / "stop_hooks_lib.py"
_spec = importlib.util.spec_from_file_location("stop_hooks_lib", _LIB)
lib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lib)


def _write_transcript(tmp_path: Path, events: list[dict]) -> Path:
    p = tmp_path / "transcript.jsonl"
    p.write_text("\n".join(json.dumps(e) for e in events))
    return p


def _assistant(blocks: list[dict]) -> dict:
    return {"type": "assistant", "message": {"role": "assistant", "content": blocks}}


def _user_text(text: str) -> dict:
    return {"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": text}]}}


def _tool_use(name: str, **inp) -> dict:
    return {"type": "tool_use", "name": name, "input": inp}


def _text(t: str) -> dict:
    return {"type": "text", "text": t}


# ---------------------------------------------------------------------------
# plan_mode_active
# ---------------------------------------------------------------------------

def test_plan_mode_active_via_exitplanmode(tmp_path):
    t = _write_transcript(tmp_path, [
        _user_text("do the thing"),
        _assistant([_tool_use("ExitPlanMode")]),
    ])
    assert lib.plan_mode_active(t) is True


def test_plan_mode_active_via_harness_plan_write(tmp_path):
    t = _write_transcript(tmp_path, [
        _assistant([_tool_use("Write", file_path="/Users/x/.claude/plans/foo.md")]),
    ])
    assert lib.plan_mode_active(t) is True


def test_plan_mode_inactive(tmp_path):
    t = _write_transcript(tmp_path, [
        _user_text("just edit a file"),
        _assistant([_tool_use("Edit", file_path="scripts/01.do")]),
    ])
    assert lib.plan_mode_active(t) is False


# ---------------------------------------------------------------------------
# plan_records_written
# ---------------------------------------------------------------------------

def test_plan_records_written_true(tmp_path):
    t = _write_transcript(tmp_path, [
        _assistant([_tool_use("Write", file_path="/repo/quality_reports/plans/2026-05-28_x.md")]),
    ])
    assert lib.plan_records_written(t) is True


def test_plan_records_written_false_wrong_dir(tmp_path):
    t = _write_transcript(tmp_path, [
        _assistant([_tool_use("Write", file_path="/Users/x/.claude/plans/foo.md")]),
    ])
    assert lib.plan_records_written(t) is False


def test_plan_records_written_false_not_md(tmp_path):
    t = _write_transcript(tmp_path, [
        _assistant([_tool_use("Write", file_path="/repo/quality_reports/plans/notes.txt")]),
    ])
    assert lib.plan_records_written(t) is False


# ---------------------------------------------------------------------------
# final_assistant_text + significant_line_count
# ---------------------------------------------------------------------------

def test_final_assistant_text(tmp_path):
    t = _write_transcript(tmp_path, [
        _assistant([_text("first")]),
        _user_text("more"),
        _assistant([_text("final answer")]),
    ])
    assert lib.final_assistant_text(t) == "final answer"


def test_significant_line_count():
    assert lib.significant_line_count("a\n\nb\n   \nc") == 3
    assert lib.significant_line_count("") == 0


# ---------------------------------------------------------------------------
# md_written_this_turn (scoped to current turn)
# ---------------------------------------------------------------------------

def test_md_written_this_turn_true(tmp_path):
    t = _write_transcript(tmp_path, [
        _user_text("write a report"),
        _assistant([_tool_use("Write", file_path="/repo/quality_reports/reviews/r.md")]),
        _assistant([_text("done")]),
    ])
    assert lib.md_written_this_turn(t) is True


def test_md_written_prior_turn_not_counted(tmp_path):
    t = _write_transcript(tmp_path, [
        _user_text("write a report"),
        _assistant([_tool_use("Write", file_path="/repo/x.md")]),
        _user_text("now just answer in chat"),     # new turn starts here
        _assistant([_text("a long answer")]),
    ])
    # The .md write was in the PRIOR turn; current turn wrote nothing.
    assert lib.md_written_this_turn(t) is False


def test_md_written_this_turn_false_non_md(tmp_path):
    t = _write_transcript(tmp_path, [
        _user_text("edit code"),
        _assistant([_tool_use("Edit", file_path="scripts/01.do")]),
    ])
    assert lib.md_written_this_turn(t) is False
