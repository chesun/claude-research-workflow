# Requirements Specification: Rigorous theory development — blueprint, blind verification, opt-in Lean

**Date:** 2026-10-11
**Status:** DRAFT — awaiting user review
**Design record:** brainstorm in session log `quality_reports/session_logs/2026-10-11_hook-launcher-fix-and-theory-brainstorm.md`; evidence in `quality_reports/reviews/2026-10-11_theory-survey_synthesis.md` (streams A–D); primer `quality_reports/2026-10-11_math-research-with-claude-primer.md`
**Decision record to write:** ADR-0004 (this design, the agent move to `main`, model routing for the new agents)

---

## Objective

Use this workflow to develop economic theory step by step and to make the correctness of each step a checked fact rather than a model's assertion. Every claim is a node in a dependency graph that moves from conjecture to verified only on recorded evidence. Lean formal verification is used where it pays.

## Principles (each traced to the survey)

1. **Prove or refute, never "prove X".** Models prove false statements on request (C: BrokenMath). Refuted, conditional and "no confident proof" are successful outcomes.
2. **Statements are immutable nodes.** A reworded statement is a new node, and the old one is superseded. Status changes are append-only and carry evidence (C: Prove2Me, Equational Theories Project; plugin ledger).
3. **Keep state outside the model.** All state lives in blueprint files, every agent starts fresh from files, and nodes are small enough for one session (C and the orchestrator-verified Anthropic FLT post: agents lost track of state until they worked from a statement DAG).
4. **Verification is the bottleneck.** Blind, independent, two-verifier checking with conservative aggregation (C; `math-olympiad` and `math-proof` plugin designs).
5. **Explore before proving.** Compute examples, search for counterexamples, and vary assumptions first (C; and the BDD 2026-09-14 referee finding, a modeling primitive that systematic variant exploration catches and Lean cannot).
6. **Lean certifies the statement as written, not as meant.** Fidelity sign-off is human, supported by companion lemmas a script can check and a fidelity card (C, D).
7. **Gates, not nags.** No new blocking hooks. Deterministic checks are scripts that return PASS / UNVERIFIED / FAIL (repo modernize principle; `adversarial-default.md` vocabulary).

## Scope decisions (user, 2026-10-11)

| Aspect | Decision |
|---|---|
| Math in scope | Elementary/algebraic; optimization & comparative statics; probability/dynamic. Equilibrium existence is out of scope. |
| Machine | This Windows 11 laptop; Lean may be installed here. Everything cross-platform (Python-first). |
| User's Lean role | **Auditor**: Claude writes the Lean; the user reads and signs statements via fidelity cards. |
| Placement | `main` (universal). `theorist`, `theorist-critic`, `/theory` move up from the `behavioral` overlay. |
| Approach | A: blueprint first, Lean an opt-in lane, phased. |
| Models | `theorist` and `proof-verifier` on `fable` with `effort: high`; `formalizer` on `opus`; `theorist-critic` on `fable`. Aliases, not dated IDs (ADR-0003). |
| Online lemma search | **Allowed.** The theory applies existing math and is not sensitive. Harmonic Aristotle is not used (it trains on submissions by default). |
| Pilot | `belief_distortion_discrimination` theory v2 (clone at `github_repos/belief_distortion_discrimination`). |

---

## Design

### 1. Blueprint (phase 1)

- **Location:** `theory/blueprint/` in each research project. One Markdown file per node, `<label>.md`, with a YAML header.
- **Header fields** (named after `leanblueprint` so a later export is possible):
  - `label` — e.g. `prop:nstar`;
  - `kind` — `definition | assumption | claim | variant | imported`;
  - `statement`;
  - `uses` — a list of labels;
  - `status`;
  - `supersedes` / `superseded_by`;
  - `lean` — an optional declaration name;
  - `paper_ref` — an optional locator in the `.tex`.
- **Body:** the proof text, with inline `[GAP: …]` markers, plus an append-only `## Evidence log` of one line per status change: date, from→to, actor, evidence locator.
- **Status ladder:**
  1. `conjecture`
  2. `survived-search`
  3. `proved`
  4. `checked`
  5. `formalized`
  6. `verified`

  Off-ladder: `refuted`, `conditional`, `superseded`. A `variant` node uses the same statuses. An `imported` node (a result from the literature) stays at `conjecture` until reading notes for its source exist, per `primary-source-first.md`. It can reach `checked` only when a verifier confirms the statement against those notes, never on memory alone.
