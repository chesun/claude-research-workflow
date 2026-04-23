# Archive Content Audit — Applied-Micro Claudeflow

**Date:** 2026-04-23
**Scope:** `.claude/agents/archive/` (16 files) + `.claude/rules/archive/` (29 files)
**Purpose:** Comprehensive record of unique content in archived files for absorb/delete decisions.

---

## Summary

**Counts by status (45 files total):**

- IDENTICAL: 6 (tikz-reviewer agent; exploration-fast-track, exploration-folder-protocol, revision-protocol, session-logging, session-reporting, severity-gradient, research-journal — note: several rules are near-identical renames; counted below with SUPERSEDED where text is reproduced in merged files)
- SUPERSEDED: 16
- PARTIAL: 14 (substantive unique content worth absorbing)
- ORPHAN: 3
- OUT-OF-SCOPE: 6

**Files with high-priority absorbable content (PARTIAL, ABSORB recommended):**

- `agents/archive/econometrician.md` — rich Stata package checks for strategist-critic are already present, but the report filename template (`quality_reports/[FILENAME]_econometrics_review.md`) and a clearer "Mode 2: standalone paper/code review" framing are more developed in the archive. ABSORB
- `agents/archive/debugger.md` — fully superseded (content moved to `coder-critic.md`). DELETE.
- `agents/archive/referee.md` — substantive weighting differs (Contribution 25%, Identification 30%, Data 20%, Writing 15%, Fit 10%) from split domain/methods referees. Historical reference only; DELETE or HOLD.
- `agents/archive/replication-auditor.md` — contains 6 detailed AEA checks with specific criteria beyond what `verifier.md` submission mode summarizes. PARTIAL → consider ABSORB into verifier.md.
- `agents/archive/surveyor.md` — fully superseded by `explorer-critic.md`. DELETE.
- `agents/archive/editor.md` — Orchestrator now handles editorial decisions; DELETE.
- `agents/archive/proofreader.md` — fully superseded by `writer-critic.md`. DELETE.
- `agents/archive/discussant.md` — fully superseded by `storyteller-critic.md`. DELETE.
- `agents/archive/domain-reviewer.md` — lecture-oriented template; OUT-OF-SCOPE for research workflow.
- `agents/archive/pedagogy-reviewer.md` — lecture/teaching agent; OUT-OF-SCOPE.
- `agents/archive/slide-auditor.md` — contains substantive Beamer overflow-fix hierarchy and environment-parity checks NOT fully represented in storyteller-critic. PARTIAL → consider ABSORB into storyteller-critic.md (especially the "Spacing-First Fix Principle" ordered list).
- `agents/archive/beamer-translator.md`, `quarto-critic.md`, `quarto-fixer.md`, `r-reviewer.md` — Quarto/RevealJS tooling; OUT-OF-SCOPE for this research project.
- `rules/archive/working-paper-format.md` — NOT present in archive; N/A. (Active version already uses biblatex+biber — fine.)
- `rules/archive/orchestrator-protocol.md` — superseded by workflow.md §2; DELETE.
- `rules/archive/orchestrator-research.md` — content is now in workflow.md "Simplified Mode"; DELETE.
- `rules/archive/r-code-conventions.md` — contains a deep "Common Pitfalls" table with 12 applied-econ R package bugs that is NOT present in any active rule (Stata-conventions is Stata-only; Python-conventions is minimal; there is no active R-conventions rule). PARTIAL → ABSORB the pitfalls table into strategist-critic.md or create a new `rules/r-code-conventions.md`.
- `rules/archive/replication-protocol.md` — contains tolerance thresholds table, Stata-to-R translation pitfalls table, and Phase 5 AEA deposit checklist that are NOT present in verifier.md. PARTIAL → ABSORB tolerance table + Phase 5 into verifier agent or a new replication rule.
- `rules/archive/plan-first-workflow.md` — identical to workflow.md §1; DELETE.
- `rules/archive/quality-gates.md` — has per-language deduction tables (R, Stata, Paper, Talks) NOT present in quality.md. PARTIAL → ABSORB tables into quality.md §1 as reference.
- `rules/archive/separation-of-powers.md`, `adversarial-pairing.md`, `three-strikes.md`, `dependency-graph.md`, `standalone-access.md` — all fully integrated into agents.md + workflow.md. DELETE.
- `rules/archive/scoring-protocol.md` — older weights (Literature 10%, Data 10%, Identification 25%, Code 15%, Paper 25%, Polish 10%, Replication 5%) differ from the CLAUDE.md-stated behavioral weights (design 25%, paper 20%, theory 15%) but MATCH the current `quality.md`. SUPERSEDED by quality.md.
- `rules/archive/severity-gradient.md` — identical to quality.md §2; DELETE.
- `rules/archive/session-logging.md`, `session-reporting.md`, `research-journal.md` — all present in logging.md; DELETE.
- `rules/archive/single-source-of-truth.md` — policy (paper is SOTR; talks derive) is stated in CLAUDE.md "Core Principles" but the explicit SSOT chain + content-fidelity checklist is NOT in an active rule. PARTIAL → consider ABSORB.
- `rules/archive/verification-protocol.md` — task-completion verification checklist (paper/talk/R) differs from verifier.md agent-mode. PARTIAL → ABSORB into workflow.md or verifier.md as a standalone end-of-task checklist.
- `rules/archive/revision-protocol.md` — matches active revision.md. SUPERSEDED.
- `rules/archive/tikz-visual-quality.md` — IDENTICAL to active file.
- `rules/archive/table-generator.md`, `figure-generator-rule.md` — contain extensive R-centric ggplot/modelsummary standards NOT present in the minimalist active tables.md/figures.md. PARTIAL → ABSORB the file-naming conventions and the "Prohibited Patterns" tables into active tables.md and figures.md.
- `rules/archive/pdf-processing.md` — Ghostscript chunking workflow; ORPHAN. Not covered elsewhere; primary-source-first.md references `pdf-learnings` skill instead. HOLD for user decision (may still be useful).
- `rules/archive/beamer-quarto-sync.md`, `no-pause-beamer.md`, `proofreading-protocol.md` — Beamer/Quarto lecture sync infrastructure; OUT-OF-SCOPE.
- `rules/archive/knowledge-base-template.md` — empty template structure; ORPHAN (could live as a project template but not a rule).
- `rules/archive/exploration-fast-track.md`, `exploration-folder-protocol.md` — IDENTICAL to active copies.

