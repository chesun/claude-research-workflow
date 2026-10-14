# ADR-0005 implementation Review — final whole-branch
**Date:** 2026-10-14
**Reviewer:** final whole-branch reviewer (independent, general-purpose agent)
**Target:** bin/blueprint_check.py, bin/test_blueprint_check.py, bin/test_lean_check.py, templates/theory/fidelity-card.md, templates/theory/blueprint-node.md, templates/theory/lean-layout.md, .claude/skills/theory/SKILL.md, .claude/agents/formalizer.md, .claude/agents/card-auditor.md
**Score:** 88/100
**Status:** Active

Range reviewed: 4fec069..8bf92b8 (full diff, 37 files) plus the uncommitted `bin/test_lean_check.py` (`test_card_template_readable`), which this review names as a target so it can be committed under ADR-0002. Pilot checked read-only in BDD at f779e92. Suites re-run 2026-10-14: `py -I bin/test_blueprint_check.py` → 185/0, `py -I bin/test_lean_check.py` → 204/0 (includes the uncommitted test), `py -I bin/test_blueprint_tools.py` → 74/0, `py -I bin/agent_lint.py .` → PASS (40 files). BDD: validator copy byte-identical to workflow HEAD (`diff` empty); `py -I bin/blueprint_check.py theory/blueprint` → UNVERIFIED, 34 warnings (the pre-existing set), 0 errors, exit 3 — the pilot node passes every new rule.

## Review Focus (plan), each checked deliberately

