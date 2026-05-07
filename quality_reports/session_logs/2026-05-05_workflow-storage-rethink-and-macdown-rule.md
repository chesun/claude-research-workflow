# Session Log: 2026-05-05 — Workflow storage rethink, MacDown rule v2, copyright strip

**Status:** IN PROGRESS

## Objective

Three loosely-related threads across the day:

1. Patch MacDown markdown rule for a newly-discovered LaTeX-rendering bug (spaces inside `$...$` delimiters).
2. Rethink storage architecture for gitignored bulk content; replace the Dropbox-symlink approach with a Git LFS + DVC + periodic-Dropbox-backup plan.
3. Strip copyright-as-reasoning from the workflow after user correction (PDFs are fair-use; authors share freely).

## Changes Made

| File | Change | Reason | Quality Score |
|---|---|---|---|
| `claude-config/rules/markdown-macdown-compat.md` | Added rule 4: no space between `$` and math content | MathJax inline-math requires non-space char immediately inside delimiters | n/a (rule update) |
| `belief_distortion_discrimination/quality_reports/plans/2026-05-01_analysis-upgrade-memo.md` | Fixed 7 broken inline/display math spans (lines 65, 75, 79, 87, 99, 139, 155) | New rule applied retroactively | n/a (cosmetic fix) |
| `claude-code-my-workflow/quality_reports/plans/2026-05-05_lfs-vs-dvc-explainer.md` | New file — concept-level explainer for Git LFS and DVC | User asked for explanation of both tools | n/a (explainer) |
| `claude-code-my-workflow/quality_reports/plans/2026-05-05_lfs-dvc-migration-plan.md` | New file — concrete migration plan with 14 sections, 2 [USER] decisions, supersedes Dropbox-symlink plan | User asked for detailed and concrete plan before any execution | n/a (plan) |
| `claude-code-my-workflow/quality_reports/plans/archive/2026-05-01_dropbox-symlink-setup-explainer.md` | Moved from `plans/` to `plans/archive/`; status updated to "Superseded by..." | Lifecycle protocol for superseded plans | n/a |
| `claude-code-my-workflow/quality_reports/plans/INDEX.md` | Added two new plans, struck through superseded one | Index hygiene | n/a |
| `claude-code-my-workflow/.gitignore` | PDF block comment rewritten — repo-bloat reasoning, no copyright | User correction | n/a |
| `claude-code-my-workflow/master_supporting_docs/literature/papers/README.md` | "PDFs are NOT distributed" section rewritten as "PDFs are gitignored by default" | User correction | n/a |
| `~/.claude/projects/.../memory/feedback_no_copyright_claims.md` | New feedback memory | Persist user correction across future sessions | n/a |
| `~/.claude/projects/.../memory/MEMORY.md` | Index updated with new feedback entry | Memory hygiene | n/a |

## Design Decisions

