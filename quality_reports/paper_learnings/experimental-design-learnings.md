# Experimental Design Learnings from Papers

**Date:** 2026-03-28
**Sources:** Croson (2002), List et al. (2011), Niederle (2025), Snowberg & Yariv (2025), Moffatt "Experimetrics"
**Purpose:** Inform design of designer agent, designer-critic agent, `/design experiment` skill, and experiment-design-principles rule
**Priority rule:** When advice conflicts between papers, favor Niederle (2025) — most recent, by a leading experimentalist.

### Source Locations

| Paper | Location |
|-------|----------|
| Croson (2002) | `master_supporting_docs/experimental_design/Croson.pdf` |
| List, Sadoff & Wagner (2011) | `master_supporting_docs/experimental_design/List_Sadoff_Wagner_Optimal_Sample_Design_Experimental_Economics_2011.pdf` |
| Niederle (2025) | `master_supporting_docs/experimental_design/niederle 2025.pdf` |
| Snowberg & Yariv (2025) | `master_supporting_docs/experimental_design/Snowberg_Yariv_2025.pdf` |
| Moffatt, Experimetrics | `master_supporting_docs/experimental_design/experimetrics.pdf` |

---

## 1. Design Principles (Cross-Paper Synthesis)

### The Golden Rules
- **Simplicity above all:** "Only keep what you really need" (Niederle). Strip everything non-essential. A great experiment looks simple and obvious — this does not mean it was easy to design. (Niederle p.14)
- **Hypothesis-driven, not "stuff happens":** Every experiment must test a specific hypothesis against a specific alternative. One-treatment experiments that just observe behavior yield uninterpretable results. (Niederle p.14)
- **Comparative statics > point predictions:** Test relative differences between treatments, not absolute levels. Point predictions are almost always trivially rejectable. (Croson pp.926-927)
- **The "dream outcome" test:** Before designing, ask: what do the ideal data look like? Can they answer the hypothesis? If data differ from expected, what additional treatment would you run? (Niederle p.19)

### Experiment Type Determines Methodology (Roth's Taxonomy via Croson)
| Type | Goal | Validity Focus | Context Level | Subject Pool |
|------|------|----------------|---------------|-------------|
| Theory-testing | Test predictions | Internal | Abstract | Students fine |
| Anomaly investigation | Explore empirical regularity | Internal | Abstract | Students fine |
| Policy testbed | Test proposed policy | External | Contextualized | May need professionals |

### No Deception (Universal Across All Papers)
- Everything in instructions must be true. (Croson pp.940, 944-945)
- Deception spoils the subject pool for all future researchers. (Croson)
- Deception is defined as deviating from what you told participants. Omitting information or being intentionally vague is acceptable. (Niederle pp.19-21)
- If a design requires deception, redesign the experiment.

---

## 2. Treatment Design

### Number and Structure
- **Don't bloat your design:** The number of treatments should be driven by the mechanisms and questions being studied, not by a fixed rule. As a rough guide, 3-6 treatments is typical; more than 6 should split into multiple studies. The key principle is simplicity — include only treatments that are necessary to answer the research question. (Croson p.938, with caveat)
- **One-factor-at-a-time:** Each treatment should differ on exactly ONE dimension from the comparison treatment. Two simultaneous changes = confounded causal interpretation. (Croson pp.938-939)
- **Sample size must be determined by power analysis, not rules of thumb.** The "20-30 per cell" heuristic (Croson p.938) is explicitly debunked by List et al. (2011, p.10) — 30 per cell only detects a 0.70 SD effect at 80% power, which is very large by social science standards. Always compute required N from effect size, variance, and desired power.

### Between vs. Within Subject
- **Default: between-subject** — avoids order effects and demand effects from seeing multiple conditions. (Croson p.939)
- **Within-subject advantage:** At least 50% fewer subjects needed (Moffatt Ch.1). Use when measuring individual-level effects.
- **Within-subject risks:** Subjects may feel compelled to change behavior OR remain consistent across conditions. Must counterbalance order. (Croson p.939)
- **Crossover designs** (half see control-then-treatment, half see treatment-then-control) detect and control for order effects. (Moffatt Ch.1)

### Controlling Alternative Hypotheses (Niederle's Framework)
1. **Design by elimination:** Create a game where your model has no "bite" but background noise is similar. If behavior differs, your model matters. (pp.36-37)
2. **Direct controls:** Change the environment to eliminate a force by design (e.g., provide computation tables to eliminate complexity). Better than measuring and controlling econometrically. (pp.53-54)
3. **Indirect controls:** Measure a nuisance force separately, control econometrically. Hidden assumptions: measurement tool is accurate, econometric model is correct. Different risk elicitation tasks give DIFFERENT orderings of individuals. (pp.49-53)
4. **"Do it both ways":** Find an environment where your model predicts a different direction than the alternative. (pp.56-58)
5. **Stress-testing:** After main result, check auxiliary predictions that should hold if your model is correct. (pp.59-60)

