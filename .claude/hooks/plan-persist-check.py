#!/usr/bin/env python3
"""
Plan-Persistence Stop hook (BLOCKING).

Enforces the "plans must be written down" rule (`.claude/rules/workflow.md` §1):
if plan mode was used this session, a plan file must exist under
`quality_reports/plans/`. Terminal output and the harness plan file
(~/.claude/plans/) are ephemeral; the project records are not.

Why a Stop hook (not a PreToolUse/PermissionRequest on ExitPlanMode): during
plan mode the agent can only write the harness plan file, never
`quality_reports/plans/`, so the records copy can only be written AFTER plan
mode exits. The Stop hook fires at turn-end and blocks once if the session
planned but didn't persist.

Blocks via {"decision":"block","reason":...}. Respects `stop_hook_active` so
it nudges at most once per turn (then lets the turn end) — never an infinite
loop. Fail-open on any internal exception.

Install (in .claude/settings.json, Stop):
    python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/plan-persist-check.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path


def _load_lib():
    p = Path(__file__).resolve().parent / "stop_hooks_lib.py"
    spec = importlib.util.spec_from_file_location("stop_hooks_lib", p)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {p}")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


REASON = (
    "PLAN NOT PERSISTED.\n\n"
    "You used plan mode this session but no plan file was written to "
    "quality_reports/plans/. Terminal output and the harness plan file are "
    "ephemeral; the project record is not (workflow.md §1: \"Save to disk\").\n\n"
    "Before stopping, copy your plan to "
    "quality_reports/plans/YYYY-MM-DD_<short-slug>.md and add a one-line entry "
    "to quality_reports/plans/INDEX.md. Then you may stop."
)


def main() -> None:
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    # Avoid loops: if a prior Stop hook already fired this turn, let it end.
    if hook_input.get("stop_hook_active"):
        sys.exit(0)

    transcript_path_str = hook_input.get("transcript_path", "") or ""
    if not transcript_path_str:
        sys.exit(0)
    transcript_path = Path(transcript_path_str)

    lib = _load_lib()

    if not lib.plan_mode_active(transcript_path):
        sys.exit(0)
    if lib.plan_records_written(transcript_path):
        sys.exit(0)

    json.dump({"decision": "block", "reason": REASON}, sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
