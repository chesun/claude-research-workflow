import Mathlib

namespace Calib2

/-- Posterior variance after a sample of size `n`, with prior variance `s0` and signal-noise variance `x`. -/
noncomputable def postVar (s0 x n : ℝ) : ℝ := s0 * x / (n * s0 + x)
/-- The posterior variance is strictly decreasing in `n` on `[0, ∞)`. -/
def case1_stmt : Prop :=
  ∀ s0 x : ℝ, 0 < s0 → 0 < x → AntitoneOn (postVar s0 x) (Set.Ici (0 : ℝ))

end Calib2
