---
name: tools
description: Utility commands — commit, compile, validate-bib, journal, context-status, deploy, learn, sync-status, propagate, list-consumers. Replaces individual utility skills.
argument-hint: "[subcommand: commit | compile | validate-bib | journal | context | deploy | learn | sync-status | propagate | list-consumers] [args]"
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

### `/tools sync-status` — Storage Sync Status (LFS + DVC + Backup)

One-shot report of bulk-content storage state for the current repo: Git LFS, DVC, and (if configured) periodic Dropbox backup. Run before declaring a session done to catch a forgotten `dvc push`.

**Step 1: Detect which tiers are active**

- LFS: `[ -f .gitattributes ] && grep -q 'filter=lfs' .gitattributes`
- DVC: `[ -d .dvc ]`
- Periodic backup (Class D): check for `~/Dropbox/research-data/<proj>/backup/` or a project-specific manifest

**Step 2: Gather state per tier**

LFS:

```bash
git lfs ls-files | wc -l                  # tracked file count
git lfs ls-files | awk '{print $1}' | sort -u | wc -l   # unique blob count
du -sh .git/lfs/objects 2>/dev/null       # local LFS cache size
git lfs env 2>/dev/null | grep -E "Endpoint|UploadTransfers|DownloadTransfers"
# Bandwidth and storage stats: only available via GitHub web UI / API; if
# `gh` CLI is configured, query the LFS endpoint via `gh api`. Otherwise just
# point user at `https://github.com/<org>/<repo>/settings/lfs`.
```

DVC:

```bash
dvc status                                 # local: any pointers ahead of working tree?
dvc status -c                              # cloud: any pending pushes / pulls?
dvc remote list                            # which remote is configured
ls -lh data/*.dvc data/**/*.dvc 2>/dev/null | wc -l   # pointer count
du -sh "$(dvc config cache.dir 2>/dev/null || echo .dvc/cache)" 2>/dev/null
```

Periodic backup (Class D): `du -sh ~/Dropbox/research-data/$(basename $PWD)/backup 2>/dev/null` and `stat -f %m` on its newest file.

**Step 3: Format output**

```
=== Git LFS ===
Tracked patterns:    [list from .gitattributes]
LFS files in repo:   N files, M MB local cache
Endpoint:            <url>
GitHub usage:        <link to repo settings → LFS for storage/bandwidth>

=== DVC ===
Remote:              <path>
Pending uploads:     N files (run: dvc push)
Pending downloads:   N files (run: dvc pull)
Pointer count:       M files
Cache size:          X MB

