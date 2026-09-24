# ADR-0003 — Model routing: reviewers and critics on `fable`, workers on `opus`

**Date:** 2026-09-24
**Status:** Decided
**Data quality:** Full context
**Scope:** Methodology / enforcement
**Sources:** this session's discussion (2026-09-24 session log `quality_reports/session_logs/2026-09-24_model-routing.md`); `quality_reports/reviews/2026-09-22_infra-survey_synthesis.md` (SKIP row: per-agent model-version pins are brittle); ADR-0002 (mandatory independent review); `.claude/rules/agents.md` § 1 (worker-critic pairs).

## Context

The harness now offers two frontier tiers: `fable` (the most capable generally available model) and `opus` (fast, strong, and the model behind fast mode). Until now every agent in `.claude/agents/` carried `model: inherit`, so a session ran everything on whichever model the main conversation used. Token cost is not a constraint for the owner; speed and review quality are.

Two facts shape the choice. First, the repo's architecture already separates authors from reviewers: every worker has a paired critic (`agents.md` § 1), and ADR-0002 makes an independent review mandatory before load-bearing code is committed. Second, execution here is not mechanical. Recent builds caught real defects only during the executor's own verification (a settings-file edit that silently no-op'd, an unimported name in a hook, a false positive in a destructive-action guard). So the executor's model can only stop being load-bearing for correctness if the review gate is mandatory and runs on the stronger model.

## Decision

- **Main session** (thinking, planning, dispatch) runs on `fable`, set through `/model`.
- **Reviewers and critics** run on `fable`: every `*-critic` agent, `domain-referee`, `methods-referee`, `editor`, `verifier`, `tikz-reviewer`, and every independent reviewer dispatched by `/review-build`. The reviewer is never on a weaker model than the author.
- **Workers** run on `opus`: `coder`, `data-engineer`, `explorer`, `librarian`, `storyteller`.
- **Exception — `writer` stays on `fable`.** Prose fidelity is judgment-heavy and voice preservation is the next committed build; the exception is one frontmatter line and is revisited after that build.
- **`orchestrator` keeps `model: inherit`.** It dispatches; the per-agent settings above govern what it dispatches to.
- **Aliases, never dated model IDs.** `fable` and `opus` track the current release. Dated pins are the brittleness the 2026-09-22 survey skipped.
- **Independence framing.** Author and reviewer on different models is a second axis of independence on top of the fresh-context requirement (never a fork). It is a hypothesis, not an established fact.

## Consequences

- Sixteen of the seventeen agent files change one line each (`orchestrator` is unchanged); `/review-build` and `independent-review.md` name the review model. No hook or gate changes.
- The split is only safe while ADR-0002 holds. If the review gate is waived habitually, the executor's model becomes load-bearing again.
- **Experiment, kept honest.** For the next few builds the session log records, per review, findings by severity and the number of fix rounds. The sample will be small; the read-out is a judgment, not a statistic. Revisit after the voice-preservation build.
- **Availability is per account.** Whether both aliases resolve depends on the account a session runs under; verify on any new machine or account before relying on the split.
- **Portability to the sibling consulting workflow.** The same mapping applies to its analyst/checker pairing and to its own independent-review dispatch. That repo decides for itself (its ADR-0001 is copy-and-adapt); nothing here depends on it.

## Not decided

- Whether `sonnet` or `haiku` has a place for cheap mechanical steps (compile checks, greps). Not needed while cost is not a constraint.
- Whether the reviewer/author model split measurably raises review yield. That is what the experiment is for.
