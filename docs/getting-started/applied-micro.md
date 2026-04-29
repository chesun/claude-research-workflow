# The applied-micro overlay

This page covers what the `applied-micro` overlay branch adds beyond `main` — the identification-strategy tooling for observational-data research (DiD, IV, RDD, synthetic control, matching).

If you haven't picked a branch yet, see [`branch-model.md`](branch-model.md) for the decision tree. This page assumes you've checked out `applied-micro`.

---

## What the overlay adds

Three skills, two agents, one rule, two references. The skills are the user-facing surface; the others are infrastructure the skills draw on.

### Skills

- **`/strategize`** — designs the identification strategy or pre-analysis plan
- **`/balance`** — generates publication-quality balance tables comparing treatment and control groups
- **`/event-study`** — generates event-study plots with pre-trends and dynamic effects

### Agents

- **`strategist`** — produces strategy memos covering design choice, estimand, assumptions, robustness plan, falsification tests, and anticipated referee objections
- **`strategist-critic`** — adversarial reviewer that runs four sequential phases: claim identification, design validity, inference soundness, polish

### Rule and references

- **`.claude/rules/air-gapped-workflow.md`** — conventions for projects on restricted-access servers (TERC, FSRDC, etc.) where Claude can't see raw data or execute code. Defines what Claude can work with (variable names, summary stats, codebooks, exported .do files, log files) and what it can't.
- **`.claude/references/identification-checklists.md`** — per-strategy pre-flight checklists used by `strategist`, `strategist-critic`, `methods-referee`, and `/review --identification`
- **`.claude/references/domain-profile-applied-micro.md`** — domain calibration for applied-micro field (notation, conventions, common identification strategies)
- **`.claude/references/journal-profiles-applied-micro.md`** — target-journal calibration (deduction weights for AER, QJE, JPE, etc.)

---

## `/strategize` — identification-strategy memo

The most distinctive applied-micro skill. Two modes: `strategy` (default — design memo) and `pap` (pre-analysis plan).

### What it produces

In strategy mode, the strategist agent produces a memo with:

1. **Design choice** — DiD / IV / RDD / synthetic control / matching, with rationale
2. **Estimand** — what causal parameter you're after (ATT, ATE, LATE, etc.)
3. **Assumptions** — explicit list of what must hold for the design to identify the estimand
4. **Comparison group** — who serves as the counterfactual and why
5. **Pseudo-code** — implementation sketch in Stata or R
6. **Robustness plan** — ordered list of checks with rationale per check
7. **Falsification tests** — what should *not* show effects if the design is valid
8. **Referee objection anticipation** — top 5 anticipated objections with responses

The strategist-critic then runs four phases:

- *Phase 1: Claim identification.* What design? What estimand? Treatment/control well-defined?
- *Phase 2: Core design validity.* Assumption checks, sanity checks (sign, magnitude, dynamics)
- *Phase 3: Inference soundness.* Clustering, multiple testing, weak instruments
- *Phase 4: Polish and completeness.* Robustness, citations, exposition

Up to three rounds before escalation per the workflow's three-strikes convention.

### Output

- `quality_reports/strategy_memo_<topic>.md` — the memo
- `quality_reports/strategy_memo_<topic>_review.md` — the critic's review

### When to invoke

- Starting a new project: `/strategize "How does X affect Y?"`
- Stress-testing an existing strategy: `/strategize` with the path to your draft strategy section
- Drafting a pre-analysis plan: `/strategize pap` with a research spec

### Underlying provenance

Per-strategy rigor draws on [`.claude/references/identification-checklists.md`](../../.claude/references/identification-checklists.md), which encodes the workflow's per-design pre-flight checks: classic DiD (parallel trends + no-anticipation), staggered DiD (TWFE diagnostics, choice between Callaway–Sant'Anna / Sun–Abraham / Borusyak–Jaravel–Spiess / de Chaisemartin–d'Haultfœuille), IV (first-stage F via Montiel Olea–Pflueger preferred, exclusion-restriction argument required), RDD (McCrary density test, bandwidth choice), synthetic control (donor pool, permutation inference), and matching (overlap/common-support, balance after match).

That checklist file is the source of truth for what `/strategize` asks about. Read it before invoking the skill if you want to know what to expect.

---

## `/balance` — balance tables

Generates publication-ready treatment-vs-control balance tables.

### What it produces

A table with:

- Column 1: Control mean (SD)
- Column 2: Treatment mean (SD)
- Column 3: Difference (T – C)
- Column 4: p-value (or SE of difference)
- Column 5: Normalized difference (per Imbens-Wooldridge convention)
- Bottom row: N for each group
- Joint F-test of all covariates

LaTeX-ready output, suitable for `\input{}` into a paper. Stata or R output depending on `CLAUDE.md`'s primary-language setting.

### Workflow

The skill reads (1) `CLAUDE.md` for analysis language, (2) the strategy memo for pre-specified covariates and treatment definition, and (3) `.claude/rules/stata-code-conventions.md` (or `r-code-conventions.md`) for output conventions. Then dispatches the `coder` + `coder-critic` pair to write and review the script.

### When to invoke

After `/strategize` produces a memo with pre-specified covariates, run `/balance <treatment_var> --vars <covariate_list>` to generate the actual table. The skill argument-hint shows the supported flags.

---

## `/event-study` — event-study plots

Generates event-study figures showing pre-trends and dynamic treatment effects. Supports both classic and staggered DiD.

### What it produces

A figure with:

- Pre-treatment coefficients (testing parallel trends)
- Post-treatment dynamic effects
- 95% confidence intervals
- Reference period marked (vertical line at zero)
- Horizontal line at zero for visual baseline
- Clean axis labels and (paper-style) caption

Vector PDF output (`bg = "transparent"` for transparent slides), per `.claude/rules/figures.md`.

### Workflow

For classic DiD: standard fixed-effects regression with `i.relative_time` interaction, often using `reghdfe` in Stata or `feols` in R. For staggered DiD: dispatches to one of the modern estimators (`csdid`, `did_multiplegt`, `eventstudyinteract` for Sun–Abraham, etc. in Stata; `did::att_gt`, `fixest::sunab`, `fastdid`, `did2s` in R) based on the strategy memo's design choice and `r-code-conventions.md`'s preferences.

The skill reads `.claude/references/identification-checklists.md` for the event-study requirements (reference period, normalization, expected pre-trend behavior, what to do when pre-trends fail).

### When to invoke

After `/strategize` and after the data are cleaned. Pass `--staggered` if your design has variable treatment timing.

---

## The applied-micro overlay's special situation: air-gapped data

Some applied-micro projects use restricted-access data — TERC, FSRDC, IPUMS-USA Confidential, state administrative data, etc. The data lives on a server Claude cannot SSH into; raw data and intermediate `.dta` files never leave the server.

`.claude/rules/air-gapped-workflow.md` covers this: Claude works with what's exportable (variable names, summary stats, codebooks, exported `.do` files, log files) and is explicit about what's not (raw data, ability to execute scripts). The convention: edit `.do` files locally with Claude's help, upload to the server via SSH/SFTP, execute remotely, export results back.

If you don't work with restricted data, the rule is dormant — it has no effect on regular projects. If you do, read it before starting; the constraints shape what's worth asking Claude for.

---

## What about `/analyze`?

`/analyze` is universal (it's on `main` too) and works for applied-micro projects. The applied-micro overlay's contribution is specialized identification tooling on top of generic data analysis — `/analyze` produces analysis scripts; `/strategize` designs the strategy that those scripts implement; `/balance` and `/event-study` are specialized analyses that fit naturally with the strategy.

A typical applied-micro session uses all four:

1. `/discover` — research-spec phase
2. `/strategize` — identification strategy memo
3. `/analyze` — main estimation
4. `/balance` and `/event-study` — supplementary analyses called out in the strategy memo
5. `/write` — paper sections drafted from approved code output
6. `/review` — peer-review simulation
7. `/submit` — final gate before journal submission

---

## Cross-references

- [`branch-model.md`](branch-model.md) — picking the right branch
- [`first-session.md`](first-session.md) — typical-first-day walkthrough (universal; complement to this overlay-specific page)
- [`../concepts/appropriate-use.md`](../concepts/appropriate-use.md) — why applied-micro work can lean on the workflow more than novel behavioral work
- [`../reference/skills.md`](../reference/skills.md) — full skill catalogue including the applied-micro overlay skills
- [`../reference/agents.md`](../reference/agents.md) — strategist + strategist-critic in the agent table
- The actual rule and reference files: [`.claude/rules/air-gapped-workflow.md`](../../.claude/rules/air-gapped-workflow.md), [`.claude/references/identification-checklists.md`](../../.claude/references/identification-checklists.md)
