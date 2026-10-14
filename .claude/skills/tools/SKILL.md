---
name: tools
description: Utility commands — commit, compile, validate-bib, context-status, deploy, learn, sync-status, normdiff, cite-check, stata-sweep. Replaces individual utility skills.
argument-hint: "[subcommand: commit | compile | validate-bib | context | deploy | learn | sync-status | stata-sweep | normdiff | cite-check] [args]"
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

### `/tools sync-status` — Storage Sync Status (git, LFS, DVC, backup)

One-shot report of the current repo's storage state. Run it before declaring a session done.

```bash
py -I bin/sync_status.py [REPO] [--hooks-dir DIR]
```

It reports, and lists as numbered actions:
- commits not on the upstream (`git push` / `git pull`), a branch with no upstream (`git push -u`), or an upstream that was never fetched. A detached HEAD or a repo with no remote is UNVERIFIED, not "in sync";
- LFS files in unpushed commits when Git LFS's own pre-push hook does not run. That happens when `core.hooksPath` replaces `.git/hooks`, as on a machine with git guards. `git push` alone would then not upload them, so the action is `git lfs push <remote> <branch>` first;
- files committed as plain blobs although an LFS rule routes them to LFS, from any `.gitattributes` (nested ones too), `info/attributes` or a macro (they show as modified with no content change; the action is `git add --renormalize`);
- DVC changes not yet pushed (`dvc status -c`), when `.dvc/` exists;
- the periodic backup's newest file and size, if `~/Dropbox/research-data/<repo>/backup/` exists.

Verdict and exit code: PASS (0) all in sync; FAIL (1) actions listed; UNVERIFIED (3) a tier is configured but cannot be checked here (for example `.dvc/` with no `dvc` CLI, or LFS rules with no `git-lfs`); 2 usage.

Whether the LFS pre-push hook runs is read from the active hooks folder's `pre-push` (comments ignored). Not reported: GitHub's LFS storage and bandwidth quotas (see the repository's Settings → LFS), the LFS endpoint, and backup staleness by path. With the `dvc` CLI present, `dvc status -c` takes DVC's lock briefly.

Reference: `.claude/rules/data-version-control.md`.

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

