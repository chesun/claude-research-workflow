# `scripts/R/` — Reproducibility-first analysis template

This directory ships a numbered-script template for **reproducible** data analysis. Every script has one responsibility; all orchestration happens through `00_run_all.R`.

## Conventions

- **Run everything from `00_run_all.R`** — never source mid-pipeline scripts individually unless you're debugging.
- **Paths via [`here::here()`](https://here.r-lib.org/)** — never `setwd()`. The project root is the git repo root.
- **Fixed seed** in every script that uses randomness: `set.seed(20260413)`. Change only with a recorded reason in the session log.
- **`sessionInfo()` written to `scripts/R/_outputs/sessionInfo.txt`** at the end of `00_run_all.R` so reviewers can verify the environment.
- **Outputs to `scripts/R/_outputs/`** — tables (`*.tex`), figures (`*.pdf`, `*.svg`), and RDS snapshots (`*.rds`). Directory is `.gitignore`d in most setups; decide per-project.
- **No hardcoded absolute paths anywhere.** `/review-r` enforces this.
- **Log package versions** either via `renv` (recommended) or a `DESCRIPTION` file at repo root.

## Files

| Script | Responsibility |
| --- | --- |
| `00_run_all.R` | Orchestrator. Sources 01–05 in order, writes `sessionInfo()`, prints timing. |
| `01_load.R` | Read raw data into data frames. No transformations. |
| `02_clean.R` | Type coercion, missingness handling, join logic, derived columns. |
| `03_analyze.R` | Regressions, tests, any model fits. Save results to RDS. |
| `04_tables.R` | Regression tables → `.tex` via `fixest::etable` / `modelsummary`. |
| `05_figures.R` | `ggplot2` figures → PDF + SVG. |

## First-time setup

```r
# From the R console, at the repo root
install.packages(c("here", "renv"))         # minimal bootstrap
renv::init()                                 # capture current package versions
# OR, if you don't want renv, commit a DESCRIPTION with your top-level deps
```

Then run:

```r
source("scripts/R/00_run_all.R")
```

Expected outputs will land in `scripts/R/_outputs/`. Verify with:

```r
list.files("scripts/R/_outputs/")
#> [1] "fig_main.pdf"  "fig_main.svg"  "sessionInfo.txt"
#> [4] "table_main.tex" "results.rds"
```

## Reviewing

`/review-r scripts/R/03_analyze.R` runs the R code-review agent. `/audit-reproducibility` (when shipped) will verify fixed seeds, no absolute paths, sessionInfo capture, and that `00_run_all.R` actually regenerates all outputs.

## Removing this template

Once you have your own analysis, the scripts 01–05 become yours. Delete this README (or rewrite it for your project). Keep `00_run_all.R` — the convention is the part that matters.
