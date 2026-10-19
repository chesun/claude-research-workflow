# Independent Review — mechanism detail

**Class:** A (universal). Pointer-loaded detail for `.claude/rules/independent-review.md` § Mechanism and its limits (moved from the rule on 2026-10-19); there is no auto-load.

## Mechanism and its limits

The hook is `PreToolUse` (matcher `Bash`): it inspects the `git commit` command Claude Code is about to run and checks the staged index. Consequences to know:

- **Fires only for commits made through Claude Code.** A commit from an external terminal or IDE is not seen. Accepted for a strictly-personal repo committed through Claude Code.
- **`--no-verify` does NOT bypass it** (that flag skips git hooks, not PreToolUse hooks). The deliberate escape is the `REVIEW_WAIVE=1` prefix.
- **Fails closed, escapably.** Once the hook has confirmed a gated, opt-in, non-waived commit, a git error or bug while evaluating the receipt **blocks** the commit (exit 2, loud banner, appended to `.claude/state/review-gate-failures.log`) rather than silently allowing it. This is not a lockout: `REVIEW_WAIVE=1` is parsed before any git call, so a broken guard is always escapable. And errors *before* the commit is confirmed gated still allow the command — the hook runs on every Bash call, so it must never brick ordinary shell use. So the only silent-allow paths are genuinely non-gated ones; a confirmed gated commit is never let through un-evaluated.
- **`git commit` detection is heuristic** on the command string (handles `cd … &&`, env prefixes, `-c` global flags); unusual phrasings may slip. Acceptable given the advisory-leaning posture.
