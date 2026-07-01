# Proposal: Unicode-aware citation parsing in `primary_source_lib.py`

**Date:** 2026-05-07
**Status:** IMPLEMENTED 2026-07-01 (workflow commit `a4084f1`) — `_ascii_fold` with precomposed map (Change 1 + 1b) applied in `extract_citations`; hyphen→underscore fallback landed in `matching_notes_files` + `paper_pdf_exists_for` (shared lib, not per-hook helpers); regression tests + rule-doc paragraph included. Remaining per-project step: remove retroactive `primary-source-ok` overrides in BDD once the fix propagates.
**Source repo:** copy this to the main workflow repo (`claude-code-my-workflow` or wherever the canonical hooks live), apply the fix, and re-sync to projects.
**Affected files:**

- `.claude/hooks/primary_source_lib.py` — citation extractor
- `.claude/hooks/primary-source-check.py` — notes-file lookup logic
- `.claude/hooks/test_primary_source_lib.py` — regression tests
- `.claude/rules/primary-source-first.md` — documentation update

---

## Problem

The `AUTHOR_YEAR` regex at `primary_source_lib.py:104-114` uses ASCII-only character classes (`[A-Z]`, `[A-Za-z]`). This causes two related failure modes for citations containing diacritics or hyphenated dual-author names with non-ASCII characters:

### Failure mode 1 — diacritic-mid-name aborts the regex match

For "Székely-Rizzo 2013":

1. The regex tries to match starting at `S`. The first char class `[A-Z]` accepts `S`, then `[A-Za-z\-']*` accepts `z`, then hits `é` (U+00E9), which is *not* in `[A-Za-z]`. The match terminates after `Sz`. The trailing `[A-Za-z]` anchor fails (capture is too short), so this entire match attempt is rejected.
2. The regex restarts after `Sz` and finds `Rizzo` as a valid single-author surname.
3. Then `(?:\s+\(?|\(|,\s*\(?)(?P<year>(?:19|20)\d{2})` matches ` 2013`.
4. Result: stem `rizzo_2013` — wrong author, wrong stem.

The hook then blocks the edit because `master_supporting_docs/literature/reading_notes/rizzo_2013.md` doesn't exist (the actual file is `szekely_rizzo_2013.md`).

### Failure mode 2 — 2-part hyphenated dual-author surnames

