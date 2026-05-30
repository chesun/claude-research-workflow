#!/usr/bin/env python3
"""
Citation-existence library (evidence-gating Phase 3, Tier-2 enforcement).

Shared logic for the citation-existence check that makes a critic's
locatable-judgment verdict carry CITED, RESOLVABLE evidence. A Tier-2 verdict
("goal X achieved", "the refactor preserves behavior beyond what the
deterministic gate covers") must attach a structured
`{claim, artifact_citation, sufficiency_argument}`; this library mechanically
resolves the `artifact_citation` so a *fabricated* artifact (a line or test
that does not exist) is caught, even though the model still judges sufficiency.

Mirrors the style of `normdiff_lib.py` / `derive_lib.py`: stdlib-only,
fail-open at the caller's IO boundary, pure helpers that raise on genuinely
bad input. The one place this library does run a subprocess (a test) is locked
down hard — see SECURITY below.

Citation format
---------------
    file[:line-or-range][:test_id]

  - `scripts/01_clean.do:47`                — file + single line
  - `scripts/01_clean.do:40-52`             — file + inclusive line range
  - `tests/test_x.py:88:test_foo`           — file + line + test id
  - `tests/test_x.py::test_foo`             — file + test id (pytest-style ::)
  - `paper/main.tex`                        — file only (existence of file)

resolve_citation(citation, repo_root) -> dict
---------------------------------------------
Keys:
  - exists  (bool)  — True iff the cited artifact resolves (file present, line
                      in range, and — if a test is named — the test passed).
  - kind    (str)   — 'line' | 'test' | 'file'.
  - status  (str)   — 'RESOLVED' | 'MISSING' | 'ASSUMED'.
  - detail  (str)   — human-readable reason / evidence.

The MISSING-vs-ASSUMED rule (the load-bearing distinction):
  - MISSING  — a real fabrication signal: the FILE does not exist, the LINE /
               line-range is out of range, the named test FAILED, or the
               citation itself is malformed/unsafe. `exists` is False.
  - ASSUMED  — infrastructure absence ONLY: a test was named but the test
               runner / language toolchain for that file type is unavailable
               (e.g. pytest not installed, an unsupported extension with no
               whitelisted runner). This must NOT read as fabrication. `exists`
               is False (we could not confirm), but the row is recorded
               ASSUMED with the reason, not MISSING. Fail-open.
  - RESOLVED — the artifact resolves: file present, line in range, and any
               named test ran and passed. `exists` is True.

SECURITY (critical — read before editing)
------------------------------------------
A citation string is UNTRUSTED INPUT. It must NEVER become arbitrary command
execution or a path-traversal read. The defenses, in order:

  1. Path containment. The file part is resolved RELATIVE to repo_root and the
     result must stay inside repo_root. Any '..' traversal, absolute path, or
     symlink that escapes the tree is REJECTED → MISSING ("path escapes repo").
     We use os.path.realpath + commonpath, so a symlink pointing outside the
     repo is caught too.
  2. test_id whitelist. A test id must match a conservative identifier pattern
     (`[A-Za-z_][A-Za-z0-9_]*` plus pytest's `::` / `[param]` shapes, and `.`
     for class-qualified ids). Anything with a shell metacharacter, space,
     slash, or quote is REJECTED → MISSING ("unsafe test id"). The id is never
     interpolated into a shell string.
  3. Fixed, whitelisted runner. Tests run only via a per-extension runner from
     a hard-coded table (e.g. python -> ['python3','-m','pytest', ...]), with
     `shell=False`, an args LIST (never a command string), and `cwd=repo_root`.
     The citation never selects the program; the extension does. An extension
     with no entry in the table is ASSUMED (infra-absent), not executed.
  4. No shell, ever. subprocess is called with a list and shell=False. There
     is no code path that passes the citation to a shell.

Stdlib only. Python 3.11+.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# Citation parsing
# ---------------------------------------------------------------------------

# A safe test identifier: a function/method name, optionally class-qualified
# (Class.method or Class::method), optionally parametrized (test_foo[case-1]).
# Deliberately conservative: letters, digits, underscore, dot, and the pytest
# node separators `::` and `[...]`. NO slash, space, quote, or shell metachar.
_SAFE_TEST_ID = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*"
                           r"(?:(?:::|\.)[A-Za-z_][A-Za-z0-9_]*)*"
                           r"(?:\[[A-Za-z0-9_.\-]+\])?$")

# A line spec is a single int or an inclusive range `lo-hi` (both 1-based).
_LINE_SPEC = re.compile(r"^(\d+)(?:-(\d+))?$")

# Characters that should never appear in a citation we are willing to act on.
# (We reject early and explicitly rather than relying on later defenses alone.)
_SHELL_META = set(";|&$`<>(){}*?!\\\n\r\t'\"")


def parse_citation(citation: str) -> dict:
    """Split a raw citation into {file, line_spec, test_id} (strings or None).

    Accepts the documented forms. Does NOT validate existence or safety — that
    is resolve_citation's job. Raises ValueError on a citation that cannot be
    structurally parsed at all (empty / no file part).

    Disambiguation rules for the colon-delimited form `a:b:c`:
      - The first field is always the file.
      - `file::test`  (double colon) → pytest node form: test_id = the part
        after `::`, no line.
      - `file:line:test` → line spec then test id.
      - `file:X` where X parses as a line spec → line, no test.
      - `file:X` where X is NOT a line spec → treated as a test id (so
        `mod.py:test_foo` works), no line.
    """
    if citation is None:
        raise ValueError("empty citation")
    raw = citation.strip()
    if not raw:
        raise ValueError("empty citation")

    # Pytest node form: split on the FIRST '::' if present.
    test_id: str | None = None
    if "::" in raw:
        head, _, tail = raw.partition("::")
        test_id = tail.strip() or None
        raw = head

    parts = raw.split(":")
    file_part = parts[0].strip()
    if not file_part:
        raise ValueError("citation has no file part")

    line_spec: str | None = None
    if len(parts) >= 2 and parts[1].strip():
        cand = parts[1].strip()
        if _LINE_SPEC.match(cand):
            line_spec = cand
            # A third field after a line is a test id (file:line:test).
            if test_id is None and len(parts) >= 3 and parts[2].strip():
                test_id = parts[2].strip()
        else:
            # Not a line → treat as a test id (file:test), if none from '::'.
            if test_id is None:
                test_id = cand
    return {"file": file_part, "line_spec": line_spec, "test_id": test_id}


# ---------------------------------------------------------------------------
# Path containment (SECURITY defense 1)
# ---------------------------------------------------------------------------


def _resolve_within_repo(file_part: str, repo_root: Path) -> Path | None:
    """Resolve `file_part` relative to repo_root; return the realpath ONLY if
    it stays inside repo_root. Return None otherwise (escape / traversal).

    Rejects absolute paths outright (a citation must be repo-relative). Uses
    realpath + commonpath so that a symlink pointing outside the tree is also
    caught.
    """
    if os.path.isabs(file_part):
        return None
    # Reject obvious shell metacharacters in the path component.
    if any(ch in _SHELL_META for ch in file_part):
        return None
    root_real = Path(os.path.realpath(repo_root))
    candidate = (root_real / file_part)
    cand_real = Path(os.path.realpath(candidate))
    try:
        common = os.path.commonpath([str(root_real), str(cand_real)])
    except ValueError:
        # Different drives (Windows) or otherwise incomparable.
        return None
    if common != str(root_real):
        return None
    return cand_real


# ---------------------------------------------------------------------------
# Test runner whitelist (SECURITY defenses 2 + 3)
# ---------------------------------------------------------------------------


def _runner_for_extension(suffix: str):
    """Return a callable (relpath, test_id, repo_root) -> argv list for the
    given file extension, or None if no whitelisted runner exists.

    The extension — NOT the citation — selects the program. Returning None
    means "infra-absent for this file type" and the caller records ASSUMED.
    """
    suffix = suffix.lower()
    if suffix == ".py":
        def _py(relpath: str, test_id: str, repo_root: Path) -> list[str]:
            # pytest node id: `<relpath>::<test_id>`. test_id already passed
            # the _SAFE_TEST_ID whitelist; it is an argv element, never shell.
            node = f"{relpath}::{test_id}"
            return ["python3", "-m", "pytest", "-q", "-x", node]
        return _py
    # No whitelisted runner for other extensions (Stata/R/LaTeX test execution
    # is out of scope for Phase 3). Treated as infra-absent → ASSUMED.
    return None


def _python_runner_available() -> bool:
    """True iff python3 + pytest appear runnable. Used to distinguish a real
    test FAIL from infra-absence (pytest not installed → ASSUMED)."""
    if shutil.which("python3") is None and shutil.which("python") is None:
        return False
    try:
        import importlib.util

        return importlib.util.find_spec("pytest") is not None
    except (ImportError, ValueError):
        return False


def _run_test(relpath: str, test_id: str, repo_root: Path, suffix: str) -> dict:
    """Run the named test via the whitelisted runner. Return a partial dict
    {status, detail}. status ∈ {RESOLVED, MISSING, ASSUMED}.

    - No runner for the extension → ASSUMED (infra-absent).
    - Runner present but toolchain missing (pytest absent) → ASSUMED.
    - Test ran and passed → RESOLVED.
    - Test ran and failed → MISSING (real fabrication / broken-evidence signal).
    - Runner crashed / could not be spawned → ASSUMED (fail-open, not MISSING).
    """
    runner = _runner_for_extension(suffix)
    if runner is None:
        return {
            "status": "ASSUMED",
            "detail": f"no whitelisted test runner for '{suffix}' (infra-absent)",
        }
    if suffix.lower() == ".py" and not _python_runner_available():
        return {
            "status": "ASSUMED",
            "detail": "pytest/python toolchain unavailable (infra-absent)",
        }
    argv = runner(relpath, test_id, repo_root)
    try:
        proc = subprocess.run(  # noqa: S603 — fixed argv, shell=False, cwd pinned
            argv,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=120,
            shell=False,
        )
    except FileNotFoundError:
        return {"status": "ASSUMED", "detail": "test runner not found (infra-absent)"}
    except (OSError, subprocess.SubprocessError) as exc:
        # Fail-open on spawn/timeout errors → ASSUMED, never MISSING.
        return {"status": "ASSUMED", "detail": f"test runner error: {exc!r} (infra-absent)"}
    if proc.returncode == 0:
        return {"status": "RESOLVED", "detail": f"test '{test_id}' passed"}
    # pytest exit 5 = "no tests collected" → the named test does not exist:
    # that IS a fabrication signal (MISSING). All other nonzero = test failed.
    if proc.returncode == 5:
        return {"status": "MISSING", "detail": f"test '{test_id}' not collected (does not exist)"}
    tail = (proc.stdout or proc.stderr or "").strip().splitlines()
    last = tail[-1] if tail else f"exit {proc.returncode}"
    return {"status": "MISSING", "detail": f"test '{test_id}' failed: {last}"}


# ---------------------------------------------------------------------------
# The public entry point
# ---------------------------------------------------------------------------


def resolve_citation(citation: str, repo_root: str | Path) -> dict:
    """Resolve a `file[:line-or-range][:test_id]` citation against repo_root.

    Returns {exists, kind, status, detail} — see module docstring for the
    contract and the MISSING-vs-ASSUMED rule. Never raises on a well-formed
    string; a structurally un-parseable citation is reported as MISSING
    ("malformed citation"), not an exception, so callers can treat the result
    uniformly.
    """
    repo_root = Path(repo_root)

    try:
        parsed = parse_citation(citation)
    except ValueError as exc:
        return {"exists": False, "kind": "file", "status": "MISSING",
                "detail": f"malformed citation: {exc}"}

    file_part = parsed["file"]
    line_spec = parsed["line_spec"]
    test_id = parsed["test_id"]

    # --- SECURITY defense 1: path containment -----------------------------
    resolved = _resolve_within_repo(file_part, repo_root)
    if resolved is None:
        return {"exists": False, "kind": "file", "status": "MISSING",
                "detail": f"path escapes repo or is unsafe: {file_part!r}"}

    # --- File existence ----------------------------------------------------
    if not resolved.is_file():
        return {"exists": False, "kind": "file", "status": "MISSING",
                "detail": f"file does not exist: {file_part}"}

    relpath = os.path.relpath(str(resolved), str(Path(os.path.realpath(repo_root))))

    # --- Line / line-range existence --------------------------------------
    if line_spec is not None:
        m = _LINE_SPEC.match(line_spec)
        # parse_citation guarantees a match, but guard defensively.
        if m is None:
            return {"exists": False, "kind": "line", "status": "MISSING",
                    "detail": f"malformed line spec: {line_spec!r}"}
        lo = int(m.group(1))
        hi = int(m.group(2)) if m.group(2) else lo
        if lo < 1 or hi < lo:
            return {"exists": False, "kind": "line", "status": "MISSING",
                    "detail": f"invalid line range: {line_spec}"}
        try:
            n_lines = sum(1 for _ in resolved.open("r", encoding="utf-8", errors="replace"))
        except OSError as exc:
            # Fail-open on read error → ASSUMED (we couldn't check), not MISSING.
            return {"exists": False, "kind": "line", "status": "ASSUMED",
                    "detail": f"could not read file to check line range: {exc!r}"}
        if hi > n_lines:
            return {"exists": False, "kind": "line", "status": "MISSING",
                    "detail": f"line {hi} out of range (file has {n_lines} lines)"}

    # --- Test id (whitelist + run) ----------------------------------------
    if test_id is not None:
        # SECURITY defense 2: whitelist the test id BEFORE it touches argv.
        if not _SAFE_TEST_ID.match(test_id):
            return {"exists": False, "kind": "test", "status": "MISSING",
                    "detail": f"unsafe test id rejected: {test_id!r}"}
        run = _run_test(relpath, test_id, Path(os.path.realpath(repo_root)),
                        resolved.suffix)
        status = run["status"]
        line_note = f" (line {line_spec} in range)" if line_spec else ""
        return {
            "exists": status == "RESOLVED",
            "kind": "test",
            "status": status,
            "detail": run["detail"] + line_note,
        }

    # --- No test: resolution is file (+ line) existence -------------------
    if line_spec is not None:
        return {"exists": True, "kind": "line", "status": "RESOLVED",
                "detail": f"{relpath}:{line_spec} resolves (line(s) in range)"}
    return {"exists": True, "kind": "file", "status": "RESOLVED",
            "detail": f"{relpath} exists"}


def summarize(result: dict) -> str:
    """One-line summary for a ledger Evidence cell / CLI output."""
    return f"{result['status']} ({result['kind']}): {result['detail']}"
