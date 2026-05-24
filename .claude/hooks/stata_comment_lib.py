"""
Shared logic for the Stata greedy-`/*` parser-bug enforcement tools.

Two callers use this library:

- .claude/skills/tools/stata_sweep.py — CLI sweep tool that detects (--check)
  or fixes (--fix) the bug across an existing codebase.
- .claude/hooks/stata-comment-balance-check.py — PreToolUse hook that blocks
  edits introducing the bug going forward.

Bug background. Stata's parser counts `/*` opens greedily regardless of
comment context. A path-glob like `prepare/*` inside any comment context
(`/* ... */` block, `*`-prefixed line, or `//`-prefixed line) silently opens
a runaway block comment. Full 8-variant taxonomy:
`master_supporting_docs/stata-block-comment-bug-field-guide.md`.

Critical invariants. Both the depth-counted matcher (`find_matching_close`)
and the inner rewriter (`rewrite_inner_block_markers`) MUST use the
path-glob predicates. A round-2 implementation that used greedy
depth-counting + blanket `inner.replace(...)` introduced Variant 8
(over-flatten). The workflow port starts at Round 3 from day one.

Project-agnostic. Stdlib only. Python 3.11+.
"""

from __future__ import annotations

import re
from typing import Literal


# Path-continuation chars used by `is_path_glob_open` / `is_path_glob_close`.
# A `/*` immediately preceded by one of these chars is a path-glob fragment
# (e.g., the `/*` in `prepare/*` or `$logdir/*`), not a block-comment open.
# A `*/` immediately followed by one of these chars is similarly a path-glob
# (e.g., the `*/` in `**/<sub>`).
_PATH_CHARS = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "_<>${}.-"
)


# ---------------------------------------------------------------------------
# Path-glob predicates (Variant 8 prevention)
# ---------------------------------------------------------------------------


def is_path_glob_open(text: str, i: int) -> bool:
    """
    Return True if `text[i:i+2] == '/*'` is a path-glob fragment.

    Heuristic: `/*` is a path-glob iff the char before it is a path char.
    Otherwise (start-of-text, whitespace, punctuation, etc.) it is a real
    block-comment open token.
    """
    if i <= 0:
        return False
    return text[i - 1] in _PATH_CHARS


def is_path_glob_close(text: str, i: int) -> bool:
    """
    Return True if `text[i:i+2] == '*/'` is a path-glob fragment.

    Heuristic: `*/` is a path-glob iff the char after it is a path char.
    Otherwise (EOF, whitespace, punctuation) it is a real block-comment close.
    """
    n = len(text)
    if i + 2 >= n:
        return False
    return text[i + 2] in _PATH_CHARS


# ---------------------------------------------------------------------------
# Depth-counted matcher (Variant 8 prevention)
# ---------------------------------------------------------------------------


def find_matching_close(text: str, open_end: int) -> int:
    """
    Given a position `open_end` immediately after a `/*` open token, scan
    forward with Stata-parser semantics (depth-counting) and return the
    start position of the `*/` that brings depth back to 0.

    Path-glob aware: path-glob `/*` and `*/` digraphs are NOT counted as
    depth changes. Without this guard, a file whose outer header contains
    a path-glob substring (e.g., `$logdir/*` inside `/* ... */`) would
    inflate the depth past 0 and the function would walk forward looking
    for a stray `*/` further down — introducing Variant 8.

    Returns -1 if no matching close exists.
    """
    n = len(text)
    depth = 1
    i = open_end
    while i < n - 1:
        if text[i] == "/" and text[i + 1] == "*":
            if not is_path_glob_open(text, i):
                depth += 1
            i += 2
            continue
        if text[i] == "*" and text[i + 1] == "/":
            if not is_path_glob_close(text, i):
                depth -= 1
                if depth == 0:
                    return i
            i += 2
            continue
        i += 1
    return -1


# ---------------------------------------------------------------------------
# Context-aware inner rewriter (Variant 8 prevention)
# ---------------------------------------------------------------------------


def rewrite_inner_block_markers(inner: str) -> str:
    """
    Rewrite real `/*` and `*/` digraphs inside an outer multi-line block
    comment to `/<x>` and `<x>` respectively, while leaving path-glob
    fragments intact (the main pass downstream handles those via its own
    state machine).

    Path-glob awareness is critical: blanket `inner.replace("/*", "/<x>")
    .replace("*/", "<x>")` is the Variant 8 trap — when combined with
    overshot depth-counting, it destroys legitimate body block markers.
    """
    n = len(inner)
    out: list[str] = []
    i = 0
    while i < n:
        if i + 1 < n and inner[i] == "/" and inner[i + 1] == "*":
            if is_path_glob_open(inner, i):
                out.append("/*")
            else:
                out.append("/<x>")
            i += 2
            continue
        if i + 1 < n and inner[i] == "*" and inner[i + 1] == "/":
            if is_path_glob_close(inner, i):
                out.append("*/")
            else:
                out.append("<x>")
            i += 2
            continue
        out.append(inner[i])
        i += 1
    return "".join(out)


