# Decision log — format, fields and supersession

**Class:** A (universal). Pointer-loaded detail for `.claude/rules/decision-log.md` § Format, fields and supersession (the file format, required fields, supersession, citation, relationship and pending-decision detail moved from the rule on 2026-10-19); there is no auto-load.

The rule keeps when to write an ADR, the append-only principle, a summary of the fields and supersession, and the enforcement. `decisions/README.md` holds the entry template, the scope categories, the index and the pending-decisions list.

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

## Pending decisions

Decisions that need to happen but haven't yet are listed under **Pending decisions** in `decisions/README.md`. They get an ADR file only once resolved, not before.
