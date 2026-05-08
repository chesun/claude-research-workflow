#!/usr/bin/env python3
"""
bootstrap_manifest.py — one-shot audit script for Phase A of the comprehensive
propagation plan (quality_reports/plans/2026-05-07_comprehensive-propagation-plan.md).

Diffs every tracked path across main / applied-micro / behavioral and proposes
a classification per the three-class taxonomy:

  A — Universal:           identical on every branch where it exists; source = main
  B — Overlay-customized:  exists on multiple branches with different content; source = consumer's overlay
  C — Overlay-only:        exists on exactly one overlay branch; source = that overlay
  D — Excluded:            never propagates (project-state files)

Output: a draft .claude/file-classes.toml written to
quality_reports/plans/proposals/proposed-file-classes-2026-05-07.toml,
with per-file comments explaining each classification.

This is a throwaway. After Phase A is complete and the manifest is committed
to .claude/file-classes.toml on main, this script should be deleted.

Usage:
  python3 .claude/skills/tools/bootstrap_manifest.py [--output PATH]

Requires Python 3.11+ and a workflow source repo with the three branches present.
"""

from __future__ import annotations

import argparse
import fnmatch
import pathlib
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass

BRANCHES = ["main", "applied-micro", "behavioral"]

# Patterns that should always be Class D (excluded). Match against repo-relative paths.
# Order matters only for clarity; matching is OR.
EXCLUDE_PATTERNS = [
    "quality_reports/*",
    "quality_reports/**",
    "decisions/*",
    "decisions/**",
    "master_supporting_docs/literature/papers/*.pdf",
    "master_supporting_docs/literature/papers/**/*.pdf",
    "master_supporting_docs/literature/reading_notes/*",
    "master_supporting_docs/literature/reading_notes/**",
    ".claude/state/*",
    ".claude/state/**",
    ".dvc/*",
    ".dvc/**",
    "data/*",
    "data/**",
    "scripts/*",
    "scripts/**",
    "paper/*",
    "paper/**",
    "talks/*",
    "talks/**",
    "figures/*",
    "figures/**",
    "tables/*",
    "tables/**",
    "explorations/*",
    "explorations/**",
    "replication/*",
    "replication/**",
    "preambles/*",
    "preambles/**",
    "MEMORY.md",
    "SESSION_REPORT.md",
    "TODO.md",
]


@dataclass
class PathRecord:
    """One tracked path's hash on each branch (None = absent on that branch)."""

    path: str
    hashes: dict[str, str | None]

    @property
    def present_on(self) -> list[str]:
        return [b for b, h in self.hashes.items() if h is not None]

    @property
    def all_hashes_match(self) -> bool:
        present = [h for h in self.hashes.values() if h is not None]
        return len(set(present)) == 1


# ----- git helpers ----------------------------------------------------------


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def list_paths_on_branch(branch: str) -> list[tuple[str, str]]:
    """Return [(path, blob-sha), ...] for every blob tracked on `branch`."""
    out = git("ls-tree", "-r", branch)
    rows: list[tuple[str, str]] = []
    for line in out.splitlines():
        # format: <mode> <type> <sha>\t<path>
        meta, path = line.split("\t", 1)
        mode, blob_type, sha = meta.split()
        if blob_type != "blob":
            continue
        rows.append((path, sha))
    return rows


def collect_path_records() -> dict[str, PathRecord]:
    """Collect hashes for every path that appears on any branch."""
    records: dict[str, PathRecord] = {}
    for branch in BRANCHES:
        for path, sha in list_paths_on_branch(branch):
            rec = records.setdefault(
                path, PathRecord(path=path, hashes={b: None for b in BRANCHES})
            )
            rec.hashes[branch] = sha
    return records


# ----- classification -------------------------------------------------------


def matches_exclude(path: str) -> bool:
    return any(fnmatch.fnmatch(path, pat) for pat in EXCLUDE_PATTERNS)


def classify(rec: PathRecord) -> tuple[str, str]:
    """Return (class, comment). Class is one of: A, B, C, D, AMBIGUOUS."""
    if matches_exclude(rec.path):
        return ("D", "matches exclude pattern (project state, not propagatable)")

    on = rec.present_on
    if not on:
        return ("D", "tracked nowhere — should not happen")

    if "main" not in on:
        # Overlay-only — Class C
        return ("C", f"overlay-only on {','.join(on)}")

    if len(on) == 1:
        # Only on main
        return ("A", "exists only on main; default Universal (no overlay version yet)")

    # Exists on main + at least one overlay
    if rec.all_hashes_match:
        return ("A", "byte-identical across all branches")

    # Exists on multiple branches but content differs — Class B candidate or stale-of-main
    main_hash = rec.hashes["main"]
    diff_overlays = [
        b for b, h in rec.hashes.items() if b != "main" and h is not None and h != main_hash
    ]
    return (
        "AMBIGUOUS",
        f"differs from main on {','.join(diff_overlays)} — user reviews B vs stale-of-main",
    )


# ----- TOML emission --------------------------------------------------------


def emit_toml(
    by_class: dict[str, list[tuple[PathRecord, str]]],
    output_path: pathlib.Path,
    repo_head: str,
) -> None:
    """Write the proposed manifest TOML to output_path."""
    lines: list[str] = []
    lines.append(
        "# Proposed .claude/file-classes.toml — autogenerated by bootstrap_manifest.py"
    )
    lines.append(
        f"# Generated 2026-05-07 from workflow @ {repo_head} across "
        f"branches: {', '.join(BRANCHES)}."
    )
    lines.append("#")
    lines.append(
        "# REVIEW BEFORE COMMITTING TO .claude/file-classes.toml ON MAIN."
    )
    lines.append("#")
    lines.append(
        "# Class definitions — see "
        "quality_reports/plans/2026-05-07_comprehensive-propagation-plan.md §2."
    )
    lines.append(
        "# Particularly review the [overlay-customized] section: any path the script"
    )
    lines.append(
        "# could not auto-classify lands there as 'AMBIGUOUS'. Decide for each:"
    )
    lines.append(
        "#   - genuinely customized? leave under [overlay-customized]"
    )
    lines.append(
        "#   - just stale-of-main? move to [universal] (and resolve via sync-overlays)"
    )
    lines.append("")

    # ----- Universal -----
    universal_paths = [r for r, _ in by_class.get("A", [])]
    lines.append("# CLASS A — Universal: byte-identical on every branch where it exists.")
    lines.append("# Source-of-truth = main. Default for unlisted files.")
    lines.append("# Listed here explicitly for the bootstrap; future Class A files default in.")
    lines.append("[universal]")
    lines.append("patterns = [")
    for rec in sorted(universal_paths, key=lambda r: r.path):
        comment = next(c for r, c in by_class["A"] if r is rec)
        lines.append(f'  "{rec.path}",  # {comment}')
    lines.append("]")
    lines.append("")

    # ----- Overlay-customized (real Class B + AMBIGUOUS for review) -----
    customized = [r for r, _ in by_class.get("B", [])]
    ambiguous = [r for r, _ in by_class.get("AMBIGUOUS", [])]
    lines.append(
        "# CLASS B — Overlay-customized: differs per branch by intent."
    )
    lines.append(
        "# Source-of-truth = consumer's overlay. NOT touched by sync-overlays."
    )
    lines.append(
        "# AUTO-PROPOSAL FLAG: every entry below was auto-classified as ambiguous"
    )
    lines.append(
        "# (file exists on main + at least one overlay with different content)."
    )
    lines.append("# Decide per file: keep here (genuine custom) OR move to [universal] (stale).")
    lines.append("[overlay-customized]")
    lines.append("patterns = [")
    for rec in sorted(customized + ambiguous, key=lambda r: r.path):
        all_records = by_class.get("B", []) + by_class.get("AMBIGUOUS", [])
        comment = next(c for r, c in all_records if r is rec)
        lines.append(f'  "{rec.path}",  # AMBIGUOUS — {comment}')
    lines.append("]")
    lines.append("")

    # ----- Overlay-only (Class C), grouped by branch set -----
    by_branches: dict[tuple[str, ...], list[PathRecord]] = defaultdict(list)
    for rec, _ in by_class.get("C", []):
        key = tuple(sorted(rec.present_on))
        by_branches[key].append(rec)

    lines.append("# CLASS C — Overlay-only: file exists on exactly one (or both) overlay(s).")
    lines.append("# Source-of-truth = the overlay branch where it lives.")
    for branches_key in sorted(by_branches.keys()):
        recs = by_branches[branches_key]
        branches_list = ", ".join(f'"{b}"' for b in branches_key)
        lines.append("[[overlay-only]]")
        lines.append(f"branches = [{branches_list}]")
        lines.append("patterns = [")
        for rec in sorted(recs, key=lambda r: r.path):
            lines.append(f'  "{rec.path}",')
        lines.append("]")
        lines.append("")

    # ----- Excluded -----
    excluded_recs = [r for r, _ in by_class.get("D", [])]
    lines.append(
        "# CLASS D — Excluded: never propagates. Project-state files."
    )
    lines.append("[exclude]")
    lines.append("# Pattern-based exclusions (matched first, before per-file lookup):")
    lines.append("patterns = [")
    for pat in EXCLUDE_PATTERNS:
        lines.append(f'  "{pat}",')
    lines.append("]")
    if excluded_recs:
        lines.append("")
        lines.append(f"# (For reference: {len(excluded_recs)} tracked files matched these patterns.)")
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines))


# ----- main -----------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path(
            "quality_reports/plans/proposals/proposed-file-classes-2026-05-07.toml"
        ),
        help="path to write the proposed manifest",
    )
    args = parser.parse_args()

    # Sanity: confirm the three branches exist
    for branch in BRANCHES:
        try:
            git("rev-parse", "--verify", branch)
        except subprocess.CalledProcessError:
            print(
                f"ERROR: branch '{branch}' not found. "
                "This script must run from a workflow source repo with main / applied-micro / behavioral.",
                file=sys.stderr,
            )
            return 2

    print(f"Collecting tracked paths from {len(BRANCHES)} branches...")
    records = collect_path_records()
    print(f"  Found {len(records)} unique paths.")

    by_class: dict[str, list[tuple[PathRecord, str]]] = defaultdict(list)
    for rec in records.values():
        cls, comment = classify(rec)
        by_class[cls].append((rec, comment))

    # Summary
    summary = {cls: len(records_list) for cls, records_list in by_class.items()}
    print("\nClassification summary:")
    print(f"  A (Universal):              {summary.get('A', 0)}")
    print(f"  B (Overlay-customized):     {summary.get('B', 0)}")
    print(f"  C (Overlay-only):           {summary.get('C', 0)}")
    print(f"  D (Excluded):               {summary.get('D', 0)}")
    print(
        f"  AMBIGUOUS (need user review): {summary.get('AMBIGUOUS', 0)}"
        " — these need explicit B vs stale-of-main decisions"
    )

    # Get repo HEAD for traceability
    repo_head = git("rev-parse", "--short", "HEAD").strip()

    emit_toml(by_class, args.output, repo_head)
    print(f"\nWrote proposed manifest to: {args.output}")
    print("Next: review this file; edit AMBIGUOUS entries (move stale-of-main to [universal]);")
    print("then copy approved content to .claude/file-classes.toml on main and commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
