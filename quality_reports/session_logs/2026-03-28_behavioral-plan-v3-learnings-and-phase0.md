# Session Log: Behavioral Plan v3 Learnings Integration + Phase 0 Setup

**Date:** 2026-03-28
**Branch:** `behavioral` (created this session)
**Duration:** Full session

---

## Goals

1. Update behavioral plan v3 with findings from 11+ papers (3 learnings docs)
2. Review the updated plan for gaps and inconsistencies
3. Create `/pdf-learnings` global skill for token-efficient PDF reading
4. Begin Phase 0 implementation: create behavioral branch and layer infrastructure

---

## What Was Done

### 1. Learnings Integration into Plan v3

Incorporated findings from three learnings documents into `quality_reports/plans/2026-03-28_behavioral-plan-v3-hugo-base.md`:

- **Inference-first checklist expanded from 12 to 14 steps:**
  - Step 3: Moffatt Stata test selection guide + clustering (size 0.46 without)
  - Step 5: Niederle's 5 alternative-hypothesis controls + background noise sources
  - Step 6: Chapman & Fisher preference elicitation table, MPL pitfalls, Healy & Leo belief elicitation decision tree, IC hierarchy, measurement error 30-50%, ORIV, false positives with noisy covariates
  - New Step 7: Process Measurement (always collect RT — Brocas et al.)
  - Step 8: Incentive design enriched (Gneezy & Rustichini, random round payment, repeated games)
  - Step 9: Survey attention checks, manipulation checks, never drop post-treatment
  - Step 10: Effect persistence decay 1/3-1/2 within 1-4 weeks
  - Step 11: List et al. power formulas, optimal allocation, Lin (2013) covariate adjustment
  - Step 12: Differential attrition planning
  - New Step 13: Parameter Selection (Snowberg & Yariv 4-objective framework)
  - Step 14: Coffman & Dreber 7-item PAP, design-hacking warning, Registered Reports, replication package

- **Experiment design principles rule expanded from 10 to 13 principles:**
  - 11: Always collect RT
  - 12: Measurement error awareness
  - 13: Parameter selection discipline

- **10 agent descriptions enriched** with paper-specific knowledge and reference file pointers

- **6 skill descriptions updated** with framework references

- **3 existing learnings docs wired** as agent-readable references

### 2. Three-Agent Review

Launched 3 parallel agents to cross-check plan vs each learnings doc. Results:
- Most content was well-integrated from the first pass
- Fixed: 17-item → 16-item theorist-critic checklist count
- Added: Registered Reports, effect persistence decay, false positives with noisy covariates, Rubinstein's 4 dilemmas in /challenge --theory, footnote constraint, theory figure standards
- Lowercase folder paths updated throughout

### 3. `/pdf-learnings` Global Skill Created

New skill in `~/github_repos/claude-config/skills/pdf-learnings/`:
- Reads PDFs in 10-15 page batches using native Read tool
- Writes findings to disk after every batch (token-efficient)
- Supports `--focus`, `--pages`, `--output` flags
- For >60 page PDFs, spawns parallel subagents
- Committed and pushed to claude-config repo

### 4. Phase 0: Behavioral Branch Setup

**Created `behavioral` branch** from `hugosantanna/main` (Hugo's clo-author v3.1.1):
- Hugo provides: 10 skills, 18 agents, 8 rules, 4 hooks
- Pushed to `origin/behavioral`

**Layered Pedro's infrastructure:**
- 4 additional hooks: context-monitor, log-reminder, verify-reminder, notify
- 4 utility skills: /commit, /deep-audit, /context-status, /learn
- 3 workflow rules: plan-first-workflow, session-logging, orchestrator-protocol
- Templates: session-log, quality-report, requirements-spec, skill-template
- Paper learnings docs (3) + behavioral plan v3
- Updated settings.json: registered all hooks, removed Hugo's local paths

---

## Commits (3 on main, 1 on behavioral)

| Branch | Commit | Description |
|--------|--------|-------------|
| main | `0131495` | docs: integrate paper learnings into behavioral plan v3 |
| main | `45613d5` | docs: fix review gaps in behavioral plan v3 |
| main | `48c970e` | docs: lowercase folder paths in behavioral plan v3 |
| behavioral | `ed66f3b` | feat: layer Pedro's infrastructure onto Hugo's clo-author base |

---

## Remaining Phase 0 Tasks

- [ ] **Task #7:** Create `/challenge` skill with behavioral modes (`--design`, `--theory`, `--paper`, `--fresh`) — plan Section 10 has full spec
- [ ] **Task #8:** Update CLAUDE.md for behavioral workflow + verify folder structure matches plan Section 12

## Next: Phase 1

After Phase 0 completes:
- Create `experiment-design-principles.md` rule (~90 lines, 13 principles)
- Create `stata-code-conventions.md` rule (~60 lines)
- Create `python-code-conventions.md` rule (~30 lines)
- Adapt Hugo's rules: quality.md (scoring weights), workflow.md (dependency graph + /preregister gate), content-standards.md, working-paper-format.md (pdflatex), tables.md (estout), figures.md (Stata)
- Create `.claude/references/`: domain profile, journal profiles, inference-first checklist, seminal papers, replication standards
- Create templates: experiment-design-checklist, pre-registration-template, subject-instructions-template

---

## Key Decisions

1. **Clean start from Hugo** — behavioral branch based on Hugo's main, not a merge into our main. Pedro's components cherry-picked on top.
2. **Learnings stay in `quality_reports/paper_learnings/`** — agents read them as reference files, not duplicated into `.claude/references/`
3. **Lowercase folder convention** — all project folders lowercase except CLAUDE.md, MEMORY.md, WORKFLOW_QUICK_REF.md
4. **Settings.json protected by hook** — must edit via shell, not Edit tool
