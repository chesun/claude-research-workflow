---
name: stata
description: "Use this skill when working with Stata code, .do files, .doh files, .dta datasets, or any statistical analysis task involving Stata. Triggers on: mentions of Stata, do-files, .dta files, regression commands (reghdfe, areg, logit, ologit, probit), Stata packages (esttab, estout, outreg2, asdoc, coefplot), data cleaning in Stata (gen, replace, merge, reshape, collapse, egen), Stata graphics (twoway, graph export, scheme), or requests to look up Stata syntax or documentation. Also use when the user mentions running batch analysis, debugging macro expansion, or working with panel/time-series data in a Stata context. Even if the user doesn't say 'Stata' explicitly, trigger if the code patterns are clearly Stata (backtick-quote macro syntax, forvalues/foreach loops, global/local macros)."
---

# Stata

Help the user write, debug, and run Stata code for research and data analysis.

## What is Stata

Stata is a statistical software package widely used in economics, epidemiology, and social sciences. It uses `.do` files (executable scripts) and `.doh` files (reusable helpers included via `include` or `do`). Data is stored in `.dta` format — one rectangular dataset in memory at a time. Stata supports both interactive use and batch execution from the terminal.

## Invocation: always call `stata17`

**Always invoke Stata as `stata17` from the command line.** Do NOT call binaries inside `/Applications/Stata/StataMP.app/...` directly — that path is reserved for an older Stata installation on this machine and `StataMP.app` is a name shared across versions.

`stata17` is the canonical command for all batch and scripted Stata work in this workflow. It is the explicit, version-pinned alias and resolves to Stata MP 17 (`~/Documents/stata/StataMP.app/Contents/MacOS/stata-mp` via `~/.local/bin/stata17`). The unqualified `stata-mp` also resolves to the same binary on this machine, but `stata17` is preferred because it is unambiguous.

If `stata17` is not on PATH on a given machine, set it up once:

```bash
ln -sf ~/Documents/stata/StataMP.app/Contents/MacOS/stata-mp ~/.local/bin/stata17
```

(Adjust the source path if Stata MP 17 is installed elsewhere; ensure `~/.local/bin` is on PATH.)

## Looking Up Documentation

The Stata manuals are large PDFs — never read them whole. Use `pdfgrep` to search and `pdfplumber` to extract only the relevant pages. See `references/doc_lookup.md` for the full workflow and manual-to-topic cheat sheet.

## Running Do-Files

### Batch mode (from terminal)
```bash
stata17 -b do /path/to/file.do      # produces .log file, no GUI
stata17 -q -b do file.do            # -q suppresses header; -e exits on error
```

### From within Stata (interactive or in a do-file)
```stata
do "path/to/file.do"       // run another do-file
include "path/to/file.doh" // include a helper (executes in current context)
run "file.do"              // run without echoing commands
```

Log files from batch runs appear next to the `.do` file with `.log` extension.

## Language Essentials

### Macros
```stata
local x = 5              // local macro (current scope only)
global path "C:/data"    // global macro (persists across do-files)
display `x'              // use local with backtick + single-quote
display "$path"          // use global with dollar sign
```

### Loops
```stata
forvalues i = 1/10 {
    display `i'
}
foreach var of varlist price mpg weight {
    summarize `var'
}
foreach name in "alice" "bob" {
    display "`name'"
}
```

### Data Manipulation
```stata
use "file.dta", clear
keep if condition
drop if condition
gen newvar = expression
replace var = value if condition
egen mean_x = mean(x), by(group)
```

### Merging and Reshaping
```stata
merge 1:1 id using "other.dta"
merge m:1 group using "lookup.dta"
drop if _merge != 3         // keep matched only

reshape wide value, i(id) j(time)
reshape long value, i(id) j(time)
```

### Regression
```stata
reg y x1 x2, robust
areg y x1 x2, absorb(group) robust
reghdfe y x1 x2, absorb(group year) vce(cluster id)
logit y x1 x2, robust
ologit y x1 x2, robust
margins x1, post           // note: overwrites e() — extract what you need first
```

### Output and Tables
```stata
log using "output.log", replace text
// ... commands ...
log close

export excel using "table.xlsx", replace firstrow(variables)

// Common table export packages
esttab using "table.rtf", cells("count(fmt(%9.0f)) mean(fmt(%3.1f))") replace
estpost tabstat varlist, stat(N mean) by(group) columns(statistics)
asdoc tabulate var, save(output.doc) replace
outreg2 using "table.tex", replace
```

### Graphics
```stata
twoway (scatter y x) (lfit y x), legend(order(1 "Data" 2 "Fit"))
graph export "figure.png", replace width(1600)
coefplot (m1, msymbol(O)) (m2, msymbol(D)), drop(_cons) baselevels label xline(0)
```

### Debugging
- `set trace on` / `set trace off` — step through macro expansion
- `set tracedepth 2` — limit trace depth
- `di _rc` after a failed command — check return code
- `assert condition` — halt if condition fails
- `describe`, `codebook var`, `tab var, mi` — inspect variables
- `list in 1/5` — view first 5 rows

## Common Patterns and Pitfalls

### Post-estimation
`margins, post` overwrites `e()` — extract sample sizes, `levelsof`, and anything else you need from the regression **before** calling `margins, post`.

### String handling in macros
Compound quotes `` `" "' `` are needed when macro contents contain quotes:
```stata
local ylabels `"`ylabels' `yval' "`label'""'
```

### Preserve/restore for plotting datasets
When you need to build a plotting dataset from estimation results:
```stata
preserve
clear
set obs N
// ... build plotting data from matrices ...
// ... create graph ...
restore
```

### esttab with estpost tabstat
When using `estpost tabstat` with `by()`, group-level counts are stored as `count` not `N`:
```stata
estpost tabstat varlist, stat(N mean) by(group) columns(statistics)
esttab . using "table.rtf", cells("count(fmt(%9.0f)) mean(fmt(a3))") replace
```

## Instructions

When helping with Stata:
1. Always read the relevant `.do` or `.doh` file before suggesting modifications
2. Prefer editing existing files over creating new ones
3. Follow the project's existing conventions (check CLAUDE.md and settings.do)
4. When running Stata in batch mode via Bash, **always invoke as `stata17`** — never call `/Applications/Stata/StataMP.app/...` directly (that path is the older Stata MP 14 install on this machine)
5. To look up command syntax, use `pdfgrep` + `pdfplumber` — see `references/doc_lookup.md`
6. When writing new code, match the style of the existing codebase (indentation, variable naming, comment style)
7. Be cautious with commands that modify data in place (`replace`, `drop`, `recode`) — confirm intent before applying
