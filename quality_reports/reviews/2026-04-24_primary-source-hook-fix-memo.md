# Primary-Source Hook: Diagnosis and Universal Fix Memo

<!-- primary-source-ok: only_2002, available_2002, spring_2015, calschls_2017, the_2022, in_2024, fall_2024, summer_2003, winter_1999, nsc_2018, caaspp_2017, acs_2015, nhanes_2020, lehd_2010, ipums_2022, naven_2022, chetty_2014, smith_jones_2024, smith_jones_brown_2024, chetty_friedman_rockoff_2014 -->
<!-- primary-source-ok: chetty-friedman-rockoff_2014 -->
<!-- primary-source-ok: goldsmith-pinkham-sorkin-swift_2020 -->
<!-- primary-source-ok: bertrand-duflo-mullainathan_2004 -->
<!-- This memo IS about the hook's false-positive behaviour. All citations below are demonstration test cases, not new framing claims. The hyphen-containing stems are placed in separate escape comments because the hook's escape-hatch regex `[^-]+` truncates a stem list at the first hyphen -- a third bug documented in section 9 below. -->

**Audience:** Claude in the `claude-code-my-workflow` repo (where the hook ships).
**Files affected:**

- `.claude/hooks/primary_source_lib.py` (shared logic)
- `.claude/hooks/primary-source-check.py` (PreToolUse Edit/Write)
- `.claude/hooks/primary-source-audit.py` (Stop)
- `.claude/state/primary_source_surnames.txt` (template)
- `.claude/rules/primary-source-first.md` (docs)

**Symptom in the field:** During a normal context-loading session in a fresh project (`va_consolidated`), the hook blocked **6+ load-bearing edits** in a row with false-positive citation matches. The hook chained block messages every turn, including the Stop audit, costing roughly 1-2 minutes per false-positive resolution and forcing manual `<!-- primary-source-ok: ... -->` escape comments on routine session-log updates. Worse, the escape-hatch regex itself is broken in a way that prevents recovery in the case the memo most needs to discuss.

---

## 1. Reproduction

The current `AUTHOR_YEAR` regex in `primary_source_lib.py`:

```python
AUTHOR_YEAR = re.compile(
    r"""
    \b
    (?P<first>[A-Z][A-Za-z\-']+)
    (?:\s*(?:,|and|&)\s*(?P<second>[A-Z][A-Za-z\-']+))?
    (?:\s*(?:,\s*and|&)\s*(?P<third>[A-Z][A-Za-z\-']+))?
    (?:\s+et\s+al\.?)?
    \s*\(?(?P<year>(?:19|20)\d{2})[a-z]?\)?
    """,
    re.VERBOSE,
)
```

When the allowlist (`primary_source_surnames.txt`) is empty -- the default for new projects -- the extractor accepts every Author-Year regex match. Tested against real session prose, it produces:

| Input prose | Extracted stem | Real citation? |
|---|---|---|
| sentence-start adverb + year-range | sentence-start adverb stem | NO |
| sentence-start adjective + year-range | sentence-start adjective stem | NO |
| season + cohort year (e.g., spring/2015) | season stem | NO |
| dataset acronym + year (e.g., calschls/2017) | acronym stem | NO |
| definite article + year | article stem | NO |
| three-name hyphenated method + year | hyphenated-as-one-token stem | NOMINAL (real paper, but stem treats whole hyphenated string as one surname; the actual reading-notes file would use underscores). The existence check fails because filename token-split won't recover the surnames. |
| single surname + year in mid-sentence | clean stem | YES |
| two surnames joined with "and" + year | clean stem | YES |

The first 6 of these are blocking on routine prose. Only the last 2 are real citations.

---

## 2. Root causes

There are **four distinct failure modes** the regex hits, in rough frequency order:

### 2a. Sentence-start false positives (most common)

Capitalized first words of sentences followed nearby by a year. Common offenders observed in actual session prose: sentence-start function words and adverbs ("only", "available", "the", "in", "from", "on", "for", "our", "we", "this", "these", "when", "where", "both", "all", "some", "most"). Any sentence beginning with a capitalised English function word followed by a year-or-year-range trips the regex.

The current regex's `\b` boundary does not distinguish "start of sentence" from "after a comma." A position-aware filter is needed.

### 2b. Cohort / season labels

Season-plus-year strings. Cohort labels are common in education research, panel data, and any time-indexed empirical work. They will appear in **any** session-log or paper-map that describes data structure. This is a permanent, unfixable false-positive class without explicit handling.

### 2c. Data-source / dataset names

Acronym-plus-year. Acronyms followed by years are extremely common dataset references. The regex currently treats them as Author-Year because the regex doesn't distinguish all-caps acronyms from mixed-case surnames, and mixed-case dataset names specifically look exactly like a surname.

### 2d. Method-name compounds

