# Practice card B — profit maximum

**Node:** (practice card; not a blueprint node)
**Lean:** Calib.CardB
**Verdict:** UNFAITHFUL
**Signed off:** CS 2026-10-13

## 1. The statement, paper and Lean side by side

| Part | Paper | Lean (verbatim) |
|---|---|---|
| (a) | A firm faces price p > 0 and cost c q²/2 with c > 0, and chooses a quantity q ≥ 0. Its profit p q − c q²/2 is maximized over q ≥ 0 at q* = p/c, and q* > 0. | `∀ p c : ℝ, 0 < p → IsMaxOn (profit p c) (Set.Ici 0) (p / c) ∧ 0 < p / c` with `profit p c q := p * q - c * q ^ 2 / 2` |

## 2. Glossary (formalizer)

| Lean | Means |
|---|---|
| `∀ p c : ℝ, …` | for all real numbers p and c … |
| `0 < p → …` | if p > 0, then … |
| `profit p c q` | p·q − c·q²/2, defined in the file |
| `Set.Ici 0` | the set of reals q ≥ 0 |
| `IsMaxOn f s x` | x is a maximizer of f over the set s: f(y) ≤ f(x) for every y in s |
| `p / c` | p divided by c |
| `P ∧ Q` | P and Q |

## 3. Per-part map (owner)

| Paper part | Lean part | equal / weaker / stronger / missing | Note |
|---|---|---|---|
| (a) | `cardB_part_a_stmt` | stronger | it does not state the assumption that c > 0 |

## 4. Types (formalizer)

| Variable | Paper | Lean type | Coercions |
|---|---|---|---|
| p | price | `ℝ`, with hypothesis `0 < p` | none |
| c | cost parameter | `ℝ` | none |
| q | quantity, q ≥ 0 | `ℝ`, ranging over `Set.Ici 0` | none |

## 5. Quantifiers, in order (formalizer)

For all real p, c: if p > 0, then [p/c maximizes profit over q ≥ 0] and [p/c > 0].

## 6. Hypotheses ↔ assumptions (formalizer)

| Lean hypothesis | Paper assumption | Lean-only? |
|---|---|---|
| `0 < p` | price p > 0 | no |
| q ranges over `Set.Ici 0` | q ≥ 0 | no |

## 7. Junk values and guards; companions (formalizer)

| Operation | Junk value | Guard hypothesis |
|---|---|---|
| `p / c` | Lean defines x / 0 = 0 | (see section 6) |

(Companions are omitted on practice cards.)

## 8. Blind back-translation (written from the Lean file only)

**Plain-English statement.** For every real p and every real c: if 0 < p, then (i) for every real q with q ≥ 0, `profit p c q ≤ profit p c (p / c)`, i.e. p·q − c·q²/2 ≤ p·(p/c) − c·(p/c)²/2; and (ii) 0 < p / c. **There is no hypothesis on c**; c ranges over all reals including 0 and negatives.

**Glossary.**
- `profit p c q := p * q - c * q ^ 2 / 2` — parses as `p*q − ((c*(q^2))/2)`.
- `IsMaxOn f s a` — `∀ x ∈ s, f x ≤ f a`. It does **not** require `a ∈ s`, and does not assert uniqueness of the maximiser.
- `Set.Ici 0` — the closed half-line `{q : ℝ | 0 ≤ q}`.
- `/` on ℝ — Lean's total division: `x / 0 = 0` for every x.
- `0 < p / c` — a separate conjunct; together with (i) it places the maximiser strictly inside the domain.

**Anything odd.**
- **The statement is false as written.** Take p = 1, c = 0: then `p / c = 0` in Lean, so conjunct (ii) `0 < 0` fails. For c < 0, `p / c < 0`, so (ii) fails again (and `profit` is then convex in q, unbounded above on `Ici 0`, so (i) fails too). The missing hypothesis is `0 < c`. With `0 < c` added, the statement is the correct one: the concave quadratic peaks at q = p/c > 0.
- Uniqueness of the maximiser is not claimed (`IsMaxOn` is non-strict).
- `0 < p` is used only for (ii) (and to keep p/c > 0); (i) would hold for any p once 0 < c.

## 9. Concrete instance (owner)

| Parameters | Paper value | Lean instance says | Agree? |
|---|---|---|---|
| | | | |

## 10. Owner's notes

Time spent: 10 min
