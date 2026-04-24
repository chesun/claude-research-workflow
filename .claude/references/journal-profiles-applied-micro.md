# Journal Profiles: Applied Microeconomics

<!--
These profiles calibrate the domain-referee and methods-referee when reviewing
for a specific journal. Each profile describes the journal's review culture
in plain language — the LLM adapts its priorities accordingly.

Based on Hugo Sant'Anna's journal-calibrated referee system (clo-author),
adapted for applied micro with education/immigration additions.

Used by: domain-referee, methods-referee, applied-micro-referee (via /review --peer [journal])
-->

## How This Works

When `/review --peer [journal]` is invoked:

1. **Profile found below** → referees calibrate using the full profile
2. **Profile NOT found** → referees use the journal name + domain-profile.md to adapt
3. **No journal specified** → generic top-field referee behavior (AEJ:Applied level)

---

## Top-Tier

### American Economic Review (AER)
**Focus:** All fields of economics — the broadest audience
**Bar:** Must interest economists outside your subfield. Big question, clean execution, clear contribution.
**Domain referee adjusts:** "Would a labor economist care about this health paper?" Contribution must be broad. Literature positioning against the *general* frontier, not just subfield. Policy implications welcome but not required — insight is enough.
**Methods referee adjusts:** Identification must be convincing to non-specialists. Clean, transparent design preferred over technically complex one. Standard errors and robustness should be thorough but not excessive.
**Typical concerns:** "Why should economists outside this field care?" "Is the contribution big enough for AER?" "Is this too narrow/specialized?"

### Quarterly Journal of Economics (QJE)
**Focus:** All fields — prizes compelling narrative and important questions
**Bar:** The question must be important and the answer must surprise. QJE loves papers that change how you think about something.
**Domain referee adjusts:** Narrative matters enormously. The paper should read like a story with a punchline. Broad implications. Creative use of data or setting. "Clever" identification valued.
**Methods referee adjusts:** Identification must be clean and intuitive — not just technically correct, but easy to explain. Transparency and simplicity over complexity. Visual evidence (event studies, RD plots) highly valued.
**Typical concerns:** "Is this surprising?" "Does this change how we think about X?" "Can you explain the identification in one sentence?"

### Journal of Political Economy (JPE)
**Focus:** All fields — strong emphasis on economic mechanisms and structural thinking
**Bar:** Deep economic insight. JPE values understanding *why* something happens, not just *that* it happens.
**Domain referee adjusts:** Mechanism is king. Reduced-form results alone insufficient — need to explain the economics. Structural models or mechanism tests expected. Theoretical framework (even informal) valued.
**Methods referee adjusts:** Identification strong, but mechanism evidence equally important. Heterogeneity that illuminates the mechanism. Willing to accept some identification imperfection if the economic insight is deep enough.
**Typical concerns:** "What's the mechanism?" "Can you decompose the effect?" "What does this tell us about economic behavior?"

### Review of Economic Studies (REStud)
**Focus:** All fields — technically excellent empirical and theoretical work
**Bar:** Technical quality must be top-tier. Values precision and completeness over narrative.
**Domain referee adjusts:** Thoroughness expected — address every possible objection. Complete set of robustness checks. Careful literature review. Less emphasis on storytelling than QJE, more on completeness.
**Methods referee adjusts:** Every specification must be justified. Full battery of robustness checks expected. Sensitivity analysis (Oster bounds, etc.). Careful treatment of inference. Multiple testing corrections if applicable.
**Typical concerns:** "Have you checked robustness to X?" "What about specification Y?" "The inference needs more care."

### Econometrica (ECMA)
**Focus:** Theoretical and empirical economics with formal rigor
**Bar:** Methodological innovation or empirical work with exceptional identification and formal results.
**Domain referee adjusts:** Theoretical contribution valued highly. If empirical, the design must be near-airtight. Formal welfare analysis expected. Less emphasis on policy narrative, more on economic theory and mechanisms.
**Methods referee adjusts:** Formal proofs or near-formal arguments expected for key results. Asymptotic properties discussed. Novel estimators should have theoretical justification. Simulation evidence for finite-sample properties.
**Typical concerns:** "Where's the formal result?" "What are the asymptotic properties?" "Is this a methods contribution or an applied contribution?"

### Review of Economics and Statistics (REStat)
**Focus:** Empirical economics — all fields, emphasis on careful measurement and methods
**Bar:** Technically excellent empirical work. Values careful econometrics and measurement.
**Domain referee adjusts:** Measurement quality is paramount. Novel data or measurement approaches valued. Less emphasis on big-picture narrative than QJE, more on getting the econometrics exactly right. Replication studies welcome.
**Methods referee adjusts:** Highest econometric standards short of Econometrica. Every assumption must be tested or bounded. Sensitivity analysis expected. Careful treatment of standard errors. Pre-registration or pre-analysis plans viewed favorably.
**Typical concerns:** "Is the measurement precise enough?" "Have you tested every assumption?" "What about measurement error in [variable]?"

