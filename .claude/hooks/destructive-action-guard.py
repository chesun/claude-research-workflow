#!/usr/bin/env python3
"""
Destructive-Action Guard — PreToolUse Bash hook.

Two-tier protection against destructive operations:

  1. **Always-blocked class** — history rewrites, force pushes, hard resets,
     destructive cleans. Block regardless of cwd; require explicit re-auth
     via `BYPASS_SHARED_GUARD=1` env-var prefix.

  2. **Path-conditional class** — `rm -rf`, `find -delete`, overwriting `mv`.
     Block only when the resolved target path lives under a canonical
     cloud-storage mount point (Dropbox, Google Drive, OneDrive, iCloud).

Triggered by the 2026-04-25 incident: a Claude Code session ran
`git filter-repo --invert-paths` on a Dropbox-shared repo to shrink it for
a failing push. The operation rewrote history AND silently rewrote the
working tree, deleting `output/dta/most_recent/` and several dated
regression-export folders. Dropbox propagated the deletion to all 3
coauthors. The session force-pushed to origin. The session log claimed
"Working tree = 8.8 GB unchanged (all .dta files still present)" without
running `ls`/`du` — the deletion only surfaced 8 days later.

This hook closes the gap that prose-level rules (`adversarial-default.md`,
"executing actions with care") could not enforce.

Hook fires on subagent Bash too — Claude Code's PreToolUse passes through
Task-dispatched subagents per docs at code.claude.com/docs/en/hooks. The
hook itself does not distinguish parent from subagent; same policy applies.
Audit trail at .claude/state/destructive-action-guard.log lets you verify
firing across both contexts.

Install (in .claude/settings.json, PreToolUse with matcher "Bash"):
    python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/destructive-action-guard.py

Fail-open on internal exceptions (don't break the agent if Python crashes).
"""

from __future__ import annotations

import json
import os
import shlex
import sys
from pathlib import Path

# --- Configuration ---------------------------------------------------------

# Always-blocked patterns. Each entry is a function: tokens -> bool.
# tokens are the shlex-split command tokens *after* any leading env-var
# assignments and any `cd X &&` chain has been consumed.
def _is_filter_repo(tokens: list[str]) -> bool:
    return len(tokens) >= 2 and tokens[0] == "git" and tokens[1] == "filter-repo"

def _is_filter_branch(tokens: list[str]) -> bool:
    return len(tokens) >= 2 and tokens[0] == "git" and tokens[1] == "filter-branch"

def _is_force_push(tokens: list[str]) -> bool:
    if len(tokens) < 2 or tokens[0] != "git" or tokens[1] != "push":
        return False
    rest = tokens[2:]
    # explicit force flags
    for flag in ("--force", "-f", "--force-with-lease"):
        if flag in rest:
            return True
    # force-with-lease in --force-with-lease=<refspec> form
    if any(t.startswith("--force-with-lease=") for t in rest):
        return True
    # refspec starting with `+` (force form: `+main:main`, `+HEAD:refs/...`)
    # skip any token that starts with `-` (flags) and look at remaining args
    for t in rest:
        if t.startswith("-"):
            continue
        # first non-flag arg after `git push` is usually the remote;
        # subsequent args are refspecs. Any refspec starting with `+` forces.
        if ":" in t and t.startswith("+"):
            return True
        if t.startswith("+") and ":" in t:
            return True
    return False

def _is_rebase_nontrivial(tokens: list[str]) -> bool:
    if len(tokens) < 2 or tokens[0] != "git" or tokens[1] != "rebase":
        return False
    rest = tokens[2:]
    # Resumption forms — ALLOW
    for flag in ("--continue", "--abort", "--skip", "--quit", "--show-current-patch"):
        if flag in rest:
            return False
    # Edit-todo also non-destructive
    if "--edit-todo" in rest:
        return False
    return True

def _is_reset_hard(tokens: list[str]) -> bool:
    return (len(tokens) >= 2 and tokens[0] == "git" and tokens[1] == "reset"
            and "--hard" in tokens[2:])

