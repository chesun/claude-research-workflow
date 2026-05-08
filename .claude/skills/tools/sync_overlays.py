#!/usr/bin/env python3
"""
/tools sync-overlays — pull Class A (Universal) file updates from main to overlay worktrees.

Reads:
  .claude/file-classes.toml      (workflow source, on main — class manifest)
Writes (per overlay worktree):
  copies of Class A files at matching paths
  one git commit per overlay listing the propagated Class A files

Design and rationale: quality_reports/plans/2026-05-07_comprehensive-propagation-plan.md §5

Routing:
  - Only Class A (Universal) files are touched. Class B / C / D are NEVER overwritten.
  - For each Class A path on main:
      overlay missing the file  -> copy (new universal file landing)
      overlay matches main      -> no-op
      overlay differs from main -> SKIP with warning (preserves intentional out-of-band edits);
                                   pass --force to overwrite anyway.

Worktree assumption (from the plan, D9):
  ~/github_repos/claude-code-my-workflow                          (main)
  ~/github_repos/claude-code-my-workflow-applied-micro            (applied-micro)
  ~/github_repos/claude-code-my-workflow-behavioral               (behavioral)

Usage:
  python3 sync_overlays.py [--dry-run] [--force]

Environment:
  Run from the workflow source repo (the main worktree). Requires Python 3.11+.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import pathlib
import subprocess
import sys

try:
    import tomllib  # Python 3.11+
except ImportError:
    sys.exit("sync_overlays.py requires Python 3.11+ (for tomllib).")

OVERLAY_BRANCHES = ["applied-micro", "behavioral"]


# ----- git helpers ----------------------------------------------------------

def git(*args: str, repo: pathlib.Path | None = None) -> str:
    cmd = ["git"]
    if repo is not None:
        cmd += ["-C", str(repo)]
    cmd += list(args)
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def git_show(repo: pathlib.Path, ref: str, path: str) -> bytes | None:
    r = subprocess.run(
        ["git", "-C", str(repo), "show", f"{ref}:{path}"],
        capture_output=True, check=False,
    )
    return r.stdout if r.returncode == 0 else None


def find_main_worktree() -> pathlib.Path:
    """Return the workflow source repo's main worktree (where script is run from)."""
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return pathlib.Path(out).resolve()


def list_worktrees(repo: pathlib.Path) -> dict[str, pathlib.Path]:
    """Map branch-name -> worktree-path for every git worktree of `repo`."""
    out = git("worktree", "list", "--porcelain", repo=repo)
    result: dict[str, pathlib.Path] = {}
    current_path: pathlib.Path | None = None
    for line in out.splitlines():
        if line.startswith("worktree "):
            current_path = pathlib.Path(line[len("worktree "):]).resolve()
        elif line.startswith("branch ") and current_path is not None:
            ref = line[len("branch "):]
            # strip refs/heads/
            branch = ref.replace("refs/heads/", "", 1)
            result[branch] = current_path
            current_path = None
        elif line == "":
            current_path = None
    return result


def worktree_class_a_dirty(
    worktree: pathlib.Path, manifest: dict
) -> list[str]:
    """List paths with uncommitted state that classify to Class A (Universal).

    Untracked files / modified files outside Class A are irrelevant to sync-overlays
    (it never touches them), so don't let them block the run.
    """
    out = subprocess.run(
        ["git", "-C", str(worktree), "status", "--porcelain"],
        check=True, capture_output=True, text=True,
    ).stdout
    dirty: list[str] = []
    for line in out.splitlines():
        if not line:
            continue
        # porcelain format: XY <path>  (where XY is two status chars)
        path = line[3:].strip()
        # Handle rename "from -> to" — take the new path
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if classify(path, manifest) == "universal":
            dirty.append(path)
    return dirty


# ----- manifest -------------------------------------------------------------

