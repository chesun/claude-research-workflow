# Session Log: 2026-09-21 — Port the mandatory independent-review pattern

**Status:** COMPLETE (built, dogfood-reviewed, committed). Continues the Claude-5 modernize effort; this repo is the strictly-personal research template.

## Goal

Turn the manual "dispatch a fresh adversarial reviewer for load-bearing artefacts" habit into an enforced gate, ported from a sibling work repository (its ADR-0016). Decision to build: ADR-0002.

## What was built

- `.claude/hooks/review-receipt-check.py` — PreToolUse (Bash) hook. On a `git commit`, blocks (exit 2) if staged **code** (`.claude/hooks/**`, `bin/**` scripts, `.githooks/**`) lacks a review receipt; **advises** (non-blocking) on staged docs. Opt-in via `git config review.required true`; waiver `REVIEW_WAIVE=1` leading prefix; **fails open** on internal error (a PreToolUse gate has no `--no-verify` escape, so it must never lock the session out). Tests: `.claude/hooks/test_review_receipt_check.py`, 35/35.
- `.claude/rules/independent-review.md`, `decisions/0002_mandatory-independent-review.md`, `.claude/skills/review-build/SKILL.md`. Wired into `settings.json` (PreToolUse Bash, beside the destructive-action guard); `review.required=true` set.

## Reviews (the pattern, applied to itself)

- **Plan** independently reviewed (`2026-09-21_port-mandatory-review-plan_review.md`, 75/100). Its two recommendations became owner decisions: PreToolUse mechanism (not a git commit-msg hook, so no `core.hooksPath` override) and gate-code / advise-docs (not gate-everything). Plan v2 adopted both.
- **Hook** dogfood-reviewed by two fresh, blind lenses: red-team `2026-09-21_review-receipt-check_redteam_review.md` (66/100) and correctness `..._correctness_review.md` (72/100). Both are the staged receipts for the two code files. Cost ≈ 238k agent tokens total, ~9 min each in parallel.

## Findings resolved

- **High (both lenses, independently) — waiver false-trigger.** `parse_commit` matched `REVIEW_WAIVE=` anywhere in the command, so a commit message merely mentioning it silently waived the gate (fires exactly when committing the review system itself). **Fixed:** the waiver is honoured only as a leading env-assignment token of the commit segment; regression test added.
- **Medium (correctness) — nested paths under `.claude/hooks/` escaped classification** (`.claude/hooks/tests/*.py`). **Fixed:** the regex now allows nesting like `bin/`; regression tests added. Also added `git.exe` detection (Windows) and a missing-field-receipt rejection test. Suite 29 → 35.

## Findings accepted (one-line reasons, per the rule)

- **Low — heuristic commit detection misses subshell/brace-group/pipeline-wrapped commits.** Accepted: the gate is advisory-leaning for a non-adversarial solo author, the waiver is deliberately trivial, and the rule documents detection as heuristic.
- **Low — day-granular / timezone freshness.** Accepted: inherent to the date-only receipt header; documented as a known limit.
- **Low — `target_matches` breadth; PASS-vs-`NN/100` score.** Accepted: receipts are author-written (not adversarial), and `/review-build` mandates the `NN/100` header, so the format is internally consistent.

No Criticals, so no extra verify pass beyond the two regression tests that pin the High and Medium.

## Next (not done)

- Behavioral-overlay mirror of the modernize prune (Track A step 3), the live-project update (step 4), and retiring the propagation automation (step 5) remain open from the modernize plan.
- The `/review-build` cost-line logging is a manual step in the skill; automating it is a future nicety.
