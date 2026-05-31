# 2026-05-31 — Recovery: Consumer CLAUDE.md and README.md Wiped by /tools propagate

**Status:** COMPLETED
**Author:** Claude (Opus 4.7) with Christina
**Branch:** main

---

## Problem

Across all 7 registered consumers, `CLAUDE.md` and `README.md` had been replaced with workflow-template boilerplate by past `chore(workflow-sync)` propagation commits. Consumer-specific project content (project overviews, coauthors, server execution model, identification strategy, repo structure) was clobbered.

## Root cause

`.claude/file-classes.toml` misclassified both files:

- **`CLAUDE.md` → Class B (overlay-customized).** Class B reads from the consumer's overlay branch *of the workflow source*. The workflow source's `CLAUDE.md` is a template, not the consumer's actual project description, so propagation pushed the template anyway. The "overlay-customized" semantics were never the right fit for a file whose source-of-truth lives in the consumer itself.
- **`README.md` → Class A (universal).** Class A pushes the workflow source's `README.md` to every consumer unconditionally, replacing each consumer's project README with the workflow's preview-release-v0.1.0 boilerplate.

Both files describe the *consumer's* project, not the workflow. The correct class is D (excluded) — each consumer owns its own copy.

## Recovery actions

For each consumer, identified the parent of the first `chore(workflow-sync)` commit that touched the file via:

```
git log --reverse --format=%H --grep="chore(workflow-sync)" -- <file> | head -1
git rev-parse <first-wipe>^
```

Then `git checkout <parent> -- <file>` and committed.

### Recovery commit table

| Repo | Branch | Pre-wipe parent | Files restored | Recovery commit |
|---|---|---|---|---|
| belief_distortion_discrimination | main | 69bf7cb | CLAUDE.md (176 lines); README.md deleted (didn't exist pre-wipe) | 6911070 |
| belief_distortion_discrimination_audit | audit-fix | 82619c7 | CLAUDE.md (151 lines); README.md deleted | 4e7962a; corrected by cd985f7 (intermediate commit 155c1e0 used wrong main-branch SHA due to failed worktree switch — see Lessons) |
| belief_distortion_discrimination_audit | main (shared worktree with BDD repo) | (same as BDD main) | (handled via BDD repo's commit 6911070) | (same) |
| bdm_bic | main | 873de29 | CLAUDE.md (163 lines); README.md (2 lines) | e0f70bb |
| csac | main | 3199afd | CLAUDE.md (135 lines); README.md (43 lines) | 4ca4108 |
| csac2025 | main | 528d77d | CLAUDE.md (148 lines); README.md (2 lines) | d54daac |
| tx_peer_effects_local | main | 2210cd0 | CLAUDE.md (147 lines); README.md (3 lines) | b42728e |
| va_consolidated | main | ac9340f | CLAUDE.md (162 lines); README.md (311 lines) | 78d6f3c |

### Manifest fix

`claude-code-my-workflow` commit **0b40e3e** moves `CLAUDE.md` and `README.md` from Class B / Class A to Class D (excluded) in `.claude/file-classes.toml`. Verified end-to-end with `python3 .claude/skills/tools/propagate.py --dry-run CLAUDE.md README.md`: all 7 consumers report "EXCLUDED (skipped — manifest [exclude] match)".

## Lessons

1. **Worktree-linked repos share branches.** `belief_distortion_discrimination_audit/` is a `git worktree` of `belief_distortion_discrimination/` — `main` is checked out in the parent, `audit-fix` in the linked worktree. A naive `git checkout main` in the audit dir fails (`fatal: 'main' is already checked out at <parent path>`). The intermediate mistake (commit 155c1e0) used main's pre-wipe SHA on audit-fix because of this failure. Fix: run `git worktree list` first when restoring across branches.
2. **Forward-port lost?** Between the first wipe commits and current HEAD, the only post-wipe edits to consumer CLAUDE.md were template-level additions (`Analysis roots:` header line, `Evidence gating` principle, `Cross-Repo Propagation` section). None were consumer-specific. They can be hand-merged into each restored CLAUDE.md later if desired; the recovery did not graft them.
3. **What the wipe commits also touched.** Each `chore(workflow-sync)` commit propagated many files at once (hooks, rules, skills). The recovery only reverted `CLAUDE.md` and `README.md` — all other propagated files remain at their current state, which is correct (those are legitimately Class A / B).
4. **Detection gap.** The propagation never alerted because every file matched a class and was processed per its class. The bug was a categorization error, not a code defect. Mitigation now structural via [exclude] entries.

## Verification

- All 7 consumers' CLAUDE.md and README.md now contain pre-wipe project-specific content.
- Workflow source `python3 .claude/skills/tools/propagate.py --dry-run CLAUDE.md README.md` reports 14/14 EXCLUDED.
- No history rewrites; all changes are forward commits.
- Audit-fix branch in `belief_distortion_discrimination_audit` has its own divergent restoration (151-line CLAUDE.md from 82619c7) distinct from main's (176-line from 69bf7cb).
