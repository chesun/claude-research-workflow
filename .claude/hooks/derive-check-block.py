#!/usr/bin/env python3
"""
Derive-Don't-Guess blocking PreToolUse hook (OPT-IN).

The blocking counterpart to derive-check-advisory.py. Blocks an Edit/Write/
MultiEdit to an analysis/paper file when it introduces a read/input path that
does not resolve on disk (or a Stata macro undefined repo-wide) — the
highest-confidence guess signal.

OFF BY DEFAULT. This hook is inert unless the opt-in flag file exists:

    .claude/state/derive-guess-block.enabled

Enable it per-project once the advisory hook's logs show an acceptable
false-positive profile:

    touch .claude/state/derive-guess-block.enabled

Disable by removing the flag. When the flag is absent the hook exits 0
immediately (no-op), so registering it in settings.json is always safe.

Escape hatch: a `derive-ok` comment in the edit delta (same as the advisory
hook). Every invocation that reaches the enabled path is recorded in
.claude/state/derive-guard.log (append-only JSONL audit trail).

Shared logic in .claude/hooks/derive_lib.py.

Install (in .claude/settings.json, PreToolUse, matcher "Write|Edit|MultiEdit"):
    python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/derive-check-block.py

Fail-open on any internal exception.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_LOG_MAX_BYTES = 1_000_000


def _load_lib():
    lib_path = Path(__file__).resolve().parent / "derive_lib.py"
    spec = importlib.util.spec_from_file_location("derive_lib", lib_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {lib_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _log(project_root: Path, entry: dict) -> None:
    """Append a JSONL audit entry; never raise (fail-open on logging)."""
    try:
        log_dir = project_root / ".claude" / "state"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "derive-guard.log"
        if log_path.exists() and log_path.stat().st_size > _LOG_MAX_BYTES:
            log_path.replace(log_path.with_suffix(".log.old"))
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass


def main() -> None:
    lib = _load_lib()

    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "")
    if tool_name not in {"Edit", "Write", "MultiEdit"}:
        sys.exit(0)

    tool_input = hook_input.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "") or ""
    if not file_path or lib.language_for_path(file_path) is None:
        sys.exit(0)

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", hook_input.get("cwd", ""))
    if not project_dir:
        sys.exit(0)
    project_root = Path(project_dir)

    # Opt-in gate: inert unless the flag file exists.
    flag = project_root / ".claude" / "state" / "derive-guess-block.enabled"
    if not flag.exists():
        sys.exit(0)

    unresolved = lib.analyze(tool_name, tool_input, file_path, project_root)
    if not unresolved:
        sys.exit(0)

    try:
        rel = str(Path(file_path).resolve().relative_to(project_root.resolve()))
    except (ValueError, OSError):
        rel = file_path

    ts = datetime.now(timezone.utc).isoformat()
    _log(project_root, {
        "ts": ts,
        "decision": "BLOCK",
        "file": rel,
        "paths": [p for p, _ in unresolved],
    })

    reason = lib.build_advisory_message(rel, unresolved) + (
        "\n\nThis edit is BLOCKED (derive-guess-block opt-in is enabled). "
        "Derive the real value and correct the reference, or add a "
        "`derive-ok` comment to the edit if the path is intentionally new."
    )
    json.dump({"decision": "block", "reason": reason}, sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
