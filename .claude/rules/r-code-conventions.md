# R Code Conventions

**Scope:** `**/*.R`
**Role:** Secondary language (Stata is primary for most analysis; R used for figures, power simulations, specialized econometric packages)

---

## When to Use R

- Publication-quality ggplot2 figures (see `figures.md`)
- Regression tables via `modelsummary`, `fixest::etable`, `kableExtra` (see `tables.md`)
- Specialized DiD estimators: `did` (Callaway-Sant'Anna), `fastdid`, `fixest::sunab`, `did2s`
- RDD: `rdrobust`, `rddensity`
- Synthetic control: `Synth`, `tidysynth`, `augsynth`
- IV bootstrap / wild cluster: `fwildclusterboot`
- Power simulations when Stata is awkward
- Machine learning / text classification

## Reproducibility

- `set.seed()` called ONCE at top of master script (YYYYMMDD format)
- All packages loaded at top via `library()`, not `require()`
- All paths relative to repository root — never `/Users/...`, `/home/...`, `C:\\...`
- Create output directories with `dir.create(..., recursive = TRUE, showWarnings = FALSE)`
- Save heavy computations as `.rds` so downstream scripts don't re-estimate

## Function Design

- `snake_case` naming; verb-noun pattern (`estimate_att`, `plot_event_study`)
- Roxygen-style documentation on non-trivial functions
- Default parameters; no magic numbers
- Return named lists or tibbles (not bare vectors)

## Domain Correctness (Applied Econometrics)

- **Estimand clarity:** ATT vs ATE vs LATE — does the code produce what the paper claims?
- **Clustering:** must match treatment assignment unit, not individual-level.
- **Staggered DiD:** NEVER use TWFE without checking for negative weights / heterogeneous treatment effects.
  - Prefer `did::att_gt()` (Callaway-Sant'Anna), `fastdid`, `fixest::sunab()`, or `did2s`.
  - If TWFE is used, report Goodman-Bacon decomposition or de Chaisemartin-D'Haultfoeuille diagnostics.
- **IV:** always report first-stage F-statistic; flag if < 10; prefer Montiel Olea-Pflueger effective F.
- **RDD:** always run `rddensity::rddensity()` (McCrary) before `rdrobust`; document bandwidth choice.
- **Event studies:** use `fixest::i()` with explicit reference period; check pre-trend coefficients.
- **`did::att_gt()`:** explicitly set `control_group = "nevertreated"` or `"notyettreated"` and document the choice.
- **Standard errors:** `fixest` defaults to appropriate cluster-robust; `lm()` scripts must wrap in `sandwich` or `clubSandwich`.

## Common Pitfalls

| Pitfall | Impact | Prevention |
|---------|--------|------------|
| Missing `bg = "transparent"` in `ggsave()` | White boxes on slides | Always include in `ggsave()` |
| Hardcoded absolute paths | Breaks on other machines | Relative paths only |
| TWFE with staggered DiD + heterogeneous TE | Biased ATT, negative weights | `did` (CS), `fastdid`, or `fixest::sunab()` |
| Clustering at individual when treatment is group-level | SEs too small, over-rejection | Cluster at treatment assignment unit |
| Wild bootstrap not used with few clusters (≤50) | Invalid inference | `fwildclusterboot::boottest()` or `fixest` with `boottest` |
| RDD without McCrary density test | Invalid continuity assumption | Run `rddensity::rddensity()` first |
| Synthetic control without permutation inference | No valid p-values | Run placebo on every donor, compute RMSPE ratios |
| Event-study binning without documentation | Masks pre-trends or dynamics | `fixest::i(rel_time, ref = -1)` with explicit bin-and-label |
| IV with F<10 using standard Wald CI | Size distortion under weak instruments | Report Anderson-Rubin CI or `fixest` tF procedure |
| `lm()` for panel data | Wrong SEs, slow, no FE absorption | `fixest::feols()` for any panel spec |
| `feols(..., se = "cluster")` (deprecated) | May break in future versions | `feols(..., cluster = ~unit)` |
| Missing first-stage report in IV | Referee red flag | Always report and interpret first stage |

## Line Length & Mathematical Exceptions

**Standard:** lines ≤ 100 characters.

**Exception — mathematical formulas** may exceed 100 chars if and only if:

1. Breaking the line would harm readability of the math (influence functions, matrix ops, simulation loops, formula implementations matching paper equations).
2. An inline comment explains the operation:
   ```r
   # Sieve projection: inner product of residuals onto basis functions P_k
   alpha_k <- sum(r_i * basis[, k]) / sum(basis[, k]^2)
   ```
3. The line is in a numerically intensive section (simulation, estimation, inference).

Long lines in non-mathematical code: minor penalty. Long lines in documented mathematical sections: no penalty.

## Code Quality Checklist

- [ ] Packages at top via `library()`
- [ ] `set.seed()` once at top (master script)
- [ ] All paths relative to repo root
- [ ] Functions documented (Roxygen on non-trivial)
- [ ] Figures: `bg = "transparent"`, explicit dimensions, vector format
- [ ] Heavy computations saved as `.rds`
- [ ] Comments explain WHY, not WHAT
