# ADR-0002 — Independent adversarial review required before committing load-bearing code

**Date:** 2026-09-21
**Status:** Decided
**Data quality:** Full context
**Scope:** Methodology / enforcement
**Sources:** `quality_reports/plans/2026-09-21_port-mandatory-review.md` (v2); `quality_reports/reviews/2026-09-21_port-mandatory-review-plan_review.md`; the modernize-effort reviews (`quality_reports/reviews/2026-09-14_*`, `2026-09-15_*`, `2026-09-16_*`); ported from a sibling work repository's ADR-0016.

## Context

Every independent review run during this repo's Claude-5 modernize effort found at least one High finding on a build the author considered finished: the confidentiality guards, the modernize plan (twice), and the guard rewrites. A single author cannot review their own work adversarially, and a prose rule without a trigger does not bind. The manual habit of dispatching a fresh reviewer worked but was invoked by hand.

## Decision

- **Mandate.** Where `git config review.required` is `true`, no staged **code** artefact is committed until an independent review has run against that version and every finding is fixed or accepted with a recorded reason.
- **Gated set — code blocks, docs advise.** Blocking: `.claude/hooks/**`, `bin/**` scripts, `.githooks/**`, on every change including deletion. Advisory (named, never blocked): `.claude/rules`, `.claude/agents`, `.claude/skills`, `.claude/references`, `decisions/NNNN`, `quality_reports/plans` (not INDEX), `templates`. The asymmetry keeps the expensive review on costly, self-missed enforcement-code defects and off routine doc editing — the repo's main activity — so the gate does not re-grow the process-nag scaffolding the modernize effort pruned.
- **Mechanism — a `PreToolUse` Bash hook,** not a git `commit-msg` hook. It is wired in `settings.json` like every other gate here, needs no `core.hooksPath` override or shims, and travels with the repo. It fires only for commits made through Claude Code (accepted for a strictly-personal repo), and it **fails open** on internal error to avoid a session-wide commit lockout (a PreToolUse hook has no `--no-verify` escape).
- **Lenses.** Code → red team + correctness. Plans/ADRs → fit-for-purpose + efficiency. Rules → consistency + bloat. Agents, templates, references, skills → correctness. Fresh general-purpose agents, never forks, blind to each other, read-only except their report, evidence per finding, synthetic sentinels, standard header. Reports are staged so the receipt check sees them.
- **Receipt.** A staged review whose `**Target:**` names the path (exact path, unique basename, or `ADR-NNNN`), with `**Score:** NN/100` and `**Status:** Active|Completed`, dated no earlier than the path's last commit and not in the future. Existence and freshness only; quality is carried by the evidence standard.
- **Waiver.** `REVIEW_WAIVE=1 git commit …` (visible, auditable via `git log`/shell history) skips the code block for one commit. Habitual waiving means the gated set is wrong; narrow it.

## Consequences

- Cost per two-lens cycle, from the recorded modernize cycles: roughly 300k–600k agent tokens and 10–20 minutes in parallel, plus the fix round. Gating code only keeps this off the frequent doc edits.
- The receipt checks existence and freshness, not quality; quality is carried by the evidence standard and the lenses.
- Known limits: fires only inside Claude Code; `--no-verify` does not bypass it; `git commit` detection is heuristic; fail-open means a guard bug silently disables the gate until noticed.

## Alternatives rejected

- **git `commit-msg` hook** (the sibling's mechanism): universal trigger and clean waiver, but forces a local `core.hooksPath` override plus delegating shims, is not committed so must be re-wired per machine, and its setup can trip the machine AI-gate. Rejected for a personal repo committed through Claude Code.
- **Gate documents too (blocking):** would tax the repo's main activity (editing rules/agents/plans) with a full review cycle per commit — the friction the modernize effort removed.
- **Advisory only:** does not bind; the effort's own history shows a prose rule without a trigger is ignored.

## Amendment (2026-09-22) — fail mode reversed to fail-closed

The original decision above specified the hook **fails open** on internal error. The owner reversed this: silent fail-open requires human vigilance to notice a disabled gate, which defeats the point. The hook now **fails closed, escapably** — a git error or bug while evaluating a *confirmed gated, opt-in, non-waived* commit blocks it (exit 2, loud banner, `.claude/state/review-gate-failures.log`), while `REVIEW_WAIVE=1` (parsed before any git call) remains the escape and errors before the commit is confirmed gated still allow (the hook runs on every Bash call, so it must not brick ordinary shell use). The rest of this ADR stands. Source: `quality_reports/session_logs/2026-09-21_port-mandatory-review.md` (2026-09-22 entry) and the fail-closed reviews `quality_reports/reviews/2026-09-22_review-receipt-check-failclosed_*_review.md`.
