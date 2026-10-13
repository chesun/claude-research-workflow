# card-auditor calibration (ADR-0005, plan 2026-10-14 Task 3)

Seven practice cases. Each has a node statement and a Lean statement file that compiles. Six carry one planted defect each, one per class: dropped hypothesis, weakened conclusion, omitted conjunct, mis-mapped symbol, swapped quantifier order, and missing junk-value guard. One case is faithful. The case numbers are shuffled against the classes.

The Lean docstrings repeat the paper statement even where the code differs, as a formalizer's might. The auditor has to read the code, not the comments.

## How it ran

- **Dispatch:** one fresh `fable` agent per case, told to follow `.claude/agents/card-auditor.md` (step 1 only) and to use only Read and Write. `card-auditor` was not yet a registered agent type in that session.
- **Blindness:** the answers were sealed outside every repository, at a path no agent was given. They were unsealed into `ANSWERS.md` only after all seven reports had returned.
- **Cost:** about 95k agent tokens, 4 tool uses and 60–90 s per case.

## Result: bar met on the first run

| Case | Planted | Verdict | Named the defect? |
|---|---|---|---|
| 1 | weakened conclusion (`AntitoneOn` for strictly decreasing) | UNFAITHFUL | yes (pattern 3, suggests `StrictAntiOn`) |
| 2 | none (faithful) | FAITHFUL | no false alarm |
| 3 | quantifier order (∃N ∀ε for ∀ε ∃N) | UNFAITHFUL | yes (pattern 6; also noticed the docstring contradicts the code) |
| 4 | dropped hypothesis k > 0 | UNFAITHFUL | yes (patterns 1 and 7; noted the sanity point cannot detect it) |
| 5 | junk-value guard (0 ≤ q, where F/0 = 0) | UNFAITHFUL | yes (patterns 7 and 8) |
| 6 | mis-mapped symbol (σ₀² in the numerator for σ_d²) | UNFAITHFUL | yes (pattern 5; counterexample s0 = 4, x = 1, n = 0) |
| 7 | omitted conjunct (the value g(x\*) = −2√c) | UNFAITHFUL | yes (pattern 4) |

Six of six defects were caught, each named, and the faithful case was not flagged.

## Limits

- Seven short, single-part cases. The pilot node has three parts and four companions.
- Step 2 (coverage) was not calibrated. It is checked by the validator's coverage rule and on the pilot.
- After five audited nodes, the session log counts catches and false alarms, and the owner decides whether the auditor stays (ADR-0005 item 3).