# ---------------------------------------------------------------------------
# Pre-pass: flatten Variant 4 (fake nested comment blocks)
# ---------------------------------------------------------------------------


def flatten_lone_block_opens(text: str) -> tuple[str, int]:
    """
    Pre-pass: find every multi-line `/* ... */` block whose inner span
    contains nested `/*` or `*/` digraphs and rewrite the inner real block
    markers to `/<x>` / `<x>`. This handles Variant 4 (fake nested comment
    blocks where the predecessor relied on Stata's depth-counter to keep
    dormant code dormant).

    Without this pre-pass, the main pass's path-glob rewrite would convert
    inner `/* ... */` to `/<x> ... */`, leaving an orphan `*/` that
    prematurely closes the outer block and activates dormant code.

    State tracking: code | string | line_star | line_slash. Tracking
    line-comment states is essential — without it, a Variant-2 path-glob
    `/*` (inside a `*`-line comment) would be mistaken for a real block
    open, and `find_matching_close` would walk forward absorbing nearby
    Variant-4 blocks into a bogus inner span.

    Returns (transformed_text, n_inner_rewrites).
    """
    n = len(text)
    spans: list[tuple[int, int]] = []  # (inner_start, inner_end)
    state = "code"  # code | string | line_star | line_slash
    i = 0
    at_line_start = True
    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""

        if ch == "\n":
            if state in ("line_star", "line_slash"):
                state = "code"
            at_line_start = True
            i += 1
            continue

        if state == "string":
            if ch == '"':
                state = "code"
            i += 1
            continue

        if state in ("line_star", "line_slash"):
            i += 1
            continue

        # state == "code"
        if ch == '"':
            state = "string"
            at_line_start = False
            i += 1
            continue

        if ch == "*" and at_line_start:
            state = "line_star"
            at_line_start = False
            i += 1
            continue

        if ch == "/" and nxt == "/":
            state = "line_slash"
            at_line_start = False
            i += 2
            continue

        if ch == "/" and nxt == "*":
            o_end = i + 2
            close_pos = find_matching_close(text, o_end)
            if close_pos < 0:
                at_line_start = False
                i += 2
                continue
            inner = text[o_end:close_pos]
            if "\n" in inner and ("/*" in inner or "*/" in inner):
                spans.append((o_end, close_pos))
            at_line_start = False
            i = close_pos + 2
            continue

        if not ch.isspace():
            at_line_start = False
        i += 1

    if not spans:
        return text, 0

    new_text = text
    rewrites = 0
    for s_start, s_end in reversed(spans):
        inner = new_text[s_start:s_end]
        inner_new = rewrite_inner_block_markers(inner)
        if inner_new != inner:
            n_open_before = sum(
                1
                for j in range(len(inner) - 1)
                if inner[j] == "/"
                and inner[j + 1] == "*"
                and not is_path_glob_open(inner, j)
            )
            n_close_before = sum(
                1
                for j in range(len(inner) - 1)
                if inner[j] == "*"
                and inner[j + 1] == "/"
                and not is_path_glob_close(inner, j)
            )
            rewrites += n_open_before + n_close_before
            new_text = new_text[:s_start] + inner_new + new_text[s_end:]

    return new_text, rewrites


# ---------------------------------------------------------------------------
# Main pass: rewrite path-globs in comment state
# ---------------------------------------------------------------------------


