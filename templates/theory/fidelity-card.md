# Fidelity card — <node label>

**Node:** <node label>
**Node statement hash:** <the node's stmt: hash from its evidence log>
**Lean:** <Pkg>.<Name>
**Statement SHA-256:** <from `python3 bin/lean_check.py <node> --hash`>
**Audited statements:** <every `<x>` with a `<x>_stmt` in the statement file, comma-separated>
**Verdict:** PENDING
**Signed off:** PENDING

<!--
The owner's audit document (ADR-0004; plan 2026-10-12, Interfaces). Copy to theory/blueprint/cards/<node file name>.

The formalizer fills in sections 1, 2, 4–7 and the hash, from the statement file only, with the proofs still `sorry`.
Section 8 is pasted from a blind back-translation: an agent that saw only the Lean statement file.
Sections 3, 9 and 10 are the owner's own, so that a card cannot be signed without being read.

Verdict:
  FAITHFUL — Lean says what the paper says.
  WITH-NOTED-DIFFERENCES — it differs only as listed in section 10, and you accept that.
  UNFAITHFUL — send it back.

Sign-off: your initials and the date (e.g. `CS 2026-10-12`), typed by you. Any later edit to the statement file changes its SHA-256,
so lean_check fails and the card no longer counts.
-->

## 1. The statement, paper and Lean side by side

| Part | Paper (node statement) | Lean (`<x>_stmt`, verbatim) |
|---|---|---|
| (a) | ... | `...` |

## 2. Glossary (formalizer)

Every Lean symbol the statement uses, in plain English. Example: `Set.Ici 0` is the set of reals ≥ 0; `StrictConcaveOn ℝ s f` means f is strictly concave on s.

| Lean | Means |
|---|---|

## 3. Per-part map (owner)

Read sections 1, 2 and 8, then mark each part.

| Paper part | Lean part | equal / weaker / stronger / missing | Note |
|---|---|---|---|

## 4. Types (formalizer)

| Variable | Paper | Lean type | Coercions |
|---|---|---|---|

## 5. Quantifiers, in order (formalizer)

"For all ..., if ..., then there exists ... such that ...", once per part.

## 6. Hypotheses ↔ assumptions (formalizer)

| Lean hypothesis | Paper assumption / node | Lean-only? (flag) |
|---|---|---|

## 7. Junk values and guards; companions (formalizer)

| Operation | Junk value | Guard hypothesis |
|---|---|---|

| Companion | Says | Why it matters |
|---|---|---|
| `<name>_nonvacuous` | ... | the hypotheses can all hold at once |
| `<name>_sanity_<k>` | ... | a concrete instance (see section 9) |
| `<name>_false_variant` | ... | a plausible wrong version is refuted |

## 8. Blind back-translation (pasted; written from the Lean file only)

## 9. Concrete instance (owner)

Pick the parameters of a sanity companion. Compute the paper's answer yourself, or take it from the numeric check file named here. Then compare it with the Lean instance.

| Parameters | Paper value (you / check file) | Lean instance says | Agree? |
|---|---|---|---|

## 10. Owner's notes

Differences you accept, questions, and anything unclear. Then set **Verdict** and **Signed off** in the header.
