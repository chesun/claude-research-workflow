# Theory Workflow — Phase 1 (prose machinery) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** DRAFT — awaiting user review

**Goal:** Ship the blueprint, prove-or-refute exploration, and blind two-verifier checking on `main`, then pilot them on `belief_distortion_discrimination` (BDD) theory v2.

**Architecture:** Each theory claim is one Markdown node file with a small header and an append-only evidence log. A stdlib-only Python validator (`bin/blueprint_check.py`) enforces graph and status rules and returns PASS / UNVERIFIED / FAIL. Agents (`theorist`, the new `proof-verifier`, `theorist-critic`) and the `/theory` skill move to `main` and drive the node lifecycle. Lean is phase 2 and has its own plan.

**Tech Stack:** Python 3 stdlib (validator); Markdown agent and skill files; SymPy / Hypothesis / z3-solver / SciPy in the *pilot project's* venv only.

**Spec:** `quality_reports/specs/2026-10-11_theory-proof-workflow-spec.md` (APPROVED 2026-10-11)

## Global Constraints

- Cross-platform (Windows 11 + macOS): Python-first, `pathlib`, no bash-only idioms. Read files as `utf-8-sig`; write as `utf-8`.
- Validator is **stdlib only**: no PyYAML, no third-party imports.
- **No new hooks** of any kind (spec principle 7).
- Models by alias only: `theorist` and `proof-verifier` = `model: fable`, `effort: high`; `theorist-critic` = `model: fable`.
- Tests follow the repo's plain-Python `check(name, ok, detail)` style with `main() -> int` (see `.claude/hooks/test_review_receipt_check.py:30,75,291`). Run as `python3 <test file>`; exit 0 = all pass.
- **ADR-0002 gate:** every file under `bin/` needs an independent review receipt staged in `quality_reports/reviews/` before it can be committed. `bin/` tasks therefore don't commit until Task 4.
- No agent instruction may say "prove X" without a refute branch (spec acceptance #5).
- Creators never set `checked` or above; only the user sets `formalized`/`verified`.
- Commit messages containing apostrophes: use `git commit -F <file>`. A heredoc body trips a known destructive-guard false positive (TODO, 2026-10-11).

## Review Focus

1. **CRLF files.** This machine has `core.autocrlf=true`, so a node checked out with CRLF must hash identically to its LF form. → test `hash_crlf_stable` (Task 1).
2. **UTF-8 BOM and non-ASCII math.** Editors on Windows add a BOM, and statements contain `σ₀²` or `\sigma`. → test `parse_bom_and_unicode` (Task 1).
3. **Windows-hostile labels.** `:` is illegal in Windows filenames, so labels map to files by replacing `:` with `-`; a mismatch must be an error, not a silent skip. → test `filename_label_mismatch` (Task 1).
4. **Locator forms.** Backslash paths and `file.tex:249-255` line suffixes must resolve; absolute or out-of-repo paths give UNVERIFIED, never PASS. → tests `locator_backslash_and_linesuffix`, `locator_outside_repo_unverified` (Task 2).
5. **A statement edited after it was checked.** Silent drift is the core failure the blueprint exists to stop. → test `statement_changed_after_log` (Task 2).

---

### Task 0: ADR-0004

**Files:**
- Create: `decisions/0004_theory-workflow-blueprint-verifier-lean.md`
- Modify: `decisions/README.md` (Index table)

**Interfaces:** none (docs).

- [ ] **Step 1:** Write ADR-0004 in the template of `decisions/README.md`.
  - Header: Date 2026-10-11, Status Decided, Scope "Methodology / theory", Data quality Full context.
  - Decision bullets:
    - blueprint-first, with Lean as an opt-in lane;
    - `theorist`/`theorist-critic`/`/theory` move to `main`;
    - new blind `proof-verifier` with two-verifier aggregation;
    - model routing: theorist and verifier on `fable` with effort high, formalizer on `opus` (phase 2); the fable-vs-opus verifier comparison is part of the ADR-0003 experiment;
    - online lemma search allowed; Harmonic Aristotle not used.
  - Sources: the spec, the survey synthesis, the session log.
  - **No author-year citations** (the primary-source hook covers `decisions/`).
- [ ] **Step 2:** Add the index row `| [0004](0004_theory-workflow-blueprint-verifier-lean.md) | Theory workflow: blueprint, blind verifier, opt-in Lean | 2026-10-11 | Decided | Methodology / theory |`.
- [ ] **Step 3:** Commit `decisions/0004_*.md decisions/README.md` with the message `decisions(ADR-0004): theory workflow — blueprint, blind verifier, opt-in Lean`.

---

### Task 1: Node format and parser

**Files:**
- Create: `bin/blueprint_check.py` (parser part)
- Create: `bin/test_blueprint_check.py`
- Create: `templates/theory/blueprint-node.md` (an annotated example node, using the format below)

**Node file format** (decided here; the spec allows it). The statement lives in a body section, not the header, so multi-line math needs no YAML block parsing.

```
---
label: prop:nstar
kind: claim
status: proved
uses: [def:vstop, asm:normal-normal]
supersedes:
superseded_by:
lean:
paper_ref: theory/quadratic_loss_model_paper_v2.tex:249
---
## Statement
<text>
## Proof
<text, may contain [GAP: ...]>
## Evidence log
- 2026-10-12 | new -> conjecture | theorist | theory/blueprint/checks/prop-nstar/README.md | stmt:0123456789ab
```

- **Header keys:** exactly the nine above. `label`, `kind`, `status` and `uses` are required, and an unknown key is an error. Values are a scalar, empty (→ `None`), or a flow list `[a, b]` (→ `list[str]`, whitespace-trimmed, `[]` allowed).
- **Label:** regex `^[a-z]+:[a-z0-9][a-z0-9-]*$`. The filename must equal `label.replace(":", "-") + ".md"`.
- **Kinds:** `definition`, `assumption` (statuses `stated`, `superseded`); `claim`, `variant`, `imported` (statuses `conjecture`, `survived-search`, `proved`, `checked`, `formalized`, `verified`, `refuted`, `conditional`, `superseded`). `imported` may not exceed `checked`.
- **Log line regex:** `^- (\d{4}-\d{2}-\d{2}) \| (\S+) -> (\S+) \| ([a-z-]+) \| (.*?) \| stmt:([0-9a-f]{12})$`. Locators are `;`-separated.

**Interfaces — Produces:**
- `statement_hash(text: str) -> str`: first 12 hex characters of the SHA-256 of the text after CRLF→LF, stripping trailing whitespace on each line, and stripping leading/trailing blank lines.
- `@dataclass LogEntry(date: str, frm: str, to: str, actor: str, locators: list[str], stmt_hash: str)`
- `@dataclass Node(label: str, kind: str, status: str, uses: list[str], supersedes: str|None, superseded_by: str|None, lean: str|None, paper_ref: str|None, statement: str, proof: str, log: list[LogEntry], path: Path)`
- `class NodeError(Exception)`
- `parse_node(path: Path) -> Node`: raises `NodeError` naming the file and the problem.
- Test helper in the test file: `write_node(dir: Path, label, kind="claim", status="conjecture", uses=(), statement="S", proof="", log=None, **header) -> Path`. When `log` is None it writes a single valid `new -> <status>` entry with the correct hash.

- [ ] **Step 1: Write failing tests**
  - `parse_minimal_claim`: round-trips every header field, the statement and the proof.
  - `hash_crlf_stable`: `statement_hash("a\r\nb  \r\n") == statement_hash("a\nb")`.
  - `parse_bom_and_unicode`: a file starting with `﻿` whose statement is `n* = σ_d/√c − σ_d²/σ₀²` parses, with the statement preserved exactly.
  - `filename_label_mismatch`: `prop-x.md` declaring `label: prop:y` raises `NodeError`.
  - `unknown_header_key`: raises.
  - `bad_kind_status_combo`: `kind: assumption` with `status: proved` raises.
  - `malformed_log_line`: raises.
- [ ] **Step 2:** Run `python3 bin/test_blueprint_check.py`. Expected: non-zero exit (the module is missing).
- [ ] **Step 3:** Implement the Produces interfaces in `bin/blueprint_check.py`.
- [ ] **Step 4:** Run the tests. Expected: exit 0.
- [ ] **Step 5:** No commit (ADR-0002: `bin/` waits for Task 4). Commit only `templates/theory/blueprint-node.md`, with the message `templates(theory): annotated blueprint node example`.

---

### Task 2: Graph, status and evidence rules

**Files:** Modify `bin/blueprint_check.py` and `bin/test_blueprint_check.py`.

**Rules** (each violation is an error unless marked warning):

| # | Rule |
|---|---|
| G1 | Every `uses` label exists; no self-use; the graph is acyclic (report one cycle path). |
| G2 | Labels are unique across files. |
| G3 | A node at `checked`/`formalized`/`verified` may use only `definition`/`assumption` nodes at `stated` or claim-kind nodes at `checked` or above. |
| G4 | Using a `refuted` node is an error; using a `superseded` or `conditional` node is a warning. |
| S1 | `status` equals the last log entry's `to`; the first entry's `frm` is `new`. |
| S2 | Transitions on the ladder `conjecture < survived-search < proved < checked < formalized < verified`: up exactly one rung; down any number of rungs; any non-terminal → `refuted`/`conditional`/`superseded`; nothing leaves a terminal status. Definitions/assumptions: `new -> stated`, `stated -> superseded`. |
| S3 | Every entry's `stmt_hash` equals `statement_hash(node.statement)`. |
| E1 | `-> survived-search` needs a locator under the blueprint's `checks/` that exists. |
| E2 | `-> proved` needs actor `theorist`, a non-empty proof, and no `[GAP:` in it. While the status is `proved` or above, the proof must still contain no `[GAP:`. |
| E3 | `-> checked` needs actor `proof-verifier` and at least 2 distinct existing locators. |
| E4 | `-> formalized`/`-> verified` need actor `user`. |
| E5 | `-> refuted` needs at least 1 existing locator. `conditional`/`superseded` need `superseded_by` naming an existing label. |
| L1 | Locators resolve against the repo root (the nearest ancestor of the blueprint dir containing `.git`). Backslashes become `/`; a trailing `:N` or `:N-M` is stripped. A missing file is an error. An absolute path, or one resolving outside the root, is a **warning**. |
| V | Verdict: any error → `FAIL`; else any warning → `UNVERIFIED`; else `PASS`. No node files → `FAIL`. |

**Interfaces — Produces:**
- `@dataclass Report(verdict: str, errors: list[str], warnings: list[str], nodes: dict[str, Node])`
- `check_blueprint(bp_dir: Path, repo_root: Path | None = None) -> Report`. `NodeError`s become errors, not crashes.

- [ ] **Step 1: Write failing tests**, one per rule, each asserting the verdict and that the error text names the offending label. Names: `g1_missing_use`, `g1_cycle`, `g2_duplicate_label`, `g3_checked_on_conjecture`, `g3_checked_on_assumption_ok`, `g4_uses_refuted`, `s1_status_log_mismatch`, `s2_skip_rung`, `s2_downgrade_ok`, `s2_leave_terminal`, `statement_changed_after_log` (S3), `e1_search_without_checks_file`, `e2_gap_in_proved`, `e3_single_verifier`, `e3_wrong_actor`, `e4_formalized_by_theorist`, `e5_superseded_without_successor`, `locator_backslash_and_linesuffix` (L1 → PASS), `locator_outside_repo_unverified` (→ `UNVERIFIED`), `empty_blueprint_fail`, and `full_valid_blueprint_pass`, which builds a 5-node chain (def → asm → claim at checked with 2 verifier reports → variant refuted → claim conditional with successor) and expects `PASS`.
- [ ] **Step 2:** Run the tests. Expected: the new ones fail.
- [ ] **Step 3:** Implement `check_blueprint`.
- [ ] **Step 4:** Run the tests. Expected: exit 0.

---

### Task 3: CLI and `STATUS.md`

**Files:** Modify `bin/blueprint_check.py` and `bin/test_blueprint_check.py`.

**Interfaces — Produces:**
- `render_status(report: Report) -> str`: a Markdown table `| label | kind | status | uses |` sorted by label, plus a fenced ```` ```mermaid ```` `graph TD` block with one edge `dep --> node` per use. Mermaid ids replace `:` and `-` with `_`, and node text is `label<br/>status`.
- `main(argv: list[str]) -> int`, usage `python3 bin/blueprint_check.py <blueprint_dir> [--write-status]`. It prints the verdict line `BLUEPRINT: PASS|UNVERIFIED|FAIL (N nodes)`, then each error or warning on its own line. `--write-status` writes `<blueprint_dir>/STATUS.md`. Exit codes: PASS 0, FAIL 1, usage error 2, UNVERIFIED 3.

- [ ] **Step 1: Write failing tests**
  - `render_has_table_and_mermaid`: the output contains every label, the string `graph TD`, and the edge `def_a --> prop_b` for a `prop:b` using `def:a`.
  - `cli_exit_codes`: 0 / 1 / 3 for the PASS / FAIL / UNVERIFIED fixtures, and 2 with no args.
  - `cli_write_status`: `STATUS.md` exists after `--write-status`.
- [ ] **Step 2:** Run the tests. Expected: the new ones fail.
- [ ] **Step 3:** Implement.
- [ ] **Step 4:** Run the tests. Expected: exit 0.

---

### Task 4: Independent review and commit of `bin/`

**Files:** Create `quality_reports/reviews/2026-10-1X_blueprint-check_{redteam,correctness}_review.md` (written by the reviewers).

- [ ] **Step 1:** Run `/review-build bin/blueprint_check.py bin/test_blueprint_check.py`. That dispatches two fresh, blind `fable` reviewers (red team + correctness), with **Target:** naming both paths.
- [ ] **Step 2:** Fix or accept each finding, with a one-line reason in the session log; Criticals get a regression test (ADR-0002). Re-run the tests: exit 0.
- [ ] **Step 3:** Stage both files and both review reports, and add them to `quality_reports/reviews/INDEX.md`. Commit with `-F` and the message `bin: blueprint validator (graph, status, evidence rules) + tests`. Expected: the review-receipt hook allows the commit.

---

### Task 5: Agents on `main`

**Files:**
- Create: `.claude/agents/theorist.md` (start from `git show origin/behavioral:.claude/agents/theorist.md`)
- Create: `.claude/agents/theorist-critic.md` (start from `origin/behavioral`)
- Create: `.claude/agents/proof-verifier.md`

**Interfaces — Consumes:** node format (Task 1), validator CLI (Task 3).

- [ ] **Step 1:** `theorist.md`.
  - Frontmatter: `tools: Read, Write, Edit, Grep, Glob, Bash`, `model: fable`, `effort: high`.
  - Keep §§1–8 (framework table, examples-first workflow, definitions, notation, proof style, theorem statements, comparative statics).
  - **Delete** the "Read `quality_reports/paper_learnings/theory-writing-learnings.md`" line.
  - Add a **Blueprint protocol** section:
    1. one node per invocation;
    2. the task is always "determine whether the statement holds; if not, give a counterexample and the weakest repair";
    3. run examples, a counterexample search and exact checks first, saving scripts plus `.out` files under `theory/blueprint/checks/<label-with-dashes>/`; a counterexample → `refuted`; none → `survived-search` (never claimed as proof); SymPy/Z3 exact results certify only the sub-claim;
    4. variants (drop/weaken/swap each assumption) become `variant` nodes;
    5. repairs create new nodes and never edit a `## Statement`;
    6. unresolved steps get `[GAP: …]`;
    7. "no confident proof" is a valid outcome;
    8. literature results become `imported` nodes, subject to primary-source-first;
    9. it may raise status only as far as `proved`, appending a log line in the Task 1 format;
    10. it runs `python3 bin/blueprint_check.py theory/blueprint` before finishing and reports the verdict.
  - **Output paths:** `theory/blueprint/` replaces `quality_reports/theory/`.
- [ ] **Step 2:** `proof-verifier.md` (new critic).
  - Frontmatter: `tools: Read, Grep, Glob, Write, Bash`, `model: fable`, `effort: high`.
  - **Inputs:** only what the dispatcher passes: the statement, the proof (with `[GAP:` lines and the evidence log removed), and the statements of the `uses` nodes. It must not open `paper/`, `theory/*.tex`, `quality_reports/`, or other node files.
  - **Checklist:**
    - unused or contradictory hypotheses;
    - quantifier order and scope;
    - boundary cases (zero or degenerate variance, n = 0, empty or unbounded sets, division by zero);
    - unjustified interchange of limits, expectations, derivatives or integrals;
    - optional stopping without its conditions;
    - WLOG that loses generality;
    - circularity (a step relying on the claim itself or a consequence of it);
    - a conclusion stronger than what is shown;
    - a result quoted from memory.
  - **Bash:** numerical spot checks only, in a scratch dir under the system temp folder.
  - **Verdict:** `PASS` / `FAIL` (quote the failing step) / `UNVERIFIED`.
  - **Report:** written to `quality_reports/reviews/YYYY-MM-DD_<label-with-dashes>_proof-verifier_review.md` with the `agents.md` §2 header. **Never edits** node files.
- [ ] **Step 3:** `theorist-critic.md`.
  - Frontmatter: `model: fable`.
  - Delete the `theory-writing-learnings.md` line.
  - Replace the "Adversarial default" ledger item 10 with a **Blueprint cross-check**: every `proposition`/`lemma`/`corollary`/`theorem` environment in the target `.tex` must map, via some node's `paper_ref`, to a node at `checked` or above. An unmapped claim is −15 (load-bearing) or −5 (otherwise); a mapped claim resting on `conjecture`/`survived-search`/`proved` is −10.
  - Keep Phases 1–3 and the scoring table otherwise unchanged.
- [ ] **Step 4: Verify.**
  - `grep -n "theory-writing-learnings" .claude/agents/*.md` returns nothing.
  - Every line in the three files matching `\bprove\b` (case-insensitive) also matches `refut`, or sits in the kept §5 proof-*style* guidance. List any exceptions in the commit body.
- [ ] **Step 5:** Commit the three agent files with the message `agents: theorist + theorist-critic to main; new blind proof-verifier`.

---

### Task 6: `/theory` skill on `main`

**Files:** Create `.claude/skills/theory/SKILL.md` (start from `origin/behavioral`).

**Interfaces — Consumes:** agents (Task 5), validator CLI (Task 3).

- [ ] **Step 1:** Rewrite the modes. Frontmatter `allowed-tools: Read,Grep,Glob,Write,Edit,Bash,Task`.
  - `explore <question>`: the theorist creates `theory/blueprint/` if needed, plus conjecture/definition/assumption nodes and example checks.
  - `node <label>`: one theorist prove-or-refute pass.
  - `variants <label>`: the theorist creates and tests variant nodes for each assumption in `uses`.
  - `verify <label> [--model fable|opus]`: the skill builds the blind input itself (statement, cleaned proof, `uses` statements) and dispatches **two** `proof-verifier`s in parallel with that model override.
    - Both PASS → it appends `proved -> checked | proof-verifier | <report1>;<report2>`.
    - Any FAIL → it appends `proved -> survived-search` with the failing report.
    - A split → a third verifier, then the user.
  - `status`: runs `python3 bin/blueprint_check.py theory/blueprint --write-status` and prints the result.
  - `review [file]`: `theorist-critic`.
  - `develop`: loops over open claim nodes in dependency order (`node` → `variants` → `verify`), stopping at user decisions.
  - Delete the `theory-writing-learnings.md` lines. Keep the Principles, rewording "Prove comparative statics" to "prove or refute comparative statics".
- [ ] **Step 2:** Verify: the same two greps as Task 5 Step 4, run on `.claude/skills/theory/`.
- [ ] **Step 3:** Commit with the message `skills(theory): blueprint modes on main (explore/node/variants/verify/status/review/develop)`.

---

### Task 7: Wire rules, manifest and docs

**Files:** Modify:
- `.claude/rules/agents.md`: the pairs table (after line 19), the creators table (after line 113), and the routing sentence at line 25, which adds `theorist` and `proof-verifier` on `fable`;
- `.claude/rules/workflow.md:124`: the row becomes `| Formal theory/model | theorist + proof-verifier (per node) + theorist-critic (paper) |`;
- `.claude/rules/quality.md:15-21`: add the row `| Theory/model quality | 15% | theorist-critic's score of theorist (only when the project has a theory component; weights renormalize per "When Components Are Missing") |`;
- `.claude/file-classes.toml:95-96,108`: remove `theorist.md`, `theorist-critic.md` and `skills/theory/SKILL.md` from `[[overlay-only]]`, so they default to Class A;
- `README.md` and `CHANGELOG.md` (`[Unreleased]` → Added): one entry each for the theory workflow.

- [ ] **Step 1:** Make the edits.
- [ ] **Step 2: Verify.**
  - `grep -rn "theory-writing-learnings" .claude/ README.md` returns nothing.
  - `grep -n "theorist" .claude/file-classes.toml` returns nothing.
  - `python3 -c "import tomllib,pathlib;tomllib.loads(pathlib.Path('.claude/file-classes.toml').read_text())"` exits 0.
- [ ] **Step 3:** Commit with the message `rules/docs: wire theory workflow into agents, workflow, quality, file classes`.

---

### Task 8: Behavioral overlay carries `main`'s copies

**Files:** On a local `behavioral` branch: `.claude/agents/theorist.md`, `.claude/agents/theorist-critic.md`, `.claude/skills/theory/SKILL.md`, and add `.claude/agents/proof-verifier.md`.

- [ ] **Step 1:** `git switch -c behavioral origin/behavioral`, then `git checkout main -- <the four paths>`.
- [ ] **Step 2:** Verify: `git diff --quiet main behavioral -- <the four paths>` exits 0.
- [ ] **Step 3:** Commit on `behavioral` with the message `overlay: take main's theory agents + skill (now Class A)`. Then `git switch main`. **No push** (the user's call).

---

### Task 9: Pilot install in BDD and its blueprint

**Repo:** `github_repos/belief_distortion_discrimination`. Run this from a Claude Code session opened **in that repo** after Step 2.

- [ ] **Step 1:** In BDD:
  - commit any work in progress;
  - `git tag pre-theory-workflow-2026-10`;
  - copy this repo's four theory files (agents, skill, `proof-verifier`) into BDD's `.claude/`, and `bin/blueprint_check.py` into BDD's `bin/`;
  - add `sympy`, `hypothesis`, `z3-solver`, `scipy`, pinned to the versions that install, to `requirements.txt`, and install into `myvenv`.
- [ ] **Step 2:** Verify: `myvenv`'s python imports all four packages, and `python3 bin/blueprint_check.py` with no arguments exits 2 (usage), confirming the install.
- [ ] **Step 3:** In a BDD session, run `/theory explore` seeded with `theory/quadratic_loss_model_paper_v2.tex`.
  - One node per assumption, definition, Prop 1–7, `lem:band` and `cor:gap-rank`.
  - Labels mirror the paper's `\label{}`: `prop:nstar`, `prop:vol-commit-equiv`, `prop:commit-cogcons`, `lem:band`, `prop:cogcons-wedge`, `prop:commit-vs-seq-size`, `prop:gap-closure`, `prop:seq-vs-commit-bias`, `cor:gap-rank`, `asm:objective`.
  - Each has a `paper_ref`.
  - The belief-cost timing (flow while sampling) gets its own `assumption` node.
  - Existing claims enter as `conjecture`, whatever earlier reviews said.
- [ ] **Step 4:** Verify `python3 bin/blueprint_check.py theory/blueprint --write-status` → `PASS` (spec acceptance #4, structural part).
- [ ] **Step 5:** Commit in BDD with the message `theory: blueprint of v2 (nodes at conjecture) + theory workflow pilot install`.

---

### Task 10: Planted-error calibration (spec acceptance #2)

**Location:** BDD, `theory/blueprint/calibration/` (pilot content stays out of the public template).

- [ ] **Step 1:** Write `prop-nstar-correct.md`, a correct proof of `prop:nstar` taken from `theory/quadratic_loss_model_proofs_v2.tex`. Then write four flawed copies, each recorded in a sealed `ANSWERS.md` that is never passed to verifiers:
  - (a) the interior condition ensuring n* > 0 is dropped;
  - (b) a quantifier swap;
  - (c) a circular step that cites the conclusion;
  - (d) an overstated conclusion (n* asserted as the unique maximizer over all real n, or as integer-optimal).
- [ ] **Step 2:** For each of the 5 files, dispatch `proof-verifier` once with `--model fable` and once with `--model opus`, giving each the same blind input.
- [ ] **Step 3:** Write the result table (file × model → verdict, quoted step) to `quality_reports/reviews/YYYY-MM-DD_verifier-calibration_review.md`. **Pass criterion:** FAIL on all four flawed files and PASS on the correct one, separately for each model. If either model misses a flaw, record it, and do not use that model as a sole verifier until the checklist is revised and calibration re-run.
- [ ] **Step 4:** Commit in BDD.

---

### Task 11: Known-answer variant test (spec acceptance #3)

- [ ] **Step 1:** Copy `theory/blueprint/` and `theory/quadratic_loss_model_paper_v2.tex` **only** into a scratch dir outside BDD (system temp), so `quality_reports/` (where the 2026-09-14 referee reports live) is unreachable. Open a Claude Code session there with the Task 9 install copied in.
- [ ] **Step 2:** Run `/theory variants prop:cogcons-wedge`. **Pass criterion:** a `variant` node replacing flow-while-sampling belief cost with terminal-belief cost reaches `refuted` for the wedge, with the theorist's evidence showing Voluntary ≡ Commitment under the variant.
- [ ] **Step 3:** Copy the resulting variant nodes and checks back into BDD's blueprint, then re-run the validator: `PASS`. Commit in BDD.

---

### Task 12: Pilot verification, model comparison and read-out

- [ ] **Step 1:** In BDD, run `/theory develop` for `prop:nstar`, `prop:vol-commit-equiv` and `lem:band`, up to `checked` or an honest stop. Run `verify` once per model for each node that reaches `proved`.
- [ ] **Step 2:** The validator gives `PASS` or `UNVERIFIED` with each warning explained.
- [ ] **Step 3:** Append the read-out to this repo's session log:
  - nodes and final statuses;
  - findings by severity per model (spec acceptance #9);
  - fix rounds;
  - what to change before phase 2.

  Update `TODO.md` (theory item → phase 2 next) and `quality_reports/plans/INDEX.md` (mark this plan COMPLETED). Commit in both repos.

---

## Spec coverage

| Spec item | Task |
|---|---|
| §1 node format, ladder, log, validator | 1, 2, 3, 4 |
| §2 exploration, variants, repairs, project-venv deps | 5 (theorist protocol), 9, 11 |
| §3 theorist / proof-verifier / theorist-critic / skill / dangling ref / overlay / rules | 5, 6, 7, 8 |
| ADR-0004; ADR-0002 review of `bin/` | 0, 4 |
| Acceptance #1, #5, #6 | 1–3, 5–7, 8 |
| Acceptance #2, #3, #4, #9 | 10, 11, 9 + 12, 12 |
| §4 Lean, §5 plugin, acceptance #7–8 | out of this plan (phase 2 and phase 3 plans) |