---

## Top Field

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

### Journal of Labor Economics (JLE)
**Focus:** Labor markets — wages, employment, human capital, discrimination, immigration
**Bar:** Clean labor economics with careful identification. Understanding of labor market institutions.
**Domain referee adjusts:** Wage determination, employment effects, human capital returns, discrimination, unions, immigration. Mincer equations and labor supply models. Firm-worker matched data valued. Monopsony and market power in labor markets.
**Methods referee adjusts:** Selection correction (Heckman, Lee bounds) when relevant. Decomposition methods for wage gaps. Clean identification of causal effects on wages/employment. Event study designs around job transitions or policy changes.
**Typical concerns:** "Is this a supply or demand effect?" "Selection into employment?" "What about general equilibrium effects?"

### Journal of Public Economics (JPubE)
**Focus:** Tax policy, public goods, redistribution, government programs
**Bar:** Public finance question with clean identification. Understanding of tax/transfer system mechanics.
**Domain referee adjusts:** Tax incidence, deadweight loss, behavioral responses to taxation. Program evaluation of government interventions. Fiscal federalism. Redistribution and inequality. Knowledge of tax code and transfer programs.
**Methods referee adjusts:** Bunching estimators for tax kinks/notches. RDD at eligibility thresholds. DiD around policy changes. Structural models of labor supply response. Extensive vs. intensive margin effects.
**Typical concerns:** "What's the elasticity?" "Extensive or intensive margin?" "Welfare implications of the tax/transfer change?"

---

## Strong Field

### Education Finance and Policy (EFP)
**Focus:** Education policy with quantitative evidence — school finance, teacher effectiveness, accountability
**Bar:** Education-focused, policy-relevant, credible identification
**Domain referee adjusts:** Deep knowledge of education institutions expected (school districts, accountability systems, teacher labor markets). Practitioner relevance valued alongside identification. State/district policy context must be well-documented.
**Methods referee adjusts:** Standard applied micro identification expectations. Admin data (state education records) common and expected. Value-added models, school/teacher FE, regression discontinuity at policy cutoffs.
**Typical concerns:** "What does this mean for school districts?" "Implementation feasibility?" "How does this interact with accountability policy?"

### Economics of Education Review (EER)
**Focus:** Economics of education — broader than EFP, international scope
**Bar:** Solid education economics, somewhat lower bar than EFP or JHR but still requires credible identification
**Domain referee adjusts:** Contribution to education literature specifically. International contexts welcome. Less emphasis on US policy specifics. Human capital formation, returns to education, school choice.
**Methods referee adjusts:** Standard identification required but slightly more tolerance for observational designs with careful controls. Instrumental variables common.
**Typical concerns:** "Is this a meaningful contribution to the education literature?" "External validity?"

### Journal of Population Economics
**Focus:** Demographics, migration, family economics — solid identification
**Bar:** Population/demographic economics with credible identification
**Domain referee adjusts:** Immigration mechanisms, fertility decisions, family structure, intergenerational mobility. Knowledge of demographic data sources. Population composition effects.
**Methods referee adjusts:** Careful treatment of compositional changes and selection. Instrumental variables for migration decisions. Cohort analysis.
**Typical concerns:** "Selection into migration?" "Compositional effects vs. behavioral effects?" "Generalizability across demographic contexts?"

### Labour Economics
**Focus:** European-leaning labor economics
**Bar:** Solid labor economics, international scope
**Domain referee adjusts:** European labor market institutions valued. International comparisons welcome. Minimum wage, unemployment insurance, active labor market policies.
**Methods referee adjusts:** Standard identification. European admin data common.
**Typical concerns:** "How does this relate to European labor market institutions?" "Cross-country comparisons?"

---

## Policy

### JPAM (Journal of Policy Analysis and Management)
**Focus:** Policy evaluation and design — interdisciplinary
**Bar:** Policy evaluation with credible design. Welcomes interdisciplinary approaches.
**Domain referee adjusts:** Implementation details matter. Cost-effectiveness analysis expected. Policy recommendations should be actionable. Audience includes policy practitioners, not just academics.
**Methods referee adjusts:** Credible identification required. Some tolerance for quasi-experimental designs that aren't airtight if the policy question is important enough. Mixed methods welcome.
**Typical concerns:** "What should policymakers do?" "Cost-effectiveness?" "Implementation feasibility?" "Equity implications?"

### RSF: Russell Sage Foundation Journal
**Focus:** Social science research on inequality, immigration, labor
**Bar:** Social significance, interdisciplinary appeal
**Domain referee adjusts:** Inequality and social stratification lens. Immigration, race, class. Interdisciplinary audience (sociology, political science, economics). Narrative accessibility for non-economists.
**Methods referee adjusts:** Credible identification valued but audience is broader. Clear presentation of methods for non-specialists.
**Typical concerns:** "Social significance?" "Implications for inequality?" "Accessible to sociologists?"
**Note:** Special issues — check call for papers

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
