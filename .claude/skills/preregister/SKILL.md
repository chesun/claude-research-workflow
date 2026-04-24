---
name: preregister
description: |
  Generate pre-registration documents from experiment design. Supports
  AsPredicted (11 questions, v2.00) and OSF (Coffman & Dreber 7-item PAP).
  This is a HARD GATE in the pipeline — no data collection without it.
argument-hint: "[--aspredicted | --osf] [design doc path or topic] [--interactive]"
allowed-tools: Read,Grep,Glob,Write,Task
---

# Preregister

Generate a pre-registration document from an approved experiment design.

**Input:** `$ARGUMENTS` — format flag, design document path or topic, optional interactive flag.

**This is a HARD GATE.** The orchestrator will not dispatch data collection or analysis agents without a filed pre-registration.

---

## Formats

### `/preregister --aspredicted [design]` — AsPredicted Format

Generate answers to all 11 AsPredicted questions (v2.00). See [Data Colada #64](http://datacolada.org/64) for guidance.

**Workflow:**

1. Read the design document from `quality_reports/designs/` if it exists
2. Read `templates/pre-registration-template.md` for the exact question structure
3. Fill in all 11 questions from the design:

   **Q1. Data collection status** — "No, no data have been collected for this study yet." (If complicated, explain in Q8.)
   **Q2. Main hypothesis** — from design Step 1-2 (research question + predictions)
   **Q3. Key dependent variables** — from design Step 4 (data structure) with exact measurement
   **Q4. Conditions** — from design Step 5 (treatment arms) with N per arm
   **Q5. Exact analyses** — from design Step 3 (statistical tests): regression spec, test statistic, clustering, controls. Be precise.
   **Q6. Outliers and exclusions** — from design Step 9 (comprehension checks) + Step 7 (RT screening): exact rules and thresholds
   **Q7. Sample size** — from design Step 11 (power analysis): exact N and how determined
   **Q8. Anything else** — secondary analyses, exploratory variables, pilot status
   **Q9. Title** — project name + study description (max 80 characters)
   **Q10. Type of study** — Experiment (default for behavioral)
   **Q11. Data source** — from design Step 10 (Prolific / MTurk / University lab / etc.)

4. Include author table (from CLAUDE.md or ask user)
5. Save to `quality_reports/preregistrations/YYYY-MM-DD_aspredicted_[topic].md`

### `/preregister --osf [design]` — OSF Pre-Analysis Plan

Generate a comprehensive PAP following Coffman & Dreber (2025) 7-item structure. See [OSF Registrations Guide](https://help.osf.io/article/330-welcome-to-registrations) for the standard OSF form.

**Workflow:**

1. Read the design document from `quality_reports/designs/`
2. Read `templates/pre-registration-template.md` for the PAP structure
3. Draft all 7 sections:

   **1. Experimental Design Description**
   - Treatment arms and their purpose (from design Step 5)
   - Randomization method (from design Step 10)
   - Platform and subject pool (from design Step 10)
   - Elicitation methods with IC justification (from design Step 6)

   **2. Inclusion Criteria for Participants**
   - Eligibility requirements
   - Comprehension/attention check criteria and thresholds (from design Step 9)
   - Pre-registered exclusion rules — be exact about what triggers exclusion

   **3. Variables and Coding**
   - Primary outcome variable(s): definition, measurement method, units
   - Secondary outcome variable(s)
   - Treatment indicator(s) and coding
   - Control variables (pre-treatment only — post-treatment controls introduce bias)

   **4. Exact Analyses**
   - For each hypothesis: full regression specification, test statistic, null (from design Step 3)
   - Non-parametric tests where appropriate (from Moffatt guide)
   - Structural estimation details if applicable
   - Software: Stata 17 (specify packages: reghdfe, estout, wyoung, etc.)

   **5. Control Variables and Clustering Decisions**
   - Clustering level and justification (session/group default — cite Moffatt size warning)
   - Covariate adjustment method (Lin 2013 if planned)
   - Fixed effects if any

   **6. Test Hierarchy**
   | Priority | Hypothesis | Test | Correction |
   |----------|-----------|------|-----------|
   | Primary | [from design] | [exact test] | [if applicable] |
   | Secondary | | | BH or Romano-Wolf |
   | Robustness | | | |
   | Exploratory | | | None (labeled as exploratory) |

   **7. Pilots**
   - Pilot status: conducted / not conducted / planned
   - If conducted: separate linked PAP, sample size, key findings
   - Design-hacking check: parameters NOT selected from pilot results

4. Optional: dispatch **designer-critic** to review the PAP for consistency with design
5. Save to `quality_reports/preregistrations/YYYY-MM-DD_osf_pap_[topic].md`

### `/preregister --interactive` — Guided Interview

If no design document exists, conduct a 6-question guided interview before drafting.

**This is conversational.** Ask questions one at a time.

1. **What is your research question?** (What behavioral/causal claim?)
2. **What is the experimental design?** (Treatment arms, between/within, platform)
3. **What are the primary outcome variables?** (How measured, what units)
4. **What statistical tests will you run?** (For each hypothesis: test, clustering, corrections)
5. **What are your exclusion criteria?** (Attention checks, comprehension, RT screening)
6. **What is your sample size and justification?** (Power analysis, budget constraints)

After all 6 answers, draft in the user's chosen format (AsPredicted or OSF).

---

## Default Format

If no format flag is specified:
- If the study is simple (2-3 arms, 1-2 outcomes) → default to `--aspredicted`
- If the study is complex (multiple outcomes, structural estimation, subgroup analyses) → default to `--osf`
- If unclear → ask the user

---

## ASSUMED Placeholder Safety

**CRITICAL: Flag every assumed item clearly.**

When drafting from a topic (without a design document or interactive interview), many details will be assumed. For each:

- Mark with **[ASSUMED]** in bold
- Explain what was assumed and why
- Provide the most reasonable default but flag for review

The final section of every pre-registration must include:

```markdown
## Pre-Filing Checklist

**Review every [ASSUMED] item before filing this pre-registration.**

- [ ] [ASSUMED] Item 1 — [what was assumed]
- [ ] [ASSUMED] Item 2 — [what was assumed]

**Do not file until all items are reviewed and confirmed or corrected.**
```

A filed pre-registration with unchecked assumptions is worse than no pre-registration.

---

## Principles

- **Pre-registration is a commitment device.** Make sure the researcher understands what they're committing to.
- **Pre-specification is the point.** Everything is decided before seeing outcomes.
- **Be honest about what's exploratory.** Label secondary analyses and subgroups clearly.
- **Pre-registration alone does NOT curb p-hacking.** Only pre-registration WITH complete pre-analysis plans reduces it (Brodeur et al. 2024).
- **Design-hacking warning.** Unreported pilots that tweak design until something "works," then PAP that design = "overly confident view of robustness" (Coffman & Dreber 2025).
- **Registered Reports strongly recommended for existence experiments** — submit before data collection; journal publishes regardless of results. Eliminates null-result career risk. Also consider for other high-risk designs.
- **The design document is the source.** Pre-registration translates the approved design into registry format. If there's no design, run `/design experiment` first.
