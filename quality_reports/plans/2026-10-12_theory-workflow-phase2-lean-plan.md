# Theory Workflow — Phase 2 (Lean lane) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** APPROVED 2026-10-12 (v2; owner chose decision (A) and kept the calibration task), revised after blind fit-for-purpose (58/100) and efficiency (64/100) reviews (`quality_reports/reviews/2026-10-12_theory-phase2-plan_{fit-for-purpose,efficiency}_review.md`); for the owner's approval.

**Goal:** Let a `checked` blueprint node climb to `formalized` (the owner has signed a fidelity card for a frozen Lean statement) and `verified` (the Lean proof of exactly that statement is kernel-checked with clean axioms), and pilot this on BDD's optimal-sample-size result.

**Who audits:** the owner, an economist who does not read Lean. The design therefore makes the card something the owner *fills in and checks*, not something they read and initial:
- the owner signs **before** any proof exists;
- an independent channel writes its own translation;
- the owner calibrates on toy cards first;
- the first real card is small.

**Architecture:** One Lean project per theory project, outside OneDrive, at the path in the project's gitignored `.claude/state/lean.toml`. Each node has its own self-contained statement file `<Pkg>/Statements/<Name>.lean`, and the **whole file** is hashed. Formalization has two stages:
1. **formalize:** statement and companion *statements*, with proofs left as `sorry`; then the card; the owner signs; `formalized`.
2. **prove:** proofs; then `lean_check`; the owner approves; `verified`.

`bin/lean_check.py` (stdlib only) checks the hash, scans for unsafe tokens, builds with `--wfail`, generates a check file that re-states every audited declaration against its statement and prints its axioms, runs `leanchecker`, and writes a dated report. The validator ties `formalized` to a signed card plus a statements-only report, and `verified` to the card plus a full PASS report with the same hash.

**Tech Stack:** Python 3 stdlib (`tomllib`, `subprocess`, `hashlib`); Lean v4.35.0-rc4 + Mathlib v4.35.0-rc4 via elan 4.2.4 (spike, session log 2026-10-11 §8); `lean-lsp-mcp` 0.31.0 (registered at user scope as `lean-lsp`).

**Spec:** `quality_reports/specs/2026-10-11_theory-proof-workflow-spec.md` §4 (APPROVED), acceptance #7–#8; ADR-0004.

## Amendment 2026-10-12: soundness via Lean FRO comparator

Two ADR-0002 review rounds broke the text-level soundness checks of Tasks 1–2: the check file did not import the statements, macros were allowed, and checks were module-scoped (round 1); then `srcDir`, `lakefile.lean` and namespace shadowing (round 2). The owner chose a spike of Lean FRO's `comparator`, and it passed on Windows: session log 2026-10-11 §9.

`lean_check` therefore delegates soundness to comparator. In full mode it generates `LeanCheck/<Name>Challenge.lean` (the signed statements as `sorry` theorems), `<Name>Solution.lean` (the proofs) and a comparator config, then runs comparator. The generated check file, the `#print axioms` parsing and the `leanchecker` step are gone.

`lean_check` keeps everything else: the hash, the card, the statement-file readability rules and the dated reports. It adds a canonical `lakefile.toml` (two libraries, `<Pkg>` and `LeanCheck`; no `lakefile.lean`), a cleaned project `.lake/build` before each run, and a project scan for code-executing commands, because the Windows build is unsandboxed.

The **threat model** is now stated: this catches Lean-level mistakes and tricks in sources and lakefile, not an actor with shell access. Tool paths go in `.claude/state/lean.toml` (`comparator`, `lean4export`, `landrun`). The Interfaces below that mention the check file, `#print axioms` or `leanchecker` are superseded by this amendment and by `templates/theory/lean-layout.md`.

## Global Constraints

- The phase-1 constraints carry over:
  - cross-platform `pathlib`; `utf-8-sig` in, `utf-8` out;
  - stdlib-only `bin/`; no hooks; model aliases only;
  - plain `check()` tests;
  - ADR-0002 review before committing `bin/`;
  - commit messages via `-F <file>`.
- **No machine paths in tracked files.** The Lean project path comes from `--project DIR` or `.claude/state/lean.toml` (gitignored in both repos). `lake`/`lean`/`leanchecker` are found on PATH, then at `~/.elan/bin` (the Git Bash PATH here lacks it).
- **Statement files are self-contained:**
  - they import only `Mathlib`;
  - they may hold only `def`s, `structure`s and the `<name>_stmt : Prop` defs, all inside the file;
  - they may not use `variable`, `notation`, `macro`, `elab`, `open … in` tricks, `set_option` beyond the header linter, or `import Lean`.
  - The **statement hash** is the SHA-256 (64 hex) of the whole file, normalized with the validator's `_normalize`.
  - `lean_check` enforces these restrictions.
