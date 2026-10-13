# Card audit — prac:case-2
**Node:** prac:case-2
**Lean:** Calib2.case2
**Statement SHA-256:** 0000000000000000000000000000000000000000000000000000000000000000
**Verdict:** FAITHFUL
**Coverage:** PENDING
**Reviewer:** card-auditor (blind)

## Glossary

| Lean name / symbol | Plain mathematics |
|---|---|
| `postVar s0 x n` | Helper `def`, body expanded: `s0 * x / (n * s0 + x)`, i.e. the real number s0·x / (n·s0 + x). With s0 ↦ σ₀², x ↦ σ_d², this is σ₀²σ_d² / (nσ₀² + σ_d²), the node's σ_n². |
| `s0 x n : ℝ` | Three real variables: prior variance, noise variance, sample size. Note `n` is a real, not a natural. |
| `0 < s0`, `0 < x` | Strict positivity of σ₀² and σ_d². |
| `0 ≤ n` | n nonnegative. |
| `/` on ℝ | Real division; Lean's `a / 0 = 0` junk convention applies only when the denominator is 0 (see Map, pattern 7). |
| `∧` | Conjunction: both conclusion parts claimed. |
| `case2_stmt : Prop` | The statement proposition: ∀ s0 x n ∈ ℝ, 0 < s0 → 0 < x → 0 ≤ n → 0 < postVar s0 x n ∧ postVar s0 x n ≤ s0. |

Naming note: the dispatcher labels the Lean as `Calib2.case2`, but the statement file declares the Prop `Calib2.case2_stmt` (and the helper `Calib2.postVar`); no declaration named `case2` appears in the file. I audited `case2_stmt` as the statement. This is recorded for the owner; it is a labelling matter, not a mathematical difference.

## Node

- Quantifiers: for all σ₀², σ_d², n (implicitly universal over the named parameters).
- Hypotheses: (H1) σ₀² > 0; (H2) σ_d² > 0; (H3) n ≥ 0.
- Definition: σ_n² = σ₀²σ_d² / (nσ₀² + σ_d²).
- Conclusion, conjunct (C1): 0 < σ_n² (strict positivity).
- Conclusion, conjunct (C2): σ_n² ≤ σ₀² (weak upper bound).

## Lean

From the code of `case2_stmt` alone:

- Quantifiers: `∀ s0 x n : ℝ` — universal over three reals, in that order, before any hypothesis.
- Hypotheses: `0 < s0`; `0 < x`; `0 ≤ n`.
- Definition: `postVar s0 x n`, whose expanded body is `s0 * x / (n * s0 + x)`.
- Conclusion, conjunct 1: `0 < postVar s0 x n`.
- Conclusion, conjunct 2: `postVar s0 x n ≤ s0`.

## Map

| Part | Node | Lean clause (verbatim) | Mark |
|---|---|---|---|
| Quantifier | ∀ σ₀², σ_d², n | `∀ s0 x n : ℝ` | equal (see pattern 8 note) |
| H1 | σ₀² > 0 | `0 < s0` | equal |
| H2 | σ_d² > 0 | `0 < x` | equal |
| H3 | n ≥ 0 | `0 ≤ n` | equal |
| Formula | σ₀²σ_d²/(nσ₀²+σ_d²) | `s0 * x / (n * s0 + x)` | equal (term by term: numerator σ₀²·σ_d²; denominator n·σ₀² + σ_d²) |
| C1 | 0 < σ_n² | `0 < postVar s0 x n` | equal (strict, as in node) |
| C2 | σ_n² ≤ σ₀² | `postVar s0 x n ≤ s0` | equal (weak ≤, as in node) |

Failure-pattern check:

1. Dropped hypothesis — none: all three node assumptions appear (`0 < s0`, `0 < x`, `0 ≤ n`).
2. Added hypothesis — none beyond the node's three.
3. Weakened conclusion — no: C1 keeps strict `<`; C2's `≤` matches the node's `≤`.
4. Omitted conjunct — no: both conjuncts present via `∧`.
5. Mis-mapped symbol — no: `postVar` expanded; numerator is `s0 * x` (prior times noise, as in node), denominator `n * s0 + x` (n times the prior variance plus the noise variance, as in node). The variances are not swapped: swapping would give denominator `n * x + s0`, which is not what the code says.
6. Quantifier order — no: all universals precede all hypotheses; no existentials anywhere.
7. Junk values — division is the only risk. Denominator `n * s0 + x`: under the hypotheses, n·s0 ≥ 0 and x > 0, so n·s0 + x > 0 and Lean's `a / 0 = 0` convention is never reached inside the claimed domain. No junk value can make the claim true or false for the wrong reason.
8. Domain and type — `n : ℝ` with `0 ≤ n`, where the node's n (a sample size) is naturally a nonnegative integer. The node's statement as given says only "n ≥ 0" without a type, and the Lean universal over all real n ≥ 0 subsumes every nonnegative integer. If the node intends integer n, the Lean claims strictly more; the extra instances are true (same algebra), so this is not a weakening and not a false strengthening. Recorded as a note, not a difference in what is claimed about the node's cases.
9. Vacuity — no: e.g. (s0, x, n) = (1, 1, 1) satisfies all hypotheses.

## Sanity values

Parameters (σ₀², σ_d², n) = (1, 1, 1).

Node side, step by step:
- Denominator: n·σ₀² + σ_d² = 1·1 + 1 = 2.
- Numerator: σ₀²·σ_d² = 1·1 = 1.
- σ_n² = 1/2.
- Conclusion check: 0 < 1/2 ✓ and 1/2 ≤ 1 ✓.

Lean side, from the helper's body:
- `postVar 1 1 1 = 1 * 1 / (1 * 1 + 1) = 1 / 2`.

They agree: both give σ_n² = 1/2, and both conclusion conjuncts hold at these parameters.

## Verdict

**FAITHFUL.** Every hypothesis, the defining formula, and both conclusion conjuncts of the Lean statement are equal to the node's, with the helper expanded and compared term by term. The only observations, neither a difference in claim: (a) `n` is quantified over ℝ (≥ 0) where a sample size is naturally an integer — the Lean subsumes the node's cases and the extra ones are true; (b) the declaration in the statement file is `Calib2.case2_stmt`, while the dispatcher's label is `Calib2.case2`.
