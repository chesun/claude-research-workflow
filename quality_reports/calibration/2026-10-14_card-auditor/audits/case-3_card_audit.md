# Card audit — prac:case-3
**Node:** prac:case-3
**Lean:** Calib2.case3
**Statement SHA-256:** 0000000000000000000000000000000000000000000000000000000000000000
**Verdict:** UNFAITHFUL
**Coverage:** PENDING
**Reviewer:** card-auditor (blind)

## Glossary

| Lean name / symbol | Plain mathematics |
|---|---|
| `Calib2.postVar s0 x n` | Body expanded: `s0 * x / (n * s0 + x)`, i.e. s0·x/(n·s0 + x), real division. With s0 ↦ σ₀², x ↦ σ_d², n ↦ n this is the node's σ_n² = σ₀²σ_d²/(nσ₀² + σ_d²), term by term. |
| `case3_stmt : Prop` | The audited proposition (a `def` of type `Prop`; no theorem named `case3` appears in the statement file). |
| `∀ s0 x : ℝ, 0 < s0 → 0 < x →` | For all real s0 > 0 and x > 0. |
| `∃ N : ℝ` | There exists a real N (not a natural-number sample size). |
| `∀ ε : ℝ, 0 < ε →` | For every real ε > 0. |
| `∀ n : ℝ, N ≤ n →` | For every real n ≥ N (n is real, not a natural number). |
| `postVar s0 x n < ε` | σ_n² < ε, strict. |
| `/` on ℝ | Mathlib real division; `a / 0 = 0` (junk value — considered below). |

The docstring on `case3_stmt` ("For every ε > 0 there is an N …") describes ∀ε ∃N; the code says ∃N ∀ε. Per protocol the docstring is a claim, not evidence; I audit the code.

## Node

Quantifiers in order, then hypotheses, then conclusion:

1. ∀ σ₀² > 0 (hypothesis: σ₀² > 0),
2. ∀ σ_d² > 0 (hypothesis: σ_d² > 0),
3. ∀ ε > 0,
4. ∃ N (a sample size),
5. ∀ n ≥ N:
6. conclusion (single conjunct): σ_n² < ε, where σ_n² = σ₀²σ_d²/(nσ₀² + σ_d²).

Quantifier shape: **∀σ₀² ∀σ_d² ∀ε ∃N ∀n**. N may depend on ε.

## Lean

From the code of `case3_stmt` alone:

1. ∀ s0 : ℝ, s0 > 0,
2. ∀ x : ℝ, x > 0,
3. ∃ N : ℝ,
4. ∀ ε : ℝ, ε > 0,
5. ∀ n : ℝ, n ≥ N:
6. conclusion: s0·x/(n·s0 + x) < ε.

Quantifier shape: **∀s0 ∀x ∃N ∀ε ∀n**. N must be chosen before ε and work for every ε > 0 simultaneously.

## Map

| Node part | Lean clause | Mark |
|---|---|---|
| σ₀² > 0 hypothesis | `0 < s0 →` | equal |
| σ_d² > 0 hypothesis | `0 < x →` | equal |
| σ_n² formula | `postVar s0 x n` = `s0 * x / (n * s0 + x)` | equal (helper expanded; variables map correctly) |
| ∀ε ∃N order | `∃ N : ℝ, ∀ ε : ℝ, 0 < ε →` | **stronger — pattern 6 (quantifier order).** The node lets N depend on ε (∀ε ∃N). The Lean fixes one N for all ε (∃N ∀ε). The Lean claim is strictly stronger and is **false**: for any real N, take n = max(N, 0) ≥ N; then n·s0 + x > 0 and postVar = s0·x/(n·s0 + x) > 0, so choosing ε = postVar/2 > 0 violates `postVar s0 x n < ε`. |
| n a sample size (ℕ) | `∀ n : ℝ, N ≤ n →` and `∃ N : ℝ` | **stronger — pattern 8 (domain and type).** The node quantifies over sample sizes (natural numbers n ≥ N); the Lean quantifies over all real n ≥ N. Here postVar is decreasing in n on the relevant range, so with the correct quantifier order this widening would be harmless, but it is a difference and is noted. |
| conclusion σ_n² < ε (strict) | `postVar s0 x n < ε` | equal (strict `<` preserved) |

Other patterns checked: 1 dropped hypothesis — none (both positivity hypotheses present). 2 added hypothesis — none. 3 weakened conclusion — no (strict `<` kept). 4 omitted conjunct — none (single conjunct present). 5 mis-mapped symbol — no (`postVar` expanded above matches σ_n² exactly). 7 junk values — division `a / 0 = 0` is unreachable when N can force n·s0 + x > 0, but because the Lean's ∃N comes first and n ranges over all reals ≥ N, if a prover picked a negative N the denominator could cross 0; this cannot rescue the statement (it is already false by the pattern-6 argument) and introduces no true-for-the-wrong-reason route. 9 vacuity — hypotheses 0 < s0, 0 < x, 0 < ε are jointly satisfiable; not vacuous.

## Sanity values

Parameters (σ₀², σ_d², ε) = (1, 1, 1/4).

Node-side computation, step by step:
- σ_n² = (1·1)/(n·1 + 1) = 1/(n + 1).
- Require 1/(n + 1) < 1/4 ⟺ n + 1 > 4 ⟺ n > 3.
- Need this for **every** n ≥ N. At n = N the requirement is 1/(N + 1) < 1/4 ⟺ N > 3; for n > N it then holds since 1/(n+1) is decreasing.
- Over the **reals** the set of valid N is the open interval (3, ∞): N = 3 fails because σ_3² = 1/4 is not < 1/4. So there is **no smallest real N**; the infimum is **3**, and any N > 3 works. If n is restricted to integer sample sizes, the smallest integer N is **4**.

Lean-side at the same parameters: `postVar 1 1 n` = 1·1/(n·1 + 1) = 1/(n + 1) — the helper agrees with the node's σ_n² exactly. But the Lean proposition demands one N with 1/(n+1) < ε for **every** ε > 0 and every real n ≥ N, i.e. 1/(n+1) ≤ 0 on [N, ∞), which no real N satisfies (e.g. n = max(N, 0) gives 1/(n+1) > 0). The node's instance at ε = 1/4 is true (any N > 3); the Lean's instance is false. They disagree.

## Verdict

**UNFAITHFUL.**

The decisive difference is pattern 6: the node says ∀ε > 0 ∃N ∀n ≥ N (N may depend on ε — convergence of σ_n² to 0); the Lean `case3_stmt` says `∃ N : ℝ, ∀ ε : ℝ, 0 < ε → ∀ n : ℝ, N ≤ n → postVar s0 x n < ε` (one N for all ε). The Lean claim is strictly stronger than the node and is mathematically false, since postVar s0 x n > 0 for any n ≥ max(N, 0) when s0, x > 0. A secondary noted difference (pattern 8): n and N are reals in the Lean where the node's sample sizes are natural numbers. The helper `postVar` itself maps the node's variance formula faithfully.

Also noted: the dispatcher names the Lean as `Calib2.case3`, but the statement file contains only the Prop-valued `def Calib2.case3_stmt` (and the helper `postVar`); no declaration named `case3` exists in the file read.
