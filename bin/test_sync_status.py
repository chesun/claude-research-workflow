#!/usr/bin/env python3
"""Tests for bin/sync_status.py (run: py -I bin/test_sync_status.py).

Plain check() style, as in bin/test_blueprint_check.py. Each case builds a scratch git repo in a temp
directory. Nothing is pushed: the upstream is a remote-tracking ref set with `git update-ref`.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

PASSES = 0
FAILS: list[str] = []
HERE = Path(__file__).resolve().parent


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASSES
    if ok:
        PASSES += 1
        print(f"  PASS  {name}")
    else:
        FAILS.append(name)
        print(f"  FAIL  {name}  {detail[:300]}")


def load():
    spec = importlib.util.spec_from_file_location("sync_status", HERE / "sync_status.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def g(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return r.stdout


def mkrepo(tmp: Path, name: str) -> Path:
    repo = tmp / name
    repo.mkdir()
    g(repo, "init", "-q", "-b", "main")
    g(repo, "config", "user.email", "sentinel@example.com")
    g(repo, "config", "user.name", "Sentinel")
    g(repo, "config", "core.autocrlf", "false")
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    g(repo, "add", "a.txt")
    g(repo, "commit", "-q", "-m", "a")
    return repo


def set_upstream_here(repo: Path) -> None:
    """Pretend the current commit is what origin/main has, without pushing anything."""
    g(repo, "config", "remote.origin.url", "https://example.invalid/sentinel.git")
    g(repo, "config", "remote.origin.fetch", "+refs/heads/*:refs/remotes/origin/*")
    g(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    g(repo, "config", "branch.main.remote", "origin")
    g(repo, "config", "branch.main.merge", "refs/heads/main")


def commit_file(repo: Path, name: str, data: bytes, msg: str) -> None:
    (repo / name).write_bytes(data)
    g(repo, "add", name)
    g(repo, "commit", "-q", "-m", msg)


def no_tool(_name: str):
    return None


def test_sync_status(tmp: Path) -> None:
    empty_hooks = tmp / "hooks-empty"
    empty_hooks.mkdir()
    lfs_hooks = tmp / "hooks-lfs"
    lfs_hooks.mkdir()
    (lfs_hooks / "pre-push").write_text('#!/bin/sh\ngit lfs pre-push "$@"\n', encoding="utf-8")

    repo = mkrepo(tmp, "clean")
    set_upstream_here(repo)
    verdict, lines, actions = ss.build_report(repo, which=no_tool, hooks_dir=lfs_hooks, home=tmp)
    check("ss_clean_repo_in_sync", verdict == "PASS" and actions == [], f"{verdict} {actions}")
    check("ss_clean_repo_main_exit_0", ss.main([str(repo), "--hooks-dir", str(lfs_hooks)]) == 0)

    repo = mkrepo(tmp, "ahead")
    set_upstream_here(repo)
    commit_file(repo, "b.txt", b"b\n", "b")
    verdict, lines, actions = ss.build_report(repo, which=no_tool, hooks_dir=lfs_hooks, home=tmp)
    check("ss_ahead_flags_push", verdict == "FAIL" and any("git push" in a and "1 commit" in a for a in actions),
          f"{verdict} {actions}")

    repo = mkrepo(tmp, "noupstream")
    verdict, lines, actions = ss.build_report(repo, which=no_tool, hooks_dir=lfs_hooks, home=tmp)
    check("ss_no_remote_unverified", verdict == "UNVERIFIED" and any("no remote" in ln for ln in lines),
          f"{verdict} {lines} {actions}")
    g(repo, "config", "remote.origin.url", "https://example.invalid/sentinel.git")
    g(repo, "config", "remote.origin.fetch", "+refs/heads/*:refs/remotes/origin/*")
    verdict, lines, actions = ss.build_report(repo, which=no_tool, hooks_dir=lfs_hooks, home=tmp)
    check("ss_remote_without_upstream_publish", verdict == "FAIL"
          and any("git push -u origin main" in a for a in actions), f"{verdict} {actions}")
    g(repo, "config", "branch.main.remote", "origin")
    g(repo, "config", "branch.main.merge", "refs/heads/main")
    verdict, lines, actions = ss.build_report(repo, which=no_tool, hooks_dir=lfs_hooks, home=tmp)
    check("ss_upstream_never_fetched_not_clean", verdict != "PASS", f"{verdict} {actions}")
    g(repo, "checkout", "-q", "--detach")
    verdict, lines, actions = ss.build_report(repo, which=no_tool, hooks_dir=lfs_hooks, home=tmp)
    check("ss_detached_head_not_clean", verdict != "PASS" and any("detached" in ln.lower() for ln in lines + actions),
          f"{verdict} {lines} {actions}")

    repo = mkrepo(tmp, "behind")
    set_upstream_here(repo)
    commit_file(repo, "b.txt", b"b\n", "b")
    g(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    g(repo, "reset", "-q", "--soft", "HEAD~1")
    g(repo, "stash", "-q")
    verdict, lines, actions = ss.build_report(repo, which=no_tool, hooks_dir=lfs_hooks, home=tmp)
    check("ss_behind_flags_pull", verdict == "FAIL" and any("git pull" in a for a in actions), f"{verdict} {actions}")
    check("ss_fail_main_exit_1", ss.main([str(repo), "--hooks-dir", str(lfs_hooks)], which=no_tool) == 1)

    repo = mkrepo(tmp, "nestedattr")
    (repo / "data").mkdir()
    commit_file(repo, "data/raw.csv", b"a,b\n1,2\n", "csv as a plain blob")
    commit_file(repo, "data/.gitattributes", b"*.csv filter=lfs diff=lfs merge=lfs -text\n", "nested lfs rule")
    set_upstream_here(repo)
    verdict, lines, actions = ss.build_report(repo, which=no_tool, hooks_dir=lfs_hooks, home=tmp)
    check("ss_nested_gitattributes_seen", verdict == "FAIL"
          and any("renormalize" in a and "data/raw.csv" in a for a in actions), f"{verdict} {actions}")

    comment_hooks = tmp / "hooks-comment"
    comment_hooks.mkdir()
    (comment_hooks / "pre-push").write_text("#!/bin/sh\n# note: this guard does NOT call git lfs pre-push\n"
                                            "exec python guard.py \"$@\"\n", encoding="utf-8")
    check("ss_hook_comment_not_counted", not ss.lfs_hook_runs(comment_hooks) and ss.lfs_hook_runs(lfs_hooks))

    repo = mkrepo(tmp, "nolfscli")
    commit_file(repo, ".gitattributes", b"*.bin filter=lfs diff=lfs merge=lfs -text\n", "route bin to lfs")
    set_upstream_here(repo)
    verdict, lines, actions = ss.build_report(repo, which=no_tool, hooks_dir=lfs_hooks, home=tmp,
                                              lfs_available=False)
    check("ss_lfs_cli_missing_unverified", verdict == "UNVERIFIED" and any("git-lfs" in ln for ln in lines),
          f"{verdict} {lines}")

    repo = mkrepo(tmp, "backup")
    set_upstream_here(repo)
    bdir = tmp / "home" / "Dropbox" / "research-data" / "backup" / "backup"
    bdir.mkdir(parents=True)
    (bdir / "f.dat").write_bytes(b"x" * 1000)
    verdict, lines, actions = ss.build_report(repo, which=no_tool, hooks_dir=lfs_hooks, home=tmp / "home")
    check("ss_backup_reported", any("Periodic backup" in ln for ln in lines) and verdict == "PASS",
          f"{verdict} {lines}")

    repo = mkrepo(tmp, "plain")
    commit_file(repo, "paper.pdf", b"%PDF-1.4 sentinel\n", "pdf as a plain blob")
    commit_file(repo, ".gitattributes", b"*.pdf filter=lfs diff=lfs merge=lfs -text\n", "route pdf to lfs")
    set_upstream_here(repo)
    verdict, lines, actions = ss.build_report(repo, which=no_tool, hooks_dir=lfs_hooks, home=tmp)
    check("ss_plain_under_lfs_flagged",
          any("renormalize" in a and "paper.pdf" in a for a in actions), f"{verdict} {actions}")
    check("ss_lfs_patterns_listed", any("*.pdf" in ln for ln in lines), str(lines))

    repo = mkrepo(tmp, "unpushedlfs")
    commit_file(repo, ".gitattributes", b"*.bin filter=lfs diff=lfs merge=lfs -text\n", "route bin to lfs")
    set_upstream_here(repo)
    commit_file(repo, "x.bin", bytes(range(200)), "an lfs file")
    lfs_listed = "x.bin" in g(repo, "lfs", "ls-files", "-n")
    verdict, lines, actions = ss.build_report(repo, which=no_tool, hooks_dir=empty_hooks, home=tmp)
    check("ss_unpushed_lfs_hook_skipped_flagged", lfs_listed
          and any("git lfs push origin main" in a for a in actions), f"lfs={lfs_listed} {actions}")
    verdict, lines, actions = ss.build_report(repo, which=no_tool, hooks_dir=lfs_hooks, home=tmp)
    check("ss_unpushed_lfs_hook_runs_no_lfs_action",
          not any("git lfs push" in a for a in actions) and any("git push" in a for a in actions), str(actions))

    repo = mkrepo(tmp, "dvc")
    (repo / ".dvc").mkdir()
    set_upstream_here(repo)
    verdict, lines, actions = ss.build_report(repo, which=no_tool, hooks_dir=lfs_hooks, home=tmp)
    check("ss_dvc_without_cli_unverified", verdict == "UNVERIFIED" and any("dvc" in ln for ln in lines),
          f"{verdict} {lines}")
    check("ss_dvc_without_cli_exit_3",
          ss.main([str(repo), "--hooks-dir", str(lfs_hooks)], which=no_tool) == 3)

    check("ss_usage_exit_2", ss.main(["--bogus"]) == 2)
    check("ss_missing_dir_exit_2", ss.main([str(tmp / "nope")]) == 2)
    check("ss_not_a_repo_exit_2", ss.main([str(empty_hooks)]) == 2)


def main() -> int:
    global ss
    try:
        ss = load()
    except Exception as e:  # noqa: BLE001
        print(f"FAIL  cannot load sync_status.py: {e!r}")
        return 1
    with tempfile.TemporaryDirectory() as t:
        for name, fn in sorted(globals().items()):
            if name.startswith("test_") and callable(fn):
                print(name)
                fn(Path(t))
    print(f"\n{PASSES} passed, {len(FAILS)} failed")
    if FAILS:
        print("failed: " + ", ".join(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
