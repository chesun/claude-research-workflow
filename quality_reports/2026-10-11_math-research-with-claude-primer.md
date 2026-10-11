# Rigorous theory with Claude — a working primer (draft for discussion)

**Date:** 2026-10-11
**Status:** DRAFT — thinking notes for the theory/proofs feature brainstorm. Not a plan.
**Evidence level:** Section 5 rests on files I read in this session. Sections 1–4 are my working knowledge and are **unverified**; every claim marked [verify] goes into the sourced survey before it shapes a design.

---

## 1. Why AI "proofs" are untrustworthy by default, and the two known fixes

A language model writes proofs that *read* correct. The common failures are a skipped case, a quietly strengthened hypothesis, a step justified by "clearly", a lemma quoted from memory that is false or misstated, or an argument that proves something slightly different from what was asked. Asking the same model "is this right?" doesn't help much, because a checker that sees the reasoning tends to agree with it. The `math-olympiad` plugin README cites a study where self-verified olympiad success fell from about 86% to under 5% once humans graded the proofs [verify against the paper itself].

There are two fixes. They are complementary, not alternatives.

- **Independent adversarial checking in prose.** A fresh agent that never saw the reasoning gets only the clean statement and proof. It is told to attack: find a counterexample, find the step that needs an unstated assumption, check that the hypotheses are actually used. This catches a lot, but it is still a model's judgment. It is what the `math-proof` and `math-olympiad` plugins do.
- **Formal verification (Lean).** The proof is written in a language where a small, trusted program (the Lean "kernel") checks every inference mechanically. If it compiles, the stated theorem follows from the stated definitions. The model cannot bluff past the kernel. As I understand them, the much-publicized recent AI math results come in both forms: some are natural-language proofs graded by humans, others are proofs checked by Lean [verify].

## 2. What Lean buys you, and what it does not

**What it buys.** Certainty that *the formal statement* follows from *the formal definitions and hypotheses*. In practice this rules out a whole class of errors: the gap, the missing case, the false "clearly".

**What it does not buy — the main risk is misformalization.** Lean checks the theorem you *wrote*, not the theorem you *meant*. In economics this risk is sharper than in pure math, because the hard part is often modeling rather than proving:
- a preference assumption encoded slightly too strongly, so the result is true but uninteresting;
- hypotheses that no object satisfies, so the theorem is vacuously true. Your `theorist-critic` already checks non-vacuity (item 16), and that check becomes *more* important with Lean, not less;
- "for all" and "there exists" swapped, or an equilibrium concept defined subtly differently from the one in the paper.

So a Lean proof is only as good as a human-readable check that the Lean statement matches the paper's statement. That check is a judgment call (Tier 2/3 in this repo's evidence-gating terms), while the kernel check is Tier 1.

**Costs [verify all].**
- *Learning curve.* You don't need to become a Lean programmer if Claude writes the Lean, but you do need to read Lean theorem statements well enough to audit them.
- *Library coverage.* Lean's math library, Mathlib, covers real analysis, order theory, convexity, linear algebra, measure theory and probability. My understanding is that it covers far less economics-specific machinery, such as the fixed-point theorems behind equilibrium existence or monotone comparative statics. Missing pieces would have to be built, which is expensive.
- *Effort.* Formalizing a proof has historically cost many times the effort of writing it on paper. LLM assistance is shrinking that, but not to zero.

The consequence is that **Lean should be selective**: use it for the lemmas that carry the paper, or where an error is suspected, or where the math is elementary enough to formalize cheaply. Not for everything.

**Tooling [verify].** Lean installs through `elan` (cross-platform, including Windows); a Mathlib project downloads a large prebuilt cache. Community MCP servers expose Lean's language server to Claude, so it sees errors and proof goals as it writes. A Lean toolchain is not installed on this machine today.

## 3. Your instinct already has a name: the "blueprint" method

What you describe — break a theory into small steps, prove each one rigorously, let conclusions follow — is how large formalization projects are actually run. A **blueprint** is a dependency graph of definitions and lemmas, where each node carries:
- an informal statement and proof,
- the nodes it depends on,
- a status: *stated → proved informally → checked independently → formalized → kernel-verified* (or *refuted*).

