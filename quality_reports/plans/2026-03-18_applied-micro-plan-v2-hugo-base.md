# Applied Micro Workflow Plan v2: Hugo Base + Pedro Infrastructure

**Status:** DRAFT — awaiting Christina's approval
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

## Always-On Rule Budget

**Target: <500 lines of always-on rules**

| Rule | Est. Lines | Source |
|------|-----------|--------|
| `workflow.md` | 80 | Hugo |
| `agents.md` | 60 | Hugo |
| `quality.md` | 70 | Hugo |
| `logging.md` | 25 | Hugo |
| `content-standards.md` | 50 | Hugo (adapted) |
| `working-paper-format.md` | 40 | Hugo (trimmed) |
| `tables.md` | 40 | Hugo |
| `figures.md` | 30 | Hugo |
| `revision.md` | 40 | Hugo |
| `stata-conventions.md` | 60 | New (trimmed) |
| `air-gapped-workflow.md` | 40 | New (trimmed) |
| **Total** | **~535** | **Down from 1,500** |

Heavy reference content (journal profiles, domain profile, identification checklists, replication standards, meta-governance) moves to `.claude/references/` — read by agents on demand, not loaded every conversation.

---

## Implementation Plan (Revised)

### Phase 0: Setup ✅ MOSTLY DONE
- [x] `applied-micro` branch exists
- [x] TX repos set up (paper + local)
- [ ] **NEW: Merge Hugo's clo-author into `applied-micro` branch**
- [ ] Layer Pedro's hooks, `/commit`, `/deep-audit`, `/context-status`, `/learn`, exploration protocol
- [ ] Add TikZ infrastructure (tikz-reviewer, extract-tikz, visual quality)
- [ ] Add `/challenge` skill (upgraded devils-advocate)

### Phase 1: Adapt for Applied Micro
- [ ] Replace Hugo's `domain-profile.md` with applied micro version (as reference file)
- [ ] Create `journal-profiles-applied-micro.md` (as reference file, merging Hugo's profiles)
- [ ] Create `stata-conventions.md` (short, always-on rule)
- [ ] Create `air-gapped-workflow.md` (short, always-on rule)
- [ ] Create `.claude/references/` directory with heavy content
- [ ] Adapt coder + coder-critic agents for Stata primary
- [ ] Adapt data-engineer for Stata
- [ ] Adapt strategist-critic for Stata packages
- [ ] Adapt verifier for pdflatex + Stata
- [ ] Update CLAUDE.md template for applied micro

### Phase 2: Test with TX
- [ ] Copy adapted `.claude/` to TX repo
- [ ] Write TX-specific CLAUDE.md (project details only, not workflow rules)
- [ ] Test `/review --peer` on TX paper
- [ ] Test `/strategize` on TX identification strategy
- [ ] Test `/analyze` code review on exported .do files
- [ ] Iterate based on output quality

### Phase 3: Additional Skills (if needed)
- [ ] `/balance` skill
- [ ] `/event-study` skill
- [ ] Beamer/slides adaptation (from Pedro)

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

### Must-Do Before Implementation
- [ ] **Merge Hugo's clo-author into applied-micro branch** ← NEXT STEP
- [ ] Export .do files from TERC (BLOCKED on FERPA)
- [ ] Share swift raid Claude Chat memory/output

### Should-Do
- [ ] Export QSF from existing Qualtrics survey (behavioral workflow)
- [ ] Share custom Beamer templates
- [ ] Clarify Stata license type (SE vs MP)
- [ ] Share TX variable codebook / summary statistics

### Nice-to-Have
- [ ] Gather seminal papers by subfield
- [ ] Set up Overleaf git sync for BDM and JMP
- [ ] Consolidate JMP satellite repos
- [ ] Review journal profiles after testing `/review --peer`

---

CS: Approve this revised approach? If yes, I'll merge Hugo's clo-author into the applied-micro branch and start Phase 0.
CS: approved.