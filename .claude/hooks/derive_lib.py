#!/usr/bin/env python3
"""
Derive-Don't-Guess detection library.

Shared logic for the derive-dont-guess hooks (advisory PostToolUse and the
opt-in blocking PreToolUse). Enforces the mechanically-detectable proxy for
the rule in `.claude/rules/derive-dont-guess.md`: a *newly-referenced
read/input path* in an analysis/paper file should resolve on disk (or via a
repo-defined macro). A path that resolves to nothing — and a Stata macro
that is defined nowhere in the repo — is the strongest available signal that
the entity was guessed rather than derived.

What this CANNOT catch (documented honestly, mirrors the rule's "why it's
hard to hook" reasoning): a lucky guess that happens to resolve is
byte-identical to a real derivation; variable names / function signatures
have no on-disk anchor; runtime-constructed paths can't be statically
resolved. We deliberately only flag the high-confidence case and stay silent
everywhere else, so the advisory is near-zero false-positive.

Design notes:
  - Only READ/INPUT verbs are matched. Write/output targets (save, export,
    ggsave, esttab using, ...) are never matched, so non-existent output
    paths — which are legitimate and routine — never warn.
  - Macro-bearing Stata paths ($g, `l') are resolvable-via-macro when the
    macro is defined anywhere in the repo; flagged only when the macro is
    undefined repo-wide.
  - Escape hatch: a `derive-ok` comment in the edit delta suppresses
    warnings (bare = suppress all; `derive-ok: a.dta, b.csv` = suppress those).

Built for reuse: the delta-reconstruction, language detection, and escape
-hatch helpers are generic enough that future no-assumptions / adversarial
hooks can import them.

Fail-open is the caller's responsibility; this library raises on bad input
so callers can wrap in try/except and exit 0.
"""

from __future__ import annotations

import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

_SUFFIX_LANG = {
    ".do": "stata",
    ".doh": "stata",
    ".r": "r",
    ".R": "r",
    ".py": "python",
    ".tex": "latex",
}

# Suffixes this library acts on (the hook's file-type filter).
ENFORCEABLE_SUFFIXES = tuple(_SUFFIX_LANG.keys())


def language_for_path(file_path: str) -> str | None:
    """Return the language slug for a path, or None if not an analysis/paper file.

    Suffix match is case-sensitive for `.R` vs `.r` (both map to "r"); we test
    the raw suffix first, then a lowercased fallback for `.DO` etc.
    """
    suffix = Path(file_path).suffix
    if suffix in _SUFFIX_LANG:
        return _SUFFIX_LANG[suffix]
    return _SUFFIX_LANG.get(suffix.lower())


# ---------------------------------------------------------------------------
# Delta reconstruction (what text did this edit ADD?)
# ---------------------------------------------------------------------------


def reconstruct_delta(tool_name: str, tool_input: dict) -> str:
    """Return the text newly introduced by an Edit/Write/MultiEdit call.

    We scan only the added text (not the whole file) so we warn on
    newly-introduced references, not pre-existing ones the agent didn't touch.
    """
    if tool_name == "Write":
        return tool_input.get("content", "") or ""
    if tool_name == "Edit":
        return tool_input.get("new_string", "") or ""
    if tool_name == "MultiEdit":
        edits = tool_input.get("edits", []) or []
        parts = [e.get("new_string", "") or "" for e in edits if isinstance(e, dict)]
        return "\n".join(parts)
    return ""


# ---------------------------------------------------------------------------
# Escape hatch
# ---------------------------------------------------------------------------

# Matches `derive-ok` in any comment form (<!-- -->, *, //, #) with an
# optional comma list of path substrings. Non-greedy capture, terminated by an
# HTML-comment close (`-->`) or end of line so a bare `<!-- derive-ok -->`
# yields an empty (suppress-all) capture rather than swallowing the `--`.
_ESCAPE_RE = re.compile(
    r"derive-ok\s*:?\s*(.*?)\s*(?:-->|$)",
    re.IGNORECASE | re.MULTILINE,
)


