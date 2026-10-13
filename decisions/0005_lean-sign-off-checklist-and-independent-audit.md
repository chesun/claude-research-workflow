# ADR-0005 — Lean sign-off: the signature is the approval, plus a checklist and an independent audit

**Date:** 2026-10-14
**Status:** Decided 2026-10-14 by the owner (v3; v1 reviewed blind for fit-for-purpose 66/100 and efficiency 82/100, v2 verified 78/100)
**Scope:** Methodology / theory
**Data quality:** Full context
**Supersedes:** #0004, the "user is the Lean auditor" bullet only. The rest of ADR-0004 stands.
**Sources:**
- pilot read-out: `quality_reports/session_logs/2026-10-11_hook-launcher-fix-and-theory-brainstorm.md` §11 (calibration) and §12 (pilot);
- reviews: v1 `quality_reports/reviews/2026-10-14_adr-0005_{fit-for-purpose,efficiency}_review.md`; v2 `quality_reports/reviews/2026-10-14_adr-0005-v2_verification_review.md`;
- phase 2 plan (COMPLETED): `quality_reports/plans/2026-10-12_theory-workflow-phase2-lean-plan.md`;
- spec: `quality_reports/specs/2026-10-11_theory-proof-workflow-spec.md`, acceptance #8;
- pilot card: BDD `theory/blueprint/cards/prop-nstar-interior-ac.md` (BDD `5da9772`, `bef1c6a`).

## Context

Under ADR-0004 the owner is the only check that a Lean statement means what the node's statement means. Nothing mechanical can confirm that. The comparator proves only that the proofs prove the signed statements. The owner signs a fidelity card per node and approves each status line (`checked -> formalized`, then `formalized -> verified`) in a separate step.

The pilot, `prop:nstar-interior-ac` (verified 2026-10-14), showed three things.

1. **The second approval adds little.** By the time the owner sees a status line, the validator has already confirmed a signed card and a PASS report. Approving it repeats the signature. The owner said so.
2. **The owner cannot audit the full card unaided.** The owner has no Lean background and found the ten-section card overwhelming. What worked was a numbered list for each part: the Lean assumptions and claims written in the paper's notation, each compared by the owner with the paper. With that list the owner finished in about 30 minutes. Acceptance #8 ("signed after reading it unaided") was therefore met only in part.
3. **The owner is a thin filter on hard statements.** On three short practice cards the owner caught both planted defects, a dropped hypothesis and a weakened conclusion, and raised one mild false alarm. The owner expects their catch rate to fall as statements get harder.

The v1 reviews also found a gap that ADR-0004 already had. The owner's signature (`initials date`) is not tied to the statement it was given for (`bin/blueprint_check.py:341`, `:368`). If a card's `Statement SHA-256` header is regenerated after a statement edit, the old signature still passes. Under ADR-0004 the status-line approval was the only, weak, human backstop for this. Dropping that approval means the signature itself must be bound.

## Decision

1. **The signature is bound to the statement, and the bound signature is the approval.**
   - **Bound.** `Signed off` becomes `<initials> <YYYY-MM-DD> sha:<first 12 hex of the card's Statement SHA-256>`. The owner copies the 12 characters from the card header.
     - The validator requires the prefix to match the card's Statement SHA-256. `lean_check` already requires that hash to match the statement file. No date ordering is checked: the validator replays every past `formalized` and `verified` line against the current card, so a date rule would fail any re-signature.
     - The formalizer resets `Verdict`, `Signed off` and `Independent audit` to `PENDING` whenever it rewrites a card header.
     - No agent and no Claude session writes `Verdict`, `Signed off` or `Audit override`. A prefix that no longer matches is never repaired: it means the owner re-signs.
   - **Approval.** Once the card is signed and the matching `lean_check` report is PASS, Claude appends the status line and tells the owner. There is no second ask.
     - This covers `formalized` (a statements-mode PASS) and `verified` (a full-mode PASS on the same statement SHA-256).
     - The line keeps actor `user`. It now records the owner's signature as checked by the validator, not a separate act by the owner.
     - The owner can withdraw a signature. Withdrawing sends the node back down by the existing down-move rules.
   - **Known limits, stated plainly.**
     - **Between checks.** The binding is checked against the statement file only when `lean_check` runs. The Lean project sits outside the repository, where the validator cannot see it. An edit to the statement file after the last run, with no card rewrite, leaves a signature that is bound to a version that no longer exists, until the next run. To narrow that window, `/theory status` runs `lean_check --hash` (hash only, no build) on every `formalized` and `verified` node whose Lean project is present, and reports any mismatch as stale. That check is advisory. The next full run makes it binding, because a mismatch FAILs and takes `verified` away.
     - **Authorship.** The validator checks that a signature is well formed and matches. It cannot check who typed it. The rule above (no agent writes the sign-off fields) is an instruction, not a check. It covers the realistic mistake, an "auto-fix" that refreshes a prefix.
     - **Forgery.** Deliberate forgery is outside the threat model (ADR-0004 phase 2: Lean-level mistakes, not an actor with shell access).
     - **Card prose.** Edits to the card's prose after signing are not hashed. They cannot change what the Lean says, which is what the signature is bound to.
