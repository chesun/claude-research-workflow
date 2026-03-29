# Handbook of Experimental Methodology — Learnings

**Date:** 2026-03-28
**Source:** Snowberg & Yariv (eds.), Handbook of Experimental Methodology, Elsevier 2025
**Chapters read:** Ch2 (Preference Elicitation), Ch3 (Belief Elicitation), Ch7 (Survey Experiments), Ch8 (Choice Processes), Ch11 (Replicability)
**Purpose:** Inform designer/designer-critic agents, `/design experiment`, `/qualtrics`, `/preregister` skills

### Chapter Locations

All chapters in `master_supporting_docs/experimental_design/handbook_experimental_methodology/`:

| Chapter | File |
|---------|------|
| Ch1: Evaluating Experimental Designs (Snowberg & Yariv) | `Chapter-1---Evaluating-experimental-designs-----We-are-indebted-t_2025_Handb.pdf` |
| Ch2: Preference Elicitation (Chapman & Fisher) | `Chapter-2---Preference-elicitation--common-methods-and-potenti_2025_Handbook.pdf` |
| Ch3: Belief Elicitation (Healy & Leo) | `Chapter-3---Belief-elicitation--a-user-s-guide-----We-thank-N_2025_Handbook-.pdf` |
| Ch4: Communication in Games | `Chapter-4---Communication-in-games_2025_Handbook-of-Experimental-Methodology.pdf` |
| Ch5: Repeated Games | `Chapter-5---Repeated-games_2025_Handbook-of-Experimental-Methodology.pdf` |
| Ch6: Lab Experiments in Developing Countries | `Chapter-6---Lab-experiments-in-developing-country-contexts-----W_2025_Handbo.pdf` |
| Ch7: Designing Survey Experiments (Huber & Graham) | `Chapter-7---Designing-survey-experiments-----We-thank-Seth-_2025_Handbook-of.pdf` |
| Ch8: Choice Process Measurement (Brocas et al.) | `Chapter-8---The-methods-and-value-of-measuring-cho_2025_Handbook-of-Experime.pdf` |
| Ch9: Experimenting with Networks | `Chapter-9---Experimenting-with-networ_2025_Handbook-of-Experimental-Methodol.pdf` |
| Ch10: Econometrics of Randomization | `Chapter-10---Recent-developments-in-the-econometrics-of-rando_2025_Handbook-.pdf` |
| Ch11: Running Replicable Experiments (Coffman & Dreber) | `Chapter-11---Running-replicable-experim_2025_Handbook-of-Experimental-Method.pdf` |

**Not yet read:** Ch4 (Communication), Ch5 (Repeated Games), Ch6 (Developing Countries), Ch9 (Networks), Ch10 (Econometrics of Randomization)

---

## Ch2: Preference Elicitation (Chapman & Fisher 2025)

### Central Challenge: Measurement Error
- Measurement error accounts for **30-50% of variance** of elicited measures (Gillen et al. 2019)
- Test-retest correlations: 0.2-0.3 for incentivized, ~0.5 for self-assessed
- Different measures of same construct show at best weak correlations
- ORIV correction (Gillen et al. 2019) can recover stronger correlations
- **False positives:** When noisy elicitation is used as control variable, false positive rates approach 100% in large samples

### Method Comparison Table

| Method | # Elicitations | Training | IC | Inconsistency | Framing |
|--------|---------------|----------|-----|---------------|---------|
| Matching (BDM) | 1 | Yes | Yes* | Very High | Low |
| Binary Choices | 20-120 | No | Yes | High | Low |
| MPLs | 2-4 | Yes | Yes | Medium | **High** |
| Convex Budget Sets | 14-45 | Yes | Yes | Medium | Medium |
| Adaptive (DOSE) | 4-10 | No | Yes* | Low | Low |
| Survey Module (quant) | 1 | No | No | n.a. | Low |

### MPL Pitfalls (Critical for Designer-Critic)
- **Multiple switching:** 16% of subjects in Holt-Laury designs (meta-analysis of 63 studies)
- **Centering bias:** Altering position of risk neutrality can REVERSE correlation between cognitive ability and risk aversion
- **Reference point effects:** Fixed element acts as endowment; MPL eliciting probability equivalents vs certainty equivalents produce different risk aversion estimates
- **Recommendation:** MPLs should be symmetric around neutral mid-point

