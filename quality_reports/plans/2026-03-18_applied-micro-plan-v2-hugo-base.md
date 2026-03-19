# Applied Micro Workflow Plan v2: Hugo Base + Pedro Infrastructure

**Status:** APPROVED — Phases 0-1 complete, Phase 2 next
**Date:** 2026-03-18
**Supersedes:** The applied micro section of `2026-03-18_consolidated-decisions-and-applied-micro-plan.md`
**Key change:** Start from Hugo's clo-author (paper-centric) instead of building up from Pedro's template (slide-centric)

---

## Rationale for Pivot

The previous approach layered paper workflow onto Pedro's slide template. This caused:
- Too many always-on rules (1,500+ lines)
- TX-specific details bleeding into the general template
- Rebuilding things Hugo already has (worker-critic pairs, journal profiles, strategist agents)

**New approach:** Hugo's clo-author IS the applied micro base. We add Pedro's infrastructure on top.

---

## What Hugo Already Has (Use As-Is or Adapt Lightly)

### Skills (11)
| Hugo Skill | What It Does | Action |
|------------|-------------|--------|
| `/discover` | Interview + lit review + ideation (3 modes) | **Keep** |
| `/strategize` | Design identification strategy + robustness plan | **Keep** — this IS our `/identify` |
| `/analyze` | End-to-end data analysis | **Adapt** for Stata primary |
| `/write` | Paper section drafting with anti-hedging | **Keep** |
| `/review` | Journal-calibrated peer review (domain + methods) | **Keep** |
| `/revise` | Address referee comments | **Keep** |
| `/submit` | Target journal, package, audit, final check | **Keep** |
| `/talk` | Paper → Beamer talk (4 formats) | **Keep** |
| `/tools` | Utility subcommands | **Keep** |
| `/archive` | Archive completed work | **Keep** |
| `/new-project` | Full orchestrated project setup | **Keep** |

### Agents (16 — full worker-critic system)
| Agent | Role | Action |
|-------|------|--------|
| librarian + librarian-critic | Literature search + coverage review | **Keep** |
| explorer + explorer-critic | Data assessment + data quality review | **Keep** |
| strategist + strategist-critic | Identification design + 4-phase audit | **Keep** |
| coder + coder-critic | Analysis code + reproducibility review | **Adapt** for Stata |
| storyteller + storyteller-critic | Paper→talk + talk review | **Keep** |
| writer + writer-critic | Paper drafting + clarity review | **Keep** |
| data-engineer | Raw → cleaned data | **Adapt** for Stata |
| domain-referee | Journal-calibrated subject review | **Keep** |
| methods-referee | Identification/inference review | **Keep** |
| orchestrator | Pipeline coordinator | **Keep** |
| verifier | Compilation + replication check | **Adapt** for pdflatex + Stata |

### Rules (12)
| Hugo Rule | Lines | Action |
|-----------|-------|--------|
| `workflow.md` | ~80 | **Keep** — plan-first + orchestrator |
| `agents.md` | ~60 | **Keep** — worker-critic protocol |
| `quality.md` | ~70 | **Keep** — weighted scoring |
| `logging.md` | ~25 | **Keep** — session logging |
| `domain-profile.md` | ~80 | **Replace** with applied micro profile |
| `journal-profiles.md` | ~170 | **Move to reference file** (not always-on) |
| `content-standards.md` | ~50 | **Keep** — adapt for Stata output |
| `working-paper-format.md` | ~60 | **Keep** — adapt for pdflatex |
| `tables.md` | ~40 | **Keep** — adapt for estout/texsave |
| `figures.md` | ~30 | **Keep** — adapt for Stata graphs |
| `meta-governance.md` | ~250 | **Replace** with Pedro's (better) |
| `revision.md` | ~40 | **Keep** |

---

## What Pedro Adds (Layer On Top)

| Pedro Component | Why Hugo Needs It | Action |
|-----------------|-------------------|--------|
| Pre-compact hook | Saves context before auto-compression | **Add** |
| Post-compact restore hook | Recovers after compression | **Add** |
| Context monitor hook | Tracks context usage | **Add** |
| Log reminder hook | Proactive logging nudge | **Add** |
| Protect-files hook | Prevents accidental overwrites | **Add** |
| Verify reminder hook | Nudges verification after changes | **Add** |
| `/deep-audit` skill | Repository-wide consistency check | **Add** |
| `/context-status` skill | Session health monitoring | **Add** |
| `/learn` skill | Extract discovery into persistent skill | **Add** |
| `/commit` skill | Stage, PR, merge workflow | **Add** (Hugo has none) |
| Exploration folder protocol | `explorations/` sandbox with archive | **Add** |
| Requirements spec template | MUST/SHOULD/MAY + clarity status | **Add** |
| `/devils-advocate` → `/challenge` | Standalone invocable challenge | **Add** as new skill |
| TikZ infrastructure | tikz-reviewer agent + visual quality rule | **Add** |