---

## 3. Power Analysis and Sample Size

### Core Formulas (List et al. 2011)

**Equal variance, two-arm:** n* = 2(t_{α/2} + t_β)² × (σ/δ)² per arm
- α=0.05, power=0.80: detect 1 SD → n*=16/cell; 0.5 SD → n*=64/cell; 0.7 SD → n*=30/cell

**Unequal variance:** Optimal allocation ratio = ratio of standard deviations. Arm with higher variance gets more subjects.
- n₁*/n₀* = σ₁/σ₀

**Unequal costs:** n₁*/n₀* = √(c₀/c₁) × (σ₁/σ₀)

**Binary outcomes:** Use formula with p̄ = (p₀+p₁)/2. Equal allocation always optimal under H₀.

**Cluster designs:** Multiply by variance inflation factor: 1 + (m-1)ρ where m=cluster size, ρ=ICC.
- Optimal cluster size: m* = √((1-ρ)/ρ) × √(c_k/c_m)
- First determine m*, then sample as many clusters as budget allows.

### Key Rules of Thumb
- **"30 per cell" is explicitly debunked** — only detects 0.70 SD effect at 80% power. (List et al. p.10)
- Equal allocation wastes 11% of budget at 2:1 SD ratio, 25% at 3:1, 44% at 5:1. (List et al. pp.10-11)
- For multiple contrasts with a baseline: weight baseline group more heavily. With arms {A,B,C} where A is baseline: optimal is {1/2, 1/4, 1/4}. (List et al. pp.15-16)
- For continuous treatment with linear effect: place half at T=0 and half at T_max, NO intermediate points. (List et al. p.15)

---

## 4. Incentive Design

### Core Principles
- **Induced valuation:** Subjects must face payoff structure consistent with the theory. Compensation must respond to choices. (Croson pp.929, 944)
- **Very small incentives can be worse than none** — Gneezy & Rustichini (2000). (Niederle p.9)
- **Payment scheme must be justified theoretically.** Almost half of experimental economics papers don't justify their payment scheme. (Niederle p.60)

### Payment for Repeated Decisions
- **Random round payment** is incentive compatible under a mild monotonicity assumption (Azrieli et al. 2018). But: monotonicity + reduction of compound lotteries = independence axiom. Problematic if studying independence violations. (Niederle p.60)
- **For infinitely repeated games:** Pay the FINAL round, not a random round. (Niederle p.60)
- **Stakes must be comparable across treatments/domains.** Use multiple price lists to calibrate equivalent stakes. (Niederle pp.63-64)

### Incentive Compatibility
- Always provide an incentive compatibility argument for your elicitation method.
- BSR (Binarized Scoring Rule): check Danz et al. (2022) on behavioral incentive compatibility of belief elicitation.
- Binary lottery method (Roth & Malouf 1979) induces risk neutrality but assumes no probability weighting. (Niederle pp.60-61)

---

## 5. Elicitation Methods

### Beliefs
- Beliefs are "notoriously hard to elicit" — they are complex functions. (Niederle p.62)
- **Simplify to binary:** "What is the chance your performance was in the top 50%?" reduces to eliciting a single number. (Niederle p.62)
- **Cross-over mechanism** (Mobius et al. 2022): avoids probability weighting issues AND has no trade-off between performance and belief accuracy. (Niederle p.62)
- **Binarized scoring rule** (Hossain & Okui 2013): Wilson & Vespa (2018) suggest simplified description. (Snowberg & Yariv p.9)

### Risk Preferences
- **CRITICAL WARNING:** Different risk elicitation tasks give different point predictions AND different orderings of individuals. (Niederle p.50; Snowberg & Yariv pp.4-6)
- Risk aversion from certainty equivalents (μ=0.134) is much lower than from choice data (μ=0.40-0.61). (Moffatt Ch.3)
- **Construct validity required:** A measure must have theory-derived testable implications. (Snowberg & Yariv pp.3-4)

### General Measure Evaluation (Snowberg & Yariv's 6 Criteria)
1. **Construct validity** — does it theoretically capture the construct? (Assessable before data collection)
2. **Responsiveness** — do data respond to parameter changes as predicted?
3. **Predictive validity** — does it predict auxiliary outcomes?
4. **Cost** — monetary, time, complexity
5. **Reliability** — consistency across repeated measures (improvable via quasi-repetitions)
6. **Stability** — consistency over longer time horizons (least critical)

### Focal Value Response
- Participants cluster at top, bottom, and middle of response ranges. In some tasks 60-70% of responses are focal. (Snowberg & Yariv pp.16-17)
- Diagnose via responsiveness checks — do focal responses shift when parameters change?
- Not automatically problematic — may reflect genuine type clustering.