Large community formalization projects have used a blueprint tool (`leanblueprint`) to coordinate exactly this [verify]. The `math-proof` siege skill's ledger (each claim PROVED / REFUTED / OPEN) is the same idea at a smaller scale.

A blueprint works even with **no Lean at all**. It gives you the structure; Lean is an optional extra level of assurance per node.

## 4. Mechanisms for "don't chase the conclusion"

The danger you name is motivated reasoning: an agent told "prove theorem X" will produce something that looks like a proof of X. Ways to resist it:

1. **Separate conjectures from results.** The ledger records conjectures as conjectures. "Refuted" and "true only under an extra condition" are first-class, successful outcomes, not failures.
2. **Examples before claims.** Compute small cases first: two agents, linear utility, a few numeric parameter draws. Let the pattern suggest the statement. The `theorist` agent already prescribes this order of work; it needs a place to record the results.
3. **Try to break each conjecture before proving it.** Run a cheap counterexample search (Python/sympy over random or edge-case parameters) before investing in a proof.
4. **Make the prover a different agent from the checker.** The checker sees only the statement and proof text, never the goal's motivation. This is the existing worker/critic split, made blind.
5. **Treat weakening as a legitimate move.** If the proof needs an extra assumption, the ledger records the weaker theorem with the assumption added, rather than hiding it.

## 5. What exists now (read this session)

- **`behavioral` overlay:** `theorist` agent (framework choice, examples before generalizing, definitions with boundary examples, proof-writing style), `theorist-critic` (a 16-item checklist, mostly presentation plus non-vacuity and the "clearly" audit), `/theory develop|review`, empty `theory/` and `theory/proofs/`. Both agents start by reading `quality_reports/paper_learnings/theory-writing-learnings.md`, **which exists on no branch**. That reference is dangling. Correctness checking today is one critic reading the proof; there is no blind verifier, no counterexample search, no ledger of proof status, no formalization.
- **`math-proof` plugin (Anthropic, available, not installed):** `/math-proof:solo` (one session, staged notes) and `/math-proof:siege` (hours of judge + blind worker rounds, a PROVED/REFUTED/OPEN ledger, double line-by-line checks, a `proof.md` with an honest Status section). It is built for **one hard, fully stated problem in an empty directory**, with web tools off. It wants environment settings that affect every session reading that settings file, and siege can run 100+ subagents. It quotes literature from memory, which conflicts with primary-source-first. **Best fit: a tool to aim at one stubborn lemma, not the theory workflow itself.**
- **`math-olympiad` plugin (available, not installed):** competition-style solving with context-isolated, failure-pattern-armed verifiers and a willingness to say "no confident solution". Its verifier patterns are worth borrowing for the blind checker.
- **Repo fit:** the evidence-gating tiers map cleanly. Kernel-checked or script-checked claims are Tier 1; a blind verifier's verdict is Tier 2; "the Lean statement means what the paper means" is Tier 2/3.

## 6. A possible shape (strawman, to react to — not decided)

1. **Blueprint and proof ledger** for a theory project: one file per node, or one tracked graph, with the status lifecycle from section 3. Prose first; Lean optional per node.
2. **Exploration step:** examples + counterexample search before any proof attempt (Python, cross-platform).
3. **Blind verifier agent:** fresh context, statement + proof only, adversarial patterns. Gates "proved informally → checked".
4. **Optional Lean lane:** per node, formalize → kernel-check, plus a statement-fidelity review of the Lean theorem against the paper's statement.
5. **Plugin hand-off:** send one stubborn node to `/math-proof:siege` in a scratch directory; its `proof.md` comes back as a candidate that still goes through the blind verifier.
6. **Fix the dangling theory-writing reference** and fold proof-status into `theorist-critic`.

## 7. Questions only you can answer

- What kind of math your theories use (this decides how much Lean is realistic).
- Which machine(s) theory work happens on, and whether installing a Lean toolchain there is acceptable.
- Whether this lives on the `behavioral` overlay (where `theorist` is) or on `main`.
- How much Lean you want to learn yourself, versus auditing statements that Claude writes.