- **Validator `bin/blueprint_check.py`** (Python, stdlib plus PyYAML or a minimal header parser). It returns PASS / UNVERIFIED / FAIL, writes `theory/blueprint/STATUS.md` (a table plus a Mermaid dependency graph, so no LaTeX is needed), and checks that:
  - every `uses` label exists and the graph is acyclic;
  - labels are unique, and statements are unchanged since their first evidence entry (statement hash recorded in the log);
  - **status monotonicity**: a node at `checked` or above depends only on nodes at `checked` or above, or on `assumption`/`definition` nodes;
  - no `[GAP:` marker sits in a node at `proved` or above;
  - every evidence locator resolves to an existing file;
  - `superseded` nodes point to their successor.

### 2. Exploration and prove-or-refute (phase 1)

- **Per claim, before any proof attempt**, scripts and outputs go in `theory/blueprint/checks/<label>/`:
  1. **examples** on special or small cases;
  2. **counterexample search** (Hypothesis / SciPy). A counterexample gives `refuted` with the instance saved; none gives `survived-search`, which is UNVERIFIED and never PASS;
  3. **exact sub-claim checks** (SymPy / Z3). PASS applies to the sub-claim only.
- **Assumption variants:** for each assumption a claim uses, create `variant` nodes that drop, weaken or swap it, each prove-or-refute. If the claim survives without the assumption, the assumption is superfluous; if it collapses, it is identifying and must be stated and defended.
- **Repairs never edit a statement.** They create a `conditional` node (an added hypothesis) or a weaker node.
- **Dependencies:** SymPy, Hypothesis, z3-solver and SciPy, pinned in the project venv (`python-code-conventions.md`). Never installed globally.

### 3. Agents and skill (phase 1)

- **`theorist`** (worker, `fable`, effort high; tools Read, Write, Edit, Grep, Glob, Bash). Moved to `main`, keeping its existing modelling and proof-writing guidance.
  - Works one node at a time under prove-or-refute.
  - Writes and runs the exploration scripts and marks gaps.
  - May raise a node only as far as `proved`.
- **`proof-verifier`** (new critic, `fable`, effort high; tools Read, Grep, Glob, Write for its report only, Bash for numerical spot checks in a scratch folder).
  - **Blind:** it receives the node statement, the cleaned proof, and the *statements* of the nodes it uses. It never sees the paper, the motivation, the target conclusion, or other verdicts.
  - **Failure-pattern checklist:** unused or contradictory hypotheses; quantifier swaps; boundary cases (zero variance, n = 0, empty sets); interchange of limits, expectations or derivatives without justification; optional stopping without its conditions; WLOG that loses generality; circular `uses`; a conclusion stronger than shown.
  - **Verdict:** PASS / FAIL (step located) / UNVERIFIED. Report at `quality_reports/reviews/YYYY-MM-DD_<label>_proof-verifier_review.md`, per `agents.md`.
  - **Aggregation:** two independent verifiers. Both PASS → `checked`. Any FAIL → back to the theorist. A split → a third verifier or the user.
- **`theorist-critic`** (critic, `fable`). Moved to `main`, keeping its paper-level 16-item and architecture review. **Adds:** every theorem, proposition, lemma or corollary in the `.tex` maps to a node at `checked` or above; an unmapped claim, or one resting on a `conjecture`, is a deduction.
- **Dangling reference:** remove the "read `quality_reports/paper_learnings/theory-writing-learnings.md`" instructions from both agents and the skill. The standards are already inline in the agent files, and the referenced file exists on no branch.
- **`/theory` skill modes:** `explore <question>`, `node <label>`, `variants <label>`, `verify <label> [--model fable|opus]`, `status`, `review`, `develop` (loops over open nodes in dependency order).
- **Overlay housekeeping:** remove the moved files from the `behavioral` overlay and update `.claude/file-classes.toml`. Add theory rows to `main`'s dispatch table in `workflow.md`, its pairs table in `agents.md`, and its components in `quality.md` (component weight: see Clarity Status).

### 4. Lean lane (phase 2)

