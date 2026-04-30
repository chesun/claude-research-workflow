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


# Save the project's actual allowlist so we can restore at exit, and clamp to
# empty for the bulk of the tests so behavior is reproducible regardless of
# what the project has populated. The "sentence-start citation passes if
# surname is in allowlist" test temporarily injects a known surname.
_PROJECT_ALLOWLIST = lib.KNOWN_SURNAMES
lib.KNOWN_SURNAMES = set()


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

print("\n=== Book/series-title nouns (should not match) ===")
assert_no_match("See Methodology (2025) for details.", "'Methodology (2025)'")
assert_no_match("In Handbook (2023), it states...", "'Handbook (2023)'")
assert_no_match("Per Annual (2024), the trend continues.", "'Annual (2024)'")
assert_no_match("As Volume (2022) covers this topic.", "'Volume (2022)'")
assert_no_match("In Encyclopedia (2024), the entry is...", "'Encyclopedia (2024)'")
assert_no_match("From Journal (2023), the article notes...", "'Journal (2023)'")
assert_no_match("In Bulletin (2022), the announcement is...", "'Bulletin (2022)'")
assert_no_match("See Issue (2025) of the publication.", "'Issue (2025)'")
assert_no_match("Per Review (2023), the finding holds.", "'Review (2023)'")

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

print("\n=== Display string round-trips safely (comma+and form, not space-joined) ===")
# A 3-name display string echoed back into prose must not re-extract as
# "Rockoff (2014)" alone. The display now uses comma+and form so the
# regex's `,/and/&` separator alternation matches it.
result = lib.extract_citations(
    "Per the canonical Chetty-Friedman-Rockoff (2014) method."
)
assert len(result) == 1, f"FAIL: expected 1 citation, got {len(result)}: {result}"
stem, display = result[0]
assert stem == "chetty_friedman_rockoff_2014", f"FAIL: stem = {stem!r}"
assert display == "Chetty, Friedman, and Rockoff (2014)", (
    f"FAIL: display = {display!r}; expected comma+and form"
)
# Now feed the display string back through the extractor; should produce
# the same stem (round-trip safety).
roundtrip = lib.extract_citations(f"See {display}.")
assert len(roundtrip) == 1, f"FAIL: roundtrip extracted {len(roundtrip)} citations"
assert roundtrip[0][0] == "chetty_friedman_rockoff_2014", (
    f"FAIL: roundtrip stem = {roundtrip[0][0]!r}"
)
print("PASS: 3-name display string round-trips to same stem")

# Two-author and one-author display strings also round-trip
two_result = lib.extract_citations("Following Chetty and Friedman (2014).")
assert two_result[0][1] == "Chetty and Friedman (2014)", (
    f"FAIL: 2-name display = {two_result[0][1]!r}"
)
print("PASS: 2-name display uses 'X and Y' form")

one_result = lib.extract_citations("Following Chetty (2014).")
assert one_result[0][1] == "Chetty (2014)", f"FAIL: 1-name display = {one_result[0][1]!r}"
print("PASS: 1-name display unchanged")

print("\n=== Hyphenated compound at sentence-start (filter 3 must run before filter 2) ===")
# These tests require chetty/friedman/rockoff in the allowlist because
# sentence-start positions only pass when the head surname is allowlisted.
lib.KNOWN_SURNAMES = {"chetty", "friedman", "rockoff"}
try:
    assert_matches(
        "Chetty-Friedman-Rockoff (2014) is canonical.",
        {"chetty_friedman_rockoff_2014"},
        "hyphenated method at start of string",
    )
    assert_matches(
        "Reference: Chetty-Friedman-Rockoff (2014).",
        {"chetty_friedman_rockoff_2014"},
        "hyphenated method right after colon",
    )
    assert_matches(
        "Foo. Chetty-Friedman-Rockoff (2014) extends earlier work.",
        {"chetty_friedman_rockoff_2014"},
        "hyphenated method right after period",
    )
    assert_matches(
        "Per the canonical Chetty-Friedman-Rockoff (2014) method.",
        {"chetty_friedman_rockoff_2014"},
        "hyphenated method mid-sentence (regression guard)",
    )
    # Comma-form at sentence start (allowlist active for chetty)
    assert_matches(
        "Chetty, Friedman, and Rockoff (2014) is canonical.",
        {"chetty_friedman_rockoff_2014"},
        "comma-form three-author at sentence start",
    )
finally:
    lib.KNOWN_SURNAMES = set()

