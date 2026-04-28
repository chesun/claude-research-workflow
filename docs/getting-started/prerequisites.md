# Prerequisites

This workflow assumes a baseline of competence with command-line tools, git, LaTeX, and at least one of Stata / R / Python. If any of those are unfamiliar, you'll need to invest a few hours in the basics before the workflow itself becomes useful. The right intervention isn't a hand-held alternative path; it's pointing you at good resources and letting you come back ready to use the same tools everyone else does.

This page is a curated list. It does not re-teach. Each prerequisite has a single recommended resource and a rough time estimate.

---

## Required for everyone

### Git basics (~2 hours)

You'll be cloning, branching, committing, pushing, and occasionally pulling. You'll see commit hashes referenced in this workflow's docs. You don't need to be an expert; you need to recognize what those operations do and be comfortable running them.

- **Read:** [Pro Git, chapters 1–3](https://git-scm.com/book/en/v2). Free online. The first three chapters cover everything you'll need for ~90% of workflow use.
- **Skip if:** you already commit and push from the command line without thinking about it.

### Terminal / command-line literacy (~1 hour)

Claude Code is a CLI tool. You'll be opening a terminal, navigating directories with `cd`, listing files with `ls`, and running commands. If "open a terminal" is unfamiliar, start here.

- **macOS / Linux:** [Apple's Terminal User Guide, "The basics" section](https://support.apple.com/guide/terminal/open-or-quit-terminal-apd5265185d-f365-44cb-8b09-71a064a42125/mac), or [The Linux Command Line by William Shotts (free PDF), chapters 1–4](https://linuxcommand.org/tlcl.php).
- **Windows:** install [Git Bash](https://git-scm.com/downloads) (comes with Git for Windows) or [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/install). Use that as your terminal — most workflow examples assume bash-style syntax.
- **Skip if:** you regularly run scripts from a terminal.

### Claude Code CLI (~30 minutes)

The actual tool this workflow extends. Install it, run it once, get comfortable with the basic interaction model.

- **Install:** [anthropic.com/claude-code](https://www.anthropic.com/claude-code) — follow the official installation steps for your OS.
- **First-run guide:** [Claude Code documentation](https://docs.claude.com/claude-code) — read the "getting started" section. Five minutes covers the basics; another twenty covers slash commands and tool use.
- **Skip if:** you've used `claude` in a project before.

### LaTeX (~1 hour to install + verify)

The workflow produces papers in LaTeX (pdflatex with biblatex/biber). You don't need to be a LaTeX expert — agents handle most of the syntax — but you need a working LaTeX installation to compile the output.

- **Install:** [MacTeX (macOS)](https://www.tug.org/mactex/), [TeX Live (Linux)](https://www.tug.org/texlive/), [MiKTeX (Windows)](https://miktex.org/).
- **Verify:** open a terminal, run `pdflatex --version` and `biber --version`. Both should print version info.
- **Optional reading:** [Overleaf's "Learn LaTeX in 30 minutes"](https://www.overleaf.com/learn/latex/Learn_LaTeX_in_30_minutes) if you've never seen a `.tex` file.
- **Skip if:** you compile LaTeX papers regularly.

---

## At least one of these (depends on your work)

### Stata 17+

Most applied-micro projects use Stata as the primary analysis language. The workflow's `stata-code-conventions.md` rule encodes the conventions we expect.

- **Required:** Stata SE or MP, version 17 or newer (the workflow uses `frames` extensively).
- **Skip if:** you don't do Stata work — R or Python is fine for many workflows.

### R (≥ 4.0)

Common for behavioral and identification-strategy work. The workflow's `r-code-conventions.md` covers package preferences (`fixest`, `did`, `modelsummary`, etc.) and clustering pitfalls.

- **Required:** R ≥ 4.0 plus an IDE if you don't already have one (RStudio is standard).
- **Skip if:** you don't use R.

### Python (≥ 3.10)

Used for ML / text classification / web scraping / specialized econometric packages. Workflow conventions in `python-code-conventions.md`.

- **Required:** Python ≥ 3.10, plus a virtual environment (`venv` or `conda`).
- **Skip if:** you don't use Python.

---

## Optional but recommended

### An IDE / editor that knows about LaTeX and your analysis language

VS Code, Cursor, RStudio, or any modern editor with syntax highlighting for `.tex`, `.do`, `.R`, or `.py`. The workflow doesn't depend on a specific editor; pick whatever you're comfortable with.

### Ghostscript (for the PDF-chunking fallback)

Some long PDFs need to be chunked before feeding them to the `pdf-learnings` skill. Ghostscript provides the fallback path. See [`.claude/references/pdf-chunking.md`](../../.claude/references/pdf-chunking.md) for the recipe.

- **Install:** `brew install ghostscript` (macOS), `apt install ghostscript` (Ubuntu).

---

## Once you've worked through the prerequisites

Come back to [`installation.md`](installation.md) for the workflow-specific install steps, then [`branch-model.md`](branch-model.md) to pick `main` vs `applied-micro` vs `behavioral`, then `first-session.md` (planned for v0.2.x) for a walkthrough.

If you want to verify your environment before forking, the simplest check: open a terminal in any directory, run `claude`, and try `/help`. If that works, you're ready.
