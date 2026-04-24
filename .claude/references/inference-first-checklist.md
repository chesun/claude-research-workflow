# Inference-First Design Checklist (14 Steps)

This is the portable reference version of the checklist. The designer agent reads this file when producing experiment designs. See `quality_reports/plans/2026-03-28_behavioral-plan-v3-hugo-base.md` Section 5 for the full annotated version with citations.

---

## Step 1: Research Question
What causal/behavioral claim are you testing?

## Step 2: Hypotheses (theoretical or empirical)
If formal model: What does the model predict? List each testable prediction.
If no formal model (existence experiment): State the empirical hypothesis, the direction, the comparison, and what would falsify it. Justify the direction from prior evidence, related findings, or intuition.
The requirement is a specific hypothesis with a specific comparison — not a formal model. "Hypothesis-driven, not 'stuff happens'" (Niederle).

## Step 3: Statistical Tests (co-designed with treatments)
For each prediction: exact test, estimand, and null. Steps 3-5 are iterative — your test choices shape your treatment design and vice versa. The goal is to ensure your design can produce the data your tests require.
- Test selection: Moffatt guide (t-test, Mann-Whitney, KS, Wilcoxon, etc.)
- Clustering strategy: session/group level (OLS without clustering → size 0.46)
- Multiple testing correction: Bonferroni, BH, or Romano-Wolf
- Structural estimation if applicable

## Step 4: Data Structure Required
What data do those tests need? (paired, independent, panel, choice lists, belief distributions)

## Step 5: Treatment Arms
- One-factor-at-a-time: each treatment differs on exactly ONE dimension
- Justify each arm: what does comparison of A vs B identify?
- Control for alternative hypotheses (Niederle's 5 strategies)
- Identify background noise sources

## Step 6: Interface & Elicitation
- Elicitation method and WHY (compare: BDM, binary choices, MPL, convex budget, DOSE, survey)
- IC assumption hierarchy: statewise monotonicity (weakest) < S-O reduction < risk-neutral EU (avoid)
- MPL pitfalls: centering bias, multiple switching (16%), reference point effects
- Belief elicitation: Healy & Leo decision tree
- Floor/ceiling risk, focal value response risk (60-70%)
- Measurement error: 30-50% of variance; ORIV or multiple elicitations
- Screen layout mockup

## Step 7: Process Measurement
- ALWAYS collect response time (free, informative)
- Log-transform RT; screen extremes
- Additional measures if needed (mouse-tracking, eye-tracking, SCR)
- Record hardware type

## Step 8: Incentive Design
- Payment structure and IC argument (cite theoretical basis)
- Random round payment: monotonicity assumption
- Stakes comparable across treatments
- Expected payment, range, IRB justification

## Step 9: Subject Comprehension
- Instructions: under 3 pages, pretested with non-experts
- Understanding checks (pre-treatment)
- Attention checks (4 instructional, pre-treatment)
- NEVER drop respondents who fail POST-TREATMENT checks
- Manipulation checks for survey experiments

## Step 10: Timing & Logistics
- Median completion time, time per task
- Session structure, matching protocol
- Randomization method
- Effect persistence: decay to 1/3-1/2 within 1-4 weeks

## Step 11: Power Analysis
- Effect size justified from theory, pilots, or literature
- **For existence experiments (unknown effect size):** flip the question — compute MDE given budget, then argue "is this MDE plausibly smaller than the true effect?" Conservative default: power for 0.3-0.4 SD (100-175 per cell).
- Core formula: n* = 2(t_alpha/2 + t_beta)^2 * (sigma/delta)^2 per arm
- "30 per cell" is debunked — only detects 0.70 SD
- Optimal allocation for unequal variance/costs
- Cluster VIF: 1 + (m-1)*rho
- Covariate adjustment: Lin (2013) estimator — especially important for existence experiments
- Power-boosting: within-subject designs (>=50% fewer subjects), ORIV for noisy measures, always collect RT

## Step 12: Budget & Attrition
- Per-subject payment, platform fees, total budget
- Budget sensitivity: what if N needs +50%?
- Differential attrition planning

## Step 13: Parameter Selection (Snowberg & Yariv 2025)
- Choose based on objective (document irregularity, discriminate models, institutional design, policy)
- Check: flat incentives, corner solutions, misperception robustness, multiple equilibria
- Guard against design-hacking

## Step 14: Pre-Registration Draft
- Coffman & Dreber 7-item PAP structure
- Test hierarchy: primary > secondary > robustness > exploratory
- Replication package requirements
- **Registered Reports strongly recommended for existence experiments** — submit before data collection; journal publishes regardless of results. Eliminates null-result career risk.
- Consider Registered Reports for other high-risk designs as well