| Decision | Alternatives Considered | Rationale |
|---|---|---|
| New MacDown rule = 4th rule, not a sub-bullet of rule 2 | Fold into rule 2 as a sub-rule | Distinct enough mechanism (whitespace-sensitivity vs delimiter-choice) to warrant equal billing; numbered rules are easier to cite |
| Hardlink vs symlink discovery for `claude-config` was a red herring | (none) | The config dirs are *directory-level symlinks*, not per-file hardlinks — my initial audit script was buggy (`[ -L ]` doesn't catch files inside symlinked dirs). The setup is fine as documented. |
| Replace Dropbox-symlink with LFS + DVC + periodic backup | (a) Dropbox-symlink as planned, (b) periodic backup only (no version control), (c) bidirectional rsync | Symlink approach has shared-storage blast-radius risks (`rm -rf` propagates) and no version control; periodic-backup-only doesn't solve the "what was the data in 2026" problem. LFS+DVC gives real version control with a clean separation between code (git) and bulk content (LFS server / DVC remote). |
| LFS for paper PDFs, DVC for data, periodic backup for ephemeral | LFS for everything; DVC for everything | Different access patterns: PDFs are read-mostly small-medium files where LFS's invisibility is the killer feature; data evolves over years and benefits from DVC's branch-and-checkout semantics. Don't conflate the two. |
| Skip `git lfs migrate import` (D3) | Run migrate to retroactively pull old PDFs into LFS | Rewrites history → coauthor disruption. Fresh-start is reversible later if specific repo bloats; keeping pre-existing committed PDFs in normal history is a small cost. |
| Drop the public/private repo distinction (D5 reframed) | Keep visibility-based LFS-eligibility policy | User corrected the copyright premise; per-repo opt-in based on whether PDFs are load-bearing is the cleaner policy. |
| New session log for today, not append to most-recent | Append to `2026-04-30_aea-citation-and-hook-hardening.md` per the strict reading of the Stop hook reminder | Today's three threads are distinct from April 30 work; a new dated log is much clearer organizationally. The Stop hook fires on session_logs/ touch generally. |

## Incremental Work Log

**13:00 UTC:** User flagged a new MacDown bug — spaces inside `$...$` delimiters cause math not to render. Pointed at `belief_distortion_discrimination/.../2026-05-01_analysis-upgrade-memo.md` as evidence.

**13:05 UTC:** Added rule 4 to `markdown-macdown-compat.md` (canonical at `claude-config/rules/`; hardlinked into `~/.claude/rules/`). Committed to claude-config as `ae79b9a`.

**13:15 UTC:** Confirmed user wanted the example file fixed too. Identified 7 actual broken spans (the original 16 grep-matched lines included false positives where space was *outside* delimiters). Edited each via Edit tool calls. Verified with tightened regex — clean.

**13:30 UTC:** Got off-track auditing `~/.claude/{rules,skills,commands}` for symlink-vs-hardlink-vs-copy state. Initial audit script was wrong (didn't account for directory-level symlinks). Eventually realized: dirs are symlinked to `claude-config/` as documented; `settings.json` is a copy and has drifted ~50 days. Tabled `settings.json` drift for later.

**13:45 UTC:** User redirected: was actually referring to `quality_reports/plans/2026-05-01_dropbox-symlink-setup-explainer.md` for a *different* symlink plan — Dropbox-symlinking gitignored bulk content into research repos.

**14:00 UTC:** Discussed: symlink approach is more trouble than it's worth (shared-storage blast radius from `rm -rf`, hook entanglement, no real version control). User pivoted to "periodic sync via script" idea.

**14:15 UTC:** Pushed back gently — periodic sync is fine for backup but doesn't solve the "what was the data in 2026" problem for long-running projects. Proposed three-tier architecture: git for code, Git LFS for paper PDFs (load-bearing binary), DVC for data (PII-safe with private remote, real version control).

**14:30 UTC:** User asked for explanations of Git LFS and DVC. Wrote `2026-05-05_lfs-vs-dvc-explainer.md` (concept primer with side-by-side comparison and per-content-class recommendations).

**14:50 UTC:** User: "lets actually write down a detailed and concrete plan for this before running anything. this will supercede the dropbox symlink plan." Investigated current `.gitignore`, repo visibility, and existing universal-gitignore plan to ground the migration design.

**15:30 UTC:** Wrote `2026-05-05_lfs-dvc-migration-plan.md` (14 sections, 530 lines): architecture, settled decisions, copyright section, pilot phase, workflow-template changes, bulk migration, coauthor coordination, rollback, cost monitoring, timeline, open [USER] questions.

**15:45 UTC:** Performed plan-lifecycle bookkeeping: marked symlink explainer "Superseded by..."; `git mv` to `archive/`; updated `INDEX.md`.

**16:00 UTC:** User correction: "forget about copyright - that was a wrong claim... papers are covered under fair use, and authors will happily share or publicly post their paper pdfs. so basically forget about copyright and strip mentions of it from the workflow."

**16:05 UTC:** Saved feedback memory `feedback_no_copyright_claims.md` (rule + Why + How to apply per memory format). Updated MEMORY.md index.

**16:10 UTC:** Grepped workflow for `copyright|fair use`. Found 5 hits across 5 files. Decided which to strip (live `.gitignore`, `papers/README.md`, the migration plan) and which to leave (LICENSE-related mentions about software licensing of the workflow fork — different concept).

**16:25 UTC:** Stripped copyright reasoning from migration plan: D5 reframed as per-repo opt-in (no public/private distinction); §4 fully rewritten ("Per-repo LFS opt-in" instead of "The copyright question"); §1.1, §3 D2, §7.1, §8.1, §13 cleaned up. Reduced [USER] decisions from 3 to 2.

**16:35 UTC:** Verified strip is clean — final grep shows no remaining "copyright" or "fair use" mentions in active workflow content (excluding LICENSE-related, which is intentional).

## Learnings & Corrections

- **[LEARN:rules]** MacDown's MathJax requires non-space immediately inside `$...$` delimiters; this is rule 4 in `markdown-macdown-compat.md`. Common offender: math-by-prose contexts where author hand-typed `$ \mathbb{E}[...] $` with internal spacing.
- **[LEARN:audit]** When auditing `~/.claude/{rules,skills,commands}` for symlink/hardlink/copy state, use `[ -L $dir ]` on the *directory* — the dirs are symlinked, not the per-file contents. Files inside report no symlink status (correctly) but share inodes with the target dir. Don't structure the audit per-file.
- **[LEARN:storage]** LFS and DVC are not interchangeable. LFS = "git for big files" (filesystem-transparent, designed for binary deliverables); DVC = "git for data" (separate CLI, designed for evolving datasets with explicit version checkouts). Use both, for their respective content classes.
- **[LEARN:rule-strip]** When the user corrects a load-bearing premise that's been used to justify a workflow rule, strip the reasoning from active content but leave session-log historical record alone (append-only). Distinguish concept domains (paper-PDF copyright vs software-LICENSE copyright) — strip the former without touching the latter.

## Verification Results

| Check | Result | Status |
|---|---|---|
| MacDown rule 4 added with correct/broken examples | Yes; both files in sync via hardlink | PASS |
| 7 broken spans in analysis-upgrade-memo all fixed | `grep` after edits returns clean | PASS |
| Dropbox-symlink plan archived with status updated | `ls archive/` shows file; header updated | PASS |
| LFS+DVC plan + explainer files created | Both at `quality_reports/plans/2026-05-05_*.md` | PASS |
| INDEX.md reflects new plans + archived plan | Read confirms updates | PASS |
| Workflow-wide copyright strip complete | Final grep clean (excluding intentional LICENSE-related lines) | PASS |
| Feedback memory persisted with rule + Why + How to apply | Both files written | PASS |
| MEMORY.md index updated | Read confirms entry | PASS |

## Open Questions / Blockers

- [ ] **D3 (LFS migration plan)** — User approval needed: skip `git lfs migrate import`? Plan recommends yes (no history rewrite, fresh-start).
- [ ] **D8 (LFS migration plan)** — User approval needed: per-repo coauthor list for migration notification (especially `tx_peer_effects_paper`).
- [ ] **`~/.claude/settings.json` drift** — `~/.claude/settings.json` is 193 bytes (May 4); `claude-config/settings.json` is 81 bytes (March 16). They've diverged ~50 days. Per the sync-global-config rule, the live file should be copied to the repo and committed. Tabled today; flag for next session.
- [ ] **claude-config commit hygiene** — today's MacDown rule 4 update was committed (`ae79b9a`). The `claude-code-my-workflow` repo has uncommitted changes (gitignore + papers/README + new plans + INDEX + archived plan). User asked at the end of the migration-plan write whether to commit; the conversation continued before that decision was made.

## Next Steps

- [ ] User reviews migration plan; decides D3 + D8.
- [ ] User decides whether to commit today's `claude-code-my-workflow` changes (or hold for further iteration).
- [ ] Sync `~/.claude/settings.json` ↔ `claude-config/settings.json` (separate small task).
- [ ] After plan approval: §7 (workflow-template updates) before §6 (pilot in `belief_distortion_discrimination`).

---

# Continued — 2026-05-06

## Day 2 status

- Phase 1 (§7 workflow-template updates) **done** on `main` — 4 commits.
- Phase 2 (§6 pilot in `belief_distortion_discrimination`) **paused mid-flight** — 2 BDD commits landed locally, 3 more queued, no pushes yet. User actively running their own analysis tasks in BDD.
- Side-tracks: behavioral-branch worktree spun up for parallel feature work; context-monitor proxy mismatch diagnosed and a token-based v2 design proposed.

## Day 2 changes (committed)

`claude-code-my-workflow` (`main`):

| SHA | Title |
|---|---|
| `9cbbdac` | templates: LFS gitattributes + setup-machine.sh + data doc templates (5 files) |
| `c48096a` | rules: data-version-control — three-tier storage architecture |
| `ad63028` | skills: add /tools sync-status — LFS + DVC + backup state report |
| `6910e84` | docs: CLAUDE.md gets bulk-content storage section; plan records D3/D8 resolved |

`belief_distortion_discrimination` (`main`, **unpushed**):

| SHA | Title |
|---|---|
| `ec8d2e8` | chore: enable Git LFS for paper PDFs |
| `c2c41f0` | chore: initialize DVC; remote = Dropbox |

Working tree in BDD has uncommitted: `data_local.dvc` (DVC pointer), `.gitignore` (DVC's `/data_local` line), 60 PDFs showing modified (LFS smudge filter — bytes unchanged on disk).

## Day 2 design decisions

| Decision | Rationale |
|---|---|
| Skip `git lfs migrate import` (D3 resolved) | User confirmed; no history rewrite needed, no force-push risk |
| No coauthor coordination (D8 resolved) | User confirmed: no active coauthors in any in-scope repo |
| **Soft-migrate** the 60 already-committed PDFs to LFS pointers | After `git lfs track`, working-tree PDFs show as forever-modified; soft-migrate (`git add --renormalize`) makes the next commit go forward with LFS pointers while leaving history untouched. Consistent with D3's letter (no `migrate import`, no force-push) and avoids the dirty-status footgun. |
| BDD as the LFS+DVC pilot, with `data_local/` as the DVC scope (not `data/`) | BDD's data convention is `data_local/`; the rule and templates assume `data/` but the per-project path adjusts cleanly. |
| Parallel worktree for behavioral branch at `~/github_repos/claude-code-my-workflow-behavioral` | User wanted to work on behavioral features while waiting; worktree shares `.git/objects/`, isolates working tree. Branch is at `576c1f0`, 4 commits behind today's `main`. Plan: bake on main, merge to behavioral once stable. |
| Token-based context-monitor v2 (hybrid: cheap proxy on every fire, real check when nearing threshold) | Current MAX_TOOL_CALLS=1000 proxy mis-fires for read-heavy projects: BDD at 84% real context but hook thinks 31.5%. Real solution: parse `message.usage` from the active session transcript (each assistant message has `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`, sum is the real context size). Hybrid keeps performance while gaining accuracy. |

## Day 2 incremental log

**13:00 UTC:** Started Phase 1 (§7 workflow-template updates) on `main`. Five new template files (gitattributes-lfs, setup-machine.sh, three data doc templates), then a new ~250-line rule `.claude/rules/data-version-control.md`, then `/tools sync-status` subcommand in the existing tools SKILL.md, then a "Bulk Content Storage" section in CLAUDE.md template. 4 commits. Pre-existing primary-source-first hook caught a false positive on the bracketed-year syntax `[Resolved 2026-05-05]`; resolved with a `<!-- primary-source-ok: resolved_2026 -->` comment.

**18:00 UTC:** User confirmed D3 and D8. D5 (public/private LFS policy) had collapsed earlier when copyright was stripped from the workflow.

**19:00 UTC:** Phase 2 pre-flight in BDD: confirmed git-lfs installed, dvc not yet → installed via `brew install dvc`. Backup repo to `~/backups/...20260506` (3.1 GB). Tag `pre-lfs-dvc-migration-2026-05-06`.

**19:30 UTC:** Discovery: BDD already had 60 PDFs tracked in plain git (no PDF-gitignore line, unlike workflow template). `.git/` at 481 MB, partially due to that. Surfaced to user: literal D3 ("do nothing") leaves git status forever-dirty due to the LFS smudge filter; soft-migrate (renormalize) is the cleaner reading. User approved soft-migrate.

**20:00 UTC:** Ran `git lfs track` + commit `.gitattributes` (`ec8d2e8`). Ran `dvc init` + remote config to Dropbox path + commit (`c2c41f0`). Ran `dvc add data_local/` — 1.1 GB hashed into `.dvc/cache/` in 4 seconds; created `data_local.dvc` pointer (uncommitted).

**21:00 UTC:** User said "wait up, I am running tasks in BDD rn." Paused mid-pilot. Surfaced uncommitted state to user with warnings against `git add .`. Tracker shows tasks #5-#8 ready; #9-#12 blocked on user go-ahead.

**21:30 UTC:** User asked for a parallel worktree for the behavioral branch. Created `git worktree add ~/github_repos/claude-code-my-workflow-behavioral behavioral`. Strategy: bake on main, merge to behavioral once features are proven through pilot.

**22:00 UTC:** Set up TaskCreate-backed live status tracker (12 tasks) replacing informal status reports.

**22:30 UTC:** User noted BDD session at 840.9k tokens with no context warnings. Investigated: hook uses `MAX_TOOL_CALLS=1000` proxy. BDD has 315 tool calls = 31.5% by proxy but ~84% real context (verified by parsing transcript JSONL `message.usage` blocks). Designed token-based v2 of context-monitor with hybrid throttling. Implementation pending user approval.

## Day 2 verification

| Check | Result |
|---|---|
| Phase 1 commits land cleanly on `main` | PASS — 4 commits, no test failures, no hook regressions |
| `data-version-control.md` rule file written and committed | PASS — 314 lines, cross-references intact |
| `/tools sync-status` SKILL.md update + frontmatter description sync | PASS |
| BDD backup created and tagged | PASS — `~/backups/...20260506` (3.1 GB), tag visible in `git tag --list` |
| BDD LFS enabled with `.gitattributes` LFS patterns | PASS — `git lfs env` shows endpoint resolved |
| BDD DVC initialized with Dropbox remote configured | PASS — `dvc remote list` shows correct path |
| `dvc add data_local/` creates pointer + caches data | PASS — `data_local.dvc` 114 bytes; `.dvc/cache/` populated |
| Worktree created at sibling path on behavioral branch | PASS — `git worktree list` shows both checkouts |
| Token-count parser finds correct usage block in BDD transcript | PASS — parsed `message.usage` matches user's reported 840.9k figure |

## Day 2 open questions / blockers

- [ ] **BDD pilot paused** — user actively running tasks in BDD. Resume on user's "resume" signal. Tracker tasks #5-#11 pending; #12 (7-day pilot run) follows validation.
- [ ] **Soft-migrate consequences for next push** — when push eventually fires, ~120 MB of LFS blobs upload to GitHub (60 PDFs × ~2 MB). Within free tier (1 GB) but worth noting.
- [ ] **Token-based context-monitor v2** — design proposed, awaiting user go-ahead on implementation. Would replace the current proxy-based heuristic with a transcript-parsed accurate reading.
- [ ] **`Resolved` false positive in primary-source-first** — bracketed-year text `[Resolved 2026]` triggered the citation regex. Hit twice today. Worth adding `Resolved` (and similar status markers like `Pending`, `Deferred`, `Open`) to the `NEVER_SURNAMES` blocklist. Small follow-up.
- [ ] **Overlay-branch sync** for §7 workflow-template changes — applied-micro and behavioral branches still need today's main-branch updates. Per user's plan, they'll cherry-pick / merge once features bake. Not blocking.
- [ ] **Math-span fix in BDD `analysis-upgrade-memo`** appears already committed in BDD's history (commit `699db4f` mentions MacDown delimiters). Worked-tree clean. No action needed unless our intra-session edits got lost — verify via diff against pre-migration tag.

## Day 2 next steps

- [ ] Wait for user "resume" → execute tasks #5-#8 (soft-migrate + DVC pointer commit + data doc contract + checkpoint).
- [ ] After user explicit "go" at #8: tasks #9 + #10 (`git push` + `dvc push`).
- [ ] Then #11 validation (LFS state + DVC state + hook compatibility checks).
- [ ] Then 7-day pilot run (#12) with metric tracking per §6.6 of the migration plan.
- [ ] If user approves token-based context-monitor v2: implement (~120 lines, hybrid design); commit on main.
