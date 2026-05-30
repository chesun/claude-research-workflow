#!/usr/bin/env python3
"""
normdiff CLI — manual normalized-content diff vs HEAD (evidence-gating Phase 1).

Thin wrapper over `.claude/hooks/normdiff_lib.py`. Prints the residue (content
change beyond path swaps / comments / blank lines / scaffold) of a file versus
its `git show HEAD:<path>` baseline.

Usage:
    python3 .claude/skills/tools/normdiff.py <file> [<file> ...]
    python3 .claude/skills/tools/normdiff.py --check <file>   # exit 1 if residue

Exit codes:
    0  — no residue (clean refactor / path swap) for every file, OR informational
         run without --check.
    1  — with --check: at least one file has a non-empty residue.

Stdlib only. Python 3.11+.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

_LIB_PATH = Path(__file__).resolve().parents[2] / "hooks" / "normdiff_lib.py"


def _load_lib():
    spec = importlib.util.spec_from_file_location("normdiff_lib", _LIB_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {_LIB_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _repo_root() -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if out.returncode == 0:
            return Path(out.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return Path.cwd()


def _head_baseline(rel_path: str, root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "show", f"HEAD:{rel_path}"],
            cwd=str(root),
            capture_output=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if out.returncode != 0:
        return ""
    try:
        return out.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return ""


def _report(lib, file_path: str, root: Path) -> bool:
    """Print the residue for one file. Return True if residue is non-empty."""
    language = lib.language_for_path(file_path)
    if language is None:
        print(f"{file_path}: unsupported file type (skipped)")
        return False
    try:
        rel = str(Path(file_path).resolve().relative_to(root.resolve()))
    except (ValueError, OSError):
        rel = file_path
    current = lib.read_text_or_empty(file_path)
    baseline = _head_baseline(rel, root)
    diff = lib.normdiff(baseline, current, language)
    if lib.residue_is_empty(diff):
        print(f"{file_path}: NO RESIDUE (clean refactor / path swap)")
        return False
    print(f"{file_path}: RESIDUE — {lib.summarize_residue(diff)}")
    for ln in diff["added"]:
        print(f"  + {ln}")
    for ln in diff["removed"]:
        print(f"  - {ln}")
    return True


def main(argv: list[str]) -> int:
    check = "--check" in argv
    files = [a for a in argv if not a.startswith("-")]
    if not files:
        print(__doc__)
        return 0
    lib = _load_lib()
    root = _repo_root()
    any_residue = False
    for fp in files:
        if _report(lib, fp, root):
            any_residue = True
    if check and any_residue:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