def escape_hatch(delta: str) -> tuple[bool, set[str]]:
    """Detect a derive-ok escape comment in the delta.

    Returns (present, substrings). If present with no substrings, ALL warnings
    in this delta are suppressed. If present with a comma list, only paths
    containing one of those substrings are suppressed.
    """
    m = _ESCAPE_RE.search(delta)
    if not m:
        return (False, set())
    raw = m.group(1).strip()
    if not raw:
        return (True, set())
    subs = {s.strip() for s in raw.split(",") if s.strip()}
    return (True, subs)


# ---------------------------------------------------------------------------
# Read/input path extraction (per language)
# ---------------------------------------------------------------------------

# Each pattern captures the path in group 1. ONLY read/input verbs appear here;
# write/output verbs are intentionally absent so output paths never warn.

_STATA_PATTERNS = [
    # use "file.dta" [, clear]  /  use var using "file.dta"
    re.compile(r'\buse\s+(?:[^"\n]*?\busing\s+)?"([^"]+)"', re.IGNORECASE),
    # merge ... using "file"  /  append using "file"  /  joinby ... using "file"
    re.compile(r'\b(?:merge|append|joinby|cross|mmerge)\b[^"\n]*?\busing\s+"([^"]+)"', re.IGNORECASE),
    # import delimited/excel/sas/spss "file"  /  import delimited using "file"
    re.compile(r'\bimport\s+\w+\s+(?:[^"\n]*?\busing\s+)?"([^"]+)"', re.IGNORECASE),
    # infile / insheet using "file"
    re.compile(r'\b(?:infile|insheet|infix)\b[^"\n]*?\busing\s+"([^"]+)"', re.IGNORECASE),
    # include path.doh  /  do path.do  (unquoted or quoted).
    # Extension alternation is longest-first so .doh isn't truncated to .do.
    re.compile(r'\b(?:include|do)\s+"?([^\s",\n]+\.(?:doh|ado|do))"?', re.IGNORECASE),
]

