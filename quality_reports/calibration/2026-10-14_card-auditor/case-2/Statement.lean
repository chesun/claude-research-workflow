import Mathlib

namespace Calib2

/-- Posterior variance after a sample of size `n`, with prior variance `s0` and signal-noise variance `x`. -/
noncomputable def postVar (s0 x n : ℝ) : ℝ := s0 * x / (n * s0 + x)
/-- The posterior variance is positive and no larger than the prior variance. -/
def case2_stmt : Prop :=
  ∀ s0 x n : ℝ, 0 < s0 → 0 < x → 0 ≤ n → 0 < postVar s0 x n ∧ postVar s0 x n ≤ s0

end Calib2
