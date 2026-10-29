---
name: theory
description: |
  Rigorous theory development on a blueprint (ADR-0004). Breaks a model into
  small nodes (definitions, assumptions, claims, variants), runs each claim
  through prove-or-refute with examples and counterexample search first,
  checks proofs with two blind proof-verifiers, and reviews the paper against
  the blueprint. Lean lane (phase 2): formalize a checked node's statement for
  the owner to audit on a fidelity card, then prove it and kernel-check it.
  Modes: explore, node, variants, verify, formalize, prove, status, review, develop.
argument-hint: "[explore <question or .tex> | node <label> | variants <label> | verify <label> [--model fable|opus] | formalize <label> | prove <label> | status | review [file] | develop]"
allowed-tools: Read,Grep,Glob,Write,Edit,Bash,Task
---

# Theory

Develop and check economic theory one small step at a time. The working record is the project's **blueprint**, `theory/blueprint/`: one node file per definition, assumption, claim or variant, with an immutable statement, a status, and an append-only evidence log. The node format is in `templates/theory/blueprint-node.md`. The validator is `python3 bin/blueprint_check.py theory/blueprint`.

**Input:** `$ARGUMENTS`, a mode keyword followed by its argument.

**Agents:** `theorist` (worker; may raise a node only as far as `proved`), `proof-verifier` (blind critic; two per node), `theorist-critic` (paper-level critic), `formalizer` (Lean worker; never sets a status), `card-auditor` (blind critic of a Lean card; ADR-0005).

**Status ladder:** `conjecture → survived-search → proved → checked → formalized → verified`, plus the terminal statuses `refuted`, `conditional`, `superseded`. `checked` needs two blind verifier PASSes. `formalized` and `verified` rest on the owner's bound signature (ADR-0005). The signature is the approval, so Claude appends the line and tells the owner; nobody asks again:
- `formalized` = a card signed `<initials> <date> sha:<12 hex>`, every checklist row marked, an independent audit (coverage PASS, verdict agreeing or overridden by the owner), plus a statements-mode `lean_check` PASS;
- `verified` = the same card plus a full `lean_check` PASS on the same statement hash.

---

## Modes

### `/theory explore <question | path to .tex>`

Turn a research question, or an existing theory section, into nodes.

1. If `theory/blueprint/` does not exist, create it and `theory/blueprint/checks/`.
2. Dispatch **theorist** with the question or file. It:
   - creates `definition` and `assumption` nodes (`stated`) for the primitives;
   - creates a `claim` node for each candidate result, at `conjecture`. Existing results from a paper also enter at `conjecture`, whatever earlier reviews said, and their `paper_ref` points at the paper;
   - writes first example checks under `checks/`.
3. Run **status** (below) and show the table.

### `/theory node <label>`

One prove-or-refute pass on one claim or variant node. Dispatch **theorist** with the label. It decides whether the statement holds and, if not, finds a counterexample and the weakest repair. The order is examples, then counterexample search, then exact sub-claim checks, then a proof attempt. It records each status change it makes (at most up to `proved`), and finishes by running the validator. Report the node's new status and the validator verdict.

**Rewriting the proof of a node at `proved` or `checked`** (a review finding, or a step to make self-contained) takes three log lines, then `verify`:
1. `<status> -> survived-search | theorist | <the review or note that prompted the rewrite> | stmt:<hash>`.
2. Rewrite the proof, then `survived-search -> proved | theorist | | stmt:<hash> proof:<new hash>`.
3. Run `verify`; two PASSes give `proved -> checked` with the new hash.

Do not move `checked -> proved`: a `-> checked` line is compared with the hash of the last *upward* move to `proved`, so the new reports are refused. Until step 3, the validator fails on every `checked` node that uses this one, so finish in one sitting. For a node at `formalized` or above, ask the owner first.

### `/theory variants <label>`