def transform_comment_globs(text: str) -> tuple[str, int, int]:
    """
    Walk `text` character-by-character. Inside any comment context (block,
    `*`-line, or `//`-line), rewrite glob-wildcard `*` chars to `<x>` so
    that no `/*` or `*/` digraph survives.

    String literals are preserved verbatim — Stata strings can contain
    anything.

    Returns (transformed_text, n_real_rewrites, n_v7_cosmetic).

    `n_real_rewrites` counts rewrites that fix a parser-confusing pattern
    (V1/V2/V3/V6). `n_v7_cosmetic` counts the `//*` → `// *` rewrite
    (V7 banner) — Stata sees both forms identically, but the grep-balance
    check sees the latter as clean. The two counters are kept separate so
    `classify_file` can distinguish "real bug fixed" from "cosmetic only."
    """
    out: list[str] = []
    n = len(text)
    i = 0
    state = "code"  # code | block | line_star | line_slash | string
    at_line_start = True
    n_real = 0
    n_v7 = 0

    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""

        if ch == "\n":
            if state in ("line_star", "line_slash"):
                state = "code"
            out.append(ch)
            at_line_start = True
            i += 1
            continue

        if state == "code":
            if ch == "*" and at_line_start:
                state = "line_star"
                out.append(ch)
                at_line_start = False
                i += 1
                continue
            if ch == "/" and nxt == "/":
                state = "line_slash"
                after = text[i + 2] if i + 2 < n else ""
                if after == "*":
                    out.append("// ")
                    n_v7 += 1
                else:
                    out.append("//")
                at_line_start = False
                i += 2
                continue
            if ch == "/" and nxt == "*":
                state = "block"
                out.append("/*")
                at_line_start = False
                i += 2
                continue
            if ch == '"':
                state = "string"
                out.append(ch)
                at_line_start = False
                i += 1
                continue
            out.append(ch)
            if not ch.isspace():
                at_line_start = False
            i += 1
            continue

        if state == "block":
            # Distinguish a real block close from a path-glob `*/<sub>`.
            if ch == "*" and nxt == "/":
                after = text[i + 2] if i + 2 < n else ""
                if after and (after.isalnum() or after in ("_", "<", "$", "{", "*")):
                    out.append("<x>/")
                    n_real += 1
                    i += 2
                    continue
                out.append("*/")
                state = "code"
                i += 2
                continue
            if ch == "/" and nxt == "*":
                out.append("/<x>")
                n_real += 1
                i += 2
                continue
            # `**/` inside block, after a slash → `<x>/`
            if ch == "*" and nxt == "*" and out and out[-1].endswith("/"):
                after_pair = text[i + 2] if i + 2 < n else ""
                if after_pair == "/":
                    out.append("<x>/")
                    n_real += 1
                    i += 3
                    continue
                out.append("<x>")
                n_real += 1
                i += 2
                continue
            # Lone trailing `*` after `/` (path-glob).
            if (
                ch == "*"
                and out
                and out[-1].endswith("/")
                and nxt != "*"
                and nxt != "/"
            ):
                out.append("<x>")
                n_real += 1
                i += 1
                continue
            out.append(ch)
            i += 1
            continue

        if state in ("line_star", "line_slash"):
            if ch == "/" and nxt == "*":
                out.append("/<x>")
                n_real += 1
                i += 2
                continue
            if ch == "*" and nxt == "/":
                after = text[i + 2] if i + 2 < n else ""
                if after and (after.isalnum() or after in ("_", "<", "$", "{", "*")):
                    out.append("<x>/")
                    n_real += 1
                    i += 2
                    continue
                out.append("<x>")
                n_real += 1
                i += 2
                continue
            if ch == "*" and nxt == "*" and out and out[-1].endswith("/"):
                after_pair = text[i + 2] if i + 2 < n else ""
                if after_pair == "/":
                    out.append("<x>/")
                    n_real += 1
                    i += 3
                    continue
                out.append("<x>")
                n_real += 1
                i += 2
                continue
            if (
                ch == "*"
                and out
                and out[-1].endswith("/")
                and nxt != "*"
                and nxt != "/"
            ):
                out.append("<x>")
                n_real += 1
                i += 1
                continue
            out.append(ch)
            i += 1
            continue

        # state == "string"
        if ch == '"':
            state = "code"
        out.append(ch)
        i += 1

    return "".join(out), n_real, n_v7


# ---------------------------------------------------------------------------
# Post-pass: strip orphan `*/` (Variant 5)
# ---------------------------------------------------------------------------


# Use `[ \t]` (not `\s`) so the match does not consume surrounding newlines —
# `\s` includes `\n`, which would greedy-match adjacent blank lines and cause
# the strip to remove more than the orphan line itself.
_ORPHAN_CLOSE_LINE = re.compile(r"^[ \t]*\*/[ \t]*$", re.MULTILINE)