- **Step 0, setup spike** (can defer the phase). Install `elan` (official PowerShell installer), the VS Code Lean 4 extension, and a Mathlib project at `C:\Users\christina.sun\lean\<project>\`, **outside OneDrive**, with `core.autocrlf=input`. Then test:
  - that the proxy allows the toolchain, Mathlib cache and lemma-search downloads;
  - `lean-lsp-mcp` on native Windows;
  - `leanchecker`.

  The user has confirmed the download is allowed and can install with their own account permissions if a step needs elevation. Phase 2 is deferred only if `lean-lsp-mcp` or the build itself fails on native Windows.
- **Layout:** one Lean repo per theory project, outside OneDrive. Its path comes from a machine-local, gitignored setting (no hardcoded paths). `Statements.lean` holds the audited statements; proofs and companions live in separate files.
- **`formalizer`** (new worker, `opus`). Per node it writes the statement, the companions (below) and the proof. It uses `lean-lsp-mcp`, online search tools included.
  - **Companions:**
    - a **non-vacuity witness**;
    - **sanity instances**;
    - a **false variant** whose negation is proved;
    - a **guard hypothesis** for every junk-value operation (`/`, `deriv`, `sSup`/`sInf`, ℕ subtraction, `sqrt`/`log`, `tsum`).
- **Fidelity card** `theory/blueprint/cards/<label>.md`, the user's audit document:
  - the paper and Lean statements side by side;
  - a plain-English glossary of every Lean symbol;
  - a map from hypotheses to paper assumptions, with Lean-only hypotheses flagged;
  - junk-value warnings with their guards;
  - companion results;
  - an advisory back-translation by a fresh `fable` agent that never saw the paper;
  - the user's sign-off: initials, date, statement SHA-256.
  
  **Only the user sets `formalized`.** A statement hash mismatch voids the card, and the node returns to `checked`.
- **`bin/lean_check.py`** produces the verdict:
  - **PASS** requires all of: the statement hash matches the signed card; the forbidden-token scan (`sorry`, `admit`, `axiom`, `native_decide` unless whitelisted) finds nothing; `lake build --wfail` exits 0; a generated check file shows that `#print axioms` for each audited theorem is a subset of {`propext`, `Classical.choice`, `Quot.sound`}; and `leanchecker`, if available, passes;
  - **UNVERIFIED** if the toolchain is missing;
  - **FAIL** otherwise.
  
  `verified` = `lean_check` PASS + a signed card with a matching hash.
- **Auditor guide:** `.claude/references/reading-lean-statements.md`, a short guide sourced from official Lean and Mathlib documentation (URLs cited).

### 5. Plugin hand-off (phase 3, optional)

- **When:** a node still at `conjecture` after K prove-or-refute passes (K is set in phase 3).
- **Input:** a fully stated problem file built from the node and its dependency statements.
- **Run:** `/math-proof:siege` in a scratch folder outside the repo, with the plugin's `env` block in *that folder's* `.claude/settings.json` only.
- **Output:** `proof.md` returns as a candidate proof that still needs two blind verifiers. Literature it cites becomes `imported` nodes.
- **User decisions:** installing the plugin, and the cost (a siege can run 100+ sub-agents).

---

## Requirements

### MUST Have

- [ ] Blueprint node format, status ladder and append-only evidence log as in §1.
- [ ] `bin/blueprint_check.py` with every check in §1 and PASS/UNVERIFIED/FAIL output; tests in the repo's existing plain-Python `check()` style.
- [ ] Prove-or-refute framing in `theorist` and `/theory`; no agent instruction of the form "prove X".
- [ ] Exploration step (§2) with saved, re-runnable scripts; counterexample search never yields PASS.
- [ ] Assumption-variant step (§2).
- [ ] `proof-verifier` agent: blind inputs, failure-pattern checklist, two-verifier aggregation, review reports.
- [ ] `theorist`, `theorist-critic`, `/theory` on `main` with the model settings in Scope; dangling reference removed; overlay copies removed; file-class manifest updated.
- [ ] Creators never set `checked` or above; only the user sets `formalized`.
- [ ] All new code cross-platform (Windows + Mac), Python-first, folder-relative paths, no new blocking hooks.
- [ ] ADR-0004 written. New `bin/` scripts independently reviewed before commit (ADR-0002).
- [ ] Phase 2: setup spike first; Lean project outside OneDrive; fidelity card; `lean_check.py` per §4; companions per node.

### SHOULD Have

- [ ] `STATUS.md` with a Mermaid dependency graph.
- [ ] `verify --model` override for the `fable`-versus-`opus` comparison.
- [ ] `theorist-critic` paper↔blueprint cross-check.
- [ ] Auditor guide `reading-lean-statements.md`.
- [ ] README and CHANGELOG entries for the feature.

### MAY Have

- [ ] Export from the Markdown blueprint to `leanblueprint` format.
- [ ] Phase 3 `math-proof` hand-off.
- [ ] A reusable Lean module for monotone comparative statics (Topkis, supermodularity) and a one-dimensional implicit-function wrapper (survey A: cheap and moderate respectively).

---

## Clarity Status