Dispatch **theorist** to create one `variant` node for each assumption in the node's `uses` (drop, weaken, or swap it), and run each through a prove-or-refute pass. Summarize which assumptions the result needs (it collapses without them) and which are superfluous (it survives without them).

### `/theory verify <label> [--model fable|opus]`

Blind two-verifier check of a node at `proved`. **You** (the dispatcher) build the blind input, so the verifiers never open the node file:

1. Build the input with `python3 bin/blueprint_tools.py verify-input theory/blueprint/<label with ':' replaced by '-'>.md`. It refuses (exit 1, reasons listed) unless:
   - the node is at `proved`, with no `[GAP:` marker;
   - every claim, variant or imported node in its `uses` is `checked` or above, and every definition and assumption is `stated`;
   - the validator reports no error on the node or on anything it rests on;
   - every node label its statement or proof cites is in `uses` or declared as a mention;
   - the proof never points into another node's proof (proof-verifier item 11).
     - Refused: "Step 2 of lem:x", "the base case of lem:x", "the proof (or argument) of lem:x" and "lem:x's proof".
     - Allowed: "part 1 of lem:x", which names a part of the statement.
     - A pronoun ("its Step 2") is not caught, so the verifiers' item 11 still applies.
     - A remark that only contrasts with another proof goes in an HTML comment.

   On a refusal, stop, report the reasons, and point to `develop`: a node cannot be `checked` on unchecked foundations. (If verifier reports already exist for the current proof hash, they stay valid; append the `-> checked` line once the dependencies are checked.)
2. The input it prints is the whole of what the verifiers see:
   - the `## Statement`;
   - the `## Proof`;
   - for each label in `uses`, that node's kind and `## Statement`;
   - the statements of the definitions and assumptions those used results rest on;
   - under "context only", the statements of any other node these texts name; they are not premises;
   - the `**Target:**` and `**Proof:**` lines each verifier copies into its report header.

   HTML comments are stripped. Add nothing to it: not the evidence log, `paper_ref`, the paper, or any other verdict.
3. Dispatch **two** `proof-verifier` agents **in parallel** (one message, two Task calls), each a fresh agent with the same input. Pass `model` from `--model` (default `fable`), and give each a distinct run suffix (`-a`, `-b`) for its report filename. Neither agent is told about the other.
4. Read the two `VERDICT:` lines.
   - **Both PASS:** append to the node's evidence log
     `- YYYY-MM-DD | proved -> checked | proof-verifier | <report-a>;<report-b> | stmt:<stmt hash> proof:<proof hash>`
     and set `status: checked`.
   - **Any FAIL:** append `- YYYY-MM-DD | proved -> survived-search | proof-verifier | <failing report> | stmt:<stmt hash>`, set `status: survived-search`, and hand the failing report to the theorist on the next `node` pass.
   - **Split, or any UNVERIFIED:** dispatch a third verifier with the same input. If it still isn't two PASSes, leave the status unchanged and ask the user.
   
   Get both hashes with `python3 bin/blueprint_check.py --hashes <node file>`.
5. Run the validator. A FAIL here means the log edit was wrong: fix the log line, not the rule.

For the fable-versus-opus comparison (ADR-0003/0004 experiment), run `verify` once with each model on the same node, and record the verdicts and findings by severity in the session log.

### `/theory formalize <label>` (Lean lane, stage 1: statement first)

Needs the node at `checked`, the project's Lean path in `.claude/state/lean.toml`, and `templates/theory/lean-layout.md` followed. The owner does not read Lean, so this stage produces something the owner can audit in English.

1. **Dispatch `formalizer`** with `stage: formalize` and the label. It writes:
   - the self-contained statement file and its companion statements;
   - `sorry` proofs;
   - the node's `lean:` header;
   - a draft card at `theory/blueprint/cards/<node>.md` (the header hashes, Appendix A–D and the formalizer column of the worked instance).
