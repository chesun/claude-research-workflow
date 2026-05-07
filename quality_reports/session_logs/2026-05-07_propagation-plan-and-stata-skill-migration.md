# Session Log: 2026-05-07 — Comprehensive Propagation Plan (DRAFT) + Stata Skill Migration

<!-- primary-source-ok: new_2026, added_2026, inserted_2026, extended_2026, replaced_2026, changed_2026, removed_2026, deleted_2026, fixed_2026, copied_2026, merged_2026, dropped_2026, status_2026, plan_2026, this_2026 -->

**Status:** IN PROGRESS

> **Note on the escape-hatch comment above:** session logs frequently contain phrases like "New 2026-05-07 entry" or "Added reminder ... (2026)" that trip the primary-source-first regex as false-positive `Author (year)` citations. Each stem listed above is a common changes-table verb plus a year that the regex sees as a citation. None of them are real citations. Tracked in TODO as a follow-up to extend `NEVER_SURNAMES` in `.claude/hooks/primary_source_lib.py`.

## Objective

Two threads in this session, both grounded in earlier infrastructure work:

1. **Drafted the comprehensive propagation plan** the 2026-05-06 evening session deferred. The v1 propagate skill is implemented and works for byte-identical files, but cherry-pick attempts onto overlay branches surfaced parallel-history conflicts on shared files (`INDEX.md`, `CLAUDE.md`, `tools/SKILL.md`). The fresh plan introduces a three-class file taxonomy (Universal / Overlay-customized / Overlay-only), a manifest at `.claude/file-classes.toml`, modified routing in `propagate.py`, and a fresh `/tools sync-overlays` skill for `main → overlay` propagation.

2. **Migrated the Stata skill from `claude-config` to `claude-code-my-workflow`** after a side-quest diagnostic revealed BDD's Claude session was invoking Stata 14 (via `/Applications/Stata/StataMP.app/Contents/MacOS/StataMP`) instead of Stata 17. Root cause: the global `claude-config/skills/stata/SKILL.md` advised `stata-mp` but also documented the `/Applications/Stata/...` path (Stata 14) in its installation section, inviting Claude to copy it verbatim. No workflow rule mandated PATH-based invocation. The migration brings the skill into the workflow (where it propagates to research consumers), drops the Stata 14 documentation, and standardizes on `stata17` as the canonical command.

## Changes Made

| File | Change | Reason | Commit |
|---|---|---|---|
| `quality_reports/plans/2026-05-07_comprehensive-propagation-plan.md` | NEW — 12 sections + 2 appendices, ~700 lines | Settles the deferred design question from 2026-05-06 evening | (1) plan |
| `quality_reports/plans/INDEX.md` | Index entry inserted for the 2026-05-07 plan; reframed v1 entry as "extended by" | Plan lifecycle bookkeeping | (1) plan |
| `quality_reports/plans/2026-05-06_tools-propagate-plan.md` | Header status now reads "Extended by 2026-05-07 plan" | Lifecycle bookkeeping; v1 implementation preserved as load-bearing | (1) plan |
| `TODO.md` | "Write comprehensive propagation plan" replaced with "Review the comprehensive propagation plan" | Plan now exists; review is the next action | (1) plan |
| `.claude/skills/stata/SKILL.md` | NEW — migrated from `claude-config/skills/stata/SKILL.md` with edits: dropped Stata 14 section, mandated `stata17` invocation, warning against `/Applications/Stata/...` direct calls | Bring research-context skill into the workflow; fix the Stata-14 invocation bug | (2) stata |
| `.claude/skills/stata/references/doc_lookup.md` | NEW — copied from `claude-config`, then edited: top-of-file note that `~/Documents/stata/docs/` is the Stata 17 manual set; replaced hardcoded `/Users/christinasun/...` with `os.path.expanduser('~/...')`; dropped stale "Both Stata installations" line | Single-version doc lookup; portable for forks | (2) stata |
| `.claude/rules/stata-code-conventions.md` | Inserted "Invocation (local machine)" section mandating `stata17`, with rationale (StataMP.app shared name across versions) and cross-reference to the skill | Codify the rule that was missing from the workflow | (2) stata |
| `claude-config/skills/stata/{SKILL.md, references/doc_lookup.md}` | Deleted via `git rm` | Migrated to workflow; no longer global | (3) claude-config |
| `quality_reports/session_logs/2026-05-07_propagation-plan-and-stata-skill-migration.md` | This file — session log | Logging.md trigger 1: post-plan log + thread close | (4) log |
| `TODO.md` | Fresh entries: changelog reminder for next docs pass; note re user's draft unicode-fix proposal at `proposals/2026-05-07_primary-source-hook-unicode-fix.md`; extend blocklist TODO with the changes-table verbs that tripped this very log | Track for follow-up | (4) log |