- **Lean files use the module system** (`module`, `public import`, `public section`). The Lean project sets `autoImplicit = false` and `relaxedAutoImplicit = false`, which `lean_check` checks.
- **Only the owner sets `formalized` and `verified`.** Tools and agents prepare evidence and the exact log lines, and the owner approves each one.
- **Allowed axioms:** exactly {`propext`, `Classical.choice`, `Quot.sound`}, for every audited declaration: each part's theorem and each companion.
- **Forbidden tokens** (file-level scan of the Lean project's own sources, `.lake/` excluded): `sorry` (allowed only in the statements-only stage), `admit`, `axiom`, `native_decide`, `implemented_by`, `extern`, `unsafe`, `skipKernelTC`, `debug.skipKernelTC`. There is no whitelist: the exact-axiom rule makes one pointless.
- **Missing tools give UNVERIFIED, never PASS.** This covers `lake` absent, an unset or dangling project path, `leanchecker` absent, or a subprocess timeout. The toolchain and Mathlib revision are recorded in every report. Bumping either is a deliberate act that re-runs `lean_check` and produces a new report.
- Hosted Lean search tools are allowed (owner, 2026-10-11).

## Interfaces

- **Lean project layout** (package `<Pkg>`):
  - `<Pkg>/Statements/<Name>.lean`: one file per node; per-part defs `<name>_part_<x>_stmt : Prop`, plus companion statements.
  - `<Pkg>/Proofs/<Name>.lean`: `theorem <name>_part_<x> : <name>_part_<x>_stmt`, and the companion theorems.
  - `<Pkg>/Check/<Name>.lean`: generated by `lean_check`, never hand-edited.
- **Node header `lean:`** = `<Pkg>.<name>`. The parts and the companion names are listed on the card.
- **Companions, by naming convention:**
  - `<name>_nonvacuous` (a witness that the hypotheses hold);
  - `<name>_sanity_<k>` (concrete instances, including one that matches an existing numeric check file);
  - `<name>_false_variant` (the negation of a plausible wrong version);
  - a guard hypothesis for each junk-value operation (`/`, `deriv`, `sSup`/`sInf`, ℕ subtraction, `sqrt`/`log`, `tsum`), listed on the card.

  `lean_check` FAILs if a listed companion is missing.
- **Fidelity card:** `theory/blueprint/cards/<label-file>.md`.
  - Header: `**Node:**`, `**Node statement hash:**` (the prose `stmt:` hash), `**Lean:**`, `**Statement SHA-256:**`, `**Verdict:** FAITHFUL | WITH-NOTED-DIFFERENCES | UNFAITHFUL | PENDING`, `**Signed off:** <initials> <YYYY-MM-DD> | PENDING`.
  - Sections:
    - paper and Lean side by side;
    - a per-part map (paper part ↔ Lean part, each marked *equal / weaker / stronger*);
    - a types table (ℕ/ℝ, coercions);
    - the quantifier order in English;
    - the hypothesis ↔ assumption map, with Lean-only hypotheses flagged;
    - junk-value guards;
    - companions;
    - **a concrete instance the owner checks** against an existing numeric file;
    - the blind back-translation with its own glossary;
    - the owner's notes and sign-off.
  - The owner types the verdict and the sign-off.
- **lean_check reports** are dated and never overwritten: `theory/blueprint/checks/<label-file>/lean_check_<YYYY-MM-DD>[_<n>].md`. Header: `**Node:**`, `**Lean:**`, `**Statement SHA-256:**`, `**Mode:** statements | full`, `**Verdict:** PASS|FAIL|UNVERIFIED`, `**Toolchain:**`, `**Mathlib:**`, then one line per check.
- **`bin/lean_check.py <node file> [--project DIR] [--statements-only] [--no-leanchecker] [--write-report] [--timeout S]`**: exit 0 PASS, 1 FAIL, 3 UNVERIFIED, 2 usage. `--no-leanchecker` is for the inner loop and yields UNVERIFIED, never PASS.
- **Validator:**
  - `checked -> formalized` (actor `user`) needs:
    - the card, with a matching `Node`, a matching `Lean`, a verdict of FAITHFUL or WITH-NOTED-DIFFERENCES, and a sign-off;
    - a statements-mode report with PASS and the card's hash.
  - `formalized -> verified` (actor `user`) needs the card plus the newest full-mode report, with PASS and the same hash.
  - A node at `formalized` or above must have `lean:` set.

## Review Focus

1. **A helper definition edited after signing.** The whole-file hash changes, so `lean_check` FAILs and the validator rejects `verified`. → tests `lc_helper_def_edited_after_signing_fails`, `bc_verified_hash_mismatch_fails`.
2. **A proof of a different statement**, and a companion with hidden `sorryAx`. Both are caught by the generated check file and `#print axioms`, not by the text scan alone. → `lc_proof_of_other_statement_fails`, `lc_companion_hidden_sorryax_fails`.
3. **Tests silently skipped.** The integration tests must find `lake` through the `~/.elan/bin` fallback and run here. A skip must be reported loudly. → `lc_resolver_finds_elan_home`.
4. **Windows output.** Spaces in paths, CRLF, and non-ASCII (`σ`, `ℝ`) in build and axiom output. → `lc_crlf_hash_stable`, `lc_parses_unicode_output`.
5. **An outdated report.** The validator uses the newest report for the node, and a report for another hash never counts. → `bc_newest_report_wins`.

---

### Task 0: Thin vertical slice, by hand (no new tooling)

- Rename `~/lean/spike` → `~/lean/bdd`. It is already a Mathlib project and holds no commits.
- Set `autoImplicit = false` and init git.
- By hand, write `Statements/NstarOpt.lean` for parts (a)–(c) of `prop:nstar-interior`, a `sorry` proof, and a hand-written `Check/` file.
- Run `lake build --wfail` (expect it to fail on `sorry`), `lake env lean Check/…`, and `leanchecker`, and time each step.
- Confirm that `lean-lsp-mcp` finds the project from a file path, with no project env needed. If it doesn't, set `LEAN_PROJECT_PATH` per project.

The output feeds Tasks 1–2: measured timings, the exact `#print axioms` output format, and any surprises. No commit to the workflow repo.

### Task 1: `lean_check` core (fakes, no Lean)

**Files:** `bin/lean_check.py`, `bin/test_lean_check.py`.

Covers:
- the toolchain resolver;
- config resolution;
- the whole-file hash;
- the statement-file restrictions;
- the file-level token scan;
- the companion convention;
- verdict assembly in statements and full modes;
- the dated report;
- timeouts.

The axiom-output parsing follows `lean-lsp-mcp`'s verifier: I read its source rather than vendor it.

### Task 2: Real runner and fixture (acceptance #7)

**Files:** extend the above; `bin/fixtures/lean_check/` is a Lean-core-only project pinned to the installed toolchain, so tests never download anything.

Integration cases:
- PASS on a clean proof;
- FAIL on `sorry`, hidden `sorryAx`, an extra `axiom`, a proof of a different statement, a missing companion, and a helper edited after signing.

### Task 3: Validator rules

**Files:** `bin/blueprint_check.py`, `bin/test_blueprint_check.py`.

Implements the Interfaces rules. Tests cover:
- a `PENDING` card, an UNFAITHFUL card, and a card for another node;
- a missing statements-mode report;
- an old report followed by a new FAIL;
- a hash mismatch;
- a missing `lean:`.

### Task 4: ADR-0002 review and commit of `bin/`

One red-team + correctness round on fable. A second round only if a fix changes the design.

### Task 5: Formalizer, card template and layout doc

**Files:** `.claude/agents/formalizer.md` (`model: opus`; Read/Write/Edit/Bash/Grep/Glob plus the `lean-lsp` MCP tools), `templates/theory/fidelity-card.md`, `templates/theory/lean-layout.md` (file headers, naming, the module-system boilerplate, `lean.toml` example), and `templates/theory/blueprint-node.md` (the `lean:` key and the new rules).

The formalizer works **statement first**:
- In **formalize** it writes the statement file, the companion statements with `sorry` proofs, and the card draft, with sign-off `PENDING`.
- In **prove** it writes the proofs and must not touch the statement file. If the statement turns out false or unprovable as written, it says so, and never weakens it silently.

Run `bin/agent_lint.py`.

### Task 6: `/theory formalize` and `/theory prove`

**Files:** `.claude/skills/theory/SKILL.md`.

**`formalize <label>`** (node at `checked`):
1. formalizer stage 1;
2. `lean_check --statements-only`;
3. a **blind back-translation**: an inline general-purpose dispatch on fable that sees only the statement file and writes its own glossary; the dispatcher pastes it into the card;
4. the owner fills in the per-part map, checks the concrete instance, and writes the verdict and sign-off;
5. on approval, the `checked -> formalized` line.

**`prove <label>`** (node at `formalized`): formalizer stage 2, then `lean_check --write-report`, then the `formalized -> verified` line on the owner's approval.

**Budgets:** at most 2 formalizer dispatches per stage; a glossary of about 15 symbols; a full `lean_check` within about 10 min. Over budget, it stops and reports.

### Task 7: Auditor calibration (spec acceptance #8 anchor)

Three short toy cards built from the spike's lemmas, one or two with a planted misformalization: `deriv` used for `HasDerivAt`, a dropped `0 < c`, `≤` for `<`, ℕ for ℝ, or a missing part. The answers are sealed in the scratchpad.

The owner reads the cards before the pilot card (about 20–30 min). Their result (caught or missed, and time taken) goes in the read-out.

### Task 8: BDD pilot setup

In BDD, write `.claude/state/lean.toml` and install `bin/lean_check.py` plus the updated `bin/blueprint_check.py` and `bin/blueprint_tools.py`.

**Back up the Lean project** (the owner's side note, 2026-10-12): the folder is outside OneDrive with local git only, on a temporary laptop. Give it a private remote on the owner's GitHub, created by the owner, then give it the same personal-repo guard setup as BDD, and push after each verified node. A verified node can be re-checked only while its Lean files exist.

The pilot's success test is "the validator reports no error, and no warning on the pilot node". The ~32 mention warnings elsewhere remain the separate TODO item and are not on this path.

### Task 9: Pilot

- First `formalize`, then `prove`, on parts (a)–(c) (see the decision below).
- Parts (d)–(e) follow only if (a)–(c) reached `verified` within budget.
- Part (d)'s "continuously differentiable" is stated as `ContDiffOn ℝ 1` on the open set, plus `HasDerivAt` for each stated partial. Per-coordinate derivatives alone would be weaker than the paper.

### Task 10: Read-out, guide and docs

- **Session-log read-out:** cost per stage, owner reading time, the calibration result, what the companions, back-translation and concrete instance caught, and acceptance #7 and #8 status.
- **Then** `.claude/references/reading-lean-statements.md`, written from the owner's actual questions and citing official Lean and Mathlib documentation, with the pilot card as the worked example.
- **Then** docs: `.claude/rules/agents.md`, `CLAUDE.md`, `CHANGELOG.md`. Overlay copies wait for the full Class A sync (Track A step 3).

## Decision for the owner (before Task 9): DECIDED (A), 2026-10-12

How to make the first card small: **(A)** a new node `prop:nstar-interior-ac` stating parts (a)–(c) word for word, which both reviews recommend. It needs a theorist pass reusing the existing proof's Steps 0–3, plus two blind verifier runs, before it reaches `checked`. **(B)** Keep the one node and formalize it part by part: separate Lean statements for each part, with (a)–(c) first. The node climbs only when all five parts are signed and proved. (B) saves the verifier runs but leaves the node at `checked` until (d)–(e) are done.

## Spec coverage

| Spec §4 item | Task |
|---|---|
| Setup spike | done; Task 0 extends it |
| Layout and machine-local path | 0, 1, 5, 8 |
| `formalizer` and companions | 1, 2, 5 |
| Card, back-translation, owner-only sign-off | 3, 5, 6, 7 |
| `lean_check` PASS/UNVERIFIED/FAIL | 1, 2 |
| `verified` = PASS + signed card, same hash | 3 |
| Auditor guide | 10 |
| Acceptance #7 / #8 | 2 / 7, 9 |

## Changes from v1 (review findings)

| Change | Finding |
|---|---|
| Two stages; signing before proving | fit #2; efficiency #1 |
| Whole-file hash and self-contained statement files | fit #1 (Critical); efficiency #5 |
| Blind back-translation, Lean-only, with its own glossary, as an inline dispatch | fit #3; efficiency #10 |
| Auditor calibration task | fit #4 |
| Companions under `#print axioms`, by naming convention | fit #5 |
| Small first card; `ContDiffOn` for (d); the owner decides the split | fit #6; efficiency #2 |
| Thin vertical slice first, reusing the spike project | efficiency #3, #7 |
| Toolchain resolver, so integration tests really run | efficiency #4 |
| Dated append-only reports; statements-only report at `formalized` | fit #7 |
| Toolchain/Mathlib recorded; bump policy | fit #8 |
| Longer token list, no whitelist, leanchecker required | fit #9, #16; efficiency #6 |
| Card sections: per-part map, types, quantifiers, concrete instance | fit #10 |
| `autoImplicit = false` | fit #11 |
| Timeouts → UNVERIFIED | fit #13 |
| Fixture pinned; one layout doc instead of four templates | fit #14; efficiency #11 |
| Guide after the pilot, from the owner's questions | efficiency #8 |
| Mentions pass off the pilot's path | efficiency #9 |
| Overlay copies deferred to Track A | efficiency #12 |
| Budgets and stop rules | efficiency #2, #14 |

Not adopted: dropping the validator's `Lean` cross-check (efficiency #13). It is cheap and catches a card filed against the wrong declaration.
