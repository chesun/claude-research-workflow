#!/usr/bin/env python3
"""Tests for destructive-action-guard.py.

Run with: python3 .claude/hooks/test_destructive_action_guard.py

Covers the 20 test cases enumerated in
quality_reports/plans/2026-05-03_destructive-action-guardrails.md.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile
from pathlib import Path


def _load_hook():
    p = Path(__file__).resolve().parent / "destructive-action-guard.py"
    spec = importlib.util.spec_from_file_location("guard", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


hook = _load_hook()


# --- Test infrastructure ---------------------------------------------------

# Build a fake shared-storage dir under tempdir, plus a symlink that points
# into it from a non-shared location. We monkey-patch _shared_prefixes() to
# include our tempdir so we can test path-resolution without needing a real
# Dropbox install.
_TMP = Path(tempfile.mkdtemp(prefix="dag_test_"))
_FAKE_DROPBOX = _TMP / "fake_dropbox"
_FAKE_DROPBOX.mkdir()
(_FAKE_DROPBOX / "repo").mkdir()
_NONSHARED = _TMP / "scratch"
_NONSHARED.mkdir()
_SYMLINK_INTO_SHARED = _TMP / "linked_to_dropbox"
os.symlink(_FAKE_DROPBOX, _SYMLINK_INTO_SHARED)

_orig_prefixes = hook._shared_prefixes
hook._shared_prefixes = lambda: [str(_FAKE_DROPBOX)]


def _cleanup():
    hook._shared_prefixes = _orig_prefixes
    shutil.rmtree(_TMP, ignore_errors=True)


# --- Test helpers ----------------------------------------------------------

PASS = 0
FAIL = 0


def assert_block(command: str, cwd: str, label: str, expect_substr: str | None = None) -> None:
    global PASS, FAIL
    msg, debug = hook.check_command(command, cwd)
    if msg is None:
        print(f"FAIL: {label}")
        print(f"  command:  {command!r}")
        print(f"  cwd:      {cwd}")
        print(f"  expected: BLOCK, got: ALLOW")
        FAIL += 1
        return
    if expect_substr and expect_substr not in msg:
        print(f"FAIL: {label}")
        print(f"  expected substring: {expect_substr!r}")
        print(f"  in block message:   {msg[:200]!r}...")
        FAIL += 1
        return
    print(f"PASS: {label}")
    PASS += 1


def assert_allow(command: str, cwd: str, label: str) -> None:
    global PASS, FAIL
    msg, debug = hook.check_command(command, cwd)
    if msg is not None:
        print(f"FAIL: {label}")
        print(f"  command:  {command!r}")
        print(f"  cwd:      {cwd}")
        print(f"  expected: ALLOW, got BLOCK:")
        print(f"  {msg.splitlines()[0] if msg else ''}")
        FAIL += 1
        return
    print(f"PASS: {label}")
    PASS += 1


# --- Always-blocked class --------------------------------------------------

print("=== Always-blocked: history rewrites (any cwd) ===")

# 1. filter-repo on /tmp/foo -> BLOCK
assert_block(
    "git filter-repo --invert-paths --path output/",
    "/tmp/foo",
    "filter-repo on non-shared path still blocks",
    expect_substr="history rewrite",
)

# 2. filter-repo in fake shared -> BLOCK
assert_block(
    "git filter-repo --invert-paths --path output/",
    str(_FAKE_DROPBOX / "repo"),
    "filter-repo in shared path blocks",
)

# 3. BYPASS env var allows filter-repo
assert_allow(
    "BYPASS_SHARED_GUARD=1 git filter-repo --invert-paths --path output/",
    str(_FAKE_DROPBOX / "repo"),
    "BYPASS_SHARED_GUARD=1 allows filter-repo",
)

# 4. force-push -> BLOCK
assert_block(
    "git push --force origin main",
    str(_FAKE_DROPBOX / "repo"),
    "git push --force blocks",
    expect_substr="force push",
)

# 5. -f short form -> BLOCK
assert_block(
    "git push -f origin main",
    "/tmp/foo",
    "git push -f short form blocks",
)

# 6. plain push -> ALLOW
assert_allow(
    "git push origin main",
    str(_FAKE_DROPBOX / "repo"),
    "plain git push allows even in shared cwd",
)

# 7. refspec force (+main:main) -> BLOCK
assert_block(
    "git push origin +main:main",
    "/tmp/foo",
    "git push +refspec (force form) blocks",
)

# 8. interactive rebase -> BLOCK
assert_block(
    "git rebase -i HEAD~3",
    "/tmp/foo",
    "git rebase -i HEAD~3 blocks (history rewrite)",
)

# 9. rebase --continue -> ALLOW
assert_allow(
    "git rebase --continue",
    "/tmp/foo",
    "git rebase --continue allows (resumption)",
)

# 9b. rebase --abort -> ALLOW
assert_allow(
    "git rebase --abort",
    "/tmp/foo",
    "git rebase --abort allows (resumption)",
)

# 10. reset --hard -> BLOCK
assert_block(
    "git reset --hard HEAD~1",
    "/tmp/foo",
    "git reset --hard blocks",
)

# 11. reset --soft -> ALLOW
assert_allow(
    "git reset --soft HEAD~1",
    "/tmp/foo",
    "git reset --soft allows",
)

# 12. clean -fd -> BLOCK
assert_block(
    "git clean -fd",
    "/tmp/foo",
    "git clean -fd blocks",
)

# 12b. clean -fdx -> BLOCK
assert_block(
    "git clean -fdx",
    "/tmp/foo",
    "git clean -fdx blocks",
)

# 13. clean -n (dry run) -> ALLOW
assert_allow(
    "git clean -n",
    "/tmp/foo",
    "git clean -n (dry run) allows",
)

# 13b. clean --dry-run -> ALLOW
assert_allow(
    "git clean --dry-run",
    "/tmp/foo",
    "git clean --dry-run allows",
)

# update-ref -d
assert_block(
    "git update-ref -d refs/heads/old",
    "/tmp/foo",
    "git update-ref -d blocks",
    expect_substr="ref deletion",
)


# --- Path-conditional class ------------------------------------------------

print("\n=== Path-conditional: rm -rf / find -delete ===")

# 14. rm -rf foo/ in /tmp/scratch -> ALLOW (not shared)
assert_allow(
    "rm -rf foo/",
    str(_NONSHARED),
    "rm -rf in non-shared cwd allows",
)

# 15. rm -rf foo/ where foo is in fake shared -> BLOCK
assert_block(
    "rm -rf foo/",
    str(_FAKE_DROPBOX / "repo"),
    "rm -rf foo/ in shared cwd blocks (relative path resolves to shared)",
    expect_substr="shared-storage",
)

# 16. cd <symlink-into-dropbox> && rm -rf bar -> BLOCK (realpath through symlink)
# Use the full command with cd-chain; effective cwd resolved through symlink.
assert_block(
    f"cd {_SYMLINK_INTO_SHARED} && rm -rf bar",
    str(_TMP),  # initial cwd is the tempdir, not the symlink
    "cd symlink-into-shared && rm -rf bar blocks (realpath resolution)",
)

# 17. find <shared-path> -delete -> BLOCK
assert_block(
    f"find {_FAKE_DROPBOX}/repo -name '*.tmp' -delete",
    "/tmp/foo",
    "find <shared> -delete blocks",
)

# 18. find <non-shared> -delete -> ALLOW
assert_allow(
    f"find {_NONSHARED} -delete",
    "/tmp/foo",
    "find <non-shared> -delete allows",
)

# 19. rm -rf in /tmp/dropbox-clone (substring "dropbox" but NOT canonical mount) -> ALLOW
fake_lookalike = _TMP / "dropbox-clone"
fake_lookalike.mkdir()
assert_allow(
    "rm -rf foo/",
    str(fake_lookalike),
    "substring 'dropbox' in path but not canonical mount allows",
)

# 20. rm without -r/-f (single file) -> ALLOW
assert_allow(
    "rm file.txt",
    str(_FAKE_DROPBOX / "repo"),
    "rm without -r flag allows (not catastrophic enough to gate)",
)


# --- Additional regression cases ------------------------------------------

print("\n=== Regression guards ===")

# Subagent semantics: hook design is agent-agnostic, so same input from a
# subagent should produce the same decision. Confirm we're not gating on
# any agent-id field.
assert_block(
    "git filter-repo --invert-paths --path foo/",
    "/tmp/foo",
    "agent-agnostic: same input blocks regardless of caller (no agent_id check)",
)

# Empty command -> ALLOW
assert_allow("", "/tmp/foo", "empty command allows")

# Whitespace-only command -> ALLOW
assert_allow("   ", "/tmp/foo", "whitespace-only command allows")

# Bypass works for path-conditional class too
assert_allow(
    "BYPASS_SHARED_GUARD=1 rm -rf foo/",
    str(_FAKE_DROPBOX / "repo"),
    "BYPASS_SHARED_GUARD=1 allows rm -rf in shared cwd",
)

# Multiple env-var assignments before command — bypass still detected
assert_allow(
    "BYPASS_SHARED_GUARD=1 DEBUG=1 git filter-repo --invert-paths",
    "/tmp/foo",
    "bypass works alongside other env-var assignments",
)

# Force-with-lease
assert_block(
    "git push --force-with-lease origin main",
    "/tmp/foo",
    "git push --force-with-lease blocks",
)

# Force-with-lease with =refspec form
assert_block(
    "git push --force-with-lease=main:abc123 origin main",
    "/tmp/foo",
    "git push --force-with-lease=<refspec> blocks",
)

# Realistic safe operations
assert_allow("ls -la", str(_FAKE_DROPBOX / "repo"), "ls allows in shared cwd")
assert_allow("git status", str(_FAKE_DROPBOX / "repo"), "git status allows in shared cwd")
assert_allow("git commit -m 'test'", str(_FAKE_DROPBOX / "repo"), "git commit allows in shared cwd")
assert_allow("git pull --rebase", str(_FAKE_DROPBOX / "repo"), "git pull --rebase allows (rebase from pull, not direct)")
# NOTE: `git pull --rebase` does invoke git rebase under the hood; but the
# command string is `git pull`, not `git rebase`. The hook matches on the
# user-typed command, not transitive operations. Documented limitation.

# Plain `mv` is not gated (covered by spec deviation note in plan)
assert_allow(f"mv {_FAKE_DROPBOX}/repo/foo {_FAKE_DROPBOX}/repo/bar",
             str(_FAKE_DROPBOX / "repo"),
             "mv within shared (rename) allows — not gated in v1")

# rm -i (interactive) without -r -> ALLOW (not destructive enough)
assert_allow("rm -i foo.txt", str(_FAKE_DROPBOX / "repo"), "rm -i allows (no recursive flag)")


# --- Summary ---------------------------------------------------------------

print(f"\n=== Summary: {PASS} passed, {FAIL} failed ===")
_cleanup()
sys.exit(0 if FAIL == 0 else 1)
