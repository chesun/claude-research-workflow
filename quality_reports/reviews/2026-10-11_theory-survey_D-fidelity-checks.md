# Theory survey D — Statement fidelity, non-vacuity, and deterministic checks
**Date:** 2026-10-11
**Reviewer:** survey agent D (general-purpose, opus)
**Target:** misformalization risk and pre-proof/post-proof checks for an auditor-economist
**Status:** Active

Scope: how an economist who reads but does not write Lean can tell whether a Claude-written Lean 4 + Mathlib statement says what the paper means, and which cheap deterministic checks (Lean-side and Python-side) turn that judgment into ledger evidence. Citations are by title and URL. Confidence is marked **[high]**, **[medium]** or **[low]**. Nothing was installed or run for this survey. Every version and wheel claim comes from PyPI or Reservoir pages fetched on 2026-10-11.

---

## Bottom line

- **A compiled proof only shows that the Lean statement is true. It does not show that the statement is the paper's.** The literature now measures this gap directly. One system "compiles 87.2% of statements but is faithful on 57.7%" ([Beyond Compilation](https://arxiv.org/abs/2606.31002)) [medium]. 31.8% of the entries in the Lean 4 ports of ProofNet had formalization errors ([Reliable Evaluation and Benchmarks for Statement Autoformalization](https://arxiv.org/abs/2406.07222), [EMNLP version](https://aclanthology.org/2025.emnlp-main.907.pdf)) [high]. More than half of miniF2F problems had formal/informal discrepancies ([miniF2F-Lean Revisited](https://arxiv.org/abs/2511.03108)) [high]. A ~10k-problem audit found 4,833 findings, including vacuous theorems and counterexamples ([Faults in Our Formal Benchmarking](https://arxiv.org/abs/2606.29493)) [high]. The working prior is that roughly a third or more of first-draft formalizations are unfaithful.
- **Fidelity is the auditor's job, and it is the one step that cannot be fully mechanized.** The official Lean reference says that if there is doubt about meaning, "its statement and all referenced definitions must be investigated carefully" ([Validating Proofs](https://lean-lang.org/doc/reference/latest/ValidatingProofs/)) [high]. LLM judges score about 86% on expert-labelled consistency data ([ReForm / ConsistencyCheck](https://arxiv.org/pdf/2510.24592)) [medium]. That is good enough for triage and not good enough to sign off.
- **Most fidelity questions can be turned into Lean theorems, which then become script-decidable.** Each statement comes with four companions: (a) a **non-vacuity witness**, an explicit object satisfying every hypothesis; (b) **sanity lemmas** that evaluate definitions on small concrete cases; (c) a **refuted false variant**, a proof that a deliberately wrong version is false; (d) where feasible, an **equivalence proof** against an independently written reference statement (the bidirectional idea in [BEq](https://proceedings.iclr.cc/paper_files/paper/2025/file/d630537fc4402cfa3ebbc7450a0cac91-Paper-Conference.pdf)). Google DeepMind's Formal Conjectures repository uses (b) at scale: 467 test and 155 API statements are 23.8% of its statements, and 291 misformalizations have been fixed ([Formal Conjectures](https://arxiv.org/html/2605.13171v1)) [high].
- **Junk values are the main trap specific to Lean.** Lean returns a value instead of failing: `x/0 = 0`, `5 - 7 = 0` in ℕ, `Real.sqrt (-1) = 0`, `Real.log 0 = 0`, `log (-x) = log x`, `deriv f x = 0` where f is not differentiable, `∑'` of a non-summable family = 0, and `sSup` of an empty or unbounded set of reals = 0 (sources in item 1d). Economists differentiate first-order conditions and take sups of value functions, so `deriv` and `sSup` junk are the most dangerous for econ work.
- **Proof status can be decided by a script:** the build exits 0, there are no `sorry` warnings, and `#print axioms` lists only a subset of `{propext, Classical.choice, Quot.sound}` ([Axioms](https://lean-lang.org/doc/reference/latest/Axioms/)) [high]. The statement must also be **frozen**: hash the audited statement, or use Lean's `comparator` challenge/solution split ([Comparator](https://reservoir.lean-lang.org/@leanprover/Comparator)). Otherwise a proof can quietly prove an edited statement. Comparator's sandbox is Linux-only, so on Windows use a statement-hash check instead [high].
- **Python pre-checks can refute a claim but rarely confirm one.** Hypothesis, random search and `scipy.optimize` searches can FAIL a claim (a counterexample found) or leave it UNVERIFIED. They never PASS it. Z3 `unsat` on the negation of a polynomial real-arithmetic claim is a genuine proof of that encoding ([Z3 nlsat](https://arxiv.org/pdf/2406.02122)) [medium]. SymPy `simplify(...) == 0` returning True is a PASS for an identity, but False or None means UNVERIFIED, because simplification is incomplete.
- **Minimal toolkit:** `sympy`, `hypothesis` and `z3-solver` are all pip-installable on Windows with Python 3.14 (pure-Python or `py3-none` wheels). Add `scipy` for optimization probes and `python-flint` for rigorous ball arithmetic if needed. On the Lean side the essentials are `#print axioms`, `#lint` (with `unusedArguments`), `plausible`, and the four companion lemmas.

---

## 1. Methods for checking that a formal statement matches informal intent

### 1a. How large the risk is (evidence)

| Source | Finding | Confidence |
|---|---|---|
| [Reliable Evaluation and Benchmarks for Statement Autoformalization](https://arxiv.org/abs/2406.07222) | ProofNet# corrects errors in **31.8%** of ProofNet's Lean 4 entries. Releases ProofNetVerif (3,752 labelled pairs) and the BEq+ metric, which "correlates strongly with human judgment". Best methods reach ~45% on undergraduate maths. | high |
| [miniF2F-Lean Revisited](https://arxiv.org/abs/2511.03108) | Formal/informal discrepancies in **more than half** of miniF2F problems. End-to-end accuracy is 36% even though the components score 97% (formalization) and 69% (proving). | high |
| [Beyond Compilation](https://arxiv.org/abs/2606.31002) | Across 8 systems and 227 graduate-level statements, compile rate overstates faithfulness. Example: 87.2% compile vs 57.7% faithful. About half of the compile gains from Lean feedback fail semantic validation. | medium |
| [Faults in Our Formal Benchmarking](https://arxiv.org/abs/2606.29493) ([HTML](https://arxiv.org/html/2606.29493v1)) | 5 Lean benchmarks: 4,833 findings, ~398 mechanically certified issues (counterexamples, vacuous theorems, unsound axioms). Seven metaprogram checkers: counterexample, vacuity, axiom, unguarded division, ℕ-subtraction, analytic domain, unused binder. Recommends `autoImplicit false`, a no-axioms policy, and pinned versions. | high (counts); medium (checker details) |
| [Formal Conjectures](https://arxiv.org/html/2605.13171v1) | Taxonomy of 291 fixed misformalizations: translation level (syntactic, semantic, misrepresentation), underspecified level (implicit conventions), source level. Misrepresentation is 48% and semantic 35%. Detection relied mostly on automated provers proving or disproving the statements, followed by human inspection. | high |
| [Formalizing Numerical Analysis: … Quality Audit Beyond Kernel Acceptance](https://arxiv.org/abs/2606.14000) | Recurring unfaithful patterns: "incomplete multi-part statements, added weakening hypotheses, and parameter restrictions". These are exactly the failure modes an econ formalization is prone to. | medium |
| [FormalRx](https://arxiv.org/abs/2607.04655) | A 28-category "SCI" error taxonomy (Semantic, Constraint, Implementation). The Implementation dimension covers Lean-specific semantics. | medium |
| [The Faithfulness Gap (BPF)](https://arxiv.org/abs/2606.16541) | Bidirectional provability fingerprinting plus counterfactual probes: 89.6% drift detection at 3.0% false positives, vs 41.2% for typechecking and 63.3% for LLM judges. | **low**: little-known authors, recent preprint, not replicated |

Takeaway: the error modes that recur across these sources are the ones the brief lists. They are (i) added or strengthened hypotheses, (ii) vacuous or contradictory hypotheses, (iii) dropped parts of a multi-part claim, (iv) parameter restrictions such as working over ℕ instead of ℝ, and (v) Lean conventions (junk values, coercions, auto-implicits).

### 1b. Back-translation (formal to natural language by an independent model)

- **Method.** A second model that has not seen the paper statement informalizes the Lean statement. A judge, either a human or a third model, compares the back-translation with the paper. [Faithful Autoformalization via Roundtrip Verification and Repair](https://arxiv.org/abs/2604.25031) extends this into a roundtrip: formalize, back-translate, re-formalize, then check that the two formal versions are logically equivalent. Rules that fail the equivalence check show 1.4–2.5x more NLI drift [medium].
- **Reliability.** LLM judges reach ~85.8% accuracy on ConsistencyCheck, 859 expert-labelled miniF2F/ProofNet items ([ReForm](https://arxiv.org/pdf/2510.24592), [dataset](https://huggingface.co/datasets/GuoxinChen/ConsistencyCheck/blob/refs%2Fpr%2F2/README.md)) [medium]. That is about one wrong verdict in seven. FormalAlign trains a dedicated alignment scorer ([FormalAlign](https://arxiv.org/abs/2410.10135), [code](https://github.com/rookie-joe/FormalAlign)) [high]. Reported numbers are high on easy sets and lower on harder ones (66% on MiniF2F-Valid).
- **Use.** Back-translation is useful because it gives the auditor plain-English text to compare. It is a Tier-2/3 signal (advise and deduct), never a PASS. The back-translator must not see the original statement; otherwise it tends to repeat the paper back.

### 1c. "Test the statement" techniques (each is a Lean theorem, so each is deterministic once proved)

1. **Non-vacuity witness.** `example : ∃ params, H₁ params ∧ H₂ params ∧ …` proved with explicit numbers. This rules out contradictory hypotheses, the failure mode in which an "unsatisfiable minimality condition … allow[s] a trivial exfalso proof" ([Faults in Our Formal Benchmarking](https://arxiv.org/html/2606.29493v1)). Strengthen it by also showing that the **conclusion is non-trivial** at the witness, for example that the inequality is strict there or that the equilibrium set is a proper subset.
2. **Concrete-instance check.** Specialize the theorem to the witness and confirm that the conclusion matches a number computed by hand or in Python, using `norm_num` or `decide`.
3. **Obvious-corollary check.** Prove a textbook consequence from the formal statement. If it cannot be proved, the statement is probably too weak or mis-quantified.
4. **Refuted false variant.** Write a deliberately wrong variant (drop a key hypothesis, flip an inequality, swap ∀/∃) and prove its **negation** on a concrete counterexample: `example : ¬ (∀ …, variant) := by …`. This shows that the statement has content and that the hypotheses do work. [Lean Disprove](https://icml.cc/virtual/2026/82610) automates certified counterexample search with REFUTED / WITNESS-UNCERTIFIED / INCONCLUSIVE outcomes and lifts external witnesses into Lean for kernel checking [medium]. `plausible` does randomized testing inside Lean ([Plausible](https://reservoir.lean-lang.org/@leanprover-community/plausible), Apache-2.0) [high]. Whether `plausible` can sample ℝ values is **not confirmed** (see Unverified).
5. **Definition API lemmas.** For every new definition (equilibrium, optimality, preference relation), add lemmas showing that it behaves as expected on small cases. For example, show that in a 2x2 game with a known payoff matrix, the profile the paper names is an equilibrium and some other profile is not. This is the Formal Conjectures "test statement" practice ([Formal Conjectures](https://arxiv.org/html/2605.13171v1)) [high].
6. **Equivalence to an independent reference.** Have a separate agent, or the auditor with help, write the paper's statement a second way, for example "no profitable unilateral deviation" vs "each strategy is a best response". Then prove `stmt_A ↔ stmt_B`. This is the BEq/BEq+ bidirectional idea ([BEq](https://proceedings.iclr.cc/paper_files/paper/2025/file/d630537fc4402cfa3ebbc7450a0cac91-Paper-Conference.pdf), [BEq+](https://arxiv.org/abs/2406.07222)) used as a proof obligation. It is the strongest deterministic fidelity evidence available, but it only moves trust onto the reference statement.

### 1d. Checking that each hypothesis is used

- `#lint` runs Batteries' `unusedArguments`, which reports declaration arguments unused in the type and value. It skips declarations containing `sorry` and allows `_`-prefixed names ([Batteries Lint Misc](https://leanprover-community.github.io/mathlib4_docs/Batteries/Tactic/Lint/Misc.html); older docs show it in the default set: [mathlib lint docs](https://cs.brown.edu/courses/cs1951x/docs/tactic/lint/misc.html)) [high]. Lean core's `linter.unusedVariables` warns about unused function arguments in every command ([UnusedVariables](https://lean-lang.org/doc/api/Lean/Linter/UnusedVariables.html)) [high].
- **How to read the result.** An unused hypothesis means either that the paper's assumption is unnecessary (worth knowing) or that it was encoded so it does no work, for example a hypothesis about `f` when the conclusion is about `g`. In both cases the auditor should map it to a paper assumption and explain the result.
- **What the linters miss.** A *contradictory* set of hypotheses **is used** by the exfalso proof, so the unused-argument linters pass it. Only the non-vacuity witness catches it.
- **Ablation.** Delete one hypothesis at a time and re-run the proof. If it still proves, that hypothesis was not needed. This is cheap with a script and gives deterministic evidence.

### 1e. Lean and Mathlib conventions that trap newcomers

| Convention | Value in Lean/Mathlib | Econ risk | Source |
|---|---|---|---|
| Division by zero | `x / 0 = 0` (ℝ, ℚ, fields) | Shares, averages, elasticities when a denominator can be 0 | [Division by zero in type theory: a FAQ](https://xenaproject.wordpress.com/2020/07/05/division-by-zero-in-type-theory-a-faq/) [high] |
| ℕ subtraction | truncated: `2 - 3 = 0` | Time periods `t - 1` at `t = 0`, counts, inventory | same FAQ; [Faults…](https://arxiv.org/html/2606.29493v1) [high] |
| ℕ/ℤ division | floor/truncation | `n / 2` for player counts or medians | [Faults…](https://arxiv.org/html/2606.29493v1) [high] |
| `Real.sqrt` of a negative | `= 0` (`Real.sqrt_eq_zero_of_nonpos`) | Discriminants, standard deviations | [Sqrt docs](https://cs.brown.edu/courses/cs1951x/docs/data/real/sqrt.html) [high] |
| `Real.log` | `log 0 = 0`, `log (-x) = log x` | Log utility, log-linearizations | [Log docs](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/SpecialFunctions/Log/Basic.html) [high] |
| `deriv` | `= 0` where f is not differentiable (`deriv_zero_of_not_differentiableAt`) | **First-order conditions**: `deriv f x = 0` holds trivially at a kink | [Deriv docs](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/Calculus/Deriv/Basic.html) [high]. Prefer `HasDerivAt f f' x` in statements. |
| `tsum` `∑'` | `= 0` if the family is not summable | Discounted payoff streams with β ≥ 1 | [InfiniteSum docs](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Topology/Algebra/InfiniteSum/Defs.html) [high] |
| `sSup`/`sInf` on ℝ | `= 0` for an empty or unbounded set (`Real.sSup_empty`, `Real.sSup_of_not_bddAbove`) | **Value functions, indirect utility, support functions** | [Real.Archimedean docs](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Data/Real/Archimedean.html) [medium: lemma names recalled, the fetched page did not quote bodies] |
| EReal / ENNReal | `0 * ⊤ = 0` in EReal. In ENNReal, `∞ - ∞ = 0` and `0⁻¹ = ∞` | Extended-real payoffs, measure-theoretic expectations | [EReal source](https://raw.githubusercontent.com/leanprover-community/mathlib4/master/Mathlib/Data/EReal/Basic.lean) [high for `0*x = 0`]; ENNReal specifics [medium] |
| Coercions ℕ→ℤ→ℝ | `((a - b : ℕ) : ℝ)` ≠ `(a : ℝ) - b` | Silent truncation before the cast | [Faults…](https://arxiv.org/html/2606.29493v1) [high] |
| `autoImplicit` | On by default in plain Lean, off in Mathlib. Typos become silently universally quantified variables | Unintended generality, or a variable of the wrong type | [Lean v4.18 notes](https://lean-lang.org/doc/reference/4.20.0/releases/v4.18.0) [high]. Set `autoImplicit false`. |
| `ConvexOn 𝕜 s f` | includes `Convex 𝕜 s` | Usually intended, but must be noted | Mathlib convention [medium] |

The rule behind the table: theorems about the "usual" behaviour carry the guard hypothesis, for example `b ≠ 0` ([FAQ](https://xenaproject.wordpress.com/2020/07/05/division-by-zero-in-type-theory-a-faq/)). An auditor should therefore ask, for every `/`, `-` on ℕ, `sqrt`, `log`, `deriv`, `sSup` and `∑'` in a statement, **which hypothesis guards it**. If none does, the statement may hold only because of the junk value.

---

## 2. The statement-fidelity audit card (design and grounding)

One card per theorem, kept next to the Lean file. Each element and why it is included:

| Element | Why | Grounding |
|---|---|---|
| Paper statement, verbatim, with page/eq. number | The fixed reference | Formal Conjectures pairs every formal statement with its source text ([link](https://arxiv.org/html/2605.13171v1)) |
| Lean statement, verbatim, plus `#check @thm` output (all implicits shown) | What is actually proved, including hidden binders and type classes | [Validating Proofs](https://lean-lang.org/doc/reference/latest/ValidatingProofs/): "custom notation and type classes" can obscure meaning |
| Statement hash (SHA-256 of the normalized statement text) | Freezes what was audited. Comparator is the stronger form | [Comparator](https://reservoir.lean-lang.org/@leanprover/Comparator) |
| Symbol glossary: each Lean symbol and definition in plain English, with its Mathlib doc link | The auditor reads Lean only at this level | Validating Proofs ("all referenced definitions") |
| Types table: each variable's type (ℕ/ℤ/ℝ/EReal/Fin n/Finset) and why | Catches parameter restrictions and coercion traps | Numerical-analysis audit ("parameter restrictions") [link](https://arxiv.org/abs/2606.14000) |
| Hypothesis map: Lean hypothesis ↔ paper assumption ID, marked equal / stronger / weaker / extra | Catches added weakening hypotheses and dropped assumptions | [link](https://arxiv.org/abs/2606.14000); Formal Conjectures "misrepresentation" class |
| Quantifier line: the statement's ∀/∃ prefix written out in English | Catches swapped quantifiers | FormalRx taxonomy, logical-structure errors ([link](https://arxiv.org/abs/2607.04655)) |
| Junk-value checklist: every partial operation and its guard | Section 1e | [Faults…](https://arxiv.org/html/2606.29493v1) |
| Concept-definition check: the Lean definition of the equilibrium or optimality concept beside the paper's, plus API lemmas | Catches misformalized solution concepts | Formal Conjectures test/API statements |
| Non-vacuity witness (Lean `example`, proved) | Rules out contradictory hypotheses | [Faults…](https://arxiv.org/html/2606.29493v1) vacuity checker |
| Concrete-instance value (Lean plus an independent Python computation) | Cross-checks that the conclusion has the right magnitude and sign | — (standard practice) |
| Refuted false variant (Lean `example : ¬ …`, proved) | Shows that the hypotheses do work | [Lean Disprove](https://icml.cc/virtual/2026/82610); BPF counterfactual probes [low] |
| Unused-argument/ablation result | Shows which assumptions are load-bearing | [Batteries lint](https://leanprover-community.github.io/mathlib4_docs/Batteries/Tactic/Lint/Misc.html) |
| Back-translation (independent model) and the auditor's diff | Plain-English comparison, advisory only | [ConsistencyCheck/ReForm](https://arxiv.org/pdf/2510.24592) |
| Proof status block (script output) | Section 4 | [Axioms](https://lean-lang.org/doc/reference/latest/Axioms/) |
| Auditor verdict: FAITHFUL / FAITHFUL-WITH-NOTED-DIFFERENCES / UNFAITHFUL, with initials and date | A human sign-off is the step that cannot be mechanized | Validating Proofs |

---

## 3. Cheap deterministic pre-proof checks in Python

| Tool | Econ claims it suits | What a result means |
|---|---|---|
| **SymPy** | Algebraic identities (closed-form equilibria, comparative statics via implicit differentiation, FOC/SOC derivations, Slutsky decompositions), sign of polynomial expressions under assumptions | `simplify(lhs - rhs) == 0` True is a PASS for the identity. False or None means UNVERIFIED, because simplification is incomplete. `ask(Q.positive(e))` returns None when undecided, which also means UNVERIFIED. |
| **Hypothesis** (property-based testing) | "For all parameters in a region, the inequality holds" (monotonicity, single crossing, IR/IC constraints, welfare rankings) | A counterexample found is a FAIL. It is shrunk toward a human-readable case ([strategies docs](https://hypothesis.readthedocs.io/en/latest/reference/strategies.html)). No counterexample is UNVERIFIED (supporting evidence only). Use `floats(min_value, max_value, allow_nan=False)` to match the domain. |
| **Z3** (SMT) | Polynomial real-arithmetic claims: assert the hypotheses and the *negation* of the conclusion, then ask for `unsat`. Also good for finding a concrete non-vacuity witness (`sat` returns a model) | `unsat` is a PASS for the encoded claim. `sat` gives a counterexample, which is a FAIL after it is checked in exact arithmetic. `unknown` is UNVERIFIED. nlsat is complete for polynomial NRA but not for exp/log/rpow ([nlsat discussion](https://arxiv.org/pdf/2406.02122)) [medium]. **Z3 leaves `x/0` unspecified (an uninterpreted function), unlike Lean's `x/0 = 0`** ([Z3 purify-arith notes](https://git.libre-chip.org/mirrors/z3/src/commit/847278fba8d376d6190c11442fccf4ca06a44a5f/src/tactic/arith/purify_arith_tactic.h)) [medium], so guard denominators explicitly. |
| **cvc5** | Same uses as Z3. A second, independent solver for cross-checking | Same mapping |
| **Interval / ball arithmetic** (python-flint `arb`, mpmath `iv`) | Rigorous bounds on transcendental expressions over a box (CES/CRRA functions at parameter ranges) | Bound excludes violation → PASS on that box. Bound overlaps → UNVERIFIED. mpmath's `iv` is "still experimental" ([mpmath contexts](https://mpmath.org/doc/current/contexts.html)) |
| **Numerical optimization** (`scipy.optimize`: `differential_evolution`, `minimize` from many starts) | Search for parameters that minimize `conclusion_slack(params)` subject to the hypotheses. Finds counterexamples to inequalities and checks argmax claims | A negative slack, once confirmed in exact or interval arithmetic, is a FAIL. Otherwise UNVERIFIED. |

Points that apply to every tool:

- The Python encoding is another formalization, with its own misformalization risk. Sharing a parameter-domain spec between the Python check and the Lean hypotheses reduces drift.
- Floating point can create false counterexamples. Confirm any counterexample in exact rationals (SymPy `Rational`, Z3 model values) before recording a FAIL.
- Set seeds once (Hypothesis `derandomize=True` or `@seed`; NumPy `default_rng(seed)`) so that results are deterministic.

---

## 4. Proof status as script-decidable evidence

Proposed ledger checks for each theorem `T` in file `F` (matching the ledger in `adversarial-default.md`):

| Check slug | Script | PASS | FAIL | UNVERIFIED |
|---|---|---|---|---|
| `lean-builds` | `lake build` (or `lake env lean F`) | exit code 0 | non-zero | toolchain unavailable |
| `lean-no-sorry` | grep build output for `declaration uses 'sorry'` | 0 matches | ≥1 | — |
| `lean-axioms-standard` | append `#print axioms T`. Parse `'T' depends on axioms: [..]` or `'T' does not depend on any axioms` ([Axioms](https://lean-lang.org/doc/reference/latest/Axioms/)) | set ⊆ {propext, Classical.choice, Quot.sound} | contains `sorryAx` or a custom axiom | contains `Lean.ofReduceBool`, `Lean.trustCompiler`, or a `…native_decide.ax_…` axiom (compiler trusted; policy decision) |
| `lean-statement-frozen` | SHA-256 of the normalized statement text (or `#check @T` output) vs the hash on the audit card. Comparator on Linux CI | match | mismatch | no card yet |
| `lean-nonvacuity` | named `example`/`theorem T_nonvacuous` exists and passes the three checks above | yes | — | missing |
| `lean-false-variant-refuted` | named `T_variant_false` exists and passes | yes | — | missing |
| `lean-lint-unused` | `#lint only unusedArguments` on `T` | no findings, or every finding explained on the card | unexplained finding | — |
| `lean-kernel-replay` (optional) | `lean4checker --fresh` ([Validating Proofs](https://lean-lang.org/doc/reference/latest/ValidatingProofs/)) | exit 0 | non-zero | not run |
| `py-sympy-identity` | script asserts `simplify(d) == 0` | True | exact counterexample | False/None |
| `py-z3-negation-unsat` | script asserts `s.check() == unsat` | unsat | sat (model confirmed exactly) | unknown/timeout |
| `py-search-counterexample` | Hypothesis / optimizer | — (never) | confirmed counterexample | none found |
| `fidelity-audit` | card verdict field | FAITHFUL signed | UNFAITHFUL | unsigned / LLM-only |

Notes:

- The Lean reference ranks the protection levels as: editor checkmarks < `#print axioms` < `lean4checker` < `comparator` ([Validating Proofs](https://lean-lang.org/doc/reference/latest/ValidatingProofs/)) [high]. For honest, non-adversarial work, `#print axioms` plus a frozen statement is proportionate.
- Comparator compares the statement-side declarations of a trusted challenge module with the solution and checks `permitted_axioms`. It needs `landrun` and is **Linux-only** for sandboxing, under Apache-2.0 ([Comparator](https://reservoir.lean-lang.org/@leanprover/Comparator)) [high]. LeanParanoia describes itself as an "outdated experimental verifier" targeting Lean 4.25 (MIT) ([LeanParanoia](https://reservoir.lean-lang.org/@oOo0oOo/paranoia)) [high]. Do not rely on it.
- `fidelity-audit` is Tier 3 (irreducible judgment). The Lean companion checks are Tier 1. Back-translation is Tier 2 (advise and deduct). A theorem should be reported as "verified as meant" only if every Tier-1 row passes **and** the audit is signed.

---

## 5. Recommendations

### Minimal fidelity-audit protocol (per theorem)

1. **Before any proof:** Claude writes the Lean statement plus four companions: a non-vacuity witness, concrete-instance lemmas, a refuted false variant, and API lemmas for any new definition. Proofs stay `sorry`/`proof_wanted` at this stage. Set `autoImplicit false`.
2. **Python pre-check:** run a property or optimizer counterexample search on the claim over the paper's parameter domain. Run Z3 when the claim is polynomial. A FAIL here sends the statement back before any proof effort is spent.
3. **Audit card:** Claude drafts the glossary, types table, hypothesis map, quantifier line and junk-value checklist. An independent model back-translates without seeing the paper. The economist reviews the card against the paper and signs a verdict. The statement hash is recorded.
4. **Proof:** Claude proves the theorem and its companions.
5. **Close-out script:** the build passes, there is no sorry, the axioms are standard, the hash matches the card, the companions are present, and lint findings are explained. Ledger rows are written.
6. **Any statement edit after sign-off** invalidates the card (hash mismatch) and requires re-audit.

### Minimal check toolkit

Lean side: `#print axioms`, `#check @T`, `#lint`, `plausible`, and the companion-lemma pattern. Add `lean4checker` optionally. Use `comparator` only on Linux CI.

Python side: `sympy` + `hypothesis` + `z3-solver`. Add `scipy` and `python-flint` when transcendental functions or optimization claims appear.

---

## Proposed fidelity-card template

```markdown
# Fidelity card — <theorem name>
Paper: <short title>, <section/eq./page>      Card version: <n>   Statement SHA-256: <12 chars>

## 1. Paper statement (verbatim)
> ...

## 2. Lean statement (verbatim) and `#check @T` output
```lean
theorem T ... : ... := by sorry
```

## 3. Plain-English reading of the quantifier prefix
"For every <x : type> satisfying ..., there exists ... such that ..."

## 4. Glossary (every non-obvious symbol / definition)
| Lean | Plain English | Mathlib doc link | Matches paper? |

## 5. Types
| Variable | Lean type | Paper domain | Restriction/coercion risk |

## 6. Hypothesis map
| Lean hypothesis | Paper assumption ID | equal / stronger / weaker / extra | Used? (lint/ablation) |
| (paper assumptions with no Lean counterpart) | A# | MISSING | — |

## 7. Junk-value checklist
| Operation in statement | Guarding hypothesis | If unguarded: why harmless |
(/, ℕ-subtraction, ℕ-division, sqrt, log, rpow, deriv, ∑', sSup/sInf, ⊤/⊥, casts)

## 8. Solution-concept definition check (if any)
Paper definition | Lean definition | API lemmas proved (names)

## 9. Non-vacuity witness
`T_nonvacuous` — values: ...; conclusion at witness: ... (non-trivial because ...)

## 10. Concrete instance
Lean value: ...  Python value (script, seed): ...  Match: yes/no

## 11. Refuted false variant
Variant: <what was changed>   `T_variant_false` proves ¬variant via counterexample ...

## 12. Back-translation (independent model, did not see §1)
> ...
Auditor diff vs §1: ...

## 13. Pre-proof Python checks
| Check | Tool | Result (PASS/FAIL/UNVERIFIED) | Evidence |

## 14. Proof status (script output, pasted)
build: exit 0 | sorry: 0 | axioms: [propext, Classical.choice, Quot.sound] | hash: match

## 15. Verdict
FAITHFUL / FAITHFUL-WITH-NOTED-DIFFERENCES (list) / UNFAITHFUL — initials, date
```

Worked fragment. This is **not compiled** and its syntax is unverified; it only shows the shape. Monopoly with linear inverse demand `p = a - b q` and constant marginal cost `c`:

```lean
theorem monopoly_opt (a b c : ℝ) (hb : 0 < b) (hca : c < a) :
    IsMaxOn (fun q => (a - b*q)*q - c*q) (Set.Ici 0) ((a - c) / (2*b)) := by sorry
-- junk guard: `/ (2*b)` guarded by hb (b = 0 would give q* = 0 silently)
example : ∃ a b c : ℝ, 0 < b ∧ c < a := ⟨2, 1, 1, by norm_num, by norm_num⟩   -- non-vacuity
example : ¬ IsMaxOn (fun q : ℝ => (2 - q)*q - q) (Set.Ici 0) ((2 - 1) / 1) := by sorry
-- false variant (q* = (a-c)/b): at a=2,b=1,c=1, profit(1)=0 < profit(1/2)=1/4
```

---

## Toolkit table

| Tool | Checks what | Install on Windows / Py 3.14 | Limits | Licence | URL |
|---|---|---|---|---|---|
| SymPy 1.14.0 | Identities, derivatives, FOC/SOC algebra, inequality solving (univariate), assumption queries | `pip install sympy`. Pure-Python `py3-none-any` wheel. Classifiers stop at 3.13, but packagers rebuild it for 3.14 [medium] | `simplify` is incomplete. Assumptions can return None. Multivariate inequalities are weak | BSD (New BSD) | https://pypi.org/project/sympy/ |
| Hypothesis 6.168.5 | Property-based search for counterexamples over parameter domains, with shrinking | `pip install hypothesis`. Requires Python ≥3.10. 3.14 classifier present [high] | Can only refute. Coverage of thin regions is poor | MPL-2.0 | https://pypi.org/project/hypothesis/ |
| z3-solver 5.1.0.0 | Polynomial real arithmetic validity (negation unsat), witness finding, linear/integer constraints | `pip install z3-solver`. `py3-none-win_amd64` wheel, so ABI-independent [high] | Incomplete for exp/log/pow (`unknown`). `x/0` is unspecified, unlike Lean. Nonlinear runs can time out | MIT | https://pypi.org/project/z3-solver/ |
| cvc5 1.4.2 | Second SMT solver for cross-checking Z3 | `pip install cvc5`. cp314 Windows wheels [high] | Same class of limits | BSD | https://pypi.org/project/cvc5/ |
| python-flint 0.9.0 (Arb) | Rigorous ball-arithmetic bounds on transcendental expressions | `pip install python-flint`. cp314 Windows wheels [high] | Needs box subdivision. Bounds can be loose | MIT AND LGPL-3.0-or-later | https://pypi.org/project/python-flint/ |
| mpmath 1.4.1 (`iv`) | Lightweight interval arithmetic, high precision | `pip install mpmath`. Pure Python [high] | `iv` is "still experimental" | BSD-3-Clause | https://mpmath.org/doc/current/contexts.html |
| SciPy 1.18.1 (`optimize`) | Counterexample search by optimization, argmax checks | `pip install scipy`. Requires Python ≥3.12. cp314 Windows wheel **not confirmed** in the fetched index | Heuristic. Float noise | BSD-3-Clause (bundled others) | https://pypi.org/project/scipy/ |
| `#print axioms` (Lean core) | Sorry/custom-axiom/native-compute detection | Built into Lean (cross-platform via elan) | Says nothing about statement fidelity | Apache-2.0 (Lean) | https://lean-lang.org/doc/reference/latest/Axioms/ |
| `#lint` / `unusedArguments` (Batteries) | Unused hypotheses | Comes with Mathlib | Misses contradictory hypotheses | Apache-2.0 | https://leanprover-community.github.io/mathlib4_docs/Batteries/Tactic/Lint/Misc.html |
| Plausible | In-Lean randomized counterexample search | Lake dependency (Mathlib already depends on it) [medium] | Needs sampleable types. ℝ support unconfirmed | Apache-2.0 | https://reservoir.lean-lang.org/@leanprover-community/plausible |
| lean4checker | Kernel replay of `.olean` files | Lake package [medium on Windows] | Trusts the `.olean` format | Apache-2.0 [medium] | https://lean-lang.org/doc/reference/latest/ValidatingProofs/ |
| Comparator | Statement freeze (challenge vs solution) plus axiom whitelist | **Linux only** (landrun sandbox) | Heavy setup | Apache-2.0 | https://reservoir.lean-lang.org/@leanprover/Comparator |
| Lean Disprove (lean4-skills) | Certified counterexample search for Claude agents | Claude Code skill package [medium] | Recent; pilot benchmarks only | not checked | https://icml.cc/virtual/2026/82610 |

---

## Unverified / uncertain

- **Plausible on ℝ.** Whether `plausible` can sample real numbers (the Real type lacks decidable equality) was not confirmed. Assume it cannot, and use ℚ instances or Python for real-valued search.
- **SciPy cp314 Windows wheel.** The fetched PyPI index excerpt did not show one. Confirm with `pip download scipy --only-binary=:all:` before relying on it.
- **SymPy on 3.14.** It is a pure-Python wheel and distro packages rebuild it for 3.14, but the PyPI classifiers stop at 3.13 [medium].
- **ENNReal conventions** (`∞ - ∞ = 0`, `0⁻¹ = ∞`) and the exact `Real.sSup_*` lemma names are from working knowledge. The fetched doc pages did not quote them [medium].
- **The BPF / Faithfulness Gap figures** (89.6% detection) come from a single recent preprint [low].
- **A widely repeated claim** that an autoformalizer's LLM-judge accuracy (97%) fell to 67% under manual checking appeared in a search summary. Its primary source was not located, so it is omitted from the body.
- **`lean4checker` and `lake` on Windows** are expected to work through elan, but this was not tested here.
- **Machine-readable Lean messages** (`lean --json`) are a better parse target than grepping text. The flag's current behaviour was not verified.
- **No source measures misformalization rates in economic-theory formalization specifically.** The rates above come from competition and undergraduate/graduate maths benchmarks.
