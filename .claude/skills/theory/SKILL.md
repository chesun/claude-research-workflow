---
name: theory
description: |
  Formal model development and proof review. Two modes: develop (build model
  from assumptions to testable predictions) and review (verify proofs, check
  assumptions, audit notation). Dispatches theorist and theorist-critic agents.
argument-hint: "[develop | review] [topic or file path] [--proofs | --assumptions | --predictions]"
allowed-tools: Read,Grep,Glob,Write,Task
---

# Theory

Develop or review formal theoretical models by dispatching the **Theorist** (builder) and **theorist-critic** (verifier).

**Input:** `$ARGUMENTS` — mode keyword followed by topic or file path.

---

## Modes

### `/theory develop [topic]` — Build a Formal Model

Develop a model from assumptions through equilibrium to testable predictions.

**Agents:** Theorist → theorist-critic
**Output:** model.tex + proofs + testable predictions

**Workflow:**

1. Read research spec, literature review, and existing theory notes if they exist
2. Read `quality_reports/paper_learnings/theory-writing-learnings.md` for Thomson/Varian/Board rules
3. Dispatch **Theorist** following the Varian KISS workflow:
   - Start with the simplest possible example (2 agents, 2 goods)
   - Work several examples to find the pattern
   - Build the general model
   - State assumptions, definitions (with boundary examples), and notation
   - Derive equilibrium/solution
   - Prove comparative statics
   - Extract testable predictions that feed into `/design experiment`
4. Dispatch **theorist-critic** to audit via 16-item checklist:
   - Formal correctness (5 items)
   - Notation and terminology (5 items)
   - Proof quality (3 items)
   - Completeness (3 items)
   - Plus Board & Meyer-ter-Vehn architecture checks and Thomson figure standards
5. If issues found, iterate (max 3 rounds)
6. Save to `theory/model.tex` and `theory/proofs/`
7. Save testable predictions to `quality_reports/designs/` for the designer agent

### `/theory review [file]` — Review Existing Theory

Review proofs, check derivations, verify predictions follow from model.

**Agents:** theorist-critic (standalone)
**Output:** Review report

**Flags:**
- `--proofs` — Focus on proof verification (correctness, completeness, style)
- `--assumptions` — Focus on assumption audit (independence, necessity, boundary conditions)
- `--predictions` — Focus on whether predictions actually follow from the model

**Workflow:**

1. Read the target file(s)
2. Read `quality_reports/paper_learnings/theory-writing-learnings.md`
3. Dispatch **theorist-critic** with the appropriate focus:
   - Full 16-item checklist (default)
   - Proof-focused: direct proofs preferred, steps synchronized, quantifiers unambiguous, math-to-English ratio
   - Assumption-focused: each independently needed, non-vacuous examples exist, boundary examples provided
   - Prediction-focused: do predictions follow from the model? Are they unique vs. alternatives? Testable?
4. Save report to `quality_reports/theory_review_[file].md`

---

## Principles

- **Theorist builds, theorist-critic verifies.** Separation of powers.
- **Simplest version first.** Varian KISS: if you can show it with 2 agents, don't use N agents.
- **Theorems are English takeaways.** Board & Meyer-ter-Vehn: every theorem should be a statement a non-theorist can understand that also happens to be mathematically true.
- **One paper, one model.** If you need two models, you might need two papers.
- **Main result by page 15.** Don't bury the contribution.
- **Predictions feed design.** The testable predictions from theory are the direct input to `/design experiment`.
- **Never fabricate proofs.** If a step is unclear, flag it as [VERIFY] rather than guessing.