=== Periodic Dropbox backup (Class D) ===
Last run:            YYYY-MM-DD HH:MM (or "never")
Mirror size:         X GB
```

**Step 4: Flag actionable items**

If any are non-zero / stale, surface as a numbered action list at the bottom:

- "Run `dvc push` — N files pending upload"
- "Run `git lfs pull` — local LFS cache is empty"
- "Backup is N days stale — run `bin/sync-backup.sh`"

If everything is clean: print "All storage tiers in sync."

Reference: `.claude/rules/data-version-control.md`.

---

### `/tools propagate <pattern>... [--dry-run] [--force-initial] [--only PATHS]` — Workflow Propagation

Sync selected files from this workflow source repo to all configured consumer repos, routed per the file-class manifest. Implementation: `python3 .claude/skills/tools/propagate.py` (~580 LOC, stdlib-only, requires Python 3.11+).

**Class-aware routing.** Every file is read from the branch its class declares as authoritative:

- **Class A — Universal** (default): read from `main`. Hooks, most rules, templates.
- **Class B — Overlay-customized**: read from consumer's overlay branch (`applied-micro` or `behavioral`). E.g., `CLAUDE.md`, `orchestrator.md`, `quality.md`.
- **Class C — Overlay-only**: read from the consumer's overlay if the consumer is on a matching branch; otherwise skipped as "not-applicable". E.g., `strategist.md` (applied-micro) or `designer.md` (behavioral).
- **Class D — Excluded**: never propagates. Project-state files like `quality_reports/`, `MEMORY.md`, `data/`.

The manifest lives at `.claude/file-classes.toml` on `main` (itself Class A so it propagates to overlay worktrees via `/tools sync-overlays`). Default for unlisted files = Class A.

**Step 1: identity check.** Run `python3 .claude/skills/tools/propagate.py --check-identity` first. The script's three identity modes:

- **source** — has `.claude/state/consumers.toml` → propagation runs.
- **consumer** — has `.claude/state/workflow-sync.json` → exits with "run from source" hint.
- **none** — neither file exists → exits with setup instructions.

**Step 2: invoke.** From the workflow source repo:

`python3 .claude/skills/tools/propagate.py [--dry-run] [--force-initial] [--only PATH1,PATH2] PATTERN [PATTERN...]`

Patterns are repo-relative paths or globs:

- `.claude/hooks/context-monitor.py` — single file
- `.claude/rules/*.md` — all rules
- `templates/data-*.md` — globbed templates
- `.claude/skills/tools/SKILL.md` — a single skill file

**Step 3: review output.** Per-consumer report annotates each file with its source branch + class:

- `copied` — files written and committed in this consumer (showing `← branch  [class]`)
- `in-sync` — already matched the source branch's current version (no action)
- `DIVERGENT` — consumer has local edits since last sync; **skipped** to preserve them. User reconciles manually.
- `MISSING-ON-SOURCE` — file's class says read from a branch where the file doesn't exist (anomaly; user investigates).
- `AMBIGUOUS` — file present in consumer but no sync record; skipped unless `--force-initial`.
- `NOT-APPLICABLE` — Class C file for a branch the consumer is not on; correctly skipped.
- `EXCLUDED` — manifest `[exclude]` match; correctly skipped (silent in totals).

Aggregate totals at the bottom.

**Step 4: handle divergent files (if any).** For each consumer where a file was skipped due to divergence, the user must manually reconcile by either accepting the workflow version (overwrite + recommit in that consumer), keeping the consumer's local version (update its `workflow-sync.json` record manually), or three-way merging by hand.

**Common patterns:**

- New hook on workflow → `/tools propagate .claude/hooks/<file>.py`
- Rules sweep → `/tools propagate .claude/rules/*.md`
- New skill → `/tools propagate .claude/skills/<name>/SKILL.md`
- Template change → `/tools propagate templates/<file>`

**Architecture:**

- Registry at `.claude/state/consumers.toml` (TOML, gitignored, hand-maintained).
- Per-consumer state at `.claude/state/workflow-sync.json` (JSON, gitignored, written by the script). Each file's record now carries `class` and `source_branch` fields for traceability.
- File-class manifest at `.claude/file-classes.toml` (tracked, on main, itself Class A).
- All `.claude/state/*` files are gitignored by the universal rule, so they don't propagate to fresh forks of the workflow.

Plans:

- v1 (registry, identity, divergence-skip): `quality_reports/plans/2026-05-06_tools-propagate-plan.md`
- v2 (class-aware routing, manifest, sync-overlays): `quality_reports/plans/2026-05-07_comprehensive-propagation-plan.md`

---

### `/tools list-consumers` — List Configured Consumer Repos

Read-only. Prints the workflow's consumer registry plus each consumer's last-sync state.

```bash
python3 .claude/skills/tools/propagate.py --check-identity
```

Same script, identity-only mode. Useful for quick inspection before a propagate run.

If invoked from a consumer repo, prints that consumer's sync state. From a fresh fork (neither source nor consumer), prints the setup hint.

---

## Principles

- **Each subcommand is lightweight.** No multi-agent orchestration.
- **Compile always uses 3-pass.** Ensures references and citations resolve; re-run if "Label(s) may have changed" appears on pass 3.
- **validate-bib catches drift.** Run before commits and submissions.
- **Engine and paths come from CLAUDE.md.** Never hardcode `pdflatex` vs `xelatex` or `paper/` vs Overleaf — read the headers.
