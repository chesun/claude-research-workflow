---
name: tools
description: Utility commands — commit, compile, validate-bib, context-status, deploy, learn, sync-status, propagate, list-consumers. Replaces individual utility skills.
argument-hint: "[subcommand: commit | compile | validate-bib | context | deploy | learn | sync-status | propagate | list-consumers | stata-sweep | normdiff | cite-check] [args]"
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
find . -name '*.dvc' -not -path './.git/*' -not -path './.dvc/*' | wc -l  # pointer count (path-agnostic)
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

### `/tools sync-overlays [--dry-run] [--force]` — Pull Class A Updates from Main to Overlay Branches

Push Universal-class file updates from `main` into the `applied-micro` and `behavioral` overlay worktrees. Solves the parallel-history conflict that blocks naive cherry-picking. Implementation: `python3 .claude/skills/tools/sync_overlays.py` (~250 LOC, stdlib-only, requires Python 3.11+).

**Scope.** Only Class A (Universal) files are touched. Class B (overlay-customized) and Class C (overlay-only) files are NEVER overwritten — those live on the overlay by design. The class lookup uses the same `.claude/file-classes.toml` manifest as `/tools propagate`.

**Worktree assumption.**

```
~/github_repos/claude-code-my-workflow                          (main)
~/github_repos/claude-code-my-workflow-applied-micro            (applied-micro worktree)
~/github_repos/claude-code-my-workflow-behavioral               (behavioral worktree)
```

If a worktree is missing, the script prints the `git worktree add` command to create it.

**Behavior per file (per overlay).**

| Overlay state | Default (no `--force`) | `--force` |
|---|---|---|
| File absent | Copy from main, stage as new | Same |
| File matches main | No-op | No-op |
| File differs from main | **Skip + warn** (preserves intentional out-of-band edits) | Overwrite + stage as updated |

The default behavior preserves any out-of-band edits the user has made directly on an overlay. Pass `--force` only when you know the overlay version is stale-of-main (e.g., during the Phase D bootstrap, where the bootstrap audit identified the exact files to overwrite).

**Pre-flight.** sync-overlays refuses to run on a worktree with uncommitted changes. Commit or stash before invoking.

**Step 1: dry-run.** From the main worktree:

```bash
python3 .claude/skills/tools/sync_overlays.py --dry-run
```

Reports proposed changes per overlay: counts of new files, in-sync files, and divergent files (which would be skipped without `--force`). No commits made.

**Step 2: apply.** Once the dry-run looks right:

```bash
python3 .claude/skills/tools/sync_overlays.py            # safe mode
python3 .claude/skills/tools/sync_overlays.py --force    # overwrite divergent files (use sparingly)
```

One commit per overlay listing the propagated Class A files. No git push — user pushes overlay branches separately when ready.

**Output annotations.**

