# Primary-Source-First

**Scope (file-level):** `decisions/**/*.md`, `experiments/designs/**/*.md`, `theory/**/*.{tex,md}`, `quality_reports/advisor_meeting_*/**`, `quality_reports/session_logs/**`, `quality_reports/plans/**`, `quality_reports/reviews/**`, `quality_reports/*_analysis.md`

**Scope (prose):** all assistant conversation text in the session

**Enforcement:**

- `.claude/hooks/primary-source-check.py` (PreToolUse, `Edit|Write`) — blocks edits to scoped files.
- `.claude/hooks/primary-source-audit.py` (Stop) — blocks turn-end when session prose contains un-grounded citations.

Before making a framing claim about an external paper — in a file edit OR in conversation text — consult the primary source. Derivative docs and paraphrases lose precision; downstream claims propagate the error silently.

## Three enforced failure modes

1. **Notes don't exist AND the PDF is in the repo.** Blocks with "read the PDF, write notes." The remediation is to use the `pdf-learnings` skill on long papers or the `Read` tool with `pages=` on short ones, then produce a notes file per `master_supporting_docs/literature/reading_notes/README.md`. If `pdf-learnings` fails on an unusually long or problematic file, see `.claude/references/pdf-chunking.md` for a Ghostscript-based fallback recipe.

2. **Notes don't exist AND the PDF is NOT in the repo.** Blocks with "add the PDF first." A citation you cannot ground in a primary source does not belong in a load-bearing artifact. The remediation is to add the PDF to `master_supporting_docs/literature/papers/` (naming it with the surname-year convention so the hook can find it), then produce notes.

3. **Notes exist but were not touched in this session.** Blocks with "Read the notes file before citing." This is the guard against working from cached context. Touching (Read / Write / Edit) a notes file in the current session is the evidence; a prior session's Read does not persist — sessions are fresh contexts.

## Where the two hooks apply

- **PreToolUse hook** — scans the *delta* (new_string for Edit, content for Write) of every Edit/Write to a scoped file path. Fires on each tool call; blocks the call.
- **Stop hook** — scans *all assistant prose* in the session transcript at turn-end. Fires on Stop; blocks the turn-end. Catches claims made in conversation that never went to a tool call. Respects `stop_hook_active` to avoid loops (blocks at most once per turn).

Both hooks share citation-detection and notes-verification logic in `.claude/hooks/primary_source_lib.py`.

## What counts as a reading-notes file

Either form is accepted by the hook:

1. A **per-paper file** named with the citation stem: `smith_jones_2024.md`, `angrist_pischke_2009.md`, etc.
2. A **section inside a compiled reading-notes file** that includes a `**Citation:** ...` metadata line naming the paper's authors and year. The hook matches on the citation line specifically, so compiled files must use this format for the hook to recognize them.

Per-paper files are preferred for load-bearing references. Compiled files are acceptable for batch reading sprints.

**Why citation-line-only (not section-header) matching:** documents like the reading-notes README or conceptual memos may mention a paper in a header without being notes about it. The `**Citation:** Author (Year)...` line is the reliable signal that "this section is reading notes for this paper."

## Required sections in a reading-notes file

The `README.md` in `master_supporting_docs/literature/reading_notes/` specifies the canonical structure. The load-bearing section for preventing derivative-doc drift is:

> **What this paper is NOT claiming (common misreadings)**

Use this section to head off future conflation errors. When downstream docs (ADRs, analysis memos, hypotheses, session logs) have previously misframed the paper, record the misreading and the corrected reading side-by-side.

## Citation extraction

The hooks extract Author-Year citations with a regex and then drop false positives through a filter stack: a built-in never-a-surname blocklist, an optional org skip-list (`.claude/state/primary_source_orgs.txt`), cue-word and abstract-noun guards, all-caps and sentence-start filters, and an optional surname allowlist (`.claude/state/primary_source_surnames.txt`). Each block is logged to `.claude/state/primary-source-blocks.jsonl` (fail-open: a logging failure never stops the block).

**Read** `.claude/references/primary-source-filter-stack.md` when tuning a false positive or naming a notes file for an unusual surname (accents, particles, hyphens). It holds the full stack, the Unicode handling, the known residue and the telemetry query.

## Escape hatch

If you need to cite a paper *without* making a new framing claim (e.g., fixing a typo in an existing sentence that happens to cite the paper; referring to a paper as a test case or example without claiming anything about its content), include an override comment:

```
<!-- primary-source-ok: smith_jones_2024, angrist_pischke_2009 -->
```

Hyphenated stems (e.g., `chetty-friedman-rockoff_2014`) are supported — the parser uses a non-greedy match terminated by `-->` so hyphens inside stems don't truncate the list. Comments may also span multiple lines:

```
<!-- primary-source-ok:
  smith_jones_2024,
  chetty-friedman-rockoff_2014,
  goldsmith-pinkham_2020
-->
```

- For PreToolUse (file edits): include the comment in the delta.
- For the Stop audit (conversation prose): include the comment in the same assistant message as the citation.

The comment only applies to the scope where it appears — it is not session-wide. Abuse is auditable: `grep -R "primary-source-ok" master_supporting_docs/ quality_reports/ experiments/ theory/` surfaces every use.

## Citation-style convention (AEA / Chicago author-date)

The project uses the AEA reference style (Chicago author-date). This applies to all in-text citations in load-bearing artifacts: paper, talks, ADRs, plans, reviews, session logs, response letters, and any external-facing prose. In-text form:

| Authors | Form | Examples |
|---|---|---|
| 1 | `Author (year)` or `(Author year)` | `Smith (2020)`; `(Smith 2020)` |
| 2 | `Author and Author (year)` — never `&`, never comma-separated | `Roth and List (2022)`; `Healy and Leo (2024)`; `(Romer and Romer 2010)` |
| 3 | `Author, Author, and Author (year)` — Oxford comma required | `Gaduh, Hanna, and Olken (2021)`; `Smith, Jones, and Brown (2020)` |
| 4 | `Author, Author, Author, and Author (year)` — all four listed, Oxford comma | `Smith, Jones, Brown, and Lee (2024)` |
| 5+ | `First-author et al. (year)` from first cite onward; reference list shows more (see the reference) | `Smith et al. (2024)` |
| Same author, same year | suffix-disambiguate with lowercase letter | `Smith (2020a)`, `Smith (2020b)` — order matches the reference list |

No comma between author and year in the parenthetical form; semicolons between works in one parenthetical; always `et al.` with the period.

**Read** `.claude/references/aea-citation-style.md` for the multiple-works, punctuation, reference-list and corporate-author forms and the AER sources (open it when writing or reviewing citations in prose or a reference list).

## Why this exists

Claude has, in prior projects, propagated an incorrect framing claim about a paper through several load-bearing documents without ever opening the PDF that was in the repo. The hooks make each of the three failure modes above deterministically blocking rather than relying on the model to remember to open the primary source.

**Read** `.claude/references/primary-source-filter-stack.md` § Why this exists for the full narrative (open it when explaining or revising the rule).

## Intended behavior

When content cites a paper — whether in a file edit or in conversation prose — the hooks either:

- Allow (notes exist AND were consulted this session), or
- Block with a clear remediation path: read the PDF (or add it first if missing), produce notes, touch the notes file in this session, re-run.

The rule is not a suggestion. It fires deterministically. The only way through without notes is the escape hatch, which is auditable.
