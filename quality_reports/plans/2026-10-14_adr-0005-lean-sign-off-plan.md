# ADR-0005 Lean sign-off — Implementation Plan

**Status:** DRAFT (awaiting owner approval)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the owner's bound signature the only approval for `formalized` / `verified`, lead each card with a marked checklist, and require an independent card audit. All of this is checked by `bin/blueprint_check.py`.

**Architecture:**
- The validator gains three checks in `_card_problem`:
  - the bound signature;
  - the checklist marks;
  - the audit report.

  It keeps replaying every past `formalized` / `verified` line against the current card.
- The card template moves the checklist up to sit right after the header, and keeps the header fields in the first 60 lines.
- `/theory formalize` gains a blind back-translator that writes the checklist, a two-step `card-auditor`, and a glossary diff. `/theory status` gains an advisory `lean_check --hash` sweep.
- The pilot is converted last.

**Tech Stack:**
- Python 3 standard library, run as `py -I`. The tests are plain scripts with `check()`, not pytest.
- Markdown agents and skills.
- Lean only through the existing `bin/lean_check.py`.

**Spec:** `decisions/0005_lean-sign-off-checklist-and-independent-audit.md` (Decided 2026-10-14). Also read ADR-0004 and the reviews named in ADR-0005's Sources.

## Global Constraints

- The signature format is exactly `<initials> <YYYY-MM-DD> sha:<12 hex>`. The prefix is the first 12 hex characters of the card's `Statement SHA-256`. No date ordering is checked.
- Marks are exactly `same`, `missing`, `added`, `weaker` and `stronger`, case-insensitive.
- The audit report lives at `theory/blueprint/checks/<node file stem>/card_audit_<YYYY-MM-DD>[_k].md`. Its header fields are `Node`, `Lean`, `Statement SHA-256`, `Verdict` and `Coverage`, with Coverage ∈ {PASS, FAIL}.
- `Audit override:` is `<initials> <YYYY-MM-DD> sha:<12 hex>: <reason>`. It never overrides `Coverage: FAIL`.
- No agent or Claude session writes `Verdict`, `Signed off` or `Audit override`. Claude writes `Independent audit:`, which is a locator.
- `bin/lean_check.py` is not modified.
- `bin/**` changes need an ADR-0002 receipt: red-team + correctness reviews on `fable`, staged with the commit.
- The validator verdict vocabulary is PASS / UNVERIFIED / FAIL. Every new rule reports an error naming the node and the fix.
- No employer or client names in any file. The workflow repository is personal.

## Review Focus

1. **A card in the old format** (the pilot before Task 4): the validator FAILs with a message that says to re-sign in the form `sha:<12 hex>` and to add an audit, not with a cryptic regex error. Test: `ln_old_format_card_message` (Task 1).
2. **An upper-case hex prefix, or extra spaces in `Signed off`:** an upper-case prefix is accepted (compared case-insensitively), and runs of spaces are accepted. Test: `ln_signed_prefix_case_and_spaces` (Task 1).
3. **A checklist row with an empty or misspelt mark:** FAIL naming the part and line number. Test: `ln_checklist_bad_mark_named` (Task 1).
4. **An audit locator for another node, or outside the node's `checks/` folder:** FAIL. Test: `ln_audit_wrong_place` (Task 1).
5. **A card saved with CRLF line endings or a BOM** (Windows editors): the checklist parses the same. Test: `ln_checklist_crlf_bom` (Task 1).

---

### Task 1: Validator rules for the bound signature, checklist and audit

**Files:**
- Modify: `bin/blueprint_check.py`:
  - `SIGNED_OFF_RE` (:341);
  - `_card_problem` (:358-373);
  - its call at :607, inside `_check_node` (:481);
  - new helpers next to `header_fields`.
- Test: `bin/test_blueprint_check.py`:
  - `write_card` (:210);
  - a new `write_card_audit`;
  - new checks in `test_phase2_lean_rules`.
- Review: `quality_reports/reviews/2026-10-14_adr0005-validator_{red-team,correctness}_review.md`

