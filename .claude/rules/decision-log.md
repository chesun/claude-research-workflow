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

## File format

- Filename: `NNNN_short-slug.md`, zero-padded to four digits. Number is permanent and never reused.
- Template, sections, and full rules live in `decisions/README.md`.
- Title ≤ 80 chars. One decision per file.

## Required fields

Every ADR must have:

- **Date** (YYYY-MM-DD).
- **Status:** `Decided`, `Proposed`, or `Superseded by #NNNN`.
- **Data quality:** `Full context` or `Reconstructed — partial context`.
- **Sources** pointing to the analysis doc or session log that holds the reasoning (section or line range), plus relevant git commit hashes.

Recommended (add when unambiguous):

- **Scope:** one tag identifying which component the decision serves. Suggested categories for behavioral projects: `Research framing`, `IC foundation`, `Behavioral theory`, `Experimental design`, `Methodology`. For applied-micro projects: `Research framing`, `Identification`, `Data`, `Specification`, `Inference`. A decision should belong to one component. If two components are entangled, write two ADRs.

Missing any of the required fields = not a valid ADR.

## Supersession rule

When a decision changes:

1. Write a new ADR with the current date and Status `Decided` (or `Proposed`). Include a `Supersedes: #NNNN` line in its header.
2. Edit the old ADR's Status line from `Decided` → `Superseded by #NNNN`. This is the only edit ever allowed on a Decided entry.
3. Update the `decisions/README.md` index.
4. Leave the old ADR's body intact. The history stays.

## Reference by number

In session logs, analysis docs, commit messages, and other ADRs, cite decisions as `ADR-0008` (or whatever the number is). Numbers are durable across file renames.

## Relationship to other records

- **Session logs** (`quality_reports/session_logs/`) — chronological narrative of what happened in a working session. Records the *process* leading to a decision and any incremental reasoning. When a decision lands, write both a session log entry *and* the ADR; cross-link them.
- **Analysis docs** (e.g., `quality_reports/*_analysis.md`) — deep reasoning, alternatives considered, evidence. Stay as-is; ADRs point at them.
- **TODO.md Done section** — tracks completed tasks, not decisions. A completed task may or may not correspond to an ADR. Keep both (see `todo-tracking.md`).
- **Research journal** (`quality_reports/research_journal.md`) — append-only agent output log. Separate concern; do not move ADR entries there.

## Pending decisions

Decisions that need to happen but haven't yet are listed under **Pending decisions** in `decisions/README.md`. They get an ADR file only once resolved, not before.

## Enforcement

- Every substantive decision mentioned in a session log's "Design Decisions" or equivalent table should have a corresponding ADR (new or updated). If no ADR exists for it, write one.
- Before presenting a plan or starting implementation, check the ADR log for relevant prior decisions. Cite them by number in the plan.
- When reviewing a PR that introduces a design or specification change, require a new or superseding ADR.

## Interaction with primary-source-first

ADRs frequently cite external papers. The primary-source-first hook enforces on `decisions/*.md` — every citation in an ADR must be backed by a reading-notes file in `master_supporting_docs/literature/reading_notes/`. See `.claude/rules/primary-source-first.md`.
