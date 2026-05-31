#!/usr/bin/env python3
"""
Normalized-content diff library (evidence-gating Phase 1).

Shared logic for the always-on evidence recorder
(`.claude/hooks/evidence-gate-recorder.py`) and the manual CLI
(`.claude/skills/tools/normdiff.py`). It answers one question: beyond pure
path swaps, comment edits, blank-line churn, and scaffold lines, did this
edit change the *substantive content* of an analysis/paper artifact?

The output is the "residue" — the set of normalized content lines that were
added or removed relative to a baseline (typically `git show HEAD:<path>`).
An empty residue means "no logic change" (a clean refactor / path swap); a
non-empty residue means there is real content change that a clean-refactor
claim cannot honestly cover.

Design notes:
  - FRESH normalizer (plan M4). We do NOT reuse stata_comment_lib.py's
    repair functions (they live inside greedy-`/*` repair machinery and have
    different goals). normalize() here is a simple per-language line filter:
    drop blanks, strip comments + scaffold lines, replace path literals with
    a `PATH` token, return the surviving content lines.
  - Per-language config dict keyed by language slug
    (`line_comment`, `block_comment`, `scaffold_patterns`,
    `path_token_patterns`). Languages: stata, python, r, latex.
  - LaTeX: `%` line comment; `\input`/`\includegraphics`/`\addbibresource`
    args are path-tokenized; `\label{}`/`\cite{}` args are CONTENT (a changed
    cite key is a substantive change, so it stays in the residue).
  - normdiff() is language-free: a pure set comparison of normalized lines.
  - Encoding (plan M8): callers read via utf-8; on UnicodeDecodeError the
    residue is treated as empty (fail-open). This module's helpers accept
    already-decoded strings, so the decode/fail-open policy is applied by the
    caller (see read_text_or_empty()).

Stdlib only. Python 3.11+. The caller is responsible for fail-open wrapping
on IO; the pure functions here raise on genuinely bad input.
"""

from __future__ import annotations

import re
from collections import Counter
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

SUPPORTED_LANGUAGES = ("stata", "python", "r", "latex")


def language_for_path(file_path: str) -> str | None:
    """Return the language slug for a path, or None if unsupported.

    Mirrors derive_lib.language_for_path so the two libraries agree on the
    file-type filter. The hook prefers derive_lib's version; this exists so
    normdiff_lib and its tests/CLI are self-contained.
    """
    suffix = Path(file_path).suffix
    if suffix in _SUFFIX_LANG:
        return _SUFFIX_LANG[suffix]
    return _SUFFIX_LANG.get(suffix.lower())


# ---------------------------------------------------------------------------
# Per-language normalization config
# ---------------------------------------------------------------------------
#
# Each language maps to a config dict:
#   line_comment        : list[str]   — line-comment prefixes (whole-line only,
#                                       after lstrip)
#   inline_comment      : list[str]   — prefixes scanned as trailing inline
#                                       comments mid-line. SUBSET of line_comment
#                                       for prefixes that can also start a whole
#                                       line. A prefix in line_comment but NOT in
#                                       inline_comment (e.g. Stata `*`) is a
#                                       whole-line comment only — never stripped
#                                       mid-line (Bug A: `gen z = x * y`).
#   quote_chars         : list[str]   — string-delimiter characters for inline
#                                       comment quote-awareness. Stata uses only
#                                       `"` (bare `'` is a local-macro close, not
#                                       a string delimiter — Bug C).
#   block_comment       : tuple|None  — (open, close) block-comment delimiters
#   scaffold_patterns   : list[re]    — whole-line scaffold to drop (logging,
#                                       housekeeping; not substantive content)
#   path_token_patterns : list[re]    — regexes whose group(1) is a path/arg
#                                       literal replaced by the `PATH` token

_PATH_TOKEN = "PATH"

# Stata: `*` is a comment ONLY as the first non-whitespace token of a line — it
# is NEVER a trailing inline comment (`gen z = x * y` is multiplication). `//`
# (and `/* ... */`) are the only inline comments. Stata strings use `"` (and
# compound `` `"..."' ``); bare `'` is a local-macro reference close, not a
# string delimiter, so it must not be in quote_chars (Bug C).
# Scaffold = logging + housekeeping that legitimately changes between refactors
# without changing analysis logic. NOTE: seed lines are NOT scaffold (Bug D) —
# a changed seed alters all stochastic output, so it must surface in the residue.
_STATA_CONFIG = {
    "line_comment": ["*", "//"],
    "inline_comment": ["//"],
    "quote_chars": ['"'],
    "block_comment": ("/*", "*/"),
    "scaffold_patterns": [
        re.compile(r"^\s*cap(?:t(?:u(?:r(?:e)?)?)?)?\s+log\s+close", re.IGNORECASE),
        re.compile(r"^\s*log\s+(?:using|close)\b", re.IGNORECASE),
        re.compile(r"^\s*set\s+more\s+off\b", re.IGNORECASE),
        re.compile(r"^\s*set\s+linesize\b", re.IGNORECASE),
        re.compile(r"^\s*clear\s+all\b", re.IGNORECASE),
        re.compile(r"^\s*clear\s*$", re.IGNORECASE),
        re.compile(r"^\s*version\s+[\d.]+\s*$", re.IGNORECASE),
    ],
    "path_token_patterns": [
        # use "file" / use ... using "file"
        re.compile(r'\buse\s+(?:[^"\n]*?\busing\s+)?"([^"]+)"', re.IGNORECASE),
        # merge/append/joinby ... using "file"
        re.compile(
            r'\b(?:merge|append|joinby|cross|mmerge)\b[^"\n]*?\busing\s+"([^"]+)"',
            re.IGNORECASE,
        ),
        # import delimited/excel/... "file" / ... using "file"
        re.compile(r'\bimport\s+\w+\s+(?:[^"\n]*?\busing\s+)?"([^"]+)"', re.IGNORECASE),
        # infile/insheet/infix using "file"
        re.compile(r'\b(?:infile|insheet|infix)\b[^"\n]*?\busing\s+"([^"]+)"', re.IGNORECASE),
        # save/export ... "file" — output paths also tokenized (a renamed
        # output path is not a logic change for refactor purposes)
        re.compile(r'\b(?:save|saveold)\s+"([^"]+)"', re.IGNORECASE),
        re.compile(r'\bexport\s+\w+\s+(?:[^"\n]*?\busing\s+)?"([^"]+)"', re.IGNORECASE),
        re.compile(r'\b(?:esttab|outreg2|estout)\b[^"\n]*?\busing\s+"([^"]+)"', re.IGNORECASE),
        re.compile(r'\b(?:graph\s+export)\b\s+"([^"]+)"', re.IGNORECASE),
        # include / do path
        re.compile(r'\b(?:include|do)\s+"?([^\s",\n]+\.(?:doh|ado|do))"?', re.IGNORECASE),
    ],
}

_R_CONFIG = {
    "line_comment": ["#"],
    "inline_comment": ["#"],
    "quote_chars": ['"', "'"],
    "block_comment": None,
    "scaffold_patterns": [
        re.compile(r"^\s*(?:suppressMessages|suppressWarnings)\s*\(", re.IGNORECASE),
        # NOTE: set.seed() is NOT scaffold (Bug D) — a changed seed value alters
        # all stochastic output, so the line stays as content and a seed change
        # surfaces in the residue.
        re.compile(r"^\s*sink\s*\("),
        re.compile(r"^\s*options\s*\("),
    ],
    "path_token_patterns": [
        re.compile(
            r'\b(?:read_csv|read_csv2|read_dta|read_rds|readRDS|read\.csv|read\.dta'
            r'|read\.table|fread|read_excel|read_parquet|read_sas|read_sav|vroom'
            r'|write_csv|write_rds|saveRDS|write\.csv|fwrite|ggsave|write_dta)'
            r'\s*\(\s*[^,()]*?["\']([^"\']+)["\']',
            re.IGNORECASE,
        ),
        re.compile(r'\bsource\s*\(\s*["\']([^"\']+)["\']'),
        re.compile(r'\bload\s*\(\s*["\']([^"\']+)["\']'),
        re.compile(r'\b(?:file\.path|here)\s*\([^)]*["\']([^"\']+)["\']'),
    ],
}

_PYTHON_CONFIG = {
    "line_comment": ["#"],
    "inline_comment": ["#"],
    "quote_chars": ['"', "'"],
    "block_comment": None,
    "scaffold_patterns": [
        # NOTE: random.seed() / np.random.seed() / torch.manual_seed() are NOT
        # scaffold (Bug D) — a changed seed value alters all stochastic output,
        # so the line stays as content and a seed change surfaces in the residue.
        re.compile(r"^\s*logging\.\w+\s*\("),
    ],
    "path_token_patterns": [
        re.compile(r'\.read_\w+\s*\(\s*["\']([^"\']+)["\']'),
        re.compile(r'\.to_\w+\s*\(\s*["\']([^"\']+)["\']'),
        re.compile(r'\bnp\.(?:load|save|savez)\s*\(\s*["\']([^"\']+)["\']'),
        re.compile(r'\bopen\s*\(\s*["\']([^"\']+)["\']'),
        re.compile(r'\bPath\s*\(\s*["\']([^"\']+)["\']'),
    ],
}

_LATEX_CONFIG = {
    "line_comment": ["%"],
    "inline_comment": ["%"],
    "quote_chars": ['"', "'"],
    "block_comment": None,
    "scaffold_patterns": [
        # nothing inherently scaffold in LaTeX bodies; preamble renames are
        # handled by path-tokenization + comment stripping, not scaffolding.
    ],
    "path_token_patterns": [
        re.compile(r'(\\input\s*\{[^}]*\})'),
        re.compile(r'(\\include\s*\{[^}]*\})'),
        re.compile(r'(\\includegraphics\s*(?:\[[^\]]*\])?\s*\{[^}]*\})'),
        re.compile(r'(\\addbibresource\s*\{[^}]*\})'),
        re.compile(r'(\\bibliography\s*\{[^}]*\})'),
    ],
}

_CONFIG_BY_LANG = {
    "stata": _STATA_CONFIG,
    "r": _R_CONFIG,
    "python": _PYTHON_CONFIG,
    "latex": _LATEX_CONFIG,
}


# ---------------------------------------------------------------------------
# Comment stripping
# ---------------------------------------------------------------------------


def _strip_block_comments(text: str, delimiters: tuple[str, str]) -> str:
    """Remove `/* ... */`-style block comments (non-nested) from text.

    Deliberately simple: a single non-greedy, string-unaware pass. A `/*` inside
    a Stata string literal is rare. Caveat: the "clips symmetrically on both
    baseline and current sides" property holds only when the delimiters bounding
    the clipped span are byte-identical on both sides; an edit that adds or moves
    a `*/` near changed content can clip asymmetrically. Accepted limitation for
    the residue use-case — worst case is a spurious residue line (over-report),
    never a missed change. Make this string-literal-aware if it proves noisy.
    """
    open_tok, close_tok = delimiters
    pattern = re.compile(
        re.escape(open_tok) + r".*?" + re.escape(close_tok), re.DOTALL
    )
    return pattern.sub(" ", text)


def _strip_line_comment(
    line: str,
    line_prefixes: list[str],
    inline_prefixes: list[str],
    quote_chars: list[str],
) -> str | None:
    """Return the content of `line` with any trailing line-comment removed.

    A line that is ENTIRELY a comment (after lstrip the first non-space token
    is one of `line_prefixes`) returns "" (drops to nothing). A line with an
    inline trailing comment (prefix in `inline_prefixes`) keeps the code
    portion. Returns the (possibly empty) surviving content; the caller decides
    whether an empty result is dropped.

    `line_prefixes` and `inline_prefixes` are deliberately distinct: a prefix
    may legally start a whole-line comment but NOT be a trailing inline comment.
    Stata's `*` is the motivating case — `* foo` is a comment line, but `gen z =
    x * y` is multiplication, never a comment (Bug A). So `*` is in
    `line_prefixes` but not in `inline_prefixes`.

    `quote_chars` are the string delimiters used for inline-comment
    quote-awareness; they are language-specific so Stata's bare `'`
    (local-macro close, not a string delimiter) does not poison quote state
    (Bug C).
    """
    stripped = line.lstrip()
    # Whole-line comment (any line_prefix at the first non-space token).
    for pref in line_prefixes:
        if stripped.startswith(pref):
            return ""
    # Inline trailing comment: find the earliest inline-prefix occurrence that
    # is not inside a quoted string. Keep it conservative — only handle the
    # common case of a comment prefix preceded by whitespace or line-start.
    earliest = None
    for pref in inline_prefixes:
        # Require the prefix to be preceded by whitespace/line-start to avoid
        # eating `//` inside paths/URLs and `#` inside other tokens.
        for m in re.finditer(r"(?:^|\s)" + re.escape(pref), line):
            pos = m.end() - len(pref)
            if not _inside_quotes(line, pos, quote_chars):
                if earliest is None or pos < earliest:
                    earliest = pos
                break
    if earliest is not None:
        return line[:earliest]
    return line