1. **Old-format card** → `ln_old_format_card_message` exists and passes; the message at `bin/blueprint_check.py:464-466` quotes the exact first-12-hex to copy ("re-sign as `<initials> <date> sha:<12>` after the card is converted and audited"), and Task 4 step 1 reproduced it on the real pilot (session log §17, correctness review's independent repro named `sha:a6cb62a1734a`). PASS.
2. **Upper-case prefix / extra spaces** → `ln_signed_prefix_case_and_spaces` passes (`CS  2026-10-12  sha:ABABABABABAB` → PASS; compare at `:473` is `.lower()`; `\s+` in `SIGNED_OFF_RE:343`). A trailing space after the signature is also accepted (my probe P10), consistent with the "runs of spaces" intent. PASS.
3. **Empty or misspelt mark** → `ln_checklist_bad_mark_named` / `ln_checklist_empty_mark_named` pass; the error names the part and the row number (`:424`). PASS — but see Important #1 for a row the parser never reaches, and Minor #4 on "line" meaning the `#` cell.
4. **Audit for another node / outside `checks/<stem>/`** → `ln_audit_wrong_place_other_node`, `ln_audit_wrong_place_cards`, plus the review-round additions `rv_audit_node_checked`, `rv_audit_lean_checked`, `rv_audit_filename_checked` (the correctness review's mutation run showed the first two tests alone did not pin the field and filename checks; the additions do). PASS.
5. **CRLF / BOM** → `ln_checklist_crlf_bom` passes; `_visible` (`:356-359`) and the `utf-8-sig` reads handle both. PASS.

## Strengths

- **Review-loop discipline was real, not performative.** Both red-team Criticals (checklist in a comment/fence; `###` ends the section) and the duplicate-header-field High have named RED→GREEN regression tests (`rv_checklist_in_comment_ignored`, `rv_checklist_in_fence_ignored`, `rv_subheading_does_not_end_checklist`, `rv_duplicate_card_field_rejected`); the correctness review's mutation findings each got a killing test (`rv_mark_vocabulary_enforced`, `rv_audit_node_checked`, `rv_audit_lean_checked`, `rv_audit_filename_checked`, `rv_checklist_no_rows_rejected`).
- **The implementer went beyond the spec where the spec had a hole:** the newest-audit rule (`newest_card_audit`, `:429-438`, `:503-506`) closes red-team #6's stale-FAITHFUL-audit window that ADR-0005's letter permits, and `rv_newer_audit_wins` pins it.
- **The `header_fields` comment fix, found while writing the template, was handled correctly under ADR-0002:** out-of-task-scope code change ruled in the ledger, given its own combined review, and its M2 follow-on (`newest_lean_report` skipping a comment-hidden FAIL report) fixed with `rv_commented_report_header_not_skipped`.
- **Calibration is clean evidence:** seven compiled cases, answers sealed outside every repo, 6/6 defects caught and named, no false alarm on the faithful case, shuffled numbering, docstrings that lie as a formalizer's might; limits stated in the README.
- **The pilot replay worked exactly as designed:** the converted card carries the bound signature `CS 2026-10-14 sha:a6cb62a1734a` matching its `Statement SHA-256`, 31 `same` rows, a matching audit with `Coverage: PASS`, and the hashes unchanged from `bef1c6a`.
- The uncommitted `test_card_template_readable` is sound: it reads the real template, exercises both checkers' header readers, asserts the unmarked template is *not* a signable card, and checks `duplicated_fields` — it is the lean_check-side guard the plan asked for.

## Issues

### Critical (Must Fix)

None.

### Important (Should Fix)

1. **A checklist data row detached from its table header is silently dropped from both the mark check and the FAITHFUL gate.** `checklist_rows` (`bin/blueprint_check.py:395-408`): any non-`|` line (a blank line, a prose note) sets `in_table = False`; the next `|` line is then consumed as a candidate *header* row (`:401-404`), and since a data row's first cell is not `Part`, the row and everything after it in that "table" are skipped. Repro (synthetic, via the test fixtures): a `formalized` node whose FAITHFUL card has `checklist("same") + "\n| (b) | 1 | \`c-b\` | clause b | weaker |\n"` → **validator PASS** (must FAIL under the FAITHFUL-all-`same` rule); same with a prose line between, and a misspelt mark in a detached row under WITH-NOTED-DIFFERENCES also passes. This is the residue of red-team #2/#5: the fix handles a `###` sub-heading *followed by a new `Part…Mark` header row* (`rv_subheading_does_not_end_checklist`) but not a row separated from any header — the exact shape of red-team probe F2b, which the session log's fix list does not cover. Realistic trigger: the owner hand-adds a `missing` row after a blank line, or rows are grouped per part with blank lines between groups. Mitigations: the coverage auditor reads the table as text, so omitted-clause coverage is not fooled; only the mark-vocabulary and FAITHFUL gates are. Fix: inside the `## Checklist` section, treat a first table line that is not a `Part…Mark` header but splits into ≥5 cells as an error naming the line ("checklist row outside its table — remove the blank line above it"), or error on any `|` line not inside a recognized checklist table once one has been seen; add regression tests for the blank-line and prose-line shapes. Do this before the next node is formalized.

### Minor (Nice to Have)

2. **The glossary-disagreement branch is still only half-routed.** `.claude/skills/theory/SKILL.md:110` names a continuation only when the *formalizer's* glossary is wrong (restart at step 1); when the owner rules that the back-translator's or auditor's reading is the wrong one, no step says to correct the readings and resume at step 5. Flow-docs review Low #8 is marked fixed in session log §15 but is fixed for one of the three outcomes.
3. **`duplicated_fields` scans the whole card** (`bin/blueprint_check.py:362-370`, called at `:480`), so a bold `**Verdict:** FAITHFUL`-shaped line quoted in Owner's notes or the appendix FAILs the card as a "duplicate header field". Fail-closed and the message names the remedy, so this is friction, not a hole — and the whole-file scan is the right call (the appended-reset attack it blocks can sit below line 60). Suggest one template comment line: don't quote header fields verbatim in the card body.
4. **"line" in the checklist error is the row's `#` cell, not a file line** (`:424`, fed from `:407`). This matches the plan's own example (`part (b) line 3`), so it is plan-conformant; "row" would be clearer, and an owner-added row with a duplicate or blank `#` shows `?`.
5. **Pilot process residue, for the owner's awareness at the 5-node review point:** the owner's blanket "they all look the same to me" was transcribed by Claude as `same` on all 31 rows (BDD card Owner's notes; session log §17). Marks are not among the fields no agent may write, the transcription is recorded in the card, and ADR-0005 item 5 says the pilot's partial result stands — but the Tier-3 leg of acceptance #8 (the owner's per-row comparison) was again met only in part, which is worth counting honestly when the auditor's stay-or-go decision is made.

## Declined to judge

Behaviors considered and set aside, with the reason; the executor rules on each line.

- `lean_check.card_fields` not given the `_visible` treatment (two checkers disagree on commented-out header fields) — found by the header-fields review (M1), fails closed, plan forbids modifying `bin/lean_check.py`, and a TODO backlog row with the exact fix exists.
- The owner can open the audit report in `checks/` before signing — ADR-mandated field, accepted as design residue in the flow-docs review (its path is not handed to the owner).
- `_visible` CommonMark fence/comment edge cases (unclosed or mismatch-closed fences, 4-backtick, indented fences, comment-opener inside a fence) — probed and accepted in the header-fields review; all fail closed or are contrived for machine-written headers.
- The newest-audit rule is stricter than ADR-0005's letter (the ADR requires only the cited audit to pass; the validator requires citing the newest) — a justified tightening, pinned by `rv_newer_audit_wins`; record it in the ADR's Known limits if the letter is ever re-read literally.
- Calibration dispatched through general-purpose fable agents following `card-auditor.md` (the agent type was not yet registered mid-session), and the sealed answers kept at an unguessable home-dir path rather than the scratchpad — both ledger rulings, disclosed; no report quotes the answers file.
- `python3` invocations in SKILL.md / templates / card-auditor.md versus the repo's `py -I` test convention — pre-existing cross-platform wording, unchanged by this branch.
- `rv_override_in_inline_comment_ignored` passes against the pre-fix code (documents behavior, does not pin the fix) — recorded with that caveat in the header-fields review and the session log.
- The audit report's `Reviewer:` field is not validated — deliberate; forgery is outside the ADR-0004/0005 threat model.
- BDD's 34 pre-existing blueprint warnings and the calibration reports' placeholder all-zero SHA — out of this branch's scope / documented calibration artifacts.
- Two spaces after `**Signed off:**` in the pilot card — normalized by `HEADER_FIELD_RE`; not a defect.

## Recommendations

- Fix Important #1 with its two regression tests, then re-run the three suites; it is a small, local change to `checklist_rows`.
- Commit `bin/test_lean_check.py` with this review staged as its ADR-0002 receipt (the ledger held it back for exactly this).
- Add the one-line SKILL.md continuation for the non-formalizer glossary-disagreement outcomes (Minor #2) next time the file is touched.
- At the five-node review point, count the pilot's blanket marking (Minor #5) as "owner guided", not "owner compared per row".

## Assessment

**Ready to merge?** Yes — the range is already on `main` and holds up; commit the pending test. Schedule the Important #1 parser fix before the next `/theory formalize`.

**Reasoning:** The implementation matches the plan and ADR-0005 on every checked interface, the review loops demonstrably bit (mutation-confirmed tests, two Criticals fixed RED→GREEN), and the pilot replay proves the end-to-end contract. The one residual defect is a narrower survivor of an already-identified bypass class in the new checklist parser — real, deterministic, and cheap to fix, but requiring two coinciding owner mistakes to cause harm.
