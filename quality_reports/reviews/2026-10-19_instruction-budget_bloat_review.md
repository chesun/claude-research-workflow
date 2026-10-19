# Instruction Budget Review — bloat
**Date:** 2026-10-19
**Reviewer:** bloat critic (independent, general-purpose agent)
**Target:** .claude/rules/primary-source-first.md, .claude/rules/destructive-actions.md, .claude/rules/data-version-control.md
**Score:** 60/100
**Status:** Active

## Verdict

The always-loaded set measures **139,264 characters**: 121,355 in this repo (CLAUDE.md + 17 unscoped rules) and 17,909 in the owner's installed user-scope rules (out of scope here). The uncommitted change is sound and correctly aimed — path-scoping `data-version-control.md` (−14,134 from the always-loaded set) and extracting the primary-source filter stack (−8,8xx) and destructive-actions hook internals (−4,7xx) to `.claude/references/` — but it stopped early: both edited rules still carry large sections that meet the same move-to-reference test (the 6,145-char AEA citation-style guide in `primary-source-first.md`; ~4,400 of incident narrative, audit-log format and coverage caveats in `destructive-actions.md`). The deeper pattern the 2026-09-16 hook-pruning did not touch is that the big "stance" rules (`adversarial-default.md`, `workflow.md`, `quality.md`, `agents.md`) still inline operational tables that are duplicated verbatim in the agent files that actually use them (`orchestrator.md`, `writer-critic.md`, `coder-critic.md`, `storyteller-critic.md`) or that are needed only at specific moments (per-domain compliance checklists, ledger column specs, worked examples). Roughly **43,500 characters (~36% of the repo's always-loaded set)** can move to references, path scopes, agents or skills with a pointer left behind and no behavioural rule deleted.

## Always-loaded set (measured, `wc -m`, on-disk including uncommitted changes)

