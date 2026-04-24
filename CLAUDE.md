# CLAUDE.MD -- Behavioral & Experimental Economics Research with Claude Code

<!-- HOW TO USE: Replace [BRACKETED PLACEHOLDERS] with your project info.
     Customize Beamer environments for your talk preamble.
     Keep this file under ~150 lines — Claude loads it every session.
     Based on clo-author (Hugo Sant'Anna) + infrastructure from Pedro Sant'Anna
     + behavioral/experimental econ extensions. -->

**Project:** [YOUR PROJECT NAME]
**Institution:** [YOUR INSTITUTION]
**Field:** Behavioral & Experimental Economics
**Branch:** main
**Stata version:** 17
**LaTeX engine:** pdflatex
**Overleaf path:** [YOUR OVERLEAF PATH — e.g., ~/Library/CloudStorage/Dropbox/Apps/Overleaf/project-name]

---

## Core Principles

- **Plan first** -- enter plan mode before non-trivial tasks; save plans to `quality_reports/plans/`
- **Verify after** -- compile and confirm output at the end of every task
- **Single source of truth** -- Paper `main.tex` is authoritative; talks and supplements derive from it
- **Quality gates** -- weighted aggregate score; nothing ships below 80/100; see `quality.md`
- **Worker-critic pairs** -- every creator has a paired critic; critics never edit files
- **Inference first** -- design experiments with inference in mind from the start; tests and treatments co-evolve (see inference-first checklist)
- **Primary source first** -- before citing a paper in a load-bearing artifact, read the PDF and produce reading notes in `master_supporting_docs/literature/reading_notes/`; hooks block edits otherwise (see `primary-source-first.md`)
- **Decisions are ADRs** -- substantive design, identification, or specification decisions live in `decisions/NNNN_slug.md`; analysis docs hold reasoning, ADRs hold the record (see `decision-log.md`)
- **Track TODOs** -- project root `TODO.md` tracks open work (Active / Up Next / Waiting / Backlog / Done); update after completing any task (see `todo-tracking.md`)
- **Auto-memory** -- corrections and preferences are saved automatically via Claude Code's built-in memory system

---

## Getting Started

1. Fill in the `[BRACKETED PLACEHOLDERS]` in this file
2. Run `/discover interview [topic]` to build your research specification
3. Or run `/new-project [topic]` for the full orchestrated pipeline

---

## Folder Structure

The project spans two locations: a **git repo** (code, data, experiments, workflow) and an **Overleaf project** (paper, talks, LaTeX). Overleaf syncs via Dropbox.

```
[YOUR-PROJECT]/                  # Git repo
├── CLAUDE.md                    # This file
├── TODO.md                      # Active work tracker (see todo-tracking.md)
├── .claude/                     # Rules, skills, agents, hooks
├── decisions/                   # ADRs — NNNN_slug.md, append-only (see decision-log.md)
├── theory/                      # Formal models
│   ├── model.tex
│   └── proofs/
├── experiments/                 # Experiment materials
│   ├── designs/                 # Design docs, checklists
│   ├── protocols/               # IRB, consent forms
│   ├── instructions/            # Subject instructions (LaTeX)
│   ├── oTree/                   # oTree project code
│   ├── qualtrics/               # QSF exports, custom JS/CSS
│   ├── comprehension/           # Understanding/attention checks
│   └── pilots/                  # Pilot data, timing, budgets
├── data/
│   ├── raw/                     # Untouched data
│   ├── cleaned/                 # Processed data
│   └── simulated/               # Power analysis simulations
├── scripts/
│   ├── stata/                   # PRIMARY (main.do, settings.do, numbered .do files)
│   └── python/                  # SECONDARY
├── replication/                  # AEA replication package (code + data + README)
├── explorations/                # Research sandbox
├── quality_reports/             # Plans, specs, reviews, session logs
├── templates/                   # Session log, quality report, experiment checklist
└── master_supporting_docs/      # Reference papers and data docs
    ├── literature/              # Primary sources (gated by primary-source-first hook)
    │   ├── papers/              # PDFs of cited papers (surname_year naming)
    │   └── reading_notes/       # One .md per cited paper (see README.md)
    └── supporting_papers/       # Methodology references, textbook chapters (not load-bearing)

[OVERLEAF_PATH]/                 # Overleaf project (via Dropbox)
├── paper/                       # Main manuscript (SOURCE OF TRUTH)
│   └── main.tex
├── slides/                      # Each talk is its own folder
│   ├── job_market/
│   ├── seminar/
│   └── short/
├── figures/
├── tables/
├── supplementary/               # Online appendix
├── preambles/                   # Shared LaTeX headers
└── bibliography_base.bib
```

---

## Commands

```bash
# Paper compilation (3-pass, pdflatex) — run from Overleaf dir
cd [OVERLEAF_PATH]/paper && pdflatex -interaction=nonstopmode main.tex
BIBINPUTS=..:$BIBINPUTS bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

# Talk compilation (pdflatex with preambles) — each talk has its own folder
cd [OVERLEAF_PATH]/slides/job_market && TEXINPUTS=../../preambles:$TEXINPUTS pdflatex -interaction=nonstopmode talk.tex
BIBINPUTS=../..:$BIBINPUTS bibtex talk
TEXINPUTS=../../preambles:$TEXINPUTS pdflatex -interaction=nonstopmode talk.tex
TEXINPUTS=../../preambles:$TEXINPUTS pdflatex -interaction=nonstopmode talk.tex
```

---

## Quality Thresholds

| Score | Gate | Applies To |
|-------|------|------------|
| 80 | Commit | Weighted aggregate (blocking) |
| 90 | PR | Weighted aggregate (blocking) |
| 95 | Submission | Aggregate + all components >= 80 |
| -- | Advisory | Talks (reported, non-blocking) |

See `quality.md` for behavioral scoring weights (design 25%, paper 20%, theory 15%).

---

## Skills Quick Reference

| Command | What It Does |
|---------|-------------|
| `/new-project [topic]` | Full pipeline: idea → paper (orchestrated) |
| `/discover [mode] [topic]` | Discovery: interview, literature, data, ideation |
| `/design experiment [topic]` | Inference-first experiment design (14-step checklist) |
| `/theory [develop/review]` | Formal model development or proof review |
| `/analyze [dataset]` | End-to-end data analysis (Stata 17 primary) |
| `/write [section]` | Draft paper sections + humanizer pass |
| `/review [file/--flag]` | Quality reviews (routes by target: paper, code, peer) |
| `/challenge [--mode] [file]` | Devil's advocate: `--design`, `--theory`, `--paper`, `--fresh` |
| `/preregister [study]` | Generate pre-registration (AsPredicted, OSF) |
| `/qualtrics [mode]` | Create/validate/improve Qualtrics surveys |
| `/otree [mode]` | Generate/review oTree experiment code |
| `/revise [report]` | R&R cycle: classify + route referee comments |
| `/talk [mode] [format]` | Create, audit, or compile Beamer presentations |
| `/submit [mode]` | Journal targeting → package → audit → final gate |
| `/tools [subcommand]` | Utilities: commit, compile, validate-bib, context-status, etc. |

---

## Beamer Custom Environments (Talks)

| Environment       | Effect        | Use Case       |
|-------------------|---------------|----------------|
| `[your-env]`      | [Description] | [When to use]  |

---

## Output Organization

Output organization: by-script

---

## Current Project State

| Component | File | Status | Description |
|-----------|------|--------|-------------|
| Paper | `[OVERLEAF]/paper/main.tex` | [draft/submitted/R&R] | [Brief description] |
| Theory | `theory/model.tex` | [not started/draft/complete] | [Model description] |
| Experiment | `experiments/designs/` | [design/piloting/running/complete] | [Design description] |
| Data | `scripts/stata/` | [complete/in-progress] | [Analysis description] |
| Replication | `replication/` | [not started/ready] | [Deposit status] |
| Pre-registration | -- | [not started/filed] | [Registry and ID] |
| Job Market Talk | `[OVERLEAF]/slides/job_market/` | -- | [Status] |