---

## What We Add (Applied Micro Specific)

### New Rules (keep them SHORT — reference files for detail)
| Rule | Lines Target | Content |
|------|-------------|---------|
| `stata-conventions.md` | ~60 | Stata 18, settings.do pattern, .doh files, key packages. Trim current 125-line version. |
| `air-gapped-workflow.md` | ~40 | When Claude can't see data. Trim current 74-line version. |

### New Reference Files (NOT always-on — read by agents on demand)
| File | Content |
|------|---------|
| `.claude/references/journal-profiles-applied-micro.md` | Hugo's profiles + education/immigration journals |
| `.claude/references/domain-profile-applied-micro.md` | Peer effects, education, immigration lit, notation, referee concerns |
| `.claude/references/identification-checklists.md` | DiD, IV, RDD, SC, FE checklists (from strategist-critic) |
| `.claude/references/replication-standards.md` | AEA Data Editor requirements |

### New Skills
| Skill | What It Does |
|-------|-------------|
| `/challenge` | Devil's advocate with modes: `--paper`, `--identification`, `--fresh` |
| `/balance` | Generate balance tables |
| `/event-study` | Generate event study plots |

### Adapted Agents
| Agent | Adaptation |
|-------|-----------|
| coder | Add Stata as primary language (reghdfe, ivreghdfe, estout patterns) |
| coder-critic | Add Stata package checks alongside R |
| data-engineer | Add Stata cleaning patterns, .doh conventions |
| strategist-critic | Add Stata package equivalents (currently R-only) |
| verifier | pdflatex instead of xelatex, Stata script checks |

---

## Always-On Rule Budget ✅ IMPLEMENTED

