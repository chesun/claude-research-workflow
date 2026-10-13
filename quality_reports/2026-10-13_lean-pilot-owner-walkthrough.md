# Lean pilot — what the owner does, step by step

**Date:** 2026-10-13
**For:** the blueprint owner (you)
**Total time:** about 1 hour across two sittings. No Lean knowledge needed: every card gives you a glossary and a plain-English back-translation.

You do two things, in this order. Claude does everything between and after them, but it cannot do your parts for you. The sign-off only means something if the judgment is yours.

---

## Step 1 — Practice cards (about 20–30 minutes)

**Where:** this repository, `quality_reports/calibration/2026-10-12_lean-cards/`. Open `README.md`, then `card-A.md`, `card-B.md` and `card-C.md`.

**Why first:** each card holds a toy Lean statement. Some say what the paper says and some do not. You are not told which. The answers are sealed outside the repository, so you will find out afterwards whether you can catch a mismatch. That tells us how much a real sign-off is worth.

**For each card:**

1. Read the paper statement (section 1, left column).
2. Work out what the Lean statement says, from the glossary (section 2) and the back-translation (section 8). You do not need to read the Lean itself.
3. **Section 3:** for each part, write whether the Lean version is *equal* to the paper, *weaker*, *stronger*, or *missing* something, with a few words on why.
4. **Section 9:** pick concrete numbers. Work out what the paper says for them, then what the Lean statement says.
5. **Section 10:** any notes, plus how long the card took you.
6. In the header, replace PENDING:
   - **Verdict:** FAITHFUL, WITH-NOTED-DIFFERENCES or UNFAITHFUL.
   - **Signed off:** your initials and the date, e.g. `CS 2026-10-13`.

**Then tell Claude.** Claude unseals the answers and records the result (caught, missed, false alarm, time per card) in the session log. A missed mismatch is useful data, not a failure on your part.

---

## Step 2 — The pilot card (about 30 minutes)

**Where:** the BDD repository, `theory/blueprint/cards/prop-nstar-interior-ac.md`. This is the real node `prop:nstar-interior-ac`, the one about the stopping maximizer n\*.

**Do not edit the header fields** `Node`, `Node statement hash`, `Lean`, `Statement SHA-256` or `Audited statements`. The checker matches them against the Lean file and the node. Only `Verdict` and `Signed off` are yours.

**What to read before writing anything:**

- **Section 1, the three helper definitions.** A mistake would most likely hide here, because every part relies on them. Check them against the paper's own definitions:
  - `postVar s0 x n = s0 * x / (n * s0 + x)` should be the paper's σ_n² = σ₀²σ_d² / (nσ₀² + σ_d²).
  - `vStop s0 x c n = -postVar s0 x n - c * n` should be the paper's V^stop(n) = −σ_n² − cn.
  - `isMaximizer` means "n ≥ 0, and no m ≥ 0 does better".
- **Section 1, the paragraph on how "the maximizer n\*" is expressed.** Each Lean part says "there is a number nstar such that n is a maximizer exactly when n = nstar". That one sentence says both that a maximizer exists and that it is unique. Decide whether you accept that this is what the paper means when it writes n\*.
- **Section 1, the table and the reading aids.** In Lean, `a / b * c` means (a/b)·c, read left to right. So `Real.sqrt x / s0 * (s0 / Real.sqrt c - Real.sqrt x)` is (σ_d/σ₀²)(σ₀²/√c − σ_d), which is the paper's second form of n\* in (b).
- **Sections 6 and 7** list the hypotheses, the companion statements and the guards against "junk values" (for example, Lean's convention that division by zero gives zero). Skim them.
- **Section 8** is the back-translation, written by an agent that saw only the Lean file. If it reads like the paper's statement, that is good evidence. If it differs anywhere, that is where to look closely.

**What to write:**

1. **Section 3, the per-part map.** One line each for (a), (b) and (c): equal, weaker, stronger or missing, with a reason. Section 1 notes that (b) and (c) repeat the existence-and-uniqueness claim instead of relying on (a). That duplication is deliberate, so it does not count as a difference.
2. **Section 9, a concrete instance.** Fill in the table for the two sanity companions. Do the arithmetic yourself if you can. The values below are there to check yours against.

   | Parameters (σ₀², σ_d², c) | Paper says | Lean companion says |
   |---|---|---|
   | (1, 1, 1/4) | σ₀²/√c = 1/0.5 = 2 > σ_d = 1, so (b) applies. n\* = 1/0.5 − 1/1 = 1. V(n\*) = −2·1·0.5 + 0.25·1/1 = −0.75. | `sanity_1`: n = 1 is a maximizer and V = −3/4 |
   | (2, 4, 1) | σ₀²/√c = 2/1 = 2 ≤ σ_d = 2, so (c) applies, exactly on the boundary. n\* = 0. V(n\*) = −σ₀² = −2. | `sanity_2`: n = 0 is a maximizer and V = −2 |

   You can check the first row directly: σ₁² = 1·1/(1 + 1) = 0.5, so V = −0.5 − 0.25 = −0.75.
3. **Section 10, your notes.** For example, that n\* = n\*(σ₀², σ_d², c) is only a name in the paper and the Lean form is how that name is pinned down. Add anything else you noticed, and your time.
4. **Header:**
   - **Verdict:** FAITHFUL or WITH-NOTED-DIFFERENCES. The checker accepts only these two.
   - **Signed off:** e.g. `CS 2026-10-13`.

   If you conclude the Lean statement is UNFAITHFUL, do not sign. Write what is wrong in section 10 and tell Claude. The formalizer then corrects the statement and a fresh card is produced.

**Then tell Claude.**

---

## What Claude does after you finish

| After | Claude does | Your part |
|---|---|---|
| Step 1 | Unseals the practice answers and records the calibration result | Read the result |
| Step 2 | Runs the statements-only check and writes its report; shows you the `checked -> formalized` status line | **Approve the line** (only you set a status) |
| Approval | Runs the formalizer's proof stage: real proofs, statement file untouched | Nothing; this may take a while |
| Proofs done | Runs the full check: the Lean FRO comparator, kernel replay, axiom check (about 5 minutes); writes its report | Nothing |
| Full PASS | Shows you the `formalized -> verified` line | **Approve the line** |
| Verified | Writes the pilot read-out (calibration result, time and cost) and sets up a private backup remote for the Lean project | **Create the private GitHub repository** when asked. Creating a repository is outward-facing, so Claude does not do it for you. |

If a proof turns out to be out of reach, the formalizer says so and the node stays at `formalized`. The statement is never weakened to make a proof go through.
