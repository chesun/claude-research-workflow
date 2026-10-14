module

public import Fix.Statements.Thing

public section

namespace Fix

theorem thing_part_a : thing_part_a_stmt := by
  unfold thing_part_a_stmt double
  intro n
  omega

theorem thing_nonvacuous : thing_nonvacuous_stmt := ⟨1, by decide⟩

theorem thing_sanity_1 : thing_sanity_1_stmt := by
  unfold thing_sanity_1_stmt double
  decide

theorem thing_false_variant : thing_false_variant_stmt := by
  unfold thing_false_variant_stmt double
  intro h
  have := h 1
  omega

end Fix
