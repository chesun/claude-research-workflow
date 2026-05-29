# Session Log: 2026-05-28 — Context-tightening: Lever-1 verification + low-risk subset review

**Status:** IN PROGRESS

## Goal

On branch `audit/workflow-context-tightening`: (1) finish verifying Lever 1 (the `paths:` frontmatter lazy-load of convention rules), then (2) evaluate whether to execute any of Levers 2/3.

## Key Context

- Lever 1 already executed earlier (commits `27d03a7`, `f48d554`): 8 convention rules path-scoped, always-on rules 165,455 → 119,914 B (−27%). Plan: `quality_reports/plans/2026-05-28_context-tightening-plan.md`.
- User opened the session having confirmed anti-ai-prose was absent from context at startup ("on purpose") — the first (absent) half of the Lever-1 smoke check.

## Work This Session

1. **Lever-1 smoke check — second (load) direction VERIFIED.** `Read README.md` (matches anti-ai-prose's `paths:` glob) → harness injected the full rule into context via system-reminder. Both directions now confirmed; lazy-load works, no requirement lost. Recorded in the plan status line, TODO, and the prior session log's addendum. No revert needed.

2. **Low-risk subset review of Levers 2/3.** User bounded scope: exclude DVC/data-version-control entirely (not used in any live repo → can't field-test relocation) and exclude hook-rule prose trims (#13–16). Reviewed the remaining non-hook dedup/dead-rule items. Report: `quality_reports/reviews/2026-05-28_context-tightening-lowrisk-subset-review.md`.

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Don't touch data-version-control (Lever 2) | DVC unused in live repos; relocating un-field-tested procedure is flying blind |
| Recommend dropping `logging.md` §2 (SESSION_REPORT.md) | `find` confirms `SESSION_REPORT.md` never instantiated across many sessions; rule contradicts actual practice (per-session logs + TODO.md). Correctness win, not just bytes |
| Keep `logging.md` §3 (research_journal.md) despite also never existing | Load-bearing in orchestrated agent pipeline; a fork running `/new-project` generates it. Meta-governance: forker benefits |
| Low-risk subset is small (~1% always-on) | Honest finding: the big wins (DVC, hook trims) are the ones being correctly skipped; only item A pays for its churn on correctness grounds |

3. **Executed: dropped both dead logging requirements (items A + B).** User decided to drop `research_journal.md` too, on the grounds that the full orchestrated pipeline (which the journal served) isn't run in practice either — same dead-requirement logic as `SESSION_REPORT.md`. Removed `logging.md` §2 + §3, renumbered §4→§2, retitled. Cleaned 5 incidental pointers (file-classes.toml, quality.md, decision-log.md, agents.md, tools/SKILL.md `/tools journal`). logging.md 5,445 → 1,972 B. Verified 0 dangling refs; no hook rules touched; `log-reminder.py` reference intact.

## Design Decisions (cont'd)

| Decision | Rationale |
|----------|-----------|
| Drop `research_journal.md` after all (reversed the earlier "keep") | User: the orchestrated agent pipeline that the journal serves isn't actually run, so it's dead for the same reason SESSION_REPORT is. Retargeted the 2 live "logged in research journal" instructions (quality.md override, agents.md escalation) to the session log — the real artifact |

## Open Questions / Next Steps

- Optional C/D/E tidy-ups (epistemic-table dedup, crosswalk dedup, misc) NOT done — await user go-ahead; modest payoff.
- Commit the logging-cleanup + verification record on branch `audit/workflow-context-tightening`, then merge to main when context-tightening decisions settle.