## Design Decisions

| Decision | Alternatives Considered | Rationale |
|---|---|---|
| Three-class file taxonomy (Universal / Overlay-customized / Overlay-only) + Excluded | (a) two classes only, (b) per-branch full duplication, (c) treat all as overlay-customized | Three classes match observed reality with minimum complexity. Two-class loses the "stale-of-main" vs "genuinely customized" distinction. Per-branch duplication is what we have today and it's broken. |
| Manifest at `.claude/file-classes.toml` (tracked, on main) | (a) `.claude/state/file-classes.toml` (gitignored — bad), (b) root `file-classes.toml` (less namespaced) | Tracked + reviewable + lives at workflow level. Itself Class A (universal) so it propagates to overlays. |
| Default classification = Universal when unlisted | Default = explicit-required-for-all-files | Most files are universal; explicit-required would balloon the manifest to ~200 entries. Defaults match the empirical majority. |
| `/tools sync-overlays` as separate skill | Fold into propagate as `propagate --sync-overlays` | Different conceptual operation (intra-workflow, between branches) vs propagate (workflow → consumers). Different state semantics. Easier to test independently. |
| Bootstrap classification approach: auto-propose then human-review | Hand-write the manifest from scratch | ~200 paths to classify; scripted proposal + human review beats hand-classification on speed *and* accuracy. |
| Plan supersedes v1 by extension, not replacement | Mark v1 fully superseded and discard | v1's `propagate.py` (433 LOC) is implemented and load-bearing. v2 adds a routing layer on top. Marking "extended" preserves the implementation as authoritative. |
| Stata skill migrated *into* workflow, not duplicated | (a) keep in claude-config + duplicate to workflow, (b) keep in claude-config only | User's intent: research-context skill should ride with research workflow. Duplication risks divergence; keeping global only doesn't fix the BDD invocation bug surface. |
| Dropped Stata 14 section entirely from the migrated skill | Keep both versions documented, mark Stata 17 as default | The Stata 14 path being *documented* was the proximate cause of Claude copying it. Removing it from the skill removes the temptation. Stata 14 is still installed on the machine but irrelevant to research workflow. |
| Standardized on `stata17` (not `stata-mp`) as canonical command | `stata-mp` (which also resolves to Stata 17 on this machine via PATH precedence) | `stata17` is unambiguous. `stata-mp` happens to resolve correctly today but would silently break if PATH ordering changes or another Stata install lands. Defense-in-depth. |
| Wrapped pdfplumber example in `os.path.expanduser('~/...')` | Hardcode `/Users/christinasun/...` (original) | Skill is now in a fork-able workflow repo per meta-governance. Portable paths matter even though Christina is the only current operator. |
| Did NOT propagate the fresh skill to BDD manually | Manually copy to BDD now to fix the immediate bug | (a) The rule update in `stata-code-conventions.md` plus future propagation is the right path. (b) Manual copy creates an unsync'd starting point that the comprehensive plan will then have to reconcile. (c) The current BDD agent's bad invocations were caught in the destructive-action-guard log; user is aware. |

## Incremental Work Log

**13:00 UTC:** Resumed from yesterday's stopping point. Read TODO, recent commits, and the 2026-05-05 session log (Day 2 evening section) to recover context. Confirmed: comprehensive propagation plan is the unblocker for both consumer sync and overlay sync.

**13:15 UTC:** Inspected the existing `.claude/state/consumers.toml` (7 entries), `propagate.py` (433 LOC, working), and the 2026-05-06 v1 plan. Confirmed v1 implementation is load-bearing; this plan should extend, not replace.

**13:25 UTC:** Diffed `main` vs `behavioral` and `main` vs `applied-micro` to identify the shape of overlay divergence. Found three distinct cases mixed together: (1) overlay-only files like `designer.md` / `strategist.md`, (2) genuinely customized files like `orchestrator.md` (behavioral has an Experimental Pipeline section the user authored), (3) stale-of-main files where the overlay just lags. Spot-checked `analyze/SKILL.md` — behavioral version defaults to Stata 17 + behavioral domain-profile. Confirmed Class B is real, not just lag.