**Interfaces:**
- Produces:
  - `SIGNED_OFF_RE = re.compile(r"^[A-Za-z][A-Za-z.\-]{0,9}\s+\d{4}-\d{2}-\d{2}\s+sha:([0-9a-fA-F]{12})$")`
  - `OVERRIDE_RE = re.compile(r"^[A-Za-z][A-Za-z.\-]{0,9}\s+\d{4}-\d{2}-\d{2}\s+sha:([0-9a-fA-F]{12}):\s+\S.*$")`
  - `CARD_AUDIT_RE = re.compile(r"card_audit_\d{4}-\d{2}-\d{2}(?:_([2-9]|[1-9]\d+))?\.md$")`
  - `MARKS = ("same", "missing", "added", "weaker", "stronger")`
  - `checklist_problem(text: str) -> str | None`: finds `## Checklist` (a heading that starts with that word) and parses its table rows `| <part> | <n> | <Lean clause> | <reading> | <mark> |`. It returns None when there is at least one row and every mark is in `MARKS`. Otherwise it names the first bad row as `part (b) line 3`. The header row and the `|---|` row are skipped.
  - `_card_problem(f: dict, n: Node, card: Path, bp: Path, root: Path | None) -> str | None`. `root` is the one `_check_node` already has. Existing checks, then the following, in order:
    1. the signature and its prefix;
    2. `checklist_problem`;
    3. `Verdict: FAITHFUL` requires every mark to be `same`;
    4. `Independent audit:` resolves through the existing `resolve_locator(loc, root)` (:287) to a file in `bp/checks/<stem>/` whose name matches `CARD_AUDIT_RE`;
    5. the audit's `Node` / `Lean` / `Statement SHA-256` equal the card's;
    6. audit `Coverage` == `PASS`;
    7. audit `Verdict` in `SIGNED_VERDICTS`, or the card's `Audit override:` matches `OVERRIDE_RE` with a matching prefix.
  - The old-format message (Review Focus 1): when `Signed off` matches the old `initials date` form, say: "signed in the pre-ADR-0005 form; re-sign as `<initials> <date> sha:<first 12 of Statement SHA-256>` after the card is converted and audited".
- Consumes: `header_fields`, `SIGNED_VERDICTS`, `label_to_filename` (existing).

- [ ] **Step 1: Update the fixtures.**
  - `write_card` gains these parameters:
    - `signed="CS 2026-10-12 sha:" + LEAN_SHA[:12]`;
    - `checklist: str | None` (a default of two `same` rows for part (a));
    - `audit: str | None` (a locator; the default writes one with `write_card_audit`);
    - `override: str | None`.
  - `write_card_audit(root, label, sha=LEAN_SHA, verdict="FAITHFUL", coverage="PASS", node=None, lean=LEAN, stamp="2026-10-12", k=1) -> str` returns the locator.
  - Existing tests must still pass on the new defaults. The three `ln_signed_off_*` cases keep failing.
- [ ] **Step 2: Add the new checks at the end of `test_phase2_lean_rules`** (reusing its nested `node_at`, and `fails_naming` from :279), one `check` per behaviour, through `node_at("formalized", form=...)` unless stated:
  - `ln_signed_without_sha_rejected` (`CS 2026-10-12`);
  - `ln_signed_wrong_prefix_rejected` (`sha:cdcdcdcdcdcd`);
  - `ln_signed_prefix_case_and_spaces`: `CS  2026-10-12  sha:ABABABABABAB` → PASS;
  - `ln_old_format_card_message`: the error contains `re-sign`;
  - `ln_checklist_missing_rejected`;
  - `ln_checklist_bad_mark_named`: the error contains `line 2`;
  - `ln_checklist_crlf_bom` → PASS;
  - `ln_faithful_needs_all_same`: a `weaker` row with verdict FAITHFUL is rejected; the same card with WITH-NOTED-DIFFERENCES passes;
  - `ln_audit_missing_rejected`;
  - `ln_audit_wrong_place`: a locator under `checks/prop-b/`, or under `cards/`, is rejected;
  - `ln_audit_sha_mismatch_rejected`;
  - `ln_audit_coverage_fail_rejected`, also with a valid override;
  - `ln_audit_unfaithful_rejected`;
  - `ln_audit_unfaithful_with_override_passes`;
  - `ln_override_wrong_prefix_rejected`;
  - `ln_verified_replays_card_rules`: a `verified` node whose card lacks the audit FAILs.