def load_manifest(main_repo: pathlib.Path) -> dict:
    content = git_show(main_repo, "main", ".claude/file-classes.toml")
    if content is None:
        sys.exit(
            "ERROR: .claude/file-classes.toml not found on main.\n"
            "  Run Phase A (bootstrap_manifest.py) and commit the manifest first."
        )
    return tomllib.loads(content.decode("utf-8"))


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, p) for p in patterns)


def classify(path: str, manifest: dict) -> str:
    """Same precedence as propagate.py: exclude > overlay-only > overlay-customized > universal."""
    if matches_any(path, manifest.get("exclude", {}).get("patterns", [])):
        return "excluded"
    for entry in manifest.get("overlay-only", []):
        if matches_any(path, entry.get("patterns", [])):
            return "overlay-only"
    if matches_any(path, manifest.get("overlay-customized", {}).get("patterns", [])):
        return "overlay-customized"
    return "universal"


# ----- file ops -------------------------------------------------------------

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def list_class_a_paths_on_main(main_repo: pathlib.Path, manifest: dict) -> list[str]:
    """Every tracked path on main that classifies to Class A."""
    out = git("ls-tree", "-r", "--name-only", "main", repo=main_repo)
    return [p for p in out.splitlines() if classify(p, manifest) == "universal"]


# ----- per-overlay sync -----------------------------------------------------

def sync_one_overlay(
    main_repo: pathlib.Path,
    overlay: str,
    overlay_worktree: pathlib.Path,
    class_a_paths: list[str],
    manifest: dict,
    dry_run: bool,
    force: bool,
) -> dict:
    """Sync Class A paths from main into overlay_worktree. Commit per overlay."""
    new_files: list[str] = []      # absent on overlay -> copy
    updated: list[str] = []        # differs (and force) -> overwrite
    in_sync: list[str] = []        # already matches
    skipped_divergent: list[str] = []  # differs and not --force

    dirty_a = worktree_class_a_dirty(overlay_worktree, manifest)
    if dirty_a:
        return {
            "overlay": overlay, "worktree": str(overlay_worktree),
            "error": (
                "worktree has uncommitted changes in Class A paths; commit or stash "
                f"before syncing. Dirty Class A paths: {dirty_a}"
            ),
            "new_files": new_files, "updated": updated, "in_sync": in_sync,
            "skipped_divergent": skipped_divergent, "commit_sha": None,
        }

    for rel_path in class_a_paths:
        main_bytes = git_show(main_repo, "main", rel_path)
        if main_bytes is None:
            continue  # Should not happen since we listed from main
        main_hash = sha256_bytes(main_bytes)

        target = overlay_worktree / rel_path
        if target.exists():
            current_bytes = target.read_bytes()
            if sha256_bytes(current_bytes) == main_hash:
                in_sync.append(rel_path)
                continue
            # differs
            if not force:
                skipped_divergent.append(rel_path)
                continue
            # force: fall through to overwrite

            if not dry_run:
                target.write_bytes(main_bytes)
            updated.append(rel_path)
        else:
            # new universal file landing on overlay
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(main_bytes)
            new_files.append(rel_path)

    commit_sha = None
    staged = new_files + updated
    if staged and not dry_run:
        subprocess.run(["git", "-C", str(overlay_worktree), "add"] + staged, check=True)
        head_short = git("rev-parse", "--short", "HEAD", repo=main_repo).strip()
        files_block = "\n".join(f"- {p}" for p in staged)
        message = (
            f"sync(overlays): pull Class A updates from main\n\n"
            f"Files updated ({len(staged)}):\n{files_block}\n\n"
            f"Source: claude-code-my-workflow @ main {head_short}\n"
            f"Routed via: .claude/file-classes.toml @ main\n"
            f"Synced via: /tools sync-overlays\n\n"
            f"Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
        )
        subprocess.run(
            ["git", "-C", str(overlay_worktree), "commit", "-m", message],
            check=True,
        )
        commit_sha = git(
            "rev-parse", "--short", "HEAD", repo=overlay_worktree
        ).strip()

    return {
        "overlay": overlay, "worktree": str(overlay_worktree),
        "new_files": new_files, "updated": updated, "in_sync": in_sync,
        "skipped_divergent": skipped_divergent, "commit_sha": commit_sha,
        "error": None,
    }


