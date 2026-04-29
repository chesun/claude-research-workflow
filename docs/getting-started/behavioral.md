# The behavioral overlay

This page covers what the `behavioral` overlay branch adds beyond `main` — the experimental-design and formal-theory tooling for lab, online, and theoretical work.

If you haven't picked a branch yet, see [`branch-model.md`](branch-model.md). This page assumes you've checked out `behavioral`.

The behavioral overlay is the most opinionated piece of this fork. Read [`../concepts/appropriate-use.md`](../concepts/appropriate-use.md) before using these skills on real research — the applied-micro vs behavioral asymmetry it discusses is most acute here. Cutting-edge experimental designs especially need your judgment; the workflow's encoded principles cover general failure modes but not the specifics of *your* novel mechanism.

---

## What the overlay adds

Five skills, six agents (four creator–critic pairs + two specialists), one rule, three references. The skills are the user-facing surface; the rest is infrastructure the skills draw on.

### Skills

- **`/design`** — inference-first experiment design via the 14-step checklist (modes: `experiment` for full design, `power` for standalone power analysis)
- **`/theory`** — formal model development or proof review (modes: `develop` for new model, `review` for existing proofs)
- **`/preregister`** — generate pre-registration documents (formats: `--aspredicted` for AsPredicted v2.00, `--osf` for OSF / Coffman and Dreber 7-item PAP). **Hard gate**: the orchestrator will not dispatch data collection without this.
- **`/otree`** — generate, review, or explain oTree experiment code (oTree 5.x / 6.x)
- **`/qualtrics`** — create, validate, or improve Qualtrics surveys (QSF format with custom JS / CSS / HTML support)

### Agents

- **`designer`** + **`designer-critic`** — designer produces 14-step designs; the critic runs adversarial checks for IC violations, MPL pitfalls, measurement error, parameter selection, focal values, clustering, design-hacking
- **`theorist`** + **`theorist-critic`** — theorist develops models; the critic runs the 16-item theory-quality checklist including the non-vacuity check (Item 16 catches theorems true of no real object)
- **`otree-specialist`** — oTree code generation and review
- **`qualtrics-specialist`** — Qualtrics QSF generation and validation

### Rule and references

- **`.claude/rules/experiment-design-principles.md`** — the 13 non-negotiable design principles. Carries in-line academic attributions throughout; this is the load-bearing source-of-truth for the behavioral overlay's design rigor.
- **`.claude/references/inference-first-checklist.md`** — the portable 14-step checklist that the designer agent reads when producing experiments. Operationalizes the 13 principles into step-by-step structure.
- **`.claude/references/domain-profile-behavioral.md`** — domain calibration (notation, conventions, common methods)
- **`.claude/references/seminal-papers-by-subfield.md`** — a curated list of subfield seminal papers (12 categories: Prospect Theory, Social Preferences, Time Preferences, Belief Formation, Discrimination, Complexity, Attention, Experimental Methods, Nudges, Structural Behavioral Estimation, Market/Auction Experiments, plus the open one)
- **`.claude/references/qualtrics-patterns.md`** — common Qualtrics patterns (used by qualtrics-specialist)

---

## `/design experiment` — the inference-first 14-step checklist

The most distinctive behavioral skill. The skill dispatches the `designer` agent (proposer) and `designer-critic` (validator), with the agents internalizing both the 13 design principles and the 14-step checklist.

### What it produces

A design document covering all 14 steps:

1. **Research question** — the causal/behavioral claim being tested
2. **Hypotheses** — theoretical predictions (formal model) or empirical hypotheses (existence experiment); both accepted, but each requires a specific direction and a falsification criterion
3. **Statistical tests** (co-designed with treatments) — exact tests, estimands, nulls, clustering, multiple-testing correction
4. **Data structure required** — what the tests need (paired, independent, panel, choice lists, belief distributions)
5. **Treatment arms** — one factor at a time per Croson 2005, with per-arm justification
6. **Interface and elicitation** — method and IC argument hierarchy (statewise monotonicity weakest; risk-neutral EU strongest, generally avoided), MPL pitfalls, belief elicitation per Healy and Leo's decision tree
7. **Process measurement** — RT always (free, informative); additional measures (mouse-tracking, eye-tracking, SCR) where justified
8. **Incentive design** — payment structure with explicit IC argument
9. **Subject comprehension** — instructions ≤ 3 pages, pretested with non-experts; understanding checks pre-treatment; never drop POST-treatment
10. **Timing and logistics** — session structure, matching, randomization
11. **Power analysis** — effect-size justified from theory / pilots / literature; Lin 2013 covariate adjustment for existence experiments; cluster VIF if relevant
12. **Budget and attrition** — per-subject payment, platform fees, total budget; differential-attrition planning
13. **Parameter selection** — per Snowberg and Yariv (2025): maximize objective relevance; check for flat incentives, corner solutions, misperception robustness, multiple equilibria; guard against design-hacking
14. **Pre-registration draft** — Coffman and Dreber 7-item PAP structure; consider Registered Reports for high-risk designs

The designer-critic then runs adversarial checks on the design: IC violations, focal-value risk (60–70% in some tasks per Snowberg and Yariv 2025), measurement-error budget (30–50% of variance per Gillen 2019), parameter-selection rigor, clustering, design-hacking.

### Underlying provenance

[`.claude/rules/experiment-design-principles.md`](../../.claude/rules/experiment-design-principles.md) is the load-bearing rule. Its 13 principles each carry in-line academic attribution: Niederle on hypothesis-driven design and alternative-hypothesis controls (5 strategies), Moffatt on test selection, Healy and Leo on the IC assumption hierarchy, Azrieli 2018 on random-round payment monotonicity, Gneezy and Rustichini (2000) on small-incentives backfire, Snowberg and Yariv (2025) on focal values + parameter selection, Brodeur 2024 on pre-registration vs PAP effectiveness, Brocas 2025 on RT / DDM, Gillen 2019 on measurement error, Chapman and Fisher (2025) on noisy covariates and false positives, Kahneman and Tversky (1979) on common-ratio K&T parameters, Croson 2005 on one-factor-at-a-time. Read that file for the full citation context; this docs page is a pointer, not a substitute.

### When to invoke

- Starting a new experimental project: `/design experiment "What I'm trying to test, in a sentence"`
- Stress-testing an existing design: `/design experiment` with the path to a draft design doc
- Standalone power analysis: `/design power` (skips the design content, focuses on N calculations + sensitivity)

---

## `/theory` — formal model development or proof review

Two modes: `develop` (build a model from assumptions to testable predictions) and `review` (verify proofs, check assumptions, audit notation).

### Develop mode

Produces a `model.tex` with definitions, propositions, proofs, and testable predictions. The theorist agent integrates with the designer when working on combined theory+experiment papers (predictions feed Step 2 of the inference-first checklist).

### Review mode

The theorist-critic runs a 16-item theory-quality checklist. Item 16 — non-vacuity — is the load-bearing one: it catches theorems that are formally correct but true of no real object (the empty-class problem). A proof can be valid; the theorem can still be useless.

### Output

- `theory/model.tex` — main model document
- `theory/proofs/` — proof appendices

---

## `/preregister` — pre-registration (hard gate)

Generates pre-registration documents. Two formats:

- **`--aspredicted`** — answers to all 11 AsPredicted questions (v2.00). Suitable for low-stakes experiments where a quick filing is sufficient.
- **`--osf`** — OSF format using the Coffman and Dreber 7-item PAP structure. Suitable for higher-stakes experiments where the full pre-analysis plan adds value (Brodeur 2024 on PAP effectiveness vs pre-registration alone).

### Hard gate

The orchestrator will not dispatch data collection or analysis agents without a filed pre-registration. This is enforced via the workflow's pipeline dependency graph; you can't skip step 14 of the inference-first checklist (pre-registration draft) and proceed to running subjects.

### When to invoke

After `/design experiment` produces an approved design (designer-critic score ≥ 80), and before any data collection. The skill reads the design document and templates the answers; you review and fill in anything the design doc didn't cover.

---

## `/otree` — oTree experiment code

Three modes: `create` (scaffold app from design doc), `review` (audit existing code), `explain` (teach oTree concepts).

### Create mode