| File | Chars |
|---|---|
| .claude/rules/adversarial-default.md | 18,609 |
| .claude/rules/workflow.md | 12,718 |
| .claude/rules/primary-source-first.md | 12,004 |
| .claude/rules/agents.md | 11,168 |
| CLAUDE.md | 11,126 |
| .claude/rules/destructive-actions.md | 10,235 |
| .claude/rules/derive-dont-guess.md | 9,078 |
| .claude/rules/quality.md | 7,942 |
| .claude/rules/no-assumptions.md | 7,662 |
| .claude/rules/decision-log.md | 4,560 |
| .claude/rules/independent-review.md | 4,445 |
| .claude/rules/verification-protocol.md | 2,644 |
| .claude/rules/single-source-of-truth.md | 2,360 |
| .claude/rules/logging.md | 1,980 |
| .claude/rules/revision.md | 1,480 |
| .claude/rules/todo-tracking.md | 1,342 |
| .claude/rules/meta-governance.md | 1,110 |
| .claude/rules/output-length.md | 892 |
| **Repo subtotal** | **121,355** |
| ~/.claude/rules/analysis-folder.md (owner's installed rules, out of scope here) | 6,301 |
| ~/.claude/rules/citations.md (same) | 6,209 |
| ~/.claude/rules/exhibits.md (same) | 3,606 |
| ~/.claude/rules/ Python-environment rule (same) | 1,793 |
| **Grand total** | **139,264** |

Path-scoped (not counted, load on matching file touch): anti-ai-prose, data-version-control (uncommitted), exploration-fast-track, exploration-folder-protocol, figures, python-code-conventions, r-code-conventions, replication-protocol, stata-code-conventions, tables, tikz-visual-quality, working-paper-format — 65,990 chars correctly kept off the floor.

## Findings (ranked by characters saved)

| # | Sev | Finding | Evidence | Verdict | Recommendation (chars saved) |
|---|---|---|---|---|---|
| 1 | Critical | Per-domain compliance checklists (6 tables: Stata, R, Python, data, design, identification, replication, bibliography) load every session but are consulted only when a compliance check runs; the Stata/R/Python rows duplicate the already path-scoped convention rules | adversarial-default.md:51–144 (5,615 chars); duplicates e.g. stata-code-conventions.md / r-code-conventions.md (path-scoped) | SOUND | Move all checklist tables to `.claude/references/adversarial-checklists.md`; keep the one-line instruction "run the per-domain checklist in the reference before claiming compliance" (**~5,300**) |
| 2 | Critical | AEA/Chicago citation-style guide (in-text forms, parenthetical punctuation, full reference-list entry forms, corporate-author cases) is a writing convention used when drafting prose, not needed at session start; writer-critic enforces it via its own deduction rows | primary-source-first.md:77–133 (6,145 chars); primary-source-first.md:124–126 says writer-critic enforces AEA form; writer-critic.md:198–205 carries the deduction table | SOUND | Move §"Citation-style convention" to `.claude/references/aea-citation-style.md` (or into path-scoped working-paper-format.md), keep the 5-row in-text form table + pointer. Functionality preserved: the hooks' permissive parser (stated at :124) catches citations regardless of style; style is scored by writer-critic (**~4,500**) |
| 3 | High | Orchestrator loop + dependency graph duplicated: workflow.md §2–§3 restate the dependency/dispatch/escalation tables that orchestrator.md (loaded when the orchestrator is dispatched) already carries | workflow.md:84–207 (4,973 chars) vs .claude/agents/orchestrator.md:12–73 (dependency table, dispatch rules, three-strikes routing, loop) and agents.md:181–215 (escalation) | SOUND | Keep in workflow.md the two-sentence "plan approved → orchestrator takes over, max 3/5/2 rounds" summary + Simplified-Mode checklist (used outside the orchestrator); move the rest behind a pointer to orchestrator.md (**~4,000**) |
| 4 | High | Verification-ledger mechanics (column spec, example rows, SHA command, cost analysis, audit greps, diagnosis example table) needed only when reading/writing the ledger | adversarial-default.md:146–205 (6,843 chars incl. Diagnostic findings) | SOUND | Keep the 6-step lookup protocol, staleness triggers and the 3-step diagnosis protocol (~1,900); move format spec, example rows, cost analysis and audit greps to `.claude/references/` or a header comment in `.claude/state/verification-ledger.md` itself (**~3,400**) |
| 5 | High | destructive-actions.md still carries movable detail after the uncommitted extraction: incident narrative, audit-log JSONL format, subagent-coverage assumption, "what this rule does NOT cover" | destructive-actions.md:12–24 (1,075), :107–117 (1,414), :118–130 (~900), :131–138 (1,043) | SOUND | Append these to the already-created `.claude/references/destructive-actions-detail.md` (4,827 chars, has room); keep the blocked-command tables, bypass prefix, and the post-action verification protocol (behavioural, stays) plus a 2-line incident summary (**~3,600**) |
| 6 | High | Pre-generation derivation checklist table + three Bad/Good example pairs: the advisory hook enforces resolvability; the table is consulted at code-generation time, not session start | derive-dont-guess.md:44–63 (2,217), :76–106 (1,436) | SOUND | Move the lookup table and examples to `.claude/references/derive-lookup-table.md`; keep the principle, Enforcement, escape hatch and citation requirement (**~3,200**) |
| 7 | High | Per-target deduction tables in quality.md §3 duplicate the critic agents that apply them | quality.md:95–168 (3,390 chars) vs writer-critic.md:93,162–205; coder-critic.md:114,228–240; storyteller-critic.md:71–97 | SOUND | Keep §3's 4-line Enforcement block (commit/PR/submission actions); replace the tables with "each critic's deduction table lives in its agent file" (**~2,900**) |
| 8 | Medium | single-source-of-truth.md is only relevant when paper/talk/figure/table files are touched | single-source-of-truth.md:1–66 (whole file, 2,360) | SOUND | Path-scope with `paths: ["paper/**", "talks/**", "figures/**", "tables/**", "supplementary/**"]`. Pre-touch need: none found — /talk and storyteller-critic read the paper first, which triggers the load (**~2,360**) |
| 9 | Medium | Review/plan lifecycle (§2a: status values, supersession steps, archive cadence, INDEX format) duplicated in quality_reports/reviews/README.md (which agents.md itself cites as "the full lifecycle") and in each critic's instructions | agents.md:127–179 (2,678); agents.md:124 "See `quality_reports/reviews/README.md` for the full lifecycle"; writer-critic.md:148–152 carries the supersession steps | SOUND | Keep the blueprint-evidence-never-moved exception (behavioural, 4 lines) and a pointer; move the rest to reviews/README.md (**~2,000**) |
| 10 | Medium | CLAUDE.md restates path-scoped/retired material: Bulk Content Storage duplicates data-version-control.md (now path-scoped); Overlays section describes tooling retired 2026-10-14; Getting Started is one-time fork onboarding | CLAUDE.md:91–114 (1,349), :115–127 (783), :45–55 (489) | SOUND | Bulk storage → 2-line pointer to the rule; Overlays → 1 line + `.claude/file-classes.toml` pointer; Getting Started → move to README.md (**~2,100**) |
| 11 | Medium | Evidence-gating section restates tier/binding-boundary/M9/Phase-3 detail that both `.claude/references/evidence-gating-detail.md` (17,242 chars) and coder-critic.md:196–240 already hold | adversarial-default.md:18–41 (3,669) | SOUND | Compress to the one principle, verdict vocabulary line, gate-on-claims line, known-limit line + the existing reference pointer (~1,800 kept) (**~1,900**) |
| 12 | Medium | no-assumptions.md examples and 7-row "what counts" table are illustrations of a one-paragraph principle | no-assumptions.md:34–47 (1,504), :70–103 (1,262) | SOUND | Keep the canonical 4-rule mapping table (it is the cited original); trim the what-counts table to 3 rows and examples to one Bad/Good pair, rest to a reference (**~1,800**) |
| 13 | Low | Standalone-skills table in workflow.md §4 duplicates CLAUDE.md's Skills Quick Reference and the harness's own skill listing with descriptions | workflow.md:209–259 (2,178) vs CLAUDE.md:155–175 (1,357) | SOUND | Keep the Two-Modes explanation and the `/new-project`-always-orchestrated constraint; drop the table (CLAUDE.md copy stays) (**~1,500**) |
| 14 | Low | decision-log.md duplicates decisions/README.md, which it names as holding "template, sections, and full rules" | decision-log.md:20–48 (format, required fields, supersession detail); :22 "Template, sections, and full rules live in `decisions/README.md`" | SOUND | Keep when-to-write, append-only + supersession principle, enforcement; move field lists and format detail to decisions/README.md (**~1,200**) |
| 15 | Low | independent-review "Mechanism and its limits" is hook-implementation caveat detail, same class as what the uncommitted change moved out of destructive-actions.md | independent-review.md:§"Mechanism and its limits" (1,453) | SOUND | Keep the two load-bearing bullets (fires only via Claude Code; `REVIEW_WAIVE=1` is the escape, `--no-verify` is not); move fail-closed/heuristic detail to a reference (**~1,000**) |
| 16 | Low | revision.md duplicates the classification/routing table inside the revise skill, which is what actually runs the cycle | revision.md:5–45 vs .claude/skills/revise/SKILL.md:26–32 (classification + routing), :46–52 (DISAGREE protocol) | SOUND | Keep the behavioural line "DISAGREE items always flagged for user; Claude never autonomously pushes back on referees" + pointer to the skill; drop the flow diagram and table (**~1,000**) |
| 17 | Low | Six pruned-hook obituaries (narrating what `log-reminder.py` etc. did before 2026-09-16) are history, not instruction | adversarial-default.md:226; derive-dont-guess.md:16; logging.md:22; output-length.md:16; workflow.md:80,277 | SOUND | Compress each to "discipline, not a hook (hook pruned 2026-09-16)"; the full story is in git history and the modernize plan (**~900**) |
| 18 | Low | primary-source-first "Why this exists" incident narrative | primary-source-first.md:135–140 (1,269) | SOUND | Compress to two sentences; the enforcement sections carry the operative content (**~900**) |
| 19 | Low | Uncommitted change review: direction and mechanics are right — `paths:` globs on data-version-control.md are correct and complete for its triggers (`data/**`, `**/*.dvc`, `.dvc/**`, `.gitattributes`, templates, papers dir; no pre-touch need found — enabling LFS/DVC starts by editing `.gitignore`/`.gitattributes` or `data/`, which matches), and the two reference extractions keep pointers. Incomplete rather than wrong: findings 2, 5 and 18 are residue in the very files it edited | git diff: data-version-control.md:1–14 (frontmatter); primary-source-first.md:48–52; destructive-actions.md:50–52,75–77 | SOUND | Commit it, then apply findings 2, 5, 18 on top (0 additional; enabler) |
| 20 | Low | User-scope rules cost 17,909 chars in every session of this repo although three of the four self-gate to "AI gate: cwd gated: permitted" sessions, which this repo is not | ~/.claude/rules/analysis-folder.md:3, citations.md:3, exhibits.md:3 (6,301 + 6,209 + 3,606) | WEAK | **Owner's installed rules, out of scope here.** Noting only: if the gate mechanism supported path/condition scoping at user scope, ~16k would leave non-client sessions. Not actionable from this repo (0 counted) |

No finding recommends deleting a behavioural rule; every move leaves a pointer, a path scope, a hook, or an agent/skill that already carries the content.

## Projected total

| | Chars |
|---|---|
| Current repo always-loaded | 121,355 |
| Savings if findings 1–18 applied (sum of estimates) | −43,560 |
| **Projected repo always-loaded** | **~77,800** |
| User-scope rules (unchanged, out of scope) | +17,909 |
| **Projected grand total** | **~95,700** |

That is comfortably under the 150k limit with ~54k of headroom for project growth (reading notes citations, new ADR-driven rules), versus ~11k today.
