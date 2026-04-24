# Domain Profile: Applied Microeconomics

## Field
- Primary: Applied Microeconomics
- Subfields: Peer Effects & Social Interactions, Education Economics, Immigration Economics, Labor Economics
- Methods: Treatment Effects (DiD, IV, RDD, Synthetic Control), Panel Data Methods

## Target Journals (by tier)
- **Top-tier:** AER, Econometrica, JPE, QJE, REStud, REStat
- **Top Field:** AEJ:Applied, AEJ:Policy, JHR, JLE, Journal of Public Economics
- **Strong Field:** Education Finance and Policy, Economics of Education Review, Journal of Population Economics, Labour Economics
- **Policy:** JPAM, RSF

## Common Identification Strategies
- Family fixed effects with within-unit variation
- Difference-in-differences (staggered and standard)
- Instrumental variables (2SLS with high-dimensional FE)
- Synthetic control (single treated unit)
- Regression discontinuity (sharp and fuzzy)
- Shift-share / Bartik instruments

## Field Conventions
- Report exact p-values (not just stars)
- Cluster standard errors at appropriate level (document why)
- Balance tables for treatment vs. control
- Event study plots for DiD
- Multiple hypothesis testing correction when many outcomes
- Sensitivity analysis (Oster bounds, Rambachan-Roth)
- Replication package required (AEA Data Editor standards)
- Pre-analysis plan encouraged for prospective studies

## Key References — Peer Effects
- Figlio et al. (2024) "Diversity in Schools" ReStud
- Sacerdote (2001), Hoxby (2000), Angrist & Lang (2004)
- Lavy, Silva & Weinhardt (2012), Figlio & Ozek (2019)

## Key References — Immigration & Education
- Amuedo-Dorantes & Lopez (2015, 2017), East et al. (2023)
- Dee & Murphy (2020), Bellows (2019, 2021)

## Key References — Methods
- Callaway & Sant'Anna (2021), Sun & Abraham (2021)
- de Chaisemartin & d'Haultfoeuille (2020)
- Abadie, Diamond & Hainmueller (2010, 2015)
- Oster (2019), Rambachan & Roth (2023)

## Notation Conventions
- Treatment: D or T; Outcome: Y; Effect: τ or β
- Fixed effects: α (individual), γ (time), δ (unit×time)
- Instrument: Z; First stage: π
- Peer exposure: E or X_peer; Family: f; School: s; Grade: g; Cohort: t

## Field-Specific Referee Concerns
- "What is the source of identifying variation?"
- "Can you rule out selection into treatment?"
- "Are parallel trends plausible? Show the event study."
- "What about spillovers / SUTVA violations?"
- "How do you handle compositional changes / selective attrition?"
- "Single-event case study — external validity?"
- "Long follow-up period — confounding events?"
