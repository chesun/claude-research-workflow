# Journal Profiles

<!--
These profiles calibrate the domain-referee and methods-referee when reviewing
for a specific journal. Each profile describes the journal's review culture
in plain language — the LLM adapts its priorities accordingly.

Used by: domain-referee.md, methods-referee.md (via /review --peer [journal])
-->

## How This Works

When `/review --peer [journal]` is invoked:

1. **Profile found below** → referees calibrate using the full profile
2. **Profile NOT found** → referees use the journal name + domain-profile.md to adapt (still better than generic)
3. **No journal specified** → generic top-field referee behavior

---

## Top-5 General Interest

### American Economic Review (AER)
**Focus:** All fields of economics — the broadest audience
**Bar:** Must interest economists outside your subfield. Big question, clean execution, clear contribution.
**Domain referee adjusts:** "Would a labor economist care about this health paper?" Contribution must be broad. Literature positioning against the *general* frontier, not just subfield. Policy implications welcome but not required — insight is enough.
**Methods referee adjusts:** Identification must be convincing to non-specialists. Clean, transparent design preferred over technically complex one. Standard errors and robustness should be thorough but not excessive.
**Typical concerns:** "Why should economists outside this field care?" "Is the contribution big enough for AER?" "Is this too narrow/specialized?"

### Econometrica (ECMA)
**Focus:** Theoretical and empirical economics with formal rigor
**Bar:** Methodological innovation or empirical work with exceptional identification and formal results.
**Domain referee adjusts:** Theoretical contribution valued highly. If empirical, the design must be near-airtight. Formal welfare analysis expected. Less emphasis on policy narrative, more on economic theory and mechanisms.
**Methods referee adjusts:** Formal proofs or near-formal arguments expected for key results. Asymptotic properties discussed. Novel estimators should have theoretical justification. Simulation evidence for finite-sample properties.
**Typical concerns:** "Where's the formal result?" "What are the asymptotic properties?" "Is this a methods contribution or an applied contribution?"

### Journal of Political Economy (JPE)
**Focus:** All fields — strong emphasis on economic mechanisms and structural thinking
**Bar:** Deep economic insight. JPE values understanding *why* something happens, not just *that* it happens.
**Domain referee adjusts:** Mechanism is king. Reduced-form results alone insufficient — need to explain the economics. Structural models or mechanism tests expected. Theoretical framework (even informal) valued.
**Methods referee adjusts:** Identification strong, but mechanism evidence equally important. Heterogeneity that illuminates the mechanism. Willing to accept some identification imperfection if the economic insight is deep enough.
**Typical concerns:** "What's the mechanism?" "Can you decompose the effect?" "What does this tell us about economic behavior?"

### Quarterly Journal of Economics (QJE)
**Focus:** All fields — prizes compelling narrative and important questions
**Bar:** The question must be important and the answer must surprise. QJE loves papers that change how you think about something.
**Domain referee adjusts:** Narrative matters enormously. The paper should read like a story with a punchline. Broad implications. Creative use of data or setting. "Clever" identification valued.
**Methods referee adjusts:** Identification must be clean and intuitive — not just technically correct, but easy to explain. Transparency and simplicity over complexity. Visual evidence (event studies, RD plots) highly valued.
**Typical concerns:** "Is this surprising?" "Does this change how we think about X?" "Can you explain the identification in one sentence?"

### Review of Economic Studies (REStud)
**Focus:** All fields — technically excellent empirical and theoretical work
**Bar:** Technical quality must be top-tier. Values precision and completeness over narrative.
**Domain referee adjusts:** Thoroughness expected — address every possible objection. Complete set of robustness checks. Careful literature review. Less emphasis on storytelling than QJE, more on completeness.
**Methods referee adjusts:** Every specification must be justified. Full battery of robustness checks expected. Sensitivity analysis (Oster bounds, etc.). Careful treatment of inference. Multiple testing corrections if applicable.
**Typical concerns:** "Have you checked robustness to X?" "What about specification Y?" "The inference needs more care."

---

## Top Field Journals

### American Economic Journal: Applied Economics (AEJ:Applied)
**Focus:** Empirical microeconomics — labor, health, education, development, public
**Bar:** Clean applied micro paper with credible identification and clear results. Slightly below top-5 bar but same rigor expectations.
**Domain referee adjusts:** Contribution should be meaningful to the subfield. Practical policy relevance appreciated. Literature positioning within the subfield, not the general field.
**Methods referee adjusts:** Same identification standards as top-5. Modern estimators expected (no naive TWFE for staggered). Replication package expected.
**Typical concerns:** "Is this incremental relative to [closely related paper]?" "Would this be better in a field journal?"

### American Economic Journal: Economic Policy (AEJ:Policy)
**Focus:** Policy evaluation and design — how policies affect outcomes
**Bar:** Must have direct policy relevance. Natural experiments from actual policy changes preferred.
**Domain referee adjusts:** Policy implications front and center — not an afterthought. Cost-benefit or welfare discussion expected. Institutional details of the policy must be well-documented. Generalizability to other policy contexts.
**Methods referee adjusts:** Identification from actual policy variation (not cross-sectional). Pre-trends must be clean. Heterogeneity by policy-relevant subgroups expected. Back-of-envelope welfare calculations.
**Typical concerns:** "What should policymakers do with this?" "Does this generalize to other states/countries?" "What's the cost-benefit?"

### Journal of Human Resources (JHR)
**Focus:** Labor economics, education, health, demography
**Bar:** Strong empirical contribution with clear policy relevance and careful identification.
**Domain referee adjusts:** Policy relevance matters more than theoretical novelty. External validity — can results inform actual policy? Sample representativeness. Heterogeneity analysis by policy-relevant subgroups expected. Institutional knowledge of labor markets/education systems/health care valued.
**Methods referee adjusts:** Clean identification is non-negotiable. Modern staggered DiD estimators required if applicable. Robustness to functional form. Pre-trends must be clean and shown. Replication package expected at acceptance.
**Typical concerns:** "What's the policy implication?" "Does this generalize beyond your sample?" "Have you considered heterogeneity by [race/gender/income]?"

### Journal of Health Economics (JHE)
**Focus:** Health economics — insurance, utilization, provider behavior, public health
**Bar:** Sound health economics with credible identification. Institutional knowledge of health care systems expected.
**Domain referee adjusts:** Must demonstrate deep understanding of health care institutions. Moral hazard vs. adverse selection distinction matters. Welfare implications expected. Connection to health policy debates. Knowledge of CMS data, insurance markets, provider incentives.
**Methods referee adjusts:** Health-specific threats: selection into insurance, Ashenfelter dip in health utilization, moral hazard confounding. IV exclusion restrictions scrutinized heavily in health contexts. GLM for cost outcomes expected alongside OLS.
**Typical concerns:** "Is this moral hazard or adverse selection?" "Have you addressed selection into treatment?" "What about the Medicaid population specifically?"

### RAND Journal of Economics (RAND)
**Focus:** Industrial organization, regulation, antitrust, health care markets
**Bar:** IO-flavored analysis with market structure or firm behavior component. Structural or quasi-experimental.
**Domain referee adjusts:** Market structure and competition implications. Firm behavior and strategic incentives. Regulatory implications. Welfare analysis (consumer surplus, total surplus) expected.
**Methods referee adjusts:** Structural models valued alongside reduced-form. Demand estimation methods (BLP, discrete choice). Entry/exit models. Merger simulation if relevant. Reduced-form papers need very clean identification.
**Typical concerns:** "What does this imply for market structure?" "Consumer welfare impact?" "Can you do a structural analysis?"

### Journal of Public Economics (JPubE)
**Focus:** Tax policy, public goods, redistribution, government programs
**Bar:** Public finance question with clean identification. Understanding of tax/transfer system mechanics.
**Domain referee adjusts:** Tax incidence, deadweight loss, behavioral responses to taxation. Program evaluation of government interventions. Fiscal federalism. Redistribution and inequality. Knowledge of tax code and transfer programs.
**Methods referee adjusts:** Bunching estimators for tax kinks/notches. RDD at eligibility thresholds. DiD around policy changes. Structural models of labor supply response. Extensive vs. intensive margin effects.
**Typical concerns:** "What's the elasticity?" "Extensive or intensive margin?" "Welfare implications of the tax/transfer change?"

### Journal of Labor Economics (JLE)
**Focus:** Labor markets — wages, employment, human capital, discrimination, immigration
**Bar:** Clean labor economics with careful identification. Understanding of labor market institutions.
**Domain referee adjusts:** Wage determination, employment effects, human capital returns, discrimination, unions, immigration. Mincer equations and labor supply models. Firm-worker matched data valued. Monopsony and market power in labor markets.
**Methods referee adjusts:** Selection correction (Heckman, Lee bounds) when relevant. Decomposition methods for wage gaps. Clean identification of causal effects on wages/employment. Event study designs around job transitions or policy changes.
**Typical concerns:** "Is this a supply or demand effect?" "Selection into employment?" "What about general equilibrium effects?"

### Journal of Development Economics (JDE)
**Focus:** Development economics — poverty, institutions, agriculture, trade in developing countries
**Bar:** Credible empirical evidence on development questions. RCTs or strong quasi-experimental designs. Field knowledge.
**Domain referee adjusts:** Context matters enormously — deep knowledge of the country/region expected. External validity to other developing country settings. Implementation details for interventions. Cost-effectiveness. Sustainability of effects. Gender and equity dimensions.
**Methods referee adjusts:** RCTs: randomization checks, attrition, compliance, spillovers, pre-analysis plan. Quasi-experimental: strong first stage for IV, clean RD, credible parallel trends. Power calculations. Clustered standard errors at appropriate level.
**Typical concerns:** "Does this generalize beyond this specific context?" "What about attrition?" "Cost-effectiveness?" "Long-run effects?"

---

## Strong Field Journals

### Review of Economics and Statistics (RESTAT)
**Focus:** Empirical economics — all fields, emphasis on careful measurement and methods
**Bar:** Technically excellent empirical work. Values careful econometrics and measurement.
**Domain referee adjusts:** Measurement quality is paramount. Novel data or measurement approaches valued. Less emphasis on big-picture narrative than QJE, more on getting the econometrics exactly right. Replication studies welcome.
**Methods referee adjusts:** Highest econometric standards short of Econometrica. Every assumption must be tested or bounded. Sensitivity analysis expected. Careful treatment of standard errors. Pre-registration or pre-analysis plans viewed favorably.
**Typical concerns:** "Is the measurement precise enough?" "Have you tested every assumption?" "What about measurement error in [variable]?"

### AER: Insights
**Focus:** Same breadth as AER but shorter format — important results that can be communicated concisely
**Bar:** AER-quality insight in a shorter paper. Must be self-contained and punchy.
**Domain referee adjusts:** Brevity is a feature, not a limitation. One clean result is enough. No need for 15 robustness checks — the core result must be compelling on its own. Well-suited for striking findings or clever identification.
**Methods referee adjusts:** Core identification must be clean. Fewer robustness checks acceptable given format, but the main result must be robust. Transparency and visual evidence valued.
**Typical concerns:** "Can this be communicated in 10 pages?" "Is the single result compelling enough?" "Does this need a longer format to be convincing?"

---

## Add Your Own Journal

Copy this template and add it above this section:

```markdown
### [Journal Name] ([Abbreviation])
**Focus:** [fields and topics covered]
**Bar:** [what it takes to publish here]
**Domain referee adjusts:** [what matters most to domain reviewers at this journal]
**Methods referee adjusts:** [rigor expectations, preferred methods, required checks]
**Typical concerns:** [common referee questions at this journal]
```
