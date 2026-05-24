#!/usr/bin/env python3
"""
Stata Greedy-`/*` Parser-Bug PreToolUse Hook.

Blocks Edit/Write/MultiEdit calls that would leave a `.do`/`.doh` file in a
worse state than before — specifically, that would introduce:

  1. A new V1/V2/V3/V6 path-glob `/*` in any comment context, causing
     state-machine balance to flip from OK to imbalanced.
  2. A new V8 over-flatten artifact (`^[\\s*=\\-]*-+<x>$` or `^\\s*<x>\\s*$`).
  3. A new MANUAL-ATTENTION state (unmatched `/*` open with no reachable
     `*/`) on a file that was previously CLEAN.

Legacy tolerance: if the file was ALREADY in a bad state before this edit,
the hook does NOT block the edit (the user may be making it worse or better
incrementally — let the sweep tool be the authority for back-catalog fixes).

V7 banners (`//*****`) are deliberately NOT blocked: they're parser-safe
and `compute_balance` correctly excludes them. Coder-critic surfaces them
as advisory deductions (see `.claude/rules/stata-code-conventions.md` § 2).

Shared logic in `.claude/hooks/stata_comment_lib.py`.

Install in `.claude/settings.json` (PreToolUse block, matcher `Edit|Write|MultiEdit`):

    python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/stata-comment-balance-check.py

Fail-open on any internal exception. Exits silently when the file is not
a `.do`/`.doh` path (so non-Stata edits never see this hook's output).
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path


# File suffixes this hook acts on. Internal check (matcher in settings.json
# is on tool name; this is the file-type filter).
_STATA_SUFFIXES = (".do", ".doh")

# Paths under which intentionally-buggy `.do` fixtures live. These exhibit
# the bug as test data and must not be blocked.
_FIXTURE_PREFIXES = (
    ".claude/hooks/tests/",
    ".claude/skills/tools/tests/",
    "templates/",
)


def _load_lib():
    """Load stata_comment_lib from the same directory as this script."""
    lib_path = Path(__file__).resolve().parent / "stata_comment_lib.py"
    spec = importlib.util.spec_from_file_location("stata_comment_lib", lib_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {lib_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _apply_edit(pre: str, edit: dict) -> str | None:
    """
    Simulate an Edit tool call: replace `old_string` with `new_string`.
    Returns None if old_string is missing or not found in pre.
    """
    old = edit.get("old_string", "") or ""
    new = edit.get("new_string", "") or ""
    if not old:
        return None
    if edit.get("replace_all"):
        if old not in pre:
            return None
        return pre.replace(old, new)
    # Single-occurrence replacement; only valid if old appears exactly once.
    count = pre.count(old)
    if count != 1:
        return None
    return pre.replace(old, new, 1)


def _build_post_text(tool_name: str, tool_input: dict, file_path: Path) -> str | None:
    """
    Compute the file's post-edit content. Returns None if we can't safely
    simulate (fail-open).
    """
    if tool_name == "Write":
        return tool_input.get("content", "") or ""

    pre = ""
    if file_path.is_file():
        try:
            pre = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None

    if tool_name == "Edit":
        result = _apply_edit(pre, tool_input)
        return result

    if tool_name == "MultiEdit":
        edits = tool_input.get("edits", []) or []
        current = pre
        for edit in edits:
            applied = _apply_edit(current, edit)
            if applied is None:
                return None
            current = applied
        return current

    return None


def _classify_safe(lib, text: str) -> str | None:
    try:
        return lib.classify_file(text)
    except Exception:
        return None


def main() -> None:
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "")
    if tool_name not in {"Edit", "Write", "MultiEdit"}:
        sys.exit(0)

    tool_input = hook_input.get("tool_input", {}) or {}
    file_path_str = tool_input.get("file_path", "") or ""
    if not file_path_str:
        sys.exit(0)

    file_path = Path(file_path_str)
    if file_path.suffix not in _STATA_SUFFIXES:
        sys.exit(0)

    # Skip intentionally-buggy fixtures.
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", hook_input.get("cwd", ""))
    if project_dir:
        try:
            rel = file_path.resolve().relative_to(Path(project_dir).resolve())
            rel_str = str(rel)
            if any(rel_str.startswith(prefix) for prefix in _FIXTURE_PREFIXES):
                sys.exit(0)
        except (ValueError, OSError):
            pass

    lib = _load_lib()

    # Compute pre-edit and post-edit classifications.
    pre_text = ""
    if file_path.is_file():
        try:
            pre_text = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            sys.exit(0)

    post_text = _build_post_text(tool_name, tool_input, file_path)
    if post_text is None:
        # Couldn't simulate (e.g., old_string not found) — let the tool
        # itself error if invalid. Don't block.
        sys.exit(0)

    pre_class = _classify_safe(lib, pre_text)
    post_class = _classify_safe(lib, post_text)

    if pre_class is None or post_class is None:
        sys.exit(0)

    # Legacy tolerance: if the file was already bad, don't block (the user
    # may be fixing it incrementally; sweep tool is the authority).
    if pre_class in ("auto-fixable", "manual-attention"):
        sys.exit(0)

    # File was CLEAN before. Block if the edit introduces problems.
    if post_class == "clean":
        sys.exit(0)

    # Build a targeted message.
    if post_class == "manual-attention":
        v8 = lib.find_over_flatten_artifacts(post_text)
        if v8:
            reason = (
                "Stata greedy-/* parser bug — Variant 8 artifact introduced.\n\n"
                "The edit would leave V8 corruption artifacts (header-separator "
                "lines ending in `<x>` instead of `*/`) at line(s): "
                + ", ".join(str(n) for n, _ in v8[:5])
                + ".\n\n"
                "Investigate the source of the corruption (likely a buggy fix "
                "tool further upstream) before editing.\n"
                "See master_supporting_docs/stata-block-comment-bug-field-guide.md "
                "§ Variant 8."
            )
        else:
            reason = (
                "Stata greedy-/* parser bug — unmatched `/*` introduced.\n\n"
                "The edit would leave an unmatched `/*` open with no reachable "
                "`*/` close anywhere downstream. Stata's parser will treat "
                "everything after the unmatched open as a runaway block comment "
                "(silent script non-execution).\n\n"
                "Fix: add the matching `*/` close, OR change the `*` to `<x>` "
                "if it was meant as a path-glob in comment text.\n"
                "See master_supporting_docs/stata-block-comment-bug-field-guide.md."
            )
    else:  # auto-fixable
        v2v3_hits = lib.has_glob_in_line_comment(post_text)
        # Only flag NEW hits (not present in pre).
        pre_hits = set(lib.has_glob_in_line_comment(pre_text))
        new_hits = [(n, t) for (n, t) in v2v3_hits if (n, t) not in pre_hits]
        if new_hits:
            preview = "\n".join(f"  line {n}: {t}" for n, t in new_hits[:5])
            reason = (
                "Stata greedy-/* parser bug — path-glob `/*` introduced in "
                "comment context.\n\n"
                "The edit introduces a `*` wildcard inside a comment, which "
                "Stata's parser will greedily treat as a `/*` block-comment "
                "open. This silently swallows downstream code as comment.\n\n"
                f"Affected line(s):\n{preview}\n\n"
                "Fix: replace the `*` glob with `<x>` (or `<file>`) — see "
                ".claude/rules/stata-code-conventions.md § Comment Safety, Rule 1.\n"
                "Auto-fix: `python3 .claude/skills/tools/stata_sweep.py --fix <file>`."
            )
        else:
            reason = (
                "Stata greedy-/* parser bug — edit would flip the file from "
                "CLEAN to AUTO-FIXABLE state-machine balance.\n\n"
                "Likely cause: path-glob `*` introduced inside a `/* ... */` "
                "header block (V1), or a new orphan `*/` (V5).\n\n"
                "Fix: review the edit; run "
                "`python3 .claude/skills/tools/stata_sweep.py --check <file>` "
                "for diagnosis."
            )

    output = {"decision": "block", "reason": reason}
    json.dump(output, sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
