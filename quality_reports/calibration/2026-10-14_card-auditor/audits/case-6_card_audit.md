# Card audit — prac:case-6
**Node:** prac:case-6
**Lean:** Calib2.case6
**Statement SHA-256:** 0000000000000000000000000000000000000000000000000000000000000000
**Verdict:** UNFAITHFUL
**Coverage:** PENDING
**Reviewer:** card-auditor (blind)

## Glossary

| Lean name / symbol | Plain mathematics |
|---|---|
| `priorWeight s0 x n` | Expanded body: `s0 / (n * s0 + x)`. A real-valued function of three reals. Its numerator is `s0`; its denominator is `n * s0 + x`, i.e. the numerator is the term that is *multiplied by n* in the denominator. The docstring calls `s0` the prior variance and `x` the signal-noise variance; the docstring is the formalizer's claim, not evidence — the body is as stated. |
| `case6_stmt` | ∀ real s0, x, n: if 0 < s0, 0 < x, 0 ≤ n, then 0 < s0/(n·s0 + x) and s0/(n·s0 + x) ≤ 1. |
| `/` on ℝ | Real division; Lean convention `a / 0 = 0` (junk value). Here the hypotheses force the denominator positive (n·s0 ≥ 0, x > 0), so no junk value arises. |
| `0 < _`, `_ ≤ 1`, `0 ≤ _` | Ordinary strict/weak real inequalities. |
| `ℝ` | The real numbers. `n` is a real variable, not a natural number. |

## Node

- Quantifiers: for all σ₀² > 0, σ_d² > 0, n ≥ 0.
- Hypotheses: σ₀² > 0; σ_d² > 0; n ≥ 0.
- Definition in the claim: w_n = σ_d² / (n·σ₀² + σ_d²) — numerator σ_d², the *additive* (non-n-multiplied) term of the denominator; the n-multiplied term is σ₀².
- Conclusion, conjunct 1: w_n > 0.
- Conclusion, conjunct 2: w_n ≤ 1 (interval (0, 1] — strict below, weak above).

## Lean

- Quantifiers: `∀ s0 x n : ℝ`.
- Hypotheses: `0 < s0`, `0 < x`, `0 ≤ n`.
- Definition in the claim: `priorWeight s0 x n = s0 / (n * s0 + x)` — numerator `s0`, which is the *n-multiplied* term of the denominator; the additive term is `x`.
- Conclusion, conjunct 1: `0 < priorWeight s0 x n`.
- Conclusion, conjunct 2: `priorWeight s0 x n ≤ 1`.

## Map

| Part | Node | Lean clause (verbatim) | Mark |
|---|---|---|---|
| Hypothesis σ₀² > 0 | σ₀² > 0 | `0 < s0` | equal (as a positivity hypothesis on the first variance) |
| Hypothesis σ_d² > 0 | σ_d² > 0 | `0 < x` | equal (as a positivity hypothesis on the second variance) |
| Hypothesis n ≥ 0 | n ≥ 0 | `0 ≤ n` with `n : ℝ` | equal-or-stronger: the node's n is a count of observations (plausibly ℕ); Lean quantifies over all reals n ≥ 0, claiming more. Harmless only if the formula were right; noted. |
| Weight formula | w_n = σ_d²/(n·σ₀² + σ_d²): numerator = additive term of denominator | `s0 / (n * s0 + x)`: numerator = n-multiplied term of denominator | **MIS-MAPPED (pattern 5)** — see below |
| Conjunct 1: w_n > 0 | w_n > 0 | `0 < priorWeight s0 x n` | equal in form, but about the wrong quantity |
| Conjunct 2: w_n ≤ 1 | w_n ≤ 1 | `priorWeight s0 x n ≤ 1` | equal in form, but about the wrong quantity; as stated the Lean conjunct is **false** (stronger, falsely) |

**The mis-mapping (pattern 5).** The node's weight has the structure B/(n·A + B), where B = σ_d² is the additive term and A = σ₀² is the n-multiplied term. The Lean body `s0 / (n * s0 + x)` has the structure A/(n·A + B): its numerator `s0` is the n-multiplied term. No renaming of (s0, x) to (σ₀², σ_d²) reconciles the two structures:

- Reading s0 = σ₀², x = σ_d² (the docstring's own reading), the Lean computes σ₀²/(n·σ₀² + σ_d²), not σ_d²/(n·σ₀² + σ_d²). Wrong numerator.
- Reading s0 = σ_d², x = σ₀², the Lean computes σ_d²/(n·σ_d² + σ₀²). Wrong denominator.

**Consequence: the Lean claim is false.** Take s0 = 4, x = 1, n = 0 (all hypotheses hold: 0 < 4, 0 < 1, 0 ≤ 0): `priorWeight 4 1 0 = 4 / (0·4 + 1) = 4 > 1`, contradicting `priorWeight s0 x n ≤ 1`. So `case6_stmt` is not merely a relabeling of the node — it asserts something stronger than the node (about a different formula) and it is false.

No dropped hypotheses (pattern 1), no added hypotheses beyond the ℝ-vs-ℕ widening of n noted above (pattern 2), no weakened conclusion (pattern 3), no omitted conjunct (pattern 4), no quantifier-order issue (pattern 6). Junk values (pattern 7): division by zero cannot occur under the hypotheses (denominator n·s0 + x ≥ x > 0). Domain/type (pattern 8): n : ℝ noted above. Vacuity (pattern 9): hypotheses are jointly satisfiable (e.g. s0 = x = 1, n = 0).

## Sanity values

Parameters (σ₀², σ_d², n) = (1, 4, 1).

**Node, step by step:**
- Denominator: n·σ₀² + σ_d² = 1·1 + 4 = 5.
- Numerator: σ_d² = 4.
- w_n = 4/5 = **0.8**. (Check: 0 < 0.8 ≤ 1. The node's claim holds here.)

**Lean helper at those parameters,** under the docstring's mapping s0 = σ₀² = 1, x = σ_d² = 4, n = 1:
- `priorWeight 1 4 1 = 1 / (1·1 + 4) = 1/5` = **0.2**.

**They disagree:** 0.8 ≠ 0.2. (Under the swapped mapping s0 = 4, x = 1: `priorWeight 4 1 1 = 4 / (1·4 + 1) = 4/5` = 0.8, which agrees numerically at this parameter point — but that mapping fails structurally, as shown in the Map section, and the Lean claim is false at n = 0 regardless.)

## Verdict

**UNFAITHFUL.**

The Lean helper `priorWeight s0 x n := s0 / (n * s0 + x)` puts the n-multiplied variance in the numerator, where the node puts the additive variance (σ_d²). The Lean statement therefore formalizes a different formula, its value at the sanity parameters (0.2) disagrees with the node's (0.8), and the Lean claim `priorWeight s0 x n ≤ 1` is false outright (counterexample s0 = 4, x = 1, n = 0 gives 4 > 1). A faithful body would be `x / (n * s0 + x)` under the docstring's variable naming.
