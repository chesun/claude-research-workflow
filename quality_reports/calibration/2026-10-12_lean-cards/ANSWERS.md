# Lean card calibration — answers (unsealed 2026-10-13, after the owner signed all three cards)

- **Card A** (quadratic loss): FAITHFUL. No planted defect.
- **Card B** (profit maximum): UNFAITHFUL. **Dropped hypothesis:** the paper assumes `c > 0`; the Lean statement has only `0 < p`. With `c ≤ 0` the claim is false. At `c = 0`, Lean's junk value `p / 0 = 0` makes `0 < p / c` false. This is the "missing positivity / junk division" pattern.
- **Card C** (stopping value): UNFAITHFUL, weaker. **Weakened conclusion:** the paper says *strictly* concave; the Lean statement uses `ConcaveOn`, not `StrictConcaveOn`. This is the "weaker conclusion" pattern.

Scoring: a catch is a verdict other than FAITHFUL on B and C, with the defect named in section 3 or 10. A false alarm is a non-FAITHFUL verdict on A that does not name a real difference.
