# Theory survey — synthesis

**Date:** 2026-10-11
**Reviewer:** orchestrator (synthesis of survey streams A–D)
**Target:** design inputs for the theory/proof workflow (approach A: blueprint first, Lean opt-in)
**Status:** Active
**Sources:** `2026-10-11_theory-survey_{A-mathlib-econ,B-lean-tooling,C-practice,D-fidelity-checks}.md`; primer `quality_reports/2026-10-11_math-research-with-claude-primer.md`

## Verified by the orchestrator

- Anthropic's post "Formalizing Fermat's Last Theorem" (https://www.anthropic.com/news/formalizing-fermats-last-theorem, dated 2026-09-04), opened directly. It says:
  - a model roughly comparable to Fable 5.1 took about 11 days;
  - the result uses only Lean's three standard axioms;
  - a comparator matched the statement to Mathlib's;
  - agents "lost track of the project's state" until they used Prove2Me's DAG of theorem statements.

  Streams B and C both reported this. Everything else below is as reported by the streams, which give URLs and confidence for each claim.

## What the survey settles

1. **Verification is the bottleneck, not generation** (C). Frontier models write correct research-level proofs but still produce many confident wrong ones, and they prove false statements on request (BrokenMath). In two economics-specific studies, external verification, not model capability, was the deciding factor, and polished output was the least verified. → The design centres on independent verification and prove-*or-refute* framing.
2. **The blueprint is right, but it must be a living conjecture graph** (C). Statements are immutable and identified by ID; a reworded statement is a new node; status changes are logged append-only. Prove2Me and the Equational Theories Project work this way. `leanblueprint` needs a TeX engine and graphviz, and this machine has no LaTeX. → Use a Markdown/YAML blueprint that keeps `leanblueprint` field names, so a later export is possible.
3. **Lean certifies the statement as written, not as meant** (C, D). In one system 87.2% of AI-drafted statements compiled but only 57.7% were faithful. Audits of benchmark formalizations found error rates around 30% and more. LLM judges agree with experts only about 86% of the time. → Statement sign-off stays human (the user as auditor), supported by a fidelity card and by companion lemmas a script can check:
   - a non-vacuity witness;
   - sanity instances;
   - a false variant that must be refuted;
   - an equivalence check against an independently written statement, where feasible.
4. **Lean defaults are the specific trap for economics** (D): `x/0 = 0`, `deriv` is 0 where a function isn't differentiable, `sSup` of an empty or unbounded set of reals is 0, and ℕ subtraction truncates. First-order conditions and value functions run straight into the `deriv` and `sSup` cases. → The card requires a guarding hypothesis for each such operation.
5. **Mathlib feasibility for the user's math** (A):
   - *Cheap:* finite expectations, Jensen, incentive-compatibility arguments (EconCSLib's sorry-free Vickrey and Myerson proofs can be adapted).
   - *Present:* one-variable first-order conditions and concavity.
   - *Needs a wrapper:* the one-dimensional implicit function theorem (moderate).
   - *Missing:* KKT and the envelope theorem.
   - *Absent but cheap to build:* Topkis and supermodularity.
   - *Moderate:* finite-state Bellman contraction.
   - *Expensive:* general-state dynamic programming and measure-theoretic Bayesian updating.
6. **Proof status can be decided by script** (B, D), as follows. A missing toolchain gives UNVERIFIED, never PASS.
   - **PASS** requires: the audited `Statements.lean` hash matches, the forbidden-token scan is clean, `lake build --wfail` exits 0, and `#print axioms` shows only {propext, Classical.choice, Quot.sound}. `leanchecker` is optional.
   - **Python pre-checks:** a counterexample means FAIL; search finding none means UNVERIFIED, never PASS. Exact Z3 `unsat` or SymPy simplifying to zero means PASS for that claim.
7. **Tooling on this machine** (B):
   - The Lean project lives *outside OneDrive*, e.g. `C:\Users\christina.sun\lean\<proj>`. Use the PowerShell `elan` installer and set `core.autocrlf=input` for the Lean repo.
   - Budget about 6–8 GB per project (estimate).
   - `lean-lsp-mcp` is the standard Claude bridge (MIT, untested on native Windows). Its hosted search tools send query text off-machine, so they are denied by default for unpublished work.
   - Skip Harmonic Aristotle for unpublished work (it trains on submissions unless you opt out first).
   - The corporate proxy filters some AI sites; downloads are untested.
8. **What carries over from the plugins** (C):
   - *Transfers:* ledger, self-contained queries, a two-verifier gate, refute queries, inline gap marks, abstention.
   - *Does not transfer:* no-web and no-code worker rules, and the single fixed goal.
   - `math-proof:siege` suits one stubborn, fully stated node.

## Pilot evidence (belief_distortion_discrimination, theory v2)

The 2026-09-14 blind reviews confirmed the math by re-derivation. Their substantive finding was a modeling one: belief cost is charged per period while sampling, not on the terminal belief. Under the terminal-belief variant, Voluntary ≡ Commitment for every γ. That is exactly what a systematic *assumption-variant* step finds early, and Lean would never flag it. → Variant exploration belongs in phase 1, and it is the pilot's calibration test.

## Open items carried into the design

- Whether `leanchecker` and `lean-lsp-mcp` work on native Windows, and whether the proxy allows the Lean downloads. Settle these by a spike at the start of phase 2.
- The SciPy Python 3.14 Windows wheel (unconfirmed); SymPy, Hypothesis and z3 are reported fine.
- The math-olympiad README misattributes figures to "Proof or Bluff" (C). Don't quote that number.
