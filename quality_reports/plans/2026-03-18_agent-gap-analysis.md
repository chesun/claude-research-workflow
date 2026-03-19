# Agent Gap Analysis — What Exists vs. What's Planned

**Date:** 2026-03-18

---

## Shared Agents (should be on `main`, available to both branches)

| Agent | Plan Says | Currently Exists in Template? | Status |
|-------|-----------|------------------------------|--------|
| librarian | Shared | No — planned only | **NEEDS CREATION** |
| librarian-critic | Shared | No — planned only | **NEEDS CREATION** |
| data-engineer | Shared | No — planned only | **NEEDS CREATION** |
| coder | Shared | No — planned only | **NEEDS CREATION** |
| coder-critic | Shared | No — planned only | **NEEDS CREATION** |
| writer | Shared | No — planned only | **NEEDS CREATION** |
| writer-critic | Shared | No — planned only | **NEEDS CREATION** |
| verifier | Shared | Yes (slide-focused) | **NEEDS ADAPTATION** |
| proofreader | Shared | Yes (slide-focused) | **NEEDS ADAPTATION** |
| tikz-reviewer | Shared | Yes | Copied to TX |

## Applied-Micro-Only Agents (on `applied-micro` branch)

| Agent | Plan Says | Exists? | Status |
|-------|-----------|---------|--------|
| identification-critic | Applied-micro | No | **NEEDS CREATION (Phase 3)** |
| applied-micro-referee | Applied-micro | No | **NEEDS CREATION (Phase 3)** |
| replication-auditor | Applied-micro | No | **NEEDS CREATION (Phase 3)** |
| robustness-designer | Applied-micro | No | **NEEDS CREATION (Phase 3)** |

## Behavioral-Only Agents (on `behavioral` branch, NOT for TX)

| Agent | Exists? |
|-------|---------|
| designer, designer-critic | No — Phase 4 of behavioral plan |
| theorist, theorist-critic | No — Phase 4 of behavioral plan |
| qualtrics-specialist | No — Phase 4 of behavioral plan |
| otree-specialist | No — Phase 4 of behavioral plan |
| methods-referee | No — Phase 4 of behavioral plan |
| domain-referee | Yes (template, slide-focused) — needs adaptation |

## Template Agents That Exist But Are Slide-Specific (NOT copied to TX)

| Agent | Why Not Copied |
|-------|----------------|
| beamer-translator | Quarto translation — not relevant |
| domain-reviewer | Slide pedagogy — not relevant |
| pedagogy-reviewer | Slide pedagogy — not relevant |
| quarto-critic | Quarto-specific |
| quarto-fixer | Quarto-specific |
| r-reviewer | R-focused — Stata primary for TX |
| slide-auditor | Slide-specific |

---

## Summary

**The core worker-critic agent pairs (librarian, coder, writer, data-engineer) don't exist yet in any repo.** They were proposed in the plan but never built. These are Phase 3-4 items in both the behavioral and applied micro roadmaps.

**What's currently in the TX repo:**
- verifier.md (needs adaptation from slides to papers)
- proofreader.md (needs adaptation from slides to papers)
- tikz-reviewer.md (good as-is for paper figures)

**Recommendation:** Create the shared agents (librarian pair, coder pair, writer pair, data-engineer) as part of Phase 1-2, since they're needed for both workflows. Build them on `main`, then they flow to both branches.

## Devils-Advocate Upgrade Plan

The current `/devils-advocate` skill is slide-pedagogy-focused. The plan v2 proposed upgrading to `/challenge` with these modes:

| Mode | Focus | Branch |
|------|-------|--------|
| `--design` | Experiment design challenge (demand effects, confounds, incentives, comprehension) | Behavioral |
| `--theory` | Model assumptions, proof gaps, alternative predictions | Behavioral |
| `--paper` | Contribution framing, identification threats, referee objections | **Shared** |
| `--identification` | Exclusion restriction, parallel trends, instrument validity | **Applied-micro** |
| `--fresh` | "Forget everything you know" cold read | **Shared** |

**Proposal:** Rename to `/challenge`, keep `--paper` and `--fresh` as shared modes. Add `--identification` on applied-micro branch. Current slide-pedagogy content becomes a `--slides` mode on the behavioral branch.

CS: Does this look right? Should I proceed with creating shared agents in Phase 1, or defer to Phase 3 as originally planned?

CS: This looks right. Make sure all of this is included in the plan. implement shared agents in phase 1, save the rest for phase 3