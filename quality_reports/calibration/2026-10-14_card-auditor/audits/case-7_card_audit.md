# Card audit — prac:case-7
**Node:** prac:case-7
**Lean:** Calib2.case7
**Statement SHA-256:** 0000000000000000000000000000000000000000000000000000000000000000
**Verdict:** UNFAITHFUL
**Coverage:** PENDING
**Reviewer:** card-auditor (blind)

## Glossary

| Lean name / symbol | Meaning in plain mathematics |
|---|---|
| `Calib2.gfun c x` | Body expanded: `-x - c / x`, i.e. g(x) = −x − c/x as a function of x with parameter c, on all of ℝ. |
| `case7_stmt` | A `Prop`-valued `def` carrying the whole claim (the file defines `case7_stmt`; no theorem named `case7` appears in the file read). |
| `∀ c : ℝ, 0 < c → …` | Universal quantification over real c with hypothesis c > 0. |
| `IsMaxOn f s a` | ∀ x ∈ s, f x ≤ f a: a is a (not necessarily strict or unique) maximizer of f on the set s. It does not by itself require a ∈ s. |
| `Set.Ioi (0 : ℝ)` | The open interval (0, ∞), i.e. {x : ℝ ∣ 0 < x}. |
| `Real.sqrt c` | The real square root; equals √c for c ≥ 0 (junk value 0 for c < 0, irrelevant here since 0 < c is hypothesized). |
| `c / x` | Real division; junk value c/0 = 0 at x = 0, irrelevant on `Set.Ioi 0` where x > 0. |

## Node

- Quantifiers / parameters: for every real c with c > 0 (hypothesis), on the domain x > 0.
- Conclusion, conjunct (a): g(x) = −x − c/x attains its maximum on {x > 0} at x* = √c.
- Conclusion, conjunct (b): the maximum value is g(x*) = −2√c.

## Lean

`∀ c : ℝ, 0 < c → IsMaxOn (gfun c) (Set.Ioi (0 : ℝ)) (Real.sqrt c)`

- Quantifier: ∀ c : ℝ; hypothesis 0 < c.
- Single conclusion: for every x ∈ (0, ∞), gfun c x ≤ gfun c (√c), i.e. −x − c/x ≤ −√c − c/√c. √c itself lies in (0, ∞) because c > 0, so the maximizer is in the domain.
- There is no clause asserting the value of g at √c.

## Map

| Part | Node | Lean clause | Mark |
|---|---|---|---|
| Quantifier over c | every c > 0 | `∀ c : ℝ, 0 < c →` | equal |
| Domain x > 0 | open half-line | `Set.Ioi (0 : ℝ)` | equal (open interval, matches strict x > 0; no x = 0 junk division reachable) |
| Function | g(x) = −x − c/x | `gfun c x = -x - c / x` (body expanded) | equal |
| Maximum at x* = √c | attains its maximum at √c | `IsMaxOn (gfun c) (Set.Ioi (0 : ℝ)) (Real.sqrt c)` | equal (IsMaxOn is a non-strict maximum; the node's "attains its maximum at x*" is matched. The node does not assert uniqueness of the maximizer, so non-strictness is not a weakening.) |
| Maximum value g(x*) = −2√c | asserted by the node | **no corresponding Lean clause** — the statement is only `IsMaxOn (gfun c) (Set.Ioi (0 : ℝ)) (Real.sqrt c)` | **missing** (failure pattern 4, omitted conjunct) |

Failure-pattern sweep: (1) no dropped hypothesis — 0 < c present; (2) no added hypothesis; (3) no weakened conclusion in the retained conjunct; (4) **omitted conjunct — the value −2√c is absent**; (5) helper `gfun` expands to exactly the node's formula; (6) quantifier order matches; (7) junk values (c/0, √ of a negative) unreachable under 0 < c and x ∈ (0, ∞); (8) types and domain correct (ℝ, open interval); (9) hypotheses satisfiable (any c > 0).

## Sanity values

Parameters c = 4, node side, computed step by step:
- x* = √c = √4 = 2.
- g(x*) = −x* − c/x* = −2 − 4/2 = −2 − 2 = −4.
- −2√c = −2·√4 = −2·2 = −4. Consistent: g(x*) = −2√c = −4.
- Spot check that 2 is a maximizer: g(1) = −1 − 4 = −5 ≤ −4; g(4) = −4 − 1 = −5 ≤ −4. ✓

Lean side at c = 4:
- `Real.sqrt 4` = 2.
- `gfun 4 2` = −2 − 4/2 = −4.
- Agreement: the Lean helper values match the node's values at the sanity point. However, the Lean statement itself contains no clause asserting `gfun c (Real.sqrt c) = -2 * Real.sqrt c`, so the value conjunct is unverified by the Lean statement — there is nothing in the code for the −4 to be checked against.

## Verdict

**UNFAITHFUL.** The node's conclusion has two conjuncts; the Lean states only the first. The maximum-value claim g(x*) = −2√c is omitted from `case7_stmt` (pattern 4). A proof of `case7_stmt` would not certify the node's value claim. All other parts are equal.
