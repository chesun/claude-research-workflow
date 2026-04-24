# Domain Profile: Behavioral & Experimental Economics

## Field

**Primary:** Behavioral Economics, Experimental Economics
**Adjacent subfields:** Decision Theory, Game Theory, Neuroeconomics, Psychology & Economics, Market Design
**Methods:** Lab experiments, online experiments (Prolific, MTurk), survey experiments, field experiments, structural estimation

---

## Target Journals (ranked by tier)

| Tier | Journals |
|------|----------|
| Top-5 | AER, Econometrica, JPE, QJE, REStud |
| Top field | AEJ: Microeconomics, JEBO, Games and Economic Behavior, JEEA |
| Strong field | Management Science, Journal of Risk and Uncertainty, Experimental Economics, Journal of Economic Psychology |
| Good field | Judgment and Decision Making, Journal of Behavioral and Experimental Economics |
| Interdisciplinary | PNAS, Nature Human Behaviour, Cognition, Psychological Science |

---

## Common Data Sources

| Source | Type | Use Case |
|--------|------|----------|
| Lab experiments (own) | Primary | Theory testing, mechanism isolation |
| Prolific / MTurk | Primary | Online experiments, survey experiments |
| oTree | Platform | Lab and online experiment implementation |
| Qualtrics | Platform | Survey experiments, belief elicitation |
| ORSEE / hroot | Recruitment | Lab subject pool management |

---

## Identification Strategies

| Strategy | When Used | Key Assumption |
|----------|-----------|----------------|
| Between-subject randomization | Default for treatment effects | Random assignment |
| Within-subject design | When individual-level variation is key | No order effects (or controlled) |
| Strategy method | Elicit complete strategies | Behavior same as direct response |
| Structural estimation | Recover preference parameters | Correct model specification |

---

## Notation Conventions

| Symbol | Meaning |
|--------|---------|
| u(.) or U(.) | Utility |
| w(p) or pi(p) | Probability weighting |
| r or rho | Risk aversion coefficient (CRRA: u(x) = x^(1-r)/(1-r)) |
| delta | Discount factor |
| beta | Present bias (quasi-hyperbolic: beta*delta^t) |
| lambda | Loss aversion |
| T or D | Treatment indicator |
| Y | Outcome |
| tau or ATE | Treatment effect |
| mu or b | Belief |
| s | Signal |
| theta | Type |
| sigma | Strategy |
| pi | Payoff |

---

## Seminal References (by subfield)

See `.claude/references/seminal-papers-by-subfield.md` for the full list organized by Christina's 11 categories.

---

## Referee Concerns (what behavioral/experimental referees care about)

1. **Design confounds** — does the treatment change exactly one thing?
2. **Demand effects** — are subjects responding to what they think the experimenter wants?
3. **Incentive compatibility** — is the elicitation mechanism IC under reasonable assumptions?
4. **Power** — was the study adequately powered for the claimed effect?
5. **Pre-registration** — was the study pre-registered, and does the analysis match?
6. **Clustering** — are standard errors clustered at the appropriate level?
7. **Comprehension** — did subjects understand the task?
8. **External validity** — do lab/online results generalize?
9. **Multiple testing** — are p-values adjusted for multiple comparisons?
10. **Replication** — would this replicate? Effect size plausible?

---

## Quality Tolerance Thresholds

| Metric | Threshold | Notes |
|--------|-----------|-------|
| p-value | 0.05 (two-sided) | 0.10 acceptable for exploratory |
| Effect size | Report Cohen's d or % of SD | "Statistically significant" alone is insufficient |
| Power | 80% minimum, 90% for replications | At plausible (not just detectable) effect size |
| Clustering | Session/group level default | Individual only if truly independent |
| Decimal places | 3 for coefficients, 2 for summary stats | Never more than 3 |
