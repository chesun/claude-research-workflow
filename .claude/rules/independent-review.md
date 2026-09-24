# Independent Review — required before committing load-bearing code

**Decision and rationale:** `decisions/0002_mandatory-independent-review.md`. **Enforcement:** `.claude/hooks/review-receipt-check.py` (PreToolUse Bash; blocks a `git commit` whose staged **code** lacks a review receipt, advises on docs). **Opt-in:** active only where `git config review.required` is `true`.

A single author cannot review their own work adversarially. Every independent review in this repo's modernize effort found a High on a build the author thought finished — the confidentiality guards, the plans, the guard rewrites. So load-bearing changes get a fresh adversarial pair of eyes before they land.

## What binds

1. **No staged code artefact is committed until an independent review has run against that version and every finding is fixed or accepted with a one-line reason in the session log.** Criticals additionally get a verify pass by a fresh agent or a named regression test.
2. **Gated (blocking): code** — `.claude/hooks/**`, `bin/**` scripts, `.githooks/**` — on every change, including deletion.
3. **Advised (non-blocking): docs** — `.claude/rules`, `.claude/agents`, `.claude/skills`, `.claude/references`, `decisions/NNNN_*`, `quality_reports/plans` (not INDEX), `templates`. The hook names unreviewed doc changes but never blocks; review them when the change is substantive, skip it for a Status line or a typo. This asymmetry is deliberate: a defect in enforcement code is costly and easy to self-miss; taxing every routine doc edit with a full review cycle would just re-grow the friction the workflow removed.
4. **Lenses:** code → red team + correctness; plans and ADRs → fit-for-purpose + efficiency; rules → consistency + bloat; agents, templates, references, skills → correctness. `/review-build <path>` dispatches them.
5. **A review is:** a fresh general-purpose agent (never a fork) dispatched on `fable` (ADR-0003), blind to the other lens, read-only except its report, evidence per finding (`file:line` or repro), synthetic sentinels, saved to `quality_reports/reviews/YYYY-MM-DD_<target>_<lens>_review.md` **and staged**, with header fields `**Date:**`, `**Reviewer:**`, `**Target:**` (every covered path, repo-relative), `**Score:** NN/100`, `**Status:** Active`.
6. **Receipt (what the hook reads):** a review in the git index whose `**Target:**` names the path (exact repo-relative path; unique basename; or `ADR-NNNN`), with `Score` and `Status` Active or Completed, dated no earlier than the path's last commit and not in the future. Existence and freshness only; quality is carried by item 5.
7. **Waiver:** prefix the commit with `REVIEW_WAIVE=1` (e.g. `REVIEW_WAIVE=1 git commit -m "…"`). It is visible in the command and auditable in shell history, and it skips the code block for that one commit. For record-only commits and edits a review would not change. Habitual waiving means the gated set is wrong — narrow it, don't keep waiving.

## Mechanism and its limits

The hook is `PreToolUse` (matcher `Bash`): it inspects the `git commit` command Claude Code is about to run and checks the staged index. Consequences to know:

- **Fires only for commits made through Claude Code.** A commit from an external terminal or IDE is not seen. Accepted for a strictly-personal repo committed through Claude Code.
- **`--no-verify` does NOT bypass it** (that flag skips git hooks, not PreToolUse hooks). The deliberate escape is the `REVIEW_WAIVE=1` prefix.
- **Fails closed, escapably.** Once the hook has confirmed a gated, opt-in, non-waived commit, a git error or bug while evaluating the receipt **blocks** the commit (exit 2, loud banner, appended to `.claude/state/review-gate-failures.log`) rather than silently allowing it. This is not a lockout: `REVIEW_WAIVE=1` is parsed before any git call, so a broken guard is always escapable. And errors *before* the commit is confirmed gated still allow the command — the hook runs on every Bash call, so it must never brick ordinary shell use. So the only silent-allow paths are genuinely non-gated ones; a confirmed gated commit is never let through un-evaluated.
- **`git commit` detection is heuristic** on the command string (handles `cd … &&`, env prefixes, `-c` global flags); unusual phrasings may slip. Acceptable given the advisory-leaning posture.

Cross-references: `adversarial-default.md` (burden of proof on the asserter), ADR-0002.
