# Practice card A — quadratic loss

**Node:** (practice card; not a blueprint node)
**Lean:** Calib.CardA
**Verdict:** PENDING
**Signed off:** PENDING

## 1. The statement, paper and Lean side by side

| Part | Paper | Lean (verbatim) |
|---|---|---|
| (a) | Let the state θ have mean μ and variance v ≥ 0. The expected quadratic loss of an action a, E[(a − θ)²] = (a − μ)² + v, is at least v, and it equals v if and only if a = μ. | `∀ μ v a : ℝ, 0 ≤ v → v ≤ quadLoss μ v a ∧ (quadLoss μ v a = v ↔ a = μ)` with `quadLoss μ v a := (a - μ) ^ 2 + v` |

## 2. Glossary (formalizer)

| Lean | Means |
|---|---|
| `ℝ` | the real numbers |
| `∀ μ v a : ℝ, …` | for all real numbers μ, v, a … |
| `0 ≤ v → …` | if v ≥ 0, then … |
| `quadLoss μ v a` | (a − μ)² + v, defined in the file |
| `x ^ 2` | x squared |
| `P ∧ Q` | P and Q |
| `P ↔ Q` | P if and only if Q |

## 3. Per-part map (owner)

| Paper part | Lean part | equal / weaker / stronger / missing | Note |
|---|---|---|---|
| (a) | `cardA_part_a_stmt` | | |

## 4. Types (formalizer)

| Variable | Paper | Lean type | Coercions |
|---|---|---|---|
| μ, a | real numbers | `ℝ` | none |
| v | a variance, v ≥ 0 | `ℝ`, with hypothesis `0 ≤ v` | none |

## 5. Quantifiers, in order (formalizer)

For all real μ, v, a: if v ≥ 0, then [v ≤ (a − μ)² + v] and [(a − μ)² + v = v exactly when a = μ].

## 6. Hypotheses ↔ assumptions (formalizer)

| Lean hypothesis | Paper assumption | Lean-only? |
|---|---|---|
| `0 ≤ v` | variance v ≥ 0 | no |

## 7. Junk values and guards; companions (formalizer)

No division, `deriv`, `sSup`, ℕ subtraction, `sqrt`, `log` or `tsum`, so there are no junk values to guard. (Companions are omitted on practice cards.)

## 8. Blind back-translation (written from the Lean file only)

**Plain-English statement.** For every real μ, every real v, and every real a: if 0 ≤ v, then (i) v ≤ (a − μ)² + v, and (ii) (a − μ)² + v = v holds if and only if a = μ. (Parsing: `→` binds weaker than `∧`, so the single hypothesis `0 ≤ v` governs the whole conjunction.) Equivalently: under 0 ≤ v, the value v is a lower bound of `quadLoss μ v` over all real a, and it is attained exactly at a = μ.

**Glossary.**
- `quadLoss μ v a := (a - μ) ^ 2 + v` — a plain real-valued function; "mean"/"variance" are docstring words only, not encoded.
- `^` with literal `2` — `Monoid.npow` with a natural-number exponent, so `x ^ 2 = x * x`; no real-power subtleties.
- `≤`, `=` on ℝ — standard; `↔` is bi-implication.
- No `IsMinOn`/`Set` is used; the minimisation claim is written out by hand as bound plus characterisation of equality.

**Anything odd.**
- The hypothesis `0 ≤ v` is unused: both conjuncts are true for every real v, since v ≤ (a−μ)²+v ⇔ 0 ≤ (a−μ)², and equality ⇔ (a−μ)² = 0 ⇔ a = μ. The statement is strictly weaker than what is provable.
- There is no quantifier structure that ties v to being a variance of anything; v is a free real parameter.
- The statement does not literally say "μ is the unique minimiser" via Mathlib's `IsMinOn`, but conjuncts (i) and (ii) together entail exactly that, since `quadLoss μ v μ = v`.

## 9. Concrete instance (owner)

| Parameters | Paper value | Lean instance says | Agree? |
|---|---|---|---|
| | | | |

## 10. Owner's notes

Time spent:
