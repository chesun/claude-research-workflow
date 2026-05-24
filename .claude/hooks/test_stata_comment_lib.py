#!/usr/bin/env python3
"""Regression tests for stata_comment_lib.py.

Covers all 8 variants from the field guide
(master_supporting_docs/stata-block-comment-bug-field-guide.md) plus
the 2026-05-23 revision additions (V7 false-positive avoidance,
string-literal protection, manual-attention classification).

Run with: python3 .claude/hooks/test_stata_comment_lib.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_lib():
    lib_path = Path(__file__).resolve().parent / "stata_comment_lib.py"
    spec = importlib.util.spec_from_file_location("stata_comment_lib", lib_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lib = _load_lib()

_FIXTURES = Path(__file__).resolve().parent / "tests" / "fixtures"


# --- Helpers ---------------------------------------------------------------


def _fail(label: str, *extras: str) -> None:
    print(f"FAIL: {label}")
    for extra in extras:
        print(f"  {extra}")
    sys.exit(1)


def assert_eq(actual, expected, label: str) -> None:
    if actual != expected:
        _fail(label, f"expected: {expected!r}", f"actual:   {actual!r}")
    print(f"PASS: {label}")


def assert_true(cond: bool, label: str, *extras: str) -> None:
    if not cond:
        _fail(label, *extras)
    print(f"PASS: {label}")


def read_fixture(name: str) -> str:
    return (_FIXTURES / name).read_text()


# ---------------------------------------------------------------------------
# 1. Path-glob predicates
# ---------------------------------------------------------------------------

print("=== Path-glob predicates ===")
assert_eq(lib.is_path_glob_open("/*", 0), False, "leading /* is a real open")
assert_eq(lib.is_path_glob_open("a/*", 1), True, "a/* is path-glob (preceded by alpha)")
assert_eq(lib.is_path_glob_open(" /*", 1), False, "space-prefixed /* is real open")
assert_eq(lib.is_path_glob_open("$logdir/*", 7), True, "$logdir/* is path-glob")
assert_eq(lib.is_path_glob_open("prepare/*", 7), True, "prepare/* is path-glob")
assert_eq(lib.is_path_glob_open(".do/*", 3), True, "after dot is path char")

assert_eq(lib.is_path_glob_close("*/", 0), False, "trailing */ at EOF is real close")
assert_eq(lib.is_path_glob_close("*/x", 0), True, "*/x is path-glob")
assert_eq(lib.is_path_glob_close("*/ ", 0), False, "*/ + space is real close")
assert_eq(lib.is_path_glob_close("**/<sub>", 1), True, "**/< is path-glob")


# ---------------------------------------------------------------------------
# 2. find_matching_close (V8 regression)
# ---------------------------------------------------------------------------

print("\n=== find_matching_close (V8 regression) ===")
# Simple case: matching close at expected position
t = "/* hello */"
assert_eq(lib.find_matching_close(t, 2), 9, "simple block close at position 9")

# Nested: /* a /* b */ c */
t = "/* a /* b */ c */"
# After opening /*, we walk. We hit /* at position 5 (nested open). Then */ at 10.
# Then */ at 15 (closes outer).
assert_eq(lib.find_matching_close(t, 2), 15, "nested block — outer close")

# V8 regression: path-glob inside outer header should NOT inflate depth.
# /* OUTPUTS $logdir/* */
#    0123456789012345678901
t = "/* OUTPUTS $logdir/* */"
# The /* at position 18 is preceded by 'r' (path char) → path-glob, depth unchanged.
# The */ at positions 21-22 is followed by EOF → real close.
assert_eq(
    lib.find_matching_close(t, 2),
    21,
    "V8: path-glob /* inside outer header — close at 21, not later",
)

# Unmatched open → -1
assert_eq(lib.find_matching_close("/* never closed", 2), -1, "unmatched returns -1")


# ---------------------------------------------------------------------------
# 3. rewrite_inner_block_markers (V8 prevention in inner rewrite)
# ---------------------------------------------------------------------------

print("\n=== rewrite_inner_block_markers ===")
# Path-globs preserved; real block markers rewritten.
inner = " comment with $logdir/* and a /* nested */ pair "
expected = " comment with $logdir/* and a /<x> nested <x> pair "
assert_eq(
    lib.rewrite_inner_block_markers(inner),
    expected,
    "preserves path-glob, rewrites real /* and */",
)

# Real markers only
assert_eq(
    lib.rewrite_inner_block_markers(" /* foo */ "),
    " /<x> foo <x> ",
    "real block markers rewritten",
)

# Path-globs only
assert_eq(
    lib.rewrite_inner_block_markers(" $logdir/* and **/<sub> "),
    " $logdir/* and **/<sub> ",
    "all-path-glob inner left intact",
)


# ---------------------------------------------------------------------------
# 4. flatten_lone_block_opens (V4 pre-pass)
# ---------------------------------------------------------------------------

print("\n=== flatten_lone_block_opens (V4) ===")
# Multi-line outer with inner pair → flatten
text = "/* outer\n  /* inner */\n  code\n*/"
out, n = lib.flatten_lone_block_opens(text)
assert_true(
    "/<x> inner <x>" in out,
    "V4: inner pair flattened",
    f"output: {out!r}",
)
assert_eq(n, 2, "V4: 2 markers rewritten (open + close)")

# Single-line block → no flatten (no risk)
text = "/* single line */"
out, n = lib.flatten_lone_block_opens(text)
assert_eq(out, text, "single-line block unchanged")
assert_eq(n, 0, "single-line block: 0 rewrites")

# V8 prevention: outer header with path-glob inside should NOT trigger
# over-walk into stray */ further down.
text = (
    "/* PURPOSE: clean every file under prepare/*\n"
    " * OUTPUTS: $logdir/*\n"
    " */\n"
    "use sec1415, clear\n"
    "* a stray */ further down\n"
)
out, n = lib.flatten_lone_block_opens(text)
# Real header close at line 3 must be preserved as */, not rewritten to <x>.
# (The inner span — header text — contains no real /* or */ pairs, only path-globs.)
assert_true(
    "*/\n" in out,
    "V8 regression: real header */ preserved",
    f"output: {out!r}",
)


# ---------------------------------------------------------------------------
# 5. transform_comment_globs (V1/V2/V3/V6 + V7 cosmetic)
# ---------------------------------------------------------------------------

print("\n=== transform_comment_globs (main pass) ===")
# V1: path-glob inside /* */ block
text = "/* INPUTS: $rawdir/prepare/* */"
out, n_real, n_v7 = lib.transform_comment_globs(text)
assert_true("prepare/<x>" in out, "V1: path-glob rewritten in block")
assert_eq(n_v7, 0, "V1: no V7 cosmetic")
assert_true(n_real > 0, "V1: real rewrite count > 0")

# V2: path-glob in *-line comment
text = "* Process every file in prepare/* and save\n"
out, n_real, n_v7 = lib.transform_comment_globs(text)
assert_true("prepare/<x>" in out, "V2: path-glob in *-line rewritten")
assert_eq(n_v7, 0, "V2: no V7 cosmetic")

# V3: path-glob in //-line comment
text = "// log to $logdir/*.smcl\n"
out, n_real, n_v7 = lib.transform_comment_globs(text)
assert_true("$logdir/<x>" in out, "V3: path-glob in //-line rewritten")

# V7: //**** banner → "// ****"
text = "//*****************\n"
out, n_real, n_v7 = lib.transform_comment_globs(text)
assert_true(out.startswith("// "), "V7: //* gets space inserted")
assert_eq(n_v7, 1, "V7: one cosmetic rewrite counted")
assert_eq(n_real, 0, "V7: no real rewrites")

# String literal: path-glob inside "..." preserved
text = 'display "$outdir/*.txt"\n'
out, n_real, n_v7 = lib.transform_comment_globs(text)
assert_eq(out, text, "string-literal preserved verbatim")
assert_eq(n_real, 0, "string-literal: no rewrites")


# ---------------------------------------------------------------------------
# 6. strip_orphan_block_closes (V5)
# ---------------------------------------------------------------------------

print("\n=== strip_orphan_block_closes (V5) ===")
text = "sort id\n\n*/\n\ngen newvar = 1\n"
out, n = lib.strip_orphan_block_closes(text)
assert_true("*/" not in out, "V5: orphan */ stripped")
assert_eq(n, 1, "V5: 1 line stripped")

# Inside a real block: */ is NOT orphan
text = "/* header\n*/\ncode\n"
out, n = lib.strip_orphan_block_closes(text)
assert_true("*/" in out, "V5: */ inside real block preserved")
assert_eq(n, 0, "V5: real close not stripped")


# ---------------------------------------------------------------------------
# 7. find_over_flatten_artifacts (V8 detection)
# ---------------------------------------------------------------------------

print("\n=== find_over_flatten_artifacts (V8) ===")
# Header separator with <x>
text = "/*--------\n * header\n----------<x>\nuse foo, clear\n"
hits = lib.find_over_flatten_artifacts(text)
assert_eq(len(hits), 1, "V8 pattern 1: header-separator <x> detected")
assert_eq(hits[0][0], 3, "V8 pattern 1: correct line number")

# Lone <x> on otherwise-empty line
text = "code line\n   <x>   \nmore code\n"
hits = lib.find_over_flatten_artifacts(text)
assert_eq(len(hits), 1, "V8 pattern 2: lone <x> detected")

# Clean file → no artifacts
text = "/* normal header */\ncode\n"
hits = lib.find_over_flatten_artifacts(text)
assert_eq(hits, [], "V8: clean file has no artifacts")


# ---------------------------------------------------------------------------
# 8. has_glob_in_line_comment
# ---------------------------------------------------------------------------

print("\n=== has_glob_in_line_comment ===")
text = (
    "code line\n"
    "* Process files in prepare/*\n"
    "// log to $logdir/*.smcl\n"
    "//*****banner*****\n"
    "real code\n"
)
hits = lib.has_glob_in_line_comment(text)
# Two matches: V2 (line 2 — */-line with /* substring), V3 (line 3 — //-line
# with /* substring). V7 (line 4 — //*****) does NOT match: there is no /*
# digraph AFTER the //. V7 is detected implicitly via compute_balance instead.
assert_eq(len(hits), 2, "line-comment globs: 2 hits (V2 + V3 only)")


# ---------------------------------------------------------------------------
# 9. compute_balance (V7 false-positive avoidance, string-literal protection)
# ---------------------------------------------------------------------------

print("\n=== compute_balance ===")
# V7-only file: state-machine sees //*****  as line comments only
text = (
    "//*****************************************************\n"
    "//* SECTION: load and clean\n"
    "//*****************************************************\n"
    "use foo, clear\n"
)
opens, closes = lib.compute_balance(text)
assert_eq((opens, closes), (0, 0), "V7-only: balanced (0, 0)")

# String literal: /* and */ inside "..." excluded
text = 'display "$outdir/*.txt and $outdir/*.log"\n'
opens, closes = lib.compute_balance(text)
assert_eq((opens, closes), (0, 0), "string literal: balanced")

# Real V1 bug
text = "/* PURPOSE: clean prepare/* */\nuse foo, clear\n"
opens, closes = lib.compute_balance(text)
# Outer /* (1 open). Inside block, path-glob /* (count +1, opens=2). Real */ close.
assert_eq(opens, 2, "V1: 2 opens (outer + path-glob)")
assert_eq(closes, 1, "V1: 1 close")
assert_true(opens != closes, "V1: unbalanced as expected")

# Normal balanced file
text = "/* header */\ncode\n/* another */\n"
opens, closes = lib.compute_balance(text)
assert_eq((opens, closes), (2, 2), "normal: 2 opens, 2 closes")


# ---------------------------------------------------------------------------
# 10. classify_file (CLEAN / AUTO-FIXABLE / MANUAL-ATTENTION)
# ---------------------------------------------------------------------------

print("\n=== classify_file ===")
# CLEAN: V7-only file
text = "//*****\n//* section\n//*****\nuse foo\n"
assert_eq(lib.classify_file(text), "clean", "V7-only: CLEAN")

# CLEAN: empty/normal file
assert_eq(lib.classify_file("use foo, clear\n"), "clean", "normal code: CLEAN")
assert_eq(lib.classify_file("/* header */\ncode\n"), "clean", "balanced block: CLEAN")

# AUTO-FIXABLE: V1 path-glob
text = "/* INPUTS: $rawdir/prepare/* */\nuse foo\n"
assert_eq(lib.classify_file(text), "auto-fixable", "V1: AUTO-FIXABLE")

# AUTO-FIXABLE: V5 orphan close
text = "sort id\n\n*/\n\ngen x = 1\n"
assert_eq(lib.classify_file(text), "auto-fixable", "V5 orphan: AUTO-FIXABLE")

# MANUAL-ATTENTION: V8 artifact present
text = "/*-----\n * h\n-------<x>\nuse foo\n"
assert_eq(lib.classify_file(text), "manual-attention", "V8: MANUAL-ATTENTION")

# MANUAL-ATTENTION: unmatched /* (missing close)
text = "/* developer forgot to close\nuse foo, clear\ngen x = 1\n"
assert_eq(lib.classify_file(text), "manual-attention", "missing close: MANUAL-ATTENTION")


# ---------------------------------------------------------------------------
# 11. sweep_text (orchestrator + idempotence)
# ---------------------------------------------------------------------------

print("\n=== sweep_text (orchestrator) ===")
# Idempotence
text = "/* INPUTS: $rawdir/prepare/* */\nuse foo\n"
swept_1, _ = lib.sweep_text(text)
swept_2, _ = lib.sweep_text(swept_1)
assert_eq(swept_1, swept_2, "idempotence: second sweep produces identical text")

# Post-sweep balance
swept, info = lib.sweep_text(text)
opens, closes = lib.compute_balance(swept)
assert_eq((opens, closes), (1, 1), "post-sweep V1 is balanced")
assert_true(info["n_real"] > 0, "sweep info: n_real > 0 for V1 fix")


# ---------------------------------------------------------------------------
# 12. Fixture round-trip: all 8 variants end-to-end
# ---------------------------------------------------------------------------

print("\n=== Fixture round-trips ===")
if _FIXTURES.is_dir():
    # all_eight_variants: sweep produces the .expected.do byte-identical
    if (_FIXTURES / "all_eight_variants.do").is_file():
        input_text = read_fixture("all_eight_variants.do")
        expected = read_fixture("all_eight_variants.expected.do")
        swept, _ = lib.sweep_text(input_text)
        assert_eq(swept, expected, "all_eight_variants: sweep matches .expected.do")

    # variant_7_only: classifies as CLEAN
    if (_FIXTURES / "variant_7_only.do").is_file():
        text = read_fixture("variant_7_only.do")
        assert_eq(lib.classify_file(text), "clean", "variant_7_only fixture: CLEAN")

    # string_literal_glob: classifies as CLEAN; sweep preserves verbatim
    if (_FIXTURES / "string_literal_glob.do").is_file():
        text = read_fixture("string_literal_glob.do")
        assert_eq(lib.classify_file(text), "clean", "string_literal_glob fixture: CLEAN")

    # missing_close: classifies as MANUAL-ATTENTION
    if (_FIXTURES / "missing_close.do").is_file():
        text = read_fixture("missing_close.do")
        assert_eq(
            lib.classify_file(text),
            "manual-attention",
            "missing_close fixture: MANUAL-ATTENTION",
        )

    # over_flatten_artifact: classifies as MANUAL-ATTENTION (V8)
    if (_FIXTURES / "over_flatten_artifact.do").is_file():
        text = read_fixture("over_flatten_artifact.do")
        assert_eq(
            lib.classify_file(text),
            "manual-attention",
            "over_flatten_artifact fixture: MANUAL-ATTENTION",
        )
else:
    print(f"SKIP: fixture directory not found at {_FIXTURES}")


print("\n=== ALL TESTS PASSED ===")
