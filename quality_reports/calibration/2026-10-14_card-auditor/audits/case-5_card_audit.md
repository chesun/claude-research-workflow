# Card audit — prac:case-5
**Node:** prac:case-5
**Lean:** Calib2.case5
**Statement SHA-256:** 0000000000000000000000000000000000000000000000000000000000000000
**Verdict:** UNFAITHFUL
**Coverage:** PENDING
**Reviewer:** card-auditor (blind)

## Glossary

| Lean name / symbol | Plain mathematics |
|---|---|
| `Calib2.avgCost F c q` | Expanded body: `F / q + c`, a real number. Over ℝ, Lean's division is total with the junk value `x / 0 = 0`, so `avgCost F c 0 = 0 + c = c`. |
| `Calib2.case5_stmt` | The statement Prop in the file (note: the dispatcher names the Lean `Calib2.case5`; the only statement `def` in the file is `case5_stmt`). Expanded body: `∀ F c q : ℝ, 0 < F → 0 < c → 0 ≤ q → avgCost F c q > c`. |
| `ℝ` | The real numbers. |
| `0 < F`, `0 < c` | Strict positivity of F and c. |
| `0 ≤ q` | q is non-negative (zero allowed). |
| `>` on ℝ | Strict greater-than. `a > c` means `c < a`. |

## Node

- Quantifiers / hypotheses, in order: F > 0; c > 0; for every output q with **q > 0** (strict).
- Conclusion (single conjunct): AC(q) = F/q + c is **strictly greater** than c, i.e. F/q + c > c.

## Lean

From the code of `case5_stmt` alone, with `avgCost` expanded:

- Quantifiers / hypotheses, in order: ∀ F c q : ℝ; `0 < F`; `0 < c`; **`0 ≤ q`** (zero allowed).
- Conclusion (single conjunct): `F / q + c > c` (strict).

## Map

| Part | Node | Lean | Mark |
|---|---|---|---|
| Hypothesis F > 0 | F > 0 | `0 < F` | equal |
| Hypothesis c > 0 | c > 0 | `0 < c` | equal |
| Domain of q | q > 0 (strict) | `0 ≤ q` | **stronger — and false** |
| Conclusion | F/q + c > c, strict | `avgCost F c q > c`, i.e. `F / q + c > c` | equal in form, but asserted on the enlarged domain |

**The difference, with the Lean clause cited.** The node restricts to q > 0; the Lean hypothesis is `0 ≤ q`, so the Lean universal claim also covers q = 0. This is failure pattern 7 (junk values) combined with pattern 8 (domain): in Lean, `F / 0 = 0`, so at q = 0 the body of `avgCost` gives `avgCost F c 0 = F / 0 + c = 0 + c = c`, and the conclusion `avgCost F c 0 > c` becomes `c > c`, which is false for every c. The Lean statement therefore claims strictly more than the node (it includes q = 0) and is **false as written**: e.g. F = 2, c = 1, q = 0 satisfies `0 < F`, `0 < c`, `0 ≤ q` but `avgCost 2 1 0 = 1 > 1` fails. No proof of `case5_stmt` can exist, and any weakening made later to prove it would not be the node's statement.

Checked against the remaining failure patterns: no dropped or added hypothesis on F or c (patterns 1–2); conclusion strictness preserved, `>` not `≥` (pattern 3); the node has a single conjunct and it is present (pattern 4); `avgCost` expanded term by term matches F/q + c (pattern 5); quantifier order ∀F ∀c ∀q matches the node (pattern 6); hypotheses are jointly satisfiable, so no vacuity (pattern 9); types are ℝ throughout, as the node intends (pattern 8, beyond the domain defect already flagged).

## Sanity values

Parameters (F, c, q) = (2, 1, 1).

- **Node, by hand:** AC(1) = F/q + c = 2/1 + 1 = 2 + 1 = **3**. Check of the node's claim: 3 > c = 1 — holds.
- **Lean helper at the same point:** `avgCost 2 1 1 = 2 / 1 + 1 = 2 + 1 = 3`. Agrees with the node's value.

Additional probe exposing the defect (not a dispatcher parameter set, computed from the Lean code): at q = 0, `avgCost 2 1 0 = 2 / 0 + 1 = 0 + 1 = 1`, and the Lean conclusion `1 > 1` is false, while the node makes no claim at q = 0.

## Verdict

**UNFAITHFUL.** The Lean hypothesis `0 ≤ q` enlarges the node's domain q > 0 to include q = 0, where Lean's junk value `F / 0 = 0` collapses `avgCost` to c and falsifies the conclusion. The Lean statement is strictly stronger than the node and is false. The fix is the node's own hypothesis: `0 < q`.

Also noted: the dispatcher labels the Lean `Calib2.case5`, but the statement `def` in the file is `Calib2.case5_stmt`; the audit is of `case5_stmt`, the only statement in the file.
