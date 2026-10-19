# Primary-Source-First — citation extraction detail

**Class:** A (universal). Pointer-loaded detail for `.claude/rules/primary-source-first.md` § Citation extraction (moved there from the rule on 2026-10-19); there is no auto-load.

The rule states what is enforced; this file documents how its two hooks, `primary-source-check.py` (PreToolUse, file edits) and `primary-source-audit.py` (Stop, conversation prose), decide what counts as a citation. Both use `.claude/hooks/primary_source_lib.py`. The escape hatch named below is the `<!-- primary-source-ok: ... -->` comment described in the rule.

## The filter stack

The hook extracts citations via an Author-Year regex, then applies the filters below. They are numbered by kind, not by execution order. The code runs blocklist (1), suffix guard (1d), all-caps (2), org skip-list (1b), cue filter (1c), hyphenated decomposition (4), sentence-start (3), allowlist (5) (`primary_source_lib.py`, the filter loop in the extractor). The drop filters are order-independent; the one order that matters is decomposition before sentence-start, so a sentence-start `Chetty-Friedman-Rockoff (2014)` is tested against the allowlist by its decomposed head.

1. **Built-in blocklist (`NEVER_SURNAMES`).** Hard-coded set of words that are *never* surnames in academic prose: function words ("the", "in", "from"), seasons, months, days of the week, document-structure words ("table", "figure", "section", "panel", "cohort"), pronouns, role-placeholder words used in citation-style examples ("Author", "Coauthor", "Editor"), book/series-title nouns ("Handbook", "Journal", "Review", "Volume"), mixed-case ADR/workflow status words ("Decided", "Superseded", "Pending", ...), changes-table verbs ("Added", "Fixed", "Merged", ...), software/tool/product names ("Stata", "Qualtrics", "Overleaf", "Photoshop", ...), document-lifecycle nouns ("Draft", "Version", "Meeting", ...), institution/program/legislation/dataset nouns ("Census", "Medicaid", "Act", "Bank", "Commission", "Compustat", "Datastream", ...), and calendar/event/award nouns ("Quarter", "Semester", "Cup", "Prize", "Medal", holidays, ...). These drop regardless of allowlist state. Collision-risk words that ARE real surnames ("Grant", "Law", "Bill", "Nielsen") are deliberately excluded — they are handled by the org skip-list or escape hatch instead.

1b. **Org skip-list (`.claude/state/primary_source_orgs.txt`).** Optional per-project list (same loader/format as the surname allowlist) of mixed-case corporate/data authors to skip ("Gallup", "Pew", Nielsen-the-company). These can't go in `NEVER_SURNAMES` safely because one project's data vendor is another project's cited author. Missing/empty file = no skipping.

1c. **Preceding-token cue filter.** A named-entity cue word ("Hurricane Katrina (2005)"), an all-caps acronym ("NSF Grant 2026"), or any other capitalized word directly before the head token ("Great Recession (2008)", "Journal of Public Economics (2019)", "Statistics Canada (2023)") marks the match as the tail of a multi-word proper noun and skips it — unless the head surname is explicitly allowlisted. Surname particles (La Ferrara, El Ghoul, De Loecker) are exempt so particle surnames still extract; the El Niño / La Niña event bigrams are carved back out. Punctuation between the preceding word and the name breaks the cue, so `IPUMS USA (Ruggles et al. 2024)` still extracts.

1d. **Abstract-noun suffix guard.** Head tokens ending in `-tion/-sion/-ism/-nomics/-demic` (length ≥ 7) or `-ment` (length ≥ 8) are event/process/doctrine nouns, essentially never surnames — "after Liberalization (1991)", "the Settlement (1998)", "under Abenomics (2013)" — caught structurally instead of by enumeration. The length floors keep short real surnames citable (`Sion`, `Nation`, `Clement`), and an allowlist entry rescues any colliding surname.

