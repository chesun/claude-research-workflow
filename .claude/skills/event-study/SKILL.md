---
name: event-study
description: Generate event study plots with pre-trends, dynamic effects, and confidence intervals. Supports Stata and R. Handles both classic and staggered DiD event studies.
argument-hint: "[specification] [--staggered] [--data path] [--normalize period]"
allowed-tools: Read,Write,Edit,Bash,Grep,Glob
---

# Event Study Plot Generator

Generate publication-quality event study plots showing pre-trends and dynamic treatment effects.

**Input:** `$ARGUMENTS` — specification details, optional flags for staggered designs.

---

## What It Produces

An event study figure with:
- Pre-treatment coefficients (test parallel trends)
- Post-treatment dynamic effects
- 95% confidence intervals
- Reference period marked (vertical line or dot at zero)
- Horizontal line at zero
- Clear axis labels and title

## Workflow

1. **Read CLAUDE.md** for analysis language (default: Stata)
2. **Read strategy memo** (if exists) for treatment timing, normalization period
3. **Read `.claude/references/identification-checklists.md`** for event study requirements

### Classic DiD (Stata)
```stata
// Event study with reghdfe
reghdfe outcome i.relative_time i.controls, absorb(unit_fe time_fe) vce(cluster cluster_var)
// Or with coefplot
coefplot, keep(*.relative_time) vertical yline(0) xline(normalization_period)
```

### Staggered DiD (Stata)
```stata
// Callaway-Sant'Anna
csdid outcome controls, ivar(unit) time(time) gvar(first_treat) agg(event)
csdid_plot

// Sun-Abraham
eventstudyinteract outcome lead_lag_dummies, cohort(first_treat) control_cohort(never_treated) absorb(unit time) vce(cluster cluster_var)
```

### R Implementation
```r
# fixest with Sun-Abraham
feols(outcome ~ sunab(first_treat, time) | unit + time, data = df, vcov = ~cluster)
iplot()

# did package (Callaway-Sant'Anna)
att_gt <- att_gt(yname = "outcome", tname = "time", idname = "unit", gname = "first_treat", data = df)
aggte(att_gt, type = "dynamic") |> ggdid()
```

## Figure Standards

- Color palette from `.claude/rules/stata-conventions.md` or project .doh
- Confidence intervals as shaded bands or capped error bars
- Pre-treatment coefficients clearly distinguishable
- Reference period at -1 (or as specified)
- Export as both `.pdf` and `.png`
- Output to `figures/` and Overleaf directory

## Checklist (from identification-checklists.md)

Before finalizing, verify:
- [ ] Normalization period explicit
- [ ] Pre-event coefficients near zero
- [ ] Binning of distant endpoints documented
- [ ] CIs plotted (not just point estimates)
- [ ] For staggered: heterogeneity-robust estimator used

## Air-Gapped Mode

If Claude cannot run code:
1. Generate the complete .do file
2. Specify expected figure dimensions and format
3. Include coefplot/graph options for styling
4. User runs on server, shares figure for review
