import Mathlib

namespace Calib2

/-- Weight on the prior mean in the posterior mean, with prior variance `s0` and signal-noise variance `x`. -/
noncomputable def priorWeight (s0 x n : ℝ) : ℝ := s0 / (n * s0 + x)
/-- The prior weight lies in (0, 1]. -/
def case6_stmt : Prop :=
  ∀ s0 x n : ℝ, 0 < s0 → 0 < x → 0 ≤ n → 0 < priorWeight s0 x n ∧ priorWeight s0 x n ≤ 1

end Calib2
