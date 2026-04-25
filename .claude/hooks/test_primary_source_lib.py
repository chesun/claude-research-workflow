#!/usr/bin/env python3
"""Regression tests for primary_source_lib.py false-positive fixes.

Run with: python3 .claude/hooks/test_primary_source_lib.py

Tests cover the cases documented in
quality_reports/reviews/2026-04-24_primary-source-hook-fix-memo.md §6.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_lib():
    lib_path = Path(__file__).resolve().parent / "primary_source_lib.py"
    spec = importlib.util.spec_from_file_location("primary_source_lib", lib_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lib = _load_lib()


# --- Helpers ---------------------------------------------------------------


def stems(text: str) -> set[str]:
    """Return the set of stems extracted from `text`."""
    return {s for s, _ in lib.extract_citations(text)}


def assert_no_match(text: str, label: str) -> None:
    found = stems(text)
    if found:
        print(f"FAIL: {label}")
        print(f"  text:    {text!r}")
        print(f"  matched: {found}")
        sys.exit(1)
    print(f"PASS: {label}")


def assert_matches(text: str, expected: set[str], label: str) -> None:
    found = stems(text)
    if found != expected:
        print(f"FAIL: {label}")
        print(f"  text:     {text!r}")
        print(f"  expected: {expected}")
        print(f"  found:    {found}")
        sys.exit(1)
    print(f"PASS: {label}")


def assert_escape_stems(text: str, expected: set[str], label: str) -> None:
    found = lib.extract_escaped_stems(text)
    if found != expected:
        print(f"FAIL: {label}")
        print(f"  text:     {text!r}")
        print(f"  expected: {expected}")
        print(f"  found:    {found}")
        sys.exit(1)
    print(f"PASS: {label}")


# --- §6 regression cases (allowlist empty by default in test env) ----------

print("=== Sentence-start function-word + year (should not match) ===")
assert_no_match("Only data from 2015 to 2020 was available.", "sentence-start 'Only'")
assert_no_match("Available 2002 records show no anomalies.", "sentence-start 'Available'")
assert_no_match("The 2022 paper introduced this approach.", "sentence-start 'The'")
assert_no_match("In 2024 the policy was revised.", "sentence-start 'In'")
assert_no_match("From 1999 onward enrollment grew.", "sentence-start 'From'")
assert_no_match("This 2020 cohort shows strong effects.", "sentence-start 'This'")
assert_no_match("These 2019 estimates are preliminary.", "sentence-start 'These'")

print("\n=== Cohort / season labels (should not match) ===")
assert_no_match("Spring 2015 enrollment data.", "season 'Spring 2015'")
assert_no_match("Fall 2018 saw a decline.", "season 'Fall 2018'")
assert_no_match("Summer 2003 data is missing.", "season 'Summer 2003'")
assert_no_match("Winter 1999 cohort.", "season 'Winter 1999'")
assert_no_match("The May 2020 wave.", "month 'May 2020' (sentence-start 'The' filter)")

print("\n=== Document-structure words (should not match) ===")
assert_no_match("Table 2 (2024) shows the result.", "Table N (year)")
assert_no_match("Figure 3 (2025) illustrates this.", "Figure N (year)")
assert_no_match("Section 4 (2023) discusses identification.", "Section N (year)")
assert_no_match("Cohort 2015 had 1,200 students.", "'Cohort YYYY'")

print("\n=== Sentence-start preposition + year (should not match) ===")
assert_no_match("On 2018 records.", "sentence-start 'On'")
assert_no_match("For 2020 data, see appendix.", "sentence-start 'For'")
assert_no_match("By 2019 the estimator had been adopted.", "sentence-start 'By'")

print("\n=== Real citations (should match) ===")
assert_matches(
    "We follow Chetty (2014) in this approach.",
    {"chetty_2014"},
    "single surname mid-sentence",
)
assert_matches(
    "Following Chetty and Friedman (2014), we estimate...",
    {"chetty_friedman_2014"},
    "two surnames + year",
)
assert_matches(
    "See Chetty, Friedman, and Rockoff (2014) for the original estimator.",
    {"chetty_friedman_rockoff_2014"},
    "three surnames + year",
)

print("\n=== Hyphenated method-name compound (should split into stem) ===")
assert_matches(
    "Following the Chetty-Friedman-Rockoff (2014) approach...",
    {"chetty_friedman_rockoff_2014"},
    "hyphenated 3-name compound -> underscore-joined stem",
)
assert_matches(
    "We use Goldsmith-Pinkham-Sorkin-Imbens (2020) shift-share inference.",
    {"goldsmith_pinkham_sorkin_imbens_2020"},
    "hyphenated 4-name compound -> underscore-joined stem",
)

print("\n=== Two-name hyphenated should NOT split (could be a real hyphen surname) ===")
# E.g. "Goldsmith-Pinkham (2020)" — Goldsmith-Pinkham is a single hyphenated
# surname. Don't decompose. It will produce stem "goldsmith-pinkham_2020".
result = stems("We follow Goldsmith-Pinkham (2020) on shift-shares.")
assert "goldsmith-pinkham_2020" in result, (
    f"FAIL: 2-part hyphenated surname should remain joined; got {result}"
)
print("PASS: 2-part hyphenated surname remains joined")

print("\n=== Escape hatch handles hyphenated stems ===")
assert_escape_stems(
    "<!-- primary-source-ok: smith_2020, chetty-friedman-rockoff_2014, jones_2021 -->",
    {"smith_2020", "chetty-friedman-rockoff_2014", "jones_2021"},
    "escape hatch with 3 stems including hyphenated middle",
)
assert_escape_stems(
    "<!-- primary-source-ok: chetty-friedman-rockoff_2014 -->",
    {"chetty-friedman-rockoff_2014"},
    "escape hatch with single hyphenated stem",
)
assert_escape_stems(
    """<!-- primary-source-ok:
    smith_2020,
    chetty-friedman-rockoff_2014,
    goldsmith-pinkham-sorkin_2020
    -->""",
    {"smith_2020", "chetty-friedman-rockoff_2014", "goldsmith-pinkham-sorkin_2020"},
    "escape hatch spans multiple lines (DOTALL)",
)

print("\n=== Sentence-start citation passes if surname is in allowlist ===")
# Temporarily inject a surname into the allowlist for this test
saved_allowlist = lib.KNOWN_SURNAMES
lib.KNOWN_SURNAMES = {"chetty"}
try:
    assert_matches(
        "Chetty (2014) shows that teacher quality matters.",
        {"chetty_2014"},
        "sentence-start real citation passes when in allowlist",
    )
    # And: when 'Only' is at sentence start AND a real citation appears mid-
    # sentence, NEVER_SURNAMES drops "Only" but the mid-sentence "Chetty (2014)"
    # still matches correctly.
    assert_matches(
        "Only Chetty (2014) provides this estimator.",
        {"chetty_2014"},
        "sentence-start 'Only' drops; mid-sentence 'Chetty' still extracts",
    )
finally:
    lib.KNOWN_SURNAMES = saved_allowlist

print("\n=== Residual: real surname at sentence start with empty allowlist ===")
# Documented as unavoidable noise; user uses escape hatch.
result = stems("Smith 2020 published a related result.")
# With empty allowlist, sentence-start Smith is dropped (good, suppresses noise)
print(f"INFO: empty-allowlist sentence-start 'Smith 2020' -> {result} (expected: empty)")

print("\nAll tests passed.")
