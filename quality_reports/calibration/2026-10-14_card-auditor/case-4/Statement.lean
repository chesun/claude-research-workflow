import Mathlib

namespace Calib2

/-- Utility from `h` hours at wage `w` with effort-cost parameter `k`. -/
noncomputable def util (w k h : ℝ) : ℝ := w * h - k * h ^ 2 / 2
/-- With w > 0 and k > 0, utility is maximized over h ≥ 0 at h = w / k. -/
def case4_stmt : Prop :=
  ∀ w k : ℝ, 0 < w → IsMaxOn (util w k) (Set.Ici (0 : ℝ)) (w / k)

end Calib2