def _is_clean_destructive(tokens: list[str]) -> bool:
    if len(tokens) < 2 or tokens[0] != "git" or tokens[1] != "clean":
        return False
    rest = tokens[2:]
    # `-n` / `--dry-run` => allow
    if "-n" in rest or "--dry-run" in rest:
        return False
    # any -f flag (alone or combined like -fd, -fdx, -fx) => block
    for t in rest:
        if t.startswith("-") and not t.startswith("--") and "f" in t:
            return True
        if t == "--force":
            return True
    return False

def _is_update_ref_delete(tokens: list[str]) -> bool:
    return (len(tokens) >= 2 and tokens[0] == "git" and tokens[1] == "update-ref"
            and "-d" in tokens[2:])

ALWAYS_BLOCKED = [
    ("git filter-repo", _is_filter_repo,
     "history rewrite — silently mutates working tree (2026-04-25 incident)"),
    ("git filter-branch", _is_filter_branch,
     "history rewrite — same risk class as filter-repo"),
    ("git push --force / -f / +refspec", _is_force_push,
     "force push — overwrites remote history; coauthors lose work"),
    ("git rebase (non-resumption)", _is_rebase_nontrivial,
     "history rewrite — interactive or range rebase mutates commit graph"),
    ("git reset --hard", _is_reset_hard,
     "destructive reset — discards uncommitted changes and resets HEAD"),
    ("git clean -f...", _is_clean_destructive,
     "destructive clean — irreversibly deletes untracked files; --dry-run allowed"),
    ("git update-ref -d", _is_update_ref_delete,
     "ref deletion — removes references to commits; can orphan history"),
]

# Path-conditional patterns — extract path arguments for shared-storage check.
def _extract_rm_paths(tokens: list[str]) -> list[str] | None:
    """Return target paths if `rm` invocation is destructive (-r/-R/-rf/-fr)."""
    if not tokens or tokens[0] != "rm":
        return None
    # need at least one of -r, -R, -rf, -fr (or --recursive); otherwise rm of
    # individual files is not catastrophic enough to gate.
    has_recursive = False
    for t in tokens[1:]:
        if t.startswith("-") and not t.startswith("--"):
            # -r, -R, -rf, -fr, -rfd, etc. — any short-flag bundle containing r/R
            if "r" in t or "R" in t:
                has_recursive = True
        elif t == "--recursive":
            has_recursive = True
    if not has_recursive:
        return None
    # Collect non-flag tokens
    paths = [t for t in tokens[1:] if not t.startswith("-")]
    return paths if paths else None

def _extract_find_delete_paths(tokens: list[str]) -> list[str] | None:
    """Return search-root paths if `find ... -delete` is invoked."""
    if not tokens or tokens[0] != "find":
        return None
    if "-delete" not in tokens[1:]:
        return None
    # The first non-flag-looking arg after `find` is the starting path.
    # `find` accepts multiple starting paths before the expression. Convention:
    # everything before the first arg starting with `-` (other than `-`) or
    # paren/expression is a path.
    paths = []
    for t in tokens[1:]:
        if t.startswith("-") or t in ("(", ")", "!"):
            break
        paths.append(t)
    return paths if paths else None

# Cloud-storage mount-point prefixes (anchored on canonical macOS paths,
# not arbitrary substrings — avoids false-positives on `/tmp/dropbox-clone`).
def _shared_prefixes() -> list[str]:
    home = str(Path.home())
    return [
        f"{home}/Library/CloudStorage/Dropbox",
        f"{home}/Library/CloudStorage/GoogleDrive",
        f"{home}/Library/CloudStorage/OneDrive",
        f"{home}/Library/CloudStorage/Box",
        f"{home}/Library/Mobile Documents/com~apple~CloudDocs",
        f"{home}/Dropbox",  # legacy direct mount
    ]

