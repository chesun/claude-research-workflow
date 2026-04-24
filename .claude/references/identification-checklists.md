# Identification Strategy Checklists

Reference checklists for common causal identification strategies. Used by strategist, strategist-critic, methods-referee, and `/review --identification`.

---

## Difference-in-Differences (Classic)
- [ ] Parallel trends assumption explicitly stated
- [ ] Pre-trend evidence shown (event study plot, formal test, or argued)
- [ ] No-anticipation assumption discussed
- [ ] Treatment timing clearly defined
- [ ] SUTVA / no-spillover addressed if relevant

## Difference-in-Differences (Staggered Adoption)
- [ ] Heterogeneous treatment effects acknowledged as TWFE concern
- [ ] "Forbidden comparisons" (already-treated as controls) avoided or discussed
- [ ] Appropriate estimator chosen:
  - Callaway-Sant'Anna (2021), Sun-Abraham (2021), Borusyak-Jaravel-Spiess (2024), or de Chaisemartin-d'Haultfoeuille
- [ ] Aggregation scheme explicit (simple, group-size weighted, calendar-time, event-time)
- [ ] Never-treated vs. not-yet-treated control group choice justified
- [ ] Negative weights checked/discussed if using TWFE

## Instrumental Variables
- [ ] First-stage F-statistic reported (Montiel Olea-Pflueger effective F preferred)
- [ ] Exclusion restriction argued, not just stated — WHY is it plausible?
- [ ] Independence/relevance assumptions explicitly stated
- [ ] LATE vs. ATE distinction made — who are the compliers?
- [ ] For weak instruments: Anderson-Rubin confidence sets or tF procedure
- [ ] Monotonicity discussed if heterogeneous effects
- [ ] Overidentification test if multiple instruments (Hansen J)

## Regression Discontinuity Design
- [ ] Continuity assumption stated
- [ ] McCrary density test run and reported
- [ ] Bandwidth selection method documented (MSE-optimal via rdrobust, or CER-optimal)
- [ ] Covariate balance at cutoff shown
- [ ] Donut-hole robustness (exclude observations near cutoff)
- [ ] Alternative bandwidth robustness (half, double)
- [ ] Fuzzy vs. sharp distinction clear
- [ ] Local linear preferred; higher polynomial orders justified

## Synthetic Control
- [ ] Pre-treatment fit quality shown (RMSPE or visual)
- [ ] Predictor balance table (treated vs. synthetic)
- [ ] Donor pool composition justified
- [ ] Inference via permutation (placebo-in-space): RMSPE ratios for all donor units
- [ ] No extrapolation (weights between 0 and 1, sum to 1)
- [ ] Sensitivity to donor pool composition tested

## Event Studies
- [ ] Leads and lags specification clear
- [ ] Normalization period explicit (typically t = -1)
- [ ] Pre-event coefficients near zero (parallel trends evidence)
- [ ] Binning of distant endpoints documented
- [ ] Confidence intervals plotted
- [ ] For staggered settings: heterogeneity-robust event study used

## Family / High-Dimensional Fixed Effects
- [ ] Source of identifying variation documented (within-unit, across-time)
- [ ] Singleton observations checked (reghdfe warnings)
- [ ] Multiple FE specifications compared
- [ ] If IV: instrument relevance, first stage F, exclusion restriction

---

## Sanity Check (Mandatory for All Strategies)
- [ ] **Sign:** Does the direction make economic sense?
- [ ] **Magnitude:** Is the effect size plausible? (back-of-envelope)
- [ ] **Dynamics:** Do pre/post coefficients tell a coherent story?
- [ ] **Consistency:** Does the result survive across specifications?

## Robustness Checklist (All Strategies)
- [ ] Alternative sample restrictions
- [ ] Alternative control variables
- [ ] Alternative functional form
- [ ] Alternative SE clustering
- [ ] Placebo / falsification tests
- [ ] Sensitivity bounds (Oster 2019, Rambachan-Roth for DiD)
- [ ] Leave-one-out (drop one unit at a time for aggregate designs)

## Inference Checklist
- [ ] Clustering level justified (matches treatment assignment)
- [ ] Few clusters (≤50): wild cluster bootstrap
- [ ] Very few clusters (≤10): randomization inference
- [ ] Multiple testing correction if many outcomes
- [ ] Conley spatial SEs if geographic spillovers possible
