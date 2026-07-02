# Primary-Source Hook — False-Positive Analysis and Improvement Roadmap

**Date:** 2026-07-01
**Author:** Claude (analysis session, post citation-guard-hardening umbrella)
**Target:** `.claude/hooks/primary_source_lib.py`
**Status:** Active
**Method:** every claim below was verified empirically by probing the *live* extractor (post-`a4084f1`) with candidate texts; probe script preserved at the session scratchpad, results reproduced inline. No speculative entries — "confirmed" means the extractor fired on the probe today.

<!-- primary-source-ok: kramer_2026, kramer_sun_2026 -->

---

## 1. Confirmed false-positive classes (extractor fires; no citation intended)

### 1a. Structural: position contexts the sentence-start filter cannot see — **the dominant class**

`SENTENCE_BOUNDARY` only recognizes `.?!:;` + space and blank lines. Markdown structure is invisible to it, so a capitalized name + year fires in exactly the documents this hook scopes (session logs, plans, reviews, TODO tables are full of these):

| Context | Probe | Extracted |
|---|---|---|
| Table cell | `\| Kramer 2026 \| done \|` | `kramer_2026` |
| Line start after single `\n` | `...yesterday\nKramer (2026) reviewed` | `kramer_2026` |
| Bullet item | `- Kramer (2026) reviewed the draft` | `kramer_2026` |
| Heading | `## Kramer 2026 review` | `kramer_2026` |

The blank-line requirement (`\n\s*\n`) means a line that starts mid-paragraph gets *no* sentence-start protection. Most real prose citations are mid-sentence, so tightening this costs little.

### 1b. Software / platform / tool names (mixed-case, so the all-caps filter can't catch them)

Confirmed firing: `Stata (2023)` → `stata_2023`; `Qualtrics (2025)`; `Prolific (2024)`; `Overleaf (2026)`. These words are never surnames — safe for `NEVER_SURNAMES`.

### 1c. Datasets, programs, institutions, legislation, places

Confirmed firing: `Census (2020)`, `Medicare (2023)`, `CARES Act (2020)` → `act_2020`, `Room 2026` → `room_2026`. Candidate cluster (same character): `medicaid`, `university`, `institute`, `center`, `committee`, `congress`, `census`, `room`, `office`, `form`, `act`. **Surname-collision exclusions — do NOT blocklist:** `Grant`, `Law`, `Bill`, `Nielsen` (all real surnames).

### 1d. Document-lifecycle nouns the verb cluster missed

The 2026-07-01 pass added the *verbs* (`added`, `fixed`, ...) but not the *nouns*. Confirmed firing: `Draft (2026)`, `Version (2026)`, `Meeting (2026)`. Candidate cluster: `draft`, `version`, `release`, `update`, `plan`, `memo`, `meeting`, `seminar`, `conference`, `workshop`, `agenda`, `milestone`, `deliverable`, `submission`, `deadline`.

### 1e. Two-letter all-caps acronyms

The all-caps filter requires length ≥ 3. Confirmed firing: `FY 2026` → `fy_2026`, `AI (2026)` → `ai_2026`. (`US (2024)` survives only by luck — "us" is in the pronoun blocklist.) Real two-letter surnames (`Ng`, `Wu`, `Li`) are written mixed-case in prose, never `NG`, so lowering the threshold to 2 is safe.

### 1f. Corporate/org authors in mixed case

Confirmed firing: `Gallup (2024)` → `gallup_2024`. Same class: Pew, Brookings, RAND (caps-filtered), IPUMS (caps-filtered). Per the rule's own philosophy, corporate data attributions don't require reading notes — but mixed-case org names can't go in `NEVER_SURNAMES` safely (`Nielsen` is a common surname). Needs a different mechanism (see §4, P3-a).

### 1g. Residual: people lists in project prose

Confirmed firing: `coordination with Kramer, Sun (2026) on logistics` → `kramer_sun_2026`. Mid-sentence names of RAs/coauthors adjacent to a year are indistinguishable from citations by syntax alone. Irreducible without the surname allowlist or the date guard (full dates are already safe). Document as known residue; the escape hatch is the designed answer.

---

## 2. Worse than false positives: stem-corruption bugs (spurious blocks on LEGITIMATE citations)

