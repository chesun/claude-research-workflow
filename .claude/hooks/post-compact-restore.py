#!/usr/bin/env python3
"""
Post-Compact Context Restoration Hook

Fires after compaction (SessionStart with source="compact") to restore context.
Reads saved state from the session directory and prints it so Claude knows
where it left off.

Hook Event: SessionStart (matcher: "compact|resume")
Returns: Exit code 0 (output to stdout)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Colors for terminal output
CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
NC = "\033[0m"  # No color


def get_session_dir() -> Path:
    """Get the session directory for storing state files."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if not project_dir:
        return Path.home() / ".claude" / "sessions" / "default"

    # Use a hash of the project dir for the session subdir
    import hashlib
    project_hash = hashlib.md5(project_dir.encode()).hexdigest()[:8]
    session_dir = Path.home() / ".claude" / "sessions" / project_hash
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


def read_pre_compact_state() -> dict | None:
    """Read and delete the pre-compact state file."""
    session_dir = get_session_dir()
    state_file = session_dir / "pre-compact-state.json"

    if not state_file.exists():
        return None

    try:
        state = json.loads(state_file.read_text())
        state_file.unlink()  # Clean up after restore
        return state
    except (json.JSONDecodeError, IOError):
        return None


def find_active_plan(project_dir: str) -> dict | None:
    """Find the most recent plan file and extract its status."""
    plans_dir = Path(project_dir) / "quality_reports" / "plans"
    if not plans_dir.exists():
        return None

    # Get most recent plan file
    plan_files = sorted(plans_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not plan_files:
        return None

    latest_plan = plan_files[0]
    content = latest_plan.read_text()

    # Extract status from plan content
    status = "unknown"
    if "COMPLETED" in content.upper():
        status = "completed"
    elif "APPROVED" in content.upper():
        status = "in_progress"
    elif "DRAFT" in content.upper():
        status = "draft"

    # Extract current task if present
    current_task = None
    for line in content.split("\n"):
        if "- [ ]" in line:  # First unchecked task
            current_task = line.replace("- [ ]", "").strip()
            break

    return {
        "plan_path": str(latest_plan),
        "plan_name": latest_plan.name,
        "status": status,
        "current_task": current_task
    }


def find_recent_session_log(project_dir: str) -> dict | None:
    """Find the most recent session log."""
    logs_dir = Path(project_dir) / "quality_reports" / "session_logs"
    if not logs_dir.exists():
        return None

    log_files = sorted(logs_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not log_files:
        return None

    return {
        "log_path": str(log_files[0]),
        "log_name": log_files[0].name
    }


def format_restoration_message(
    pre_compact_state: dict | None,
    plan_info: dict | None,
    session_log: dict | None
) -> str:
    """Striking system-reminder restoration message. Plain text — no ANSI; rendered in a system-reminder block."""
    lines = []
    lines.append("🔄 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 🔄")
    lines.append("   CONTEXT RESTORED AFTER COMPACTION")

    if pre_compact_state:
        tool_calls = pre_compact_state.get("tool_calls")
        max_calls = pre_compact_state.get("max_tool_calls")
        percentage = pre_compact_state.get("percentage")
        if tool_calls is not None and max_calls:
            pct_str = f"{percentage:.0f}%" if percentage is not None else "?"
            lines.append(f"   Compacted at: {tool_calls} / {max_calls} tool calls ({pct_str})")
        if pre_compact_state.get("trigger"):
            lines.append(f"   Trigger: {pre_compact_state['trigger']}")
        if pre_compact_state.get("plan_path"):
            lines.append(f"   Plan: {pre_compact_state['plan_path']}")
        if pre_compact_state.get("current_task"):
            ct = pre_compact_state['current_task']
            if len(ct) > 100:
                ct = ct[:100] + "…"
            lines.append(f"   Last task: {ct}")
        if pre_compact_state.get("decisions"):
            lines.append("   Recent decisions:")
            for decision in pre_compact_state["decisions"][-3:]:
                d = decision[:90] + "…" if len(decision) > 90 else decision
                lines.append(f"     • {d}")

    if plan_info:
        lines.append(f"   Active plan now: {plan_info['plan_name']} ({plan_info['status']})")
        if plan_info.get("current_task"):
            ct = plan_info['current_task']
            if len(ct) > 100:
                ct = ct[:100] + "…"
            lines.append(f"   Next task: {ct}")

    if session_log:
        lines.append(f"   Session log: {session_log['log_name']}")

    lines.append("   ▶ Read active plan to confirm objectives")
    lines.append("   ▶ git status / diff to check uncommitted changes")
    lines.append("   ▶ Continue from where you left off")
    lines.append("🔄 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 🔄")
    return "\n".join(lines)


def main() -> int:
    """Main hook entry point."""
    # Read hook input (not strictly needed but good practice)
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, IOError):
        hook_input = {}

    # Only run on compact/resume sessions
    session_source = hook_input.get("source", "")
    if session_source not in ("compact", "resume"):
        return 0

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if not project_dir:
        return 0

    # Gather context
    pre_compact_state = read_pre_compact_state()
    plan_info = find_active_plan(project_dir)
    session_log = find_recent_session_log(project_dir)

    # Belt-and-suspenders compaction logging: if pre-compact.py didn't fire
    # (Claude Code bug #14111: PreCompact bypasses on auto-compact when MCP
    # servers are present), record the compaction event from the snapshot
    # data instead. Skipped when there's no snapshot (nothing to record).
    if pre_compact_state:
        try:
            log_file = get_session_dir() / "compactions.jsonl"
            entry = {
                "ts": datetime.now().isoformat(),
                "trigger": pre_compact_state.get("trigger", "unknown") + ":restored",
                "tool_calls": pre_compact_state.get("tool_calls"),
                "max_tool_calls": pre_compact_state.get("max_tool_calls"),
                "percentage": pre_compact_state.get("percentage"),
                "session_start_time": pre_compact_state.get("session_start_time"),
                "plan_path": pre_compact_state.get("plan_path"),
                "plan_status": pre_compact_state.get("plan_status"),
                "session_source": session_source,
            }
            with log_file.open("a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass

    # If we have any context to restore, emit it via JSON additionalContext
    # so it surfaces as a visible system-reminder block. SessionStart hook
    # output IS visible per Claude Code docs; the JSON channel is the most
    # reliable form across UI versions.
    if pre_compact_state or plan_info or session_log:
        message = format_restoration_message(pre_compact_state, plan_info, session_log)
        payload = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": message,
            },
            "suppressOutput": True,
        }
        try:
            sys.stdout.write(json.dumps(payload))
            sys.stdout.flush()
        except Exception:
            # Fallback: plain print
            print(message)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Fail open — never block Claude due to a hook bug
        sys.exit(0)
