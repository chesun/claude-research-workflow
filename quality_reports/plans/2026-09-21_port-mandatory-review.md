# Port the mandatory independent-review pattern into this personal template

**Status:** DRAFT v2 — revised after independent review (`quality_reports/reviews/2026-09-21_port-mandatory-review-plan_review.md`, 75/100, fit-with-fixes) and two owner decisions. Awaiting go to build.
**Source pattern:** a sibling work repository's ADR-0016 + `independent-review.md` + `bin/commit-msg-guard.py` + `/review-build`.

## What v2 changed (from the review)

The plan review verified the mechanism is faithful and the hooks-path premise true, but flagged that v1 reached for the most invasive design and the heaviest possible cost. Two owner decisions resolve it:

- **Mechanism → a `PreToolUse` Bash hook on `git commit`,** not a git `commit-msg` hook. This is wired in `settings.json` like every other gate here, needs **no `core.hooksPath` override and no shims**, and travels with the repo. It fires only for commits made through Claude Code — acceptable for a strictly-personal repo committed that way. This deletes v1's entire override/shim/delegation risk surface.
- **Scope → gate code, advise on docs.** Block a commit only when a staged **code** artefact (`.claude/hooks/**`, `bin/**` scripts, `.githooks/**`) lacks a review receipt. For **docs** (`.claude/rules`, `.claude/agents`, `.claude/skills`, `decisions/NNNN`, `quality_reports/plans`, `templates`, `.claude/references`) emit a **non-blocking advisory**. This keeps the expensive review where a defect is costly and self-missed, and stops it taxing routine doc editing — the repo's main activity.

v2 is not re-reviewed as a plan: it adopts the reviewer's own two recommendations, so a fresh plan cycle would spend 300–600k tokens to confirm its own advice. The review budget is spent instead on the **guard code**, which is genuinely new and is itself gated by this rule (dogfood).

## The mechanism

`PreToolUse` (matcher `Bash`) hook `.claude/hooks/review-receipt-check.py`:

1. Read `tool_input.command`. Detect a `git commit` (handle `cd X && …`, `-m`, `-F`, heredoc; ignore `git commit --amend`? — treat like a normal commit). If not a commit, exit 0.
2. If `git config review.required` is not `true`, exit 0 (opt-in; decoupled from the machine guards' repository-class setting).
3. Classify staged paths (`git diff --cached --name-status -z -M`): CODE vs DOC vs neither (receipt logic ported from the work repository's guard — `target_matches` by exact path / unique basename / `ADR-NNNN`, `Score`+`Status` header, freshness ≥ path's last commit and not future).
4. **CODE path missing a receipt → block (exit 2)** with the remediation. **DOC path missing a receipt → advisory** on stderr (exit 0), listing them.
5. **Waiver:** an env prefix `REVIEW_WAIVE=1 git commit …` (visible in the command, auditable in shell history) skips the code block. `--no-verify` does NOT bypass a PreToolUse hook, so the env waiver is the deliberate escape; note this in the rule.

No scrub/message-content scan (that was an employer-confidentiality concern; message confidentiality is out of scope for this personal repo — its push guard already governs what leaves the machine).

## Files

- `.claude/rules/independent-review.md` — genericized: what binds, code-block/doc-advise split, lenses, review definition, receipt, env waiver, limits. No employer or confidentiality wording.
- `decisions/0002_mandatory-independent-review.md` — ADR (decisions/ holds 0001).
- `.claude/hooks/review-receipt-check.py` — the PreToolUse guard (self-contained; no scrub dependency).
- `.claude/hooks/test_review_receipt_check.py` — harness: git-commit detection incl. `cd &&`, gated CODE vs DOC classification, receipt match (path/basename/ADR), freshness, waiver, fail-open-vs-closed (see cautions).
- `.claude/skills/review-build/SKILL.md` — dispatches the lens pair for a target, saves reports with the receipt header, logs one cost line.
- `settings.json` — add the PreToolUse Bash entry.

## Lenses (unchanged from source)

code → red-team + correctness; plans/ADRs → fit-for-purpose + efficiency; rules → consistency + bloat; agents/templates/references/skills → correctness. A review is a **fresh general-purpose agent (never a fork)**, blind to the other lens, read-only except its report, evidence per finding, synthetic sentinels, saved to `quality_reports/reviews/YYYY-MM-DD_<target>_<lens>_review.md` and **staged**, header `**Date:** **Reviewer:** **Target:** **Score:** NN/100 **Status:** Active`.

## Phases

1. **Build** rule, ADR, hook, tests, skill; wire settings.json; `git config review.required true`. Gate: `test_review_receipt_check.py` green; a manual dry-run shows a code-only staged set blocks without a receipt and passes with one, a doc-only set advises, a mixed set blocks on the code.
2. **Dogfood:** run `/review-build` (code lens + correctness) on `review-receipt-check.py` and the rule; fix findings; stage the reports.
3. **Commit the port** — the staged review reports are the receipts for the hook; the rule/ADR/plan are docs (advisory, no block).
4. **Document:** `CLAUDE.md` Core Principles bullet + rules-list line; `TODO.md`; INDEX files.

## Fail-open vs fail-closed (a real decision for a PreToolUse gate)

A `commit-msg` git hook can fail closed cheaply (a broken guard blocks the commit; you use `--no-verify`). A `PreToolUse` hook that fails closed on an internal error would **block all git commits in the session with no `--no-verify` escape** — a session-lockout risk. So this hook **fails OPEN on internal error** (exit 0, log to stderr): a guard bug must not make the repo uncommittable. It exits 2 **only** on the deliberate policy result (a gated code path with no receipt). This matches the workflow's "session hooks fail open" stance and is the safe default here; the cost is that a guard bug silently disables the gate until noticed.

## Cautions / known limits

- Fires only inside Claude Code (accepted per the mechanism decision).
- `git commit` detection is heuristic on the command string; document the forms covered; `--amend` and unusual phrasings may slip — acceptable for a personal advisory-leaning gate.
- Do not copy employer-specific content; port the mechanism only.
- Adding a hook after pruning nine is justified only as a code gate (costly, self-missed defects); docs stay advisory precisely so this does not re-grow the nag scaffolding.
