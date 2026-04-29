# Reviews

Critic-produced review reports. Append-mostly, lifecycle-managed to prevent navigational bloat.

---

## File naming

```
quality_reports/reviews/YYYY-MM-DD_<target>_<critic>_review.md
```

- `YYYY-MM-DD` — date of review.
- `<target>` — stable slug of what was reviewed (`main` for paper, `01-clean` for a script, `job-market` for a talk, `bibliography`, `strategy-memo`, etc.). Reuse the same slug when re-reviewing the same target so glob-matching finds priors.
- `<critic>` — agent name without the `-critic` suffix where natural: `coder`, `writer`, `storyteller`, `librarian`, `explorer`, `tikz`, `domain`, `methods`, `verifier`, `editor`, `strategist` (applied-micro overlay), `designer` / `theorist` (behavioral overlay).

Examples:

- `2026-04-28_main_writer_review.md`
- `2026-04-28_01-clean_coder_review.md`
- `2026-04-28_job-market_storyteller_review.md`

For one-off audits or memos that don't fit the worker-critic naming (e.g., `2026-04-24_primary-source-hook-fix-memo.md`), keep the date prefix but skip the `<critic>` suffix.

---

## Required header

Every review report must start with:

```markdown
# <Target> Review — <Critic>
**Date:** YYYY-MM-DD
**Reviewer:** <critic-agent-name>
**Target:** <path or slug>
**Score:** XX/100 (or PASS/FAIL or N/A)
**Status:** Active
**Supersedes:** <prior review path, if applicable>
```

`Status` values:

- `Active` — current, load-bearing review
- `Completed` — work is shipped or otherwise resolved; kept for history but no longer actively cited
- `Superseded by <path>` — explicit pointer to the newer review that replaces this one
- `Archived` — moved to `archive/` subdir; expected to be rarely opened

Default for a freshly written review is `Active`.

---

## Lifecycle

### Supersession (explicit, on new review of the same target)

When a critic writes a new review for a target that already has an `Active` review:

1. Find the prior review: `ls quality_reports/reviews/*<target>*_<critic>_review.md`.
2. Edit the prior review's header: `Status: Superseded by quality_reports/reviews/archive/<old-name>.md`.
3. Move it: `git mv <old> quality_reports/reviews/archive/`.
4. Write the new review with `Supersedes: quality_reports/reviews/archive/<old-name>.md` in its header.
5. Update `INDEX.md` (remove the superseded entry; add the new one).

### Time-based archive (slow cadence)

A review with `Status: Completed` and no edits for 90+ days moves to `archive/`:

```
git mv quality_reports/reviews/<old>.md quality_reports/reviews/archive/
```

Update its header to `Status: Archived`. Update `INDEX.md`.

This is a slow-cadence sweep — done manually or via a tooling skill — not on every commit.

### Manual archive

If a review is no longer relevant (e.g., the target was deleted, the question was resolved differently), move it to `archive/` with `Status: Archived` and a one-line note explaining why.

---

## Where things live

- **Top level** (`quality_reports/reviews/`) — `Active` and recently `Completed` reviews. Should stay scannable; if it grows past ~30 entries, sweep `Completed` items older than 90 days to `archive/`.
- **`archive/`** — `Superseded` and `Archived` reviews. Still git-tracked and grep-able; rarely opened directly. Browse via `ls archive/` or `grep`.

---

## INDEX.md

`INDEX.md` lists `Active` reviews with one-line summaries:

```markdown
- [2026-04-28_main_writer_review.md](2026-04-28_main_writer_review.md) — paper/main.tex, score 92, Active
```

Critics consult `INDEX.md` before writing a new review — if an `Active` entry for the same target exists, follow the supersession protocol above.

`INDEX.md` is maintained as part of writing a review — the critic adds the new entry and removes superseded ones in the same commit.

---

## Cross-references

- `.claude/rules/agents.md` § 2 — Separation of Powers (source vs report artifacts)
- `.claude/rules/agents.md` § 2a — Review and Plan Lifecycle
- `.claude/rules/logging.md` — research journal conventions
