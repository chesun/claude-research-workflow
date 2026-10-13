import Mathlib

namespace Calib2

/-- Average cost at output `q` with fixed cost `F` and constant marginal cost `c`. -/
noncomputable def avgCost (F c q : ℝ) : ℝ := F / q + c
/-- For positive output, average cost exceeds marginal cost. -/
def case5_stmt : Prop :=
  ∀ F c q : ℝ, 0 < F → 0 < c → 0 ≤ q → avgCost F c q > c

end Calib2
