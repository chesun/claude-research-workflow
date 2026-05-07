#!/usr/bin/env python3
"""
/tools propagate — synchronize selected files from this workflow source repo
to all configured consumer repos.

Reads:
  .claude/state/consumers.toml   (workflow source — gitignored)
Writes (per consumer):
  copies of selected files at matching paths
  .claude/state/workflow-sync.json   (consumer — gitignored)
  one git commit per consumer with traceable source-commit ref

Design and rationale: quality_reports/plans/2026-05-06_tools-propagate-plan.md

Identity modes:
  source     - has consumers.toml; runs the propagation
  consumer   - has workflow-sync.json; exits with hint "run from source"
  none       - has neither; exits with hint about how to set up

Usage:
  python3 propagate.py --check-identity
  python3 propagate.py [--dry-run] [--force-initial] [--only PATHS] PATTERN [PATTERN...]

Environment:
  Requires Python 3.11+ (uses tomllib).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

try:
    import tomllib  # Python 3.11+
except ImportError:
    sys.exit("propagate.py requires Python 3.11+ (for tomllib). Install a newer Python.")

VALID_OVERLAYS = {"main", "applied-micro", "behavioral"}


# ----- repo discovery and identity ------------------------------------------

def find_repo_root(start: pathlib.Path) -> pathlib.Path:
    p = start.resolve()
    while p != p.parent:
        if (p / ".git").exists():
            return p
        p = p.parent
    sys.exit("propagate.py: not in a git repository.")


def detect_identity(repo_root: pathlib.Path) -> str:
    state = repo_root / ".claude" / "state"
    if (state / "consumers.toml").exists():
        return "source"
    if (state / "workflow-sync.json").exists():
        return "consumer"
    return "none"


# ----- registry parsing -----------------------------------------------------

def load_consumers(consumers_toml: pathlib.Path) -> list[dict]:
    data = tomllib.loads(consumers_toml.read_text(encoding="utf-8"))
    out = []
    for entry in data.get("consumer", []):
        path_raw = entry.get("path")
        overlay = entry.get("overlay")
        if not path_raw or not overlay:
            print(f"WARNING: skipping invalid consumer entry: {entry}", file=sys.stderr)
            continue
        if overlay not in VALID_OVERLAYS:
            print(f"WARNING: invalid overlay {overlay!r} for {path_raw}; skipping", file=sys.stderr)
            continue
        path = pathlib.Path(path_raw).expanduser().resolve()
        if not path.is_dir() or not (path / ".git").exists():
            print(f"WARNING: consumer path missing or not a git repo: {path}; skipping", file=sys.stderr)
            continue
        out.append({"path": path, "overlay": overlay, "note": entry.get("note", "")})
    return out


# ----- per-consumer sync state ----------------------------------------------

def load_sync_state(consumer_root: pathlib.Path) -> dict:
    p = consumer_root / ".claude" / "state" / "workflow-sync.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_sync_state(consumer_root: pathlib.Path, state: dict) -> None:
    p = consumer_root / ".claude" / "state" / "workflow-sync.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


# ----- git helpers ----------------------------------------------------------

def git_show(repo: pathlib.Path, ref: str, path: str) -> bytes | None:
    r = subprocess.run(
        ["git", "-C", str(repo), "show", f"{ref}:{path}"],
        capture_output=True, check=False,
    )
    return r.stdout if r.returncode == 0 else None


def git_head_short(repo: pathlib.Path) -> str:
    r = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
        capture_output=True, check=True, text=True,
    )
    return r.stdout.strip()


def git_branch_exists(repo: pathlib.Path, ref: str) -> bool:
    r = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", ref],
        capture_output=True, check=False,
    )
    return r.returncode == 0


def git_add_commit(repo: pathlib.Path, paths: list[str], message: str) -> str:
    subprocess.run(["git", "-C", str(repo), "add"] + paths, check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", message], check=True)
    return git_head_short(repo)


# ----- file ops -------------------------------------------------------------

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def write_file_bytes(path: pathlib.Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def resolve_patterns(workflow_root: pathlib.Path, patterns: list[str]) -> list[str]:
    out = set()
    for pattern in patterns:
        for match in workflow_root.glob(pattern):
            if match.is_file():
                out.add(str(match.relative_to(workflow_root)))
    return sorted(out)


# ----- per-consumer propagation ---------------------------------------------

def propagate_one_consumer(
    workflow_root: pathlib.Path,
    consumer: dict,
    file_paths: list[str],
    dry_run: bool,
    force_initial: bool,
) -> dict:
    consumer_path = consumer["path"]
    overlay = consumer["overlay"]
    state = load_sync_state(consumer_path)
    records = state.get("synced_files", {})

    copied: list[str] = []
    skipped_in_sync: list[str] = []
    skipped_divergent: list[str] = []
    skipped_missing_branch: list[str] = []
    skipped_ambiguous: list[str] = []
    new_records_only: list[str] = []  # files where we only updated the record

    if not git_branch_exists(workflow_root, overlay):
        return {
            "consumer": str(consumer_path), "overlay": overlay,
            "copied": copied, "skipped_in_sync": skipped_in_sync,
            "skipped_divergent": skipped_divergent,
            "skipped_missing_branch": list(file_paths),
            "skipped_ambiguous": skipped_ambiguous,
            "commit_sha": None,
            "error": f"workflow has no branch {overlay!r}",
        }

    for rel_path in file_paths:
        source_bytes = git_show(workflow_root, overlay, rel_path)
        if source_bytes is None:
            skipped_missing_branch.append(rel_path)
            continue
        source_hash = sha256_bytes(source_bytes)

        target = consumer_path / rel_path
        record = records.get(rel_path, {})
        record_source_hash = record.get("source_sha256")
        record_at_sync = record.get("consumer_sha256_at_sync")

        if target.exists():
            current_bytes = target.read_bytes()
            current_hash = sha256_bytes(current_bytes)

            if record_source_hash and record_at_sync:
                if current_hash != record_at_sync:
                    skipped_divergent.append(rel_path)
                    continue
                if source_hash == record_source_hash:
                    skipped_in_sync.append(rel_path)
                    continue
                # workflow updated; consumer matches old version → safe to copy
            else:
                # no sync record yet
                if current_hash == source_hash:
                    # already matches; just record it (no commit needed for this)
                    if not dry_run:
                        records[rel_path] = {
                            "source_sha256": source_hash,
                            "consumer_sha256_at_sync": current_hash,
                        }
                        new_records_only.append(rel_path)
                    skipped_in_sync.append(rel_path)
                    continue
                if not force_initial:
                    skipped_ambiguous.append(rel_path)
                    continue
                # force_initial → treat as initial sync; fall through to copy

        if not dry_run:
            write_file_bytes(target, source_bytes)
            records[rel_path] = {
                "source_sha256": source_hash,
                "consumer_sha256_at_sync": source_hash,  # post-write hash equals source
            }
        copied.append(rel_path)

    commit_sha = None
    state_written = False
    if (copied or new_records_only) and not dry_run:
        state["source_repo"] = str(workflow_root)
        state["overlay"] = overlay
        state["last_synced_commit"] = git_head_short(workflow_root)
        state["last_synced_at"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
        state["synced_files"] = records
        save_sync_state(consumer_path, state)
        state_written = True

    if copied and not dry_run:
        # Stage propagated files only — workflow-sync.json is gitignored
        # (.claude/state/* rule), so we don't try to git-add it.
        message = build_commit_message(copied, workflow_root, overlay)
        commit_sha = git_add_commit(consumer_path, copied, message)

    return {
        "consumer": str(consumer_path), "overlay": overlay,
        "copied": copied, "skipped_in_sync": skipped_in_sync,
        "skipped_divergent": skipped_divergent,
        "skipped_missing_branch": skipped_missing_branch,
        "skipped_ambiguous": skipped_ambiguous,
        "new_records_only": new_records_only,
        "commit_sha": commit_sha,
        "state_written": state_written,
    }


def build_commit_message(copied: list[str], workflow_root: pathlib.Path, overlay: str) -> str:
    head = git_head_short(workflow_root)
    files_block = "\n".join(f"- {p}" for p in copied)
    return (
        f"chore(workflow-sync): propagate updates from claude-code-my-workflow\n\n"
        f"Files updated ({len(copied)}):\n{files_block}\n\n"
        f"Source: claude-code-my-workflow @ {head} ({overlay})\n"
        f"Synced via: /tools propagate\n\n"
        f"Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
    )


# ----- output ---------------------------------------------------------------

def print_summary(summary: list[dict], dry_run: bool) -> None:
    print()
    print(f"=== {'DRY RUN' if dry_run else 'PROPAGATION'} SUMMARY ===")
    print()
    totals = {"copied": 0, "in_sync": 0, "divergent": 0, "missing": 0, "ambiguous": 0, "commits": 0}
    for r in summary:
        copied_n = len(r["copied"])
        in_sync_n = len(r["skipped_in_sync"])
        div_n = len(r["skipped_divergent"])
        miss_n = len(r["skipped_missing_branch"])
        ambig_n = len(r["skipped_ambiguous"])
        totals["copied"] += copied_n
        totals["in_sync"] += in_sync_n
        totals["divergent"] += div_n
        totals["missing"] += miss_n
        totals["ambiguous"] += ambig_n
        if r.get("commit_sha"):
            totals["commits"] += 1

        name = pathlib.Path(r["consumer"]).name
        print(f"  {name} ({r['overlay']})")
        if r.get("error"):
            print(f"    ERROR: {r['error']}")
        if copied_n:
            label = "would copy" if dry_run else "copied"
            print(f"    {label}: {copied_n}")
            for p in r["copied"]:
                print(f"      + {p}")
        if in_sync_n:
            print(f"    in-sync: {in_sync_n}")
        if div_n:
            print(f"    DIVERGENT (skipped — consumer has local edits since last sync): {div_n}")
            for p in r["skipped_divergent"]:
                print(f"      ! {p}")
        if miss_n:
            print(f"    NOT-ON-OVERLAY (skipped): {miss_n}")
            for p in r["skipped_missing_branch"]:
                print(f"      ? {p}")
        if ambig_n:
            print(f"    AMBIGUOUS (skipped — file present but no sync record; use --force-initial to bootstrap): {ambig_n}")
            for p in r["skipped_ambiguous"]:
                print(f"      ? {p}")
        if r.get("commit_sha"):
            print(f"    commit: {r['commit_sha']}")
        print()
    print(f"Totals: copied={totals['copied']} | in-sync={totals['in_sync']} | "
          f"divergent={totals['divergent']} | missing-on-overlay={totals['missing']} | "
          f"ambiguous={totals['ambiguous']} | commits={totals['commits']}")


def print_identity(repo_root: pathlib.Path, identity: str) -> None:
    if identity == "source":
        consumers_path = repo_root / ".claude" / "state" / "consumers.toml"
        consumers = load_consumers(consumers_path)
        print(f"identity: source ({repo_root})")
        print(f"consumers ({len(consumers)}):")
        for c in consumers:
            note = f"  — {c['note']}" if c["note"] else ""
            print(f"  - {c['path']}  ({c['overlay']}){note}")
    elif identity == "consumer":
        state = load_sync_state(repo_root)
        print(f"identity: consumer ({repo_root})")
        print(f"  source_repo:        {state.get('source_repo', '?')}")
        print(f"  overlay:            {state.get('overlay', '?')}")
        print(f"  last_synced_commit: {state.get('last_synced_commit', '?')}")
        print(f"  last_synced_at:     {state.get('last_synced_at', '?')}")
        files = state.get("synced_files", {})
        print(f"  synced_files:       {len(files)}")
    else:
        print(f"identity: none ({repo_root})")
        print("  Neither .claude/state/consumers.toml nor .claude/state/workflow-sync.json exists.")
        print("  To make this a workflow source: create consumers.toml.")
        print("  To make this a consumer: run /tools propagate from a source repo.")


# ----- main -----------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(prog="propagate.py", description=__doc__)
    parser.add_argument("--check-identity", action="store_true",
                        help="print identity status and exit")
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would happen without writing or committing")
    parser.add_argument("--force-initial", action="store_true",
                        help="treat ambiguous files (present but no sync record) as initial sync")
    parser.add_argument("--only", default=None,
                        help="comma-separated list of consumer paths to limit to")
    parser.add_argument("patterns", nargs="*",
                        help="repo-relative file paths or globs to propagate")
    args = parser.parse_args()

    repo_root = find_repo_root(pathlib.Path.cwd())
    identity = detect_identity(repo_root)

    if args.check_identity:
        print_identity(repo_root, identity)
        return 0

    if identity == "consumer":
        state = load_sync_state(repo_root)
        sys.exit(
            "This is a consumer repo. /tools propagate runs from the workflow source.\n"
            f"  Last sync: {state.get('last_synced_commit', '?')} on {state.get('overlay', '?')}.\n"
            f"  Source repo: {state.get('source_repo', '?')}"
        )
    if identity == "none":
        sys.exit(
            "No propagation context here.\n"
            "  - To make this a workflow source: create .claude/state/consumers.toml.\n"
            "  - To make this a consumer: run /tools propagate from a source repo."
        )

    if not args.patterns:
        sys.exit("No patterns given. Usage: /tools propagate <pattern>...")

    file_paths = resolve_patterns(repo_root, args.patterns)
    if not file_paths:
        sys.exit(f"No files matched patterns: {args.patterns}")

    consumers = load_consumers(repo_root / ".claude" / "state" / "consumers.toml")
    if args.only:
        only = {p.strip() for p in args.only.split(",")}
        # match by absolute path or by basename for convenience
        consumers = [
            c for c in consumers
            if str(c["path"]) in only or pathlib.Path(c["path"]).name in only
        ]
    if not consumers:
        sys.exit("No consumers configured (or all filtered out by --only).")

    print(f"Propagating {len(file_paths)} file(s) to {len(consumers)} consumer(s)"
          f"{' (DRY RUN)' if args.dry_run else ''}")
    print(f"Workflow source HEAD: {git_head_short(repo_root)}")
    print(f"Files: {', '.join(file_paths)}")
    print()

    summary = []
    for consumer in consumers:
        result = propagate_one_consumer(
            repo_root, consumer, file_paths, args.dry_run, args.force_initial,
        )
        summary.append(result)

    print_summary(summary, args.dry_run)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
