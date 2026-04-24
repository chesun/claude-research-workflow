---
name: design
description: |
  Inference-first experiment design. Dispatches Designer (proposer) and
  designer-critic (validator). Two modes: experiment (full 14-step checklist)
  and power (standalone power analysis). Use when designing an experiment
  or calculating sample size requirements.
argument-hint: "[experiment | power] [topic or spec path] [--lab | --online]"
allowed-tools: Read,Grep,Glob,Write,Bash,Task
---

# Design

Design an experiment or run a power analysis by dispatching the **Designer** (proposer) and **designer-critic** (validator).

**Input:** `$ARGUMENTS` — mode keyword followed by topic, research question, or path to spec file.

---

## Modes

### `/design experiment [topic]` — Full Experiment Design

Produce a complete inference-first design using the 14-step checklist.

**Agents:** Designer → designer-critic
**Output:** Design document + filled checklist

**⚠️ MANDATORY AGENT DISPATCH: You MUST use the Agent tool (subagent_type="designer") for the design phase, then use the Agent tool (subagent_type="designer-critic") for the review. Do NOT design the experiment yourself inline — the agents have specialized prompts with the 14-step checklist and 13 design principles internalized.**

**Workflow:**

1. Read research spec, literature review, and theory predictions if they exist
2. Read `.claude/references/inference-first-checklist.md` for the 14-step structure
3. Read `.claude/references/domain-profile-behavioral.md` for field conventions
4. If `--lab` or `--online` flag present, tailor platform-specific sections
5. **DISPATCH: Use the Agent tool with subagent_type="designer"** to produce the 14-step design. Include in the agent prompt:
   - The research question, hypotheses, and any existing literature review or theory predictions
   - The path to the inference-first checklist and domain profile
   - Instructions to produce all 14 steps:
   - Steps 1-2: Research question and hypotheses (theoretical predictions OR empirical hypotheses — both accepted)
   - Steps 3-5: Statistical tests, data structure, and treatment arms (co-designed iteratively)
   - Step 6: Interface and elicitation choices with IC justification
   - Step 7: Process measurement plan (always RT)
   - Step 8: Incentive design with IC argument
   - Step 9: Subject comprehension plan
   - Step 10: Timing and logistics
   - Step 11: Power analysis (see `/design power` for standalone)
   - Step 12: Budget and attrition planning
   - Step 13: Parameter selection (Snowberg & Yariv framework)
   - Step 14: Pre-registration draft outline (full PAP via `/preregister`)
   - Instructions to save to `quality_reports/designs/`
6. **DISPATCH: Use the Agent tool with subagent_type="designer-critic"** to review. Include in the agent prompt the path to the design document and instructions for adversarial audit:
   - Phase 1: Completeness (all 14 steps addressed)
   - Phase 2: Design validity (13 principles from experiment-design-principles.md)
   - Phase 3: Inference validity (test selection, clustering, power)
   - Phase 3b: Existence experiment scrutiny (if no formal model — MDE plausibility, informative under null, Registered Reports)
   - Phase 4: Completeness and polish
7. If FATAL or SERIOUS issues found, iterate (max 3 rounds)
8. Save design to `quality_reports/designs/YYYY-MM-DD_[topic]_design.md`
9. Save review to `quality_reports/designs/YYYY-MM-DD_[topic]_design_review.md`
10. Fill in `templates/experiment-design-checklist.md` with the design decisions

#### Platform Flags

**`--lab`:** Tailors for laboratory experiments
- oTree/z-Tree implementation considerations
- Session logistics (subjects per session, simultaneous play)
- Lab-specific subject pool (ORSEE/hroot recruitment)
- Matching protocols (strangers vs. partners)
- Privacy and payment procedures

**`--online`:** Tailors for online experiments
- Prolific/MTurk platform considerations
- Attention screening and bot detection
- Device/browser requirements
- Dropout and differential attrition (higher online)
- Completion time estimation and payment calibration

#### Interactive Mode

If invoked with just a topic (no spec file), the Designer asks up to 5 clarifying questions before producing the design:

1. What behavioral/causal claim are you testing?
2. Do you have a formal model with predictions, or an empirical hypothesis? *(If empirical: what's the direction, and why do you expect it?)*
3. Lab or online? (Or both?)
4. What's your approximate budget and timeline?
5. Are there existing experiments on this question? (What's the gap?)

---

### `/design power [spec]` — Power Analysis

Standalone power analysis, either simulation-based or analytical.

**Input:** `$ARGUMENTS` — a design spec, effect size, or topic description.

**Agents:** Designer (power analysis mode only)

**Workflow:**

1. Determine inputs:
   - Effect size (from theory, pilots, or literature — must be justified)
   - Significance level (default: 0.05)
   - Target power (default: 0.80; 0.90 for replications)
   - Number of arms and allocation ratio
   - Clustering structure (if applicable)
   - Covariate adjustment plan (if applicable)

2. **Analytical mode** (default): Apply List et al. (2011) formulas:
   - Equal variance, two-arm: n* = 2(t_{alpha/2} + t_beta)^2 * (sigma/delta)^2 per arm
   - Quick reference: alpha=0.05, power=0.80: 1 SD -> n*=16; 0.5 SD -> n*=64; 0.7 SD -> n*=30
   - "30 per cell" is debunked — only detects 0.70 SD
   - Optimal allocation (unequal variance): n1*/n0* = sigma1/sigma0
   - Optimal allocation (unequal costs): n1*/n0* = sqrt(c0/c1) * (sigma1/sigma0)
   - Multiple contrasts with baseline: {A,B,C} where A=baseline -> optimal is {1/2, 1/4, 1/4}
   - Cluster designs: multiply by VIF = 1 + (m-1)*rho; optimal cluster size m* = sqrt((1-rho)/rho) * sqrt(c_k/c_m)
   - Covariate adjustment: Lin (2013) estimator guarantees smaller SE
   - For replications: aim 90% power to detect 1/2 to 2/3 of original effect

3. **Simulation mode** (when `--simulate` flag or complex design):
   - Generate Stata or R simulation code
   - Simulate data under the design + assumed DGP
   - Run the planned test on each simulated dataset
   - Report rejection rate = empirical power
   - Useful for: non-standard tests, structural estimation, complex clustering

4. Output:
   - Required N per arm and total
   - Minimum detectable effect given budget constraint
   - Sensitivity table: power at different effect sizes and N
   - Budget implication: N * cost per subject * platform fee
   - Save to `quality_reports/designs/YYYY-MM-DD_[topic]_power.md`

---

## Principles

- **Designer proposes, designer-critic critiques.** Adversarial pairing catches design flaws before resources are committed.
- **Inference and design co-evolve.** Tests and treatments are developed together, not sequentially.
- **The design document is the contract.** Once approved, it feeds into `/preregister` and then the Coder implements faithfully.
- **Catch problems before running.** A flawed design caught now saves months and thousands of dollars.
- **The user decides.** If Designer and designer-critic disagree after 3 rounds, the user resolves it.
- **Power calculations require assumptions.** State every assumption. Show sensitivity. Never just report one number.
- **"30 per cell" is not a justification.** Every sample size must be derived from an effect size, not a rule of thumb.
