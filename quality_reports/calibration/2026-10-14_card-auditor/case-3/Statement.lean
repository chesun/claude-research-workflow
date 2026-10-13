import Mathlib

namespace Calib2

/-- Posterior variance after a sample of size `n`, with prior variance `s0` and signal-noise variance `x`. -/
noncomputable def postVar (s0 x n : ℝ) : ℝ := s0 * x / (n * s0 + x)
/-- For every ε > 0 there is an N beyond which the posterior variance is below ε. -/
def case3_stmt : Prop :=
  ∀ s0 x : ℝ, 0 < s0 → 0 < x →
    ∃ N : ℝ, ∀ ε : ℝ, 0 < ε → ∀ n : ℝ, N ≤ n → postVar s0 x n < ε

end Calib2