---

## 6. Background Noise and Demand Effects

### Sources of Background Noise (Niederle pp.30-36)
1. **Randomizing participants** — confusing instructions or overly difficult tasks generate random behavior mistaken for meaningful
2. **Floor/ceiling effects** — making one option artificially costly steers choices without the model being the cause
3. **Framing/instructions** — emphasizing certain aspects, using specific examples, naming games (e.g., "community game" vs. "wall street game")

### Demand Effects (Croson pp.930, 938, 940)
- Authority relationship, instructions suggesting "correct" behavior, quiz examples hinting at desired responses
- **Mitigation:** Neutral instructions, unbiased quizzes (use abstract examples), induced valuation, post-experimental questionnaires
- **Quiz design:** Use different scales than the experiment, balance across spectrum of possible decisions

### Instructions
- **2-3 pages maximum.** Pretest with non-experts. (Croson p.938)
- Pretesters must answer: What decision am I making? How do I make it? Where do I record it? What are the possible outcomes?
- **Default to abstract/context-free framing** for theory-testing. Context only when purpose requires it (policy testbed). (Croson pp.929-930)

---

## 7. Parameter Selection (Snowberg & Yariv Framework)

### Choose Parameters Based on Objective
| Objective | Parameter Rule |
|-----------|---------------|
| Document irregularity | Maximize distance from benchmark behavior |
| Discriminate models | Maximize distance between model predictions |
| Institutional design | Maximize welfare vs. status quo |
| Policy evaluation | Echo real-world parameters |

### Parameter Pitfalls
- **Flat incentives:** Parameters maximizing model discrimination may create flat reward functions, reducing reliability. (Snowberg & Yariv pp.24-26)
- **Misperception robustness:** Choose parameters where optimal behavior is robust to small perception errors. (Snowberg & Yariv pp.25-26)
- **Corner solutions:** Avoid parameters where optimal actions are near 0 or 1 — noise compresses responses toward center, making behavior appear suboptimal. (Snowberg & Yariv pp.25-26)
- **Multiple equilibria:** If equilibrium isn't unique, any test introduces a confounding coordination problem. (Snowberg & Yariv p.19)

### G-Hacking Warning (Niederle pp.24-29)
- Selecting games/parameters via piloting while presenting results "as if" randomly drawn
- **30%+ of common ratio experiments use Kahneman & Tversky (1979) parameters** — effects are smaller or reversed at other parameters
- **Mitigation:** Randomly select parameters from a specified set, use canonical environments, be transparent about selection

---

## 8. Statistical Methods for Experiments (Moffatt)

### Test Selection Guide
| Design | Data Type | Test | Stata Command |
|--------|-----------|------|---------------|
| Between-subject | Continuous, normal | t-test (unequal var) | `ttest y, by(g) unequal` |
| Between-subject | Continuous, non-normal | Mann-Whitney | `ranksum y, by(g)` |
| Between-subject | Distribution comparison | Kolmogorov-Smirnov | `ksmirnov y, by(g)` |
| Between-subject | Discrete | Epps-Singleton | `escftest y, group(g)` |
| Within-subject | Continuous, normal | Paired t-test | `ttest WTA=WTP` |
| Within-subject | Continuous, non-normal | Wilcoxon signed-rank | `signrank WTA=WTP` |
| Within-subject | Any | Sign test | `signtest WTA=WTP` |

### CLUSTERING IS CRITICAL
**OLS without clustering has size 0.46** — you "find" a significant effect 46% of the time even when none exists. (Moffatt Ch.2)

| Approach | Actual Size (target: 0.05) |
|----------|---------------------------|
| OLS no clustering | **0.46** |
| OLS cluster at subject | 0.15 |
| OLS cluster at group/session | 0.07 |
| Multi-level model (xtmixed) | 0.08 |

**Rules:**
1. Always cluster at the **highest possible level** (session/group, not subject)
2. Multi-level model (`xtmixed`) is the best framework for between-subject designs
3. Within-subject designs: all approaches perform well except OLS without clustering

### Structural Estimation
- **CRRA utility:** U(x) = x^(1-r)/(1-r). Estimate via custom MLE (`ml` command).
- **Heterogeneous agents:** r ~ N(μ, σ²). Back out from MPL switch points via interval regression or probit.
- **Social preferences:** CES utility via NLS (`nl`), conditional logit (`asclogit`) for discrete choices.
- **Finite mixture models:** When subjects have different behavioral processes (not just different parameters). Use `fmm` or custom `ml` with `d0` evaluator.
- **Three data types determine estimator:** Binary → probit/logit; Interval → `intreg`; Continuous → normal MLE; Censored → Tobit.

---

## 9. Pilot Studies