Three-or-more-name hyphenated method references. Multi-author method references written with hyphens (instead of commas + ampersand) get captured as a single surname token. The resulting hyphenated stem won't match a normal reading-notes filename (which uses underscores) or a proper bib-key.

This one is half-real (the underlying paper IS a real citation) but the stem is wrong, so the hook still incorrectly blocks even when the notes file exists.

---

## 3. Suggested universal fixes

Three orthogonal layers. Pick all three for full coverage:

### Fix 1: Sentence-start filter (addresses 2a)

Before checking the allowlist, reject any candidate whose `match.start()` position is at start-of-document or immediately after a sentence terminator (`.`, `?`, `!`, `:`, `;`, `\n\n`) plus optional whitespace. Implementation:

```python
SENTENCE_BOUNDARY = re.compile(r"(?:\A|[.?!:;]\s+|\n\s*\n)\s*$")

def _is_sentence_start(text: str, pos: int) -> bool:
    return bool(SENTENCE_BOUNDARY.search(text[:pos]))
```

Then in `extract_citations`:

```python
for match in AUTHOR_YEAR.finditer(text):
    if _is_sentence_start(text, match.start()):
        if not (allowlist_active and first.lower() in KNOWN_SURNAMES):
            continue
    ...
```

This preserves real sentence-start citations when the allowlist is populated, while filtering sentence-start function words regardless.

### Fix 2: Built-in blocklist for common false-positive tokens (addresses 2a + 2b + partly 2c)

Add a hard-coded blocklist of words that are NEVER surnames, applied independent of the allowlist. This is needed because new projects ship with empty allowlists, and the hook should be reasonable on day 1.

```python
NEVER_SURNAMES = frozenset({
    "the", "a", "an", "this", "these", "those", "that",
    "in", "on", "at", "from", "for", "to", "by", "with", "of",
    "we", "our", "us", "i", "you", "your", "he", "she", "they", "their",
    "all", "some", "most", "both", "each", "every", "any", "no",
    "only", "also", "even", "still", "yet", "however", "moreover",
    "additionally", "furthermore", "thus", "therefore", "hence",
    "available", "important", "notable", "key", "main", "primary",
    "when", "where", "why", "how", "what", "which", "who", "whose",
    "if", "unless", "until", "while", "since", "because", "although",
    "despite", "given", "based", "using", "according", "see",
    "spring", "summer", "fall", "autumn", "winter",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
    "table", "figure", "panel", "column", "row", "section", "appendix",
    "chapter", "footnote", "equation", "model", "specification",
    "step", "stage", "phase", "round", "wave", "cohort", "year", "yr",
})
```

Apply in `extract_citations`:

```python
if first.lower() in NEVER_SURNAMES:
    continue
```

This kills the common cohort/season/sentence-start false positives without any project configuration. The list is conservative -- only words that have effectively zero chance of being a real surname.

### Fix 3: Hyphenated-name decomposition (addresses 2d)

When the captured `first` group contains 2+ hyphens AND each segment looks like a proper name, split it and treat as multi-author. Implementation:

```python
def _split_hyphenated_surname(token: str) -> list[str]:
    parts = token.split("-")
    if len(parts) < 3:
        return [token]
    if all(p[:1].isupper() and p[1:].isalpha() and len(p) >= 2 for p in parts):
        return parts
    return [token]
```

Then in extraction, replace `first` with its split if applicable, and build the stem from all parts joined by `_`. The stem becomes underscore-separated, matching a properly-named reading-notes file.

### Fix 4 (small but useful): Acronym handling (addresses 2c more thoroughly)

Hyphenation handling alone won't catch dataset acronyms followed by years. Cleanest fix: combine the blocklist (Fix 2) with a runtime supplement loaded from a project-level "known-acronyms" file, e.g. `.claude/state/primary_source_acronyms.txt`. Project owners populate this with their dataset acronyms. Default-empty is fine because the blocklist already catches the common cases.

Recommended: **Fix 2's blocklist plus a project-extensible acronyms file** named consistently with the surname allowlist.

---

## 4. Project-side responsibility (separate from the universal fix)

The hook documentation (`primary-source-first.md`) explicitly says: when `primary_source_surnames.txt` is empty, the hook is in maximum-noise mode. So part of the answer is "every project must populate that file before serious work."

The va_consolidated project will populate it as part of normal onboarding -- TODO already lists this. Suggested initial content (lowercase surnames, one per line):

```
chetty
friedman
rockoff
naven
kane
staiger
hanushek
rivkin
koedel
carrell
kurlaender
martorell
sun
angrist
deming
abdulkadiroglu
beuermann
jackson
hubbard
mountjoy
card
altonji
rothstein
mbekeani
dobbie
hoxby
goldstein
veiga
jacob
jennings
backes
kraft
davis
phillips
purkey
sammons
bloom
pischke
```

Even a populated allowlist won't fix one residual case: when a real surname is at sentence start and is followed by a year due to coincidence. There's no clean automated fix for this without heavy NLP. Leave it as residual noise, addressable per-incident with the `primary-source-ok` escape hatch.

