#!/usr/bin/env python3
"""
Post-Rewrite-Verify — PostToolUse Bash hook.

Soft-injects a verification reminder into the next agent turn after any
git history-rewrite command runs. Catches the false-success-narration
failure mode that was the *actual* root cause of the 2026-04-25 incident:
the session ran filter-repo, claimed "working tree unchanged" without
verification, and the deletion only surfaced 8 days later when a coauthor
noticed missing files.

Triggers on the same always-blocked patterns as destructive-action-guard
(filter-repo, filter-branch, force push, non-resumption rebase, reset --hard,
clean -f...). When any of these run successfully (and weren't blocked),
inject a reminder demanding `ls -la` + `du -sh` verification before
narrating success.

Hook fires on subagent Bash too — same coverage as the PreToolUse guard.

Install (in .claude/settings.json, PostToolUse with matcher "Bash"):
    python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/post-rewrite-verify.py

Output format: writes JSON to stdout per Claude Code hook spec
(hookSpecificOutput.additionalContext) so the reminder is wrapped in a
system-reminder and inserted into the next agent turn. Exit 0 always —
this hook never blocks.

Fail-open silently on any internal exception.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path


def _load_guard():
    """Reuse the always-blocked-class detectors from the PreToolUse guard."""
    p = Path(__file__).resolve().parent / "destructive-action-guard.py"
    spec = importlib.util.spec_from_file_location("guard", p)
    if spec is None or spec.loader is None:
        return None
    m = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)
    except Exception:
        return None
    return m


REMINDER = """HISTORY-REWRITE VERIFICATION REQUIRED.

You ran `{command}`. Before claiming the working tree is unchanged or the
operation succeeded as intended, run BOTH:

  1. ls -la <affected paths>      (compare to expected file list)
  2. du -sh <repo root>           (compare to pre-rewrite size)

The 2026-04-25 incident: a session ran `git filter-repo --invert-paths`,
claimed "Working tree = 8.8 GB unchanged (all .dta files still present)"
without verification. The deletion only surfaced 8 days later when a
coauthor noticed missing analysis output.

Adversarial-default rule applies (.claude/rules/adversarial-default.md):
compliance is a positive claim that requires positive evidence. Without
ls/du output captured in your response, you have not verified — do not
narrate success."""


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
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    if hook_input.get("tool_name") != "Bash":
        sys.exit(0)

    tool_input = hook_input.get("tool_input", {}) or {}
    command = tool_input.get("command", "") or ""
    cwd = hook_input.get("cwd", "") or os.getcwd()

    guard = _load_guard()
    if guard is None:
        sys.exit(0)

    # Tokenize same way as the guard so detection matches exactly.
    try:
        import shlex
        tokens_all = shlex.split(command, posix=True, comments=True)
    except ValueError:
        sys.exit(0)
    if not tokens_all:
        sys.exit(0)

    tokens, _ = guard._strip_env_assignments(tokens_all)
    tokens, _ = guard._consume_cd_chain(tokens, cwd)
    if not tokens:
        sys.exit(0)

    # Only a subset of always-blocked is interesting for verification.
    # Force push, reset --hard, clean -f don't typically need ls/du
    # verification — they're already caught and the user re-authorized.
    # The dangerous-narration mode hits specifically on history rewrites
    # that reach into the working tree (filter-repo, filter-branch,
    # rebase). Inject the reminder for those.
    rewrite_predicates = [
        guard._is_filter_repo,
        guard._is_filter_branch,
        guard._is_rebase_nontrivial,
    ]
    if not any(p(tokens) for p in rewrite_predicates):
        sys.exit(0)

    try:
        _emit(REMINDER.format(command=command))
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
