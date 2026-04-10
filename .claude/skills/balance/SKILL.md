---
name: balance
description: Generate balance tables comparing treatment and control groups. Produces LaTeX-ready output with means, differences, p-values, and normalized differences. Supports Stata and R.
argument-hint: "[treatment variable] [--vars var1 var2 ...] [--data path] [--cluster var]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob
---

# Balance Table Generator

Generate publication-quality balance tables comparing treatment and control groups.

**Input:** `$ARGUMENTS` — treatment variable name, optional covariate list, data path, and clustering variable.

---

## What It Produces

A balance table with:
- Column 1: Control group mean (SD)
- Column 2: Treatment group mean (SD)
- Column 3: Difference (T - C)
- Column 4: p-value (or SE of difference)
- Column 5: Normalized difference (Imbens & Wooldridge 2009)
- Bottom row: N for each group
- Joint F-test of all covariates

## Workflow

1. **Read CLAUDE.md** for analysis language (default: Stata)
2. **Read strategy memo** (if exists) for pre-specified covariates and treatment definition
3. **Read `.claude/rules/stata-conventions.md`** for output conventions

### Stata Implementation
```stata
// Balance table skeleton
local covariates [var1 var2 var3 ...]
local treatment [treatment_var]

// Means and SDs by group
estpost tabstat `covariates', by(`treatment') statistics(mean sd count) columns(statistics)

// Difference tests
foreach var of local covariates {
    reg `var' `treatment', vce(cluster `cluster_var')
    // store coefficient, SE, p-value
}

// Joint F-test
reg `treatment' `covariates', vce(cluster `cluster_var')
test `covariates'

// Export via esttab or texsave
```

### R Implementation
```r
# Using modelsummary::datasummary_balance or custom
datasummary_balance(~treatment, data = df, output = "latex")
```

## Output

- `tables/balance_table.tex` — LaTeX table (booktabs, threeparttable)
- Notes include: sample definition, clustering level, significance levels
- Format follows `.claude/references/content-standards.md` table conventions

## Air-Gapped Mode

If Claude cannot run code (air-gapped server):
1. Generate the complete .do file
2. Document expected output structure
3. Include assertions about data structure
4. User runs on server, shares output for formatting