---

## 5. Implementation priority for the workflow-repo Claude

Order by impact-per-effort:

1. **Fix 9 (escape-hatch regex bug, see section 9)** -- ONE line change. Without this, the escape hatch itself is broken when stems contain hyphens. **Highest priority.**
2. **Fix 2 (built-in blocklist)** -- 20 lines, eliminates ~70% of observed false positives. Zero project configuration required.
3. **Fix 1 (sentence-start filter)** -- 10 lines, eliminates the rest of sentence-start false positives.
4. **Fix 3 (hyphen split)** -- 15 lines, fixes method-name compound stems so they correctly match notes files.
5. **Update `primary-source-first.md`** -- document the new blocklist behavior and the recommendation that projects populate the allowlist on init.
6. **Optional: project-extensible acronyms file** -- only if Fix 2 isn't enough in practice.

Total estimated work: under 110 LOC + tests + doc update. Single PR.

---

## 6. Test cases for regression

After implementing the fixes, the regex should produce these results (run as a unit test). For brevity these are referred to by description rather than written verbatim, since spelling them out triggers the bug being fixed. The test fixtures should include:

- sentence-start adverb + year-range -> none
- sentence-start adjective + year-range -> none
- season + cohort year -> none
- dataset acronym + year -> none
- "Table 2 (2024)" -> none
- "Figure 3 (2025) shows..." -> none
- definite-article + year -> none
- preposition-at-sentence-start + year -> none
- three-name hyphenated method + year -> single underscore-joined stem
- single surname + year mid-sentence -> single stem
- two surnames + year -> two-name stem
- three surnames + year -> three-name stem
- residual case: real surname at sentence start + unrelated year -> stem (UNAVOIDABLE; user's escape hatch handles)

Plus an escape-hatch regression test:

- escape comment containing a hyphenated stem -> the stem is recognised in full

---

## 7. Related issue: Stop-hook turn-end churn

Even with regex fixes, there's a separate UX problem: the Stop audit runs at every turn-end, scanning the **entire** session prose. So if I write an escape comment in turn 5, it satisfies turn 5's audit, but a NEW false positive in turn 6's prose triggers a fresh block. This is correct in theory but creates the impression of "the hook keeps blocking me" because the user only sees the latest block.

Possible mitigation: have the Stop audit cache satisfied stems in `.claude/state/session_satisfied_stems.json` keyed by session ID, and only re-block on stems that haven't been satisfied yet. Out of scope for this memo but worth filing.

---

## 8. Summary deliverable for the workflow-repo Claude

> Implement Fixes 9, 1, 2, and 3 in `.claude/hooks/primary_source_lib.py`. Add unit tests covering the cases in section 6. Update `.claude/rules/primary-source-first.md` to document the new built-in blocklist and the recommendation that projects populate the surname allowlist on init. Reference this memo's section numbers in the PR description.

---

## 9. NEW BUG: Escape-hatch regex truncates on hyphens

While writing this very memo, I hit a separate bug in the hook. The escape-hatch regex at line 95-98 of `primary_source_lib.py`:

```python
ESCAPE_HATCH = re.compile(
    r"<!--\s*primary-source-ok:\s*(?P<stems>[^-]+)-->",
    re.IGNORECASE,
)
```

The character class `[^-]+` matches one-or-more non-hyphen characters. This means as soon as the regex encounters a stem with a hyphen in it (e.g., `chetty-friedman-rockoff_2014`, which is exactly the buggy stem produced by problem 2d), the match stops at the hyphen. Any stems listed *after* the hyphen-containing one in the comment are silently dropped.

In other words: **the escape hatch is broken precisely for the stems most likely to need escaping** -- the buggy hyphenated method-name stems that Fix 3 is supposed to repair. Concretely, in this memo I had to write four separate `<!-- primary-source-ok: ... -->` comments to escape all the test-case stems, because consolidating them into one comment caused everything after the first hyphen to be ignored.

### The one-line fix

Change `[^-]+` to a more careful pattern that allows hyphens inside stems but stops at the closing `-->`:

```python
ESCAPE_HATCH = re.compile(
    r"<!--\s*primary-source-ok:\s*(?P<stems>.+?)\s*-->",
    re.IGNORECASE | re.DOTALL,
)
```

Using `.+?` (non-greedy "any char") with the explicit `-->` terminator allows stems with hyphens. `re.DOTALL` lets the comment span multiple lines if a project has many stems to escape.

### Test for it

```python
def test_escape_hatch_with_hyphenated_stem():
    text = "<!-- primary-source-ok: smith_2020, chetty-friedman-rockoff_2014, jones_2021 -->"
    stems = extract_escaped_stems(text)
    assert stems == {"smith_2020", "chetty-friedman-rockoff_2014", "jones_2021"}
```

The current regex fails this test (it would return `{"smith_2020"}` and silently drop the other two).
