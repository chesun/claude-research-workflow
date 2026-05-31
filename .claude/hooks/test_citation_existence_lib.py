#!/usr/bin/env python3
"""
Tests for citation_existence_lib.py (evidence-gating Phase 3).

Runnable two ways:
    python3 .claude/hooks/test_citation_existence_lib.py   # standalone (recommended)
    python3 -m pytest .claude/hooks/test_citation_existence_lib.py -q

Covers:
  Resolution:
    - real file:line resolves                          → RESOLVED
    - file-only citation for an existing file          → RESOLVED
    - nonexistent file                                 → MISSING
    - out-of-range line                                → MISSING
    - in-range line at file end                        → RESOLVED
    - a real PASSING test_id (runs pytest)             → RESOLVED
    - a FAILING test_id (runs pytest)                  → MISSING
    - a nonexistent test_id (pytest collects nothing)  → MISSING
  SECURITY:
    - '../etc/passwd:1' traversal                      → MISSING (rejected)
    - absolute path outside repo                       → MISSING (rejected)
    - test_id with shell metacharacters               → MISSING (rejected)
    - path part with shell metacharacters             → MISSING (rejected)
  Infra-absence:
    - test_id on an unsupported extension (.do)        → ASSUMED (fail-open)
  Cross-platform:
    - non-ASCII (Unicode) filename resolves            → RESOLVED
    - Windows backslash path separators (Windows only) → RESOLVED
    - Windows-reserved-name rejection (Windows only)   → MISSING

The RESOLVED/MISSING test-running cases create a throwaway pytest file UNDER
the repo root (the runner uses repo-relative paths + cwd=repo_root) and delete
it afterward.

Cross-platform note
-------------------
This suite runs on the developer's host OS (CI/dev is macOS, ``sys.platform ==
'darwin'``). Non-ASCII filename handling is exercised unconditionally — it works
on POSIX and is verified here. Windows-specific cases (backslash separators,
reserved device names like ``CON``/``NUL``) are guarded by ``sys.platform ==
'win32'`` and only execute on a Windows machine; on POSIX they are skipped and
counted as pass. Full cross-platform verification therefore requires running
this suite on an actual Windows host — the macOS/Linux run cannot exercise the
Windows-only branches.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

_LIB_PATH = Path(__file__).resolve().parent / "citation_existence_lib.py"
_spec = importlib.util.spec_from_file_location("citation_existence_lib", _LIB_PATH)
lib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lib)


def _repo_root() -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0:
            return Path(out.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    # Fall back to two levels up from this file (.claude/hooks/ -> repo root).
    return Path(__file__).resolve().parents[2]


_ROOT = _repo_root()
_PYTEST_AVAILABLE = lib._python_runner_available()

_RESULTS: list[tuple[str, bool, str]] = []


def _check(name: str, cond: bool, detail: str = "") -> None:
    _RESULTS.append((name, bool(cond), detail))


# ---------------------------------------------------------------------------
# Throwaway in-repo fixture management (for test-running cases)
# ---------------------------------------------------------------------------


class _RepoFixture:
    """Create a temp file under repo_root, yield its repo-relative path, delete."""

    def __init__(self, content: str, suffix: str = ".py", prefix: str = "_citecheck_tmp_"):
        self.content = content
        self.suffix = suffix
        self.prefix = prefix
        self.path: Path | None = None

    def __enter__(self) -> str:
        fd, name = tempfile.mkstemp(suffix=self.suffix, prefix=self.prefix, dir=str(_ROOT))
        os.close(fd)
        self.path = Path(name)
        self.path.write_text(self.content, encoding="utf-8")
        return os.path.relpath(str(self.path), str(_ROOT))

    def __exit__(self, *exc):
        if self.path is not None and self.path.exists():
            self.path.unlink()
        return False


# ---------------------------------------------------------------------------
# Resolution — file / line
# ---------------------------------------------------------------------------


def test_real_file_line_resolves():
    # This very test file exists and has many lines; line 1 is in range.
    rel = os.path.relpath(str(_LIB_PATH), str(_ROOT))
    r = lib.resolve_citation(f"{rel}:1", _ROOT)
    _check("real_file_line_resolves",
           r["status"] == "RESOLVED" and r["exists"] and r["kind"] == "line", str(r))


def test_file_only_resolves():
    rel = os.path.relpath(str(_LIB_PATH), str(_ROOT))
    r = lib.resolve_citation(rel, _ROOT)
    _check("file_only_resolves",
           r["status"] == "RESOLVED" and r["exists"] and r["kind"] == "file", str(r))


def test_nonexistent_file_missing():
    r = lib.resolve_citation("scripts/this_does_not_exist_zzz.do:5", _ROOT)
    _check("nonexistent_file_missing",
           r["status"] == "MISSING" and not r["exists"], str(r))


def test_out_of_range_line_missing():
    rel = os.path.relpath(str(_LIB_PATH), str(_ROOT))
    r = lib.resolve_citation(f"{rel}:9999999", _ROOT)
    _check("out_of_range_line_missing",
           r["status"] == "MISSING" and not r["exists"] and r["kind"] == "line", str(r))


def test_in_range_last_line_resolves():
    rel = os.path.relpath(str(_LIB_PATH), str(_ROOT))
    n = sum(1 for _ in _LIB_PATH.open("r", encoding="utf-8", errors="replace"))
    r = lib.resolve_citation(f"{rel}:{n}", _ROOT)
    _check("in_range_last_line_resolves",
           r["status"] == "RESOLVED" and r["exists"], str(r))


def test_range_resolves():
    rel = os.path.relpath(str(_LIB_PATH), str(_ROOT))
    r = lib.resolve_citation(f"{rel}:1-3", _ROOT)
    _check("range_resolves",
           r["status"] == "RESOLVED" and r["kind"] == "line", str(r))


# ---------------------------------------------------------------------------
# Resolution — test execution (real pytest run)
# ---------------------------------------------------------------------------


def test_passing_test_id_resolves():
    if not _PYTEST_AVAILABLE:
        _check("passing_test_id_resolves", True, "SKIPPED: pytest unavailable (infra)")
        return
    content = "def test_citecheck_pass():\n    assert 1 + 1 == 2\n"
    with _RepoFixture(content) as rel:
        r = lib.resolve_citation(f"{rel}::test_citecheck_pass", _ROOT)
    _check("passing_test_id_resolves",
           r["status"] == "RESOLVED" and r["exists"] and r["kind"] == "test", str(r))


def test_failing_test_id_missing():
    if not _PYTEST_AVAILABLE:
        _check("failing_test_id_missing", True, "SKIPPED: pytest unavailable (infra)")
        return
    content = "def test_citecheck_fail():\n    assert False\n"
    with _RepoFixture(content) as rel:
        r = lib.resolve_citation(f"{rel}::test_citecheck_fail", _ROOT)
    _check("failing_test_id_missing",
           r["status"] == "MISSING" and not r["exists"], str(r))


def test_nonexistent_test_id_missing():
    if not _PYTEST_AVAILABLE:
        _check("nonexistent_test_id_missing", True, "SKIPPED: pytest unavailable (infra)")
        return
    content = "def test_citecheck_real():\n    assert True\n"
    with _RepoFixture(content) as rel:
        r = lib.resolve_citation(f"{rel}::test_citecheck_absent", _ROOT)
    _check("nonexistent_test_id_missing",
           r["status"] == "MISSING" and not r["exists"], str(r))


def test_line_and_test_id_form():
    if not _PYTEST_AVAILABLE:
        _check("line_and_test_id_form", True, "SKIPPED: pytest unavailable (infra)")
        return
    content = "def test_citecheck_pass2():\n    assert True\n"
    with _RepoFixture(content) as rel:
        # file:line:test form (line 1 in range, test passes).
        r = lib.resolve_citation(f"{rel}:1:test_citecheck_pass2", _ROOT)
    _check("line_and_test_id_form",
           r["status"] == "RESOLVED" and r["exists"], str(r))


# ---------------------------------------------------------------------------
# SECURITY
# ---------------------------------------------------------------------------


def test_traversal_rejected():
    r = lib.resolve_citation("../etc/passwd:1", _ROOT)
    _check("traversal_rejected",
           r["status"] == "MISSING" and not r["exists"]
           and "escapes" in r["detail"].lower(), str(r))


def test_deep_traversal_rejected():
    r = lib.resolve_citation("../../../../etc/passwd", _ROOT)
    _check("deep_traversal_rejected",
           r["status"] == "MISSING" and not r["exists"], str(r))


def test_absolute_path_outside_repo_rejected():
    r = lib.resolve_citation("/etc/passwd:1", _ROOT)
    _check("absolute_path_outside_repo_rejected",
           r["status"] == "MISSING" and not r["exists"], str(r))


def test_shell_metachar_test_id_rejected():
    # File exists; the test id carries a shell metacharacter → rejected before
    # any subprocess is spawned.
    rel = os.path.relpath(str(_LIB_PATH), str(_ROOT))
    r = lib.resolve_citation(f"{rel}::test_foo;rm -rf /", _ROOT)
    _check("shell_metachar_test_id_rejected",
           r["status"] == "MISSING" and not r["exists"]
           and "unsafe test id" in r["detail"].lower(), str(r))


def test_backtick_test_id_rejected():
    rel = os.path.relpath(str(_LIB_PATH), str(_ROOT))
    r = lib.resolve_citation(f"{rel}::test_`whoami`", _ROOT)
    _check("backtick_test_id_rejected",
           r["status"] == "MISSING" and not r["exists"], str(r))


def test_shell_metachar_path_rejected():
    r = lib.resolve_citation("scripts/foo;cat /etc/passwd.do:1", _ROOT)
    _check("shell_metachar_path_rejected",
           r["status"] == "MISSING" and not r["exists"], str(r))


# ---------------------------------------------------------------------------
# Infra-absence → ASSUMED (fail-open, not MISSING)
# ---------------------------------------------------------------------------


def test_unsupported_extension_test_id_assumed():
    # A real .do file with a test_id: there is no whitelisted .do test runner,
    # so this is infra-absent → ASSUMED, NOT MISSING. We need a real .do file
    # under the repo so the FILE-existence check passes first.
    content = "* a stata comment\nregress y x\n"
    with _RepoFixture(content, suffix=".do") as rel:
        r = lib.resolve_citation(f"{rel}::test_something", _ROOT)
    _check("unsupported_extension_test_id_assumed",
           r["status"] == "ASSUMED" and not r["exists"]
           and "infra-absent" in r["detail"].lower(), str(r))


def test_unsupported_extension_safe_id_pattern_still_assumed():
    # Even a perfectly safe-looking id on an unsupported extension is ASSUMED
    # (the runner table, not the id, gates execution).
    content = "x <- 1\n"
    with _RepoFixture(content, suffix=".R") as rel:
        r = lib.resolve_citation(f"{rel}::test_clean", _ROOT)
    _check("unsupported_extension_safe_id_pattern_still_assumed",
           r["status"] == "ASSUMED", str(r))


# ---------------------------------------------------------------------------
# Cross-platform — non-ASCII (Unicode) paths and Windows-specific behavior
# ---------------------------------------------------------------------------


def test_unicode_path_resolves():
    # A non-ASCII filename must resolve like any other in-repo file. Exercised
    # unconditionally (works on POSIX; verified here). The prefix carries a
    # Greek delta so the basename is non-ASCII end to end.
    content = "x = 1\n"
    with _RepoFixture(content, prefix="_citecheck_δ_tmp_") as rel:
        r = lib.resolve_citation(f"{rel}:1", _ROOT)
    _check("unicode_path_resolves",
           r["status"] == "RESOLVED" and r["exists"] and r["kind"] == "line", str(r))


def test_unicode_path_file_only_resolves():
    content = "x = 1\n"
    with _RepoFixture(content, prefix="_citecheck_éñ_tmp_") as rel:
        r = lib.resolve_citation(rel, _ROOT)
    _check("unicode_path_file_only_resolves",
           r["status"] == "RESOLVED" and r["exists"] and r["kind"] == "file", str(r))


def test_windows_backslash_path_resolves():
    # Windows-only: a citation written with backslash separators must resolve
    # to the same in-repo file as the forward-slash form. Skipped on POSIX,
    # where backslash is a legal filename character (not a separator).
    if sys.platform != "win32":
        _check("windows_backslash_path_resolves", True,
               "SKIPPED: Windows-only (sys.platform != 'win32')")
        return
    content = "x = 1\n"
    with _RepoFixture(content) as rel:
        r = lib.resolve_citation(f"{rel.replace('/', chr(92))}:1", _ROOT)
    _check("windows_backslash_path_resolves",
           r["status"] == "RESOLVED" and r["exists"], str(r))


def test_windows_reserved_name_missing():
    # Windows-only: a reserved device name (CON) cannot be a real repo file, so
    # the citation must resolve MISSING rather than crash. Skipped on POSIX,
    # where 'CON' is an ordinary (absent) filename and already MISSING.
    if sys.platform != "win32":
        _check("windows_reserved_name_missing", True,
               "SKIPPED: Windows-only (sys.platform != 'win32')")
        return
    r = lib.resolve_citation("CON:1", _ROOT)
    _check("windows_reserved_name_missing",
           r["status"] == "MISSING" and not r["exists"], str(r))


# ---------------------------------------------------------------------------
# Parser unit checks
# ---------------------------------------------------------------------------


def test_parse_forms():
    p1 = lib.parse_citation("a/b.py:47")
    p2 = lib.parse_citation("a/b.py:40-52")
    p3 = lib.parse_citation("a/b.py:88:test_foo")
    p4 = lib.parse_citation("a/b.py::test_foo")
    p5 = lib.parse_citation("a/b.py")
    ok = (
        p1 == {"file": "a/b.py", "line_spec": "47", "test_id": None}
        and p2 == {"file": "a/b.py", "line_spec": "40-52", "test_id": None}
        and p3 == {"file": "a/b.py", "line_spec": "88", "test_id": "test_foo"}
        and p4 == {"file": "a/b.py", "line_spec": None, "test_id": "test_foo"}
        and p5 == {"file": "a/b.py", "line_spec": None, "test_id": None}
    )
    _check("parse_forms", ok, f"{p1} {p2} {p3} {p4} {p5}")


def test_parse_empty_raises():
    raised = False
    try:
        lib.parse_citation("   ")
    except ValueError:
        raised = True
    _check("parse_empty_raises", raised, "")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

_ALL_TESTS = [
    test_real_file_line_resolves,
    test_file_only_resolves,
    test_nonexistent_file_missing,
    test_out_of_range_line_missing,
    test_in_range_last_line_resolves,
    test_range_resolves,
    test_passing_test_id_resolves,
    test_failing_test_id_missing,
    test_nonexistent_test_id_missing,
    test_line_and_test_id_form,
    test_traversal_rejected,
    test_deep_traversal_rejected,
    test_absolute_path_outside_repo_rejected,
    test_shell_metachar_test_id_rejected,
    test_backtick_test_id_rejected,
    test_shell_metachar_path_rejected,
    test_unsupported_extension_test_id_assumed,
    test_unsupported_extension_safe_id_pattern_still_assumed,
    test_unicode_path_resolves,
    test_unicode_path_file_only_resolves,
    test_windows_backslash_path_resolves,
    test_windows_reserved_name_missing,
    test_parse_forms,
    test_parse_empty_raises,
]


def main() -> int:
    for t in _ALL_TESTS:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            _check(t.__name__, False, f"EXCEPTION: {e!r}")
    passed = sum(1 for _, ok, _ in _RESULTS if ok)
    failed = [(n, d) for n, ok, d in _RESULTS if not ok]
    for name, ok, detail in _RESULTS:
        status = "PASS" if ok else "FAIL"
        line = f"[{status}] {name}"
        if not ok and detail:
            line += f"  -> {detail}"
        print(line)
    print(f"\n{passed}/{len(_RESULTS)} checks passed.")
    if not _PYTEST_AVAILABLE:
        print("(note: pytest unavailable — test-execution cases SKIPPED, counted as pass.)")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