Reads the approved design document and produces an oTree app: `models.py`, `pages.py`, `templates/`, `_templates/global/`. Targets oTree 5.x or 6.x (specify in `CLAUDE.md` if you have a preference).

### Review mode

Audits existing oTree code for correctness and best practices: data export sanity, page sequence logic, group-formation correctness, payment calculation, proper use of `Currency` vs raw numerics.

### Explain mode

For users new to oTree. Produces explanations of specific oTree concepts on request — page sequences, sessions vs groups vs players, the `models.py` / `pages.py` separation, etc.

---

## `/qualtrics` — Qualtrics survey generation and validation

Four modes: `create` (generate QSF from design doc), `validate` (check exported QSF for correctness), `improve` (suggest fixes), `export-js` (custom JS / CSS / HTML for custom interactions).

### Create mode

Reads the approved design document and produces a `.qsf` (Qualtrics Survey Format) file you can import into Qualtrics. Includes: question blocks, branching logic, randomization, embedded data fields, end-of-survey logic.

### Validate mode

Checks an exported QSF for common errors: branching logic that orphans questions, randomization that breaks block ordering, embedded data fields not properly initialized, custom JS that won't survive Qualtrics' editor.

### Underlying reference

[`.claude/references/qualtrics-patterns.md`](../../.claude/references/qualtrics-patterns.md) catalogs common Qualtrics patterns the qualtrics-specialist agent draws on. Useful read if you're authoring custom JS for elicitation interfaces.

---

## A typical behavioral session

Behavioral work has more steps than applied-micro because the experimental design itself is a substantial artifact. A typical first project:

1. **`/discover`** — research-spec phase (universal)
2. **`/theory develop`** *(if your project has a formal model)* — build the model
3. **`/design experiment`** — the 14-step inference-first design, with designer-critic review
4. **`/preregister --osf`** *or* `--aspredicted` — file the pre-registration (hard gate)
5. **`/otree`** *or* `/qualtrics` — implement the experiment platform
6. *(Run subjects on the platform — outside the workflow)*
7. **`/analyze`** — analyze the collected data (universal)
8. **`/write`** — paper sections drafted from approved code (universal)
9. **`/review`** — peer-review simulation (universal)
10. **`/submit`** — final gate before journal submission (universal)

Steps 2–5 are where the behavioral overlay does most of its work. Steps 1 and 7–10 are universal across all branches.

---

## Why behavioral needs more human judgment than applied micro

Repeated from [`../concepts/appropriate-use.md`](../concepts/appropriate-use.md), worth saying again here: the workflow's behavioral overlay codifies *general* design principles drawn from the experimental-economics literature. These cover failure modes that apply to most experiments. They do **not** cover whether *your specific design* identifies the mechanism you think it does.

Two specific risks unique to behavioral work that the workflow cannot catch on its own:

1. **Mechanism-confound errors.** A design that the 14-step checklist passes can still confound your hypothesized mechanism with a second mechanism the checklist doesn't mention. Pattern-matching against textbook templates doesn't tell you whether *your* mechanism is well-identified for *your* population.
2. **Literature-recency errors.** A paper currently in the workshop circuit (not yet published) may have already shown your manipulation doesn't work. The workflow's `seminal-papers-by-subfield.md` reference is a curated list of foundational work; it cannot know about ongoing work the model hasn't been trained on.

For these, your judgment + literature knowledge + subject-matter expertise are the load-bearing parts. The workflow's design output is a first draft of your reasoning, not a verification.

---

## Cross-references

- [`branch-model.md`](branch-model.md) — picking the right branch
- [`first-session.md`](first-session.md) — typical-first-day walkthrough (universal)
- [`../concepts/appropriate-use.md`](../concepts/appropriate-use.md) — the applied-micro vs behavioral asymmetry; load-bearing for behavioral users
- [`../reference/skills.md`](../reference/skills.md) — full skill catalogue including behavioral overlay skills
- [`../reference/agents.md`](../reference/agents.md) — designer / theorist / otree-specialist / qualtrics-specialist in the agent table
- The actual rule and reference files: [`.claude/rules/experiment-design-principles.md`](../../.claude/rules/experiment-design-principles.md), [`.claude/references/inference-first-checklist.md`](../../.claude/references/inference-first-checklist.md)