2. **Run `python3 bin/lean_check.py <node> --statements-only`.** Every check must pass (the card exists with its hashes and statement list; it is still unsigned, and signing is the validator's check). On any other FAIL, send it back to the formalizer (at most twice in total), then stop and report.
3. **Blind back-translation, which writes the checklist.** Dispatch a fresh general-purpose agent with `model: fable`, giving it only the text of the statement file with comments and docstrings stripped. Withhold the paper, the node, the card and every glossary. Ask it for:
   - **checklist rows:** one per top-level hypothesis and per top-level conjunct of each `_stmt`, as `| Part | # | Lean clause (verbatim) | reading | PENDING |`, with the reading in plain mathematics using the Lean names;
   - **its own glossary** of every Lean name and Mathlib symbol it relied on;
   - **notes:** anything vacuous or odd.

   Paste the glossary and the notes into Appendix E word for word.
4. **Independent audit, step 1.** Dispatch `card-auditor` (blind) with:
   - the node label (e.g. `prop:nstar-interior-ac`) and the Lean name from the node's `lean:` header, both copied exactly, because its report header must match them;
   - the node's `## Statement`;
   - the statement file's path;
   - the parameters of each sanity companion;
   - the Statement SHA-256 (64 hex, from `lean_check --hash`);
   - the report path `theory/blueprint/checks/<node file stem>/card_audit_<YYYY-MM-DD>.md`. For a second audit on the same day, use `_2`, then `_3`; never `_1`. An earlier audit is never edited.

   Keep its verdict, and the report's path, from the owner until the owner has signed (step 8).
5. **Compare the three glossaries:** the formalizer's (Appendix A), the back-translator's (Appendix E) and the auditor's (in its report).
   - **If they agree,** rewrite each checklist reading in the paper's symbols, substituting symbol for symbol and changing nothing else, and paste the table into the card's checklist.
   - **If they disagree,** show the owner the disagreement before the checklist. The owner decides which reading is right. If it is the formalizer's that is wrong, the formalizer fixes the statement, and the card restarts at step 1 with a new Statement SHA-256.

   Put the auditor's paper values next to the formalizer's in the worked instance. Fill the "Lean companion says" column from the sanity companions in the statement file. Leave `Independent audit:` at `PENDING` for now.
6. **Independent audit, step 2 (coverage).** Send the same auditor the checklist table. If it reports `Coverage: FAIL`, re-run the back-translator on the missing clauses (at most twice in all), then repeat this step. If it still fails, stop and report.
7. **Hand the card to the owner.** Name the file. The owner:
   - marks every checklist row (`same`, `weaker`, `stronger`, `added`, or a `missing` row of their own);
   - checks the worked instance;
   - writes the notes;
   - sets `Verdict`, and `Signed off` as `<initials> <date> sha:<first 12 of Statement SHA-256>`.

   Never fill these in, never suggest marks, and never write `Signed off`, `Verdict` or `Audit override`. A walk-through that translates a row the owner asks about is fine; record that it happened in the notes.
8. **Once the owner has signed,** write the audit report's path into `Independent audit:` and compare the owner's verdict with the auditor's.
   - **If they agree** (both FAITHFUL / WITH-NOTED-DIFFERENCES), go to step 9.
   - **If they disagree,** stop. Show the owner the auditor's map. The owner either:
     - **accepts the auditor's finding:** the formalizer fixes the statement, and the card restarts at step 1. The old signature no longer matches;
     - **overrides it:** the owner writes an `Audit override:` line in the header block, right under `Signed off` (the validator reads only the header), with a reason. Then go to step 9.

     Either way, record the outcome in the owner's notes.
9. **Run `python3 bin/lean_check.py <node> --statements-only --write-report`.** On PASS, append the line below and tell the owner it is done:

   `- YYYY-MM-DD | checked -> formalized | user | theory/blueprint/cards/<node>.md;<report> | stmt:<stmt hash>`

   Then run the validator. A FAIL here names the card rule that is not met; fix that, never the rule.

### `/theory prove <label>` (Lean lane, stage 2)

Needs the node at `formalized`, and comparator set up in `.claude/state/lean.toml` (`templates/theory/lean-layout.md`). `lean_check` hands the soundness judgment to comparator.

1. **Dispatch `formalizer`** with `stage: prove`. It replaces the `sorry`s and must not touch the statement file.
2. **Run `python3 bin/lean_check.py <node> --write-report` yourself** (full mode; not the formalizer) and report every check line.
3. **On PASS**, append the line below and tell the owner (the bound signature is the approval; ADR-0005):

   `- YYYY-MM-DD | formalized -> verified | user | theory/blueprint/cards/<node>.md;<report> | stmt:<stmt hash>`

   Then run the validator.
4. **On FAIL, or after two formalizer dispatches with parts still open,** report the open goals. A part shown false sends the prose claim back to the theorist; the owner decides.

A later toolchain or Mathlib bump means re-running `lean_check` on every `verified` node. A new failing report takes the node's verification away (the validator checks the newest full report).

### `/theory status`

Run `python3 bin/blueprint_check.py theory/blueprint --write-status`. Show the verdict line, any errors and warnings, and the status table from `theory/blueprint/STATUS.md`.

**Fingerprint sweep (advisory, ADR-0005).** The Lean project sits outside the repository, so the validator cannot see the statement file. When `.claude/state/lean.toml` names the project, run `python3 bin/lean_check.py <node> --hash` for every `formalized` or `verified` node and compare the result with its card's `Statement SHA-256`. Report a mismatch as **stale**: the statement changed after it was signed, and the next full check will FAIL. A mismatch is never fixed by editing the card: the owner re-signs after a new audit.

A warning that a node "uses superseded node X" or "uses conditional node X" means its dependents were not moved to the successor. Run `python3 bin/blueprint_tools.py repoint theory/blueprint/<X>.md`, show the dry run, then apply it with `--apply` (the same authority as the theorist's own down-moves; the dry run goes in the report). Re-proving the demoted nodes is a `node` pass.

### `/theory review [file]`

First run **status** so `theory/blueprint/STATUS.md` is current. Then dispatch **theorist-critic** on the paper's theory section (default: the `.tex` that the most nodes' `paper_ref`s point to). Besides its 16-item checklist and architecture checks, it cross-checks every result in the paper against the blueprint.

Flags (narrow the critic's focus):
- `--proofs`: proof presentation (proof correctness is carried by the blueprint, not this review);
- `--assumptions`: independence, necessity, non-vacuity, boundary examples;
- `--predictions`: whether predictions follow from `checked` nodes and are testable.

### `/theory develop`

Loop over the open claim and variant nodes in dependency order (a node's `uses` first):

1. `node <label>` until the node is `proved`, `refuted`, `conditional`, or the theorist reports no confident proof;
2. `variants <label>` once per claim node;
3. `verify <label>` for each `proved` node.

Stop and ask the user whenever a decision is theirs: a modeling choice (which assumption to keep, how to repair a refuted claim), a split verifier verdict, or anything a node's evidence can't settle. Never loop on one node more than three passes without reporting.

---

## Principles

- **Prove or refute.** No instruction to an agent is ever "prove X". Refuted, conditional and "no confident proof" are real results.
- **Statements are immutable.** A reworded statement is a new node; the validator detects edits by hash.
- **Explore before proving.** Examples and counterexample search first. A search that finds nothing is evidence, not proof.
- **Vary the assumptions.** The variant step shows which assumptions do the identifying work.
- **Verification is blind and doubled.** Two fresh verifiers who never see the paper or the motivation.
- **Simplest version first.** Two agents, two goods, linear utility: if the idea fails there, it fails in general.
- **Theorems are English takeaways that are also mathematically true**, and the paper states only what the blueprint has checked.
- **Predictions feed design.** Testable predictions cite the node labels they rest on.
