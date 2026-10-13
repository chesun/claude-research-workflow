# Practice card C — concavity of a stopping value

**Node:** (practice card; not a blueprint node)
**Lean:** Calib.CardC
**Verdict:** UNFAITHFUL
**Signed off:** CS 2026-10-13

## 1. The statement, paper and Lean side by side

| Part | Paper | Lean (verbatim) |
|---|---|---|
| (a) | With prior variance s > 0 and per-draw cost c > 0, the stopping value V(n) = −s/(1 + n) − c n is strictly concave in the sample size n on n ≥ 0. | `∀ s c : ℝ, 0 < s → 0 < c → ConcaveOn ℝ (Set.Ici 0) (stopValue s c)` with `stopValue s c n := -(s / (1 + n)) - c * n` |

## 2. Glossary (formalizer)

| Lean | Means |
|---|---|
| `∀ s c : ℝ, …` | for all real numbers s and c … |
| `0 < s → 0 < c → …` | if s > 0 and c > 0, then … |
| `stopValue s c n` | −s/(1 + n) − c·n, defined in the file |
| `Set.Ici 0` | the set of reals n ≥ 0 |
| `ConcaveOn ℝ S f` | f is concave on the (convex) set S: f(t x + (1 − t) y) ≥ t f(x) + (1 − t) f(y) for x, y in S and t in [0, 1] |

## 3. Per-part map (owner)

| Paper part | Lean part | equal / weaker / stronger / missing | Note |
|---|---|---|---|
| (a) | `cardC_part_a_stmt` | weaker | concave is not the same as strictly concave |

## 4. Types (formalizer)

| Variable | Paper | Lean type | Coercions |
|---|---|---|---|
| s | prior variance, s > 0 | `ℝ`, with hypothesis `0 < s` | none |
| c | per-draw cost, c > 0 | `ℝ`, with hypothesis `0 < c` | none |
| n | sample size, n ≥ 0 (real relaxation) | `ℝ`, ranging over `Set.Ici 0` | none |

## 5. Quantifiers, in order (formalizer)

For all real s, c: if s > 0 and c > 0, then the function n ↦ −s/(1 + n) − c n has the stated concavity on n ≥ 0.

## 6. Hypotheses ↔ assumptions (formalizer)

| Lean hypothesis | Paper assumption | Lean-only? |
|---|---|---|
| `0 < s` | s > 0 | no |
| `0 < c` | c > 0 | no |
| n ranges over `Set.Ici 0` | n ≥ 0 | no |

## 7. Junk values and guards; companions (formalizer)

| Operation | Junk value | Guard hypothesis |
|---|---|---|
| `s / (1 + n)` | x / 0 = 0 | on n ≥ 0, 1 + n ≥ 1 > 0, so the denominator never vanishes |

(Companions are omitted on practice cards.)

## 8. Blind back-translation (written from the Lean file only)

**Plain-English statement.** For every real s and every real c: if 0 < s and 0 < c, then the function n ↦ −(s/(1+n)) − c·n is concave on the set {n : ℝ | 0 ≤ n}, in Mathlib's sense: `Ici 0` is a convex set, and for all x, y ≥ 0 and all weights a, b ≥ 0 with a + b = 1, `a·f x + b·f y ≤ f (a·x + b·y)`.

**Glossary.**
- `stopValue s c n := -(s / (1 + n)) - c * n` — parses as `(−(s/(1+n))) − (c*n)`; n is a **real** variable, not a natural number.
- `ConcaveOn ℝ s f` — `Convex ℝ s ∧ ∀ x ∈ s, ∀ y ∈ s, ∀ a b : ℝ, 0 ≤ a → 0 ≤ b → a + b = 1 → a • f x + b • f y ≤ f (a • x + b • y)`. Non-strict concavity only.
- `Set.Ici 0` — `{n | 0 ≤ n}`.
- `/` on ℝ — total, `x / 0 = 0`; irrelevant here since 1 + n ≥ 1 on the domain, but relevant if the domain were widened past n = −1.

**Anything odd.**
- The hypothesis `0 < c` is unused: `−c·n` is affine, hence concave, for every real c.
- `0 < s` could be weakened to `0 ≤ s` (s = 0 gives an affine function). For s < 0 the claim would be false, so some sign condition on s is genuinely needed.
- The domain could be enlarged to `Set.Ioi (−1)` with the same proof; `Ici 0` is a conservative choice. Note Lean's `x / 0 = 0` would make the function discontinuous at n = −1, so a domain including −1 would break concavity.
- Only non-strict concavity is asserted; strict concavity holds for s > 0 but is not claimed.
- "Sampling cost c·n" with real n is a continuous relaxation; nothing here restricts n to integers.

## 9. Concrete instance (owner)

| Parameters | Paper value | Lean instance says | Agree? |
|---|---|---|---|
| | | | |

## 10. Owner's notes

Time spent:
