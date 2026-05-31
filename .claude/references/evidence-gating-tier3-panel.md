# Evidence-Gating Tier-3: Adversarial-Verify / Diverse-Lens Panel

**Class:** A (universal). Pointer-loaded convention for `.claude/rules/adversarial-default.md` § Evidence gating and `.claude/references/evidence-gating-detail.md` (Tier 3). Open this when a verdict is **irreducible judgment** — no single artifact pins it. There is no auto-load.

**Status: advisory.** This whole convention is a discipline for *how* to verify a Tier-3 judgment verdict, not a gate that blocks. **Nothing in this system blocks a commit, a PR, or a turn based on this convention.** Enforcement is non-blocking: a load-bearing Tier-3 `PASS` shipped without a panel is, by the verdict vocabulary (`evidence-gating-detail.md`), not a credible `PASS` — the honest verdict is `UNVERIFIED`, recorded as such in the ledger. The word "mandatory" below is a **protocol obligation for credible work**, not a system gate: it means "a credible Tier-3 `PASS` for this case *requires* a panel," not "the harness refuses your turn until you ran one." It defines what a credible Tier-3 `PASS` looks like and when producing one is obligatory versus optional.

**Design of record:** `quality_reports/reviews/2026-05-28_whole-picture-critic-gates-dispatch.md` §7. **Build plan:** `quality_reports/plans/2026-05-29_evidence-gating-build-plan.md` Phase 4.

---

## What Tier 3 is

A Tier-3 claim is one that does **not** decompose into a script check (Tier 1) or an artifact citation (Tier 2). The evidence is a reasoned argument, and the only honest verification is to subject that argument to independent challenge. Examples:

- Is this proof correct?
- Is the identification sound (exclusion restriction credible, parallel trends defensible)?
- Is this writing clearer than before?
- Is the stated goal actually *achieved* on a shipped artifact, beyond the Tier-1/Tier-2 sub-claims that operationalization extracted?

Tier 3 is the residue left after Step-0 operationalization has pushed every checkable sub-claim down toward Tiers 1 and 2 (see `evidence-gating-detail.md` § Step 0). Keep the residue as small as operationalization allows — the cost of the panel below is the reason.

---

## When the panel is MANDATORY

A credible Tier-3 `PASS` for a **load-bearing judgment verdict** requires an adversarial-verify panel — a Tier-3 `PASS` that, if wrong, would propagate a defect into a shipped artifact. (This is the protocol obligation, not a hard gate: skipping the panel does not block anything, but the verdict is then `UNVERIFIED`, not `PASS`.) The load-bearing cases:

- **Identification soundness** — before a strategy memo's identification verdict is treated as approved.
- **Proof correctness** — before a formal-model proof is treated as established.
- **"Goal achieved" on a shipped artifact** — the final "this artifact meets its stated goal" verdict, where the goal could only be partly operationalized and a judgment residue remains.

These are the verdicts where a silent false `PASS` is most expensive, so the N× token cost of a panel is justified.

## When the panel is OPTIONAL

Everywhere else. Tier-3 verdicts that are not load-bearing — an exploratory read, a low-stakes "is this clearer" on a sandbox draft, an early-phase encouraging review — **may** use a panel but are not required to. The reason is cost: an adversarial panel spends **N verifiers' worth of tokens per claim** (one producer plus each refuter or lens). Reserve that spend for verdicts that ship.

When optional and skipped, the verdict is still subject to the verdict vocabulary (`evidence-gating-detail.md`): a bare assertion is never a `PASS`; absent a panel the honest verdict is `UNVERIFIED` unless other evidence carries it.

---

## How the panel works

### Separation of powers (non-negotiable)

The verifier is **never the producing critic.** A model grading its own judgment is self-scoring — exactly the failure `agents.md` §2 (Separation of Powers) forbids. The producer of a Tier-3 verdict and its verifier must be independent dispatches.

This generalizes the worker-critic separation: the critic *produced* the judgment verdict; the Tier-3 panel members are independent of that critic, the same way a critic is independent of the worker it scores.

### Two panel shapes

Pick one; both satisfy the mandatory cases.

1. **Refutation panel.** Dispatch one or more independent verifiers, each prompted to **refute** the verdict — to find the flaw, not to confirm. The instruction is adversarial by construction ("assume this judgment is wrong; produce the strongest case against it"). This mirrors the **deep-research skill's adversarial-verify pattern**, where fanned-out verifiers are tasked to challenge each synthesized claim rather than rubber-stamp it.

