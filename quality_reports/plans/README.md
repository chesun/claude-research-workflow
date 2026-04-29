# Plans

Plan-mode artifacts saved to disk so they survive context compression. Append-mostly, lifecycle-managed.

---

## File naming

```
quality_reports/plans/YYYY-MM-DD_<short-description>.md
```

- `YYYY-MM-DD` — date the plan was approved.
- `<short-description>` — 2–6 hyphen-separated words describing the change. Reuse stems for revisions of the same plan (`-v2`, `-v3`).

Examples:

- `2026-04-28_adversarial-default-rule-proposal.md`
- `2026-03-18_workflow-adaptation-plan-v2.md`

---

## Required header

Every plan must start with:

```markdown
# <Plan Title>
**Date:** YYYY-MM-DD
**Status:** Active
**Supersedes:** <prior plan path, if applicable>

## Goal
## Approach
## Files to modify
## Verification steps
## Open questions
```

`Status` values:

- `Active` — currently being executed or referenced
- `Approved` — approved by user but not yet started
- `Completed` — work shipped; plan is history
- `Superseded by <path>` — replaced by a newer plan
- `Archived` — moved to `archive/` subdir

---

## Lifecycle

### When work ships

After the plan's work is complete:

1. Edit header: `Status: Completed`.
2. Optionally append a `## Outcome` section noting commits, ADRs, or follow-ups.
3. Update `INDEX.md`.

### Supersession

When a new plan replaces an existing `Active` plan for the same scope:

1. Mark old plan: `Status: Superseded by quality_reports/plans/archive/<old-name>.md`.
2. `git mv <old> quality_reports/plans/archive/`.
3. New plan's header: `Supersedes: quality_reports/plans/archive/<old-name>.md`.
4. Update `INDEX.md`.

### Time-based archive

`Status: Completed` plan with no edits for 90+ days moves to `archive/`. Update header to `Status: Archived`. Update `INDEX.md`.

---

## Where things live

- **Top level** (`quality_reports/plans/`) — `Active`, `Approved`, recently `Completed` plans.
- **`archive/`** — `Superseded` and `Archived` plans.

---

## INDEX.md

Lists `Active` and `Approved` plans:

```markdown
- [2026-04-28_critic-write-architecture.md](2026-04-28_critic-write-architecture.md) — critic-write + lifecycle, Active
```

Maintained by the agent that creates or completes a plan, in the same commit.

---

## Cross-references

- `.claude/rules/workflow.md` § 1 — Plan-First Protocol
- `.claude/rules/agents.md` § 2a — Review and Plan Lifecycle
