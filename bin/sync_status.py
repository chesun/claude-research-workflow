#!/usr/bin/env python3
"""Storage sync status for one repository: git, Git LFS, DVC, and the periodic backup.

Usage:  py -I bin/sync_status.py [REPO] [--hooks-dir DIR]

Run before calling a session done, to catch what a plain `git status` misses:
  - commits not yet pushed to the upstream;
  - LFS files in those commits when Git LFS's own pre-push hook does not run (a `core.hooksPath`
    that replaces .git/hooks, as on a machine with git guards), so `git push` would not upload them;
  - files committed as plain blobs although `.gitattributes` routes them to LFS (they show as
    modified with no content change; `git add --renormalize` moves them into LFS);
  - DVC data not yet pushed to its remote, or a DVC setup this machine cannot check.

Verdict and exit code: PASS (0) everything in sync; FAIL (1) at least one action listed;
UNVERIFIED (3) a tier is configured but cannot be checked here (say, no `dvc` CLI); 2 usage error.
Standard library only (see .claude/rules/python-code-conventions.md).
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

POINTER_HEAD = b"version https://git-lfs.github.com/spec/v1"
POINTER_MAX = 1024  # an LFS pointer file is about 130 bytes; anything larger is a plain blob


def git(repo: Path, *args: str) -> tuple[int, str]:
    try:
        r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, str(e)
    return r.returncode, r.stdout.decode("utf-8", "replace")


def lfs_cli_available(repo: Path) -> bool:
    rc, _ = git(repo, "lfs", "version")
    return rc == 0


def lfs_patterns(repo: Path) -> list[str]:
    """Patterns routed to LFS by every tracked `.gitattributes` (shown with their folder)."""
    rc, out = git(repo, "ls-files", "-z", "--", ".gitattributes", "*/.gitattributes")
    found = []
    for rel in [p for p in out.split("\0") if p] if rc == 0 else []:
        f = repo / rel
        if not f.is_file():
            continue
        prefix = rel[: -len(".gitattributes")]
        for ln in f.read_text(encoding="utf-8", errors="replace").splitlines():
            parts = ln.split()
            if parts and not parts[0].startswith("#") and "filter=lfs" in parts[1:]:
                found.append(prefix + parts[0])
    return found


def lfs_attr_files(repo: Path) -> list[str]:
    """Tracked files whose attributes (any .gitattributes, info/attributes, macros) say filter=lfs."""
    rc, files = git(repo, "ls-files", "-z")
    if rc != 0 or not files:
        return []
    paths = [p for p in files.split("\0") if p]
    r = subprocess.run(["git", "-C", str(repo), "check-attr", "--stdin", "-z", "filter"],
                       input="\0".join(paths).encode("utf-8"), capture_output=True)
    fields = r.stdout.decode("utf-8", "replace").split("\0")
    return [fields[i] for i in range(0, len(fields) - 2, 3) if fields[i + 2] == "lfs"]


def plain_under_lfs(repo: Path, lfs_files: list[str] | None = None) -> list[str]:
    """LFS-routed tracked files whose index entry is a plain blob, not a pointer (two git calls in all)."""
    lfs_files = lfs_attr_files(repo) if lfs_files is None else lfs_files
    if not lfs_files:
        return []
    r = subprocess.run(["git", "-C", str(repo), "ls-files", "-s", "-z", "--", *lfs_files], capture_output=True)
    shas = {}
    for entry in r.stdout.decode("utf-8", "replace").split("\0"):
        if "\t" in entry:
            meta, path = entry.split("\t", 1)
            shas[path] = meta.split()[1]
    if not shas:
        return []
    order = list(shas)
    sizes = subprocess.run(["git", "-C", str(repo), "cat-file", "--batch-check=%(objectname) %(objectsize)"],
                           input="\n".join(shas[p] for p in order).encode() + b"\n", capture_output=True)
    size_of = {}
    for ln in sizes.stdout.decode("utf-8", "replace").splitlines():
        parts = ln.split()
        if len(parts) == 2 and parts[1].isdigit():
            size_of[parts[0]] = int(parts[1])
    out, small = [], []
    for p in order:
        s = size_of.get(shas[p])
        if s is None:
            continue
        (small if s <= POINTER_MAX else out).append(p)
    if small:
        r = subprocess.run(["git", "-C", str(repo), "cat-file", "--batch"],
                           input="\n".join(shas[p] for p in small).encode() + b"\n", capture_output=True)
        data, pos = r.stdout, 0
        for p in small:
            nl = data.find(b"\n", pos)
            if nl < 0:
                break
            head = data[pos:nl].split()
            size = int(head[2]) if len(head) == 3 and head[2].isdigit() else 0
            body = data[nl + 1:nl + 1 + size]
            pos = nl + 1 + size + 1
            if not body.startswith(POINTER_HEAD):
                out.append(p)
    return sorted(out)


def upstream_state(repo: Path) -> dict:
    """{'state': 'detached' | 'no-remote' | 'no-upstream' | 'unfetched' | 'error' | 'ok', ...}."""
    rc, branch = git(repo, "symbolic-ref", "-q", "--short", "HEAD")
    if rc != 0 or not branch.strip():
        return {"state": "detached"}
    branch = branch.strip()
    rc, remotes = git(repo, "remote")
    remotes = [r for r in remotes.split() if r] if rc == 0 else []
    _, remote = git(repo, "config", "--get", f"branch.{branch}.remote")
    _, merge = git(repo, "config", "--get", f"branch.{branch}.merge")
    remote, merge = remote.strip(), merge.strip()
    if not remote or not merge:
        if not remotes:
            return {"state": "no-remote", "branch": branch}
        return {"state": "no-upstream", "branch": branch, "remote": "origin" if "origin" in remotes else remotes[0]}
    up_branch = merge.removeprefix("refs/heads/")
    rc, up = git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    if rc != 0 or not up.strip():
        return {"state": "unfetched", "branch": branch, "remote": remote, "up_branch": up_branch}
    up = up.strip()
    rc, counts = git(repo, "rev-list", "--left-right", "--count", f"{up}...HEAD")
    parts = counts.split()
    if rc != 0 or len(parts) != 2 or not all(x.isdigit() for x in parts):
        return {"state": "error", "branch": branch, "upstream": up}
    return {"state": "ok", "branch": branch, "remote": remote, "up_branch": up_branch, "upstream": up,
            "behind": int(parts[0]), "ahead": int(parts[1])}


def unpushed_lfs(repo: Path, upstream: str) -> list[str]:
    rc, out = git(repo, "lfs", "ls-files", "-n", upstream, "HEAD")
    return [ln.strip() for ln in out.splitlines() if ln.strip()] if rc == 0 else []


def hooks_dir_of(repo: Path) -> Path:
    rc, out = git(repo, "rev-parse", "--git-path", "hooks")
    p = Path(out.strip()) if rc == 0 and out.strip() else repo / ".git" / "hooks"
    return p if p.is_absolute() else repo / p


def lfs_hook_runs(hooks: Path) -> bool:
    """True if the pre-push hook in `hooks` calls Git LFS (comments do not count)."""
    f = hooks / "pre-push"
    if not f.is_file():
        return False
    code = "\n".join(ln.split("#", 1)[0] for ln in f.read_text(encoding="utf-8", errors="replace").splitlines())
    return "git lfs" in code or "git-lfs" in code


def dvc_state(repo: Path, which) -> dict:
    if not (repo / ".dvc").is_dir():
        return {"configured": False}
    if not which("dvc"):
        return {"configured": True, "cli": False}
    try:
        r = subprocess.run(["dvc", "status", "-c", "--json"], cwd=repo, capture_output=True, timeout=600)
        pending = r.stdout.decode("utf-8", "replace").strip() not in ("", "{}")
        return {"configured": True, "cli": True, "ok": r.returncode == 0, "pending": pending}
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"configured": True, "cli": True, "ok": False, "error": str(e)}


def backup_state(repo: Path, home: Path) -> dict | None:
    d = home / "Dropbox" / "research-data" / repo.name / "backup"
    if not d.is_dir():
        return None
    files = [p for p in d.rglob("*") if p.is_file()]
    newest = max((p.stat().st_mtime for p in files), default=None)
    return {"path": d, "files": len(files), "size": sum(p.stat().st_size for p in files), "newest": newest}


def build_report(repo: Path, which=shutil.which, hooks_dir: Path | None = None,
                 home: Path | None = None, lfs_available: bool | None = None) -> tuple[str, list[str], list[str]]:
    """(verdict, report lines, action items) for one repository."""
    lines: list[str] = []
    actions: list[str] = []
    unverified = False

    lines.append("=== Git ===")
    up = upstream_state(repo)
    st = up["state"]
    if st == "detached":
        unverified = True
        lines.append("Upstream:            UNVERIFIED — detached HEAD; commits made here are on no branch")
    elif st == "no-remote":
        unverified = True
        lines.append(f"Upstream:            UNVERIFIED — no remote; branch {up['branch']} exists only on this machine")
    elif st == "no-upstream":
        lines.append(f"Upstream:            none for branch {up['branch']}")
        actions.append(f"Run `git push -u {up['remote']} {up['branch']}` — branch {up['branch']} has no upstream, "
                       f"so its commits exist only here")
    elif st == "unfetched":
        lines.append(f"Upstream:            {up['remote']}/{up['up_branch']} is configured but not fetched")
        actions.append(f"Run `git fetch {up['remote']}` and check again — the upstream ref is missing, so "
                       f"unpushed commits cannot be counted")
    elif st == "error":
        unverified = True
        lines.append(f"Upstream:            UNVERIFIED — could not compare with {up['upstream']}")
    else:
        lines.append(f"Upstream:            {up['upstream']} (ahead {up['ahead']}, behind {up['behind']})")
        if up["ahead"]:
            n = up["ahead"]
            actions.append(f"Run `git push` — {n} commit{'s' if n != 1 else ''} not on {up['upstream']}")
        if up["behind"]:
            actions.append(f"Run `git pull` — {up['behind']} commit(s) on {up['upstream']} not here")

    pats = lfs_patterns(repo)
    lfs_files = lfs_attr_files(repo)
    if pats or lfs_files:
        lines.append("")
        lines.append("=== Git LFS ===")
        lines.append(f"Tracked patterns:    {', '.join(pats) if pats else '(set outside a tracked .gitattributes)'}")
        cli = lfs_cli_available(repo) if lfs_available is None else lfs_available
        if not cli:
            unverified = True
            lines.append("Status:              UNVERIFIED — LFS rules are present but the `git-lfs` CLI is not "
                         "installed here, so LFS files cannot be listed or pushed")
        else:
            rc, out = git(repo, "lfs", "ls-files", "-n")
            lines.append(f"LFS files in repo:   {len([x for x in out.splitlines() if x.strip()])}")
        hooks = hooks_dir if hooks_dir is not None else hooks_dir_of(repo)
        runs = lfs_hook_runs(hooks)
        lines.append(f"LFS pre-push hook:   {'runs' if runs else 'does not run'} ({hooks})")
        plain = plain_under_lfs(repo, lfs_files)
        if plain:
            shown = ", ".join(plain[:5]) + (f" and {len(plain) - 5} more" if len(plain) > 5 else "")
            actions.append(f"Run `git add --renormalize -- <files>` and commit — {len(plain)} file(s) committed "
                           f"as plain blobs under an LFS rule: {shown}")
        if cli and st == "ok" and up["ahead"]:
            pend = unpushed_lfs(repo, up["upstream"])
            lines.append(f"LFS files unpushed:  {len(pend)}")
            if pend and not runs:
                actions.append(f"Run `git lfs push {up['remote']} {up['up_branch']}` before `git push` — "
                               f"{len(pend)} LFS file(s) in unpushed commits, and the LFS pre-push hook "
                               f"does not run here")

    dvc = dvc_state(repo, which)
    if dvc["configured"]:
        lines.append("")
        lines.append("=== DVC ===")
        if not dvc["cli"]:
            unverified = True
            lines.append("Status:              UNVERIFIED — .dvc/ is present but the `dvc` CLI is not installed "
                         "here, so pending uploads are unknown")
        elif not dvc.get("ok"):
            unverified = True
            lines.append(f"Status:              UNVERIFIED — `dvc status -c` failed {dvc.get('error', '')}".rstrip())
        else:
            lines.append(f"Pending changes:     {'yes' if dvc['pending'] else 'none'}")
            if dvc["pending"]:
                actions.append("Run `dvc push` (or `dvc pull`) — `dvc status -c` reports changes")

    bk = backup_state(repo, home if home is not None else Path.home())
    if bk is not None:
        lines.append("")
        lines.append("=== Periodic backup (Class D) ===")
        when = time.strftime("%Y-%m-%d %H:%M", time.localtime(bk["newest"])) if bk["newest"] else "never"
        lines.append(f"Last file written:   {when}")
        lines.append(f"Mirror size:         {bk['size'] / 1e6:.1f} MB in {bk['files']} files")

    verdict = "FAIL" if actions else ("UNVERIFIED" if unverified else "PASS")
    return verdict, lines, actions


def main(argv: list[str], which=shutil.which) -> int:
    args = list(argv)
    hooks = None
    if "--hooks-dir" in args:
        i = args.index("--hooks-dir")
        if i + 1 >= len(args):
            print("usage: py -I bin/sync_status.py [REPO] [--hooks-dir DIR]", file=sys.stderr)
            return 2
        hooks = Path(args[i + 1])
        del args[i:i + 2]
    if any(a.startswith("-") for a in args) or len(args) > 1:
        print("usage: py -I bin/sync_status.py [REPO] [--hooks-dir DIR]", file=sys.stderr)
        return 2
    repo = Path(args[0]) if args else Path.cwd()
    if not repo.is_dir():
        print(f"sync_status: no such directory: {repo}", file=sys.stderr)
        return 2
    rc, top = git(repo, "rev-parse", "--show-toplevel")
    if rc != 0 or not top.strip():
        print(f"sync_status: not a git repository: {repo}", file=sys.stderr)
        return 2
    repo = Path(top.strip())
    verdict, lines, actions = build_report(repo, which=which, hooks_dir=hooks)
    print(f"SYNC STATUS: {verdict} — {repo.name}")
    for ln in lines:
        print(ln)
    print("")
    if actions:
        for i, a in enumerate(actions, 1):
            print(f"{i}. {a}")
    elif verdict == "PASS":
        print("All storage tiers in sync.")
    return {"PASS": 0, "FAIL": 1, "UNVERIFIED": 3}[verdict]


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    sys.exit(main(sys.argv[1:]))