# ----- output ---------------------------------------------------------------

def print_summary(summary: list[dict], dry_run: bool, force: bool) -> None:
    print()
    label = "DRY RUN" if dry_run else "SYNC"
    if force:
        label += " --force"
    print(f"=== /tools sync-overlays {label} SUMMARY ===")
    print()
    totals = {"new": 0, "updated": 0, "in_sync": 0, "divergent": 0, "commits": 0}
    for r in summary:
        new_n = len(r["new_files"])
        upd_n = len(r["updated"])
        sync_n = len(r["in_sync"])
        div_n = len(r["skipped_divergent"])
        totals["new"] += new_n
        totals["updated"] += upd_n
        totals["in_sync"] += sync_n
        totals["divergent"] += div_n
        if r.get("commit_sha"):
            totals["commits"] += 1

        print(f"  {r['overlay']}  ({r['worktree']})")
        if r.get("error"):
            print(f"    ERROR: {r['error']}")
            print()
            continue
        if new_n:
            verb = "would add" if dry_run else "added"
            print(f"    {verb} (new on overlay): {new_n}")
            for p in r["new_files"]:
                print(f"      + {p}")
        if upd_n:
            verb = "would overwrite" if dry_run else "overwrote"
            print(f"    {verb} (was stale-of-main): {upd_n}")
            for p in r["updated"]:
                print(f"      ~ {p}")
        if sync_n:
            print(f"    in-sync: {sync_n}")
        if div_n:
            verb = "would skip" if dry_run else "SKIPPED"
            print(f"    {verb} DIVERGENT (overlay differs from main; pass --force to overwrite): {div_n}")
            for p in r["skipped_divergent"]:
                print(f"      ! {p}")
        if r.get("commit_sha"):
            print(f"    commit: {r['commit_sha']}")
        print()
    print(
        f"Totals: new={totals['new']} | updated={totals['updated']} | "
        f"in-sync={totals['in_sync']} | divergent-skipped={totals['divergent']} | "
        f"commits={totals['commits']}"
    )


# ----- main -----------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(prog="sync_overlays.py", description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="report proposed changes without writing or committing")
    parser.add_argument("--force", action="store_true",
                        help="overwrite Class A files on overlays even if they differ from main")
    args = parser.parse_args()

    main_repo = find_main_worktree()
    worktrees = list_worktrees(main_repo)

    # Verify each overlay branch has a worktree
    missing = [b for b in OVERLAY_BRANCHES if b not in worktrees]
    if missing:
        sys.exit(
            f"ERROR: missing worktree(s) for {missing}. Set them up with:\n"
            + "\n".join(
                f"  git worktree add ../claude-code-my-workflow-{b} {b}"
                for b in missing
            )
        )

    print(f"Workflow source (main): {main_repo}")
    print(f"Overlay worktrees:")
    for b in OVERLAY_BRANCHES:
        print(f"  {b}: {worktrees[b]}")
    print()

    manifest = load_manifest(main_repo)
    class_a_paths = list_class_a_paths_on_main(main_repo, manifest)
    print(f"Class A paths to sync: {len(class_a_paths)}")
    if args.dry_run:
        print("(DRY RUN — no files will be written, no commits made)")
    print()

    summary = []
    for overlay in OVERLAY_BRANCHES:
        result = sync_one_overlay(
            main_repo, overlay, worktrees[overlay], class_a_paths, manifest,
            args.dry_run, args.force,
        )
        summary.append(result)

    print_summary(summary, args.dry_run, args.force)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