Even after the diacritic problem is fixed, "Szekely-Rizzo" is one hyphenated token. The existing `_split_hyphenated_surname` only splits 3+ part hyphens (preserves 2-part tokens like `Goldsmith-Pinkham` because they're often a single author with a hyphenated surname).

But many 2-part hyphen citations *are* dual authors (Székely-Rizzo, García-Pérez, etc.) and the reading-notes file uses underscores: `szekely_rizzo_2013.md`. The current stem builder produces `szekely-rizzo_2013` which doesn't match the underscore filename.

---

## Proposed fix (two changes, complementary)

### Change 1: NFD-normalize text before regex matching (in `primary_source_lib.py`)

Strip combining marks (accents) before parsing. Handles any Latin diacritic (Western *and* Eastern European) generically.

```python
import unicodedata


def _ascii_fold(text: str) -> str:
    """NFD-decompose then strip combining marks.

    "Székely" → "Szekely"
    "García-Pérez" → "Garcia-Perez"
    "Müller" → "Muller"
    "Bénabou" → "Benabou"
    "Łukasz" → "Lukasz" (Eastern European stroke; survives NFD without combining mark, but ł is a precomposed letter that NFKD partially handles; for full coverage use a character map fallback — see Change 1b below)
    """
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )


def extract_citations(text: str) -> list[tuple[str, str]]:
    """..."""
    text = _ascii_fold(text)  # ← apply before regex extraction
    citations: list[tuple[str, str]] = []
    for match in AUTHOR_YEAR.finditer(text):
        ...
```

**What it covers:** any Latin character with a separable combining mark — é, è, à, ñ, ü, ö, č, ć, ž, š, etc. Reading-notes filenames already use ASCII stems (`szekely_rizzo_2013.md`, `garcia_cerrotti_palminteri_2021.md`), so the post-fold lookups resolve.

**What it does NOT cover (Change 1b, optional):** precomposed letters with no combining-mark decomposition — `ł`, `ø`, `ß`, `æ`, `œ`. NFD doesn't separate these. For full coverage, supplement with a character map:

```python
_PRECOMPOSED_MAP = str.maketrans({
    'ł': 'l', 'Ł': 'L',
    'ø': 'o', 'Ø': 'O',
    'ß': 'ss',
    'æ': 'ae', 'Æ': 'AE',
    'œ': 'oe', 'Œ': 'OE',
    'ð': 'd', 'Ð': 'D',
    'þ': 'th', 'Þ': 'Th',
})

def _ascii_fold(text: str) -> str:
    nfd = unicodedata.normalize('NFD', text)
    stripped = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    return stripped.translate(_PRECOMPOSED_MAP)
```

The map is short and covers the cases that matter for academic econ citations (Polish, Norwegian, German `ß`, French/Old English ligatures). Skip if simplicity is preferred — combining-mark NFD covers ~95% of real cases.

### Change 2: hyphen-to-underscore fallback for notes-file lookup (in `primary-source-check.py`)

When checking whether a reading-notes file exists for a stem, also try the underscore-substituted form. Handles the convention mismatch where a 2-part hyphenated dual-author citation maps to an underscore-separated filename.

```python
def _find_notes_file(stem: str, notes_dir: Path) -> Path | None:
    """Return a path to the notes file for `stem`, or None if not found.

    Tries the stem as-is first, then a hyphen-to-underscore fallback to
    handle 2-part hyphen-separated dual-author citations.
    """
    direct = notes_dir / f"{stem}.md"
    if direct.exists():
        return direct
    if "-" in stem:
        alt = notes_dir / f"{stem.replace('-', '_')}.md"
        if alt.exists():
            return alt
    return None
```

Replace direct `(notes_dir / f"{stem}.md").exists()` checks with calls to `_find_notes_file`.

**Edge case:** if a project has BOTH `goldsmith-pinkham_2020.md` (single hyphenated surname) AND `goldsmith_pinkham_2020.md` (different paper, two authors), the direct match wins — no ambiguity.

---

## Test cases to add to `test_primary_source_lib.py`

```python
def test_diacritic_in_first_surname_position():
    """Székely-Rizzo (2013) should parse as szekely-rizzo or szekely_rizzo."""
    citations = extract_citations("Székely-Rizzo (2013) prove the energy distance is consistent.")
    assert ("szekely-rizzo", "2013") in citations or ("szekely_rizzo", "2013") in citations
    # NOT just rizzo_2013
    assert ("rizzo", "2013") not in citations


def test_diacritic_in_single_surname():
    citations = extract_citations("Müller (2020) shows...")
    assert ("muller", "2020") in citations


def test_multiple_diacritics():
    citations = extract_citations("Bénabou and Tirole (2003)...")
    assert ("benabou_tirole", "2003") in citations


def test_garcia_cerrotti_palminteri():
    """3-author citation with diacritic in first author."""
    citations = extract_citations("García-Cerrotti, Palminteri (2021) document...")
    # Should split via _split_hyphenated_surname into 3+ parts? Probably not —
    # only 2 hyphenated parts in "García-Cerrotti". Confirm desired behavior.
    expected_stems = {"garcia-cerrotti_palminteri", "garcia_cerrotti_palminteri"}
    assert any(c[0] in expected_stems for c in citations), citations


def test_eastern_european_precomposed():
    """Łukasz (2024) should fold to lukasz_2024 (only with Change 1b)."""
    citations = extract_citations("Łukasz (2024) finds...")
    assert ("lukasz", "2024") in citations


def test_notes_lookup_underscore_fallback():
    """Stem szekely-rizzo_2013 should resolve to szekely_rizzo_2013.md."""
    # Simulate: notes_dir contains only szekely_rizzo_2013.md
    # Verify _find_notes_file returns the underscore variant when called with hyphen variant.
```

---

## Documentation update (`.claude/rules/primary-source-first.md`)

Add a paragraph in the citation-extraction section documenting:

> **Unicode handling.** The citation extractor NFD-normalizes text before regex matching, so accented surnames (Székely, García, Müller, Bénabou, Łukasz) are folded to their ASCII equivalents (Szekely, Garcia, Muller, Benabou, Lukasz). Reading-notes filenames should use these ASCII forms — `szekely_rizzo_2013.md` not `székely_rizzo_2013.md`.
>
> **Hyphen-vs-underscore fallback.** If a citation is parsed with a hyphenated stem (e.g., `szekely-rizzo_2013`), the notes-file lookup also tries the underscore form (`szekely_rizzo_2013`). This handles 2-part hyphen-separated dual-author citations that conventionally map to underscore-separated filenames.

---

## Why this matters

The current behavior blocks legitimate edits to load-bearing files when they cite papers with non-ASCII author names. The escape hatch (`<!-- primary-source-ok: stem -->`) works as a manual workaround but is auditable noise; making the parser correct removes a class of false-positive blocks entirely.

In this project alone, citations that hit the bug:

- Székely-Rizzo (2013) — energy distance method
- García-Cerrotti, Palminteri (2021) — DEG neuroeconomics
- Bénabou and Tirole (2003) — self-confidence model (if cited in future)

Likely affects every project that cites European authors. Single fix, applied once in the canonical workflow repo, propagates to all projects via the existing sync mechanism.

---

## Implementation checklist for the workflow repo

- [ ] Add `_ascii_fold` to `primary_source_lib.py` (Change 1 + 1b)
- [ ] Apply fold at the top of `extract_citations`
- [ ] Add `_find_notes_file` helper to `primary-source-check.py` and `primary-source-audit.py`; replace direct `(notes_dir / ...).exists()` checks
- [ ] Add 5–7 regression tests to `test_primary_source_lib.py`
- [ ] Update `.claude/rules/primary-source-first.md` with the Unicode-handling paragraph
- [ ] Sync to all projects (or let projects pull on next workflow refresh)
- [ ] In this project, retroactively remove `<!-- primary-source-ok: rizzo_2013, szekely_rizzo_2013 -->` overrides for Székely-Rizzo since the parser now handles it correctly
