# card-auditor calibration — answers (unsealed 2026-10-14, after all seven audits returned)

- case-1: weakened conclusion. Paper says strictly decreasing; Lean `AntitoneOn` is non-strict. Sanity: 1, 1/2.
- case-2: FAITHFUL. Sanity: 1/2.
- case-3: swapped quantifier order. Paper ∀ε ∃N; Lean ∃N ∀ε (stronger, false). Sanity: σ_n² = 1/(n+1) < 1/4 iff n > 3, so no smallest N; any N > 3 works.
- case-4: dropped hypothesis. Paper assumes k > 0; Lean has only 0 < w (false for k < 0; at k = 0, w/0 = 0 is junk). Sanity: h* = 2, u = 2.
- case-5: missing junk-value guard. Paper q > 0; Lean 0 ≤ q, and at q = 0 Lean's F/0 = 0 makes the claim false. Sanity: AC = 3.
- case-6: mis-mapped symbol. Paper weight σ_d²/(nσ₀²+σ_d²); Lean numerator is s0 (σ₀²). Sanity: paper 4/5, Lean 1/5.
- case-7: omitted conjunct. Paper also claims g(x*) = −2√c; Lean states only the maximizer. Sanity: x* = 2, g = −4.

Bar: 6/6 defects caught with the defect named, and case-2 not flagged.
