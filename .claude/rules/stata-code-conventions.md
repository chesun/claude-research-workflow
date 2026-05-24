# Stata Code Conventions

**Paths:** `**/*.do`, `**/*.doh`

## Version
- Server may use Stata 18 with older package versions — flag compatibility concerns

## Invocation (local machine)
- **Always invoke as `stata17` from the command line** — `stata17 -b do file.do` for batch runs.
- **Never call binaries inside `/Applications/Stata/StataMP.app/...` directly.** That path is the older Stata MP 14 install on this machine; both versions ship a binary literally named `StataMP` / `stata-mp` inside their respective `.app` bundles, so a direct path call to `/Applications/Stata/...` silently picks Stata 14.
- `stata17` is the version-pinned alias on PATH (typically `~/.local/bin/stata17 → ~/Documents/stata/StataMP.app/Contents/MacOS/stata-mp`). The unqualified `stata-mp` resolves to the same binary on this machine but is ambiguous in principle; prefer `stata17`.
- See `.claude/skills/stata/SKILL.md` for full Stata reference, including documentation lookup, language essentials, and common pitfalls.

## Project Structure
- **Master file:** `mainscript.do` or `main.do` — runs all do files via `do ./do/filename.do`
- **Settings:** `settings.do` — globals for paths, machine-specific via `c(hostname)` branching
- **Helpers:** `.doh` extension — included via `include` (preserves local macros)
- **Naming:** `01_clean.do`, `02_analysis.do`, `03_figures.do` (numbered order)
- **Subdirs:** `clean/`, `share/`, `learn/`, `helpers/`

## Required Packages
reghdfe, estout, coefplot, ivreghdfe, palettes, cleanplots, egenmore, regsave, cdfplot, binscatter, binscatter2

When new package used: save `[LEARN:stata] New package: name — purpose` to MEMORY.md.

## Code Style
- `local` for within-file constants; `global` only in settings.do
- `cap log close _all` and `set more off` at top of master
- `preserve`/`restore` for temporary manipulation; `tempfile` for intermediates
- `set seed` once in main.do (reproducibility)
- `log using` for every analysis do file
- Never overwrite raw data

## Table Export
- `texsave` for manual tables; `esttab`/`estout` for regression tables
- Output to both local folder AND Overleaf directory
- Format: `tostring var, force format(%10.3f) replace`
- Stars: manual `replace coef=coef+"*" if pval<.05` or esttab options

## Figures
- `graph export` with `.pdf` and `.png`
- Color palette in `.doh` file; opacity locals: `opmax`, `ophigh`, `opmed`, `oplow`
- `binscatter`/`binscatter2` for binned scatter plots

## Regression
- `reghdfe` for OLS with high-dimensional FE
- `ivreghdfe` for IV with high-dimensional FE
- `regsave` for saving results to datasets
- Cluster SEs at appropriate level (document why)

## Comment Safety (greedy `/*` parser bug)

Stata's parser counts `/*` opens **greedily** regardless of comment context. A path-glob like `prepare/*` inside any comment — `/* ... */` block, `*`-prefixed line, or `//`-prefixed line — silently opens a nested block comment that swallows downstream code. Symptoms: scripts log "end of do-file" with zero "file saved" messages; downstream pipelines fail when an expected output is missing. Full diagnosis and 8-variant taxonomy: `master_supporting_docs/stata-block-comment-bug-field-guide.md`.

**Rule 1 — Wildcards in comments.** Inside any comment context, do not use `*` as a path-glob wildcard. Use `<x>` (or `<file>`, `<filename>`) as the placeholder. The sequence `/*` is reserved for legitimate block-comment opens.

| Before (bug) | After (fixed) |
|---|---|
| `$logdir/*` | `$logdir/<x>` |
| `prepare/*` | `prepare/<x>` |
| `do/**/*.do` | `do/<x>/<x>.do` |

**Rule 2 — Banner discipline.** For decorative section dividers, use `* ----------------------------------------`, `// ----------------------------------------`, or `*****************************************` (no slash before the asterisks). Avoid `//*****...` — Stata parses it correctly (the `//` opens a line comment), but the `/*` substring trips naive grep-balance checks and adds cognitive load when reading the file. The state-machine sweep tool recognizes the V7 banner pattern and treats it as benign, so legacy `//*****` banners do not need to be retroactively rewritten — this rule applies to new code.

**Rule 3 — Commit-time balance check.** For every modified `.do` / `.doh` file: `grep -c '/\*' <file>` must equal `grep -c '\*/' <file>`. Imbalance guarantees the bug. Use `python3 .claude/skills/tools/stata_sweep.py --check` for an accurate state-machine balance (filters Variant-7 banners and string-literal `/*` digraphs that inflate the naive count); see `.claude/skills/tools/SKILL.md` § stata-sweep.

The PreToolUse hook `.claude/hooks/stata-comment-balance-check.py` enforces Rule 1 and Variant-8 detection at edit time. Rule 2 (banner discipline) is advisory — flagged by coder-critic on new code, not blocked by the hook.
