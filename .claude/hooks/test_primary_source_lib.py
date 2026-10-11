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

# The tests print non-ASCII surnames (e.g. Łukasz); a Windows cp1252 console
# cannot encode them, so force UTF-8 output rather than crash mid-suite.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


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

# Same clamp for the org skip-list — tests that exercise it inject their own
# entries and restore to empty.
_PROJECT_ORG_SKIPLIST = lib.ORG_SKIPLIST
lib.ORG_SKIPLIST = set()


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

print("\n=== All-caps status markers (should not match) ===")
assert_no_match("Status: COMPLETED (2026).", "'COMPLETED (2026)'")
assert_no_match("Marked DRAFT (2025) by author.", "'DRAFT (2025)'")
assert_no_match("Phase DONE (2024) per ledger.", "'DONE (2024)'")
assert_no_match("Currently BLOCKED (2026) on review.", "'BLOCKED (2026)'")
assert_no_match("Now ACTIVE (2026) and shipping.", "'ACTIVE (2026)'")
assert_no_match("Item TODO (2026) — flag follow-up.", "'TODO (2026)'")
assert_no_match("FIXME (2026) before merge.", "sentence-start 'FIXME (2026)'")
assert_no_match("Build status WIP (2026).", "'WIP (2026)'")
assert_no_match("Mark PENDING (2025) for now.", "'PENDING (2025)'")

print("\n=== Acronym corporate authors (should not match — data citations, not framing claims) ===")
assert_no_match("Per BLS (2024) labor data.", "'BLS (2024)'")
assert_no_match("From OECD (2023) statistics.", "'OECD (2023)'")
assert_no_match("USDA (2025) reports show...", "sentence-start 'USDA (2025)'")
assert_no_match("Per IRS (2024) filings.", "'IRS (2024)'")
assert_no_match("From CDC (2023) bulletin.", "'CDC (2023)'")

print("\n=== All-caps filter does not over-fire on real surnames ===")
# Mixed-case surnames must still pass (the filter only triggers on isupper).
assert_matches("As Smith (2020) shows...", {"smith_2020"}, "'Smith (2020)' still matches")
assert_matches("Per McGregor (2019), this holds.", {"mcgregor_2019"}, "'McGregor (2019)' still matches (mixed-case)")
assert_matches("Per DeAngelo (2021), the result...", {"deangelo_2021"}, "'DeAngelo (2021)' still matches (mixed-case)")

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

print("\n=== ADR status words + changes-table verbs (should not match) ===")
assert_no_match("Status: Decided (2026) per the ADR.", "'Decided (2026)'")
assert_no_match("Marked Superseded (2026) by ADR-0021.", "'Superseded (2026)'")
assert_no_match("Left as Deferred (2026) in the tracker.", "'Deferred (2026)'")
assert_no_match("Still Open (2026) in the backlog.", "'Open (2026)'")
assert_no_match("Row reads Added (2026) in the changes table.", "'Added (2026)'")
assert_no_match("Cell says Fixed (2026) with a link.", "'Fixed (2026)'")
assert_no_match("Entry Merged (2026) into main.", "'Merged (2026)'")
assert_no_match("Item Dropped (2026) from scope.", "'Dropped (2026)'")
assert_no_match("Line Patched (2026) in hotfix.", "'Patched (2026)'")

print("\n=== ISO-date / range guard: year opening a date is not a citation ===")
# Structural guard: (?![-–—/]\d) after the year. Mid-sentence capitalized
# words followed by full dates must not extract — no blocklist entry needed.
assert_no_match("The milestone Kickoff 2026-09-01 was set by the team.", "'Kickoff 2026-09-01' (ISO date)")
assert_no_match("See the entry Baseline 2026-01-15 in the ledger.", "'Baseline 2026-01-15' (ISO date)")
assert_no_match("Per the row Snapshot 2026/07/15 in the table.", "'Snapshot 2026/07/15' (slashed date)")
assert_no_match("The panel Coverage 2019–2021 spans three years.", "'Coverage 2019–2021' (en-dash range)")
assert_no_match("The window Sample 2018-2022 covers five cohorts.", "'Sample 2018-2022' (hyphen range)")
# Real citations unaffected, including the letter-suffix form.
assert_matches("We follow Adams (2014) throughout.", {"adams_2014"}, "real citation unaffected by date guard")
assert_matches("Estimates match Adams (2014b) closely.", {"adams_2014"}, "letter-suffix citation unaffected by date guard")