- `+` — new file added to overlay
- `~` — overwrote a stale-of-main file (only with `--force`)
- `!` — divergent, skipped (use `--force` to overwrite, or accept the overlay's version as intentional)

Plan: `quality_reports/plans/2026-05-07_comprehensive-propagation-plan.md` §5.

---

### `/tools normdiff [--check] FILE` — Evidence-Gating Normalized-Content Diff

Compute the normalized-content diff of a research-artifact file vs its `HEAD` baseline — the Tier-1 evidence check of the evidence-gating discipline (`.claude/rules/adversarial-default.md`; design of record `quality_reports/reviews/2026-05-28_whole-picture-critic-gates-dispatch.md` §7). Strips comments/scaffold/blank lines and path-tokenizes, then reports any residual analysis/content change (Stata/R/Python/LaTeX). Implementation: `python3 .claude/skills/tools/normdiff.py`; shared logic `.claude/hooks/normdiff_lib.py`.

- default — prints the residue (added/removed/reordered normalized lines) vs `HEAD`.
- `--check` — exits nonzero if residue is non-empty (clean refactor = exit 0).

The always-on PostToolUse recorder `evidence-gate-recorder.py` uses the same lib to silently record a `no-logic-change` row to the verification ledger on every research-artifact edit (scope: `paper/ talks/ scripts/ replication/ figures/ tables/ preambles/`); this subcommand is the manual / orchestrator entry point to the same check.

### `/tools cite-check <citation>...` — Tier-2 Citation Existence Check

Resolve a Tier-2 evidence citation (`file[:line-or-range][:test_id]`) — the existence-check half of the evidence-gating discipline's Tier-2 enforcement (`.claude/rules/adversarial-default.md`; detail `.claude/references/evidence-gating-detail.md`; design of record `quality_reports/reviews/2026-05-28_whole-picture-critic-gates-dispatch.md` §7). A locatable-judgment verdict ("goal X achieved") must carry a structured `{claim, artifact_citation, sufficiency_argument}`; this confirms the cited *artifact* resolves — file exists, any cited line / range is in the file, and any named test runs and passes — so a *fabricated* artifact is caught mechanically (the critic still judges sufficiency). Implementation: `python3 .claude/skills/tools/cite_check.py`; shared logic `.claude/hooks/citation_existence_lib.py`.

- Format: `scripts/01_clean.do:47` (file+line), `scripts/01_clean.do:40-52` (range), `tests/test_x.py:88:test_foo` or `tests/test_x.py::test_foo` (named test).
- Exit codes: `0` RESOLVED (or ASSUMED, with a printed note); `1` MISSING (file/line absent or test failed).
- **MISSING vs ASSUMED:** a missing file / out-of-range line / failed test is **MISSING** (a real fabrication signal). Infra-absence only — no test runner for the file type, toolchain absent — is **ASSUMED** (fail-open, exit 0), never MISSING.
- **Security:** the citation is untrusted input. Paths are resolved repo-relative and must stay inside the repo (`..` traversal / absolute / symlink-escape rejected → MISSING); test ids must match a safe-identifier whitelist; tests run via a fixed per-extension runner with `shell=False` and an argv list — the citation never reaches a shell.

### `/tools stata-sweep [--check | --fix] [--root PATH] [--diff] [--json] [FILE ...]` — Stata Greedy-`/*` Bug Sweep

Detect and fix the Stata greedy-`/*` parser bug across a codebase. Background: `master_supporting_docs/stata-block-comment-bug-field-guide.md` (8-variant taxonomy). Implementation: `python3 .claude/skills/tools/stata_sweep.py` (~280 LOC, stdlib-only, requires Python 3.11+). Shared state-machine logic in `.claude/hooks/stata_comment_lib.py`.

**Modes.**

- `--check` (default) — walks the tree, classifies each `.do`/`.doh` file, reports counts. No mutations.
- `--fix` — mutates AUTO-FIXABLE files in place. MANUAL-ATTENTION files are **never** mutated.

**Classification (per file).**

- **CLEAN** — pre-sweep balanced from Stata's perspective AND sweep would make no structural changes (V4 flatten, V5 orphan strip, V1/V2/V3/V6 path-glob rewrites). Pure Variant-7 banner files are CLEAN — the `//*****` form is parser-safe and the sweep would only do cosmetic `// *****` rewrites.
- **AUTO-FIXABLE** — sweep can safely produce a balanced post-state. The file has V1/V2/V3/V4/V5/V6 issues that the three-pass algorithm resolves.
- **MANUAL-ATTENTION** — sweep **cannot** safely auto-fix. Two causes: (a) Variant-8 corruption artifacts present (e.g., `^[\\s*=\\-]*[\\-=]{3,}<x>$` patterns from a buggy round-2-equivalent fix tool); (b) unmatched `/*` open with no reachable `*/` anywhere (developer forgot the close). Sweep `--fix` reports these but does NOT mutate.

**Exit codes.**

| Code | Meaning |
|---|---|
| 0 | All files CLEAN |
| 1 | At least one AUTO-FIXABLE file found (`--check`) or fixed (`--fix`) |
| 2 | At least one MANUAL-ATTENTION file found (subsumes 1) |
| 3 | Parse / IO error |

**Key invariants.**

- Balance is computed via state-machine walker, **not** naive `grep -c '/\\*'`. The naive grep inflates 7×–14× on real codebases due to V7 banners and string-literal `/*` digraphs.
- Both the depth-counted matcher and the inner rewriter use path-glob predicates (`is_path_glob_open`, `is_path_glob_close`) — Variant-8 prevention. The workflow port starts at Round 3 from day one (no round-1 narrow-regex or round-2 over-flatten bugs).
- String literals are preserved verbatim — Stata strings can contain anything.
- Idempotent by construction: `sweep_text(sweep_text(text)[0])[0] == sweep_text(text)[0]`.

**Examples.**

```bash
# Walk a project, report counts only (no mutations)
python3 .claude/skills/tools/stata_sweep.py --check --root ~/github_repos/my_project

# Fix all AUTO-FIXABLE files (MANUAL-ATTENTION skipped)
python3 .claude/skills/tools/stata_sweep.py --fix --root ~/github_repos/my_project

# Check specific files
python3 .claude/skills/tools/stata_sweep.py --check scripts/01_clean.do scripts/02_analyze.do

# Machine-readable output for CI
python3 .claude/skills/tools/stata_sweep.py --check --json --root .
```

**Opt-in commit-time enforcement.** A reference pre-commit hook ships at `templates/git-hooks/pre-commit-stata-balance`. Install per repo:

```bash
cp templates/git-hooks/pre-commit-stata-balance .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Rule and convention cross-references.**

- `.claude/rules/stata-code-conventions.md` § Comment Safety — Rule 1 (no `*` glob in comments; use `<x>` placeholder), Rule 2 (banner discipline), Rule 3 (commit-time balance check).
- `.claude/agents/coder-critic.md` § 10b — deduction rows for unbalanced state-machine balance (-25), V8 artifacts (-25), path-glob in comment (-5/occurrence, cap -25), `//*****`-style banner (-3/occurrence, cap -10).
- `.claude/hooks/stata-comment-balance-check.py` — PreToolUse hook that uses the same library to block edits introducing the bug going forward.

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