**Actual: 964 lines** (target was <500, but Hugo's workflow.md and working-paper-format.md are larger than estimated — acceptable for now, can trim later)

| Rule | Actual Lines | Source |
|------|-------------|--------|
| `workflow.md` | 262 | Hugo |
| `working-paper-format.md` | 131 | Hugo |
| `logging.md` | 123 | Hugo |
| `agents.md` | 111 | Hugo |
| `quality.md` | 88 | Hugo |
| `tikz-visual-quality.md` | 56 | Pedro |
| `stata-conventions.md` | 43 | New |
| `exploration-folder-protocol.md` | 42 | Pedro |
| `revision.md` | 40 | Hugo |
| `air-gapped-workflow.md` | 28 | New |
| `exploration-fast-track.md` | 20 | Pedro |
| `figures.md` | 10 | Hugo |
| `tables.md` | 10 | Hugo |
| **Total** | **964** | **Down from 1,697** |

**Moved to `.claude/references/`** (read by agents on demand):
- `journal-profiles.md` (149 lines) — Hugo's 20+ journal profiles
- `domain-profile-applied-micro.md` (57 lines) — applied micro field profile
- `domain-profile.md` (100 lines) — Hugo's generic template
- `content-standards.md` (304 lines) — writing/output standards
- `meta-governance.md` (251 lines) — template vs project separation

All agent/skill references updated to `.claude/references/` paths (11 files fixed).

---

## Implementation Plan (Revised)

### Phase 0: Setup ✅ COMPLETE
- [x] `applied-micro` branch created fresh from main (commit 396dc4e)
- [x] TX repos set up: `tx_peer_effects_paper` (Overleaf-synced), `tx_peer_effects_local` (renamed)
- [x] Merged Hugo's clo-author into applied-micro branch (git checkout hugosantanna/main)
- [x] Layered Pedro's hooks (7), skills (7), rules (3), agent (tikz-reviewer)
- [x] Committed: 56e149b — 128 files, 18 skills, 18 agents, 15 rules, 7 hooks
- [ ] Add `/challenge` skill (upgraded devils-advocate) — DEFERRED to Phase 3

### Phase 1: Adapt for Applied Micro ✅ COMPLETE
- [x] Moved 4 heavy rules to `.claude/references/` (journal-profiles, domain-profile, content-standards, meta-governance)
- [x] Created `domain-profile-applied-micro.md` as reference file
- [x] Created `stata-conventions.md` (43 lines, always-on)
- [x] Created `air-gapped-workflow.md` (28 lines, always-on)
- [x] Adapted 5 agents for Stata: coder, coder-critic, data-engineer, strategist-critic, verifier
- [x] Updated CLAUDE.md template (pdflatex, Stata primary)
- [x] Fixed all agent/skill path references (11 files) — committed: 7273dd1, da17ba7

### Phase 2: Complete Template Setup ✅ COMPLETE

**Reference files:**
- [x] `journal-profiles-applied-micro.md` — Hugo's profiles + education/immigration journals (171 lines)
- [x] `identification-checklists.md` — standalone DiD/IV/RDD/SC/FE/event study checklists (88 lines)
- [x] `replication-standards.md` — AEA Data Editor requirements (73 lines)

**New skills:**
- [x] `/challenge` — devil's advocate (--paper, --identification, --fresh)
- [x] `/balance` — balance table generator (Stata/R, air-gapped aware)
- [x] `/event-study` — event study plots (classic + staggered DiD)

**Compilation:**
- [x] `/compile-latex` adapted for pdflatex (auto-detects paper vs talk mode)
- [x] `/talk` skill (Hugo's, uses `/compile-latex` internally — works with pdflatex)

**Template cleanup:**
- [x] CLAUDE.md verified clean (no TX-specific content), skills table updated
- [x] All agent/skill references point to `.claude/references/`
- [ ] Run `/deep-audit` on template — DEFERRED (needs full project context to be meaningful)

### Phase 3: Deploy to TX Project ✅ COMPLETE
- [x] Cleaned old pre-pivot `.claude/` from TX repo
- [x] Copied fresh template (21 skills, 18 agents, 13 rules, 8 references, 7 hooks, 7 templates)
- [x] Wrote lean TX-specific CLAUDE.md (project details only — 95 lines)
- [x] Committed to TX repo: 7c84c68
- [ ] Test `/review --peer` on TX paper — ready to test
- [ ] Test `/review --proofread` on TX paper — ready to test
- [ ] Test `/strategize` on TX identification strategy — ready to test
- [ ] Test `/challenge` on TX paper — ready to test
- [ ] Test `/analyze` code review on exported .do files — blocked on FERPA
- [ ] Iterate based on output quality

### Phase 4: Beamer/Slides Adaptation (Later — Not Urgent)
- [ ] Adapt Pedro's slide agents for applied micro presentations
- [ ] Copy slide-related skills: `/proofread`, `/visual-audit`, `/slide-excellence`
- [ ] Copy slide agents: slide-auditor, pedagogy-reviewer
- [ ] Retain all TikZ infrastructure (already in place)

---

## Key Differences from Previous Plan

| Aspect | Previous Plan | This Plan |
|--------|--------------|-----------|
| Base | Pedro's slide template | Hugo's clo-author |
| Agents | Build from scratch (9 planned) | Hugo has 16 already — adapt 5 |
| Skills | Build from scratch (10+ planned) | Hugo has 11 already — adapt 2, add 3 |
| Rules | 1,500 lines always-on | ~535 lines always-on + reference files |
| Strategist | New identification-strategy rule | Hugo's strategist + strategist-critic agents (+ rule) |
| Journal review | New journal-profiles rule | Hugo's domain-referee + methods-referee + profiles |
| Scope | TX-specific | General applied micro (TX config in CLAUDE.md only) |

---

## Running To-Do List

### Must-Do (Template)
- [x] Merge Hugo's clo-author into applied-micro branch
- [x] Adapt agents/skills for Stata and pdflatex
- [x] Move heavy rules to references, fix all paths
- [x] Complete Phase 2 (reference files, new skills, compilation)
- [ ] Run `/deep-audit` on template before deploying to projects

### Must-Do (TX Project — after template is complete)
- [x] Copy template `.claude/` to TX repo
- [x] Write TX-specific CLAUDE.md
- [ ] Export .do files from TERC (BLOCKED on FERPA)
- [ ] Share swift raid Claude Chat memory/output (partially done — chat memory in consolidated plan)

### Should-Do
- [ ] Clarify Stata license type (SE vs MP)
- [ ] Share TX variable codebook / summary statistics
- [ ] Gather seminal papers for applied micro subfields (peer effects, education, immigration, labor)
- [ ] Review journal profiles after testing `/review --peer` on a real paper

---

**APPROVED** by Christina (2026-03-18). Phases 0-1 implemented same session.