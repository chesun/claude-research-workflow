# Session Log: 2026-03-29 — Seminal Papers Expansion + Qualtrics QSF Analysis

**Status:** IN PROGRESS
**Branch:** `behavioral`

## Objective
1. Expand seminal papers reference list from starter (37 entries) to comprehensive (232 entries)
2. Analyze Christina's JMP Qualtrics QSF files to inform `/qualtrics` skill development

## Changes Made

| File | Change | Reason |
|------|--------|--------|
| `.claude/references/seminal-papers-by-subfield.md` | Expanded 37 → 232 entries, 12 sections | To-do item: gather seminal papers per subfield |
| `quality_reports/session_logs/2026-03-29_phase0-completion-phase1.md` | Appended seminal papers expansion log | Session tracking |
| `quality_reports/plans/2026-03-28_behavioral-plan-v3-hugo-base.md` | Checked off seminal papers + subfield categories items | Plan tracking |

## Seminal Papers Summary
- Searched Mendeley by subfield (11 searches) and by researcher name (Oprea, Yuksel, Enke, Zimmermann, Vieider, Coffman, Bohren, Bordalo, Niederle, Esponda)
- Web searched for canonical papers not in Mendeley
- Added section 12: Gender & Competition
- Christina reviewed and corrected: renamed section 1, fixed Chakraborty cite, added Krupka & Weber, removed Carrell/Page/West (applied not behavioral), moved Exley & Kessler to Beliefs
- Committed: `99239a6`, `cc84133`

## Qualtrics QSF Analysis (in progress)
Analyzing two JMP experiment QSF files:
- `All_treats_diff_prior_June_30_FIXED.qsf` (302KB, 97 questions, 24 blocks)
- `Match__Benchmark_July_10.qsf` (362KB, 107 questions, 27 blocks)

### Key findings from File 1:
- **2 BlockRandomizers:** (1) worker_group = asian/hispanic, (2) treat_dfe = 0-5 mapping to d/v/f20/b/vc
- **19 questions with custom JavaScript** — largest are 16K+ chars implementing worker draw-without-replacement interface
- **DB/TB questions** = Descriptive Text blocks used as containers for custom HTML/JS button-click interfaces
- **Loop & Merge** in Part 3: 10 iterations over randomly drawn worker profiles for wage offers (0-12)
- **Custom CSS** in Look & Feel settings
- Worker arrays hardcoded in JS: 100 workers per group with [name, race, male, scoreBin, age, color, exactScore]
- State persistence via Base64-encoded JSON in hidden text inputs
- Embedded data extensively used: draw_count, drawn_bins, drawn_races, drawn_workers, draw_duration_sec, profile1-10_name/age/color/gender/avatar

### File 2 Differences (Match & Benchmark)
- 2 new treatment arms: m (Match), fb (Forced Benchmark) — follow-up treatments in separate QSF
- QID602 (36,826 chars JS): yoking design — hardcoded ~200 prior participants' draw sequences, randomly assigns matched sequence
- QID591 (5,490 chars): draws workers using the matched sequence (forced replay)
- 3 new blocks: Part 2 Match Beliefs, Part 2 instructions Match, Part 2 Match Draws

### Additional Patterns Documented (second pass)
- Pattern 6: Consent branching → End Survey on decline
- Pattern 7: Comprehension quiz with CustomValidation + JS error counting + failure routing (3 errors → End Survey)
- Pattern 8: Attention checks recorded as embedded data (not gates) — instructed response MC + absurd statement Matrix
- Pattern 9: Treatment-specific block routing via nested branches
- Pattern 10: Constant Sum (CS/VRTL) for full prior/posterior belief distribution elicitation
- Pattern 11: Survey-level settings (no back button, no progress bar, Prolific redirect, reCAPTCHA, RelevantID)
- Pattern 12: show_* modular flags for testing individual sections

### Corrections from Christina
- Two-file strategy is NOT best practice — was a necessity for follow-up treatments. Single file with one randomizer is preferred for proper randomization.

### Saved to: `quality_reports/paper_learnings/jmp-qualtrics-patterns.md` (18 reusable patterns)

## Decisions
- Cross-listing papers between sections is fine (Christina confirmed)
- 232 entries is sufficient — add organically going forward
- Single-file QSF with all treatments in one randomizer is the standard

## Qualtrics Skill & Agent Enrichment (2026-03-29)

**Task:** Improve `/qualtrics` skill and `qualtrics-specialist` agent based on JMP QSF analysis.

**Commits:**
- `9c49f8c` — enriched skill (117→177 lines) and agent (104→320 lines) with 14 named patterns
- `30030d3` — added `.claude/references/qualtrics-patterns.md` quick reference + auto-learning instructions

**Changes:**
- Skill: all 4 modes enriched with concrete patterns, 10 principles, pattern-learning section
- Agent: 8 new design pattern sections (survey flow, MPL, quiz error counting, attention checks, state persistence, L&M, input validation, asset hosting), reference docs, pattern-learning section
- Reference doc: portable quick reference for agent consumption
- Patterns doc: expanded to 14 named patterns + 19 reusable bullet points (added MPL implementation from earlier JMP version QSF, input validation patterns)

**Key additions from 3rd QSF (MPL version):**
- MPL uses Matrix/Bipolar question type with JS autofill on switch + single-switch enforcement
- Custom Next button replaces built-in for validation before advancing
- Switch row stored in embedded data per L&M iteration
- Bonus calculation JS reads embedded data across all rounds, randomly selects paying round

**Architecture decisions:**
- Two-tier doc system: quick reference (`.claude/references/`) + detailed patterns (`quality_reports/paper_learnings/`)
- Auto-learning: skill and agent check patterns docs after each task, append novel techniques
- Single-file with one randomizer is the standard (two-file is a workaround)

## Open Questions
- None currently blocking
