module

@[expose] public section

/-! Fixture for bin/test_lean_check_integration.py: core Lean only, no Mathlib. -/

namespace Fix

/-- A helper the statements use; editing it must change the statement hash. -/
def double (n : Nat) : Nat := n + n

def thing_part_a_stmt : Prop := ∀ n : Nat, double n = 2 * n

def thing_nonvacuous_stmt : Prop := ∃ n : Nat, 0 < n

def thing_sanity_1_stmt : Prop := double 3 = 6

def thing_false_variant_stmt : Prop := ¬ ∀ n : Nat, double n = n

end Fix