| Aspect | Status | Notes |
|---|---|---|
| Math scope, machine, Lean role, placement, approach, models, online search, pilot | CLEAR | User decisions 2026-10-11 (table above) |
| Proxy allows Lean downloads | CLEAR | User, 2026-10-11: the download is fine; the user can install with their own account permissions if needed |
| `lean-lsp-mcp`, `leanchecker` on native Windows | BLOCKED → phase 2 spike | Fixes are reported merged but untested here |
| `theory` component weight in `main`'s `quality.md` | ASSUMED | Adopt the behavioral overlay's 15% theory component; the user can override |
| YAML parsing dependency for the validator | ASSUMED | Prefer a minimal stdlib parser over a PyYAML dependency; decided in the implementation plan |
| K (passes before siege hand-off) | ASSUMED | Set in phase 3, from pilot experience |
| SciPy wheel for Python 3.14 on Windows | ASSUMED | Reported fine for SymPy, Hypothesis and z3; SciPy checked at venv setup |

---

## Acceptance Criteria

| # | Criterion | Level | Tier | How checked |
|---|---|---|---|---|
| 1 | Validator test suite passes: cycles, missing `uses`, monotonicity violations, gap-in-proved, dangling evidence, and statement-hash change are each detected | MUST | Tier 1 | `py bin/test_blueprint_check.py` exit 0 |
| 2 | Planted-error calibration: `proof-verifier` returns FAIL on each of ≥4 planted flaws (dropped boundary condition, quantifier swap, circular use, overstated conclusion) in a pilot proof, and PASS on the correct proof, with the verifier run on `fable` and, separately, on `opus` | MUST | Tier 2 | Calibration report in `quality_reports/reviews/`, each verdict located to the planted step |
| 3 | Known-answer test: the variant step on BDD's belief-cost timing assumption independently finds that a terminal-belief cost makes Voluntary ≡ Commitment, without being given the 2026-09-14 referee reports | MUST | Tier 2 | Variant node in BDD `theory/blueprint/` with status and evidence; the verifier prompt shows no referee input |
| 4 | Every BDD v2 assumption, proposition, lemma and corollary has a blueprint node whose status carries evidence; the validator returns PASS | MUST | Tier 1 | `py bin/blueprint_check.py <BDD>/theory/blueprint` |
| 5 | No agent file or skill contains a "prove X"-style instruction without a refute branch | MUST | Tier 1 | grep sweep over `.claude/agents/theorist*.md`, `proof-verifier.md`, `skills/theory/` |
| 6 | Moved agents and skill exist on `main`, are absent from the `behavioral` overlay, and no file references `theory-writing-learnings` | MUST | Tier 1 | `git ls-tree` per branch plus a grep sweep |
| 7 | Phase 2: `lean_check.py` returns FAIL on a proof containing `sorry`, on a hidden `sorryAx`, on an extra axiom, and on a statement edited after signing; PASS on a clean proof | MUST | Tier 1 | Test suite with fixture Lean files |
| 8 | Phase 2: BDD Prop 1 reaches `verified`, with a fidelity card the user signed after reading it unaided | MUST | Tier 3 | User sign-off on the card plus `lean_check` PASS |
| 9 | Model-comparison read-out (verifier on `fable` vs `opus`, same nodes) recorded in the session log, per ADR-0003's experiment | SHOULD | Tier 2 | Session-log table: findings by severity per model |

## Phasing

1. **Phase 1 (prose machinery):** implementation plan → build on `main` → independent review of `bin/` code (ADR-0002) → calibration (#2) → pilot in BDD (#3, #4) → read-out.
2. **Phase 2 (Lean):** setup spike → plan → build → review → Prop 1 pilot (#7, #8).
3. **Phase 3 (optional):** `math-proof` hand-off, only if the pilot shows nodes that stay stuck.

Each phase gets its own implementation plan in `quality_reports/plans/`.

## Out of scope

- Equilibrium-existence formalization (Brouwer/Kakutani are not in Mathlib).
- General-state dynamic programming and measure-theoretic Bayesian updating in Lean (survey A rates these expensive; revisit after the pilot).
- Hosted AI provers.
- `leanblueprint`'s LaTeX output (no LaTeX on this machine).
- Any blocking hook.

## Risks

| Risk | Mitigation |
|---|---|
| Misformalization passes `lean_check` | Fidelity card, companions, human sign-off; `verified` needs both |
| Two verifiers share a model's blind spots | `--model` comparison; the planted-error calibration measures the catch rate |
| Blueprint upkeep becomes a nag | Nodes are created by the `/theory` modes, not by hand; the validator is run on demand, with no hook |
| Lean tooling fails on native Windows | The setup spike finds out first; phase 1 is independently useful |
| OneDrive interference | Lean project outside OneDrive by design |

---

## Approval

[ ] User approved: [Date]