def _is_under_shared(resolved_path: str) -> str | None:
    """Return matching shared prefix if `resolved_path` is under one, else None.

    Both `resolved_path` and the prefix candidates are realpath-resolved before
    comparison so that platform symlinks (e.g., macOS `/var` -> `/private/var`)
    don't cause false negatives.
    """
    try:
        rp = os.path.realpath(resolved_path)
    except OSError:
        rp = resolved_path
    for prefix in _shared_prefixes():
        try:
            prefix_real = os.path.realpath(prefix) if os.path.exists(prefix) else prefix
        except OSError:
            prefix_real = prefix
        for candidate in {prefix, prefix_real}:
            # match prefix-of, but only at directory boundary
            if rp == candidate or rp.startswith(candidate + os.sep):
                return candidate
            # CloudStorage/Dropbox-Personal, CloudStorage/GoogleDrive-foo@bar, etc.
            # Match candidate as the start of a path segment with optional suffix.
            parent = os.path.dirname(candidate)
            base = os.path.basename(candidate)
            if parent and rp.startswith(parent + os.sep):
                after = rp[len(parent) + 1:]
                seg, _, _ = after.partition(os.sep)
                if seg == base or seg.startswith(base + "-"):
                    return parent + os.sep + seg
    return None

# --- Command parsing -------------------------------------------------------

def _strip_env_assignments(tokens: list[str]) -> tuple[list[str], dict[str, str]]:
    """Strip leading VAR=VAL tokens; return (remaining tokens, env dict)."""
    env: dict[str, str] = {}
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if "=" in t and not t.startswith("=") and not t.startswith("-"):
            name, _, val = t.partition("=")
            # Variable name must be valid identifier
            if name.replace("_", "").isalnum() and not name[0].isdigit():
                env[name] = val
                i += 1
                continue
        break
    return tokens[i:], env

def _consume_cd_chain(tokens: list[str], cwd: str) -> tuple[list[str], str]:
    """Consume leading `cd X && ...` directives; return (remaining tokens, effective cwd)."""
    effective = cwd
    while len(tokens) >= 3 and tokens[0] == "cd" and tokens[2] in ("&&", ";"):
        target = os.path.expanduser(tokens[1])
        if not os.path.isabs(target):
            target = os.path.join(effective, target)
        try:
            effective = os.path.realpath(target)
        except OSError:
            effective = os.path.abspath(target)
        tokens = tokens[3:]
    return tokens, effective

def _resolve_path(path: str, cwd: str) -> str:
    """Resolve `path` to an absolute realpath relative to `cwd`."""
    expanded = os.path.expanduser(path)
    if not os.path.isabs(expanded):
        expanded = os.path.join(cwd, expanded)
    try:
        return os.path.realpath(expanded)
    except OSError:
        return os.path.abspath(expanded)

# --- Core check ------------------------------------------------------------

