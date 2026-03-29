# Behavioral & Experimental Economics Workflow Plan v3: Hugo Base + Pedro Infrastructure

**Status:** DRAFT — awaiting Christina's approval
**Date:** 2026-03-28
**Supersedes:** `2026-03-17_workflow-adaptation-plan-v2.md` (behavioral v2.1)
**Key change:** Restructured around Hugo's clo-author as base (mirroring applied micro plan structure), preserving all v2.1 content
**Learnings update (2026-03-28):** Incorporated findings from 11+ papers across theory writing (Thomson, Board & Meyer-ter-Vehn, Varian, Halmos, Rubinstein, McCloskey, Knuth, Cochrane), experimental design (Niederle, Croson, List et al., Snowberg & Yariv, Moffatt), and experimental methodology handbook (Chapman & Fisher, Healy & Leo, Huber & Graham, Brocas et al., Coffman & Dreber). Major changes: 14-step checklist (was 12), 13 design principles (was 10), enriched agent/skill descriptions with paper-specific knowledge and reference files.
**Test projects:** JMP (`belief_distortion_discrimination`), BDM (`bdm_bic`)
**Stata version:** 17 (no `dtable`, no `frames` from v18)
**LaTeX engine:** pdflatex

---

## Rationale for Restructuring

The v2.1 behavioral plan (2026-03-17) was comprehensive but built from scratch. The applied micro plan (2026-03-18) demonstrated a better approach: start from Hugo's clo-author, layer Pedro's infrastructure, then add domain-specific components. This restructuring:

- Makes explicit what Hugo already provides (11 skills, 16 agents, 12 rules)
- Eliminates rebuilding things Hugo has (worker-critic pairs, journal profiles, scoring, orchestrator)
- Makes the behavioral plan directly comparable to the applied micro plan
- Clarifies what is **unique** to behavioral/experimental economics

**The v2.1 plan's content is excellent.** This document reorganizes it into the Hugo-base framework and adds Keep/Adapt/Replace/Move/Add annotations.

---

## 1. What Hugo Already Has (Use As-Is or Adapt)

### Skills (11)

| Hugo Skill | What It Does | Action | Behavioral Notes |
|------------|-------------|--------|------------------|
| `/discover` | Interview + lit review + ideation (3 modes) | **Adapt** | Default lit mode searches behavioral/experimental + psychology crossover journals (no subfield flags — literature pools overlap heavily). Evaluate psychology papers critically (different inference/design standards). Add `--theory` flag for theory development: focuses on decision theory, game theory, mechanism design, structural models, and characterization results. |
| `/strategize` | Design identification strategy + robustness plan | **Replace** with `/design experiment` | Behavioral uses inference-first design, not observational identification |
| `/analyze` | End-to-end data analysis | **Adapt** for Stata 17 primary | Add non-parametric tests, permutation tests, structural estimation |
| `/write` | Paper section drafting with anti-hedging | **Adapt** | Add experimental reporting standards (N, demographics, exclusions, instructions) |
| `/review` | Journal-calibrated peer review (domain + methods) | **Adapt** | Calibrate to behavioral/experimental journals |
| `/revise` | Address referee comments | **Keep** | |
| `/submit` | Target journal, package, audit, final check | **Adapt** | Add pre-registration cross-check, AEA data editor compliance |
| `/talk` | Paper → Beamer talk (4 formats) | **Adapt** for pdflatex | |
| `/tools` | Utility subcommands | **Keep** | |
| `/archive` | Archive completed work | **Keep** | |
| `/new-project` | Full orchestrated project setup | **Adapt** | Add theory/, experiments/ folders to scaffold |

### Agents (16 — full worker-critic system)

