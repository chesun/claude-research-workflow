#!/usr/bin/env python3
"""
/tools propagate — synchronize selected files from this workflow source repo
to all configured consumer repos, routing per the file-class manifest.

Reads:
  .claude/state/consumers.toml   (workflow source — gitignored)
  .claude/file-classes.toml      (workflow source, on main branch — class manifest)
Writes (per consumer):
  copies of selected files at matching paths
  .claude/state/workflow-sync.json   (consumer — gitignored)
  one git commit per consumer with traceable source-commit ref

Design and rationale:
  v1: quality_reports/plans/2026-05-06_tools-propagate-plan.md
  v2: quality_reports/plans/2026-05-07_comprehensive-propagation-plan.md (file taxonomy)

Class-aware routing (per file-classes.toml):
  Class A — Universal:           read from main
  Class B — Overlay-customized:  read from consumer's overlay
  Class C — Overlay-only:        read from consumer's overlay (skip if branch mismatch)
  Class D — Excluded:            never propagate (skip silently)

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
import fnmatch
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

CLASS_LABELS = {
    "universal": "A",
    "overlay-customized": "B",
    "overlay-only": "C",
    "excluded": "D",
}


# ----- file-class manifest --------------------------------------------------

class Manifest:
    """Parsed .claude/file-classes.toml — class lookup with precedence."""

    def __init__(self, data: dict, source_ref: str):
        self.source_ref = source_ref  # for diagnostics
        self._exclude_patterns = data.get("exclude", {}).get("patterns", [])
        self._universal_patterns = data.get("universal", {}).get("patterns", [])
        self._overlay_customized_patterns = (
            data.get("overlay-customized", {}).get("patterns", [])
        )
        self._overlay_only: list[dict] = []
        for entry in data.get("overlay-only", []):
            branches = set(entry.get("branches", []))
            invalid = branches - VALID_OVERLAYS
            if invalid:
                print(
                    f"WARNING: manifest [[overlay-only]] entry has invalid branches "
                    f"{invalid}; ignoring entry: {entry.get('patterns', [])}",
                    file=sys.stderr,
                )
                continue
            self._overlay_only.append({
                "branches": branches,
                "patterns": entry.get("patterns", []),
            })

    @classmethod
    def load_from_main(cls, workflow_root: pathlib.Path) -> "Manifest":
        content = git_show(workflow_root, "main", ".claude/file-classes.toml")
        if content is None:
            sys.exit(
                "ERROR: .claude/file-classes.toml not found on main.\n"
                "  Phase A of the comprehensive propagation plan must land before"
                " /tools propagate works. See quality_reports/plans/"
                "2026-05-07_comprehensive-propagation-plan.md."
            )
        data = tomllib.loads(content.decode("utf-8"))
        return cls(data, source_ref="main:.claude/file-classes.toml")

    @staticmethod
    def _matches_any(path: str, patterns: list[str]) -> bool:
        return any(fnmatch.fnmatch(path, p) for p in patterns)

    def classify(self, path: str) -> tuple[str, set[str] | None]:
        """Return (class_name, branches-for-overlay-only-or-None).

        Precedence: exclude > overlay-only > overlay-customized > universal (default).
        """
        if self._matches_any(path, self._exclude_patterns):
            return ("excluded", None)
        for entry in self._overlay_only:
            if self._matches_any(path, entry["patterns"]):
                return ("overlay-only", entry["branches"])
        if self._matches_any(path, self._overlay_customized_patterns):
            return ("overlay-customized", None)
        # default
        return ("universal", None)


def resolve_source_branch(
    rel_path: str, consumer_overlay: str, manifest: Manifest
) -> tuple[str | None, str, str]:
    """Return (source_branch, class_name, status).

    source_branch == None means do not propagate this file to this consumer.
    status is one of: ok | excluded | overlay-only-not-applicable.
    """
    cls, branches = manifest.classify(rel_path)
    if cls == "excluded":
        return (None, cls, "excluded")
    if cls == "universal":
        return ("main", cls, "ok")
    if cls == "overlay-customized":
        return (consumer_overlay, cls, "ok")
    if cls == "overlay-only":
        if branches and consumer_overlay in branches:
            return (consumer_overlay, cls, "ok")
        return (None, cls, "overlay-only-not-applicable")
    raise ValueError(f"unknown class from manifest.classify: {cls!r}")


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
    manifest: Manifest,
    dry_run: bool,
    force_initial: bool,
) -> dict:
    consumer_path = consumer["path"]
    overlay = consumer["overlay"]
    state = load_sync_state(consumer_path)
    records = state.get("synced_files", {})

    # Per-file output records: list of (rel_path, class_name, source_branch)
    copied: list[tuple[str, str, str]] = []
    skipped_in_sync: list[tuple[str, str, str]] = []
    skipped_divergent: list[tuple[str, str, str]] = []
    skipped_missing_branch: list[tuple[str, str, str]] = []
    skipped_ambiguous: list[tuple[str, str, str]] = []
    skipped_excluded: list[str] = []
    skipped_not_applicable: list[tuple[str, str]] = []  # (rel_path, class_name)
    new_records_only: list[tuple[str, str, str]] = []

    # Sanity check: consumer's overlay must exist on workflow source
    if not git_branch_exists(workflow_root, overlay):
        return {
            "consumer": str(consumer_path), "overlay": overlay,
            "copied": copied, "skipped_in_sync": skipped_in_sync,
            "skipped_divergent": skipped_divergent,
            "skipped_missing_branch": [(p, "?", overlay) for p in file_paths],
            "skipped_ambiguous": skipped_ambiguous,
            "skipped_excluded": skipped_excluded,
            "skipped_not_applicable": skipped_not_applicable,
            "new_records_only": new_records_only,
            "commit_sha": None, "state_written": False,
            "error": f"workflow has no branch {overlay!r}",
        }

    for rel_path in file_paths:
        source_branch, class_name, status = resolve_source_branch(
            rel_path, overlay, manifest
        )
        if status == "excluded":
            skipped_excluded.append(rel_path)
            continue
        if status == "overlay-only-not-applicable":
            skipped_not_applicable.append((rel_path, class_name))
            continue
        # status == "ok"; source_branch is set
        assert source_branch is not None

        source_bytes = git_show(workflow_root, source_branch, rel_path)
        if source_bytes is None:
            skipped_missing_branch.append((rel_path, class_name, source_branch))
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
                    skipped_divergent.append((rel_path, class_name, source_branch))
                    continue
                if source_hash == record_source_hash:
                    skipped_in_sync.append((rel_path, class_name, source_branch))
                    continue
                # workflow updated; consumer matches old version → safe to copy
            else:
                # no sync record yet
                if current_hash == source_hash:
                    # already matches; just record it (no commit needed for this)
                    if not dry_run:
                        records[rel_path] = {
                            "class": class_name,
                            "source_branch": source_branch,
                            "source_sha256": source_hash,
                            "consumer_sha256_at_sync": current_hash,
                        }
                        new_records_only.append((rel_path, class_name, source_branch))
                    skipped_in_sync.append((rel_path, class_name, source_branch))
                    continue
                if not force_initial:
                    skipped_ambiguous.append((rel_path, class_name, source_branch))
                    continue
                # force_initial → treat as initial sync; fall through to copy

        if not dry_run:
            write_file_bytes(target, source_bytes)
            records[rel_path] = {
                "class": class_name,
                "source_branch": source_branch,
                "source_sha256": source_hash,
                "consumer_sha256_at_sync": source_hash,  # post-write hash equals source
            }
        copied.append((rel_path, class_name, source_branch))

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
        commit_sha = git_add_commit(
            consumer_path, [p for p, _, _ in copied], message
        )

    return {
        "consumer": str(consumer_path), "overlay": overlay,
        "copied": copied, "skipped_in_sync": skipped_in_sync,
        "skipped_divergent": skipped_divergent,
        "skipped_missing_branch": skipped_missing_branch,
        "skipped_ambiguous": skipped_ambiguous,
        "skipped_excluded": skipped_excluded,
        "skipped_not_applicable": skipped_not_applicable,
        "new_records_only": new_records_only,
        "commit_sha": commit_sha,
        "state_written": state_written,
    }


def build_commit_message(
    copied: list[tuple[str, str, str]],
    workflow_root: pathlib.Path,
    overlay: str,
) -> str:
    head = git_head_short(workflow_root)
    # Annotate each file with its source branch (most are 'main'; flagging the
    # exceptions keeps the audit trail explicit for Class B/C).
    files_block = "\n".join(
        f"- {p}  ← {src} [{cls}]" for p, cls, src in copied
    )
    return (
        f"chore(workflow-sync): propagate updates from claude-code-my-workflow\n\n"
        f"Files updated ({len(copied)}):\n{files_block}\n\n"
        f"Source: claude-code-my-workflow @ {head} (consumer overlay: {overlay})\n"
        f"Routed via: .claude/file-classes.toml @ main\n"
        f"Synced via: /tools propagate\n\n"
        f"Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
    )


# ----- output ---------------------------------------------------------------

def _fmt_file_line(rel_path: str, class_name: str, source_branch: str) -> str:
    """Format one file's annotation: path  ← branch  [class]"""
    cls_letter = CLASS_LABELS.get(class_name, "?")
    return f"{rel_path}  ← {source_branch}  [{cls_letter} {class_name}]"


