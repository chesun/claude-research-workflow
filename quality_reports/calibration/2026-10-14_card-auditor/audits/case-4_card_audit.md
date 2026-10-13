# Card audit — prac:case-4
**Node:** prac:case-4
**Lean:** Calib2.case4
**Statement SHA-256:** 0000000000000000000000000000000000000000000000000000000000000000
**Verdict:** UNFAITHFUL
**Coverage:** PENDING
**Reviewer:** card-auditor (blind)

## Glossary

| Lean name / symbol | Plain mathematics |
|---|---|
| `Calib2.util w k h` | Expanding the `def` body: `w * h - k * h ^ 2 / 2` = w·h − (k·h²)/2 (precedence: `^` then `*` then `/`, so the ½ divides the whole cost term). Matches the node's u(h) = w h − k h²/2. |
| `Set.Ici (0 : ℝ)` | The closed ray {h ∈ ℝ : 0 ≤ h}, i.e. h ≥ 0. |
| `IsMaxOn f s a` | ∀ x ∈ s, f x ≤ f a — a is a (not necessarily unique, non-strict) maximum point of f on s. |
| `w / k` (ℝ division) | Ordinary real division for k ≠ 0; Lean junk value `w / 0 = 0` when k = 0. |
| `0 < w` | w > 0. |

Note: the dispatcher names the Lean as `Calib2.case4`; the statement file I was given declares `Calib2.case4_stmt`. I audit `case4_stmt`, the only statement in the file.

## Node

- Quantification: for all wages w > 0 and all cost parameters k > 0 (implicit universal over the parameters).
- Hypotheses: (H1) w > 0; (H2) k > 0.
- Domain of choice: h ≥ 0.
- Conclusion: u(h) = w h − k h²/2 attains its maximum over h ≥ 0 at h* = w/k.

## Lean

```lean
def case4_stmt : Prop :=
  ∀ w k : ℝ, 0 < w → IsMaxOn (util w k) (Set.Ici (0 : ℝ)) (w / k)
```

- Quantification: ∀ w k : ℝ.
- Hypotheses: `0 < w` only.
- Domain: `Set.Ici (0 : ℝ)` = {h : 0 ≤ h}.
- Conclusion: `IsMaxOn (util w k) (Set.Ici 0) (w / k)` — w/k is a maximum point of u on h ≥ 0.

## Map

| Part | Node | Lean clause (verbatim) | Mark |
|---|---|---|---|
| Objective u(h) | w h − k h²/2 | `w * h - k * h ^ 2 / 2` (body of `util`) | equal |
| Hypothesis w > 0 | present | `0 < w →` | equal |
| Hypothesis k > 0 | present | **absent** — quantifier is `∀ w k : ℝ` with no `0 < k` | **missing → Lean stronger (pattern 1, dropped hypothesis)** |
| Choice domain h ≥ 0 | present | `Set.Ici (0 : ℝ)` | equal |
| Maximized at h* = w/k | present | `IsMaxOn (util w k) (Set.Ici (0 : ℝ)) (w / k)` | equal in form, but see junk value below |

**The dropped hypothesis makes the Lean claim false, not merely stronger-but-true:**

- At k = 0: `w / k` is the junk value `w / 0 = 0` (pattern 7). The claim becomes `IsMaxOn (fun h => w * h - 0) (Set.Ici 0) 0`, i.e. ∀ h ≥ 0, w·h ≤ 0. With w > 0 and h = 1 this fails (w·1 = w > 0). Counterexample: w = 1, k = 0.
- At k < 0: u(h) = w h − k h²/2 has −k/2 > 0, so u is convex and unbounded above on h ≥ 0 (u(h) → ∞); no point can satisfy `IsMaxOn`. Counterexample: w = 1, k = −1.

No other difference: no added hypotheses, the conclusion is not weakened (`IsMaxOn` on the correct set at the correct point; the node claims a maximum, not uniqueness, so non-strict `IsMaxOn` matches), no omitted conjunct, no quantifier-order issue, types are ℝ throughout, and the hypotheses are satisfiable (no vacuity).

## Sanity values

Parameters (w, k) = (2, 1).

Node-side, step by step:
- h* = w/k = 2/1 = **2**.
- u(h*) = w·h* − k·h*²/2 = 2·2 − 1·(2²)/2 = 4 − 4/2 = 4 − 2 = **2**.

Lean-side at the same parameters:
- `w / k` = 2 / 1 = 2.
- `util 2 1 2` = 2·2 − 1·2²/2 = 4 − 2 = 2.

They agree. (The sanity point lies inside the parameter region where the dropped hypothesis holds, so it cannot detect the omission.)

## Verdict

**UNFAITHFUL.** The node's hypothesis k > 0 has no Lean counterpart (pattern 1). The Lean statement therefore claims strictly more than the node, and the extra claim is false at k = 0 (where `w / 0 = 0` is a junk value, pattern 7) and at every k < 0. Every other part is equal.
