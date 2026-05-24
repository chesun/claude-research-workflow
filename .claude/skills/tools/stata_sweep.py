#!/usr/bin/env python3
"""
stata_sweep — detect and fix the Stata greedy-`/*` parser bug across a
codebase.

Background: `master_supporting_docs/stata-block-comment-bug-field-guide.md`
(8-variant taxonomy). Shared state-machine logic lives in
`.claude/hooks/stata_comment_lib.py` and is reused by the PreToolUse hook
`.claude/hooks/stata-comment-balance-check.py`.

Usage:

    python3 .claude/skills/tools/stata_sweep.py [--check | --fix]
        [--root PATH] [--exclude PATTERN ...] [--diff] [--json]
        [FILE ...]

Modes:
    --check    No-fix mode (default). Walks the tree, classifies each
               .do/.doh file, reports counts. Exit code reflects worst
               class found.
    --fix      Mutates AUTO-FIXABLE files in place. MANUAL-ATTENTION
               files are reported but NEVER mutated (sweep cannot
               produce a balanced post-state; user must investigate).

Exit codes:
    0  All files CLEAN.
    1  At least one AUTO-FIXABLE file found (--check) or fixed (--fix).
    2  At least one MANUAL-ATTENTION file found (V8 corruption or
       missing-close `/*`). Subsumes 1.
    3  Parse / IO error.

Reads `.do` and `.doh` files. Excludes `_archive` by default.

Stdlib only. Python 3.11+.
"""

from __future__ import annotations

import argparse
import fnmatch
import importlib.util
import json
import sys
from pathlib import Path
from typing import Iterable