2. **Diverse-lens panel.** Dispatch multiple verifiers, each from a distinct evaluative lens (e.g. a methods lens, a domain lens, a robustness/falsification lens). Each lens casts a **single binary vote** — `sustain` or `reject` — accompanied by a one-line reason. The vote is the unit the decision rule counts; the reasons go in the review report. A lens does **not** itself produce a fresh Tier-3 judgment that needs its own panel (that would stack panels indefinitely); it produces a bit plus a rationale, evaluated flat. If a lens cannot decide from its angle, it abstains (its vote is not counted toward either side, and the panel is treated as the next smaller size for the majority test below).

### The decision rule

- **Majority-refute kills the `PASS`.** "Majority" means **strictly more than half** the non-abstaining votes (`> 50%`). With an odd panel this is unambiguous; **prefer odd-sized panels** for exactly this reason. For an even panel that ties (`= 50%` refute), the tie **downgrades to `UNVERIFIED`** — a verdict the panel split on has not survived refutation, so it does not earn `PASS`.
- A refutation panel and a diverse-lens panel apply the same count: refute-votes (refutation panel) or reject-votes (diverse-lens panel) `> 50%` of non-abstaining members ⇒ not `PASS`.
- **Which non-`PASS` label.** A panel that refutes splits into two cases:
  - **`REFUTED`** — a refutation is **dispositive**: at least one panel member produced a concrete, correct counter-argument that disproves the verdict (a counterexample, a broken step, a failed falsification). The claim was checked and found wrong. (`REFUTED` is the Tier-3 analogue of Tier-1/2 `FAIL`; record it as `FAIL` in the ledger `Result` column, with the `refuter_tally` and the dispositive reason in Evidence.)
  - **`UNVERIFIED`** — the panel raised doubts the producer has not yet answered, but no single refutation is dispositive. Evidence is *insufficient*, not *contradicted*. The producer must address the refutations and re-verify. This matches `evidence-gating-detail.md:46` (`UNVERIFIED` = evidence absent / not yet produced).
  - The distinction matters: `REFUTED`/`FAIL` says "this is wrong"; `UNVERIFIED` says "this is not yet shown." Do not collapse a dispositive refutation into `UNVERIFIED`.
- A verdict survives to `PASS` only if it **survives independent refutation** — i.e. the panel tried to break it and could not (no dispositive refutation, and refute-votes `≤ 50%`).
- Record the panel outcome. Tier-3 verdicts that gate a load-bearing artifact should leave a trail: the `refuter_tally` column in `.claude/state/verification-ledger.md` records how many panel members refuted versus sustained (and how many abstained), and the review report (per `agents.md` §2 canonical review-report path) holds the reasoning.

---

## Cost discipline (why this is graduated, not universal)

A panel is the most expensive verification mechanism in the workflow — N model dispatches per single claim. The discipline is therefore **graduated**: mandatory for the small set of load-bearing judgment verdicts above, optional everywhere else. This is the same logic as the whole evidence-gating design — scale the verification *mechanism* to how checkable the claim is and how costly a wrong `PASS` would be — applied at the most expensive end of the spectrum.

---

## Honest limits

- **Probabilistic, not hard.** A surviving Tier-3 verdict has been challenged and held; it has not been *proven*. Tier-3 reduces error, it does not eliminate it (`evidence-gating-detail.md` § Honest limits).
- **Presence ≠ authenticity.** The panel catches fabricated *reasoning* a single reviewer would wave through; it does not catch a fabrication that survives independent refutation.
- **Advisory.** No part of this convention blocks. It defines the standard for a credible Tier-3 `PASS`; the honest enforcement is the verdict vocabulary itself — a load-bearing Tier-3 shipped without a panel is `UNVERIFIED`, never a silent `PASS` — not a hard gate. (A critic deduction is a candidate future hardening; it is not wired into any critic agent today.)

---

## Cross-references

- `.claude/rules/adversarial-default.md` — the rule this operationalizes (burden of proof on the asserter).
- `.claude/references/evidence-gating-detail.md` — the three tiers, the verdict vocabulary, and the Tier-3 row in the enforcement-actors map this doc expands.
- `.claude/rules/agents.md` §2 — Separation of Powers; the verifier-independence requirement above is a generalization of worker-critic separation.
- `.claude/rules/workflow.md` §1 — Step-0 operationalization tags each acceptance criterion with a tier; Tier-3 criteria route here.