def print_summary(summary: list[dict], dry_run: bool) -> None:
    print()
    print(f"=== {'DRY RUN' if dry_run else 'PROPAGATION'} SUMMARY ===")
    print()
    totals = {
        "copied": 0, "in_sync": 0, "divergent": 0,
        "missing": 0, "ambiguous": 0,
        "excluded": 0, "not_applicable": 0,
        "commits": 0,
    }
    for r in summary:
        copied_n = len(r["copied"])
        in_sync_n = len(r["skipped_in_sync"])
        div_n = len(r["skipped_divergent"])
        miss_n = len(r["skipped_missing_branch"])
        ambig_n = len(r["skipped_ambiguous"])
        excl_n = len(r.get("skipped_excluded", []))
        not_app_n = len(r.get("skipped_not_applicable", []))
        totals["copied"] += copied_n
        totals["in_sync"] += in_sync_n
        totals["divergent"] += div_n
        totals["missing"] += miss_n
        totals["ambiguous"] += ambig_n
        totals["excluded"] += excl_n
        totals["not_applicable"] += not_app_n
        if r.get("commit_sha"):
            totals["commits"] += 1

        name = pathlib.Path(r["consumer"]).name
        print(f"  {name} ({r['overlay']})")
        if r.get("error"):
            print(f"    ERROR: {r['error']}")
        if copied_n:
            label = "would copy" if dry_run else "copied"
            print(f"    {label}: {copied_n}")
            for p, cls, src in r["copied"]:
                print(f"      + {_fmt_file_line(p, cls, src)}")
        if in_sync_n:
            print(f"    in-sync: {in_sync_n}")
        if div_n:
            print(f"    DIVERGENT (skipped — consumer has local edits since last sync): {div_n}")
            for p, cls, src in r["skipped_divergent"]:
                print(f"      ! {_fmt_file_line(p, cls, src)}")
        if miss_n:
            print(f"    MISSING-ON-SOURCE (skipped — file's class says read from a branch where it doesn't exist): {miss_n}")
            for p, cls, src in r["skipped_missing_branch"]:
                print(f"      ? {_fmt_file_line(p, cls, src)}")
        if ambig_n:
            print(f"    AMBIGUOUS (skipped — file present but no sync record; use --force-initial to bootstrap): {ambig_n}")
            for p, cls, src in r["skipped_ambiguous"]:
                print(f"      ? {_fmt_file_line(p, cls, src)}")
        if not_app_n:
            print(f"    NOT-APPLICABLE (skipped — overlay-only file for a different overlay): {not_app_n}")
            for p, cls in r["skipped_not_applicable"]:
                print(f"      - {p}  [{CLASS_LABELS.get(cls, '?')} {cls}]")
        if excl_n:
            print(f"    EXCLUDED (skipped — manifest [exclude] match): {excl_n}")
        if r.get("commit_sha"):
            print(f"    commit: {r['commit_sha']}")
        print()
    print(
        f"Totals: copied={totals['copied']} | in-sync={totals['in_sync']} | "
        f"divergent={totals['divergent']} | missing-on-source={totals['missing']} | "
        f"ambiguous={totals['ambiguous']} | excluded={totals['excluded']} | "
        f"not-applicable={totals['not_applicable']} | commits={totals['commits']}"
    )


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

    # Load the file-class manifest from main (canonical, even if cwd is on an overlay)
    manifest = Manifest.load_from_main(repo_root)

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
    print(f"Manifest: {manifest.source_ref}")
    print(f"Files: {', '.join(file_paths)}")
    print()

    summary = []
    for consumer in consumers:
        result = propagate_one_consumer(
            repo_root, consumer, file_paths, manifest,
            args.dry_run, args.force_initial,
        )
        summary.append(result)

    print_summary(summary, args.dry_run)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
