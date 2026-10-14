# Fidelity card — <node label>

**Node:** <node label>
**Node statement hash:** <the node's stmt: hash from its evidence log>
**Lean:** <Pkg>.<Name>
**Statement SHA-256:** <from `python3 bin/lean_check.py <node> --hash`>
**Audited statements:** <every `<x>` with a `<x>_stmt` in the statement file, comma-separated>
**Independent audit:** PENDING
**Verdict:** PENDING
**Signed off:** PENDING

<!--
The owner's sign-off document (ADR-0004 as amended by ADR-0005). Copy to theory/blueprint/cards/<node file name>.
Keep every header field above in the first lines, once each: both checkers read them there.

Who writes what:
  The formalizer writes the header hashes, the formalizer column of the worked instance, and Appendix A-D.
  The blind back-translator writes the checklist rows (Lean clause, reading) and Appendix E. Claude substitutes
  the paper's symbols into the readings once the three glossaries agree, and changes nothing else.
  The card-auditor's report is cited in `Independent audit:` (Claude fills in the path).
  The owner marks every checklist row, checks the worked instance, writes the notes, and sets Verdict and
  Signed off. No agent ever writes Verdict, Signed off or Audit override.

Verdict:
  FAITHFUL                — every checklist row is marked `same`.
  WITH-NOTED-DIFFERENCES  — some rows differ, you accept each one, and the notes say why.
  UNFAITHFUL              — send it back. Do not sign.

Signed off: your initials, the date and the first 12 characters of the Statement SHA-256 above, typed by you:
  <initials> <YYYY-MM-DD> sha:<first 12 of the Statement SHA-256>
If the statement changes, the 12 characters stop matching and you sign again. Nobody "fixes" the prefix for you.

Audit override (only if the auditor's verdict is not FAITHFUL / WITH-NOTED-DIFFERENCES and you disagree with it).
Put it in the header block, right under Signed off; the validator reads only the header:
  Audit override (as a bold header field): <initials> <YYYY-MM-DD> sha:<first 12 of the Statement SHA-256>: <your reason>
An override never covers a coverage FAIL: that means a Lean clause is missing from your list.
-->

## Checklist (owner marks)

One row per Lean clause: each hypothesis, then each part of the conclusion. Compare each reading with the node's statement and mark it:
- `same`: it says what the paper says;
- `weaker`: the Lean claims less, for example "concave" for "strictly concave";
- `stronger`: the Lean claims more, which may be false;
- `added`: the Lean assumes something the paper does not. That makes the Lean claim weaker;
- `missing`: add your own row, with `—` in the Lean column, for something the paper says that no row covers.

A dropped assumption makes the Lean claim stronger. An added assumption makes it weaker.

| Part | # | Lean clause (verbatim) | Reading (paper symbols) | Mark |
|---|---|---|---|---|
| (a) | 1 | `...` | ... | PENDING |

## Worked instance

The formalizer and the auditor each compute the paper's values, independently. Check that they agree, and check the arithmetic. The Lean value is the sanity companion. It is a claim until the full check proves it at `verified`.

| Parameters | Paper value (formalizer) | Paper value (auditor) | Lean companion says | Agree? (owner) |
|---|---|---|---|---|

## Owner's notes

Differences you accept and why, questions, anything unclear, and the time you spent. Then set **Verdict** and **Signed off** in the header.

## Appendix (reference; you may skip it)

### A. Glossary (formalizer)

| Lean | Means |
|---|---|

### B. Types (formalizer)

| Variable | Paper | Lean type | Coercions |
|---|---|---|---|

### C. Hypotheses ↔ assumptions (formalizer)

| Lean hypothesis | Paper assumption / node | Lean-only? (flag) |
|---|---|---|

### D. Junk values and guards; companions (formalizer)

| Operation | Junk value | Guard hypothesis |
|---|---|---|

| Companion | Says | Why it matters |
|---|---|---|
| `<name>_nonvacuous` | ... | the hypotheses can all hold at once |
| `<name>_sanity_<k>` | ... | a concrete instance (see the worked instance) |
| `<name>_false_variant` | ... | a plausible wrong version is refuted |

### E. Back-translator's glossary and notes (blind; written from the Lean file only)