def strip_orphan_block_closes(text: str) -> tuple[str, int]:
    """
    Strip whole-line orphan `*/` tokens — lines that contain only
    whitespace + `*/` and that lie at code-depth 0.

    After the main pass fixes spurious `/*` opens, these orphans become
    real Stata syntax errors. They were previously masked by an upstream
    runaway block comment.

    Returns (transformed_text, n_stripped).
    """
    candidate_lines: list[tuple[int, int]] = []
    for m in _ORPHAN_CLOSE_LINE.finditer(text):
        candidate_lines.append((m.start(), m.end()))

    if not candidate_lines:
        return text, 0

    # Build a per-offset depth map by walking the text once.
    n = len(text)
    depth_at_offset = [0] * n
    state = "code"
    depth = 0
    i = 0
    while i < n:
        depth_at_offset[i] = depth
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if state == "code":
            if ch == "/" and nxt == "/":
                state = "line_slash"
                i += 2
                continue
            if ch == "/" and nxt == "*":
                state = "block"
                depth = 1
                i += 2
                continue
            if ch == '"':
                state = "string"
                i += 1
                continue
            i += 1
            continue
        if state == "block":
            if ch == "*" and nxt == "/":
                depth -= 1
                if depth <= 0:
                    state = "code"
                    depth = 0
                i += 2
                continue
            if ch == "/" and nxt == "*":
                depth += 1
                i += 2
                continue
            i += 1
            continue
        if state == "line_slash":
            if ch == "\n":
                state = "code"
            i += 1
            continue
        if state == "string":
            if ch == '"':
                state = "code"
            i += 1
            continue
        i += 1

    new_text = text
    stripped = 0
    for start, end in reversed(candidate_lines):
        line_text = text[start:end]
        star_pos = line_text.find("*/")
        if star_pos < 0:
            continue
        global_star = start + star_pos
        if global_star >= len(depth_at_offset):
            continue
        if depth_at_offset[global_star] > 0:
            continue
        line_end = end
        if line_end < len(new_text) and new_text[line_end] == "\n":
            line_end += 1
        new_text = new_text[:start] + new_text[line_end:]
        stripped += 1

    return new_text, stripped


# ---------------------------------------------------------------------------
# Balance check (state-machine; replaces naive grep)
# ---------------------------------------------------------------------------


def compute_balance(text: str) -> tuple[int, int]:
    """
    Return `(opens, closes)` — the count of `/*` and `*/` digraphs that
    Stata's parser would actually see, excluding:

    - `/*` and `*/` inside string literals (Stata ignores)
    - `/*` and `*/` inside `//` or `*` line comments (Stata terminates the
      line comment at newline; the digraph is consumed as line-comment text
      and never counted by the parser)

    A file is balanced iff `opens == closes`. This is the "true" balance
    from Stata's perspective. Path-glob `/*` inside a `/* ... */` header
    IS counted (that's the V1 bug — Stata's greedy parser sees it as a
    nested open and the file becomes unbalanced).

    This replaces naive `grep -c '/\\*'` vs `grep -c '\\*/'` which inflates
    on Variant 7 banners (`//*****`) and string-literal `/*` digraphs.
    """
    n = len(text)
    state = "code"  # code | block | line_star | line_slash | string
    opens = 0
    closes = 0
    depth = 0
    at_line_start = True
    i = 0
    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""

        if ch == "\n":
            if state in ("line_star", "line_slash"):
                state = "code"
            at_line_start = True
            i += 1
            continue

        if state == "string":
            if ch == '"':
                state = "code"
            i += 1
            continue

        if state in ("line_star", "line_slash"):
            i += 1
            continue

        # state is "code" or "block"
        if state == "code":
            if ch == '"':
                state = "string"
                i += 1
                continue
            if ch == "*" and at_line_start:
                state = "line_star"
                at_line_start = False
                i += 1
                continue
            if ch == "/" and nxt == "/":
                state = "line_slash"
                at_line_start = False
                i += 2
                continue

        if ch == "/" and nxt == "*":
            opens += 1
            depth += 1
            state = "block"
            at_line_start = False
            i += 2
            continue

        if ch == "*" and nxt == "/":
            closes += 1
            depth -= 1
            if depth <= 0:
                state = "code"
                depth = 0
            i += 2
            continue

        if not ch.isspace():
            at_line_start = False
        i += 1

    return opens, closes


# ---------------------------------------------------------------------------
# Variant detectors (line-level grep)
# ---------------------------------------------------------------------------


_LINE_STAR_GLOB = re.compile(r"^\s*\*.*/\*")
_LINE_SLASH_GLOB = re.compile(r"^\s*//.*/\*")
# V8 detection: lines whose trailing `*/` was rewritten to `<x>` by a buggy
# round-2-equivalent fix tool. Two forms:
#   - Pure dash/equals/asterisk header separator: `------<x>`, `*-----<x>`,
#     ` *-----<x>` (mirrors the va_consolidated sec1415/sec1617 incident).
#   - Standalone `<x>` on otherwise-empty line (a legitimate single-line body
#     block whose close was blanket-rewritten).
# Permitted prefix chars in the dash form: whitespace, `*`, `=`, `-`.
_V8_DASH_PATTERN = re.compile(r"^[\s*=\-]*[\-=][\-=][\-=]+<x>$")
_V8_LONE_PATTERN = re.compile(r"^\s*<x>\s*$")


def has_glob_in_line_comment(text: str) -> list[tuple[int, str]]:
    """
    Return `[(line_number, line_text), ...]` for lines that match
    Variants 2, 3, or 7 (path-glob `/*` inside `*`-line or `//`-line
    comments, including `//****` banners — the caller decides whether
    to treat V7 separately).
    """
    results: list[tuple[int, str]] = []
    for n, line in enumerate(text.splitlines(), start=1):
        if _LINE_STAR_GLOB.match(line) or _LINE_SLASH_GLOB.match(line):
            results.append((n, line.rstrip()))
    return results


def find_over_flatten_artifacts(text: str) -> list[tuple[int, str]]:
    """
    Return `[(line_number, line_text), ...]` for Variant 8 corruption
    artifacts — lines left by a buggy round-2-equivalent fix tool that
    over-flattened legitimate body block markers.

    Two patterns:
      - `^-+<x>$` — header separator whose trailing `*/` was rewritten
      - `^\\s*<x>\\s*$` — lone `<x>` on otherwise-empty line (a
        legitimate single-line body block whose close was rewritten)
    """
    results: list[tuple[int, str]] = []
    for n, line in enumerate(text.splitlines(), start=1):
        stripped = line.rstrip()
        if _V8_DASH_PATTERN.match(stripped) or _V8_LONE_PATTERN.match(stripped):
            results.append((n, stripped))
    return results


# ---------------------------------------------------------------------------
# Orchestrator: full three-pass sweep
# ---------------------------------------------------------------------------


def sweep_text(text: str) -> tuple[str, dict[str, int]]:
    """
    Apply all three passes in order: pre-pass (V4 flatten), main pass
    (V1/V2/V3/V6/V7), post-pass (V5 orphan strip).

    Returns `(new_text, info)` where `info` has keys:
      - `n_pre`: V4 flatten count
      - `n_real`: real path-glob rewrites in the main pass (V1/V2/V3/V6)
      - `n_v7`: V7 cosmetic `//*` → `// *` rewrites
      - `n_orphans`: V5 orphan close strips
    """
    text, n_pre = flatten_lone_block_opens(text)
    text, n_real, n_v7 = transform_comment_globs(text)
    text, n_orphans = strip_orphan_block_closes(text)
    return text, {
        "n_pre": n_pre,
        "n_real": n_real,
        "n_v7": n_v7,
        "n_orphans": n_orphans,
    }


# ---------------------------------------------------------------------------
# File classification (CLEAN / AUTO-FIXABLE / MANUAL-ATTENTION)
# ---------------------------------------------------------------------------


FileClass = Literal["clean", "auto-fixable", "manual-attention"]


def classify_file(text: str) -> FileClass:
    """
    Classify a file based on whether the sweep can safely auto-remediate.

    - `manual-attention`: Variant 8 corruption artifacts present, OR the
      file contains a `/*` open with no reachable matching `*/` anywhere
      (post-sweep balance still imbalanced). Sweep `--fix` skips these.
    - `auto-fixable`: pre-sweep imbalanced (V1/V2/V3/V5/V6) OR V4 nested
      blocks would be flattened. Sweep `--fix` will mutate the file.
    - `clean`: pre-sweep already balanced AND no V4 nesting. Sweep would
      do nothing or only cosmetic V7 banner cleanup (Stata sees both
      forms identically; not load-bearing).
    """
    if find_over_flatten_artifacts(text):
        return "manual-attention"

    pre_opens, pre_closes = compute_balance(text)
    swept, info = sweep_text(text)
    post_opens, post_closes = compute_balance(swept)

    if post_opens != post_closes:
        return "manual-attention"

    # CLEAN iff: pre-sweep already balanced AND sweep made no structural
    # changes (V4 flatten, V5 orphan strip, V1/V2/V3/V6 real rewrites).
    # V7 cosmetic rewrites (`//*` → `// *`) are not load-bearing and do
    # not flip CLEAN to AUTO-FIXABLE.
    if (
        pre_opens == pre_closes
        and info["n_pre"] == 0
        and info["n_orphans"] == 0
        and info["n_real"] == 0
    ):
        return "clean"

    return "auto-fixable"