2. **All-caps token filter.** A captured surname written entirely in uppercase (length ≥ 2) is rejected. Real surnames in academic prose are written `Smith`, never `SMITH`; real two-letter surnames (`Ng`, `Wu`, `Li`) are written mixed-case. Catches status markers (`COMPLETED (2026)`, `WIP (2026)`) and acronym corporate authors (`BLS (2024)`, `OECD (2023)`, `EU (2024)`, `AY 2026`). Corporate-author citations are *data* attributions, not framing claims about research papers, so they don't require reading notes. Mixed-case surnames (`McGregor`, `DeAngelo`, `O'Brien`) still match.

3. **Sentence-start / structural-boundary filter.** A capitalized first word right after a sentence terminator (`.?!:;` or paragraph break) **or at a markdown structural boundary — line start, bullet, numbered item, heading, blockquote, table cell —** is dropped *unless* it appears in the project allowlist. This kills the dominant false-positive class in workflow docs (person + year in TODO tables, standup bullets, session-log lines) while a real citation in those positions still extracts once the surname is allowlisted. Mid-sentence prose citations are unaffected.

4. **Hyphenated-name decomposition.** A 3+ part hyphenated capitalized token (e.g., `Chetty-Friedman-Rockoff`) is split into separate surnames and the stem is built with underscores (`chetty_friedman_rockoff_2014`). This matches reading-notes filename conventions. Two-part hyphenated tokens (`Goldsmith-Pinkham`) are preserved as single hyphenated surnames since real hyphen-containing surnames are common.

5. **Project allowlist (`.claude/state/primary_source_surnames.txt`).** Optional, one lowercase surname per line. When the file is empty or missing, all matches that pass the earlier filters are accepted. Populated allowlists tighten the filter further — only Author-Year matches whose leading surname is in the allowlist extract — and rescue real citations at structural boundaries (filter 3) and after cue tokens (filter 1c). Recommended: populate as you accumulate cited authors.

### Structural guards in the regex itself (before any filter)

- **ISO-date/range guard.** A year immediately followed by dash/slash + digit is the leading component of a date or range, not a citation year — `Kickoff 2026-09-01`, `Snapshot 2026/07/15`, `Coverage 2019–2021` never extract. This kills the "CapitalizedWord YYYY-MM-DD" class generically, including words no blocklist enumerates.
- **Full author-list capture.** The author list is captured as one repeated span and split in Python, so comma-only lists (`Bohren, Imas, Rosenberg (2019)`) and the AEA 4-author form (`Smith, Jones, Brown, and Lee (2024)`) extract with the lead author intact at any author count. (The earlier 3-slot pattern restarted mid-list and silently dropped the lead author.)

### Unicode and typographic handling

The extractor ASCII-folds text before matching (NFD-decompose + strip combining marks, plus a precomposed-letter map for `ł ø ß æ œ ð þ`), so accented surnames (`Székely`, `García`, `Müller`, `Bénabou`, `Łukasz`) match as their ASCII forms. Typographic characters are folded too: curly quotes/apostrophes → ASCII apostrophe, en/em-dash → hyphen, NBSP → space — so curly-apostrophe surnames and en-dash compounds no longer mis-parse to the wrong author. Possessives are normalized (`Chetty's (2014)` → `chetty_2014`; `Smith et al.'s (2020)` and `Smith and colleagues (2020)` extract), and stems are apostrophe-free (`O'Brien` → `obrien_2020`) to match filename conventions. Reading-notes filenames should use ASCII, apostrophe-free stems — `szekely_rizzo_2013.md`, `obrien_2020.md`. The notes/PDF lookups also try a hyphen→underscore stem fallback, so a 2-part hyphenated dual-author citation (stem `szekely-rizzo_2013`) resolves to the conventional underscore filename, and accented `**Citation:**` metadata lines are folded before matching.

### Known residue (by design)

Bare place-name + year (`Tokyo 2020`), titles that are also surnames, and mixed-case polling orgs are irreducible by syntax — the org skip-list or escape hatch handles them. Particle surnames (`van Reenen`, `de Chaisemartin`) build stems without the lowercase particles; name the notes file by the extracted stem or rely on the `**Citation:**`-line match, which resolves regardless of filename.

**The structural limit (verify-loop conclusion, 2026-07-02):** "capitalized common noun + year" is a productive open class — an adversarial hunter can always mint fresh members (a new disaster, platform, or policy episode). The blocklist and suffix guards cover the high-frequency core; the tail is handled per-project by the org skip-list, the escape hatch, and block telemetry. The one *rejected* general fix, for the record: a lowercase-determiner cue ("the X (year)" ⇒ not a citation) kills legitimate eponymous forms — "the Heckman (1979) correction", "the Card and Krueger (1994) study" — and must not be added; a regression test pins this.

### Block telemetry

Every block by either hook appends a JSONL record to `.claude/state/primary-source-blocks.jsonl` (gitignored, per-project; rotates to `.old` past ~1MB; fail-open — telemetry never breaks the hook). Each record carries the timestamp, which hook fired, the source (file path or `session-prose`), and the missing stems with their status. This is the evidence base for residual-false-positive tuning: a stem that blocks repeatedly without ever gaining a notes file is a false-positive candidate (or a chronically unread citation — the judgment is human). Aggregate before a tuning pass:

```bash
jq -r '.missing[].stem' .claude/state/primary-source-blocks.jsonl | sort | uniq -c | sort -rn
```

Route confirmed false positives to the right mechanism: never-a-surname words → `NEVER_SURNAMES` upstream in the workflow repo (propagates to everyone); project-local names (orgs, tools, colleagues) → the org skip-list; one-off framing-free mentions → the escape hatch.
