import Mathlib

namespace Calib2

/-- The function g(x) = -x - c/x. -/
noncomputable def gfun (c x : ℝ) : ℝ := -x - c / x
/-- On x > 0, g attains its maximum at √c, with value -2√c. -/
def case7_stmt : Prop :=
  ∀ c : ℝ, 0 < c → IsMaxOn (gfun c) (Set.Ioi (0 : ℝ)) (Real.sqrt c)

end Calib2
