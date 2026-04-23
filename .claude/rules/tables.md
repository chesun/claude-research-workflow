# Tables: Standards and Prohibited Patterns

**Target:** Publication-quality tables matching AER, QJE, Econometrica formatting.

## Core rules

- **Never embed titles, captions, or notes inside generated `.tex` table files** — no `\caption{}` or embedded notes inside output from R/Stata. Those live in the paper where the table is `\input{}`'d.
- **Table information goes in two places:**
  1. **File name** — descriptive, e.g., `table2_enrollment_ascm.tex`
  2. **LaTeX `\caption{}` and `\begin{tablenotes}`** — added in the paper
- **Generated `.tex` files contain only the tabular content** — the wrapping `\begin{table}`, `\caption`, `\label`, and `\begin{tablenotes}` live in the paper.
- **Use `threeparttable`** in the paper — wrap tables for proper notes alignment.
- **Use `booktabs`** — `\toprule`, `\midrule`, `\bottomrule` only. No vertical lines. `\cmidrule(lr){2-4}` for partial rules spanning column groups.
- **Coefficient display** — point estimate on one row, standard error in parentheses directly below. Stars: `*` p<0.10, `**` p<0.05, `***` p<0.01. Align note at bottom: "Robust standard errors in parentheses" or "Clustered at X level."
- **Human-readable variable names** — `Log wages` not `ln_wage_deflated`; `Female` not `sex_2`; `Years of education` not `educ_yrs`.
- **Fixed effects rows** at the bottom before `\bottomrule`: N, R², FE indicators (Yes/No), Controls (Yes/No).
- **Panels** — italic label `\multicolumn{K}{l}{\textit{Panel A: Full sample}}`, `\midrule` after the panel label, `\\[0.5em]` between panels.

## Preferred R packages

- **`modelsummary`** — primary. Use `output = "latex_tabular"` for bare tabular.
- **`fixest::etable`** — for `fixest` models, with `tex = TRUE` and `style.tex(main = "aer", ...)`.
- **`kableExtra`** — for descriptive tables.

Write output to both `paper/tables/` and `results/tables/`:

```r
writeLines(tex_output, file.path("paper/tables", "reg_main_specification.tex"))
```

## Preferred Stata commands

- **`esttab`** / `estout` — primary for regression tables. Output bare `tabular`.
- **`\begin{threeparttable}` wrapping is added in the paper, not in the `.tex` fragment.**

## File naming

```
tables/
├── descriptive/
│   ├── sumstats_main_sample.tex
│   └── balance_treatment_control.tex
├── estimation/
│   ├── reg_main_specification.tex
│   ├── reg_heterogeneity_gender.tex
│   └── did_event_study_coefficients.tex
└── robustness/
    └── reg_alternative_controls.tex
```

Pattern: `{table_type}_{content}.tex`

- `sumstats_` — summary statistics
- `balance_` — balance / pre-treatment tests
- `reg_` — regression output
- `did_` — difference-in-differences specific tables
- `first_stage_` — IV first stage

## Prohibited patterns

| Pattern | Reason |
|---------|--------|
| Title row inside the table body | Titles go in `\caption{}`, not the table body |
| Notes embedded in table body | Notes go below via `\begin{tablenotes}` in the paper |
| `\hline` | Use `\toprule` / `\midrule` / `\bottomrule` (booktabs) |
| Vertical rules (`\|` in column spec) | Never used in economics journals |
| `stargazer` | Deprecated workflow; use `modelsummary` or `fixest::etable` |
| Raw R/Stata variable names as labels | Human-readable required |
| `xtable` without booktabs | Produces non-journal-quality output |
| `\begin{table}` in R/Stata output | Scripts export bare `tabular`; float wrapper lives in `main.tex` |