print("\n=== Negative: unknown hyphenated compound at sentence-start still rejected ===")
# With empty allowlist, sentence-start hyphenated compound has no head surname
# in any allowlist, so should be rejected.
assert_no_match(
    "Foo-Bar-Baz (2020) is the method.",
    "unknown hyphenated compound at sentence-start (no allowlist)",
)
# Even with allowlist active but missing the head:
lib.KNOWN_SURNAMES = {"chetty"}
try:
    assert_no_match(
        "Foo-Bar-Baz (2020) is the method.",
        "unknown hyphenated compound at sentence-start (allowlist missing head)",
    )
finally:
    lib.KNOWN_SURNAMES = set()

print("\n=== Sentence-start citation passes if surname is in allowlist ===")
# Temporarily inject a surname into the allowlist for this test
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
    lib.KNOWN_SURNAMES = set()  # back to empty for residual test below

print("\n=== Year-separator requirement (no shorthand-coalescing) ===")
# The original misparse: `Cameron-Miller, Eyting-2024` was coalescing into
# stem `cameron-miller_eyting-_2024` because (a) the surname char class
# allowed `Eyting-` (trailing hyphen) and (b) the year regex allowed zero
# separator. Fix requires whitespace/paren/comma before the year AND
# requires surname captures to end in a letter.
assert_no_match(
    "PDFs (Cameron-Miller, Eyting-2024) need to move.",
    "shorthand 'Eyting-2024' must not coalesce with adjacent surname",
)
assert_no_match(
    "Smith-2020 was a milestone.",
    "shorthand 'Smith-2020' alone (no separator) must not match",
)
assert_no_match(
    "References include Smith-2020.",
    "shorthand 'Smith-2020' mid-sentence must not match",
)

print("\n=== Surname-ending-in-letter constraint (residual case) ===")
# Even with year-separator, this still mis-coalesced before the
# trailing-letter constraint on the surname char class:
# `Cameron-Miller and Eyting- (2024)` -> the year sep ` (` was satisfied, so
# `second = "Eyting-"` got captured and post-stripping produced
# `cameron-miller_eyting_2024`. Anchor: surname must end in a letter.
assert_no_match(
    "We follow Cameron-Miller and Eyting- (2024) per the typo.",
    "second surname ending in trailing hyphen must not match",
)
assert_no_match(
    "Cited as Smith- (2020) somewhere.",
    "first surname ending in trailing hyphen must not match",
)
assert_no_match(
    "See Foo and Bar' (2020) for details.",
    "second surname ending in trailing apostrophe must not match",
)

print("\n=== Adjacent citations connected by 'and' (must extract both) ===")
# Variations of the original misparse case: two distinct citations connected
# by list-conjunction `and` or comma. Both must extract independently.
assert_matches(
    "We cite Eyting (2024) and Cameron-Miller (2015) together.",
    {"eyting_2024", "cameron-miller_2015"},
    "two citations joined by ' and '",
)
assert_matches(
    "Including Cameron-Miller (2015), Eyting (2024) as the relevant pair.",
    {"cameron-miller_2015", "eyting_2024"},
    "two citations comma-separated (mid-sentence)",
)
assert_matches(
    "Following Smith (2020), Jones (2021), and Brown (2022)...",
    {"smith_2020", "jones_2021", "brown_2022"},
    "three independent citations in a list",
)

print("\n=== Real two-author citation still works (regression guard) ===")
# Defensive: ensure my year-separator fix didn't break the legitimate
# two-coauthor form. `Smith and Jones (2020)` must still match as one
# citation, not two.
assert_matches(
    "Following Smith and Jones (2020), we estimate the effect.",
    {"smith_jones_2020"},
    "two-author 'X and Y (year)' form preserved",
)
assert_matches(
    "See Chetty & Friedman 2014 for the canonical version.",
    {"chetty_friedman_2014"},
    "two-author '&' + bare year preserved",
)
assert_matches(
    "We follow Smith, Jones, and Brown (2022) for the design.",
    {"smith_jones_brown_2022"},
    "three-author comma+and form preserved (mid-sentence)",
)

print("\n=== Residual: real surname at sentence start with empty allowlist ===")
# Documented as unavoidable noise; user uses escape hatch.
result = stems("Smith 2020 published a related result.")
# With empty allowlist, sentence-start Smith is dropped (good, suppresses noise)
print(f"INFO: empty-allowlist sentence-start 'Smith 2020' -> {result} (expected: empty)")

# Restore project's actual allowlist (in case anything imports the lib after)
lib.KNOWN_SURNAMES = _PROJECT_ALLOWLIST

print("\nAll tests passed.")
