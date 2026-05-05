#!/usr/bin/env python3
"""
Session Reset Hook

Fires at SessionStart on fresh sessions (source: startup or clear) and resets
session-scoped fields in context-monitor-cache.json so:

  1. Warning thresholds (40/55/65/80/90%) fire fresh each session, instead of
     only once per project lifetime.
  2. The pre-compact-state snapshot fallback in context-monitor.py — gated on
     `not shown_warn_90` — can run again. This is load-bearing because the
     PreCompact hook silently bypasses on auto-compact when MCP servers are
     present (anthropics/claude-code#14111), and the 90%-threshold fallback
     is the only thing that captures state in that path.

Does NOT run on source=compact|resume — those preserve context across the
boundary, so resetting the heuristic would mis-warn on an already-loaded
session.

Hook Event: SessionStart (matcher: "startup|clear")
"""

from __future__ import annotations

import json
import os
import sys
import hashlib
from pathlib import Path


def get_session_dir() -> Path:
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if not project_dir:
        return Path.home() / ".claude" / "sessions" / "default"
    project_hash = hashlib.md5(project_dir.encode()).hexdigest()[:8]
    session_dir = Path.home() / ".claude" / "sessions" / project_hash
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


def reset_cache() -> None:
    cache_file = get_session_dir() / "context-monitor-cache.json"
    if not cache_file.exists():
        return
    try:
        data = json.loads(cache_file.read_text())
    except (json.JSONDecodeError, IOError):
        data = {}

    # Reset session-scoped fields. Keep `last_check_time` — it's only throttle
    # state and resetting it would just cause an extra check on the next tool
    # call, no harm either way.
    data["tool_calls"] = 0
    data["shown_warn_80"] = False
    data["shown_warn_90"] = False
    data["shown_learn"] = []
    # session_start_time gets re-initialized by context-monitor on the next
    # tool call (it's a "set if missing" field). Delete the stale value so
    # the next session age starts fresh.
    data.pop("session_start_time", None)
    # Same for last_snapshot_time — old snapshot from previous session is
    # not relevant; let the new session re-trigger snapshot logic past 60%.
    data.pop("last_snapshot_time", None)

    try:
        cache_file.write_text(json.dumps(data, indent=2))
    except IOError:
        pass


def main() -> int:
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, IOError):
        hook_input = {}

    source = hook_input.get("source", "")
    # Only reset on truly fresh sessions. compact|resume retain context.
    if source not in ("startup", "clear"):
        return 0

    reset_cache()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Fail open — never block Claude due to a hook bug.
        sys.exit(0)
