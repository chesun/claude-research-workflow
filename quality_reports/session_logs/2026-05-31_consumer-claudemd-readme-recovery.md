# 2026-05-31 — Consumer CLAUDE.md / README.md recovery

## Goal

Christina reported: "the previous propagations wiped all of the consumer repo claude.md and readme.md files and replaced them with boilerplate templates." Recover the consumer-specific content and prevent re-occurrence.

## What happened

1. **Damage survey.** All 7 registered consumers (`belief_distortion_discrimination`, `_audit`, `bdm_bic`, `csac`, `csac2025`, `tx_peer_effects_local`, `va_consolidated`) had CLAUDE.md and README.md replaced with workflow-template boilerplate — confirmed by `head` on each file.
2. **Root cause identified.** `.claude/file-classes.toml` classified `CLAUDE.md` as Class B (overlay-customized) and `README.md` as Class A (universal). Both pulled from the workflow source — the workflow's CLAUDE.md is a template, not the consumer's project description; same for README. Both should have been Class D (excluded) all along.
3. **Pre-wipe SHA per consumer.** Found via `git log --reverse --grep="chore(workflow-sync)" -- <file> | head -1` then `git rev-parse <first-wipe>^`. Verified pre-wipe content was real consumer content (135-176 lines of CLAUDE.md, 2-311 lines of README.md per repo).
4. **User decisions (via AskUserQuestion):** restore + commit directly (not on a review branch); fix the manifest at the same time; for BDD audit, restore on both audit-fix and main.
5. **Execution.** For each consumer: `git checkout <parent> -- CLAUDE.md README.md` (or `git rm README.md` for the 2 repos where it didn't exist pre-wipe), then one fix commit per consumer.
6. **One mistake.** On BDD audit's audit-fix branch, `git checkout main` failed silently (BDD audit is a `git worktree` of BDD; main is checked out in the parent dir). The next `git checkout 69bf7cb -- CLAUDE.md` ran on audit-fix instead, writing main's 176-line version into the audit-fix branch (commit 155c1e0). Corrected with a follow-up commit `cd985f7` that re-restored from 82619c7 (audit-fix's actual pre-wipe parent, 151 lines).
7. **Manifest fix.** Moved CLAUDE.md and README.md to Class D in `.claude/file-classes.toml`. Committed (0b40e3e in workflow source). Verified end-to-end with `--dry-run` — all 7 consumers report EXCLUDED for both files.

## Recovery commit SHAs

| Repo | Branch | Pre-wipe parent | Commit |
|---|---|---|---|
| belief_distortion_discrimination | main | 69bf7cb | 6911070 |
| belief_distortion_discrimination_audit | audit-fix | 82619c7 | 4e7962a + cd985f7 |
| (BDD audit main — shared worktree with BDD) | main | (same as BDD) | (covered by 6911070) |
| bdm_bic | main | 873de29 | e0f70bb |
| csac | main | 3199afd | 4ca4108 |
| csac2025 | main | 528d77d | d54daac |
| tx_peer_effects_local | main | 2210cd0 | b42728e |
| va_consolidated | main | ac9340f | 78d6f3c |
| claude-code-my-workflow (manifest fix) | main | — | 0b40e3e |

## Open questions

- Push the recovery commits to each consumer's remote? Christina did not authorize push; recovery commits are local-only. She can `git push` per repo when ready.
- Forward-port the post-wipe template additions (Analysis roots header line, Evidence gating principle, Cross-Repo Propagation section) into the restored consumer CLAUDE.md files? Not done — those are workflow-template enhancements, not consumer content. Christina can graft if desired.

## Lessons (for future work)

1. **`git worktree list` first** when restoring files across branches in a worktree-linked repo.
2. **A new class type "consumer-owned"** would be more explicit than "exclude" — currently the [exclude] section mixes "never propagate" with "consumer-specific". Not necessary now since exclude works correctly, but if more files in this category emerge, consider a dedicated section.
3. **Audit other Class A / Class B paths** for similar miscategorization. Spot check suggests rules / hooks / skills are correct (those are workflow infrastructure that should propagate), but the user may want a broader review.

## Files touched

- `belief_distortion_discrimination/CLAUDE.md` (restored), `README.md` (deleted)
- `belief_distortion_discrimination_audit/CLAUDE.md` (restored 2x — intermediate mistake), `README.md` (deleted)
- `bdm_bic/CLAUDE.md`, `bdm_bic/README.md` (restored)
- `csac/CLAUDE.md`, `csac/README.md` (restored)
- `csac2025/CLAUDE.md`, `csac2025/README.md` (restored)
- `tx_peer_effects_local/CLAUDE.md`, `tx_peer_effects_local/README.md` (restored)
- `va_consolidated/CLAUDE.md`, `va_consolidated/README.md` (restored)
- `claude-code-my-workflow/.claude/file-classes.toml` (CLAUDE.md and README.md moved to Class D)
- `claude-code-my-workflow/quality_reports/plans/2026-05-31_consumer-readme-claudemd-recovery.md` (recovery plan)
- `claude-code-my-workflow/quality_reports/session_logs/2026-05-31_consumer-claudemd-readme-recovery.md` (this file)