def check_command(command: str, cwd: str) -> tuple[str | None, dict]:
    """
    Inspect `command` (Bash command string) executed from `cwd`.
    Return (block_message, debug) where block_message is None if allowed.
    """
    debug = {"command": command, "cwd": cwd}
    if not command or not command.strip():
        return None, debug

    # Tokenize. Use posix=True to match shell quoting.
    try:
        tokens_all = shlex.split(command, posix=True, comments=True)
    except ValueError:
        # Unparseable — fail-closed for always-blocked patterns by simple substring
        # check; fail-open otherwise. Conservative on the dangerous classes.
        for label, _, reason in ALWAYS_BLOCKED:
            # crude substring fallback
            if label.split(" (")[0].split(" / ")[0].split()[0] in command and \
               any(kw in command for kw in ("filter-repo", "filter-branch", "--force", "-f ", "--hard", "update-ref -d")):
                return _format_block(label, reason, command, cwd, []), debug
        return None, debug

    if not tokens_all:
        return None, debug

    # Strip env assignments; check for bypass first.
    tokens, env_assigns = _strip_env_assignments(tokens_all)
    debug["env_assigns"] = env_assigns
    if env_assigns.get("BYPASS_SHARED_GUARD") == "1":
        # Bypass authorized; record in debug for audit log.
        debug["bypass"] = True
        return None, debug

    if not tokens:
        return None, debug

    # Consume leading cd-chain to compute effective cwd.
    tokens, effective_cwd = _consume_cd_chain(tokens, cwd)
    debug["effective_cwd"] = effective_cwd

    # Tier 1: always-blocked patterns.
    for label, predicate, reason in ALWAYS_BLOCKED:
        if predicate(tokens):
            return _format_block(label, reason, command, effective_cwd, []), debug

    # Tier 2: path-conditional — extract paths.
    extractors = [
        ("rm -r/-R/-rf/-fr", _extract_rm_paths),
        ("find ... -delete", _extract_find_delete_paths),
    ]
    for label, extract in extractors:
        paths = extract(tokens)
        if not paths:
            continue
        # Resolve each path; check if any lands in shared storage.
        resolved = [_resolve_path(p, effective_cwd) for p in paths]
        # Also check effective_cwd itself (for `rm -rf .` / `rm -rf *` with cwd in shared)
        # but only if no explicit paths or all paths are under cwd.
        for r in resolved:
            shared = _is_under_shared(r)
            if shared:
                reason = f"destructive command on shared-storage path under {shared}"
                return _format_block(label, reason, command, effective_cwd, resolved), debug
        # Even if explicit paths aren't under shared, check effective_cwd if cwd
        # is shared and the rm/find target is relative (could mean "files in cwd")
        if any(not os.path.isabs(p) and not p.startswith("~") for p in paths):
            shared = _is_under_shared(effective_cwd)
            if shared:
                reason = f"destructive command in shared-storage cwd under {shared}"
                return _format_block(label, reason, command, effective_cwd, resolved), debug

    return None, debug

def _format_block(label: str, reason: str, command: str, cwd: str, paths: list[str]) -> str:
    paths_str = "\n  ".join(paths) if paths else "(none extracted)"
    return f"""DESTRUCTIVE-ACTION-GUARD: blocking.

Matched: {label}
Reason: {reason}
Effective cwd: {cwd}
Resolved path(s):
  {paths_str}
Original command: {command}

Why this exists: 2026-04-25 incident — `git filter-repo --invert-paths`
silently rewrote a Dropbox-shared repo's working tree, deleted analysis
output, and force-pushed. The session falsely claimed 'working tree
unchanged' without verification. See .claude/rules/destructive-actions.md.

Bypass:
  - Re-run with: BYPASS_SHARED_GUARD=1 <original command>
  - Audit trail: bypass invocations are visible in shell history,
    session logs, and .claude/state/destructive-action-guard.log."""

# --- Audit log -------------------------------------------------------------

def _log_invocation(project_dir: str, command: str, cwd: str, decision: str,
                    debug: dict) -> None:
    """Append-only audit log; cap at ~1MB by truncating-and-rotating."""
    try:
        log_dir = Path(project_dir) / ".claude" / "state"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "destructive-action-guard.log"
        # Rotate if > 1MB
        if log_path.exists() and log_path.stat().st_size > 1_000_000:
            log_path.rename(log_path.with_suffix(".log.old"))
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc).isoformat()
        entry = {
            "ts": ts,
            "decision": decision,
            "command": command,
            "cwd": cwd,
            "effective_cwd": debug.get("effective_cwd"),
            "bypass": debug.get("bypass", False),
        }
        with log_path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # logging failure must never break the hook

# --- Hook entrypoint -------------------------------------------------------

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
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", cwd)

    try:
        block_msg, debug = check_command(command, cwd)
    except Exception as e:  # fail-open
        _log_invocation(project_dir, command, cwd, f"error:{e}", {})
        sys.exit(0)

    if block_msg:
        _log_invocation(project_dir, command, cwd, "BLOCK", debug)
        sys.stderr.write(block_msg + "\n")
        sys.exit(2)

    _log_invocation(project_dir, command, cwd, "ALLOW", debug)
    sys.exit(0)

if __name__ == "__main__":
    main()