### Adaptive Methods (DOSE — Chapman et al. 2024)
- Bayesian updating after each answer, selects next question to maximize information gain
- 4-10 binary choices sufficient; higher temporal stability and predictive validity
- Key finding: ~50% of U.S. population is "loss tolerant" (contradicts prior lab findings)
- Can be pre-programmed as question tree (avoids real-time computation)

### Dealing with Noise (4 strategies)
1. Careful design: simplify, training rounds, visual aids for probabilities
2. Multiple elicitations + ORIV or averaging
3. Exclude noisy data ex post (comprehension quizzes, pre-registered exclusion criteria)
4. Econometric corrections (MLE/Bayesian with noise parameters)

### Structural Estimation Approaches
- **MLE:** Requires substantial data (120+ choices for individual-level). Optimization may fail with small samples.
- **Bayesian:** Provides estimates for ALL participants even with limited data. Gao et al. (2023): MLE fails for 8-28% of observations even with 80 choices.
- **Finite mixture models:** Classify into types (Bruhin et al. 2019; Fehr et al. 2023 Dirichlet Process Means)
- **Simulation/parameter recovery:** Underused. Generate simulated data, estimate, compare to truth. Low marginal cost.

---

## Ch3: Belief Elicitation (Healy & Leo 2025)

### The 6 Formal Recommendations

1. **USE incentives** but do NOT put incentive details on the decision screen. DO say "truth-telling is optimal."
2. **For beliefs about a number, avoid eliciting the mean** — requires EU assumption. Prefer MODE or MEDIAN.
3. **For beliefs about a frequency, elicit probability of single random draw instead** — converts complex distribution belief to single number.
4. **Consider coarse elicitation** — often a precise probability is unnecessary. Single MPL row at 50% is assumption-free.
5. **For probabilities, use a price list (MPL)** — superior IC (weaker assumptions) to scoring rules.
6. **If using scoring rule, use binarized. Recommend BQSR** — strongest uniform incentives.

### IC Assumption Hierarchy (weakest to strongest)
1. **Statewise Monotonicity** — required by MPL, BDM (weakest, preferred)
2. **S-O Reduction** — required by ALL binarized scoring rules (strictly stronger)
3. **Risk-neutral EU** — required by dollar-denominated scoring rules (strongest, avoid)

### MPL vs BQSR
- MPL: weaker IC assumptions, eliminates hedging, but flatter incentives
- BQSR: strongest incentives (G''=2 everywhere), but requires S-O reduction, does NOT eliminate hedging
- **When participant can influence outcome (effort, performance): use MPL** (eliminates hedging)
- Showing on-screen payoff calculators for BQSR causes significant misreporting (Danz et al. 2022)

### What Can Go Wrong (Designer-Critic Checklist)
1. Risk aversion distortion (dollar scoring rules) — compress reports toward 50%
2. Probability weighting / S-O reduction failure — core vulnerability of binarized rules
3. Hedging — MPL/BDM eliminate it; BQSR does not
4. Calculator display causing misreporting — don't show payoff formulas on decision screen
5. Focal/default reporting without incentives — cluster at 50% and 100%
6. Multiple switch points in MPL — enforce single switch
7. Order effects in MPL — ordering, left-right placement, skewing all matter
8. Ambiguity aversion — binarized rules require probabilistic sophistication
9. Mean elicitation requires EU — does NOT get weak-IC benefit
10. BDM comprehension failure — understanding quiz is critical

### Decision Tree for Mechanism Selection
- **Probability of binary event:** Default MPL. If need stronger incentives: TPL.
- **Beliefs about a number:** Mode (pay-if-true, simplest). Median (quantile MPL). Mean only if necessary.
- **Entire distribution:** Elicit probability of each bin; randomly pick one for payment.
- **Most likely event:** Modal event elicitation (zero assumptions).

---

## Ch7: Survey Experiments (Huber & Graham 2025)

### Treatment Design
- **"Bundle" problem:** Even simple treatments affect outcomes through multiple pathways
- **"Leave one out" approach** (Dafoe et al. 2018): Include all confounding info in ALL arms, vary only factor of interest
- **Active control conditions:** Control must match on confounding dimensions
- **Placebo randomization** (Porter & Velez 2022): Multiple placebos randomized

### Manipulation Checks (3 critical recommendations)
1. Measure outcomes for intended mechanisms (did treatment move beliefs?)
2. Measure outcomes for unintended mechanisms (exclusion restriction check)
3. Test for demand effects (Mummolo & Peterson 2019)

### Outcome Measures
- **Specificity:** Ask about concrete policies with defined parameters, not vague scales
- **Behavioral/costly measures:** Allocate bonus between self/charity, pay for accurate forecasts, sign petitions
- **Persistence:** Effects decay to 1/3-1/2 within 1-4 weeks. Design panel follow-ups.

### Power — Covariate Adjustment
- **Pre-treatment outcome measure** is the single most effective power booster
- **Lin (2013) estimator** guarantees smaller SE than unadjusted
- **CRITICAL: Do NOT drop respondents who fail post-treatment checks** — introduces bias
- Pre-register exact covariate adjustment strategy
- Only control for pre-treatment variables (post-treatment controls introduce bias)

### Attention Checks
- Use 4 pre-treatment instructional checks (Berinsky et al. 2021)
- Mock vignette checks (Kane et al. 2023) mimic experimental stimulus
- Response time screening: limit to pre-treatment questions only (RT is partly post-treatment)
- **Never drop based on post-treatment manipulation checks** (Montgomery et al. 2018)

### Differential Attrition
- Balance time and effort across treatment arms
- Control respondents should read similar-length text about unrelated topic
- Test: regress attrition indicator on treatment indicators
- **Warning:** Survey vendors may obscure breakoff data

---

## Ch8: Choice Processes (Brocas, Camerer, Carrillo & Krajbich 2025)

### Response Time (collect in EVERY experiment)
- RT reflects strength-of-preference: faster = larger utility difference
- Small errors are slow; large errors are fast
- RT can identify decision thresholds, predict choice reversals
- **DDM (Drift-Diffusion Model):** Combining choice + RT yields lower-variance preference estimates
- Log-transform RT for regression analysis
- Screen out very fast (guessing) and very slow (inattention) responses

### Mouse-Tracking
- AUC (area under curve) correlates with risky-choice parameters at r=0.25 (vs r=0.17 for RT)
- Reveals attribute processing latencies and order
- Hardware matters: trackpads produce straighter trajectories than mice
- Record hardware type and control for it

### Mouselab (Eye-Tracking on Budget)
- Information hidden behind opaque boxes; reveals what is attended to
- Tests whether subjects look at opponents' payoffs (strategic reasoning)
- Click-and-hold variant preferred over mouseover

### Practical Decision Matrix
| Want to measure... | Use... | Cost |
|---|---|---|
| Strength of preference | RT or mouse AUC | Free |
| Attribute processing order | Mouse-tracking or eye-tracking | Free-moderate |
| Information search strategy | Mouselab or eye-tracking | Free-moderate |
| Strategic reasoning in games | Mouselab | Free |
| Emotional arousal | SCR (Empatica) | $0.5-2K |
| Cognitive effort | Pupil dilation | Moderate |

### Key Design Principle
**Always collect RT** — it is free and informative. Mouse-tracking and Mouselab are next easiest adds.

---

## Ch11: Replicability (Coffman & Dreber 2025)

### Two Master Precepts
1. "Make sure it's right the first time."
2. "Be very clear and comprehensive in describing everything you did."

### Design-Hacking (Most Nefarious Tool)
- Unreported pilots that tweak design until something "works," then PAP that design
- Gives "overly confident view of robustness and generalizability"
- Every data collection must be decided ahead of time: pilot or real study

### Pre-Analysis Plans — What to Include
1. Experimental design description
2. Inclusion criteria for participants
3. Variables and coding
4. Exact analyses (regression models)
5. Control variables and clustering decisions
6. Test hierarchy: primary > secondary > robustness > exploratory
7. Pilots done (with separate linked PAP)

### Key Finding
- Brodeur et al. (2024): Pre-registration alone does NOT curb p-hacking. Only pre-registration WITH complete pre-analysis plans reduces p-hacking. **More detail = more effective.**

### Power for Replications
- Replication effect sizes are ~75% of originals (Camerer et al. 2018)
- Aim for **90% power to detect 1/2 to 2/3** of original effect size
- "30 per cell" is inadequate — compute from effect size and variance

### Replication Package Requirements
- Raw data (platform exports before cleaning)
- Analysis code that does BOTH cleaning AND analysis
- Extensive comments explaining every step
- "Computational empathy" (Lars Vilhuber): write as if a stranger needs to understand
- ALL top journals now require replication packages (as of July 2024)

### Registered Reports
- Paper submitted with intro, design, hypotheses, analysis — but NO results
- Peer review before data collection
- If accepted, journal publishes regardless of results
- Lead to more null results than normal publications (Scheel et al. 2021)
