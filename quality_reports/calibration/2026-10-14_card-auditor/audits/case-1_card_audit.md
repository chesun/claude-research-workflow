# Card audit — prac:case-1
**Node:** prac:case-1
**Lean:** Calib2.case1
**Statement SHA-256:** 0000000000000000000000000000000000000000000000000000000000000000
**Verdict:** UNFAITHFUL
**Coverage:** PENDING
**Reviewer:** card-auditor (blind)

## Glossary

| Lean name / symbol | Plain mathematics |
|---|---|
| `Calib2.postVar s0 x n` | Body expanded: `s0 * x / (n * s0 + x)`, i.e. s0·x / (n·s0 + x), a real-valued function of reals. With s0 = σ₀² and x = σ_d², this is σ₀²σ_d²/(nσ₀² + σ_d²), the node's σ_n². |
| `Calib2.case1_stmt` | The `Prop`: for all real s0, x, if 0 < s0 and 0 < x then `postVar s0 x` is antitone on [0, ∞). |
| `AntitoneOn f s` | Non-strict: for all a, b ∈ s, a ≤ b → f b ≤ f a. It does **not** say f b < f a for a < b. |
| `Set.Ici (0 : ℝ)` | The closed ray [0, ∞) in ℝ, i.e. {n : ℝ ∣ 0 ≤ n}. |
| `/` on ℝ | Mathlib real division; division by 0 yields 0 (junk value). On the stated domain the denominator n·s0 + x ≥ 0·s0 + x = x > 0, so no junk value arises. |

## Node

- **Quantifiers:** implicitly universal over σ₀², σ_d² (and over sample sizes n in the monotonicity claim).
- **Hypotheses:** (H1) σ₀² > 0; (H2) σ_d² > 0.
- **Conclusion (single conjunct):** (C1) the function n ↦ σ_n² = σ₀²σ_d²/(nσ₀² + σ_d²) is **strictly decreasing** in n on n ≥ 0.

## Lean

From the code of `case1_stmt` alone:

- **Quantifiers:** `∀ s0 x : ℝ` — universal over both parameters.
- **Hypotheses:** `0 < s0`, `0 < x`.
- **Conclusion:** `AntitoneOn (postVar s0 x) (Set.Ici (0 : ℝ))` — the function n ↦ s0·x/(n·s0 + x) is **non-strictly** decreasing (antitone) on [0, ∞).

## Map

| Part | Node | Lean clause (verbatim) | Mark |
|---|---|---|---|
| Quantifier over parameters | ∀ σ₀², σ_d² | `∀ s0 x : ℝ` | equal |
| H1: σ₀² > 0 | yes | `0 < s0` | equal |
| H2: σ_d² > 0 | yes | `0 < x` | equal |
| Formula for σ_n² | σ₀²σ_d²/(nσ₀² + σ_d²) | `s0 * x / (n * s0 + x)` (body of `postVar`) | equal (term-by-term: numerator s0·x = σ₀²σ_d²; denominator n·s0 + x = nσ₀² + σ_d²) |
| Domain of n | n ≥ 0 | `Set.Ici (0 : ℝ)` | equal as a set ([0, ∞)); note the Lean takes n real, which subsumes integer sample sizes — not a defect given the node says "on n ≥ 0" |
| C1: strictly decreasing | **strict** decrease | `AntitoneOn (postVar s0 x) (Set.Ici (0 : ℝ))` | **weaker** — pattern 3 (weakened conclusion): `AntitoneOn` asserts only a ≤ b → f(b) ≤ f(a); strict decrease requires `StrictAntiOn` (a < b → f(b) < f(a)). A constant function satisfies `AntitoneOn`; it does not satisfy the node's claim. |

Failure-pattern sweep:
1. Dropped hypothesis — none; both positivity hypotheses present.
2. Added hypothesis — none.
3. Weakened conclusion — **yes**: `AntitoneOn` where the node says strictly decreasing (see map row C1).
4. Omitted conjunct — none; the node has one conclusion.
5. Mis-mapped symbol — none; `postVar` expanded and matched term by term.
6. Quantifier order — fine; parameters quantified before hypotheses before conclusion.
7. Junk values — division by zero cannot occur on the domain: for n ∈ [0, ∞), s0 > 0, x > 0, the denominator n·s0 + x ≥ x > 0.
8. Domain and type — n is ℝ with `Set.Ici 0`, matching "on n ≥ 0" read over the reals; closed at 0 as the node requires.
9. Vacuity — hypotheses 0 < s0, 0 < x are jointly satisfiable (e.g. s0 = x = 1).

## Sanity values

Parameters (σ₀², σ_d²) = (1, 1).

**Node, by hand:**
- n = 0: σ_n² = (1·1)/(0·1 + 1) = 1/1 = **1**.
- n = 1: σ_n² = (1·1)/(1·1 + 1) = 1/2 = **0.5**.

**Lean helper `postVar 1 1 n`:**
- n = 0: 1 * 1 / (0 * 1 + 1) = 1/1 = **1**.
- n = 1: 1 * 1 / (1 * 1 + 1) = 1/2 = **0.5**.

They agree at both points, and 1 > 0.5 is consistent with the claimed decrease.

## Verdict

**UNFAITHFUL.** The node asserts *strict* decrease; the Lean conclusion `AntitoneOn (postVar s0 x) (Set.Ici (0 : ℝ))` is non-strict (pattern 3, weakened conclusion). Everything else — quantifiers, both hypotheses, the σ_n² formula, the domain [0, ∞), and the sanity values — is equal. The faithful form would use `StrictAntiOn` in place of `AntitoneOn`.