2. **The owner signs a checklist, not the full card.**
   - **What the list is.** For each part, the card opens, right after the header, with a numbered list. Every line quotes one Lean clause verbatim (a hypothesis or one conjunct of the conclusion) and gives the back-translator's plain-mathematics reading of it, written with the Lean names.
     - Once the three glossaries agree (the formalizer's, the back-translator's and the auditor's), Claude rewrites each reading in the paper's symbols. It substitutes symbol for symbol from the agreed glossary and changes nothing else. Any glossary disagreement is shown to the owner before the list is. The owner marks each line against the node's statement as same, missing, added, weaker or stronger. A short reminder sits above the list: an added assumption makes the Lean claim weaker; a dropped assumption makes it stronger, and possibly false.
   - **Who writes it.** The blind back-translator writes the list. It sees only the statement file, with comments stripped, and derives its own glossary as in the pilot. It gets no symbol table from anyone. Claude compares its glossary with the formalizer's and names every difference to the owner.
   - **Coverage is checked.** The auditor (item 3) checks that every top-level hypothesis and conjunct of each `_stmt` has a line, after it has recorded its own verdict.
   - **The worked instance (section 9).** The formalizer and the auditor each compute the paper-side values for the sanity parameters, independently. The auditor gets only the parameters and the node statement, in its blind step. The owner checks that the two agree, and checks the arithmetic. The Lean-side value is the sanity companion, which is a claim until the full check proves it at `verified`.
   - **What the card drops.** Section 3 becomes the marks on the list. Section 5 (quantifiers) is dropped as a duplicate of the list. Section 8 shrinks to the back-translator's glossary and its "anything odd" notes. Sections 2, 4, 6 and 7 stay as a reference appendix the owner may skip. Header fields stay in the first lines, where both checkers read them.
3. **An independent auditor reviews every card before the owner signs.**
   - **The agent.** A new `card-auditor` agent on `fable` (ADR-0003). In its first step it sees only the node's `## Statement` (the hash-bound text) and the statement file. It does not see the formalizer's card, the back-translation, a symbol table or any verdict.
   - **What it does.** It derives its own glossary, writes a per-part map (equal / weaker / stronger / missing) with the Lean clause cited for each finding, and gives a verdict. Only after that is recorded is it shown the checklist, for the coverage check in item 2.
   - **The record.** The audit is a report file, `theory/blueprint/checks/<node>/card_audit_<date>.md`, with header fields `Node`, `Lean`, `Statement SHA-256`, `Verdict` and `Coverage` (PASS or FAIL). The card header field `Independent audit:` cites that path. For `formalized`, the validator requires all of the following:
     - the file exists;
     - its SHA-256 matches the card's;
     - its `Coverage` is PASS (a FAIL cannot be overridden: it means a Lean clause is missing from the owner's list, so the list is regenerated and coverage re-checked);
     - its verdict is FAITHFUL or WITH-NOTED-DIFFERENCES, or the card carries an `Audit override:` line in the form `<initials> <date> sha:<12 hex>: <reason>`.
   - **Disagreement stops the node.** If the auditor and the owner disagree, nothing moves until the owner decides. The disagreement and its resolution go in section 10. An override is the owner's explicit, signed act.
   - **Calibration before trust** (ADR-0004).
     - Before the auditor is relied on, it runs on a fresh sealed set of practice cases. Each case is a node statement and a Lean statement file, and the answers are kept outside the repository until the run is done.
     - It runs on seven cases. Six carry one planted defect each, one per class: a dropped hypothesis, a weakened conclusion, an omitted conjunct, a mis-mapped symbol, a swapped quantifier order, and a missing guard against a junk value (for example, Lean's division by zero gives zero). The seventh is faithful.
     - Each case gets one fresh dispatch.
     - The bar is every planted defect caught and no false alarm on the faithful case. On a failure, the auditor prompt is revised once and re-run on a second fresh set. A second failure goes to the owner.
     - The 2026-10-12 practice cards are not reused, because their answers are now in the repository.
   - **Review point.** After five audited nodes, the session log counts the auditor's catches and false alarms, and the owner decides whether it stays.
4. **Rollout includes the pilot.** The pilot card is converted to the new form, audited, and re-signed with the bound signature. Without that, the validator change would fail its existing `formalized` and `verified` lines. If the audit disagrees with the pilot's verdict, the node goes back to `checked` until the owner resolves it.
5. **Acceptance #8 is restated** for later nodes: "every checklist line on the signed card carries one of the five marks, the signature is bound to the statement SHA-256, and an independent audit with coverage PASS agrees or is overridden by the owner" (Tier 1, checked by the validator). Added to that is the owner's comparison of each line with the node's statement (Tier 3, the owner's judgment). The pilot's partial result stands as recorded.

## Consequences

- **Owner time per node** drops to the checklist plus copying a 12-character hash: about 30 minutes on the pilot, and less once the list leads the card. The owner no longer approves status lines.
- **Who can catch what.**
  - A mis-reading or a weakened clause has three readers: the back-translator, which writes the list blind to the paper; the auditor, blind to the card and the back-translation; and the owner.
  - An omitted clause has two readers, the auditor's blind map and its coverage check. The owner cannot compare a line that is not on the list.
  - A mis-mapped symbol has three glossaries to disagree: the formalizer's, the back-translator's and the auditor's.
  - The readers' blind spots are correlated, since all of them read the same Lean, but none sees another's conclusions before giving its own.
- **Cost.** One fable dispatch and one short follow-up per node; a one-off calibration of seven dispatches, or fourteen on a re-run; one retroactive audit for the pilot.
- **Changes to make** (one plan; the `bin/` items are gated by ADR-0002):
  - `templates/theory/fidelity-card.md`: header fields first, including `Independent audit:` and the bound `Signed off`; then the checklist; section 5 dropped; section 8 shrunk; sections 2, 4, 6 and 7 as an appendix.
  - `.claude/skills/theory/SKILL.md`, the formalize and prove modes:
    - the back-translator writes the checklist and its own glossary;
    - the glossaries are diffed;
    - the auditor runs in two steps;
    - the status line is appended without a second ask.
  - `.claude/agents/card-auditor.md`: the new agent, and its sealed calibration set (built outside the repository; committed after the run).
  - `.claude/agents/formalizer.md`: reset the sign-off fields on any header rewrite; write the section 9 arithmetic; the handover note.
  - `bin/blueprint_check.py`, in `_card_problem` and the evidence checks:
    - the bound signature;
    - every checklist line carries one of the five marks;
    - the audit report (exists, SHA, coverage, verdict, or an override);
    - test fixtures for each.
  - `bin/lean_check.py`: no change. Its card check reads the header, which stays at the top, and `--hash` already exists. The plan confirms both with tests.
  - `/theory status` in `.claude/skills/theory/SKILL.md`: the advisory `--hash` sweep (item 1, Known limits).
  - The pilot card, converted, audited and re-signed (item 4).
- **Rules out:** a node reaching `formalized` on the owner's signature alone; a signature carried over to a statement that has changed by the time `lean_check` runs (between runs, see Known limits); and Claude setting a status without a bound signature.

## Not decided

- Whether a disagreement between auditor and owner should also trigger a second auditor run before the owner decides.
- Whether the owner guide (efficiency #8 of the phase 2 plan) is a separate document or is the reminder above the checklist.
