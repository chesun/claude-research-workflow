---
name: tools
description: Utility commands — commit, compile, validate-bib, journal, context-status, deploy, learn. Replaces individual utility skills.
argument-hint: "[subcommand: commit | compile | validate-bib | journal | context | deploy | learn] [args]"
allowed-tools: Read,Grep,Glob,Write,Edit,Bash,Task
---

# Tools

Utility subcommands for project maintenance and infrastructure.

**Input:** `$ARGUMENTS` — subcommand followed by any arguments.

---

## Subcommands

### `/tools commit [message]` — Git Commit

Stage changes, create commit, optionally create PR and merge.

- Run `git status` to identify changes
- Stage relevant files (never stage `.env` or credentials)
- Create commit with descriptive message
- If quality score available and >= 80, note in commit

---

### `/tools compile [file]` — LaTeX Compilation

3-pass compile with bibtex/biber and structured warning report.

**Step 1: detect engine and paths from CLAUDE.md**

- `LaTeX engine:` header → `pdflatex` (default) or `xelatex`
- `Overleaf path:` header → if set, run from that path; else use in-repo `paper/`
- Mode inference: `--paper`/`--talk` flag, or path (`paper/*` vs `talks/*`)

**Step 2: run the 3-pass sequence**

For papers (assume in-repo `paper/` unless Overleaf path is set):

```bash
cd paper && {ENGINE} -interaction=nonstopmode [file].tex
biber [file]                # if preamble uses biblatex
# OR: BIBINPUTS=..:$BIBINPUTS bibtex [file]   # if preamble uses natbib
{ENGINE} -interaction=nonstopmode [file].tex
{ENGINE} -interaction=nonstopmode [file].tex
```

For talks: `cd talks && TEXINPUTS=../preambles:$TEXINPUTS {ENGINE} ...` (3 passes; bibtex/biber if talks cite).

Detect `biber` vs `bibtex` by grepping the preamble for `\usepackage{biblatex}` or `addbibresource`.

**Step 3: parse the log for warnings**

```bash
grep -c "Overfull \\hbox" [file].log
grep -E "undefined (citation|reference)" [file].log
grep "Label(s) may have changed" [file].log    # → re-run if present
```

**Step 4: report**

- Compile: PASS / FAIL (exit code)
- Page count: `pdfinfo [file].pdf | grep Pages`
- Overfull hbox: count + worst (>10pt = critical, 1–10pt = minor)
- Undefined citations / references: list each
- Suggest re-run if "Label(s) may have changed" appeared on the final pass

---

### `/tools validate-bib` — Bibliography Validation

Cross-reference all citation keys against the project's `.bib` file.

**Step 1: locate the bib file**

- Default: `paper/references.bib`. If absent, scan `\addbibresource{}` or `\bibliography{}` in `paper/main.tex`.
- Extract all entry keys: `grep -E "^@\w+\{([^,]+)" [bib] | sed 's/.*{//'`

**Step 2: extract cite keys from source files**

- LaTeX: `grep -oE '\\(cite[tp]?|citeauthor|citeyear|parencite)\{[^}]+\}' paper/**/*.tex talks/**/*.tex` → split comma-separated keys
- Markdown / Quarto (if present): `grep -oE '\[?@([a-zA-Z0-9_:.-]+)' paper/**/*.qmd` → extract key after `@`

**Step 3: cross-reference**

- **Missing:** keys cited but not in `.bib` → CRITICAL
- **Unused:** entries in `.bib` not cited anywhere → informational
- **Near-matches:** Levenshtein distance ≤ 2 between a missing key and a real one → likely typo, flag

**Step 4: entry quality (sampled, top 20 issues)**

- Required fields: `author`, `title`, `year`, plus `journal`/`booktitle`/`publisher`
- Encoding: flag non-ASCII characters that aren't escaped (`{\"o}`, `{\'e}`, etc.)
- Year sanity: 1800 ≤ year ≤ current+1

**Step 5: report**

| Category | Count | Examples |
|---|---|---|
| Missing entries | N | (list keys + first source location) |
| Unused entries | N | (list keys) |
| Near-matches | N | (cited → suggested) |
| Quality issues | N | (key → which field is missing/malformed) |

Save full report to `quality_reports/bib_validation_[YYYY-MM-DD].md` if any issues found.

---

### `/tools journal` — Research Journal

Regenerate `quality_reports/research_journal.md` from quality reports and git history.

- Walk `quality_reports/` for agent reports, extract date + score + verdict
- Cross-reference with `git log` for phase-transition commits
- Append-only: never overwrite existing entries; only add new ones since the last journal update

---

### `/tools context` — Context Status

Show context usage, auto-compact distance, what state will be preserved.

- Read recent message count and approximate token usage
- Check `quality_reports/session_logs/` for the latest entry timestamp
- Confirm `MEMORY.md`, latest plan file, and TODO.md are up to date — if not, prompt to update before compaction

---

### `/tools deploy` — Deploy Guide Site (when present)

Render Quarto guide site and sync to GitHub Pages.

```bash
cd guide && quarto render          # outputs to docs/
git add docs/ && git commit -m "docs: update guide site" && git push
```

Requires `guide/` directory with a Quarto project — universal main does not ship one (deferred). If you build a guide site, this subcommand is the deploy hook.

---

### `/tools learn` — Extract Learnings

Extract reusable knowledge from the current session into memory.

- Look for: non-obvious discoveries, workarounds, multi-step workflows that future sessions would benefit from
- Two-tier routing:
  - Generic / project-relevant → `MEMORY.md` or auto-memory `.claude/projects/.../memory/`
  - Machine-specific (paths, credentials) → `.claude/state/personal-memory.md` (gitignored)

---

## Principles

- **Each subcommand is lightweight.** No multi-agent orchestration.
- **Compile always uses 3-pass.** Ensures references and citations resolve; re-run if "Label(s) may have changed" appears on pass 3.
- **validate-bib catches drift.** Run before commits and submissions.
- **Engine and paths come from CLAUDE.md.** Never hardcode `pdflatex` vs `xelatex` or `paper/` vs Overleaf — read the headers.
