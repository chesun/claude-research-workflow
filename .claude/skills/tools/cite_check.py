#!/usr/bin/env python3
"""
cite-check CLI — resolve a Tier-2 evidence citation (evidence-gating Phase 3).

Thin wrapper over `.claude/hooks/citation_existence_lib.py`. Given an
`artifact_citation` of form `file[:line-or-range][:test_id]`, mechanically
confirms the cited artifact RESOLVES: the file exists, any cited line / range
is within the file, and any named test runs and passes. This is the
existence-check half of Tier-2 enforcement — the critic still judges
*sufficiency*; this catches a *fabricated* artifact.

Usage:
    python3 .claude/skills/tools/cite_check.py <citation> [<citation> ...]

Examples:
    python3 .claude/skills/tools/cite_check.py scripts/01_clean.do:47
    python3 .claude/skills/tools/cite_check.py scripts/01_clean.do:40-52
    python3 .claude/skills/tools/cite_check.py tests/test_x.py:88:test_foo

Exit codes:
    0  — RESOLVED for every citation (artifacts exist; named tests pass), OR
         ASSUMED (infra unavailable — fail-open, with a printed note).
    1  — at least one citation is MISSING (file/line absent or test failed) —
         a real fabrication / broken-evidence signal.

Stdlib only. Python 3.11+.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

_LIB_PATH = Path(__file__).resolve().parents[2] / "hooks" / "citation_existence_lib.py"


def _load_lib():
    spec = importlib.util.spec_from_file_location("citation_existence_lib", _LIB_PATH)
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


def main(argv: list[str]) -> int:
    citations = [a for a in argv if not a.startswith("-")]
    if not citations:
        print(__doc__)
        return 0
    lib = _load_lib()
    root = _repo_root()
    any_missing = False
    any_assumed = False
    for cit in citations:
        result = lib.resolve_citation(cit, root)
        print(f"{cit}: {lib.summarize(result)}")
        if result["status"] == "MISSING":
            any_missing = True
        elif result["status"] == "ASSUMED":
            any_assumed = True
    if any_assumed and not any_missing:
        print("note: one or more citations ASSUMED (infra unavailable) — fail-open, exit 0.")
    return 1 if any_missing else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
