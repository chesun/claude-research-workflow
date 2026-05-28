#!/usr/bin/env python3
"""
Derive-Don't-Guess advisory PostToolUse hook.

Fires after Edit/Write/MultiEdit to an analysis/paper file (.do/.doh/.R/.py/.tex)
and injects a NON-BLOCKING advisory when the edit introduces a read/input path
that does not resolve on disk (or a Stata macro defined nowhere in the repo) —
the strongest mechanically-detectable signal of a guessed (vs derived) entity.

This is the on-by-default enforcement for `.claude/rules/derive-dont-guess.md`.
It fires in the ad-hoc path (a plain "write me this .do file") where the
critic-based enforcement never runs. Advisory only — it never blocks; it
injects via hookSpecificOutput.additionalContext so the reminder reaches the
model's next turn. Per-session dedup avoids re-warning on the same path.

Shared logic in `.claude/hooks/derive_lib.py`.

Install (in .claude/settings.json, PostToolUse, matcher "Write|Edit|MultiEdit"):
    python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/derive-check-advisory.py

Fail-open on any internal exception (exit 0, no output).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path


def _load_lib():
    lib_path = Path(__file__).resolve().parent / "derive_lib.py"
    spec = importlib.util.spec_from_file_location("derive_lib", lib_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {lib_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _session_cache_path(project_dir: str) -> Path:
    project_hash = hashlib.md5(project_dir.encode()).hexdigest()[:8]
    d = Path.home() / ".claude" / "sessions" / project_hash
    d.mkdir(parents=True, exist_ok=True)
    return d / "derive-advisory-cache.json"


def _filter_already_warned(cache_file: Path, file_path: str, unresolved: list) -> list:
    """Drop (file,path) pairs warned within the last 5 minutes; record the rest."""
    now = time.time()
    try:
        cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
    except (json.JSONDecodeError, OSError):
        cache = {}
    # Prune entries older than 5 minutes.
    cache = {k: v for k, v in cache.items() if now - v < 300}

    fresh = []
    for path, reason in unresolved:
        key = f"{file_path}::{path}"
        if now - cache.get(key, 0) >= 60:
            fresh.append((path, reason))
        cache[key] = now

    try:
        cache_file.write_text(json.dumps(cache))
    except OSError:
        pass
    return fresh


def _emit(additional_context: str) -> None:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": additional_context,
        },
        "suppressOutput": True,
    }
    sys.stdout.write(json.dumps(payload))
    sys.stdout.flush()


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
    if not file_path:
        sys.exit(0)

    if lib.language_for_path(file_path) is None:
        sys.exit(0)

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", hook_input.get("cwd", ""))
    if not project_dir:
        sys.exit(0)
    project_root = Path(project_dir)

    unresolved = lib.analyze(tool_name, tool_input, file_path, project_root)
    if not unresolved:
        sys.exit(0)

    # Display the file path relative to the project when possible.
    try:
        rel = str(Path(file_path).resolve().relative_to(project_root.resolve()))
    except (ValueError, OSError):
        rel = file_path

    cache_file = _session_cache_path(project_dir)
    fresh = _filter_already_warned(cache_file, rel, unresolved)
    if not fresh:
        sys.exit(0)

    _emit(lib.build_advisory_message(rel, fresh))
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
