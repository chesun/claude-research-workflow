# Primary-Source-First

**Scope (file-level):** `decisions/**/*.md`, `experiments/designs/**/*.md`, `theory/**/*.{tex,md}`, `quality_reports/advisor_meeting_*/**`, `quality_reports/session_logs/**`, `quality_reports/plans/**`, `quality_reports/reviews/**`, `quality_reports/*_analysis.md`

**Scope (prose):** all assistant conversation text in the session

**Enforcement:**

- `.claude/hooks/primary-source-check.py` (PreToolUse, `Edit|Write`) — blocks edits to scoped files.
- `.claude/hooks/primary-source-audit.py` (Stop) — blocks turn-end when session prose contains un-grounded citations.

Before making a framing claim about an external paper — in a file edit OR in conversation text — consult the primary source. Derivative docs and paraphrases lose precision; downstream claims propagate the error silently.

## Three enforced failure modes

1. **Notes don't exist AND the PDF is in the repo.** Blocks with "read the PDF, write notes." The remediation is to use the `pdf-learnings` skill on long papers or the `Read` tool with `pages=` on short ones, then produce a notes file per `master_supporting_docs/literature/reading_notes/README.md`.

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

## Project-specific surname allowlist (optional)

The hook extracts citations via an Author-Year regex. Without filtering, this matches false positives like "Table 2 (2024)" or other coincidental capitalized-word-plus-year patterns.

An optional allowlist at `.claude/state/primary_source_surnames.txt` (one lowercase surname per line) reduces false positives. **When the file is empty or missing, every Author-Year match is accepted** — the hook errs toward noise rather than silently skipping unfamiliar citations.

Populate the allowlist as you accumulate cited authors for this project. Applied-micro and behavioral projects will have different allowlists.

## Escape hatch

If you need to cite a paper *without* making a new framing claim (e.g., fixing a typo in an existing sentence that happens to cite the paper; referring to a paper as a test case or example without claiming anything about its content), include an override comment:

```
<!-- primary-source-ok: smith_jones_2024, angrist_pischke_2009 -->
```

- For PreToolUse (file edits): include the comment in the delta.
- For the Stop audit (conversation prose): include the comment in the same assistant message as the citation.

The comment only applies to the scope where it appears — it is not session-wide. Abuse is auditable: `grep -R "primary-source-ok" master_supporting_docs/ quality_reports/ experiments/ theory/` surfaces every use.

## Why this exists

Claude has, in prior projects, propagated an incorrect framing claim about a paper through multiple load-bearing documents — a decision log, an identification analysis, a session log, and a slide review — without ever opening the PDF despite it being in the repo the whole time. The error originates in a paraphrase, gets amplified across derivative docs, and each downstream claim inherits and amplifies the distortion.

The rule exists to make this failure mode deterministically catchable rather than relying on the model to remember to open the primary source. Three failure modes — missing notes with PDF present, missing notes with no PDF, existing notes not consulted in-session — are each paths the failure could have been caught; the hooks make all three deterministically blocking.

## Intended behavior

When content cites a paper — whether in a file edit or in conversation prose — the hooks either:

- Allow (notes exist AND were consulted this session), or
- Block with a clear remediation path: read the PDF (or add it first if missing), produce notes, touch the notes file in this session, re-run.

The rule is not a suggestion. It fires deterministically. The only way through without notes is the escape hatch, which is auditable.