def _load_lib():
    """Load stata_comment_lib from .claude/hooks/ relative to this script."""
    script_dir = Path(__file__).resolve().parent
    # script_dir is .claude/skills/tools/ — go up to .claude/, then into hooks/
    lib_path = script_dir.parent.parent / "hooks" / "stata_comment_lib.py"
    spec = importlib.util.spec_from_file_location("stata_comment_lib", lib_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {lib_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _iter_targets(
    root: Path,
    explicit_files: list[Path],
    excludes: list[str],
) -> Iterable[Path]:
    """Yield .do/.doh files under root, or the explicit files if provided."""
    if explicit_files:
        for p in explicit_files:
            if p.is_file() and p.suffix in (".do", ".doh"):
                yield p
        return
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in (".do", ".doh"):
            continue
        rel = path.relative_to(root)
        if any(fnmatch.fnmatch(str(rel), pat) or pat in rel.parts for pat in excludes):
            continue
        yield path


def _print_diff(before: str, after: str, label: str) -> None:
    """Compact unified-diff style printout."""
    import difflib

    diff = difflib.unified_diff(
        before.splitlines(keepends=True),
        after.splitlines(keepends=True),
        fromfile=f"a/{label}",
        tofile=f"b/{label}",
        n=2,
    )
    sys.stdout.write("".join(diff))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stata_sweep",
        description="Detect and fix the Stata greedy-/* parser bug.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="No-fix mode (default). Classify and report.",
    )
    mode.add_argument(
        "--fix",
        action="store_true",
        help="Mutate AUTO-FIXABLE files in place. MANUAL-ATTENTION files are skipped.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root to walk (default: cwd).",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=["_archive", ".claude"],
        help=(
            "Path component to exclude (repeatable; defaults: _archive, "
            ".claude). The .claude default skips workflow infrastructure "
            "including test fixtures that are intentionally buggy."
        ),
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Print unified diff for each AUTO-FIXABLE file (--fix mode only).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON summary instead of text.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Specific files to process (overrides --root walk).",
    )
    args = parser.parse_args(argv)

    if not args.fix and not args.check:
        args.check = True  # default

    try:
        lib = _load_lib()
    except Exception as exc:
        print(f"stata_sweep: cannot load library: {exc}", file=sys.stderr)
        return 3

    root = args.root.resolve()
    if not root.is_dir() and not args.files:
        print(f"stata_sweep: root not a directory: {root}", file=sys.stderr)
        return 3

    targets = list(_iter_targets(root, args.files, args.exclude))

    clean_paths: list[Path] = []
    auto_fixable: list[tuple[Path, dict, str, str]] = []  # (path, info, before, after)
    manual_attention: list[tuple[Path, list[tuple[int, str]] | None]] = []  # (path, v8_hits)
    errors: list[tuple[Path, str]] = []

    for path in targets:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append((path, str(exc)))
            continue

        try:
            klass = lib.classify_file(text)
        except Exception as exc:
            errors.append((path, f"classify_file: {exc}"))
            continue

        if klass == "clean":
            clean_paths.append(path)
            continue

        if klass == "manual-attention":
            v8 = lib.find_over_flatten_artifacts(text)
            manual_attention.append((path, v8 if v8 else None))
            continue

        # auto-fixable
        try:
            swept, info = lib.sweep_text(text)
        except Exception as exc:
            errors.append((path, f"sweep_text: {exc}"))
            continue
        auto_fixable.append((path, info, text, swept))

    # Apply --fix mutations.
    fixed_count = 0
    if args.fix:
        for path, _info, _before, after in auto_fixable:
            try:
                path.write_text(after, encoding="utf-8")
                fixed_count += 1
            except OSError as exc:
                errors.append((path, f"write: {exc}"))

    # Determine exit code.
    if errors:
        exit_code = 3
    elif manual_attention:
        exit_code = 2
    elif auto_fixable:
        exit_code = 1
    else:
        exit_code = 0

    # Report.
    if args.json:
        out = {
            "mode": "fix" if args.fix else "check",
            "root": str(root),
            "scanned": len(targets),
            "clean": [str(p.relative_to(root)) for p in clean_paths],
            "auto_fixable": [
                {"path": str(p.relative_to(root)), "info": info}
                for p, info, _b, _a in auto_fixable
            ],
            "manual_attention": [
                {
                    "path": str(p.relative_to(root)),
                    "v8_artifacts": v8 or [],
                }
                for p, v8 in manual_attention
            ],
            "errors": [{"path": str(p.relative_to(root)), "error": e} for p, e in errors],
            "fixed": fixed_count,
            "exit_code": exit_code,
        }
        print(json.dumps(out, indent=2))
        return exit_code

    # Text report.
    mode_label = "FIX" if args.fix else "CHECK"
    print(f"stata_sweep ({mode_label}) — root: {root}")
    print(f"scanned: {len(targets)} files")
    print()

    if auto_fixable:
        verb = "FIXED" if args.fix else "AUTO-FIXABLE"
        print(f"{verb} ({len(auto_fixable)}):")
        for path, info, before, after in auto_fixable:
            rel = path.relative_to(root)
            detail = []
            if info["n_pre"]:
                detail.append(f"V4 flatten={info['n_pre']}")
            if info["n_real"]:
                detail.append(f"path-glob={info['n_real']}")
            if info["n_orphans"]:
                detail.append(f"V5 orphan={info['n_orphans']}")
            if info["n_v7"]:
                detail.append(f"V7 banner={info['n_v7']}")
            print(f"  {rel}  ({', '.join(detail) or 'cosmetic'})")
            if args.diff and args.fix:
                _print_diff(before, after, str(rel))
        print()

    if manual_attention:
        print(f"MANUAL-ATTENTION ({len(manual_attention)}):")
        print(
            "  Sweep cannot safely auto-fix these files (Variant 8 corruption "
            "OR missing-close `/*`).\n"
            "  Investigate before editing."
        )
        for path, v8 in manual_attention:
            rel = path.relative_to(root)
            if v8:
                print(f"  {rel}  (V8 artifacts:)")
                for line_no, line_text in v8[:5]:
                    print(f"    line {line_no}: {line_text}")
                if len(v8) > 5:
                    print(f"    ... +{len(v8) - 5} more")
            else:
                print(f"  {rel}  (unmatched `/*` open — missing close)")
        print()

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for path, err in errors:
            rel = path.relative_to(root) if path.is_absolute() else path
            print(f"  {rel}: {err}")
        print()

    print(f"clean: {len(clean_paths)} | auto-fixable: {len(auto_fixable)} | manual-attention: {len(manual_attention)} | errors: {len(errors)}")
    print(f"exit code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
