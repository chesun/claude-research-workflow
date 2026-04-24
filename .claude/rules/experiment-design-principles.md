# Experiment Design Principles

**Scope:** `experiments/**`, `designs/**`
**Status:** Always-on for behavioral/experimental economics projects

These 13 principles are non-negotiable. Every experiment must satisfy all of them before data collection begins. Agents that touch experiment files must internalize these.

---

## The 13 Principles

### 1. Inference First
Design your experiment with inference in mind from the start. Know what you need to demonstrate statistically — the tests, estimands, null hypotheses, and clustering strategy — while designing treatments, not after. Design and inference co-evolve: your "dream outcome" (Niederle) shapes the treatment structure, and the treatment structure determines what tests are feasible. When inference needs conflict with design convenience, inference wins. Test selection follows Moffatt's guide. Multiple hypothesis testing correction specified upfront. This applies equally to theory-testing experiments (model predicts X) and existence experiments (we hypothesize X exists) — the requirement is a specific hypothesis with a specific comparison, not a formal model. "Hypothesis-driven, not 'stuff happens'" (Niederle).

### 2. Subject Comprehension
Instructions must be clear, under 3 pages, and pretested with non-experts. Pretesters answer: What decision am I making? How do I make it? Where do I record it? What are possible outcomes? Understanding checks are required and must be pre-treatment.

### 3. Interface Intentionality
Every elicitation method choice must be documented with justification. Compare alternatives (BDM, binary choices, MPL, convex budget, DOSE, survey). Know the IC assumption each method requires (Healy & Leo hierarchy: statewise monotonicity < S-O reduction < risk-neutral EU). Check for centering bias (MPL), multiple switching (16% in Holt-Laury), and reference point effects.

### 4. Simplicity
The shortest experiment that answers the question is the best experiment. Every screen, every question, every treatment arm must justify its existence. If removing an element doesn't weaken the test, remove it.

### 5. Incentive Compatibility
Payment structure must align incentives with truthful behavior. Cite the theoretical basis for IC (not just "standard practice"). Random round payment requires monotonicity assumption (Azrieli et al. 2018) — problematic if studying independence violations. Stakes must be comparable across treatments. "Very small incentives can be worse than none" (Gneezy & Rustichini 2000).

### 6. Floor/Ceiling Awareness
Analyze bounded variables for compression risk. Focal value responses reach 60-70% in some tasks (Snowberg & Yariv 2025). Diagnose via responsiveness checks. Design response scales to avoid boundary effects.

### 7. Pre-Registration Mandatory
No data collection without registered hypotheses and primary analysis plan. This means goal, design, N, and main hypothesis — not necessarily a rigid pre-analysis plan that stifles innovation (Niederle 2025). Pre-registration alone does NOT curb p-hacking; only pre-registration WITH complete pre-analysis plans reduces it (Brodeur et al. 2024). Consider Registered Reports for high-risk designs.

### 8. Budget Realism
Expected payment x N x platform fee calculated before launch. Budget sensitivity: what if N needs to increase 50%? Differential attrition planning: balance time/effort across arms.

### 9. Pilot When Needed
Pilot for debugging (instructions, timing, comprehension), not for confirming hypotheses. Simple, well-understood paradigms may not need pilots. Beware pilot dangers: anchoring to a design that "worked," chasing side results, repeated piloting = design-hacking (Niederle 2025). Every data collection must be declared in advance as pilot or real study.

### 10. No Deception
Never deceive participants. Intentional vagueness or omission of details is acceptable; outright deception is not. If a design requires deception, redesign the experiment. This is both an ethical principle and a practical one — the experimental economics subject pool's trust depends on it.

### 11. Collect Response Time Always
RT is free, informative, and enables DDM-based preference estimation. Log-transform for regression analysis. Screen out very fast responses (guessing) and very slow responses (inattention). Record hardware type (trackpad vs. mouse) if using mouse-tracking. (Brocas et al. 2025)

### 12. Measurement Error Awareness
Budget for noise: 30-50% of variance in elicited measures is measurement error (Gillen et al. 2019). Mitigation: (1) careful design with training rounds and visual aids, (2) multiple elicitations with ORIV correction or averaging, (3) exclude noisy data via pre-registered comprehension criteria, (4) econometric corrections (MLE/Bayesian with noise parameters). Never treat a single elicitation as ground truth. When noisy elicitation is used as a covariate, false positive rates approach 100% in large samples (Chapman & Fisher 2025).

### 13. Parameter Selection Discipline
Choose parameters to maximize the relevant objective (Snowberg & Yariv 2025):
- Document irregularity → maximize distance from benchmark
- Discriminate models → maximize distance between predictions
- Institutional design → maximize welfare vs. status quo
- Policy evaluation → echo real-world parameters

Check for: flat incentive functions (reduce reliability), corner solutions (noise compresses toward center), misperception sensitivity (5% error flips optimal action?), multiple equilibria (confounds with coordination). Guard against design-hacking: justify parameter selection transparently; 30%+ of common ratio experiments use K&T (1979) parameters with effects smaller/reversed at other values.

---

## One-Factor-at-a-Time Rule

Each treatment must differ from its comparison on exactly ONE dimension. Two simultaneous changes = confounded design. For every treatment arm, state: "Comparison of Arm A vs Arm B identifies [specific mechanism] because the ONLY difference is [specific change]." (Croson 2005)

## Alternative Hypothesis Controls (Niederle 2025)

Every design must address alternative explanations via at least one strategy:
1. **Design by elimination** — game where your model has no "bite"
2. **Direct controls** — eliminate confounding force by design
3. **Indirect controls** — measure separately, control econometrically (caveat: measurement accuracy)
4. **"Do it both ways"** — find environment where your model predicts opposite direction from alternative
5. **Stress-testing** — check auxiliary predictions after main result