print("\n=== Comma-separated author lists keep the lead author ===")
# Regression: the 3-slot regex restarted mid-list and dropped the lead
# author ('Bohren, Imas, Rosenberg (2019)' -> imas_rosenberg_2019).
assert_matches(
    "As shown in Bohren, Imas, Rosenberg (2019), beliefs distort.",
    {"bohren_imas_rosenberg_2019"},
    "comma-only 3-author list keeps lead author",
)
assert_matches(
    "See Smith, Jones, Brown, and Lee (2024) for details.",
    {"smith_jones_brown_lee_2024"},
    "AEA 4-author Oxford form keeps lead author",
)
assert_matches(
    "Per Adams, Baker, Clark, Davis, and Evans (2020), effects persist.",
    {"adams_baker_clark_davis_evans_2020"},
    "5-author list captured in full",
)
assert_matches(
    "Following Chakraborty & Kendall 2025, we elicit beliefs.",
    {"chakraborty_kendall_2025"},
    "ampersand pair still extracts",
)
assert_matches(
    "Results echo Brown et al. (2025) closely.",
    {"brown_2025"},
    "et al. still extracts lead author only",
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

print("\n=== Code-span mask: pedagogical examples are skipped ===")
# Backtick-wrapped citations are style-guide examples, not framing claims.
# The systemic fix masks them out before the regex runs.
assert_no_match(
    "Use the form `Smith (2020)` for single-author cites.",
    "inline-code citation must not match (single backticks)",
)
assert_no_match(
    "Examples: `Smith (2020)`, `Jones and Brown (2021)`, `Smith et al. (2024)`.",
    "multiple inline-code citations must not match",
)
assert_no_match(
    "```\nUse Smith (2020) and Brown (2021) as examples.\n```",
    "code-fenced block citations must not match",
)
# But real citations in surrounding prose should still match.
assert_matches(
    "We follow the form `Smith (2020)` and apply it: We cite Adams (2014) here.",
    {"adams_2014"},
    "real citation in prose still extracts even with example in backticks",
)

print("\n=== Code-span mask: edge cases ===")
# Unmatched / nested backticks shouldn't hide real citations
assert_matches(
    "We follow Adams (2014) — note the ` character is just punctuation here.",
    {"adams_2014"},
    "single stray backtick doesn't break extraction",
)
# Multiline prose where a real citation lives outside backticks
result = stems(
    "Use the syntax `Smith (2020)` in your text.\nWe follow Adams (2014).\n"
)
assert "adams_2014" in result and "smith_2020" not in result, (
    f"FAIL: expected only adams_2014, got {result}"
)
print("PASS: real citation extracts when example is on a separate line")

print("\n=== Unicode fold: accented surnames extract with ASCII stems ===")
assert_matches("As Müller (2020) shows, effects persist.", {"muller_2020"}, "diacritic single surname 'Müller'")
assert_matches(
    "Per Bénabou and Tirole (2003), confidence matters.",
    {"benabou_tirole_2003"},
    "diacritics in two-author citation 'Bénabou and Tirole'",
)
# The original bug: diacritic mid-name aborted the match and the regex
# restarted at the second name — 'Székely-Rizzo 2013' parsed as rizzo_2013.
result = stems("The estimator in Székely-Rizzo (2013) is consistent.")
assert "szekely-rizzo_2013" in result and "rizzo_2013" not in result, (
    f"FAIL: expected szekely-rizzo_2013 only, got {result}"
)
print("PASS: 'Székely-Rizzo (2013)' folds to szekely-rizzo_2013 (not rizzo_2013)")
assert_matches("Following Łukasz (2024), we proceed.", {"lukasz_2024"}, "precomposed 'Ł' folds (char map)")
assert_matches("Per García-Pérez (2019), unemployment falls.", {"garcia-perez_2019"}, "hyphenated diacritic surname")

print("\n=== Notes/PDF lookup: hyphen→underscore fallback ===")
import tempfile

with tempfile.TemporaryDirectory() as _td:
    _nd = Path(_td)
    (_nd / "szekely_rizzo_2013.md").write_text(
        "# Notes\n**Citation:** Székely-Rizzo (2013). Energy distance.\n",
        encoding="utf-8",
    )
    assert lib.notes_exist_for("szekely-rizzo_2013", _nd), (
        "FAIL: hyphen stem should resolve to underscore filename"
    )
    print("PASS: hyphen stem szekely-rizzo_2013 resolves to szekely_rizzo_2013.md")
    assert lib.notes_exist_for("szekely_rizzo_2013", _nd), "FAIL: direct stem should resolve"
    print("PASS: direct underscore stem still resolves")
    assert not lib.notes_exist_for("garcia_2020", _nd), "FAIL: unrelated stem must not resolve"
    print("PASS: unrelated stem does not resolve")
    # Accented citation-metadata line matches via per-line fold
    (_nd / "compiled_reading_notes.md").write_text(
        "## Batch\n**Citation:** Bénabou and Tirole (2003), self-confidence.\n",
        encoding="utf-8",
    )
    assert lib.notes_exist_for("benabou_tirole_2003", _nd), (
        "FAIL: accented **Citation:** line should match ASCII stem"
    )
    print("PASS: accented citation-metadata line matches ASCII stem")

with tempfile.TemporaryDirectory() as _td:
    _pd = Path(_td)
    (_pd / "szekely_rizzo_2013_energy.pdf").write_bytes(b"%PDF-1.4")
    assert lib.paper_pdf_exists_for("szekely-rizzo_2013", _pd), (
        "FAIL: hyphen stem should match underscore-named PDF"
    )
    print("PASS: hyphen stem matches underscore-named PDF")
    assert not lib.paper_pdf_exists_for("smith_2020", _pd), "FAIL: unrelated PDF stem must not match"
    print("PASS: unrelated PDF stem does not match")

print("\n=== Typographic fold (P1-a): curly quotes, en/em-dash, NBSP ===")
_folded = lib._ascii_fold("O’Brien – Smith — Jones (2020) “quoted”")
assert _folded == "O'Brien - Smith - Jones (2020) \"quoted\"", (
    f"FAIL: typographic fold produced {_folded!r}"
)
print("PASS: _ascii_fold maps curly quotes -> ', en/em-dash -> -, NBSP -> space")
assert_matches(
    "We follow O’Brien (2020) in constructing the exposure measure.",
    {"obrien_2020"},
    "curly apostrophe: O’Brien no longer truncates to wrong author 'Brien'",
)
assert_matches(
    "The Goldsmith–Pinkham (2020) decomposition of Bartik instruments.",
    {"goldsmith-pinkham_2020"},
    "en-dash folds to hyphen; lead surname no longer dropped",
)
assert_matches(
    "We use the Chetty—Friedman—Rockoff (2014) teacher value-added measure.",
    {"chetty_friedman_rockoff_2014"},
    "em-dash compound decomposes to full underscore stem",
)
# The ISO-date guard still fires after the dash fold (en-dash range folds
# to a hyphen range, which the guard's ASCII-hyphen branch already rejects).
assert_no_match(
    "The panel Window 2019–2021 spans three years.",
    "en-dash year range still rejected by ISO-date guard after fold",
)

print("\n=== Possessive handling (P1-b): 's stripped; et al.'s reaches the year ===")
assert_matches(
    "Following Chetty's (2014) mobility estimates, we define upward mobility as...",
    {"chetty_2014"},
    "ASCII possessive stripped from stem (was chetty's_2014 -> spurious block)",
)
assert_matches(
    "Following Chetty’s (2014) mobility estimates, we define upward mobility as...",
    {"chetty_2014"},
    "curly possessive extracts (was a false negative — escaped the hook)",
)
assert_matches(
    "We adopt Smith et al.'s (2020) design for the elicitation stage.",
    {"smith_2020"},
    "et al. ASCII possessive extracts (was a false negative)",
)
assert_matches(
    "We adopt Smith et al.’s (2020) design for the elicitation stage.",
    {"smith_2020"},
    "et al. curly possessive extracts (was a false negative)",
)
assert_matches(
    "As shown by Smith and colleagues (2020), attrition is differential.",
    {"smith_2020"},
    "'Author and colleagues (year)' form extracts (was a false negative)",
)
assert_matches(
    "Per Jones and coauthors (2019), effects fade.",
    {"jones_2019"},
    "'Author and coauthors (year)' form extracts",
)

print("\n=== Apostrophe stem normalization (P3-b) ===")
assert_matches(
    "We follow O'Brien (2020) in constructing the exposure measure.",
    {"obrien_2020"},
    "ASCII-apostrophe surname builds apostrophe-free stem",
)
with tempfile.TemporaryDirectory() as _td:
    _nd = Path(_td)
    (_nd / "obrien_2020.md").write_text(
        "# Notes\n**Citation:** O'Brien (2020). Exposure construction.\n",
        encoding="utf-8",
    )
    assert lib.notes_exist_for("obrien_2020", _nd), (
        "FAIL: apostrophe-free stem should resolve to apostrophe-free filename"
    )
    print("PASS: obrien_2020 stem resolves to obrien_2020.md")
    assert lib.notes_exist_for("o'brien_2020", _nd), (
        "FAIL: apostrophe stem (escape-hatch style) should still resolve"
    )
    print("PASS: o'brien_2020 stem (apostrophe form) also resolves")
    # Apostrophe in the notes FILENAME also resolves (stripped on both sides)
    (_nd / "o'connor_2019.md").write_text("# Notes\n", encoding="utf-8")
    assert lib.notes_exist_for("oconnor_2019", _nd), (
        "FAIL: apostrophe in filename should be stripped before startswith"
    )
    print("PASS: apostrophe-bearing filename o'connor_2019.md resolves")
    # Citation-metadata line with an apostrophe name matches the stripped stem
    (_nd / "compiled_batch.md").write_text(
        "## Batch\n**Citation:** D'Haultfoeuille (2018). Estimation notes.\n",
        encoding="utf-8",
    )
    assert lib.notes_exist_for("dhaultfoeuille_2018", _nd), (
        "FAIL: apostrophe citation line should match apostrophe-free stem"
    )
    print("PASS: **Citation:** D'Haultfoeuille line matches dhaultfoeuille stem")

with tempfile.TemporaryDirectory() as _td:
    _pd = Path(_td)
    (_pd / "obrien_2020_exposure.pdf").write_bytes(b"%PDF-1.4")
    assert lib.paper_pdf_exists_for("obrien_2020", _pd), (
        "FAIL: apostrophe-free stem should match PDF tokens"
    )
    print("PASS: obrien_2020 stem matches obrien-named PDF")
    assert lib.paper_pdf_exists_for("o'brien_2020", _pd), (
        "FAIL: apostrophe stem should match PDF after normalization"
    )
    print("PASS: o'brien_2020 stem matches obrien-named PDF")
    (_pd / "o'brien_2021.pdf").write_bytes(b"%PDF-1.4")
    assert lib.paper_pdf_exists_for("obrien_2021", _pd), (
        "FAIL: apostrophe in PDF filename should be stripped before tokenizing"
    )
    print("PASS: apostrophe-bearing PDF filename matches apostrophe-free stem")

print("\n=== Markdown-aware boundaries (P1-c): structural FPs suppressed ===")
assert_no_match(
    "| Task | Owner | Status |\n|---|---|---|\n| Merge review | Kramer 2026 | done |",
    "table cell, bare year (person in TODO table)",
)
assert_no_match(
    "| Reviewed by | Sun (2026) |\n| Approved | yes |",
    "table cell, paren year (reviewer metadata)",
)
assert_no_match(
    "Standup notes:\n\n- Kramer (2026) reviewed the draft tables\n- rerun bootstrap tonight",
    "bullet item opening with a person name",
)
assert_no_match(
    "> Sun (2026) approved the merge during standup.\n\nProceeding with the release.",
    "blockquote opening with a person name",
)
assert_no_match(
    "## Kramer 2026 review\n\nComments received on the intro.",
    "heading opening with a person name",
)
assert_no_match(
    "The seminar draft went out yesterday\nKramer (2026) circulated comments this morning.",
    "line start after a single newline (no blank line required)",
)
assert_no_match(
    "Next steps:\n\n1. Update the ADR index.\n2. Chen (2024) replication re-run with corrected weights.",
    "numbered-list start suppressed with empty allowlist (now consistent with bullets)",
)

print("\n=== Markdown boundaries: allowlisted citations still extract (by design) ===")
lib.KNOWN_SURNAMES = {"chen", "chetty"}
try:
    assert_matches(
        "Next steps:\n\n1. Update the ADR index.\n2. Chen (2024) replication re-run with corrected weights.",
        {"chen_2024"},
        "numbered-list citation extracts when head surname is allowlisted",
    )
    assert_matches(
        "- Chetty (2014) shows teacher effects persist.",
        {"chetty_2014"},
        "bullet-start citation extracts when allowlisted",
    )
    assert_matches(
        "| Key cite | Chetty (2014) | canonical |",
        {"chetty_2014"},
        "table-cell citation extracts when allowlisted (ADR tables stay citable)",
    )
finally:
    lib.KNOWN_SURNAMES = set()
# Mid-sentence prose citations are never boundary-suppressed.
assert_matches(
    "In the second bullet we follow Chetty (2014) closely.",
    {"chetty_2014"},
    "mid-sentence citation unaffected by markdown-boundary logic",
)

print("\n=== All-caps threshold 3 -> 2 (P2-d) ===")
assert_no_match(
    "Sample restricted to EU (2024) member states with harmonized survey items.",
    "'EU (2024)' two-letter acronym",
)
assert_no_match(
    "Enrollment counts are for AY 2026 and exclude summer sessions.",
    "'AY 2026' academic-year marker",
)
assert_matches("As Ng (2019) shows, factor selection is consistent.", {"ng_2019"}, "two-letter mixed-case surname 'Ng' still extracts")
assert_matches("Per Wu (2021), the estimator converges.", {"wu_2021"}, "two-letter mixed-case surname 'Wu' still extracts")

print("\n=== NEVER_SURNAMES additions (P2-e): software / products / models ===")
assert_no_match("We re-ran the cleaning pipeline in RStudio (2023) before handing off to the coder agent.", "'RStudio (2023)'")
assert_no_match("The dashboard mockup was built in Tableau (2025) and exported as static PNGs for the talk.", "'Tableau (2025)'")
assert_no_match("All replication code is versioned on GitHub (2025) under the lab organization.", "'GitHub (2025)'")
assert_no_match("The RA machines were upgraded to Microsoft Office 2021 over the break.", "'Office 2021'")
assert_no_match("The legacy survey terminal still runs Windows 2000 and cannot install DVC.", "'Windows 2000'")
assert_no_match("Transcripts were classified with Claude (2025) using a zero-shot prompt.", "'Claude (2025)' AI model name")
assert_no_match("Sentiment was scored with Gemini (2024) in batch mode.", "'Gemini (2024)' AI model name")
assert_no_match("Filenames are normalized per Unicode (2023) NFC before hashing.", "'Unicode (2023)' versioned standard")

print("\n=== NEVER_SURNAMES additions: cluster neighbors (verifier generalization probes) ===")
assert_no_match("References were deduplicated in Zotero (2024) before export.", "'Zotero (2024)' reference manager")
assert_no_match("Notebooks run under Jupyter (2023) on the lab server.", "'Jupyter (2023)' tool name")
assert_no_match("Earnings histories come from the Panel Study of Income Dynamics (2021) waves.", "'... Dynamics (2021)' survey tail")
assert_no_match("Tariff schedules follow the European Commission (2023) notification.", "'... Commission (2023)' institution tail")
assert_no_match("County population counts come from the Census Bureau (2024) intercensal file.", "'... Bureau (2024)' institution tail")
assert_no_match("Deflators are from the World Development Indicators (2023) release.", "'... Indicators (2023)' dataset tail")

print("\n=== NEVER_SURNAMES additions (P2-e): datasets / surveys / programs / institutions ===")
assert_no_match("We merge firm fundamentals from Compustat (2024) at the gvkey-year level.", "'Compustat (2024)'")
assert_no_match("Demographic controls come from the American Community Survey (2022) five-year estimates.", "'... Survey (2022)' tail")
assert_no_match("Expectations data come from the Understanding America Study (2023) wave.", "'... Study (2023)' tail")
assert_no_match("Our sample includes children enrolled in Head Start (2019) centers in the treated counties.", "'Head Start (2019)' tail")
assert_no_match("Eligibility is imputed from state Medicaid (2022) income thresholds.", "'Medicaid (2022)'")
assert_no_match("The post-period begins after Dodd-Frank (2010) took effect.", "'Dodd-Frank (2010)' legislation")
assert_no_match("School accountability changed under the Every Student Succeeds Act (2015) framework.", "'... Act (2015)' statute tail")
assert_no_match("GDP deflators are taken from the World Bank (2024) development indicators.", "'World Bank (2024)' tail")
assert_no_match("Rate-change dates follow the Federal Reserve (2025) FOMC calendar.", "'Federal Reserve (2025)' tail")
assert_no_match("Preliminary results were presented at the NBER Summer Institute 2025.", "'Summer Institute 2025' conference")

print("\n=== NEVER_SURNAMES additions (P2-e): calendar / events / awards ===")
assert_no_match("The pilot runs in Spring Quarter 2026 sections only.", "'Quarter 2026' calendar term")
assert_no_match("The lab sessions will be held in Suite 2026 of the economics building.", "'Suite 2026' room number")
assert_no_match("She acknowledges support from a Sloan Fellowship (2024) during the fieldwork.", "'Fellowship (2024)' award")
assert_no_match("The mechanism echoes themes from her Nobel Prize (2023) lecture on credibility.", "'Prize (2023)' award")
assert_no_match("Attendance spikes around the Qatar World Cup (2022) contaminate the control weeks.", "'World Cup (2022)' tournament tail")
assert_no_match("We drop match days from Euro 2024 to avoid crowd-size confounds.", "'Euro 2024' tournament")
assert_no_match("We exclude post Brexit (2016) trade flows from the UK sample.", "'Brexit (2016)' named event")
assert_no_match("Recruitment pauses over the Labor Day 2026 weekend.", "'Labor Day 2026' holiday tail")
assert_no_match("Treatment timing follows the UK Budget 2026 announcement.", "'UK Budget 2026' fiscal event")

print("\n=== Round-2 verifier survivors: enumeration-gap siblings ===")
assert_no_match("Figures were retouched in Photoshop (2024) before export.", "'Photoshop (2024)' software")
assert_no_match("Bond prices come from Datastream (2023) daily closes.", "'Datastream (2023)' commercial dataset")
assert_no_match("Recruiting happens in Fall Semester 2026 sections only.", "'Semester 2026' calendar term")
assert_no_match("Themes from her Clark Medal (2021) lecture recur here.", "'Medal (2021)' award")
assert_no_match("The panel pauses over Thanksgiving 2026 travel days.", "'Thanksgiving 2026' holiday")
assert_no_match("Waves resume after Christmas 2026 in all arms.", "'Christmas 2026' holiday")

print("\n=== Org skip-list (P3-a): per-project mixed-case corporate authors ===")
lib.ORG_SKIPLIST = {"pew", "blue", "gallup"}
try:
    assert_no_match(
        "Baseline attitudes are benchmarked against Pew (2024) tracking polls.",
        "org skip-list suppresses 'Pew (2024)'",
    )
    assert_no_match(
        "The pilot uses YouGov Blue (2025) sampling.",
        "org skip-list suppresses trailing token 'Blue' of 'YouGov Blue'",
    )
    assert_no_match(
        "Per Gallup (2024) polling, trust declined.",
        "org skip-list suppresses 'Gallup (2024)'",
    )
finally:
    lib.ORG_SKIPLIST = set()
# By design the skip only applies when the state file lists the org.
assert_matches(
    "Baseline attitudes are benchmarked against Pew (2024) tracking polls.",
    {"pew_2024"},
    "empty org skip-list leaves Pew extracting (documented default; per-project opt-in)",
)

print("\n=== Org skip-list loader: same pattern as the surname allowlist ===")
import os as _os

with tempfile.TemporaryDirectory() as _td:
    _state = Path(_td) / ".claude" / "state"
    _state.mkdir(parents=True)
    (_state / "primary_source_orgs.txt").write_text(
        "# per-project data vendors\nGallup\npew\n\n", encoding="utf-8"
    )
    _old_env = _os.environ.get("CLAUDE_PROJECT_DIR")
    _os.environ["CLAUDE_PROJECT_DIR"] = _td
    try:
        _loaded = lib._load_state_wordlist("primary_source_orgs.txt")
    finally:
        if _old_env is None:
            _os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            _os.environ["CLAUDE_PROJECT_DIR"] = _old_env
    assert _loaded == {"gallup", "pew"}, f"FAIL: org loader returned {_loaded}"
    print("PASS: org skip-list loader lowercases entries, skips comments/blanks")
assert lib._load_state_wordlist("nonexistent_wordlist_xyz.txt") == set(), (
    "FAIL: missing wordlist file must load as empty set"
)
print("PASS: missing wordlist file loads as empty set (mechanism inert)")

print("\n=== Preceding-token cue (filter 1c): storms, funding lines, acronym precursors ===")
# The head token here is a real or unenumerable name ("Katrina", "Grant",
# "Rotterdam") — no blocklist can carry it. The word immediately BEFORE it
# is the reliable signal: a named-entity cue word or an all-caps acronym.
assert_no_match(
    "We use Hurricane Katrina (2005) as the exogenous displacement shock.",
    "'Hurricane Katrina (2005)' named-storm cue",
)
assert_no_match(
    "Damage estimates follow Tropical Storm Sandy (2012) closely.",
    "'Storm Sandy (2012)' storm cue word",
)
assert_no_match(
    "This work was funded by NSF Grant 2026 from the economics program.",
    "'NSF Grant 2026' acronym precursor ('Grant' is a real surname; blocklist unsafe)",
)
assert_no_match(
    "Slides are due before EEA-ESEM Rotterdam 2026.",
    "'EEA-ESEM Rotterdam 2026' hyphenated-acronym precursor",
)
# Punctuation between the acronym and the name breaks the cue — the standard
# dataset-citation form "IPUMS USA (Ruggles et al. 2024)" must still extract.
assert_matches(
    "Extracts come from IPUMS USA (Ruggles et al. 2024) harmonized files.",
    {"ruggles_2024"},
    "parenthetical citation after acronym unaffected (punctuation breaks the cue)",
)
# Allowlist override: a project that actually cites author Grant can rescue
# the head surname, same escape as the sentence-start filter.
lib.KNOWN_SURNAMES = {"grant"}
try:
    assert_matches(
        "This work was funded by NSF Grant 2026 from the economics program.",
        {"grant_2026"},
        "allowlisted head surname overrides the acronym cue (escape hatch then applies)",
    )
finally:
    lib.KNOWN_SURNAMES = set()

print("\n=== Documented residue (wontfix): escape hatch / org skip-list per project ===")
# These are irreducible by blocklist: the extracted token is (or could be) a
# real citable surname, or place names that no fixed list can enumerate and
# that carry no cue word before them. The escape hatch and the per-project
# org skip-list are the designed answers; the asserts pin the residual
# behavior so a future change that alters it is noticed.
assert_matches(
    "The infrastructure shock from Tokyo 2020 construction predates our sample.",
    {"tokyo_2020"},
    "residue: host-city-plus-year (city names not enumerable; no cue word before)",
)
assert_matches(
    "The placebo window coincides with the Oppenheimer (2023) release weekend.",
    {"oppenheimer_2023"},
    "residue: film title (Oppenheimer IS a citable surname — irreducible)",
)
# The org skip-list can retire any of these per project:
lib.ORG_SKIPLIST = {"tokyo"}
try:
    assert_no_match(
        "The infrastructure shock from Tokyo 2020 construction predates our sample.",
        "org skip-list retires the host-city residue per project",
    )
finally:
    lib.ORG_SKIPLIST = set()

print("\n=== Documented residue (wontfix): particle surnames drop the particle ===")
# Space-separated particles ('Van Reenen', 'de Chaisemartin', 'van der
# Klaauw') are not joinable by the author-separator alternation, so the stem
# lacks the particle. A particle-prefix mechanism is outside the P1-P3
# roadmap; the mitigation is that a **Citation:** line in the notes file
# resolves the lookup regardless (verified below).
assert_matches(
    "See Van Reenen (2011) for the management-practices evidence.",
    {"reenen_2011"},
    "residue: capitalized particle 'Van' dropped from stem",
)
assert_matches(
    "Following de Chaisemartin and D'Haultfoeuille (2020), we use a heterogeneity-robust estimator.",
    {"chaisemartin_dhaultfoeuille_2020"},
    "residue: lowercase particle 'de' dropped; apostrophe normalized (P3-b)",
)
assert_matches(
    "Bandwidth selection follows van der Klaauw (2008).",
    {"klaauw_2008"},
    "residue: 'van der' particles dropped from stem",
)
with tempfile.TemporaryDirectory() as _td:
    _nd = Path(_td)
    (_nd / "van_reenen_2011.md").write_text(
        "# Notes\n**Citation:** Van Reenen (2011). Management practices.\n",
        encoding="utf-8",
    )
    assert lib.notes_exist_for("reenen_2011", _nd), (
        "FAIL: particle-less stem should resolve via the **Citation:** line"
    )
    print("PASS: particle-less stem reenen_2011 resolves via citation line in van_reenen_2011.md")
    (_nd / "de_chaisemartin_dhaultfoeuille_2020.md").write_text(
        "# Notes\n**Citation:** de Chaisemartin and D'Haultfoeuille (2020). Two-way FE estimators.\n",
        encoding="utf-8",
    )
    assert lib.notes_exist_for("chaisemartin_dhaultfoeuille_2020", _nd), (
        "FAIL: particle-less apostrophe-free stem should resolve via citation line"
    )
    print("PASS: chaisemartin_dhaultfoeuille_2020 resolves via citation line despite dropped particle")

print("\n=== Named macro / policy episodes (should not match) ===")
assert_no_match("Employment fell sharply during the Great Recession (2008) in our sample.", "'Great Recession (2008)' episode")
assert_no_match("Bank suspensions rose in the Depression (1933) sample years.", "'Depression (1933)' episode")
assert_no_match("Spreads widened in the Financial Crisis (2008) window.", "'Financial Crisis (2008)' episode")
assert_no_match("Attrition doubled during the Pandemic (2020) waves.", "'Pandemic (2020)' episode")
assert_no_match("Volatility fell over the Great Moderation (1985) era.", "'Great Moderation (1985)' episode")
assert_no_match("Transfers increased under the Stimulus (2009) provisions.", "'Stimulus (2009)' program episode")
assert_no_match("Spending fell after the Sequester (2013) cuts.", "'Sequester (2013)' fiscal episode")
assert_no_match("Miami wages are measured after the Boatlift (1980) natural experiment.", "'Boatlift (1980)' natural experiment")
assert_no_match("Furloughs occurred during the Shutdown (2019) weeks.", "'Shutdown (2019)' episode")
assert_no_match("Trade flows shift after the Referendum (2016) vote.", "'Referendum (2016)' political event")
assert_no_match("Yields spiked in the Taper Tantrum (2013) episode.", "'Taper Tantrum (2013)' episode")
assert_no_match("Outage exposure after the Blackout (2003) identifies the effect.", "'Blackout (2003)' episode")

print("\n=== Election / corporate-event nouns (should not match) ===")
assert_no_match("Turnout data span the Presidential Election (2016) cycle.", "'Presidential Election (2016)'")
assert_no_match("We merge the Midterms (2022) canvass files by county.", "'Midterms (2022)'")
assert_no_match("Support shifted after the Reform (2025) passed.", "'Reform (2025)'")
assert_no_match("Returns are measured around the firm's Listing (2019) date.", "'Listing (2019)' corporate event")

print("\n=== Hyphenated statute names (compound blocked; components stay citable) ===")
assert_no_match("Disclosure costs rose after Sarbanes-Oxley (2002) took effect.", "'Sarbanes-Oxley (2002)' statute")
assert_no_match("Universal banks were split under Glass-Steagall (1933) provisions.", "'Glass-Steagall (1933)' statute")
assert_no_match("Tariff retaliation followed Smoot-Hawley (1930) closely.", "'Smoot-Hawley (1930)' statute")
# The statute components remain citable as real surnames.
assert_matches("We follow Glass (1976) on meta-analysis.", {"glass_1976"}, "'Glass' alone stays a citable surname")

print("\n=== Holidays beyond the Western set (should not match) ===")
assert_no_match("Sessions avoided Ramadan (2025) fasting weeks.", "'Ramadan (2025)' holiday")
assert_no_match("Sales spike around Diwali 2024 in the treated districts.", "'Diwali 2024' holiday")
assert_no_match("Recruitment paused over Eid (2025) in both arms.", "'Eid (2025)' holiday")
assert_no_match("Offices closed for Juneteenth 2025 in all states.", "'Juneteenth 2025' holiday")
assert_no_match("The panel breaks over Hanukkah 2026 and resumes in January.", "'Hanukkah 2026' holiday")

print("\n=== Institutions / bodies (should not match) ===")
assert_no_match("Results were presented at the Econometric Society (2026) winter meetings.", "'Econometric Society (2026)' learned-society tail")
assert_no_match("Auction schedules follow the Treasury (2023) calendar.", "'Treasury (2023)'")
assert_no_match("The bill cleared Parliament (2024) in March.", "'Parliament (2024)'")
assert_no_match("Hearings continued in the Senate (2023) through spring.", "'Senate (2023)'")
assert_no_match("Rate paths follow the Fed (2024) dot plot.", "'Fed (2024)'")

print("\n=== Journal-title tail nouns (should not match) ===")
assert_no_match("The paper appeared in the Journal of Public Economics (2019) symposium issue.", "'... Public Economics (2019)' journal tail")
assert_no_match("The chapter is in the Handbook of Labor Economics (2011) volume.", "'... Labor Economics (2011)' handbook tail")
assert_no_match("Published in the Quarterly Journal of Economics (2021) spring issue.", "'... of Economics (2021)' tail after lowercase 'of'")
assert_no_match("See the Review of Economic Studies (2021) version for proofs.", "'... Economic Studies (2021)' tail")
assert_no_match("Forthcoming in the Journal of Finance (2024) June issue.", "'Journal of Finance (2024)' tail")
assert_no_match("Surveyed in the Journal of Economic Literature (2020) piece.", "'... Economic Literature (2020)' tail")
assert_no_match("A short version ran in Economics Letters (2020) that year.", "'Economics Letters (2020)' tail")
assert_no_match("Summarized in the Journal of Economic Perspectives (2019) symposium.", "'... Economic Perspectives (2019)' tail")

print("\n=== Programs / assets / products (should not match) ===")
assert_no_match("Coverage expanded under Obamacare (2014) provisions.", "'Obamacare (2014)' program")
assert_no_match("The run-up in Bitcoin (2017) prices contaminates the event window.", "'Bitcoin (2017)' asset")
assert_no_match("Summaries came from ChatGPT (2025) with a fixed prompt.", "'ChatGPT (2025)' product")
assert_no_match("Transcripts were coded with Claude Code (2026) in batch mode.", "'Claude Code (2026)' two-word product")
assert_no_match("Files sync through Google Drive (2025) shared folders.", "'Google Drive (2025)' two-word product")
assert_no_match("Tourism spiked around the Paris Olympics 2024 fortnight.", "'Paris Olympics 2024' event")

print("\n=== Capitalized-phrase precursor cue (general mechanism, filter 1c) ===")
assert_no_match("Staff visas were processed at the US Embassy Madrid 2026 desk.", "'US Embassy Madrid 2026' place tail of proper-noun phrase")
assert_no_match("Income data come from Statistics Canada (2023) public tables.", "'Statistics Canada (2023)' org tail")
assert_no_match("Panels convened at the World Economic Forum Davos 2026 meetings.", "'... Forum Davos 2026' host city after capitalized phrase")
# Sentence-start capitalization of the preceding word is positional, not a
# proper-noun phrase — real citations after it must keep extracting.
assert_matches(
    "Notably Smith (2020) reaches the same conclusion.",
    {"smith_2020"},
    "sentence-start capitalized word before a citation is exempt from the phrase cue",
)
# Capitalized name particles are part of the NAME — exempt.
assert_matches(
    "Markups are estimated following De Loecker and Warzynski (2012) throughout.",
    {"loecker_warzynski_2012"},
    "capitalized particle 'De' exempt from the phrase cue (particle-residue stem)",
)
assert_matches(
    "Utility is expected per Von Neumann and Morgenstern (1944) axioms.",
    {"neumann_morgenstern_1944"},
    "capitalized particle 'Von' exempt from the phrase cue",
)
# (A capitalized word + comma before a citation joins the author list —
# that is the documented mid-sentence people-list residue, not this cue.)
# Given-name + surname is designed suppression (same tradeoff as the acronym
# cue; AEA/Chicago in-text form is surname-only). The allowlist rescues it.
_result = stems("The seminar cited Raj Chetty (2014) as the canonical reference.")
assert _result == set(), (
    f"FAIL: given-name precursor should suppress with empty allowlist; got {_result}"
)
print("PASS: 'Raj Chetty (2014)' suppressed with empty allowlist (designed; allowlist rescues)")
lib.KNOWN_SURNAMES = {"chetty"}
try:
    assert_matches(
        "The seminar cited Raj Chetty (2014) as the canonical reference.",
        {"chetty_2014"},
        "allowlist rescues given-name + surname from the phrase cue",
    )
finally:
    lib.KNOWN_SURNAMES = set()

print("\n=== Documented residue (wontfix): awards named for real surnames ===")
# Pulitzer and Guggenheim ARE real surnames, so NEVER_SURNAMES may not carry
# them (same reasoning as Grant/Law/Bill/Nielsen). The per-project org
# skip-list is the designed retirement path; the asserts pin both sides.
assert_matches(
    "She won a Pulitzer (2023) for the investigative series.",
    {"pulitzer_2023"},
    "residue: Pulitzer is a real surname — org skip-list per project",
)
assert_matches(
    "He was awarded a Guggenheim (2025) during the fieldwork.",
    {"guggenheim_2025"},
    "residue: Guggenheim is a real surname — org skip-list per project",
)
lib.ORG_SKIPLIST = {"pulitzer", "guggenheim"}
try:
    assert_no_match(
        "She won a Pulitzer (2023) for the investigative series.",
        "org skip-list retires the Pulitzer residue per project",
    )
    assert_no_match(
        "He was awarded a Guggenheim (2025) during the fieldwork.",
        "org skip-list retires the Guggenheim residue per project",
    )
finally:
    lib.ORG_SKIPLIST = set()

print("\n=== Round-3: macro / policy / historical episode nouns (should not match) ===")
assert_no_match("Deposits contracted sharply after the Crash (1929) in our bank panel.", "'Crash (1929)' episode")
assert_no_match("Call-loan rates spiked during the Panic (1907) window.", "'Panic (1907)' episode")
assert_no_match("Valuations were inflated through the Bubble (2000) years.", "'Bubble (2000)' episode")
assert_no_match("Spreads stayed wide after the Default (2001) episode in Argentina.", "'Default (2001)' episode")
assert_no_match("Bank equity recovered after the Bailout (2008) announcement.", "'Bailout (2008)' episode")
assert_no_match("Gas lines formed during the Embargo (1973) shock.", "'Embargo (1973)' episode")
assert_no_match("Grain output collapsed during the Famine (1959) years.", "'Famine (1959)' episode")
assert_no_match("Rates were pegged until the Accord (1951) freed the Fed.", "'Accord (1951)' Treasury-Fed episode")
assert_no_match("Households spent the Rebate (2008) checks within a quarter.", "'Rebate (2008)' fiscal episode")
assert_no_match("Tourism collapsed during the Intifada (2000) period.", "'Intifada (2000)' episode")
assert_no_match("Copper output fell after the Coup (1973) in Chile.", "'Coup (1973)' episode sibling")

print("\n=== Round-3 GENERAL mechanism: abstract-noun suffix guard ===")
# -tion / -sion / -ism / -nomics / -demic heads (length >= 7) are event /
# process / doctrine nouns, never surnames — caught structurally, so fresh
# class members need no enumeration.
assert_no_match("Tariffs fell after Liberalization (1991) in India.", "'Liberalization (1991)' -tion")
assert_no_match("Eastern wages converged slowly after Reunification (1990) despite transfers.", "'Reunification (1990)' -tion")
assert_no_match("The peso collapsed following the Devaluation (1994) in December.", "'Devaluation (1994)' -tion")
assert_no_match("Migration surged after the Partition (1947) of Punjab.", "'Partition (1947)' -tion")
assert_no_match("Prices doubled daily during the Hyperinflation (1923) months.", "'Hyperinflation (1923)' -tion")
assert_no_match("Coverage rose in states adopting the Expansion (2014) early.", "'Expansion (2014)' -sion (Medicaid)")
assert_no_match("Mortality peaked during the Epidemic (1918) autumn wave.", "'Epidemic (1918)' -demic")
assert_no_match("Compliance improved in findings from the Inspection (2023) wave.", "'Inspection (2023)' -tion")
assert_no_match("The yen weakened under Abenomics (2013) easing.", "'Abenomics (2013)' -nomics")
# Fresh members the blocklist never enumerated — the point of the mechanism.
assert_no_match("Cash-intensive firms retrenched after Demonetization (2016) in India.", "'Demonetization (2016)' fresh -tion member")
assert_no_match("Output fell during Privatization (1992) in Russia.", "'Privatization (1992)' fresh -tion member")
# Length floor: short real names whose tail spells a suffix stay citable.
assert_matches(
    "The proof applies Sion (1958) to the payoff kernel.",
    {"sion_1958"},
    "'Sion (1958)' minimax theorem — protected by the length floor",
)
# The guard is a heuristic (unlike exact NEVER_SURNAMES), so an explicit
# allowlist entry rescues a colliding real surname.
lib.KNOWN_SURNAMES = {"attrition"}
try:
    assert_matches(
        "Rates follow Attrition (2020) closely.",
        {"attrition_2020"},
        "allowlist rescues a suffix-guard collision",
    )
finally:
    lib.KNOWN_SURNAMES = set()

print("\n=== Round-3: firm-event nouns (should not match) ===")
assert_no_match("Returns are measured around the Merger (2015) window.", "'Merger (2015)' corporate event")
assert_no_match("Suppliers cut exposure after the Bankruptcy (2009) filing.", "'Bankruptcy (2009)' corporate event")
assert_no_match("We run the Spinoff (2018) event study at the parent level.", "'Spinoff (2018)' corporate event")
assert_no_match("Minority bidders withdrew after the Takeover (2007) bid lapsed.", "'Takeover (2007)' corporate-event sibling")

print("\n=== Round-3: conference / lifecycle / institution nouns (should not match) ===")
assert_no_match("The draft was presented at the Symposium (2025) in June.", "'Symposium (2025)' conference-cluster gap")
assert_no_match("Earnings histories come from the Vintage (2019) file of the LEHD.", "'Vintage (2019)' data-lifecycle noun")
assert_no_match("A circular from the Ministry (2024) changed the eligibility rule.", "'Ministry (2024)' institution tail")

print("\n=== Round-3: program / legislation names (should not match) ===")
assert_no_match("Farm wages rose after the Amnesty (1986) legalized workers.", "'Amnesty (1986)' IRCA")
assert_no_match("Crop wages jumped after termination of the Bracero (1964) program.", "'Bracero (1964)' program")
assert_no_match("Housing prices fall near sites designated under Superfund (1980) rules.", "'Superfund (1980)' legislation")

print("\n=== Round-3: software / platform / crypto names (should not match) ===")
assert_no_match("All sessions were run over Zoom (2025) with recording enabled.", "'Zoom (2025)' platform")
assert_no_match("Figures were vectorized in Inkscape (2024) before submission.", "'Inkscape (2024)' software")
assert_no_match("Environments are pinned inside Anaconda (2024) for the RAs.", "'Anaconda (2024)' software")
assert_no_match("Notebooks are hosted on Colab (2025) with GPU runtimes.", "'Colab (2025)' platform")
assert_no_match("The measurement model was scripted in Mplus (2023) syntax.", "'Mplus (2023)' software")
assert_no_match("The cluster was migrated to Ubuntu 2024 images.", "'Ubuntu 2024' OS release")
assert_no_match("Retail holdings of Dogecoin (2021) spiked with the meme cycle.", "'Dogecoin (2021)' crypto asset")

print("\n=== Round-3: holidays / festivals / recurring events (should not match) ===")
assert_no_match("Beer demand spikes during Oktoberfest (2025) weeks.", "'Oktoberfest (2025)' festival")
assert_no_match("Absenteeism rises around Carnival (2024) in Brazil.", "'Carnival (2024)' festival")
assert_no_match("Ad prices peak around the Superbowl (2024) broadcast.", "'Superbowl (2024)' event")
assert_no_match("Enrollment opens for Michaelmas (2025) term in August.", "'Michaelmas (2025)' academic term")
assert_no_match("Attendance at the Biennale (2024) doubled hotel rates.", "'Biennale (2024)' festival")

print("\n=== Round-3: particle-led climate events (El Niño / La Niña bigrams) ===")
# NAME_PARTICLES exempts El/La from the phrase cue (needed for real particle
# surnames), so the bigram set carves the climate events back out.
assert_no_match(
    "Yields fell during El Niño (2015) in the treated provinces.",
    "'El Niño (2015)' particle-led named event",
)
assert_no_match(
    "Insurance losses mounted during La Niña (2022) planting seasons.",
    "'La Niña (2022)' particle-led named event",
)
# Particle-led real SURNAMES keep extracting — the exemption the bigrams
# carve into must stay intact.
assert_matches(
    "Following La Ferrara (2007), we proxy diversity with a fractional index.",
    {"ferrara_2007"},
    "'La Ferrara (2007)' still extracts (particle-residue stem)",
)
# Allowlist rescue for a project that really cites author Niño.
lib.KNOWN_SURNAMES = {"nino"}
try:
    assert_matches(
        "Yields fell during El Niño (2015) in the treated provinces.",
        {"nino_2015"},
        "allowlist rescues 'Niño' from the event bigram",
    )
finally:
    lib.KNOWN_SURNAMES = set()

print("\n=== Round-3 survivor closures: disaster/disease/treaty/labor/event nouns ===")
assert_no_match("Remittances rose after the Earthquake (2010) in Haiti.", "'Earthquake (2010)' disaster")
assert_no_match("Crop insurance claims spiked during the Drought (2012) counties.", "'Drought (2012)' disaster")
assert_no_match("Trade fell during Ebola (2014) in West Africa.", "'Ebola (2014)' disease")
assert_no_match("Births declined after Zika (2016) advisories.", "'Zika (2016)' disease")
assert_no_match("Emissions pledged under the Protocol (1997) fell short.", "'Protocol (1997)' treaty noun")
assert_no_match("Targets set by the Agreement (2015) bind unevenly.", "'Agreement (2015)' treaty noun")
assert_no_match("Wages fell after the Strike (1981) was broken.", "'Strike (1981)' labor action")
assert_no_match("Capital fled during the Peso (1994) crisis.", "'Peso (1994)' currency crisis")
assert_no_match("Output held up during the Blitz (1940) months.", "'Blitz (1940)' conflict episode")
assert_no_match("Mobility collapsed during the Quarantine (2020) order.", "'Quarantine (2020)' lifecycle")
assert_no_match("Bills stalled after the Legislature (2019) reconvened.", "'Legislature (2019)' institution")
assert_no_match("Farm income rose after Apartheid (1994) ended.", "'Apartheid (1994)' policy episode")
assert_no_match("Pilgrim spending surged during the Hajj (2010) window.", "'Hajj (2010)' calendar event")
assert_no_match("Planting shifted before the Monsoon (2019) season.", "'Monsoon (2019)' season")
assert_no_match("Viewership of the Oscars (2024) declined again.", "'Oscars (2024)' named event")
assert_no_match("STEM enrollment jumped after Sputnik (1957) launched.", "'Sputnik (1957)' named event")
assert_no_match("Slides were typeset in Quarto (2024) for the deck.", "'Quarto (2024)' software")
assert_no_match("Subjects were recruited via CloudResearch (2023) panels.", "'CloudResearch (2023)' platform")

print("\n=== -ment suffix guard (floor 8; Clement stays citable) ===")
assert_no_match("Payments from the Settlement (1998) funded the programs.", "'Settlement (1998)' -ment guard")
assert_no_match("Turnout rose after the Amendment (1971) lowered the age.", "'Amendment (1971)' -ment guard")
assert_no_match("Migration surged after the Enlargement (2004) round.", "'Enlargement (2004)' -ment guard")
assert_no_match("Markets moved after the Impeachment (2019) vote.", "'Impeachment (2019)' -ment guard")
assert_matches("The estimator follows Clement (2007) closely.", {"clement_2007"}, "'Clement (2007)' (7 chars) below -ment floor — citable")

print("\n=== Collision exclusions stay citable (skip-list residue, not blocklist) ===")
assert_matches("We follow Flood (2019) on exchange-rate regimes.", {"flood_2019"}, "'Flood (2019)' real surname not blocklisted")
assert_matches("Estimates match Julia (2021) on network effects.", {"julia_2021"}, "'Julia (2021)' not blocklisted (skip-list residue)")
assert_matches("As shown in the Heckman (1979) correction literature.", {"heckman_1979"}, "eponymous 'the Heckman (1979) correction' still extracts")

print("\n=== Block telemetry: log_block writes, rotates, fails open ===")
import json as _json
import os as _os
import tempfile as _tempfile

with _tempfile.TemporaryDirectory() as _td:
    _prev = _os.environ.get("CLAUDE_PROJECT_DIR")
    _os.environ["CLAUDE_PROJECT_DIR"] = _td
    try:
        lib.log_block("primary-source-check", "decisions/0001_test.md",
                      [("smith_2020", "Smith (2020)", "MISSING_NOTES_NO_PDF")])
        _log = Path(_td) / ".claude" / "state" / "primary-source-blocks.jsonl"
        assert _log.is_file(), "FAIL: log file not created"
        _rec = _json.loads(_log.read_text().splitlines()[0])
        assert _rec["hook"] == "primary-source-check", _rec
        assert _rec["source"] == "decisions/0001_test.md", _rec
        assert _rec["missing"][0]["stem"] == "smith_2020", _rec
        assert _rec["missing"][0]["status"] == "MISSING_NOTES_NO_PDF", _rec
        assert "ts" in _rec, _rec
        print("PASS: log_block writes a well-formed JSONL record")

        # Rotation: inflate past the 1MB threshold, then log again.
        _log.write_text("x" * (lib._BLOCK_LOG_MAX_BYTES + 1))
        lib.log_block("primary-source-audit", "session-prose",
                      [("jones_2021", "Jones (2021)", "NOTES_NOT_READ_IN_SESSION")])
        assert (Path(_td) / ".claude" / "state" / "primary-source-blocks.jsonl.old").is_file(), (
            "FAIL: oversized log not rotated to .old"
        )
        _lines = _log.read_text().splitlines()
        assert len(_lines) == 1 and _json.loads(_lines[0])["hook"] == "primary-source-audit"
        print("PASS: oversized log rotates to .old; fresh log gets the new record")
    finally:
        if _prev is None:
            _os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            _os.environ["CLAUDE_PROJECT_DIR"] = _prev

# Fail-open: unwritable state dir must not raise.
_prev = _os.environ.get("CLAUDE_PROJECT_DIR")
_os.environ["CLAUDE_PROJECT_DIR"] = "/dev/null/not-a-dir"
try:
    lib.log_block("primary-source-check", "x.md", [("a_2020", "A (2020)", "MISSING_NOTES_NO_PDF")])
    print("PASS: log_block fails open on unwritable state dir")
finally:
    if _prev is None:
        _os.environ.pop("CLAUDE_PROJECT_DIR", None)
    else:
        _os.environ["CLAUDE_PROJECT_DIR"] = _prev

print("\n=== Residual: real surname at sentence start with empty allowlist ===")
# Documented as unavoidable noise; user uses escape hatch.
result = stems("Smith 2020 published a related result.")
# With empty allowlist, sentence-start Smith is dropped (good, suppresses noise)
print(f"INFO: empty-allowlist sentence-start 'Smith 2020' -> {result} (expected: empty)")

# Restore project's actual lists (in case anything imports the lib after)
lib.KNOWN_SURNAMES = _PROJECT_ALLOWLIST
lib.ORG_SKIPLIST = _PROJECT_ORG_SKIPLIST

print("\nAll tests passed.")