- [ ] **Step 3: Run `py -I bin/test_blueprint_check.py`.** Expected: the new checks FAIL and the old ones pass.
- [ ] **Step 4: Implement the Interfaces block** in `bin/blueprint_check.py`.
- [ ] **Step 5: Run `py -I bin/test_blueprint_check.py` and `py -I bin/test_lean_check.py`.** Expected: all pass. The second confirms that `lean_check` is untouched.
- [ ] **Step 6: Run `/review-build bin/blueprint_check.py bin/test_blueprint_check.py`** (red-team + correctness, `fable`). Fix or accept each finding; a Critical gets a named regression test. Stage the reports.
- [ ] **Step 7: Commit** `bin/blueprint_check.py`, `bin/test_blueprint_check.py` and the two reviews.

### Task 2: Card template, formalizer and the `/theory` flow

**Files:**
- Modify:
  - `templates/theory/fidelity-card.md`;
  - `.claude/agents/formalizer.md` (Stage 1 steps 4–6, "What you never do");
  - `.claude/skills/theory/SKILL.md` (formalize steps 3–5, prove step 3, status, the status-ladder line at :23).
- Test: `bin/test_lean_check.py`, a new `test_card_template_readable`.

**Interfaces:**
- Consumes: `checklist_problem`, the field names and the formats from Task 1.
- Produces:
  - **The template layout.**
    - Header, in this order: `Node`, `Node statement hash`, `Lean`, `Statement SHA-256`, `Audited statements`, `Independent audit: PENDING`, `Verdict: PENDING`, `Signed off: PENDING`, with an optional `Audit override:`.
    - Then `## Checklist (owner marks)`, starting with the one-line direction reminder from ADR-0005 item 2 and a table with the columns `| Part | # | Lean clause (verbatim) | Reading (paper symbols) | Mark |`.
    - Then `## Worked instance` (formalizer and auditor values side by side, plus the owner's "agree?").
    - Then `## Owner's notes`.
    - Then `## Appendix`, holding A. Glossary (formalizer), B. Types, C. Hypotheses ↔ assumptions, D. Junk values and companions, and E. Back-translator glossary and notes.
    - The old sections 3 and 5, and the full back-translation, are removed.
    - A paper clause with no Lean line gets an owner-added row whose Lean column is `—`, marked `missing`.
- **The `/theory formalize` steps:**
  1. formalizer;
  2. `lean_check --statements-only`;
  3. **back-translator** (fresh `fable`, statement file only, comments stripped) returns checklist rows using the Lean names, its glossary and its notes;
  4. **`card-auditor` step 1** (Task 3);
  5. **diff the three glossaries:**
     - if they agree, substitute the paper symbols into the readings (symbols only) and paste the table;
     - if they disagree, show the owner the differences first;
  6. **`card-auditor` step 2** (coverage). On a FAIL, re-run the back-translator, at most twice in total, then stop;
  7. **the owner** marks every row, writes notes, and sets `Verdict` and `Signed off` with `sha:` copied from the header. The audit verdict is not shown until the owner has signed;
  8. **compare the verdicts:**
     - if they agree, run `lean_check --statements-only --write-report` and, on PASS, append the `formalized` line and tell the owner;
     - if they disagree, stop, and the owner decides (override or fix), recorded in Owner's notes.
- **`prove`:** after a full PASS, append the `verified` line and tell the owner. There is no ask.
- **`status`:** for each `formalized` / `verified` node whose Lean project is configured, run `py -I bin/lean_check.py <node> --hash` and compare the result with the card's `Statement SHA-256`. Report a mismatch as **stale (advisory)**.
- **The formalizer:**
  - reset `Independent audit`, `Verdict` and `Signed off` to `PENDING` on any header rewrite;
  - fill the formalizer column of the worked instance;
  - never write the sign-off fields or `Audit override`;
  - never "refresh" a `sha:` prefix.

- [ ] **Step 1: Write `test_card_template_readable` in `bin/test_lean_check.py`.**
  - Load `templates/theory/fidelity-card.md` and substitute the placeholders with sentinel values (`prop:zz-sentinel`, 64 × `a`).
  - Assert that `lean_check.card_fields` returns every header field, including `Independent audit`.
  - Assert that `blueprint_check.checklist_problem` on the template with its `PENDING` marks reports a bad mark (the template is not a signed card).
- [ ] **Step 2: Run `py -I bin/test_lean_check.py`.** Expected: FAIL (there is no `Independent audit` field yet).
- [ ] **Step 3: Rewrite the template and edit the formalizer and `SKILL.md`** as in the Interfaces block. Keep every other mode untouched.
- [ ] **Step 4: Run `py -I bin/test_lean_check.py` and `py -I bin/agent_lint.py .claude/agents`.** Expected: PASS.
- [ ] **Step 5: Commit** the template, the formalizer, the skill and the test. The docs get an advisory correctness review via `/review-build`, staged with the commit.

### Task 3: The `card-auditor` agent and its calibration

**Files:**
- Create:
  - `.claude/agents/card-auditor.md`;
  - after the run, `quality_reports/calibration/2026-10-14_card-auditor/{README.md,ANSWERS.md,case-1..7/}`.
- Scratch, until the run is done: `<scratchpad>/auditor-calibration/` (the cases) and `<scratchpad>/auditor-calibration-SEALED.md` (the answers). Neither is inside any repository.

**Interfaces:**
- Consumes: the audit header fields (Task 1) and the worked-instance column (Task 2).
- Produces:
  - **The agent's frontmatter:** `model: fable`; tools `Read, Write` only, so it cannot search for answers.
  - **Step 1 input:** the node's `## Statement` text, the statement file path, the sanity parameters, and the report path.
  - **Step 1 output:** a report with the header fields and `Coverage: PENDING`. The body holds:
    - its glossary;
    - a per-part map (equal / weaker / stronger / missing), each finding citing the Lean clause verbatim;
    - the paper-side values for each sanity triple;
    - the verdict.
  - **Step 2** (the same agent, by SendMessage): the checklist table. It sets `Coverage: PASS`, or FAIL listing every top-level hypothesis and conjunct with no row, and must not change step 1's verdict.

- [ ] **Step 1: Write the agent file.** Model its prompt on `.claude/agents/proof-verifier.md`: blind inputs, an adversarial default, evidence per finding, and the verdict vocabulary.
- [ ] **Step 2: Build the seven cases** in scratch:
  - six with one planted defect each: a dropped hypothesis, a weakened conclusion, an omitted conjunct, a mis-mapped symbol, a swapped quantifier order and a missing junk-value guard;
  - one faithful.

  Each case has a `node.md` (statement only) and a `Statement.lean` that compiles (`lean_run_code`). Record the answers in the sealed file.
- [ ] **Step 3: Run one fresh `card-auditor` dispatch per case** (step 1 only). Score each against the sealed answers. Expected: 6/6 defects caught with the defect named, and no false alarm on the faithful case.
- [ ] **Step 4: If it misses**, revise the prompt once, build seven fresh cases, and re-run. On a second failure, stop and report to the owner.
- [ ] **Step 5: Commit** the agent, the calibration folder (with ANSWERS.md, now unsealed) and a session-log read-out (catches, false alarms, tokens).

### Task 4: Convert, audit and re-sign the pilot

**Files:**
- BDD:
  - `theory/blueprint/cards/prop-nstar-interior-ac.md`;
  - `theory/blueprint/checks/prop-nstar-interior-ac/card_audit_<date>.md`;
  - `bin/blueprint_check.py` (copied from the workflow repository).
- Workflow repository: `TODO.md` and the session log.

**Interfaces:** Consumes Tasks 1–3.

- [ ] **Step 1: Copy `bin/blueprint_check.py` into BDD** and run the validator. Expected: FAIL on `prop:nstar-interior-ac` with the re-sign message from Review Focus 1. This proves the replay.
- [ ] **Step 2: Run the new formalize steps 3–6** (back-translator, auditor steps 1 and 2, glossary diff) on the unchanged statement file. Rewrite the card in the new layout, keeping the hashes and moving the old sections into the appendix. Expected: Coverage PASS.
- [ ] **Step 3: The owner marks the rows** and re-signs with the bound signature. The audit verdict is compared afterwards. Expected: they agree. If they don't, the node goes back to `checked` (ADR-0005 item 4) and the owner decides.
- [ ] **Step 4: Run the validator in BDD.** Expected: no errors for the node, and the same 34 pre-existing warnings. Then run `/theory status`. Expected: the `--hash` sweep reports the pilot as current.
- [ ] **Step 5: Commit in BDD** and in the workflow repository (TODO: replace the ADR item with the 5-node sunset review; the session-log read-out). Pushing is the owner's call.

---

**Execution note:** each task commits on `main` in its own repository, as earlier phases did. There are no branches.