| Hugo Agent | Role | Action | Behavioral Notes |
|------------|------|--------|------------------|
| librarian + librarian-critic | Literature search + coverage review | **Adapt** | Add behavioral/experimental journals, psychology crossover journals (evaluate psychology papers critically — different inference/design standards). Default behavior: always check for existing experimental evidence on the question before proposing a novel study. |
| explorer + explorer-critic | Data assessment + data quality review | **Adapt** | Experimental data: session structure, attention checks, exclusion criteria |
| strategist + strategist-critic | Identification design + 4-phase audit | **Replace** with designer + designer-critic | Behavioral needs inference-first experimental design, not observational identification |
| coder + coder-critic | Analysis code + reproducibility review | **Adapt** for Stata 17 | Non-parametric tests, permutation tests, structural estimation, session clustering. **Knows:** Moffatt test selection guide with exact Stata commands; default clustering at session/group level; structural estimation (CRRA via `ml`, heterogeneous agents via `intreg`/`fmm`, social preferences via `asclogit`). **Reads:** `experimental-design-learnings.md` Section 8 |
| storyteller + storyteller-critic | Paper → talk + talk review | **Keep** | |
| writer + writer-critic | Paper drafting + clarity review | **Adapt** | Experimental reporting standards. **Writer follows:** McCloskey (2019) anti-pattern rules (no "This paper..." openings, one word per concept, active verbs, concrete examples); Cochrane (2005) structure (punchline first, intro max 3 pages, first sentence states YOUR contribution, Golden Rule: nothing before main result reader doesn't need); Knuth et al. (1989) math writing (separate formulas with words, never start sentence with symbol, no logical symbols in prose). **Writer-critic uses:** McCloskey 11-item anti-pattern checklist + bad words list; Cochrane style flags (passive voice, naked "this," >3 decimal places, fancy words); Knuth hard rules + strong preferences. **Reads:** `theory-writing-learnings.md` Sections 13-15 |
| data-engineer | Raw → cleaned data | **Adapt** for Stata 17 | Session/round/role structure, attention check filtering. RT screening (log-transform, exclude extremes per Brocas et al.) |
| domain-referee | Journal-calibrated subject review | **Adapt** | Calibrate to Experimental Economics, AEJ:Micro, JEBO, etc. |
| methods-referee | Identification/inference review | **Adapt** | Experimental validity, demand effects, incentive compatibility, power. **Enriched checks:** clustering adequacy (Moffatt: OLS without clustering → size 0.46); elicitation IC assumptions against Healy & Leo hierarchy; parameter selection against Snowberg & Yariv framework; replication package against Coffman & Dreber requirements; measurement error budget (30-50% of variance). **Reads:** `experimental-design-learnings.md` and `handbook-experimental-methodology-learnings.md` |
| orchestrator | Pipeline coordinator | **Adapt** | Behavioral dependency graph (theory → design → preregister gate) |
| verifier | Compilation + replication check | **Adapt** for pdflatex + Stata 17 | |

### Rules (12)

| Hugo Rule | Est. Lines | Action | Behavioral Notes |
|-----------|-----------|--------|------------------|
| `workflow.md` | ~80 | **Adapt** | Behavioral dependency graph, `/preregister` gate |
| `agents.md` | ~60 | **Keep** | Worker-critic protocol unchanged |
| `quality.md` | ~70 | **Replace** scoring weights | Experimental design 25%, theory 15% (see Section 4) |
| `logging.md` | ~25 | **Keep** | |
| `domain-profile.md` | ~80 | **Replace** with behavioral econ profile | **Move to reference file** |
| `journal-profiles.md` | ~170 | **Move to reference file** | Replace with behavioral/experimental journals |
| `content-standards.md` | ~50 | **Adapt** | Add experimental reporting standards |
| `working-paper-format.md` | ~60 | **Adapt** for pdflatex | |
| `tables.md` | ~40 | **Adapt** | estout/esttab for Stata |
| `figures.md` | ~30 | **Adapt** | Stata graph export (.pdf, .png) |
| `meta-governance.md` | ~250 | **Replace** with Pedro's version | Already in template repo |
| `revision.md` | ~40 | **Keep** | |

---

## 2. What Pedro Adds (Layer On Top)

All Pedro infrastructure carries over identically to the applied micro plan.

| Pedro Component | Why Hugo Needs It | Status |
|-----------------|-------------------|--------|
| Pre-compact hook | Saves context before auto-compression | **Exists** in template |
| Post-compact restore hook | Recovers after compression | **Exists** in template |
| Context monitor hook | Tracks context usage | **Exists** in template |
| Log reminder hook | Proactive logging nudge | **Exists** in template |
| Protect-files hook | Prevents accidental overwrites | **Exists** in template |
| Verify reminder hook | Nudges verification after changes | **Exists** in template |
| `/deep-audit` skill | Repository-wide consistency check | **Add** |
| `/context-status` skill | Session health monitoring | **Add** |
| `/learn` skill | Extract discovery into persistent skill | **Add** |
| `/commit` skill | Stage, PR, merge workflow | **Add** (Hugo has none) |
| Exploration folder protocol | `explorations/` sandbox with archive | **Exists** in template |
| Requirements spec template | MUST/SHOULD/MAY + clarity status | **Add** |
| `/challenge` skill | Standalone invocable challenge | **Add** with `--design`, `--theory`, `--paper`, `--fresh` modes |
| TikZ infrastructure | tikz-reviewer agent + visual quality rule | **Exists** in template |
| Plan-first workflow | Spec-then-plan before implementation | **Exists** in template |

---

## 3. What We Add (Behavioral/Experimental Econ Specific)

This is what makes the behavioral workflow **different** from the applied micro workflow. These components do not exist in Hugo or Pedro.

### 3a. New Skills (6 behavioral-specific)

| Skill | What It Does | Why Applied Micro Doesn't Need This |
|-------|-------------|--------------------------------------|
| `/theory develop [topic]` | Formal model: assumptions → setup → equilibrium → comparative statics → testable predictions. **Follows:** Varian (1997) KISS workflow (simplest example → pattern → model → generalize → simplify again); Thomson (1999) notation conventions (mnemonic symbols, logical sequencing, boundary examples); Board & Meyer-ter-Vehn (2018) architecture (one paper one model, main result by page 15). Theorist agent reads `theory-writing-learnings.md` | Applied micro rarely builds formal theory from scratch |
| `/theory review [file]` | Review proofs, check derivations, verify predictions follow from model (`--proofs`, `--assumptions`, `--predictions`). **Uses:** theorist-critic 16-item checklist + Knuth/Halmos proof quality rules (direct proofs preferred, proof steps synchronized with reader, structured proofs). Reads `theory-writing-learnings.md` Section 8 + Section 14 | Applied micro uses existing theory |
| `/design experiment [topic]` | Full inference-first design checklist (14 steps, see Section 5) (`--lab`, `--online`). **Incorporates:** Niederle (2025) alternative-hypothesis controls, Snowberg & Yariv (2025) parameter selection, Healy & Leo (2025) belief elicitation, Chapman & Fisher (2025) preference elicitation, Brocas et al. (2025) process measurement, List et al. (2011) power analysis, Moffatt test selection, Coffman & Dreber (2025) replication standards. Survey experiment sub-steps: manipulation checks, differential attrition, covariate adjustment (Huber & Graham 2025) | Applied micro uses `/strategize` for observational identification |
| `/qualtrics [mode]` | Create importable QSF, validate exported QSF, improve survey, generate custom JS/CSS (`create`, `validate`, `improve`, `export-js`) | Applied micro doesn't run surveys |
| `/otree [mode]` | Generate oTree app from design doc, review code, explain concepts (`create`, `review`, `explain`) | Applied micro doesn't run lab experiments |
| `/preregister [study]` | Generate pre-registration from design checklist (`--aspredicted`, `--osf`) | Applied micro occasionally pre-registers but it's not a gate |

**`/design power [spec]`** is a subcommand of `/design experiment`, not a standalone skill. Modes: `--simulate` (simulation-based) and `--analytical` (formula-based).

### 3b. New Agents (6 behavioral-specific)

| Agent | Role | Why Applied Micro Doesn't Need This |
|-------|------|--------------------------------------|
| **theorist** | Formal model development: game theory (Nash, SPE, PBE), decision theory (EU, prospect theory, Kőszegi-Rabin), dynamic programming (Bellman, Markov), behavioral (present bias, loss aversion, probability weighting), structural estimation setup (MLE, MSM, indirect inference). **Follows:** Thomson (1999) rules (simplest version first, mnemonic notation, boundary examples for definitions, logical sequencing); Varian (1997) KISS workflow (simplest example → pattern → model → generalize); Board & Meyer-ter-Vehn (2018) architecture (one paper one model, main result by page 15, theorems as English-language takeaways). **Figure standards** (Thomson Section 5): use pictures to lighten papers and illustrate proof steps; label completely (allocations, prices, endowments); Venn diagrams for logical relations between assumptions. **Reads:** `quality_reports/paper_learnings/theory-writing-learnings.md` Sections 1-10 | Applied micro uses existing theory |
| **theorist-critic** | Proof verification, assumption stress-testing, boundary conditions, uniqueness checks, notation consistency. **Uses 16-item checklist** from theory-writing-learnings.md Section 8: informal descriptions match formal statements, each hypothesis independently needed, "clearly"/"obviously" claims verified, notation introduced before use, math-to-English ratio in [52%, 63.5%] for proofs, quantifiers unambiguous, all conditions gathered before conclusion, logical sequencing, no single-use notation, assumptions specified per proof step, consistent terminology, functions vs values not confused, variants explored, boundary examples provided, examples satisfying all assumptions exist (non-vacuous), parallel format, proof divided into labeled units. **Additional checks:** fewer footnotes than pages (Board & Meyer-ter-Vehn); figures used to illustrate proof steps and logical relations (Thomson Section 5). **Reads:** `quality_reports/paper_learnings/theory-writing-learnings.md` Section 8 | No new proofs to verify |
| **designer** | Inference-first design specialist: produces 14-step checklist, interface/elicitation expertise, incentive compatibility analysis, power analysis, budget/timing estimates. Knows: BDM, MPL, strategy method, direct elicitation, belief elicitation (Schotter & Trevino), allocation tasks. **Also knows:** Snowberg & Yariv (2025) parameter selection framework (4 objectives); Healy & Leo (2025) belief elicitation decision tree (6 recommendations + IC hierarchy); Chapman & Fisher (2025) preference elicitation comparison (6 methods + MPL pitfalls + DOSE adaptive); List et al. (2011) optimal sample allocation (unequal variance, costs, clusters); Brocas et al. (2025) process measurement (always collect RT). **Reads:** `quality_reports/paper_learnings/experimental-design-learnings.md` and `handbook-experimental-methodology-learnings.md` | Applied micro doesn't design experiments |
| **designer-critic** | Adversarial design review: demand effects, confounds, comprehension, interface effects, floor/ceiling, incentive issues, external validity, multiple testing, ethics/IRB. **Enriched checks from learnings:** MPL pitfalls (centering bias, multiple switching 16%, reference point effects); IC assumption hierarchy violation (is the method's IC assumption justified per Healy & Leo?); measurement error budget (30-50% of variance — ORIV recommended?); parameter pitfalls (flat incentives, corner solutions, misperception sensitivity per Snowberg & Yariv); focal value response risk for bounded measures (60-70%); design-hacking check (parameters selected via unreported pilots?); clustering adequacy (OLS without clustering → size 0.46 per Moffatt). **Reads:** `quality_reports/paper_learnings/handbook-experimental-methodology-learnings.md` and `experimental-design-learnings.md` | Applied micro uses strategist-critic for identification threats |
| **qualtrics-specialist** | QSF generation, custom JS/CSS/HTML, survey flow, embedded data, piped text, display logic, quotas, randomizers, web services, end-of-survey redirects | Not applicable |
| **otree-specialist** | App scaffolding, pages, models, templates, live pages, session config, group matching, role assignment, custom JS, settings.py | Not applicable |

### 3c. New Rules (behavioral-specific)

| Rule | Lines Target | Content | Scope |
|------|-------------|---------|-------|
| `experiment-design-principles.md` | ~90 | The experiment "constitution" — 13 principles (see Section 6) | Paths: `experiments/**`, `designs/**` |
| `stata-code-conventions.md` | ~60 | Stata 17, settings.do, .doh, key packages, experimental data conventions | Paths: `**/*.do`, `**/*.doh` |
| `python-code-conventions.md` | ~30 | Type hints, requirements.txt, seed management, Jupyter for exploration only | Paths: `**/*.py` |

**Note:** `experiment-design-principles.md` is the single biggest difference from the applied micro workflow. It is the "constitution" for experimental design — non-negotiable principles that every experiment must follow. Applied micro has no equivalent.

### 3d. New Reference Files (NOT always-on — read by agents on demand)

| File | Content |
|------|---------|
| `.claude/references/domain-profile-behavioral.md` | Full behavioral econ profile: field, journals, data sources, identification strategies, conventions, notation, seminal references by subfield (11 categories), referee concerns, tolerance thresholds |
| `.claude/references/journal-profiles-behavioral.md` | 15+ journals with calibration (see Section 10 for full list) |
| `.claude/references/inference-first-checklist.md` | Full 14-step design checklist (portable, read by designer agent) |
| `.claude/references/seminal-papers-by-subfield.md` | Organized by Christina's 11 categories (see Section 8) |
| `.claude/references/replication-standards.md` | AEA Data Editor requirements for experimental papers |
| `quality_reports/paper_learnings/theory-writing-learnings.md` | **Already exists** — read by theorist, theorist-critic, writer, writer-critic agents. Covers Thomson, Board & Meyer-ter-Vehn, Varian, Halmos, Rubinstein, McCloskey, Knuth, Cochrane |
| `quality_reports/paper_learnings/experimental-design-learnings.md` | **Already exists** — read by designer, designer-critic, coder, methods-referee agents. Covers Niederle, Croson, List et al., Snowberg & Yariv, Moffatt |
| `quality_reports/paper_learnings/handbook-experimental-methodology-learnings.md` | **Already exists** — read by designer, designer-critic, methods-referee agents. Covers Chapman & Fisher (preference elicitation), Healy & Leo (belief elicitation), Huber & Graham (survey experiments), Brocas et al. (choice processes), Coffman & Dreber (replicability) |

### 3e. New Templates

| Template | Content |
|----------|---------|
| `templates/experiment-design-checklist.md` | Blank 14-step inference-first checklist |
| `templates/pre-registration-template.md` | AsPredicted and OSF formats |
| `templates/subject-instructions-template.tex` | LaTeX template for participant instructions |

### 3f. Adapted Skills (from Hugo, with behavioral modifications)

| Hugo Skill | Behavioral Adaptation |
|------------|----------------------|
| `/discover` | Add `--behavioral`, `--experimental`, `--neuro`, `--decision-theory` subfield flags to lit mode. Librarian searches behavioral/experimental journals plus psychology crossovers. |
| `/analyze` | Stata 17 primary. Add non-parametric tests (KS, Mann-Whitney, Fisher exact, Wilcoxon, permutation). Cluster by session for lab data. Multiple hypothesis testing corrections (Bonferroni, BH, Romano-Wolf). Structural estimation (MLE, MSM). estout/esttab output. |
| `/write` | Add experimental reporting: subject pool description (N, demographics, recruitment, payment), exclusion criteria and counts, treatment descriptions with exact instructions shown to subjects. Anti-hedging enforcement retained. **Writer uses McCloskey + Cochrane + Knuth rules; writer-critic uses combined anti-pattern checklist (see theory-writing-learnings.md Sections 13-15).** |
| `/review` | Calibrate domain-referee to behavioral journals. Methods-referee checks: demand effects, incentive compatibility, power adequacy, pre-registration compliance, interface effects. **Enriched with:** clustering adequacy (Moffatt), elicitation IC hierarchy (Healy & Leo), parameter selection (Snowberg & Yariv), replication package (Coffman & Dreber), measurement error budget. |
| `/submit` | Cross-check pre-registration compliance. AEA replication package with experimental materials (instructions, QSF, oTree code, IRB approval). **Replication package must include:** raw data (platform exports before cleaning), code that does BOTH cleaning AND analysis, extensive comments, "computational empathy" (Coffman & Dreber 2025). |
| `/talk` | pdflatex compilation (not xelatex). Retain TikZ support. |

---

## 4. Scoring Weights (Behavioral-Specific)

These differ substantially from applied micro, where identification strategy takes the 25% slot.

| Component | Weight | Scored By | Rationale |
|-----------|--------|-----------|-----------|
| Literature coverage | 8% | librarian-critic | Important but not the bottleneck |
| Theory/model quality | 15% | theorist-critic | Math must be rigorous, predictions must be testable |
| **Experimental design** | **25%** | **designer-critic** | **The experiment IS the paper. Bad design = bad paper.** Designer-critic now uses enriched adversarial checklist drawing from 5+ papers (Niederle, Snowberg & Yariv, Healy & Leo, Chapman & Fisher, Moffatt) |
| Implementation quality | 7% | qualtrics/otree specialist review | Survey/code must work correctly |
| Code quality | 10% | coder-critic | Reproducibility matters |
| Paper quality | 20% | domain-referee + methods-referee (avg) | Clarity and argumentation |
| Manuscript polish | 10% | writer-critic | Professional presentation |
| Replication readiness | 5% | verifier | AEA compliance |
| **Total** | **100%** | | |

**Per-component minimum for submission:** 80 on every component (no "great paper, broken design").

**Severity gradient:**

| Phase | Critic Stance | Example |
|-------|--------------|---------|
| Discovery/Ideation | Encouraging | Missing citation: -2 |
| Theory development | Constructive | Assumption gap: -5 |
| Experimental design | **Strict** | Missing power analysis: -15 |
| Implementation | Strict | QSF validation error: -10 |
| Execution/Analysis | Strict | Wrong clustering: -10 |
| Peer Review | **Adversarial** | Design confound: -20 |

**Comparison with applied micro scoring:**

| Component | Behavioral | Applied Micro |
|-----------|-----------|---------------|
| Experimental design | **25%** | 0% (not applicable) |
| Theory/model quality | **15%** | 0% (not applicable) |
| Identification strategy | 0% (subsumed by design) | **25%** |
| Implementation quality | 7% | 0% (not applicable) |
| Literature coverage | 8% | 10% |
| Code quality | 10% | 15% |
| Paper quality | 20% | 25% |
| Manuscript polish | 10% | 15% |
| Replication readiness | 5% | 10% |

---

## 5. The Inference-First Design Checklist (14 Steps)

This is the core intellectual contribution of the behavioral workflow. It reverses the usual design process: specify statistical tests BEFORE designing treatments. Enriched with findings from Niederle (2025), Snowberg & Yariv (2025), List et al. (2011), Healy & Leo (2025), Chapman & Fisher (2025), Brocas et al. (2025), Moffatt "Experimetrics," Coffman & Dreber (2025), and Huber & Graham (2025).

```
1. RESEARCH QUESTION
   What causal/behavioral claim are you testing?

2. THEORETICAL PREDICTIONS
   What does the model predict? List each testable prediction.

3. STATISTICAL TESTS (specify BEFORE designing treatments)
   For each prediction: exact test, estimand, and null.
   - Test selection guide (Moffatt):
     Between-subject continuous normal → t-test (`ttest y, by(g) unequal`)
     Between-subject continuous non-normal → Mann-Whitney (`ranksum y, by(g)`)
     Between-subject distribution → KS (`ksmirnov y, by(g)`)
     Between-subject discrete → Epps-Singleton (`escftest y, group(g)`)
     Within-subject continuous normal → paired t (`ttest WTA=WTP`)
     Within-subject continuous non-normal → Wilcoxon (`signrank WTA=WTP`)
     Within-subject any → sign test (`signtest WTA=WTP`)
   - CLUSTERING IS CRITICAL: Always cluster at session/group level.
     OLS without clustering has size 0.46 (rejects 46% under null).
     OLS cluster at subject → size 0.15. Cluster at session → size 0.07.
     Multi-level model (`xtmixed`) → size 0.08 (best for between-subject).
   - Multiple hypothesis testing: specify correction method
     (Bonferroni, Benjamini-Hochberg, Romano-Wolf)
   - Structural estimation if applicable: CRRA via `ml`, heterogeneous
     agents via `intreg`/`fmm`, social preferences via `asclogit`

4. DATA STRUCTURE REQUIRED
   What data do those tests need? (e.g., paired observations,
   independent samples, panel, choice lists, belief distributions)

5. TREATMENT ARMS
   Design treatments that produce the required data structure.
   - One-factor-at-a-time: each treatment differs on exactly ONE
     dimension from comparison. Two changes = confounded. (Croson)
   - Justify each arm. What does comparison of A vs B identify?
   - Control for alternative hypotheses (Niederle's 5 strategies):
     (1) Design by elimination — game where your model has no "bite"
     (2) Direct controls — eliminate force by design (e.g., provide
         computation tables to remove complexity)
     (3) Indirect controls — measure separately, control econometrically
         (caveat: hidden assumptions about measurement accuracy)
     (4) "Do it both ways" — find environment where your model predicts
         opposite direction from alternative
     (5) Stress-testing — check auxiliary predictions after main result
   - Background noise sources to control (Niederle):
     Randomizing participants (confusing tasks → random behavior),
     floor/ceiling effects, framing/instructions effects

6. INTERFACE & ELICITATION
   For every choice subjects make:
   - Elicitation method and WHY (cite evidence for/against alternatives)

   Preference elicitation comparison (Chapman & Fisher 2025):
   | Method          | # Elicitations | IC  | Inconsistency | Framing |
   |-----------------|---------------|-----|---------------|---------|
   | BDM             | 1             | Yes*| Very High     | Low     |
   | Binary Choices  | 20-120        | Yes | High          | Low     |
   | MPLs            | 2-4           | Yes | Medium        | HIGH    |
   | Convex Budget   | 14-45         | Yes | Medium        | Medium  |
   | DOSE (adaptive) | 4-10          | Yes*| Low           | Low     |
   | Survey (quant)  | 1             | No  | n.a.          | Low     |

   MPL PITFALLS (designer-critic must check):
   - Multiple switching: 16% of subjects in Holt-Laury (63-study meta)
   - Centering bias: altering risk-neutrality position can REVERSE
     correlation between cognitive ability and risk aversion
   - Reference point effects: fixed element acts as endowment
   - Recommendation: MPLs should be symmetric around neutral mid-point

   Belief elicitation decision tree (Healy & Leo 2025):
   - Probability of binary event → default MPL; stronger incentives → TPL
   - Beliefs about a number → mode (pay-if-true, simplest) or median
     (quantile MPL). Mean ONLY if necessary (requires EU assumption)
   - Entire distribution → probability of each bin; randomly pick one
   - Most likely event → modal event elicitation (zero assumptions)
   - USE incentives but do NOT show incentive details on decision screen
   - When participant can influence outcome → use MPL (eliminates hedging)
   - If using scoring rule → use binarized; recommend BQSR

   IC assumption hierarchy (weakest = preferred):
   (1) Statewise Monotonicity — MPL, BDM (weakest, preferred)
   (2) S-O Reduction — all binarized scoring rules (strictly stronger)
   (3) Risk-neutral EU — dollar scoring rules (strongest, avoid)

   - Floor/ceiling risk analysis for bounded variables
   - Focal value response risk: 60-70% at focal values in some tasks
     (Snowberg & Yariv). Diagnose via responsiveness checks.
   - MEASUREMENT ERROR WARNING: 30-50% of variance in elicited measures
     is measurement error (Gillen et al. 2019). Mitigation:
     (1) Careful design: simplify, training rounds, visual aids
     (2) Multiple elicitations + ORIV correction or averaging
     (3) Exclude noisy data (comprehension quizzes, pre-registered criteria)
     (4) Econometric corrections (MLE/Bayesian with noise parameters)
   - COVARIATE WARNING: When noisy elicitation is used as a control
     variable, false positive rates approach 100% in large samples
     (Chapman & Fisher 2025). Never treat noisily-elicited variables
     as reliable covariates without ORIV correction.
   - Screen layout mockup

7. PROCESS MEASUREMENT (NEW — Brocas et al. 2025)
   - ALWAYS collect response time — it is free and informative
   - RT reflects strength-of-preference; enables DDM-based estimates
   - Log-transform RT for regression analysis
   - Screen out very fast (guessing) and very slow (inattention)
   - Additional measures decision matrix:
     | Want to measure...          | Use...                | Cost      |
     |-----------------------------|-----------------------|-----------|
     | Strength of preference      | RT or mouse AUC       | Free      |
     | Attribute processing order  | Mouse-tracking / eye  | Free-mod  |
     | Information search strategy | Mouselab / eye        | Free-mod  |
     | Strategic reasoning         | Mouselab              | Free      |
     | Emotional arousal           | SCR (Empatica)        | $0.5-2K   |
     | Cognitive effort            | Pupil dilation        | Moderate  |
   - Record hardware type (trackpad vs. mouse) if using mouse-tracking

8. INCENTIVE DESIGN
   - Payment structure (flat fee + bonus, or piece rate, or lottery)
   - Incentive compatibility argument (cite theoretical basis)
   - "Very small incentives can be worse than none" (Gneezy & Rustichini)
   - Payment scheme must be justified theoretically (almost half of
     experimental econ papers don't justify — Niederle)
   - Random round payment: IC under monotonicity assumption (Azrieli
     et al. 2018). But monotonicity + reduction of compound lotteries
     = independence axiom. Problematic if studying independence violations.
   - For infinitely repeated games: pay FINAL round, not random (Niederle)
   - Stakes must be comparable across treatments/domains
   - Expected average payment calculation
   - Payment range (min/max possible)
   - IRB-compliant payment justification

9. SUBJECT COMPREHENSION
   - Instructions: 2-3 pages maximum, pretested with non-experts (Croson)
   - Pretesters must answer: What decision am I making? How do I make it?
     Where do I record it? What are possible outcomes?
   - Understanding checks (quiz questions with criteria for exclusion)
   - Attention checks: 4 pre-treatment instructional checks (Berinsky
     et al. 2021); mock vignette checks (Kane et al. 2023)
   - CRITICAL: NEVER drop respondents who fail POST-TREATMENT checks
     — introduces bias (Montgomery et al. 2018)
   - Manipulation checks (survey experiments — Huber & Graham):
     (1) Measure outcomes for intended mechanisms (did treatment move beliefs?)
     (2) Measure outcomes for unintended mechanisms (exclusion restriction)
     (3) Test for demand effects (Mummolo & Peterson 2019)
   - Practice/learning rounds (if applicable)
   - Default to abstract/context-free framing for theory-testing

10. TIMING & LOGISTICS
    - Expected median completion time
    - Time per screen/task estimate
    - Total experiment length target (shorter = better)
    - Session structure (if lab: how many per session, simultaneous?)
    - Matching protocol consistent with theory (strangers vs. partners)
    - Randomization of subjects to treatments
    - Privacy: private payment, anonymous data
    - Effect persistence: treatment effects decay to 1/3-1/2 within
      1-4 weeks (Huber & Graham). Design panel follow-ups if long-term
      effects are of interest.

11. POWER ANALYSIS
    - Effect size assumption (justify from theory, pilots, or literature)
    - Core formulas (List et al. 2011):
      Equal variance, two-arm: n* = 2(t_{α/2} + t_β)² × (σ/δ)² per arm
      α=0.05, power=0.80: 1 SD → n*=16; 0.5 SD → n*=64; 0.7 SD → n*=30
    - "30 per cell" is explicitly debunked — only detects 0.70 SD (List et al.)
    - Optimal allocation (unequal variance): n₁*/n₀* = σ₁/σ₀
    - Optimal allocation (unequal costs): n₁*/n₀* = √(c₀/c₁) × (σ₁/σ₀)
    - Multiple contrasts with baseline: weight baseline heavier
      {A,B,C} where A=baseline → optimal is {1/2, 1/4, 1/4} (List et al.)
    - Cluster designs: multiply by VIF = 1 + (m-1)ρ; optimal cluster
      size m* = √((1-ρ)/ρ) × √(c_k/c_m) (List et al.)
    - Covariate adjustment: pre-treatment outcome is single most effective
      power booster; Lin (2013) estimator guarantees smaller SE (Huber & Graham)
    - Only control for pre-treatment variables (post-treatment → bias)
    - Minimum detectable effect given budget constraint
    - For replications: aim 90% power to detect 1/2 to 2/3 of original
      effect (replication effects ~75% of originals, Camerer et al. 2018)

12. BUDGET
    - Per-subject expected payment
    - Platform fees (Prolific, lab overhead)
    - Total budget for target N
    - Budget sensitivity: what if N needs to increase 50%?
    - Differential attrition planning: balance time/effort across arms;
      control respondents read similar-length text about unrelated topic
      (Huber & Graham). Test: regress attrition on treatment indicators.

13. PARAMETER SELECTION (NEW — Snowberg & Yariv 2025)
    - Choose parameters based on objective:
      | Objective               | Parameter Rule                          |
      |-------------------------|-----------------------------------------|
      | Document irregularity   | Maximize distance from benchmark        |
      | Discriminate models     | Maximize distance between predictions   |
      | Institutional design    | Maximize welfare vs. status quo         |
      | Policy evaluation       | Echo real-world parameters              |
    - Parameter pitfalls:
      Flat incentives — parameters maximizing discrimination may create
        flat reward functions, reducing reliability
      Misperception robustness — choose where optimal behavior is robust
        to small perception errors
      Corner solutions — avoid parameters where optimal actions near 0/1;
        noise compresses toward center, appearing suboptimal
      Multiple equilibria — if not unique, any test confounds with
        coordination problem
    - G-hacking check (Niederle): 30%+ of common ratio experiments use
      K&T (1979) parameters; effects smaller/reversed at other parameters.
      Mitigation: randomly select from specified set, use canonical
      environments, be transparent about selection process

14. PRE-REGISTRATION DRAFT
    - Coffman & Dreber (2025) 7-item PAP structure:
      (1) Experimental design description
      (2) Inclusion criteria for participants
      (3) Variables and coding
      (4) Exact analyses (regression models)
      (5) Control variables and clustering decisions
      (6) Test hierarchy: primary > secondary > robustness > exploratory
      (7) Pilots done (with separate linked PAP)
    - "Pre-registration alone does NOT curb p-hacking. Only pre-registration
      WITH complete pre-analysis plans reduces p-hacking." (Brodeur et al. 2024)
    - Design-hacking warning: unreported pilots that tweak design until
      something "works," then PAP that design = "overly confident view
      of robustness and generalizability" (Coffman & Dreber)
    - Every data collection decided ahead of time: pilot or real study
    - Replication package requirements (all top journals as of July 2024):
      Raw data (platform exports before cleaning), analysis code that does
      BOTH cleaning AND analysis, extensive comments, "computational empathy"
      (Vilhuber) — write as if a stranger needs to understand
    - Multiple testing correction method specified
    - Alternative path — Registered Reports (Coffman & Dreber):
      Submit paper with intro, design, hypotheses (no results); journal
      peer-reviews before data collection; if accepted, publishes regardless
      of results. Leads to more null results (Scheel et al. 2021).
```

---

## 6. Experiment Design Principles Rule (The "Constitution")

This is an **always-on rule** (scoped to `experiments/**`, `designs/**`). Non-negotiable principles:

1. **Inference-first**: Specify statistical tests before designing treatments
2. **Subject comprehension**: Instructions must be clear; understanding checks required
3. **Interface intentionality**: Every elicitation choice documented with justification
4. **Simplicity**: Shortest experiment that answers the question
5. **Incentive compatibility**: Payment structure must align incentives; cite theoretical basis
6. **Floor/ceiling awareness**: Analyze bounded variables for compression risk
7. **Pre-registration mandatory**: No data collection without registered hypotheses + primary analysis plan. This is about pre-registration (goal, design, N, main hypothesis), not necessarily a rigid pre-analysis plan that may stifle innovation (Niederle 2025)
8. **Budget realism**: Expected payment × N × platform fee calculated before launch
9. **Pilot when needed**: Pilot for debugging (instructions, timing, comprehension), not for confirming hypotheses. Simple, well-understood paradigms may not need pilots. Beware pilot dangers: anchoring to a design that "worked," chasing side results, repeated piloting = g-hacking (Niederle 2025)
10. **No deception**: Never deceive participants. Intentional vagueness or omission of details is acceptable; outright deception is not. If a design requires deception, redesign the experiment
11. **Collect response time always**: RT is free, informative, and enables DDM-based preference estimation. Log-transform for regression; screen out very fast (guessing) and very slow (inattention). (Brocas et al. 2025)
12. **Measurement error awareness**: Budget for noise — 30-50% of variance in elicited measures is measurement error (Gillen et al. 2019). Use ORIV correction, multiple elicitations, adaptive methods (DOSE), or econometric corrections. Never treat a single elicitation as ground truth.
13. **Parameter selection discipline**: Choose parameters to maximize the relevant objective (Snowberg & Yariv 2025). Check for: flat incentive functions (reduce reliability), corner solutions (noise compresses toward center), misperception sensitivity, multiple equilibria (confounds with coordination). Guard against g-hacking: justify parameter selection transparently.

**Target: ~90 lines.** Behavioral justifiably exceeds applied micro's per-rule budget because experimental design principles must be internalized by every agent that touches experiment files. The 3 new principles (11-13) draw from Brocas et al. (2025), Gillen et al. (2019)/Chapman & Fisher (2025), and Snowberg & Yariv (2025).

---

## 7. Always-On Rule Budget

**Target: <620 lines of always-on rules**

Behavioral needs more than applied micro (~535) because the experiment design principles rule has no equivalent in applied micro. The rule grew from ~80 to ~90 lines with the addition of 3 new principles from the paper learnings (RT collection, measurement error, parameter selection).

| Rule | Est. Lines | Source | Scope |
|------|-----------|--------|-------|
| `workflow.md` | 80 | Hugo (adapted) | Always-on |
| `agents.md` | 60 | Hugo | Always-on |
| `quality.md` | 70 | Hugo (replaced weights) | Always-on |
| `logging.md` | 25 | Hugo | Always-on |
| `content-standards.md` | 50 | Hugo (adapted) | Path-scoped |
| `working-paper-format.md` | 40 | Hugo (adapted, pdflatex) | Path-scoped: `paper/**/*.tex` |
| `tables.md` | 40 | Hugo (adapted, estout) | Path-scoped: `tables/**` |
| `figures.md` | 30 | Hugo (adapted, Stata graphs) | Path-scoped: `figures/**` |
| `revision.md` | 40 | Hugo | Path-scoped |
| `experiment-design-principles.md` | 90 | **New** (behavioral-specific, 13 principles) | Path-scoped: `Experiments/**`, `designs/**` |
| `stata-code-conventions.md` | 60 | **New** | Path-scoped: `**/*.do`, `**/*.doh` |
| `python-code-conventions.md` | 30 | **New** | Path-scoped: `**/*.py` |
| **Total** | **~615** | | |

**Heavy content moved to `.claude/references/` (read on demand):**
- Domain profile (behavioral econ)
- Journal profiles (15+ journals)
- Seminal papers by subfield
- Inference-first checklist detail
- Replication standards
- Meta-governance (already in Pedro's template)

**Comparison:**
- Applied micro: ~535 lines (no experiment-design-principles, no python-code-conventions)
- Behavioral: ~615 lines (+90 for experiment principles with 13 principles from paper learnings, +30 for Python conventions, −40 for no air-gapped-workflow rule)

---

## 8. Seminal Papers Subfield Categories

Christina's edited list (11 categories with sub-categories):

1. Prospect Theory & Reference Dependence
2. Social Preferences & Cooperation
3. Time Preferences & Present Bias
4. Belief Formation & Updating
5. Discrimination
6. Complexity & Noisy Cognition
7. Attention & Limited Cognition
   - Rational Inattention (sub-category)
8. Experimental Methods & Design
   - Risk Elicitation & Measurement (sub-category)
   - Belief Elicitation Methods (sub-category)
9. Nudges & Choice Architecture
10. Structural Behavioral Estimation
11. Market/Auction Experiments

**Process:** Claude gathers seminal papers per subfield → Christina reviews, approves, augments from Mendeley library. Stored in `.claude/references/seminal-papers-by-subfield.md`.

---

## 9. Dependency Graph — Research Pipeline

```
/discover interview ─────┐
                         ├──→ /discover lit ──→ /theory develop
/discover ideate ────────┘         │                    │
                                   │                    ▼
                                   │            /theory review
                                   │                    │
                                   ▼                    ▼
                          /design experiment ←── testable predictions
                                   │
                          ┌────────┼────────┐
                          ▼        ▼        ▼
                  /design power  /qualtrics  /otree
                          │        │        │
                          ▼        ▼        ▼
                     /preregister (GATE — no data collection without it)
                               │
                               ▼
                          COLLECT DATA
                               │
                          ┌────┴────┐
                          ▼         ▼
                     /analyze    /write
                          │         │
                          ▼         ▼
                     /review --peer [journal]
                               │
                          ┌────┴────┐
                          ▼         ▼
                     /revise     /talk
                          │
                          ▼
                     /submit
```

**Key behavioral-specific features:**
- `/preregister` is a **hard gate** — no data collection without it
- Theory produces testable predictions that feed directly into experiment design
- The design checklist's step 3 (statistical tests) feeds directly into the pre-registration analysis plan and eventually into `/analyze`
- `/qualtrics` and `/otree` are parallel implementation paths from the same design document

**Mid-pipeline entry points:**
- Have data already? → Start at `/analyze`
- Have a draft? → Start at `/review`
- Have a design but no theory? → Start at `/design`, flag that theory is missing
- Have theory but no design? → Start at `/theory review`, then `/design`

---

## 10. The `/challenge` Skill — Behavioral Modes

Shared modes (`--paper`, `--fresh`) plus behavioral-specific modes (`--design`, `--theory`). Applied micro adds `--identification` instead.

### Mode: `--design` (Experiment Design Challenge) — MOST IMPORTANT

**Identification & Inference:**
- "You say Treatment A tests mechanism X — but it also changes Y. How do you isolate X?"
- "Your statistical test assumes independence, but subjects interact in the lab. What's your clustering strategy?"
- "You powered for a 0.3 SD effect — what if the true effect is 0.15?"

**Subject Experience:**
- "Walk me through exactly what a subject sees, screen by screen. Where do they get confused?"
- "You're using a slider for belief elicitation — centering bias will contaminate your data. Why not an input box?"
- "Your instructions mention 'other participants' decisions' — this introduces social desirability bias"
- "A median subject takes 25 minutes on your pilot. The 90th percentile takes 55 minutes. Your slowest subjects are your most confused — is that a problem?"

**Incentive Compatibility:**
- "Is your BDM implementation actually incentive compatible? (What does Danz et al. 2022 say about this?)"
- "Subjects earn $0.50 for a 'correct' belief but $12 show-up fee — are beliefs even incentivized?"
- "Your payment is capped at $20 — subjects near the cap have no marginal incentive"

**Alternative Designs:**
- "What if you used within-subject instead of between-subject? What do you gain/lose?"
- "Could a strategy method elicit the same information with fewer subjects?"
- "Have you considered a 2×2 factorial? It would let you test for interaction effects"

**Parameter Selection (NEW — from Snowberg & Yariv 2025):**
- "Your parameters maximize model discrimination, but does the reward function become flat there? Flat incentives = noisy data."
- "At these parameter values, is behavior robust to small misperceptions? Or does a 5% perception error flip the optimal action?"
- "You chose parameters near 0 — noise will compress responses toward the center. Can you move the interesting region to interior values?"
- "Is equilibrium unique at these parameters? If not, you're confounding your treatment effect with a coordination problem."
- "30% of common ratio experiments use K&T (1979) parameters. Are your results robust to other parameter values, or did you g-hack?"

**Elicitation (NEW — from Healy & Leo + Chapman & Fisher):**
- "You're using an MPL for belief elicitation — have you checked for centering bias? 16% of Holt-Laury subjects show multiple switching."
- "Your belief elicitation uses a dollar-denominated scoring rule. That assumes risk-neutral EU. Your subjects are risk averse. Switch to BQSR or MPL."
- "You're eliciting mean beliefs, but that requires EU. Since you're studying probability weighting, elicit the mode instead."
- "30-50% of variance in elicited preferences is measurement error. Are you using ORIV, or treating single elicitations as ground truth?"

**Process Measurement (NEW — from Brocas et al. 2025):**
- "Are you collecting response times? They're free and would let you estimate a DDM for more precise preference recovery."
- "Your mouse-tracking data uses trackpads and mice — hardware produces different trajectories. Are you controlling for this?"

### Mode: `--theory` (Model Challenge)

- "Your model assumes common knowledge of rationality — but your experiment tests bounded rationality. Contradiction?"
- "Equilibrium is unique only when parameter X > 0. What if X = 0 in your experiment?"
- "Your comparative static prediction requires λ > 1 — but Tversky & Kahneman's median estimate is λ = 2.25. How sensitive is your prediction to λ?"
- "Your theorem statement is 4 lines of notation. Board & Meyer-ter-Vehn say theorems should be English-language takeaways that are also mathematically true. Can you rephrase?"
- "You have 10 theorems. If I forced you to cut to 3, which survive? Those are your paper." (Board & Meyer-ter-Vehn)
- "Your model takes 4 pages to state. Varian says the best notation is no notation. Can you start with a 2-agent, 2-good example?"

**Rubinstein's 4 Dilemmas (NEW — from Rubinstein 2006):**
- "Where does your model produce absurd results? All models do somewhere — have you probed the boundary conditions?"
- "You're evaluating your model by empirical fit. Rubinstein argues models clarify mechanisms, not predict. What mechanism does yours isolate?"
- "Could you have found this regularity just by looking at the data with no model? When is the model doing real work?"
- "Your formal presentation may obscure moral complexity. What does your model have to say about this practical question — honestly?"

---

## 11. Christina's Project Details (Preserved from v2.1)

### JMP Project: `belief_distortion_discrimination`

| Item | Value |
|------|-------|
| Main repo | `/Users/christinasun/github_repos/belief_distortion_discrimination` |
| Satellite repo 1 | `/Users/christinasun/github_repos/endogenous_info` (text classification, ML) |
| Satellite repo 2 | `/Users/christinasun/github_repos/jmp_sample_behavior` (stopping rule models) |
| Overleaf dir | `/Users/christinasun/Library/CloudStorage/Dropbox/Apps/Overleaf/belief_distortion_discrimination` |
| Status | Mostly finished |

### BDM Project: `bdm_bic`

| Item | Value |
|------|-------|
| Main repo | `/Users/christinasun/github_repos/bdm_bic` |
| Overleaf dir | `/Users/christinasun/Library/CloudStorage/Dropbox/Apps/Overleaf/BDM Incentive and Truth Telling` |
| Status | Halfway — lit review stage |

### Repo Architecture

- **Separate repos per project** (not inside workflow repo)
- Template repo (`claude-code-my-workflow`) has domain branches; `.claude/` directory is copied to project repos
- Overleaf sync via Dropbox (considering git sync)

### Stata Conventions

- `main.do` / `doall.do` — master file runs everything
- `settings.do` — global macros for paths and settings
- `.doh` files — do helper files, used with `include` to preserve local macros
- Numbered scripts: `01_clean.do`, `02_analysis.do`, `03_figures.do`
- Key packages: reghdfe, estout, coefplot, ivreghdfe, palettes, cleanplots, egenmore, regsave, cdfplot, binscatter, binscatter2

### LaTeX Compilation

```bash
# Beamer slides (3-pass, pdflatex)
cd Slides && TEXINPUTS=../Preambles:$TEXINPUTS pdflatex -interaction=nonstopmode file.tex
BIBINPUTS=..:$BIBINPUTS bibtex file
TEXINPUTS=../Preambles:$TEXINPUTS pdflatex -interaction=nonstopmode file.tex
TEXINPUTS=../Preambles:$TEXINPUTS pdflatex -interaction=nonstopmode file.tex

# Paper (3-pass, pdflatex)
cd Paper && pdflatex -interaction=nonstopmode main.tex
BIBINPUTS=..:$BIBINPUTS bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

---

## 12. Folder Structure (Behavioral Project)

```
project-repo/
├── CLAUDE.md                    # Project configuration (project-specific only)
├── CLAUDE.local.md              # Machine-specific overrides (gitignored)
├── MEMORY.md                    # Cross-session learning
├── bibliography_base.bib        # Centralized bibliography
│
├── paper/                       # Main manuscript (SOURCE OF TRUTH)
│   ├── main.tex
│   └── sections/                # Modular section files
│
├── theory/                      # Formal models (BEHAVIORAL-SPECIFIC)
│   ├── model.tex
│   ├── proofs/
│   └── notes/
│
├── experiments/                  # Experiment materials (BEHAVIORAL-SPECIFIC)
│   ├── designs/                 # Design documents, checklists
│   ├── protocols/               # IRB protocols, consent forms
│   ├── instructions/            # Subject instructions (LaTeX → PDF)
│   ├── oTree/                   # oTree project code
│   ├── qualtrics/               # QSF exports, custom JS/CSS, flow docs
│   ├── comprehension/           # Understanding checks, attention checks
│   └── pilots/                  # Pilot data, budget estimates, timing
│
├── data/
│   ├── raw/                     # Untouched data
│   ├── cleaned/                 # Processed data
│   └── simulated/               # Simulated data for power analysis
│
├── figures/
├── tables/
├── supplementary/               # Online appendix
│
├── slides/                      # Beamer presentations
├── preambles/                   # LaTeX headers
├── replication/                 # Replication package
│
├── scripts/
│   ├── stata/                   # PRIMARY
│   │   ├── main.do
│   │   ├── settings.do
│   │   ├── 01_clean.do
│   │   ├── 02_analysis.do
│   │   ├── 03_figures.do
│   │   └── helpers/             # .doh reusable routines
│   └── python/                  # SECONDARY
│
├── explorations/                # Research sandbox
├── master_supporting_docs/      # Reference papers
├── quality_reports/             # Plans, specs, reviews, session logs
│
├── .claude/
│   ├── settings.json
│   ├── WORKFLOW_QUICK_REF.md
│   ├── skills/                  # 17 skills
│   ├── agents/                  # 22 agents (16 Hugo-adapted + 6 new)
│   ├── rules/                   # ~12 rules
│   ├── hooks/                   # 7 hooks (from Pedro)
│   └── references/              # Heavy content (read on demand)
│
└── templates/
    ├── session-log.md
    ├── quality-report.md
    ├── requirements-spec.md
    ├── experiment-design-checklist.md
    ├── pre-registration-template.md
    ├── subject-instructions-template.tex
    └── skill-template.md
```

---

## 13. Key Differences from Applied Micro Plan

| Aspect | Applied Micro | Behavioral |
|--------|--------------|------------|
| `/strategize` | **Keep** (observational identification) | **Replace** with `/design experiment` |
| strategist pair | **Keep** | **Replace** with designer + designer-critic |
| Theory agents | Not needed | **Add** theorist + theorist-critic |
| Platform agents | Not needed | **Add** qualtrics-specialist, otree-specialist |
| `/theory` skill | Not needed | **Add** (develop + review) |
| `/qualtrics` skill | Not needed | **Add** (create, validate, improve, export-js) |
| `/otree` skill | Not needed | **Add** (create, review, explain) |
| `/preregister` skill | Not needed | **Add** as hard gate |
| experiment-design-principles rule | Not needed | **Add** (~80 lines, path-scoped) |
| Top scoring weight | Identification strategy 25% | Experimental design 25% |
| Theory scoring weight | 0% | 15% |
| Air-gapped workflow rule | **Yes** (TERC server) | **No** |
| `/balance` skill | **Yes** | **No** |
| `/event-study` skill | **Yes** | **No** |
| Stata version | 18 | **17** |
| Always-on budget | ~535 lines | **~615 lines** |
| Test projects | TX | JMP, BDM |
| Pre-registration | Optional | **Mandatory gate** |

---

## 14. Phased Implementation Plan

### Phase 0: Setup
- [ ] Create `behavioral` branch from main
- [ ] Merge Hugo's clo-author into `behavioral` branch
- [ ] Verify Pedro's hooks, `/commit`, `/deep-audit`, `/context-status`, `/learn` carry over from main
- [ ] Verify TikZ infrastructure carries over
- [ ] Add `/challenge` skill with behavioral modes (`--design`, `--theory`, `--paper`, `--fresh`)

### Phase 1: Rules and Reference Files
- [ ] Create `experiment-design-principles.md` (always-on rule, ~90 lines, 13 principles)
- [ ] Create `stata-code-conventions.md` (always-on rule, ~60 lines)
- [ ] Create `python-code-conventions.md` (always-on rule, ~30 lines)
- [ ] Adapt `quality.md` with behavioral scoring weights
- [ ] Adapt `workflow.md` with behavioral dependency graph and `/preregister` gate
- [ ] Adapt `content-standards.md` with experimental reporting standards
- [ ] Adapt `working-paper-format.md` for pdflatex
- [ ] Adapt `tables.md` for estout/esttab
- [ ] Adapt `figures.md` for Stata graph export
- [ ] Create `.claude/references/` with: domain profile, journal profiles, inference-first checklist, seminal papers, replication standards
- [ ] Create templates: experiment-design-checklist.md, pre-registration-template.md, subject-instructions-template.tex

### Phase 2: Agents
- [ ] Adapt Hugo's shared agents:
  - librarian pair → behavioral/experimental journals
  - explorer pair → experimental data structure
  - coder pair → Stata 17, non-parametric tests, session clustering
  - writer pair → experimental reporting standards
  - data-engineer → session/round/role, attention checks, exclusion criteria
  - domain-referee → behavioral journal calibration
  - methods-referee → experimental validity, demand effects, incentive compatibility
  - orchestrator → behavioral dependency graph
  - verifier → pdflatex + Stata 17
  - storyteller pair → keep as-is
- [ ] Create behavioral-specific agents:
  - theorist + theorist-critic
  - designer + designer-critic
  - qualtrics-specialist
  - otree-specialist

### Phase 3: Skills
- [ ] Adapt Hugo's skills: `/discover`, `/analyze`, `/write`, `/review`, `/submit`, `/talk`, `/revise`, `/tools`, `/archive`, `/new-project`
- [ ] Create behavioral-specific skills: `/theory`, `/design experiment`, `/qualtrics`, `/otree`, `/preregister`

### Phase 4: Testing with BDM Project
- [ ] Copy adapted `.claude/` to BDM repo
- [ ] Write BDM-specific CLAUDE.md
- [ ] Test `/discover lit` on BDM belief elicitation literature
- [ ] Test `/design experiment` on BDM experimental design
- [ ] Test `/challenge --design` on BDM experiment
- [ ] Test `/qualtrics validate` on existing BDM survey (requires QSF export)
- [ ] Test `/preregister` on BDM study
- [ ] Run `/deep-audit`
- [ ] Iterate agent prompts based on output quality

### Phase 5: Testing with JMP Project
- [ ] Copy adapted `.claude/` to JMP repo
- [ ] Write JMP-specific CLAUDE.md
- [ ] Test `/review --peer` on JMP paper
- [ ] Test `/challenge --theory` on JMP model
- [ ] Test `/analyze` code review on existing .do files
- [ ] Build up MEMORY.md with `[LEARN]` entries

---

## 15. Running To-Do List

### Must-Do (Blocks Implementation)
- [ ] **Merge Hugo's clo-author into behavioral branch** ← NEXT STEP
- [ ] **Gather seminal papers per subfield** — Claude searches, Christina reviews and augments (11 categories)
- [ ] **Confirm subfield categories** — Christina's edited list has 11; confirm no changes
- [ ] **Export a QSF from existing Qualtrics survey** — needed for `/qualtrics` skill development

### Should-Do (Improves Quality)
- [ ] Share custom Beamer templates (pdflatex and xelatex)
- [ ] Provide a sample `.doh` file (if not visible in test repos)
- [ ] Clarify Stata license type (SE vs MP)
- [ ] Set up Overleaf git sync for BDM and JMP
- [ ] Consolidate JMP satellite repos into main JMP repo
- [ ] Share swift raid Claude Chat memory/output

### Nice-to-Have (Can Do Later)
- [ ] Review and refine journal profiles after testing `/review --peer`
- [ ] Identify additional referee concerns from real reviews
- [ ] Customize notation conventions to Christina's exact preferences
- [ ] Set up Stata package auto-discovery hook

---

## 16. Notation Conventions (Behavioral Econ)

To be placed in `.claude/references/domain-profile-behavioral.md`.

| Symbol | Meaning |
|--------|---------|
| u(·) or U(·) | Utility |
| w(p) or π(p) | Probability weighting |
| r or ρ | Risk aversion coefficient |
| u(x) = x^(1-r)/(1-r) | CRRA utility |
| δ | Discount factor |
| β | Present bias (quasi-hyperbolic: βδ^t) |
| r or x* | Reference point |
| λ | Loss aversion |
| T or D | Treatment indicator |
| Y | Outcome |
| τ or ATE | Treatment effect |
| μ or b | Belief |
| s | Signal |
| θ | Type |
| v(x) | Value function (PT): x^α for gains, −λ(−x)^β for losses |
| σ | Strategy |
| π | Payoff |
| NE, SPE, PBE | Nash equilibrium, Subgame perfect, Perfect Bayesian |
| V(s) = max_a {u(s,a) + δ E[V(s')|s,a]} | Bellman equation |

---

## 17. Quality Tolerance Thresholds

| Quantity | Tolerance |
|----------|-----------|
| Treatment effect replication | within 0.01 SD |
| p-values | within 0.001 |
| Power calculations | within 1% of simulated power |
| Cross-language replication (Stata vs Python) | within 1e-6 for point estimates |
| Structural parameter estimates | within 1e-4 |

---

## Appendix A: Full Skills Summary (17 total)

| # | Skill | Source | Behavioral-Specific? |
|---|-------|--------|---------------------|
| 1 | `/discover` (interview, lit, ideate) | Hugo (adapted) | Partly |
| 2 | `/theory` (develop, review) | **New** | Yes |
| 3 | `/design experiment` | **New** (replaces `/strategize`) | Yes |
| 4 | `/qualtrics` (create, validate, improve, export-js) | **New** | Yes |
| 5 | `/otree` (create, review, explain) | **New** | Yes |
| 6 | `/preregister` (aspredicted, osf) | **New** | Yes |
| 7 | `/analyze` | Hugo (adapted) | No |
| 8 | `/write` | Hugo (adapted) | Partly |
| 9 | `/review` | Hugo (adapted) | Partly |
| 10 | `/challenge` (design, theory, paper, fresh) | Pedro + New | Partly |
| 11 | `/revise` | Hugo | No |
| 12 | `/submit` | Hugo (adapted) | Partly |
| 13 | `/talk` | Hugo (adapted) | No |
| 14 | `/commit` | Pedro | No |
| 15 | `/tools` | Hugo + Pedro | No |
| 16 | `/archive` | Hugo | No |
| 17 | `/new-project` | Hugo (adapted) | Partly |

## Appendix B: Full Agents Summary (22 total)

| # | Agent | Source | Behavioral-Specific? |
|---|-------|--------|---------------------|
| 1 | librarian | Hugo (adapted) | No |
| 2 | librarian-critic | Hugo (adapted) | No |
| 3 | **theorist** | **New** | Yes |
| 4 | **theorist-critic** | **New** | Yes |
| 5 | **designer** | **New** (replaces strategist) | Yes |
| 6 | **designer-critic** | **New** (replaces strategist-critic) | Yes |
| 7 | **qualtrics-specialist** | **New** | Yes |
| 8 | **otree-specialist** | **New** | Yes |
| 9 | explorer | Hugo (adapted) | No |
| 10 | explorer-critic | Hugo (adapted) | No |
| 11 | coder | Hugo (adapted) | No |
| 12 | coder-critic | Hugo (adapted) | No |
| 13 | data-engineer | Hugo (adapted) | No |
| 14 | writer | Hugo (adapted) | Partly |
| 15 | writer-critic | Hugo (adapted) | No |
| 16 | storyteller | Hugo | No |
| 17 | storyteller-critic | Hugo | No |
| 18 | domain-referee | Hugo (adapted) | Partly |
| 19 | methods-referee | Hugo (adapted) | Partly |
| 20 | orchestrator | Hugo (adapted) | Partly |
| 21 | verifier | Hugo (adapted) | No |
| 22 | tikz-reviewer | Pedro | No |
