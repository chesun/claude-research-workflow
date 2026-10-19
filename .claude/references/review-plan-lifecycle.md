# Review and plan lifecycle

**Class:** A (universal). Pointer-loaded detail for `.claude/rules/agents.md` § 2a Review and Plan Lifecycle (moved from the rule on 2026-10-19); there is no auto-load.

The rule keeps the blueprint-evidence exception (repeated below). The folder READMEs (`quality_reports/reviews/README.md`, `quality_reports/plans/README.md`) carry the naming and header conventions.

**The reviews/ and plans/ folders are append-mostly, but lifecycle-managed to prevent navigational bloat.**

### Status field

Every review and plan declares a status in its header:

- `Active` — current, load-bearing
- `Completed` — work is shipped or superseded by ADR; kept for history but not actively cited
- `Superseded by <path>` — explicit pointer to the newer review/plan that replaces this one
- `Archived` — moved to `archive/` subdir, kept for git history; not expected to be read

### Supersession protocol

**Exception: blueprint evidence is never moved.** `proof-verifier` reports, and any other file named as a locator in a `theory/blueprint/` evidence log, are evidence. They are never superseded, archived, renamed or swept by the time-based archive below. The two runs of one verification (`-a`, `-b`) and a later re-verification of the same node are separate records, not supersessions. A moved file breaks the evidence chain and makes the blueprint validator FAIL (ADR-0004).

When a critic writes a new review for a target that already has an `Active` review:

1. Read the existing review (find via `ls quality_reports/reviews/*<target>*_<critic>_review.md`).
2. Edit its header: `Status: Superseded by <new-path>`.
3. Move it: `git mv <old> quality_reports/reviews/archive/`.
4. Write the new review with `Supersedes: <archive/old-path>` in its header.

Same protocol for plans (`quality_reports/plans/`).

### Time-based archive

A review or plan in `Status: Completed` with no edits for 90+ days moves to `archive/`. The orchestrator's pre-dispatch step (or a manual `/tools archive-stale` invocation) sweeps these on a slow cadence.

### Index files

Each lifecycle-managed folder maintains an `INDEX.md` listing active items:

```markdown
# Active reviews

- [2026-04-28_main_writer_review.md](2026-04-28_main_writer_review.md) — paper/main.tex, score 92, Active
- [2026-04-25_01-clean_coder_review.md](2026-04-25_01-clean_coder_review.md) — scripts/01_clean.do, score 88, Active
```

Critics consult `INDEX.md` before writing a new review — if an `Active` review for the same target exists, follow the supersession protocol.

### What lives where

- `quality_reports/reviews/` — top-level: `Active` and recently `Completed` reviews
- `quality_reports/reviews/archive/` — `Superseded` and `Archived` reviews; rarely opened
- `quality_reports/plans/` — top-level: `Active`/recent plans
- `quality_reports/plans/archive/` — completed/superseded plans

The convention prevents indefinite top-level growth without losing history. Archive contents are still git-tracked and grep-able.