**13:50 UTC:** Drafted `2026-05-07_comprehensive-propagation-plan.md` with sections 0–11 + appendices. 700 lines, 14 settled decisions, 10 [USER] questions flagged. Wrote v1 plan status header update and INDEX entry.

**14:10 UTC:** User asked a side-quest: "in BDD claude is calling stata.MP in the application folder, and that invokes stata14...this should be already in the workflow. why is this happening." Investigated.

**14:15 UTC:** Confirmed the rule was NOT in the workflow — the closest thing is `claude-config/skills/stata/SKILL.md:165` ("use `stata-mp` (resolves to Stata 17)") but the same skill *also documents* `/Applications/Stata/StataMP.app/Contents/MacOS/stata-mp` in the Installation section. Claude reads the skill, sees the path, copies it. BDD's destructive-action-guard log shows three calls to `/Applications/Stata/StataMP.app/Contents/MacOS/StataMP` between 23:02 and 23:04 UTC the prior evening.

**14:20 UTC:** Diagnosed three gaps: (a) no rule mandating PATH-based Stata invocation in the workflow; (b) no PreToolUse hook blocking direct `/Applications/Stata/...` calls; (c) the global skill itself documenting the Stata 14 path. Recommended three fixes; user picked: drop Stata 14 from skill + insert binary call rule into `stata-code-conventions.md` + migrate skill to workflow. Skipped the hook for now.