---

## Agents

### beamer-translator.md
- **Likely counterpart(s):** none (no active Quarto/RevealJS agent)
- **Status:** OUT-OF-SCOPE
- **Unique content in archived:** Beamer-to-Quarto translation tables (environment mapping, citation mapping, text commands, math boundary rule, figure decision tree, plotly pattern, SCSS-first rule). Specific to lecture Quarto workflow.
- **Recommendation:** DELETE (retain in git history; OUT-OF-SCOPE for research workflow).

### debugger.md
- **Likely counterpart(s):** `agents/coder-critic.md`
- **Status:** SUPERSEDED
- **Unique content in archived:** Originally R-only; active coder-critic.md extends it to Stata (adds Stata-specific reproducibility, program design, output persistence, error handling sections). Only unique archive item is the R-centric framing of check #6 (reproducibility) without Stata branches, which is strictly less general. No unique content worth absorbing.
- **Recommendation:** DELETE.

### discussant.md
- **Likely counterpart(s):** `agents/storyteller-critic.md`
- **Status:** IDENTICAL (byte-for-byte aside from reviewer-name line)
- **Unique content in archived:** none worth absorbing.
- **Recommendation:** DELETE.

### domain-reviewer.md
- **Likely counterpart(s):** none (it's a template for lecture slides, not a research paper)
- **Status:** OUT-OF-SCOPE
- **Unique content in archived:** Five-lens review framework (Assumption Stress Test, Derivation Verification, Citation Fidelity, Code-Theory Alignment, Backward Logic Check) for lecture decks. Framework is generic and interesting, but the explicit target is lecture slides, not papers.
- **Recommendation:** DELETE (lecture-oriented; not part of this project's research scope).

### econometrician.md
- **Likely counterpart(s):** `agents/strategist-critic.md`
- **Status:** SUPERSEDED (active file is a superset — adds a full Stata package-check block)
- **Unique content in archived:** Active strategist-critic.md contains everything the archive does PLUS Stata-specific package checks (reghdfe, ivreghdfe, did_multiplegt, csdid, eventstudyinteract, synth, synth_runner, rdrobust Stata, boottest, estout/esttab, regsave, binscatter/binscatter2, coefplot, psestimate). The archive's "econometrician" name and "Mode 1/Mode 2" framing are preserved in strategist-critic. Report filename template identical. No unique content.
- **Recommendation:** DELETE.

### editor.md
- **Likely counterpart(s):** `agents/orchestrator.md` (editorial decisions), `agents/librarian-critic.md` (Mode 1 lit review), `agents/writer-critic.md` (Mode 2 paper critic)
- **Status:** SUPERSEDED
- **Unique content in archived:** The "3-mode evolving role" framing (Lit Critic → Paper Critic → Journal Editor) has been unbundled into librarian-critic + writer-critic + orchestrator. Mode 1 deduction table (missing seminal paper -20, no methods lit -15, working papers >50% -10, etc.) is reproduced in librarian-critic. Journal selection criteria and editorial decision matrix are in orchestrator. No unique content.
- **Recommendation:** DELETE.

### pedagogy-reviewer.md
- **Likely counterpart(s):** none (lecture-oriented)
- **Status:** OUT-OF-SCOPE
- **Unique content in archived:** 13 pedagogical patterns (Motivation Before Formalism, Incremental Notation, Worked Example After Every Definition, Progressive Complexity, Fragment Reveals, Standout Slides at Conceptual Pivots, Two-Slide Strategy for Dense Theorems, Semantic Color Usage, Box Hierarchy, Box Fatigue, Socratic Embedding, Visual-First, Two-Column Definition Comparisons) plus deck-level checks. Entirely lecture/pedagogy-focused.
- **Recommendation:** DELETE (no applicability to behavioral economics research workflow).

### proofreader.md
- **Likely counterpart(s):** `agents/writer-critic.md`
- **Status:** IDENTICAL (archive is the older name; writer-critic.md reproduces all 6 categories, scoring, format-aware severity, 3-strikes, report format verbatim). Active file adds "Critical Rules" (ignore commented LaTeX; tables are source of truth) which is a plus.
- **Unique content in archived:** none worth absorbing (active is strictly stronger).
- **Recommendation:** DELETE.

### quarto-critic.md
- **Likely counterpart(s):** none
- **Status:** OUT-OF-SCOPE
- **Unique content in archived:** Beamer/Quarto adversarial audit with hard-gates (Overflow, Plot Quality, Content Parity, Visual Regression, Slide Centering, Notation Fidelity, Equation Formatting). Lecture-specific.
- **Recommendation:** DELETE.

### quarto-fixer.md
- **Likely counterpart(s):** none
- **Status:** OUT-OF-SCOPE
- **Unique content in archived:** Implementer for quarto-critic. Lecture-specific.
- **Recommendation:** DELETE.

### r-reviewer.md
- **Likely counterpart(s):** `agents/coder-critic.md`
- **Status:** SUPERSEDED
- **Unique content in archived:** 10-category R-only review. All 10 categories (Structure, Console, Reproducibility, Function Design, Domain Correctness, Figure Quality, RDS Pattern, Comments, Error Handling, Polish) are folded into coder-critic's 12 categories (which extend to Stata). No unique content.
- **Recommendation:** DELETE.

### referee.md
- **Likely counterpart(s):** `agents/domain-referee.md`, `agents/methods-referee.md`
- **Status:** SUPERSEDED (unbundled into two specialized referees)
- **Unique content in archived:** Single-referee weighted dimensions (Contribution 25%, Identification 30%, Data 20%, Writing 15%, Journal Fit 10%). The split critics use different weights (domain-referee: 30/25/20/15/10 with Substantive Arguments + External Validity; methods-referee: 35/25/20/15/5). The combined scheme in the archive is now obsolete — orchestrator averages the two critics. No unique content to absorb.
- **Recommendation:** DELETE.

### replication-auditor.md
- **Likely counterpart(s):** `agents/verifier.md` (submission mode)
- **Status:** PARTIAL
- **Unique content in archived:** Six detailed AEA checks with specific criteria that are more granular than verifier.md's submission mode summary:
  - **Check 1 (Package Inventory)** — explicit requirement that README lists data sources, script order, software requirements, runtime estimate; flag orphan files.
  - **Check 2 (Dependency Verification)** — flag packages not on CRAN (GitHub-only need install instructions); Stata version documented; Python requirements.txt.
  - **Check 3 (Data Provenance)** — explicit grep for `/Users/`, `/home/`, `C:\\` as hard fail.
  - **Check 4 (Execution)** — wall-clock time capture, master-script-runs-numbered-order fallback.
  - **Check 5 (Output Cross-Reference)** — "output file timestamps newer than script timestamps", "spot-check 2-3 key numbers per table".
  - **Check 6 (README AEA format)** — explicit required sections: Data Availability Statement; Computational Requirements; Description of Programs; Instructions for Replicators. Required content: software version, package versions (from `sessionInfo()`), runtime estimate, memory requirements (if >8GB), IRB approval if human subjects.
  - Important Rules block: "Run scripts in a controlled way. Use Rscript with timeout. Capture stderr." / "Runtime matters. If the README says 5 minutes and it takes 2 hours, flag it."
- **Recommendation:** ABSORB into `agents/verifier.md` submission-mode section — replace the current 6-bullet summaries (checks 5–10) with this more detailed checklist, especially the AEA README required sections and the spot-check + timestamp rules.

### slide-auditor.md
- **Likely counterpart(s):** `agents/storyteller-critic.md`
- **Status:** PARTIAL
- **Unique content in archived:** Content beyond storyteller-critic's 5 categories:
  - **Spacing-First Fix Principle** — ordered hierarchy of fixes (1. negative margins → 2. consolidate lists → 3. inline equations → 4. reduce image size → 5. last-resort font reduction, never below 0.85em). Storyteller-critic does not state this hierarchy.
  - **Format-Specific Intelligence** — specific Quarto-native solutions (`:::: {.columns}`, `::: {.panel-tabset}`, `::: {.notes}`) and Beamer-specific checks (`\resizebox{}` on tables exceeding textwidth, `\vspace{-Xem}` overuse warning, prefer splitting over `\footnotesize`).
  - **Environment parity (Beamer → Quarto)** — every Beamer env must have CSS class; flag CSS class used in QMD that doesn't exist in theme SCSS.
  - **Plotly chart quality** checks.
  - **Image & Figure Paths** — flag PDF images in Quarto explicitly.
- **Recommendation:** ABSORB the Beamer-only portion (spacing-first fix hierarchy, `\resizebox` on wide tables, `\vspace{-Xem}` overuse) into storyteller-critic.md as an additional "Fix Priority" subsection. The Quarto portions are OUT-OF-SCOPE for this project.

### surveyor.md
- **Likely counterpart(s):** `agents/explorer-critic.md`
- **Status:** IDENTICAL (renamed)
- **Unique content in archived:** none worth absorbing.
- **Recommendation:** DELETE.

### tikz-reviewer.md
- **Likely counterpart(s):** `agents/tikz-reviewer.md`
- **Status:** IDENTICAL (byte-for-byte)
- **Unique content in archived:** none.
- **Recommendation:** DELETE.

---

## Rules

### adversarial-pairing.md
- **Likely counterpart(s):** `rules/agents.md` §1
- **Status:** SUPERSEDED
- **Unique content in archived:** Old agent names (Editor, Surveyor, Econometrician, Debugger, Proofreader, Discussant) — all renamed in agents.md. No unique content.
- **Recommendation:** DELETE.

### beamer-quarto-sync.md
- **Likely counterpart(s):** none
- **Status:** OUT-OF-SCOPE
- **Unique content in archived:** Lecture-specific .tex↔.qmd sync rule with LaTeX → Quarto translation reference table.
- **Recommendation:** DELETE (no Quarto files in this research project).

### dependency-graph.md
- **Likely counterpart(s):** `rules/workflow.md` §3
- **Status:** SUPERSEDED
- **Unique content in archived:** Old agent names only. Content structure identical.
- **Recommendation:** DELETE.

### exploration-fast-track.md
- **Likely counterpart(s):** `rules/exploration-fast-track.md`
- **Status:** IDENTICAL
- **Unique content in archived:** none.
- **Recommendation:** DELETE.

### exploration-folder-protocol.md
- **Likely counterpart(s):** `rules/exploration-folder-protocol.md`
- **Status:** IDENTICAL
- **Unique content in archived:** none.
- **Recommendation:** DELETE.

### figure-generator-rule.md
- **Likely counterpart(s):** `rules/figures.md`
- **Status:** PARTIAL
- **Unique content in archived:** Active figures.md is a minimalist 10-line file. Archive contains:
  - Full `theme_econ()` ggplot function definition with journal-quality parameters (clean axes, minimal grid, transparent background, legend styling, facet strips, margins).
  - Showtext + Source Serif Pro setup code.
  - Color/linetype pairing rule (never color alone, always pair with linetype/shape/fill).
  - Axis/label formatting (scales::comma, percent, dollar; round-number breaks).
  - Multi-panel rules (lowercase panel tags (a),(b),(c); `scales="free_y"` only when needed).
  - Export pattern with `cairo_pdf`, 6.5in AER single-column width, `bg="transparent"`.
  - File-naming pattern (`{plot_type}_{variable_or_content}.pdf`) with folder structure example (descriptive/estimation/robustness).
  - **Prohibited patterns table** (ggtitle, labs(title/caption), theme_gray/theme_bw, sans-serif, rainbow/jet, 3D effects, png() for final output).
- **Recommendation:** ABSORB the Prohibited Patterns table, the file-naming convention, and a pointer to the `theme_econ()` code into active `rules/figures.md`. The full R theme code block could live at `.claude/references/theme_econ.R` rather than in a rule file.

### knowledge-base-template.md
- **Likely counterpart(s):** none (course-knowledge-base skeleton)
- **Status:** ORPHAN
- **Unique content in archived:** Empty skeleton with headers: Notation Registry, Symbol Reference, Lecture Progression, Empirical Applications, Design Principles, Anti-Patterns, R Code Pitfalls.
- **Recommendation:** HOLD. The skeleton could be useful as a project template file (e.g., `templates/knowledge-base.md`), but as an active rule it's not load-bearing. Delete from `.claude/rules/archive/` and optionally move to `templates/` if the user finds the structure useful.

### no-pause-beamer.md
- **Likely counterpart(s):** none
- **Status:** OUT-OF-SCOPE (lecture-specific)
- **Unique content in archived:** Single rule: never use `\pause`, `\onslide`, `\only`, `\uncover` or any overlay commands in Beamer. Note: this could still apply to job-market/seminar talks in this research project.
- **Recommendation:** HOLD for user judgment. If the user wants the no-pause rule applied to research talks (storyteller agent), ABSORB into `agents/storyteller.md` as a one-line constraint. Otherwise DELETE.

### orchestrator-protocol.md
- **Likely counterpart(s):** `rules/workflow.md` §2
- **Status:** SUPERSEDED
- **Unique content in archived:** Old agent names only (Librarian + Editor, Strategist + Econometrician, Coder + Debugger, etc.). Structure identical to workflow.md §2.
- **Recommendation:** DELETE.

### orchestrator-research.md
- **Likely counterpart(s):** `rules/workflow.md` §2 "Simplified Mode"
- **Status:** SUPERSEDED
- **Unique content in archived:** Explicitly labeled R-script-oriented (`scripts/**/*.R`, `Figures/**/*.R`, `explorations/**`). Simplified-loop content is reproduced verbatim in workflow.md.
- **Recommendation:** DELETE.

### pdf-processing.md
- **Likely counterpart(s):** none (the `pdf-learnings` skill now handles this)
- **Status:** ORPHAN
- **Unique content in archived:** Ghostscript-based 5-page-chunk PDF splitting workflow, error-handling fallback to `pdftk`. This is a concrete operational recipe for long PDFs.
- **Recommendation:** HOLD. The `pdf-learnings` skill is now the intended path (see primary-source-first.md which references it explicitly), but the archive's GS chunking recipe is a concrete fallback. User decides whether to keep as a backup reference at `.claude/references/pdf-chunking.md` or delete.

### plan-first-workflow.md
- **Likely counterpart(s):** `rules/workflow.md` §1
- **Status:** IDENTICAL (text is reproduced verbatim as workflow.md §1)
- **Unique content in archived:** none.
- **Recommendation:** DELETE.

### proofreading-protocol.md
- **Likely counterpart(s):** none directly (writer-critic.md is closest but describes the agent, not the 3-phase workflow)
- **Status:** OUT-OF-SCOPE
- **Unique content in archived:** Three-phase workflow for lecture files: Phase 1 Review & Propose (NO EDITS, saves to quality_reports/), Phase 2 Review & Approve (user), Phase 3 Apply Fixes. The "agent must NEVER apply changes directly" pattern is similar to the general critic-creator separation already codified in agents.md §2.
- **Recommendation:** DELETE (lecture-specific; separation-of-powers is already codified generally).

### quality-gates.md
- **Likely counterpart(s):** `rules/quality.md`
- **Status:** PARTIAL
- **Unique content in archived:** Active quality.md has weighted aggregation and severity gradient but NO per-language deduction tables. Archive has four tables:
  - **Paper LaTeX table** (XeLaTeX fail -100, numbers-tables mismatch -25, undefined citation -15, broken ref -15, overfull hbox >10pt -10, typo in equation -10, notation inconsistency -5, missing fig/table -5, hedging -3 each max -15, overfull 1-10pt -1, long lines -1 except math).
  - **R scripts table** (syntax error -100, domain bugs -30, code-memo mismatch -25, hardcoded paths -20, missing robustness -15, wrong clustering -15, missing set.seed -10, missing RDS -10, magnitude implausible -10, missing fig/table -5, no session info -5, no headers -5, stale outputs -5).
  - **Stata scripts table** (similar structure).
  - **Talks table** (compile fail -100, slide count off -10, talk-only result -10, notation mismatch -5, overfull hbox -2, dense slide -1).
  - Enforcement rules: "Score < 80: Block commit. < 90: Allow, warn. >= 95 + all components >= 80: Submission-ready."
  - Tolerance Thresholds stub table (point estimates, standard errors, coverage rates).
- **Recommendation:** ABSORB all four per-language deduction tables and the "Tolerance Thresholds (Research)" stub into `rules/quality.md` as a new section "§3 Per-Language Deduction Tables". These are useful reference for critics.

### r-code-conventions.md
- **Likely counterpart(s):** none active (only stata-conventions.md and python-code-conventions.md exist)
- **Status:** PARTIAL (there is no active R conventions rule, but this project declares Stata as primary so R may not be needed in active rules)
- **Unique content in archived:**
  - Full **Common Pitfalls table** (12 entries): missing bg=transparent, hardcoded paths, TWFE with staggered DiD + heterogeneous TE, clustering at wrong level, wild bootstrap with few clusters, RDD without McCrary, synthetic control without permutation, event-study binning undocumented, IV F<10 standard CI, `lm()` for panel data, deprecated `feols(..., se="cluster")`, missing first-stage report.
  - **Domain Correctness** section — package-specific DiD guidance (Callaway-Sant'Anna, fastdid, fixest::sunab, did2s), Goodman-Bacon diagnostics requirement, `did::att_gt()` control_group choice.
  - **Line Length & Math Exceptions** — explicit exception rule for mathematical formulas (influence functions, matrix ops, simulation loops) with inline-comment requirement.
  - Institutional color palette definitions (as an example).
  - **Code Quality Checklist** (packages at top, set.seed once, relative paths, Roxygen, transparent bg, RDS saves, WHY comments).
- **Recommendation:** ABSORB. Create a new active rule `rules/r-code-conventions.md` containing the R-specific content, even though R is secondary for this project — the behavioral-economics project may still use R for plots, power simulations, or ML. The "Common Pitfalls" table has substantial strategist-critic value and is NOT duplicated anywhere in active rules. Alternatively, fold the pitfalls table into `strategist-critic.md` under "Package-Specific Checks".

### replication-protocol.md
- **Likely counterpart(s):** `agents/verifier.md` (submission mode)
- **Status:** PARTIAL
- **Unique content in archived:**
  - **Phase 1 Replication Targets table** — explicit format for recording gold-standard numbers from original paper (target, table/figure, value, SE/CI, notes) saved to `quality_reports/LectureNN_replication_targets.md`.
  - **Stata-to-R Translation Pitfalls table** — `reg y x, cluster(id)` vs `feols(y~x, cluster=~id)`; `areg y x, absorb(id)` vs `feols(y~x | id)`; `probit` for PS; bootstrap reps; df-adjustment differences.
  - **Tolerance Thresholds table** — exact-match for integers; <0.01 for point estimates; <0.05 for SEs; same significance level for p-values; <0.1pp for percentages.
  - **Phase 5 AEA Deposit Checklist** — 3 subsections (Package Assembly, Audit, Deposit) with explicit steps: numbered scripts, master script, AEA README, no hardcoded paths, no API keys, sessionInfo(); run /audit-replication; openICPSR deposit + DOI + Data Availability Statement + data citation in .bib.
  - **Audit Tolerance Thresholds table** — table values exact match (same R version); figure visual + same underlying data; runtime within 2x documented; package version mismatch = warning not failure.
- **Recommendation:** ABSORB. Create a new active rule `rules/replication-protocol.md` containing at minimum the Tolerance Thresholds table and the Phase 5 AEA deposit checklist. The Stata-to-R translation pitfalls could also live here since this project has a Stata-primary convention and may need to cross-check to R. These items are not covered elsewhere.

### research-journal.md
- **Likely counterpart(s):** `rules/logging.md` §3
- **Status:** IDENTICAL (reproduced verbatim)
- **Unique content in archived:** none (old agent names only).
- **Recommendation:** DELETE.

### revision-protocol.md
- **Likely counterpart(s):** `rules/revision.md`
- **Status:** SUPERSEDED
- **Unique content in archived:** Old agent names (Debugger, Proofreader, Editor); skill name is `/respond-to-referee` whereas active is `/revise`. Structurally identical.
- **Recommendation:** DELETE.

### scoring-protocol.md
- **Likely counterpart(s):** `rules/quality.md` §1
- **Status:** SUPERSEDED (weights preserved verbatim)
- **Unique content in archived:** Weights are identical (Literature 10%, Data 10%, Identification 25%, Code 15%, Paper 25%, Polish 10%, Replication 5%). Note: these DIFFER from the CLAUDE.md "Quality Thresholds" section which mentions behavioral weights (design 25%, paper 20%, theory 15%). The quality.md file matches the archive; CLAUDE.md may need to be updated separately, but that is outside this audit's scope.
- **Recommendation:** DELETE. (Flag for user: CLAUDE.md's "See `quality.md` for behavioral scoring weights (design 25%, paper 20%, theory 15%)" references a behavioral-specific weighting that is NOT present in the active quality.md — this is a pre-existing mismatch, not an archive issue.)

### separation-of-powers.md
- **Likely counterpart(s):** `rules/agents.md` §2
- **Status:** SUPERSEDED
- **Unique content in archived:** Old agent names only. Structure identical.
- **Recommendation:** DELETE.

### session-logging.md
- **Likely counterpart(s):** `rules/logging.md` §1
- **Status:** SUPERSEDED (active adds Trigger #3, the hard-cap stop-hook reminder)
- **Unique content in archived:** none — archive has 3 triggers; active has 4 (adds hard-cap enforcement). Active is strictly stronger.
- **Recommendation:** DELETE.

### session-reporting.md
- **Likely counterpart(s):** `rules/logging.md` §2
- **Status:** IDENTICAL (reproduced verbatim)
- **Unique content in archived:** none.
- **Recommendation:** DELETE.

### severity-gradient.md
- **Likely counterpart(s):** `rules/quality.md` §2
- **Status:** IDENTICAL (reproduced verbatim)
- **Unique content in archived:** none.
- **Recommendation:** DELETE.

### single-source-of-truth.md
- **Likely counterpart(s):** `CLAUDE.md` "Core Principles" (single source of truth bullet); no dedicated rule file
- **Status:** PARTIAL
- **Unique content in archived:** CLAUDE.md only states the principle in one bullet. Archive contains:
  - **Explicit SSOT chain diagram** (paper/main.tex → talks/*.tex, supplementary/*.tex, figures/, tables/, Bibliography_base.bib, replication/).
  - **Talk Derivation Protocol** — paper-change flag → affected talks flagged; format-specific coverage (job market 40-50 slides / seminar 25-35 / short 10-15 / lightning 3-5).
  - **Figure and Table Freshness** — timestamp check, numbering match, flag for re-derivation after paper revision.
  - **Content Fidelity Checklist (Paper → Talk)** — 6 checks: all results in paper, effect sizes match, SEs/CIs match, notation consistent, citations subset of paper, figures identical (same script output).
- **Recommendation:** ABSORB. Create a new active rule `rules/single-source-of-truth.md` (or merge into `agents/storyteller.md`) containing the SSOT chain, talk derivation protocol, and paper-to-talk fidelity checklist. These are substantive and not captured elsewhere.

### standalone-access.md
- **Likely counterpart(s):** `rules/workflow.md` §4
- **Status:** SUPERSEDED (reproduced verbatim)
- **Unique content in archived:** none (old skill name `/econometrics-check` → `/strategize`).
- **Recommendation:** DELETE.

### table-generator.md
- **Likely counterpart(s):** `rules/tables.md`
- **Status:** PARTIAL
- **Unique content in archived:** Active tables.md is 11 bullet points. Archive contains:
  - **Three-Line Format** code example (`\toprule`, `\midrule`, `\bottomrule`, `\cmidrule(lr)`); explicit ban on `\hline`, `|`, vertical rules.
  - **Coefficient Display** conventions (point estimate on one row, SE parenthetical below, stars, note at bottom).
  - **Column and Row Structure** rules — variable names human-readable examples (`Log wages` not `ln_wage_deflated`; `Female` not `sex_2`); N/R²/FE/Controls at bottom before `\bottomrule`.
  - **Panel Structure** example with `\multicolumn`, italic panel labels, `\midrule` after each panel.
  - **Preferred R Packages** code examples (modelsummary, fixest::etable, kableExtra).
  - **Typography** — serif, `\small`/`\footnotesize` for width-constrained, `\textit{}` for panel labels.
  - **Export** pattern (writeLines to both `paper/tables/` and `results/tables/`).
  - **File Naming** conventions (`sumstats_`, `balance_`, `reg_`, `did_`, `first_stage_`) with folder structure.
  - **Prohibited Patterns table** (7 rows: title row inside table, embedded notes, `\hline`, vertical rules, stargazer, raw R variable names, xtable without booktabs, `\begin{table}` in R output).
- **Recommendation:** ABSORB. The active tables.md is too minimal. Either expand it directly with the Prohibited Patterns table and the file-naming convention, or keep the current minimalist tables.md and add a `.claude/references/table-standards.md` with the full content. The 7-row prohibitions table in particular is valuable for critics.

### three-strikes.md
- **Likely counterpart(s):** `rules/agents.md` §3
- **Status:** SUPERSEDED (reproduced verbatim, just renamed agents)
- **Unique content in archived:** none.
- **Recommendation:** DELETE.

### tikz-visual-quality.md
- **Likely counterpart(s):** `rules/tikz-visual-quality.md`
- **Status:** IDENTICAL
- **Unique content in archived:** none.
- **Recommendation:** DELETE.

### verification-protocol.md
- **Likely counterpart(s):** `agents/verifier.md`
- **Status:** PARTIAL
- **Unique content in archived:** Archive file is a rule that orchestrates end-of-task verification (pre-commit); verifier.md is an agent definition. Content differs in purpose:
  - Archive — explicit per-target checklists (Paper: 3-pass xelatex + bibtex, check `\ref{}` and `\cite{}`, overfull hbox >1pt, tables compile, figures exist; Talk: xelatex, figures/tables match paper, overfull hbox, slide count; R: Rscript runs, output files non-zero size, magnitude spot-check, set.seed present).
  - Archive — **Common Pitfalls** list (assuming success without verifying, stale figures via timestamp check, hardcoded paths, missing packages).
  - Archive — final **Verification Checklist** bullet list.
  - The framing "at the end of EVERY task, Claude MUST verify the output works correctly" is a user-facing rule, not an agent behavior.
- **Recommendation:** ABSORB. Create a new active rule `rules/verification-protocol.md` (or add this content as a new section in `rules/workflow.md`). The verifier agent covers "what to check" but the archive rule covers "when to check and the per-target checklists" which is user-facing and should not require agent dispatch.

---

## End of Audit