def _inside_quotes(line: str, pos: int, quote_chars: list[str]) -> bool:
    """Heuristic: is character index `pos` inside a quoted span?

    Tracks one open-quote state at a time across the configured `quote_chars`.
    A quote char only toggles state when no *other* quote char is currently
    open (so a `'` inside a `"..."` span is treated as literal). Quote chars
    not in the language's set (e.g. Stata's bare `'`) are ignored entirely,
    which prevents an odd number of `'` from poisoning the rest of the line
    (Bug C).
    """
    open_q: str | None = None
    for idx, ch in enumerate(line):
        if idx >= pos:
            break
        if ch in quote_chars:
            if open_q is None:
                open_q = ch
            elif open_q == ch:
                open_q = None
            # else: a different quote char is open → this one is literal.
    return open_q is not None


# ---------------------------------------------------------------------------
# Region extraction
# ---------------------------------------------------------------------------


def extract_executable_regions(text: str, language: str) -> list[str]:
    """Return the executable/content regions of `text`.

    For stata/r/python/latex this is the whole file as a single region (region
    awareness is reserved for the deferred Quarto `.qmd` normalizer, which
    needs chunk extraction). Returning a list keeps the interface stable for
    that future multi-region case.
    """
    if language not in _CONFIG_BY_LANG:
        return []
    return [text]


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------


def _is_pathlike(s: str) -> bool:
    """A captured literal is treated as a path only if it contains a path
    separator or ends in a dotted file extension. Prevents tokenizing a
    non-path first-quoted-arg (e.g. a separator/option string like ",") into
    PATH, so a change to such a literal correctly surfaces as residue."""
    s = s.strip()
    return "/" in s or "\\" in s or bool(re.search(r"\.[A-Za-z0-9]{1,8}$", s))


def _tokenize_paths(line: str, patterns: list[re.Pattern]) -> str:
    """Replace each captured path/arg literal (group 1) with the PATH token —
    only when the literal looks path-like (see _is_pathlike)."""
    out = line
    for pat in patterns:

        def _repl(m: re.Match) -> str:
            full = m.group(0)
            captured = m.group(1)
            if not _is_pathlike(captured):
                return full
            # Replace only the captured span within the full match so the
            # surrounding verb/command structure is preserved (so a renamed
            # path collapses to identical text but a changed command does not).
            start = m.start(1) - m.start(0)
            end = m.end(1) - m.start(0)
            return full[:start] + _PATH_TOKEN + full[end:]

        out = pat.sub(_repl, out)
    return out


def normalize(region: str, language: str) -> list[str]:
    """Return the normalized content lines of a region.

    Steps (fresh impl per plan M4):
      1. Strip block comments (languages that have them).
      2. Per line: strip line comments; drop whole-comment / blank lines.
      3. Drop scaffold lines (logging / housekeeping).
      4. Replace path literals with the PATH token.
      5. Collapse internal whitespace and strip; drop anything now empty.

    LaTeX note: `\\label{}` / `\\cite{}` args are NOT path-tokenized, so a
    changed cite key survives into the residue (it is substantive content).
    """
    config = _CONFIG_BY_LANG.get(language)
    if config is None:
        return []

    block = config["block_comment"]
    if block is not None:
        region = _strip_block_comments(region, block)

    line_prefixes = config["line_comment"]
    inline_prefixes = config.get("inline_comment", line_prefixes)
    quote_chars = config.get("quote_chars", ['"', "'"])
    scaffold = config["scaffold_patterns"]
    path_patterns = config["path_token_patterns"]

    out: list[str] = []
    for raw in region.splitlines():
        if not raw.strip():
            continue
        # Scaffold check is on the raw line (before comment stripping) so that
        # e.g. `log using "..."` matches regardless of trailing comment.
        if any(p.search(raw) for p in scaffold):
            continue
        content = _strip_line_comment(raw, line_prefixes, inline_prefixes, quote_chars)
        if content is None or not content.strip():
            continue
        content = _tokenize_paths(content, path_patterns)
        # Collapse runs of whitespace so indentation/spacing churn is ignored.
        collapsed = re.sub(r"\s+", " ", content).strip()
        if collapsed:
            out.append(collapsed)
    return out


