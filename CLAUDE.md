# CLAUDE.MD -- Applied Microeconomics Research with Claude Code

<!-- HOW TO USE: Replace [BRACKETED PLACEHOLDERS] with your project info.
     Customize for your analysis language, LaTeX engine, and identification strategy.
     Keep this file under ~150 lines — Claude loads it every session.
     Based on clo-author (Hugo Sant'Anna) + infrastructure from Pedro Sant'Anna. -->

**Project:** [YOUR PROJECT NAME]
**Institution:** [YOUR INSTITUTION]
**Branch:** main

---

## Core Principles

- **Plan first** -- enter plan mode before non-trivial tasks; save plans to `quality_reports/plans/`
- **Verify after** -- compile and confirm output at the end of every task
- **Single source of truth** -- Paper `main.tex` is authoritative; talks and supplements derive from it
- **Quality gates** -- weighted aggregate score; nothing ships below 80/100; see `quality.md`
- **Worker-critic pairs** -- every creator has a paired critic; critics never edit files
- **[LEARN] tags** -- when corrected, save `[LEARN:category] wrong → right` to MEMORY.md

---

## Getting Started

1. Fill in the `[BRACKETED PLACEHOLDERS]` in this file
2. Run `/discover interview [topic]` to build your research specification
3. Or run `/new-project [topic]` for the full orchestrated pipeline

---

## Folder Structure

```
[YOUR-PROJECT]/
├── CLAUDE.MD                    # This file
├── .claude/                     # Rules, skills, agents, hooks
├── Bibliography_base.bib        # Centralized bibliography
├── paper/                       # Main LaTeX manuscript (source of truth)
│   ├── main.tex                 # Primary paper file
│   └── sections/                # Section-level .tex files
├── talks/                       # Derivative Beamer presentations
│   ├── job_market_talk.tex      # 45-60 min, full results
│   ├── seminar_talk.tex         # 30-45 min, standard seminar
│   ├── short_talk.tex           # 15 min, conference session
│   └── lightning_talk.tex       # 5 min, spiel/elevator pitch
├── data/                        # Project data
│   ├── raw/                     # Original untouched data (often gitignored)
│   └── cleaned/                 # Processed datasets ready for analysis
├── output/                      # Intermediate results (logs, temp files)
├── figures/                     # Final figures (.pdf, .png) referenced in paper
├── tables/                      # Final tables (.tex) referenced in paper
├── supplementary/               # Online appendix and supplements
├── replication/                 # Replication package for deposit
├── preambles/header.tex         # LaTeX headers / shared preamble
├── scripts/                     # Analysis code (Stata primary, R/Python secondary)
├── quality_reports/             # Plans, session logs, reviews, scores
├── explorations/                # Research sandbox (see rules)
├── templates/                   # Session log, quality report templates
└── master_supporting_docs/      # Reference papers and data docs
```

---

## Commands

```bash
# Paper compilation (3-pass, pdflatex)
cd Paper && pdflatex -interaction=nonstopmode main.tex
BIBINPUTS=..:$BIBINPUTS bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

# Talk compilation (pdflatex with preambles)
cd Talks && TEXINPUTS=../Preambles:$TEXINPUTS pdflatex -interaction=nonstopmode talk.tex
```

---

## Quality Thresholds

| Score | Gate | Applies To |
|-------|------|------------|
| 80 | Commit | Weighted aggregate (blocking) |
| 90 | PR | Weighted aggregate (blocking) |
| 95 | Submission | Aggregate + all components >= 80 |
| -- | Advisory | Talks (reported, non-blocking) |

See `quality.md` for weighted aggregation formula.

---

## Skills Quick Reference

| Command | What It Does |
|---------|-------------|
| `/new-project [topic]` | Full pipeline: idea → paper (orchestrated) |
| `/discover [mode] [topic]` | Discovery: interview, literature, data, ideation |
| `/strategize [question]` | Identification strategy or pre-analysis plan |
| `/analyze [dataset]` | End-to-end data analysis |
| `/write [section]` | Draft paper sections + humanizer pass |
| `/review [file/--flag]` | Quality reviews (routes by target: paper, code, peer) |
| `/revise [report]` | R&R cycle: classify + route referee comments |
| `/talk [mode] [format]` | Create, audit, or compile Beamer presentations |
| `/submit [mode]` | Journal targeting → package → audit → final gate |
| `/challenge [file --mode]` | Devil's advocate: `--paper`, `--identification`, `--fresh` |
| `/balance [treatment]` | Generate balance tables (Stata/R) |
| `/event-study [spec]` | Event study plots with pre-trends and CIs |
| `/compile-latex [file]` | 3-pass pdflatex + bibtex (papers and talks) |
| `/tools [subcommand]` | Utilities: commit, validate-bib, context-status, learn, etc. |

---

<!-- CUSTOMIZE: Replace the example entries below with your own
     Beamer environments for talks. -->

## Beamer Custom Environments (Talks)

| Environment       | Effect        | Use Case       |
|-------------------|---------------|----------------|
| `[your-env]`      | [Description] | [When to use]  |

---

## Current Project State

| Component | File | Status | Description |
|-----------|------|--------|-------------|
| Paper | `paper/main.tex` | [draft/submitted/R&R] | [Brief description] |
| Data | `scripts/stata/` | [complete/in-progress] | [Analysis description] |
| Replication | `replication/` | [not started/ready] | [Deposit status] |
| Job Market Talk | `talks/job_market_talk.tex` | -- | [Status] |