_R_PATTERNS = [
    # read_csv("f") / read_dta / readRDS / read_rds / read.csv / read.dta / fread / read_excel / read_parquet
    re.compile(r'\b(?:read_csv|read_csv2|read_dta|read_rds|readRDS|read\.csv|read\.dta|read\.table|fread|read_excel|read_parquet|read_sas|read_sav|import|vroom)\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE),
    # source("file.R")
    re.compile(r'\bsource\s*\(\s*["\']([^"\']+)["\']'),
    # load("file.RData")
    re.compile(r'\bload\s*\(\s*["\']([^"\']+)["\']'),
]

_PYTHON_PATTERNS = [
    # pd.read_csv("f") / read_stata / read_excel / read_parquet / read_pickle / read_table
    re.compile(r'\.read_\w+\s*\(\s*["\']([^"\']+)["\']'),
    # np.load("f")
    re.compile(r'\bnp\.load\s*\(\s*["\']([^"\']+)["\']'),
    # open("f")  or  open("f", "r")  — read mode only (no 'w'/'a'/'x')
    re.compile(r'\bopen\s*\(\s*["\']([^"\']+)["\']\s*(?:,\s*["\'][rb+]+["\'])?\s*\)'),
]

_LATEX_PATTERNS = [
    re.compile(r'\\input\s*\{([^}]+)\}'),
    re.compile(r'\\include\s*\{([^}]+)\}'),
    re.compile(r'\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}'),
    re.compile(r'\\addbibresource\s*\{([^}]+)\}'),
    re.compile(r'\\bibliography\s*\{([^}]+)\}'),
]

_PATTERNS_BY_LANG = {
    "stata": _STATA_PATTERNS,
    "r": _R_PATTERNS,
    "python": _PYTHON_PATTERNS,
    "latex": _LATEX_PATTERNS,
}


def extract_read_paths(delta: str, language: str) -> list[str]:
    """Return de-duplicated read/input path-literals introduced in the delta."""
    patterns = _PATTERNS_BY_LANG.get(language, [])
    found: list[str] = []
    seen: set[str] = set()
    for pat in patterns:
        for m in pat.finditer(delta):
            p = m.group(1).strip()
            if p and p not in seen:
                seen.add(p)
                found.append(p)
    return found


# ---------------------------------------------------------------------------
# Stata macro detection
# ---------------------------------------------------------------------------

# $name, ${name}, `name'  — macro references inside a path string.
_MACRO_REF_RE = re.compile(r"\$\{?(\w+)\}?|`(\w+)'")

_MACRO_DEF_RE = re.compile(
    r"\b(?:global|local|tempfile|scalar)\s+(\w+)", re.IGNORECASE
)

# Don't walk pathological trees; advisory hook must stay fast. Fail-open above this.
_MAX_DO_FILES = 2000


def macro_refs(path: str) -> list[str]:
    """Return macro names referenced in a Stata path string."""
    names: list[str] = []
    for m in _MACRO_REF_RE.finditer(path):
        name = m.group(1) or m.group(2)
        if name:
            names.append(name)
    return names


def repo_defined_macros(project_root: Path) -> set[str]:
    """Set of macro names defined anywhere in the repo's .do/.doh files.

    Walks .do/.doh files and collects global/local/tempfile/scalar names.
    Bounded by _MAX_DO_FILES; returns what it found (fail-soft).
    """
    defined: set[str] = set()
    count = 0
    for pattern in ("*.do", "*.doh"):
        for f in project_root.rglob(pattern):
            count += 1
            if count > _MAX_DO_FILES:
                return defined
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for m in _MACRO_DEF_RE.finditer(text):
                defined.add(m.group(1))
    return defined


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

# LaTeX paths frequently omit the extension; try these in resolution.
_LATEX_EXT_CANDIDATES = (".tex", ".pdf", ".png", ".jpg", ".jpeg", ".eps", ".bib")


def _exists_with_glob(candidate: Path) -> bool:
    """True if the candidate exists or, when it contains a wildcard, matches anything."""
    raw = str(candidate)
    if any(ch in raw for ch in "*?[]"):
        try:
            # glob is relative to the candidate's anchor; use parent.glob on the name pattern
            parent = candidate.parent
            return parent.is_dir() and any(parent.glob(candidate.name))
        except (OSError, ValueError):
            return False
    return candidate.exists()


def resolve_path(
    path: str,
    project_root: Path,
    language: str,
    defined_macros: set[str] | None = None,
) -> tuple[bool, str]:
    """Decide whether a referenced read path is resolvable.

    Returns (resolvable, reason). `reason` is only meaningful when not
    resolvable. `defined_macros` is the repo macro set (Stata only); pass it
    in so callers can compute it once per invocation.
    """
    raw = path.strip()
    if not raw:
        return (True, "")

    # Stata macro handling.
    if language == "stata":
        refs = macro_refs(raw)
        if refs:
            macros = defined_macros if defined_macros is not None else set()
            undefined = [r for r in refs if r not in macros]
            if undefined:
                return (False, f"references undefined Stata macro(s): {', '.join('$' + u for u in undefined)}")
            # All macros are defined somewhere — can't statically expand; trust it.
            return (True, "")

    # Absolute / home paths: check directly (also a hardcoded-path smell, but
    # not this hook's job to flag that — only resolvability).
    expanded = Path(raw).expanduser()
    if expanded.is_absolute():
        return (True, "") if _exists_with_glob(expanded) else (False, "absolute path not found on disk")

    # Relative path: resolve against project root.
    rel = raw[2:] if raw.startswith("./") else raw
    base = project_root / rel

    candidates = [base]
    # LaTeX: try common extensions when none given.
    if language == "latex" and not Path(rel).suffix:
        candidates += [project_root / (rel + ext) for ext in _LATEX_EXT_CANDIDATES]

    for cand in candidates:
        if _exists_with_glob(cand):
            return (True, "")

    return (False, "path not found on disk")


# ---------------------------------------------------------------------------
# Top-level analysis
# ---------------------------------------------------------------------------


def _scan_text(
    text: str, language: str, project_root: Path
) -> list[tuple[str, str]]:
    """Core scan: extract read paths from `text` and return the unresolved ones.

    Shared by analyze() (scans an edit delta) and scan_file() (scans whole-file
    content for the /commit pre-flight). Respects the derive-ok escape hatch.
    """
    if not text.strip():
        return []

    escaped_all, escaped_subs = escape_hatch(text)
    if escaped_all and not escaped_subs:
        return []

    paths = extract_read_paths(text, language)
    if not paths:
        return []

    # Compute the repo macro set once, only if a Stata macro path appears.
    defined_macros: set[str] | None = None
    if language == "stata" and any(macro_refs(p) for p in paths):
        try:
            defined_macros = repo_defined_macros(project_root)
        except Exception:
            defined_macros = set()

    unresolved: list[tuple[str, str]] = []
    for p in paths:
        if escaped_subs and any(sub in p for sub in escaped_subs):
            continue
        ok, reason = resolve_path(p, project_root, language, defined_macros)
        if not ok:
            unresolved.append((p, reason))
    return unresolved


def analyze(
    tool_name: str,
    tool_input: dict,
    file_path: str,
    project_root: Path,
) -> list[tuple[str, str]]:
    """Return [(path, reason), ...] for newly-referenced read paths that don't resolve.

    Empty list means nothing to warn about. Respects the derive-ok escape
    hatch. The caller decides whether to advise (PostToolUse) or block
    (PreToolUse opt-in). Scans the edit DELTA (newly-added text only).
    """
    language = language_for_path(file_path)
    if language is None:
        return []
    return _scan_text(reconstruct_delta(tool_name, tool_input), language, project_root)


def scan_file(file_path: str, project_root: Path) -> list[tuple[str, str]]:
    """Scan a whole file's current content (used by the /commit pre-flight CLI)."""
    language = language_for_path(file_path)
    if language is None:
        return []
    try:
        text = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    return _scan_text(text, language, project_root)


def build_advisory_message(file_path: str, unresolved: list[tuple[str, str]]) -> str:
    """Human-readable advisory for the additionalContext injection."""
    lines = [
        "DERIVE-DON'T-GUESS — unresolved reference(s) just written to "
        f"{file_path}:",
        "",
    ]
    for p, reason in unresolved:
        lines.append(f"  • {p}  ({reason})")
    lines += [
        "",
        "Per .claude/rules/derive-dont-guess.md: a read/input path that does "
        "not resolve is the signature of a guessed entity. Before relying on "
        "it, DERIVE the real value — grep settings (`global`/`local`), the "
        "master script, or an existing loader — and cite the source line. If "
        "the path is intentionally new or built at runtime, disclose it or add "
        "`derive-ok: <path>` to the edit to silence this notice.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI — `python3 derive_lib.py --check <file>...` for the /commit pre-flight
# ---------------------------------------------------------------------------


def _cli(argv: list[str]) -> int:
    """Scan the given files; print unresolved read paths; exit 1 if any found."""
    import os

    files = [a for a in argv if a != "--check"]
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    found = False
    for fp in files:
        for path, reason in scan_file(fp, root):
            found = True
            print(f"{fp}: {path}  ({reason})")
    if found:
        print(
            "\nderive-dont-guess: unresolved read path(s) above. Derive the real "
            "value or add a `derive-ok` comment. See .claude/rules/derive-dont-guess.md."
        )
    return 1 if found else 0


if __name__ == "__main__":
    import sys

    raise SystemExit(_cli(sys.argv[1:]))