def normalize_text(text: str, language: str) -> list[str]:
    """Normalize a whole file (all regions concatenated)."""
    lines: list[str] = []
    for region in extract_executable_regions(text, language):
        lines.extend(normalize(region, language))
    return lines


# ---------------------------------------------------------------------------
# Normalized diff
# ---------------------------------------------------------------------------


def normdiff(baseline_text: str, current_text: str, language: str) -> dict[str, list[str]]:
    """Multiset + order comparison of normalized content between baseline/current.

    Returns {"added": [...], "removed": [...], "reordered": bool}.

    - `added` / `removed`: normalized content lines whose *count* increased
      (added) or decreased (removed) between baseline and current. Computed via
      `collections.Counter` so multiplicity is preserved — deleting one of two
      identical substantive lines surfaces as a removal (Bug B, multiplicity).
    - `reordered`: True when the multisets are identical (no added/removed
      lines) but the line ORDER differs. Statement order is semantically
      load-bearing in Stata (`drop`/`keep`/`replace`/`sort`-dependent `by:`),
      so a pure reorder is a real logic change and must not read as
      "no logic change" (Bug B, ordering).

    An edit is "no logic change" iff `added` and `removed` are both empty AND
    `reordered` is False.
    """
    base_lines = normalize_text(baseline_text, language)
    curr_lines = normalize_text(current_text, language)

    base_counts = Counter(base_lines)
    curr_counts = Counter(curr_lines)

    # Multiset difference, expanding by count so duplicates surface.
    added: list[str] = []
    for line, n in (curr_counts - base_counts).items():
        added.extend([line] * n)
    removed: list[str] = []
    for line, n in (base_counts - curr_counts).items():
        removed.extend([line] * n)

    # Reorder detection: only meaningful when the multisets match exactly
    # (otherwise the add/remove residue already flags the change).
    reordered = False
    if not added and not removed:
        reordered = base_lines != curr_lines

    return {
        "added": sorted(added),
        "removed": sorted(removed),
        "reordered": reordered,
    }


def residue_is_empty(diff: dict) -> bool:
    """True iff the normdiff shows no logic change.

    No logic change requires NO added lines, NO removed lines, AND no
    reordering of identical content (reordering is a real logic change in
    order-sensitive languages — Bug B).
    """
    return (
        not diff.get("added")
        and not diff.get("removed")
        and not diff.get("reordered")
    )


def summarize_residue(diff: dict, max_items: int = 3) -> str:
    """One-line human summary of a residue, for the ledger Evidence column."""
    added = diff.get("added", [])
    removed = diff.get("removed", [])
    if not added and not removed:
        if diff.get("reordered"):
            return "content reordered (order-sensitive logic change)"
        return "no logic change (path/comment/blank only)"
    parts = [f"+{len(added)}/-{len(removed)} content line(s)"]
    sample: list[str] = []
    for ln in added[:max_items]:
        sample.append("+" + (ln[:60] + ("..." if len(ln) > 60 else "")))
    for ln in removed[: max(0, max_items - len(sample))]:
        sample.append("-" + (ln[:60] + ("..." if len(ln) > 60 else "")))
    if sample:
        parts.append("; ".join(sample))
    return " ".join(parts)


# ---------------------------------------------------------------------------
# IO helper (fail-open decode policy, plan M8)
# ---------------------------------------------------------------------------


def read_text_or_empty(path: str | Path) -> str:
    """Read a file as utf-8; on decode error or missing file, return "".

    This applies the plan's M8 fail-open policy at the IO boundary so callers
    can pass the result straight into normdiff().
    """
    try:
        return Path(path).read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""