### Legitimate Uses (Niederle pp.21-22)
- Testing for floor/ceiling effects
- Confirming environment has necessary properties (task is effort-elastic)
- "Variance is your friend" — ensure treatments aren't too attractive or unattractive

### Dangers
1. **Ambiguous pilot** → temptation to chase "side results" on underpowered sample
2. **"Successful" pilot** → anchoring to that design, reluctant to abandon even if better design exists
3. **"Failed" pilot** → leads to repeated pilots = g-hacking

### Recommendation (Niederle takes priority)
- Niederle: "I almost never run designated pilots." Pilots are more valuable in field experiments than lab.
- If you run a pilot: know exactly what you're testing, don't anchor to the design if a better one exists, and don't chase "side results" on underpowered data.
- Pilots are for debugging the experiment (instructions, timing, comprehension), not for generating data or confirming hypotheses. (Croson p.924)
- **Note for behavioral plan:** The "pilot first" design principle should be understood as "pilot when needed for debugging," not "always pilot before every study." Simple, well-understood paradigms may not need pilots.

---

## 10. Pre-Registration (Niederle's Nuanced View, pp.65, 69-70)

- **Pre-registration (broad: goal, design, N, main hypothesis) has no real downside.**
- **Pre-analysis plans (detailed: exact specifications, tables, figures) are costly** for young researchers: increase pre-testing (g-hacking risk), may discourage novel designs, may stifle innovation.
- **Important distinction:** The behavioral plan's mandatory pre-registration gate is about pre-registration, not necessarily a rigid pre-analysis plan. The gate ensures hypotheses and primary analysis are specified before data collection, while allowing flexibility for exploratory analyses.
- Lab experiments naturally have limited p-hacking risk (few variables, obvious analysis)
- **What matters more than pre-registration:** Replications and extensions in different settings; a vibrant literature that routinely tests robustness

---

## 11. Common Objections and Rebuttals (Croson pp.942-943)

| Objection | Rebuttal |
|-----------|---------|
| "Just a lab game" (external validity) | If theory fails in controlled lab, it fails in noisy real world |
| "Students aren't real people" | Students ARE real people; often less biased than professionals |
| "Stakes too low" ($10-20) | Empirically, few differences between high and low stakes |
| "Lab ≠ field behavior" | Behaviors and associations in lab closely resemble field (Snowberg & Yariv p.14) |

---

## 12. Synthesized Checklist for `/design experiment`

### Pre-Design
- [ ] What specific hypothesis are we testing? What is the alternative?
- [ ] What type of experiment? (Theory test / Anomaly / Policy testbed)
- [ ] What does the "dream outcome" look like?
- [ ] Has this been tested before? (Check existing experimental evidence)

### Statistical Design (INFERENCE-FIRST)
- [ ] For each prediction: specify exact test, estimand, and null BEFORE designing treatments
- [ ] What data structure do those tests need?
- [ ] Power analysis: effect size assumption (justified), sample size, MDE
- [ ] Multiple hypothesis testing correction method specified

### Treatment Design
- [ ] Number of treatments driven by research question (not a fixed rule); each differing on exactly one dimension
- [ ] Between-subject (default) or within-subject (with counterbalancing)?
- [ ] Background noise control treatment included?
- [ ] For each alternative hypothesis: elimination game, direct control, or "do it both ways"?

### Elicitation & Interface
- [ ] Every elicitation choice documented with justification and evidence
- [ ] Floor/ceiling risk analysis for bounded variables
- [ ] Focal value response risk assessed
- [ ] Construct validity confirmed for all measures

### Incentives
- [ ] Payment tied to decisions, consistent with theory
- [ ] Incentive compatibility argument (cite theoretical basis)
- [ ] Expected average payment calculated
- [ ] Stakes comparable across treatments/domains

### Subject Experience
- [ ] Instructions: 2-3 pages, pretested, neutral framing
- [ ] Understanding checks with exclusion criteria
- [ ] No deception of any kind
- [ ] Demand effects audit: do instructions suggest "correct" behavior?

### Parameters
- [ ] Parameters chosen to maximize relevant objective (discrimination, distance from benchmark)
- [ ] Robust to small misperceptions? Away from corner solutions?
- [ ] Unique equilibrium under these parameters?
- [ ] G-hacking check: can you justify parameter selection?

### Logistics
- [ ] Matching protocol consistent with theory (strangers vs. partners)
- [ ] Randomization of subjects to treatments
- [ ] Privacy: private payment, anonymous data
- [ ] Clustering plan: cluster at session/group level

### Pre-Launch
- [ ] Pilot plan (if needed): what specifically will it test?
- [ ] Pre-registration drafted
- [ ] Budget: per-subject × N × platform fees; sensitivity to 50% increase
- [ ] Stress-test plan: what auxiliary predictions will be checked?
