# ADR-0004 — Theory workflow: blueprint, blind verifier, opt-in Lean

**Date:** 2026-10-11
**Status:** Decided
**Scope:** Methodology / theory
**Data quality:** Full context
**Sources:**
- spec: `quality_reports/specs/2026-10-11_theory-proof-workflow-spec.md` (APPROVED 2026-10-11);
- survey synthesis: `quality_reports/reviews/2026-10-11_theory-survey_synthesis.md`, with streams A–D alongside it;
- session log: `quality_reports/session_logs/2026-10-11_hook-launcher-fix-and-theory-brainstorm.md`;
- phase 1 plan: `quality_reports/plans/2026-10-11_theory-workflow-phase1-plan.md`.

## Context

The owner wants to develop economic theory step by step and make each step's correctness a checked fact, not a model's assertion. The math involved is elementary/algebraic, optimization and comparative statics, and probability/dynamic.

The survey found three things that shape the design:
- **Verification, not generation, is the bottleneck.** Models write correct proofs and confident wrong ones, and they will prove false statements when asked.
- **Long efforts fail when state lives inside the model.** Anthropic's Fermat formalization post says the agents lost track of state until they worked from a statement graph. The orchestrator confirmed this in the post directly.
- **Lean certifies the statement as written, not as meant.**

The existing `theorist` and `theorist-critic` lived only on the `behavioral` overlay. They focused on presentation and loaded a reference file that exists on no branch.

## Decision

- **Blueprint first; Lean is an opt-in lane.**
  - Each theory project keeps a dependency graph of small nodes in `theory/blueprint/`. Each node has an immutable statement (rewording creates a new node), a status ladder (`conjecture → survived-search → proved → checked → formalized → verified`, plus `refuted`, `conditional`, `superseded`), and an append-only evidence log.
  - A stdlib Python validator (`bin/blueprint_check.py`) enforces the rules and returns PASS / UNVERIFIED / FAIL.
- **Prove or refute.** No agent is told "prove X". Exploration (examples, counterexample search, exact sub-claim checks) and assumption variants come before any proof attempt.
- **Blind verification.** A new `proof-verifier` critic sees only the statement, the cleaned proof, and the statements of the nodes it depends on. Two independent verifiers must both PASS before a node reaches `checked`.
- **Placement.** `theorist`, `theorist-critic` and `/theory` move to `main` and become universal. The dangling reference to `theory-writing-learnings.md` is removed.
- **Model routing**, as an extension of ADR-0003:
  - `theorist` and `proof-verifier` on `fable` with `effort: high`;
  - `theorist-critic` on `fable`;
  - phase 2's `formalizer` on `opus`.
  
  A fable-versus-opus comparison of the verifier on the same nodes joins the ADR-0003 experiment.
- **The user is the Lean auditor** (phase 2). Claude writes the Lean. The user signs a fidelity card per node, and only the user sets `formalized`. `verified` requires the user's signed card plus a deterministic `lean_check` PASS.
- **External services.** Online lemma search is allowed, since the theory applies existing mathematics and is not sensitive. Hosted provers that train on submissions (Harmonic Aristotle) are not used.
- **No new hooks.** Every check is a script or an agent step.

## Consequences

- One more critic, one validator script (gated by ADR-0002), and three files moving from the overlay to `main`. The overlay carries `main`'s copies.
- **Phasing:**
  1. prose machinery, piloted on `belief_distortion_discrimination` theory v2;
  2. the Lean lane, after a setup spike on Windows;
  3. an optional `math-proof:siege` hand-off for stubborn nodes.
- **Calibration before trust.** The verifier must catch planted errors in a real proof before it is relied on, and the variant step must rediscover a known modeling finding blind.
- Lean is formalized selectively. General-state dynamic programming and measure-theoretic updating are expensive in Mathlib and out of scope for now.

## Not decided

- Whether the Markdown blueprint ever exports to `leanblueprint`.
- How many prove-or-refute passes a node gets before the siege hand-off (set in phase 3).