**14:35 UTC:** Created `claude-code-my-workflow/.claude/skills/stata/SKILL.md` with the corrected content (dropped Stata 14 section, mandated `stata17`, updated all examples, updated instruction #4 with the warning). Copied `references/doc_lookup.md` verbatim. Verified diff against original.

**14:40 UTC:** `git rm -r skills/stata/` in claude-config. The directory-level symlink at `~/.claude/skills` still works — only the per-file content moved. Sessions in workflow consumers (or in the workflow itself) now pick up the project-level skill; sessions in non-consumer projects lose the skill (acceptable per migration intent).

**14:45 UTC:** Edited `.claude/rules/stata-code-conventions.md` — inserted "Invocation (local machine)" section under "Version". Cross-referenced the skill.

**14:50 UTC:** User flagged: "make sure the doc lookup links to the correct stata17 doc". Re-read `doc_lookup.md`. Verified `~/Documents/stata/docs/` is the Stata 17 manual set (March 2024 PDFs); `/Applications/Stata/docs/` is the Stata 14 set. Found three issues:

1. Stale line at end: "Both Stata installations share the same documentation layout..." — implied Stata 14 still in scope.
2. Hardcoded `/Users/christinasun/Documents/stata/docs/r.pdf` in the Python snippet — Christina-specific, brittle for forks.
3. No top-of-file reference to which Stata version the docs path corresponds to.

Patched all three: top-of-file note + warning, `os.path.expanduser` wrap on the hardcoded path, dropped the stale line.

**15:00 UTC:** User: "yes please commit and push. and log the work in this repo. this new stata skill will need to go in the changelog when we write the updated docs." Wrote this session log; updated TODO with changelog reminder; staged the four-commit sequence.

**15:10 UTC:** First write of this log tripped the primary-source-first hook on a false positive: a table-cell phrase beginning with the word "Added" followed elsewhere by "(2026)" parsed as a citation. Reworded the offending cells. Second write tripped on "New 2026-05-07 entry" pattern. Third write applies the escape-hatch comment at the top of the file covering all the changes-table verbs. User confirmed the previously-mysterious file at `proposals/2026-05-07_primary-source-hook-unicode-fix.md` is their draft fix for a related primary-source regex issue (unicode); also logged in TODO.

## Learnings & Corrections

- **[LEARN:rules]** A workflow rule that's only documented in a global skill (`~/.claude/skills/...`) is too soft. The rule needs to be in `.claude/rules/` so it's part of the workflow's enforced contract; the skill is for syntax / patterns / examples, not for load-bearing rules. The Stata-14 bug propagated for weeks because the rule lived in the wrong layer.
- **[LEARN:skills]** When documenting a tool that has multiple installed versions on a machine, do NOT list paths to non-canonical versions. The path is an attractive nuisance — Claude will read the documentation and copy the wrong path. Mention version-pinned aliases (`stata17`) and warn against alternatives, but don't quote the wrong-version paths.
- **[LEARN:propagation]** Overlay branches are not "stale main" — they're genuinely customized at specific files. Mechanical sync (cherry-pick, full-branch merge) drops user customizations or generates conflict on every commit. The fix isn't a smarter merge tool; it's a per-file class taxonomy that names which file's source-of-truth lives where.
- **[LEARN:meta-governance]** Skills that are research-context (Stata, R, Python, LaTeX) belong in the workflow repo where they propagate to research consumers, not in global `claude-config`. Skills that are universally useful across non-research contexts (skill-creator, mcp-builder, pdf, docx) stay global. The split: project-relevant or research-relevant → workflow; everything else → global.
- **[LEARN:hooks]** Common past-tense English verbs at table-cell starts ("Added", "Fixed", "Removed", "New") followed elsewhere by a four-digit year trip the primary-source regex when neither the all-caps filter nor the sentence-start filter catches them. Table-cell pipes aren't sentence terminators in the regex's view. Add to the `NEVER_SURNAMES` blocklist alongside the existing status-word entries (`Resolved` / `Pending` / `Deferred` / `Open`). Until the blocklist is extended, session-log writers should add an escape-hatch comment near the top covering the common changes-table verbs.

## Verification Results

| Check | Result | Status |
|---|---|---|
| Comprehensive plan saved at correct path with correct status header | Yes | PASS |
| INDEX.md and v1 plan status updated for lifecycle | Yes | PASS |
| Stata skill landed at `.claude/skills/stata/SKILL.md` | Yes (4 sections updated, 1 dropped, 1 sub-rule slotted into instructions) | PASS |
| `references/doc_lookup.md` copied + corrected (top-of-file + Python snippet + bottom line) | Yes (3 edits applied) | PASS |
| `stata-code-conventions.md` Invocation section present | Yes | PASS |
| Skill index now shows single `stata` entry (was duplicated mid-session, then claude-config side `git rm`'d) | Yes | PASS |
| All Stata 17 doc paths correct (`~/Documents/stata/docs/` only; no `/Applications/Stata/docs/` references in skill or rule) | Yes (grep clean) | PASS |
| No accidental commits or pushes pre-authorization | Yes | PASS |

## Open Questions / Blockers

- [ ] **The comprehensive propagation plan is DRAFT.** 10 [USER] decisions to confirm/amend. Implementation breaks into Phase A (manifest) → Phase B (propagate.py routing) → Phase C (sync-overlays) → Phase D (bootstrap) → Phase E (docs). Total estimate ~5–6 hours over 1–2 sessions. User needs to review.
- [ ] **The migrated Stata skill has not yet propagated to BDD or other consumers.** Until the comprehensive plan's Phase D bootstrap runs, the skill exists only on workflow `main`. BDD's Stata-14 bug will recur until either (a) the comprehensive plan lands and propagates, OR (b) the skill is manually copied to BDD's `.claude/skills/stata/`. Current state: BDD agent is aware of the bug from the prior session; user can intervene if it recurs before propagation lands.
- [ ] **Stata skill needs a changelog entry when updated docs are written** — recorded in TODO; mention as a release-note item.
- [ ] **User's draft proposal at `quality_reports/plans/proposals/2026-05-07_primary-source-hook-unicode-fix.md`** — copied from BDD repo as a starting point for a primary-source regex fix on unicode handling. Tracked in TODO; left untracked until user is ready to land it.
- [ ] **Overlay branches still don't have the migrated stata skill or rule update.** They lag main on this commit too. Will be picked up by the comprehensive plan's `/tools sync-overlays` once Phase C lands.
- [ ] **`~/.claude/settings.json` drift** — still in backlog from 2026-05-05; not addressed today.

## Next Steps

(See `TODO.md` for the persistent cross-session view.)

- User reviews the comprehensive propagation plan; confirms or amends the 10 [USER] decisions.
- Implementation phases A–E, in dependency order, in 1–2 follow-up sessions.
- Until then: when committing routine workflow updates, manual cherry-picks onto overlays remain off-limits (parallel-history conflicts); manual file copies to specific consumers remain on-limits but should be tracked in a session log.