These produce a *wrong stem* for a real citation, so the hook demands a notes file that can never exist — blocking correct writing even when the notes are present under the right name:

| Input (probe) | Extracted stem | Problem |
|---|---|---|
| `Following Chetty's (2014) estimates` | `chetty's_2014` | Possessive `'s` swallowed into the stem; `chetty_2014.md` no longer matches the startswith check → spurious block despite notes existing |
| `O’Brien (2020)` (curly apostrophe U+2019) | `brien_2020` | Curly apostrophe not in the ASCII char class; match aborts mid-name → **wrong author** |
| `Goldsmith–Pinkham (2020)` (en-dash U+2013) | `pinkham_2020` | En-dash ≠ hyphen; lead surname dropped → **wrong author** |
| `O'Brien (2020)` (ASCII) | `o'brien_2020` | Stem contains `'`; PDF lookup tokenizes filenames on non-alphanumerics so `o'brien` can never equal a token → PDF check unfixably fails |

## 3. False negative (enforcement gap)

`We adopt Smith et al.'s (2020) design.` extracts **nothing** — the possessive after `et al.` breaks the year-separator match. A load-bearing framing claim escapes the hook entirely.

---

## 4. Ranked improvement roadmap

**P1 — structural, fixes real-citation corruption and the dominant FP class:**

- **(a) Typographic normalization in `_ascii_fold`:** map curly quotes `’ ‘` → `'`, en/em-dash `– —` → `-` (when between letters, or globally — the date guard already keys on both dash forms so keep its char class in sync), NBSP → space. Fixes the wrong-author bugs in §2 rows 2–3.
- **(b) Possessive handling:** strip trailing `'s` from captured name tokens; allow optional `['’]s` after `et al.` in the regex. Fixes §2 row 1 and the §3 false negative together.
- **(c) Markdown-aware sentence boundaries:** extend `SENTENCE_BOUNDARY` so a match preceded by line start (single `\n`), a table-cell separator (`|`), a bullet (`-`/`*`/`1.`), or a heading marker (`#`) counts as sentence-start (i.e., requires the allowlist). Kills §1a wholesale. Tradeoff: a real citation opening a bullet line needs the allowlist or mid-line placement — same tradeoff sentence-start already makes, and prose citations are overwhelmingly mid-sentence.

**P2 — cheap filter tightening:**

- **(d) All-caps threshold 3 → 2** (`FY`, `AI`, `US` without pronoun luck).
- **(e) Blocklist nouns:** software/tools (`stata`, `matlab`, `python`, `qualtrics`, `prolific`, `overleaf`, `github`, `dropbox`, `beamer`, `latex`, `excel`), document-lifecycle nouns (§1d list), institution/program/legislation nouns (§1c list). Respect the collision exclusions (`grant`, `law`, `bill`, `nielsen`).

**P3 — new mechanisms:**

- **(a) Org skip-list state file** (`.claude/state/primary_source_orgs.txt`): mixed-case corporate/data authors to skip (Gallup, Pew, Brookings, Nielsen-as-company). Mirrors the surname allowlist mechanics; per-project because one project's company is another's cited author.
- **(b) Apostrophe stem normalization:** drop `'` when building stems (`obrien_2020`) and try both variants in notes/PDF lookup — completes §2 row 4.
- **(c) False-positive telemetry:** when the PreToolUse hook blocks, append `(stem, matched text, file)` to `.claude/state/primary-source-blocks.jsonl`. Turns "monitor for residual false positives" (TODO) from anecdote into data; future blocklist passes get grounded in real frequencies.

**Explicitly rejected options:**

- *Skip markdown tables wholesale* — ADRs legitimately cite papers inside tables; the boundary treatment in P1-c is strictly gentler.
- *Require a populated allowlist* — breaks day-one usability for fresh forks; the template's empty-allowlist default is a deliberate design choice.

---

## 5. Verification notes

All §1–§3 rows reproduced against the live lib on 2026-07-01 (post-`a4084f1`, suite at 116 checks). True-positive sanity held throughout: `Chetty (2014)` and `Roth and List (2022)` extract correctly in the same probe run. Any implementation of §4 must add a regression test per confirmed row and re-run the end-to-end PreToolUse check.
