# CLAUDE.md — Research Workflow with Claude Code

<!-- HOW TO USE: This is the universal (main) template.
     If your research is applied micro (observational data, identification
     strategies), check out the `applied-micro` branch after forking.
     If your research is behavioral/experimental (lab, field, online
     experiments, formal theory), check out the `behavioral` branch.
     Otherwise, main works on its own as a general-purpose research template.

     Replace [BRACKETED PLACEHOLDERS] with your project info.
     Keep this file under ~150 lines — Claude loads it every session.
     Based on clo-author (Hugo Sant'Anna) + infrastructure from
     Pedro Sant'Anna, adapted for research-paper workflows. -->

**Project:** [YOUR PROJECT NAME]
**Institution:** [YOUR INSTITUTION]
**Branch:** main (universal)
**Primary analysis language:** [e.g., Stata 17 / R / Python / Julia]
**LaTeX engine:** [pdflatex | xelatex]
**Overleaf path:** [optional — e.g., ~/Library/CloudStorage/Dropbox/Apps/Overleaf/project-name. If set, compile/verify tooling targets this path instead of in-repo paper/ and talks/.]

---

## Core Principles

- **Plan first** — enter plan mode before non-trivial tasks; save plans to `quality_reports/plans/`
- **Verify after** — compile and confirm output at the end of every task
- **Single source of truth** — the paper is authoritative; talks and supplements derive from it (see `single-source-of-truth.md`)
- **Quality gates** — weighted aggregate score; nothing ships below 80/100 (see `quality.md`)
- **Worker-critic pairs** — every creator has a paired critic; critics never edit files (see `agents.md`)
- **Primary source first** — before citing a paper in a load-bearing artifact, read the PDF and produce reading notes in `master_supporting_docs/literature/reading_notes/`; hooks block edits otherwise (see `primary-source-first.md`)
- **Decisions are ADRs** — substantive decisions live in `decisions/NNNN_slug.md` (see `decision-log.md`)
- **Track TODOs** — project root `TODO.md` (see `todo-tracking.md`)
- **Auto-memory** — corrections and preferences saved automatically via Claude Code's built-in memory system

---

## Getting Started

1. Fill in the `[BRACKETED PLACEHOLDERS]` in this file.
2. Decide whether you want an overlay:
   - Observational-data, identification-strategy research → `git checkout applied-micro`
   - Experimental, theoretical, or behavioral research → `git checkout behavioral`
   - General-purpose → stay on `main`.
3. Run `/discover interview [topic]` to build your research specification, or `/new-project [topic]` for the full orchestrated pipeline.

---

## Folder Structure

```
[YOUR-PROJECT]/
├── CLAUDE.md                    # This file
├── TODO.md                      # Active work tracker (see todo-tracking.md)
├── README.md                    # Project README
├── .claude/                     # Rules, skills, agents, hooks
├── decisions/                   # ADRs — NNNN_slug.md, append-only (see decision-log.md)
├── paper/                       # Main LaTeX manuscript (source of truth)
│   ├── main.tex                 # Primary paper file (populate when starting)
│   └── sections/                # Section-level .tex files
├── talks/                       # Derivative Beamer presentations (job_market / seminar / short / lightning)
├── figures/                     # Final figures (.pdf, .png) referenced in paper
├── tables/                      # Final tables (.tex) referenced in paper
├── preambles/                   # Shared LaTeX preamble / header
├── data/
│   ├── raw/                     # Original untouched data (often gitignored)
│   └── cleaned/                 # Processed datasets
├── scripts/                     # Analysis code (stata/, R/, python/)
├── replication/                 # AEA replication package (code + data + README)
├── explorations/                # Research sandbox (see exploration-folder-protocol)
├── quality_reports/             # Plans, specs, reviews, session logs, merges
├── templates/                   # Session log, quality report, requirements spec templates
└── master_supporting_docs/
    ├── literature/              # Primary sources (gated by primary-source-first hook)
    │   ├── papers/              # PDFs (surname_year naming)
    │   └── reading_notes/       # One .md per cited paper
    └── supporting_papers/       # Methodology references, textbook chapters
```

**If using Overleaf:** keep `paper/` and `talks/` as stubs (or symlinks to your Overleaf directory). Point compile and verify tooling at the Overleaf path via the `Overleaf path:` header above — rules and skills honor that override.

---

## Commands

```bash
# Paper compilation (3-pass) — adjust engine and paths per project
cd paper && pdflatex -interaction=nonstopmode main.tex
BIBINPUTS=..:$BIBINPUTS bibtex main    # or: biber main (with biblatex)
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

See `.claude/skills/tools/SKILL.md` for the `/tools compile` subcommand that automates this.

---

## Quality Thresholds

| Score | Gate | Applies To |
|-------|------|------------|
| 80 | Commit | Weighted aggregate (blocking) |
| 90 | PR | Weighted aggregate (blocking) |
| 95 | Submission | Aggregate + all components >= 80 |
| — | Advisory | Talks (non-blocking) |

See `quality.md` for weighted aggregation formula and per-target deduction tables.

---

## Skills Quick Reference (universal)

| Command | What It Does |
|---------|-------------|
| `/new-project [topic]` | Full pipeline: idea → paper (orchestrated) |
| `/discover [mode] [topic]` | Discovery: interview, literature, data, ideation |
| `/analyze [dataset]` | End-to-end data analysis |
| `/write [section]` | Draft paper sections + humanizer pass |
| `/review [file/--flag]` | Quality reviews (routes by target) |
| `/revise [report]` | R&R cycle: classify + route referee comments |
| `/talk [mode] [format]` | Create, audit, or compile Beamer presentations |
| `/submit [mode]` | Journal targeting → package → audit → final gate |
| `/challenge [file --mode]` | Devil's advocate: `--paper`, `--fresh`, etc. |
| `/tools [subcommand]` | Utilities: commit, compile, validate-bib, context-status, learn |

Overlay branches add paradigm-specific skills: `applied-micro` adds `/strategize`, `/balance`, `/event-study`; `behavioral` adds `/design`, `/theory`, `/otree`, `/qualtrics`, `/preregister`.

---

## Current Project State

| Component | File | Status | Description |
|-----------|------|--------|-------------|
| Paper | `paper/main.tex` | [draft/submitted/R&R] | [Brief description] |
| Data | `scripts/` | [complete/in-progress] | [Analysis description] |
| Replication | `replication/` | [not started/ready] | [Deposit status] |
| Job Market Talk | `talks/job_market_talk.tex` | — | [Status] |
