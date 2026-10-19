# Decision Log (ADR)

**Location:** `decisions/` at project root
**Template and index:** `decisions/README.md`
**Purpose:** Single source of truth for *what* was decided and *when*. Analysis docs hold the reasoning; the ADR log holds the record.

The log is append-only. Each ADR is a short, dated, immutable file. When a decision changes, write a new ADR that supersedes the old one — never edit a Decided entry.

## When to write an ADR

Write one when any of the following gets committed:

- A research framing or hypothesis choice is locked.
- A design parameter is committed (arm structure, instrument format, sample size, burden budget — for experiments; specification choice, sample restriction, identification assumption — for applied micro).
- A methodological choice is made (accuracy metric, ε tolerance, MPL format, instruction style — for experiments; instrument, clustering level, estimator — for applied micro).
- A scope decision excludes a candidate (e.g., "no preference-for-control arm"; "restrict to 2018–2022 cohorts").

Do **not** write an ADR for literature reading, reading-note additions, code/repo logistics, or tentative thoughts that have not been committed to. Draft those in a session log or analysis doc; promote to an ADR once settled.

## Format, fields and supersession

One decision per file, `NNNN_short-slug.md`. Required fields: **Date**, **Status**, **Data quality** and **Sources**; missing any of them = not a valid ADR. When a decision changes, write a new ADR with a `Supersedes: #NNNN` line and edit the old ADR's Status line to `Superseded by #NNNN`, the only edit ever allowed on a Decided entry; leave its body intact. Cite decisions by number (`ADR-0008`). When a decision lands, write both a session log entry *and* the ADR; cross-link them.

**Read** `.claude/references/decision-log-detail.md` for the filename and title rules, the field values and scope tag, the supersession steps, how ADRs relate to session logs, analysis docs and `TODO.md`, and pending decisions (open it when writing or superseding an ADR); `decisions/README.md` holds the entry template and the index.

## Enforcement

- Every substantive decision mentioned in a session log's "Design Decisions" or equivalent table should have a corresponding ADR (new or updated). If no ADR exists for it, write one.
- Before presenting a plan or starting implementation, check the ADR log for relevant prior decisions. Cite them by number in the plan.
- When reviewing a PR that introduces a design or specification change, require a new or superseding ADR.

## Interaction with primary-source-first

ADRs frequently cite external papers. The primary-source-first hook enforces on `decisions/*.md` — every citation in an ADR must be backed by a reading-notes file in `master_supporting_docs/literature/reading_notes/`. See `.claude/rules/primary-source-first.md`.
