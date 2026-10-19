# Session Log: 2026-10-11 — Catch-up, hook launcher fix, theory/proof workflow brainstorm

**Status:** IN PROGRESS

## 1. Catch-up survey

Read CLAUDE.md, README, CHANGELOG, TODO, ADR-0001–0003, the September session logs and plans, and the archived work branch. Brief: `quality_reports/reviews/2026-10-11_repo-catch-up-survey.md`.

## 2. Hooks were silently failing open — fixed

- **Diagnosis (investigated, not assumed):** every hook in `.claude/settings.json` launched with `python3`. On this machine that name resolves to the Microsoft Store stub (WindowsApps, PATH entry 30), which exits 49; the real Python (installed 2026-10-08 at `AppData\Local\Python\bin`) is PATH entry 32. Claude Code treats exit codes other than 0 and 2 as non-blocking, so every gate was failing open.
- **Evidence:** a harmless `git update-ref -d` on a nonexistent ref was not blocked; the destructive-action guard log had 1 entry for the day's ~10 Bash calls versus 9 on 2026-09-24.
- **Fix 1:** each hook command now probes `python3`, `python`, `py` with `-c ''` and `exec`s the first that runs. If none run, it prints a loud stderr message and exits 1 (deliberately not 2, so a missing Python can't brick every Bash call). Applied by parsed-JSON edit with the `BYPASS_SHARED_GUARD=1` audit prefix.
- **Fix 2:** hook stderr was cp1252 (em-dash byte `0x97`), but Claude Code decodes UTF-8, so dashes showed as `�`. Confirmed with `od -c`. Prefixed every launcher with `export PYTHONIOENCODING=utf-8;` (no-op on Mac).
- **Verified live:** the same probe is now blocked by the guard, and the message renders a clean `—`.
- **Not committed yet.**

## 3. Theory/proof workflow — brainstorm (architectural path)

Goal (user): use the workflow to develop economic theory and proofs with more rigor. Break concepts into small steps, prove each rigorously, let conclusions follow from exploration rather than chasing them. Considering Lean and the `math-proof` plugin. The user is new to both.

Primer for discussion: `quality_reports/2026-10-11_math-research-with-claude-primer.md`. Sections 1–4 are unverified working knowledge, marked [verify].

**Decisions (user, via AskUserQuestion):**

| Question | Answer |
|---|---|
| Math involved | Elementary/algebraic; optimization & comparative statics; probability/dynamic (not equilibrium existence) |
| Machine | This Windows laptop; installing Lean here is acceptable |
| Lean role | **Auditor**: Claude writes Lean; the user audits statements via a side-by-side fidelity check |
| Placement | **`main`**; move `theorist`/`theorist-critic` up from the behavioral overlay |
| Pilot | A live project's theory (`bdm_bic` or `belief_distortion_discrimination`); not cloned on this machine yet |
| Approach | **A — blueprint first, Lean as an opt-in lane**, phased: (1) prose machinery: blueprint/ledger, exploration + counterexample search, blind verifier, theorist move, dangling-ref fix; (2) Lean lane; (3) `math-proof` siege hand-off for stubborn nodes |

**Found:** both `theorist` and `theorist-critic` (behavioral overlay) read `quality_reports/paper_learnings/theory-writing-learnings.md`, which exists on no branch.

**Survey dispatched:** four web-research agents on `opus` (ADR-0003 worker routing), each writing `quality_reports/reviews/2026-10-11_theory-survey_{A-mathlib-econ,B-lean-tooling,C-practice,D-fidelity-checks}.md`. Next: synthesize, then present the design in sections for approval, then write the spec.

**Survey done:** synthesis at `quality_reports/reviews/2026-10-11_theory-survey_synthesis.md`. The orchestrator opened Anthropic's FLT post directly and confirmed it; other claims are as reported by the streams, with URLs.

**Design approved section by section (user):**
1. Blueprint: Markdown/YAML nodes, immutable statements, status ladder, validator.
2. Exploration: prove-or-refute, counterexample search, assumption variants.
3. Agents: `theorist`/`theorist-critic` to `main`, new blind `proof-verifier`, two-verifier aggregation, dangling ref removed.
4. Lean lane: setup spike, project outside OneDrive, `formalizer` on `opus`, fidelity card signed by the user, `lean_check.py`.
5. Plugin hand-off, planted-error calibration, BDD known-answer test, phasing.

**Further user decisions:** `fable` with `effort: high` for theorist and verifier (fable-vs-opus verifier comparison folded into the ADR-0003 experiment). Online lemma search **allowed**, since the theory applies existing math and isn't sensitive.

**Pilot:** BDD cloned at `github_repos/belief_distortion_discrimination`, inside OneDrive (fine for the paper repo; the Lean project goes outside). Theory v2 has Assumption 1, Props 1–7, the band lemma and Cor 1. Its 2026-09-14 blind reviews confirmed the math and found the flow-vs-terminal belief-cost primitive, which becomes the known-answer test.

**Spec written:** `quality_reports/specs/2026-10-11_theory-proof-workflow-spec.md` (DRAFT, awaiting user review).

## 4. Phase 1 build (branch `theory-workflow-phase1`; plan `quality_reports/plans/2026-10-11_theory-workflow-phase1-plan.md`)

User approved the spec ("if there is no major deviation from the walkthrough") and the plan, and chose native execution. Tasks 0–8 were built on a feature branch, `theory-workflow-phase1`; the overlay copy is on a local `behavioral` branch, not pushed. Rulings are in the executor ledger. The main ones:
- `bin/` was held uncommitted until its review (ADR-0002);
- the overlay was updated through a temp worktree;
- the BDD pilot (Tasks 9–12) needs a session opened in the BDD repo.

### ADR-0002 review of `bin/blueprint_check.py` + tests

Two blind lenses on `fable`: red team 58/100 (`2026-10-11_blueprint-check_redteam_review.md`) and correctness 78/100 (`..._correctness_review.md`).

**Fixed.** Each fix has a test that failed first; the suite went from 50 to 97 checks.
- **Critical:** Windows device names (`nul`, `con`, …) counted as existing evidence files. They are now rejected, and locators must be regular files.
- **High:**
  - Directories satisfied every existence rule.
  - Any two files counted as "two verifier reports". Reports must now carry `**Reviewer:** proof-verifier`, `**Target:** <label>`, `**Score:** PASS`, and `**Proof:** <hash>`, and they are de-duplicated by file identity, so hard links don't count twice.
  - The proof was never hashed, so a checked proof could be replaced, and old reports could be reused after a re-climb. `-> proved` and `-> checked` now log ` proof:<hash>`; the current proof must match it; the checked hash must equal the proved hash; and reports must name that hash.
  - Non-ASCII output crashed the command line on the cp1252 console. Its output is now reconfigured to UTF-8.
- **Medium:**
  - `[GAP:` matching is now case- and space-insensitive, and comment-only proofs count as empty.
  - Look-alike section headings and stray text before `## Statement` are rejected.
  - The cycle search is iterative (a 1,500-node chain passed).
  - Empty statements are rejected.
  - With no enclosing repo, the result is UNVERIFIED, not a misleading FAIL, and there is a new `--repo-root` flag.
  - Masked and mutation-surviving tests were replaced by single-rule tests (E4 on verified, the imported cap, new→conjecture, G3 "stated", the E5 unknown successor, the Mermaid id, sorting, required keys).
- **Low:**
  - dates validated and non-decreasing;
  - `superseded_by` may not be self or refuted, and `supersedes` must exist;
  - drive-relative (`C:x`) and URL locators give UNVERIFIED;
  - `STATUS.md` is written with LF and escapes pipes;
  - quoted header values are accepted;
  - new `--hashes <node>` helper.

The format change reached the template, `theorist`, `proof-verifier` (a `**Proof:**` header line) and `/theory verify`.

**Accepted, with reasons:**
- **Actor field unauthenticated; statement and proof hashes self-attested; append-only not provable from a snapshot.** These are inherent to a file-based check. Git history is the backstop, and the review gate covers the tooling.
- **Evidence content other than verifier-report headers is not read.** By design: the validator checks provenance, not mathematics.
- **`imported` reading-notes rule not enforced by the script.** It is enforced by the theorist protocol and `primary-source-first.md`.
- **The plan's `g2_duplicate_label` test is absent.** The guard is unreachable: labels are lowercase and map 1:1 to filenames.
- **Case-insensitive-filesystem edge on macOS.** Labels are lowercase-only, and the filename comparison is exact.
- **`|` cannot appear inside a locator.** The format reserves it.
- **The test file needs Python 3.10 or later; the module runs on 3.7 or later.** The repo runs 3.14.
- **The downgrade-needs-locator rule is stricter than the plan's S2.** Kept deliberately: the spec says a verifier FAIL records the failing report. It is now documented in the template.
- **The no-repo warning echoes the path as given.** Harmless.

**Cost:** two lenses, about 353k agent tokens in total (red team 157k / 9.6 min; correctness 196k / 14.3 min). Findings: 1 Critical, 4 High, about 9 Medium, about 19 Low.

### Whole-branch review and merge

Final fresh review (`fable`): ready with fixes, no Critical. Fixed six Important findings, plus one Minor re-graded to Important because a template placeholder gave a false PASS:
- the proof hash now covers `uses`;
- the critic gets Bash, so it can run the validator;
- one meaning for `conditional`;
- verifier reports are never archived;
- `verify` checks its dependencies first;
- the pilot install list includes the template and tests;
- a placeholder Score line is not a PASS.

Then, at the user's request, fixed the ten deferred minors (validator suite 103/103) and fast-forwarded `main` to `69083fc`; the merged result passes. Pre-existing Windows failures in four hook test suites are recorded in TODO. Status: COMPLETE for phase 1 tooling; the pilot is next.

## 5. Hook test suites on Windows (branch `hooks-windows-tests`)

**Starting point:** four suites failed on Windows (citation backslash paths, the cp1252 print in primary-source, pytest missing for derive, symlink privilege in the destructive guard).

**Fixes:**
- **Citation library:** normalizes `\` to `/` on Windows only, then runs the existing containment checks; POSIX behaviour is unchanged.
- **Primary-source test:** forces UTF-8 output.
- **Destructive-guard test:** falls back to a directory junction, but only on WinError 1314, and uses `as_posix()` paths in shell strings.
- **Dev environment:** `requirements-dev.txt` plus `.venv` for pytest.

All eight suites now pass on Windows.

**ADR-0002 review:** red team 78, correctness 82.
- **Fixed:**
  - High (both lenses): the citation runner spawned a literal `python3` rather than the interpreter that had probed pytest, so a passing test reported MISSING under a venv. Now `sys.executable`; 26/26 under the venv.
  - Medium: skipped cases were counted as passes. They are now reported separately ("22/26 passed, 4 skipped" without pytest).
  - Medium: the junction fallback swallowed POSIX symlink errors. Narrowed to Windows WinError 1314.
  - Medium: Pygments was unpinned. Now pinned.
  - Low: removed the duplicate test; the POSIX branch asserts the rejection reason; UTF-8 guard on the citation suite.
- **Accepted:**
  - the guard summary has no explicit skip count (it prints which link kind was used);
  - drive-letter citations give a "file does not exist: C" message (pre-existing, harmless);
  - 8.3 and trailing-dot aliases resolve inside the repo (not an escape).
- **Cost:** about 283k agent tokens.

**Also found:** the destructive-action guard does not path-gate Windows OneDrive at all; it has macOS prefixes only. Recorded in TODO as separate work.

## 6. Phase 1 pilot read-out (`belief_distortion_discrimination` theory v2; plan Tasks 9–12)

**Setup.**
- The BDD clone's index was missing, so git listed every file as staged for deletion. The cause was a filename containing `|`, which Windows cannot hold. The user renamed it upstream, and the index was rebuilt from HEAD without touching any file.
- Tooling installed as commit `44d746b` (bin/ waiver: verbatim copies of code already reviewed in this repo).
- Windows `.venv` with pinned theory tools in `theory/requirements-theory.txt`.
- Restore tag: `pre-theory-workflow-2026-10`.

**Blueprint.** `/theory explore` built 30 nodes, ending in `BLUEPRINT: PASS` (`aa0d2ff`). The blueprint now has 48 nodes:
- 3 checked, 12 proved, 8 conjecture, 19 stated;
- 3 conditional (the original statements that were repaired);
- 3 refuted variants.

**What the workflow found in the paper.** None of these were in the 2026-09-14 reviews, which reported the math "correct by re-derivation":
1. **Prop 1 (`prop:nstar`) is false as stated.**
   - "Negative otherwise" fails at σ_d = σ₀²/(2√c), where the derivative is 0.
   - The strict comparative statics fail on the corner region, where n* ≡ 0.
   - The paper's proof also never derives the corner case its statement asserts.

   Found blind by both verifier models in calibration round 1; confirmed independently by the theorist with SymPy. The repair `prop:nstar-interior` is **checked** (4/4 blind PASS).
2. **Prop 2 (`prop:vol-commit-equiv`) is ill-posed.** It equates the real-valued n* with an integer stopping time. At the paper's own parameters, n* = 9.75 while both regimes stop at 10. The repair `prop:vol-commit-equiv-int` gives the exact integer statement and the rounding rule (equality iff n* ∈ {0..T}), and is **checked** (4/4).
3. **`lem:martingale` is false in one edge case.** "Not a martingale given θ" fails at T = 1, θ = μ₀. The repair `lem:martingale-horizon` is **checked** (4/4), with each part's probability measure explicit.
4. **The known-answer test passed (spec #3).** Working blind in a scratch copy with no reviews, the variant step rediscovered the referees' central finding: terminal-belief cost collapses the wedge, and so do held-belief and update-step costs. It also showed that attributing the wedge to γ rests on normal-normal signals and a location-invariant loss, which is the methods referee's identification point. Eight assumptions proved superfluous, and an unstated step in the wedge proof (b_t > 0 for t < T−1) was flagged.

**Calibration (spec #2).**
- **Round 1 was invalid as a calibration** because the "correct" baseline inherited the false statement. Both models correctly FAILed it. On the planted errors opus caught 3/4 and fable 2/4, plus one fable noticed but rated non-failing. Both missed a weak plant.
- **Round 2** (corrected statement, the theorist's proof, 12 runs): 4/4 planted errors caught on each model, and the correct proof PASSed on both. **Met.**

**Model comparison (spec #9; small sample, a judgment rather than a statistic).**

| | fable | opus |
|---|---|---|
| Round-1 planted errors caught | 2/4 (+1 noted as non-failing) | 3/4 |
| Found the real statement defect (round 1) | yes, in 3 of 5 runs | yes, in 4 of 5 runs |
| Round-2 planted errors caught | 4/4 | 4/4 |
| Real verifications (3 nodes × 2 runs) | 6/6 PASS | 6/6 PASS |
| Typical run | ~140–190 s, ~85–95k tokens | ~80–100 s, ~78–87k tokens |

Opus was slightly stricter in round 1 and about twice as fast. Otherwise the two are indistinguishable. Keep two verifiers, and keep fable as the default for `checked`.

**Acceptance criteria status:**
- #1 validator suite: PASS (103).
- #2: MET in round 2.
- #3: MET.
- #4: validator PASS on 48 nodes, with every v2 result a node.
- #5 and #6: PASS (#6 as amended: overlay copies are byte-identical).
- #9: recorded above.
- #7 and #8: phase 2 (Lean).

**What to change before phase 2:**
- **Script the blind verify input.** It was built by a scratchpad script here; it belongs in `bin/` as `--verify-input <label>`.
- **Tool the repointing of dependents** when a node becomes conditional. It took a dedicated theorist pass, plus re-logging of proved nodes, because the proof hash covers `uses`.
- **Lint agent frontmatter in CI.** A `: ` in a `description:` silently unregistered two agents.
- **Write the paper repairs.** Props 1 and 2 need rewording in `theory/quadratic_loss_model_paper_v2.tex`; that is the author's or the writer's job, not done here.

**Other outcomes:**
- The guard-hardening branch was SHELVED by the owner after three review cycles (see TODO).
- `lem:band` (below).

**`lem:band`.** It holds as stated; the theorist proved it by backward induction (`61b82bd`). Of three variants, γ = 0 was refuted, tie-continue proved, and objective-measure forecasts refuted (the band's symmetry rests on the subjective transition).

The first blind verify split, one UNVERIFIED and one PASS-with-caveat, and both pointed at the same gap: the proof used `def:posterior` and `asm:normal-normal`, which were missing from `uses`, so the verifiers never saw them. The theorist completed `uses` and the hash was re-logged. Two fresh verifiers then gave 2/2 PASS, and the node is **checked** (`e486bab`). The final blueprint has **51 nodes: 4 checked**, 13 proved, 7 conjecture, 19 stated, 3 conditional, 5 refuted.

**Lesson (add to the phase-2 list):** blind verification also tests the *dependency list*. A missing `uses` entry surfaced as UNVERIFIED, which is the intended behaviour. The theorist protocol should require `uses` to list every node the proof cites; the validator could check cited `prefix:label` tokens in the proof against `uses`.

**Caveat on numerical evidence:** the shared helper `checks/_lib/cogcons_dp.py` (40-node Gauss–Hermite) is not monotone in x and produced spurious shape violations. The known-answer variants used it, but their verdicts rest on written arguments; the helper served as search evidence only. Do not use it for shape claims.

Status: **phase 1 COMPLETE.** Spec acceptance #1–#6 and #9 are met. #7–#8 belong to phase 2 (Lean).

## 7. Pushes and phase 2 prep (2026-10-12)

**Pushes.** Sixteen unpushed workflow commits named the employer, which the personal-repo guard blocks. On the owner's choice ("Rewrite each commit"), they were replayed onto `origin/main` with neutral wording, keeping author and date: 165 replacements, local history only. The unscrubbed tip is kept locally as `main-backup-unscrubbed-2026-10-12`. A follow-up commit (`7c729db`) reworded two lines the mechanical replacement had left awkward. Pushed: `main` (17 commits) and `behavioral` (4). BDD was classified `personal` (approved remote: the owner's GitHub account) and its 10 pilot commits pushed.

**Phase 2 prep: four tools, built TDD.**
1. Validator (`bin/blueprint_check.py`): a proof that cites an existing node label in neither `uses` nor a declared mention gives a warning (UNVERIFIED).
2. `bin/blueprint_tools.py verify-input`: builds the blind verifier input and refuses unless the node is ready.
3. `bin/blueprint_tools.py dependents` and `repoint [--apply]`.
4. `bin/agent_lint.py`: frontmatter lint for agents and skills.

Tests: 117 validator, 30 tools, 45 lint. Every mutation of the new logic was caught except one, the label lookahead, which exposed a real bug (below).

Rulings (each with its cost if wrong):
- **Mentions.** On BDD's 51 nodes the first cut of the cited-label check gave 13 warnings, 12 of them meta-mentions ("asm:X is not used", "contradicting prop:Y"). So a node can declare `<!-- mentions: a, b -->` in the preamble before `## Statement`, which is outside both hashes: declaring a mention never forces re-verification. Cost if wrong: a mention could hide a real dependency. That is mitigated by the blind verifier, who flags a step resting on an unseen statement as UNVERIFIED.
- **Warning, not error** (as the TODO specified). `verify-input` turns it into a hard refusal, which is where it matters.
- **Lookahead dropped from `CITED_RE`.** A surviving mutation showed the `(?![a-z0-9:])` lookahead missed "By lem:b: …". Test `cl_label_before_colon` went RED→GREEN.
- **verify-input refuses rather than strips.** It refuses on a `[GAP:` marker instead of removing the line. It strips HTML comments so no motivation reaches the verifier. It accepts only `proved` nodes. Cost: re-verifying a `checked` node for a model comparison needs it moved down first.
- **repoint rewrites only `uses`.** It demotes dependents at proved or above to `survived-search`, keeping their search evidence, with actor `blueprint-tools` and the old and new node files as locators. It never edits proof prose (the validator then flags the stale citation for the theorist) and never edits statements (only reported). Terminal dependents are skipped. Cost: the theorist edits proof prose by hand.
- **Tools in a separate file** (`bin/blueprint_tools.py`), so the validator stays a validator. Projects copy both files.
- **agent_lint** checks `model` against aliases only (ADR-0003) and accepts a skill without `name`. It passes all 38 files here and 45 in BDD, and it flags the pre-fix `theorist.md` from before the 2026-10-11 fix.

BDD trial (read-only): `verify-input` correctly refuses `var:band-tie-continue` (cites `asm:tie-stop`). `dependents lem:martingale` lists its 3 refuted users plus 1 cite. A `repoint` dry run finds nothing live to move. BDD still needs a pass declaring its 12 mentions. That is a judgment call per node, recorded in TODO.

**ADR-0002 review, round 1** (fable; red-team 72/100, correctness 84/100; about 25 min of agent time, 380k agent tokens). Highs:
- `repoint` did not cascade to checked nodes resting on a demoted dependent;
- statement citations were never checked;
- `verify-input` ignored validator errors, flagged by both lenses.

Mediums:
- `repoint` was not atomic, and a lone-CR file crashed it;
- a mention could hide a dependency;
- verify-input omitted the definitions and assumptions under the used claims;
- the lint judged an empty `description` by other keys' blocks;
- the correctness lens found test gaps by mutation.

Every finding is fixed, each with a RED→GREEN test (validator 119, tools 54, lint 60), except the accepted ones below. The fixes redesigned `repoint` (an in-memory plan, the successor chain, the cascade to `proved`, pre-flight refusals, write-all-or-restore) and `verify-input` (a validator gate over the `uses` closure, base statements, a context-only section), so round 2 is running.

Rulings:
- **Mentioned nodes appear as "context only, not premises".** They are no longer withheld. BDD's variant statements name their parent claim and the dropped assumption: 30 statement warnings, which the verifier needs in order to read the claim at all.
- **The cascade demotes `checked` to `proved`, not further.** The proof and verifier reports stay valid, so the node can return to `checked` without re-verification.

Accepted, not fixed:
- `x-lem:b` (glued after a hyphen) stays uncited, by design;
- `lem:b-based` reads as the label `lem:b-based` (longest match; a label-shaped token);
- multi-line quoted scalars and flow lists, and trailing ` #` comments, stay flagged as house style, with messages that now say so;
- YAML 1.1 implicit typing (`name: yes`) is not checked, because Claude Code's parser is unknown;
- a demoted node keeps its `lean:` declaration, which is reported for the user to decide;
- two mutation survivors are benign: the writability pre-check is a second layer behind restore-on-failure, and the cascade line's proof hash is informational.

**ADR-0002 review, round 2** (fresh fable agents; red-team 74/100, correctness 87/100; about 25 min, 430k agent tokens). Round-1 fixes held under re-attack, including restore on an injected mid-batch write failure. The correctness lens traced the climb-back: a cascaded node returns to `checked` on its original verifier reports.

Highs:
- the cascade line wrote the current proof hash, so a checked node edited after logging went from FAIL to PASS;
- the lint crashed on a `description:` whose text starts on the next line.

Mediums:
- the cascade was global, demoting unrelated pre-existing errors;
- unparseable dependents were silently dropped;
- a dependency cycle did not block verify-input;
- the comment-leak check skipped mentioned statements;
- several behaviours were unpinned (mutations survived).

All fixed, each with a RED→GREEN test, or pinned (tools 74, lint 64, validator 119):
- a cascade line carries no proof hash, and repoint refuses any node with validator errors of its own;
- the cascade is scoped to what this repoint lowers;
- unparseable files make repoint refuse and dependents warn;
- a cycle among the closure blocks verify-input;
- the context section is built from one list of shown labels, so nothing appears as both a premise and context; it includes labels named by the shown statements, and a mention of no node blocks;
- the future-date refusal applies only to logged nodes;
- `--out <dir>` is a usage error;
- lint: next-line descriptions are checked as plain scalars, a per-file exception guard was added, `README.md` in agents is skipped, a comment on `name` is no longer double-flagged, and messages are corrected.

Pins: cascade locator, fixpoint order, restore on write failure, successor-self, supersession loop, transitive validator error, imported readiness, context without status or proof.

A spot mutation run killed 3/3 before Claude Code stopped it for low system memory. The other 8 mutations were not run.

Accepted, not fixed:
- the CLAIM_KINDS filter in the cascade is now redundant with the scoping (only claims are lowered), so it is not separately pinned;
- a `checked` dependency whose reports sit outside the repo counts as ready, matching the validator's UNVERIFIED design;
- the lint flags dotted or spaced keys and does not catch less-indented block-scalar lines (house style; nothing in the repo is affected);
- whether Claude Code accepts a next-line plain description is unconfirmed (no YAML parser on this machine).

No third cycle: the round-2 fixes are scoped and do not change the design.

## 8. Lean setup spike (2026-10-12): blocked at step 1

Machine state: no elan, lake, lean or uv; no proxy variables; WinHTTP is direct; 284 GB free on C:.

Downloading the official installer `https://elan.lean-lang.org/elan-init.ps1` (into an empty folder under `C:\Users\christina.sun\lean\_downloads\elan\`, to be read before running) returned the corporate web filter's block page: "Website blocked … Threat found: Sandbox Suspicious". Nothing was downloaded or installed.

This is an organisational security control, so no alternative mirror or download route was tried. Phase 2 cannot proceed on this machine until the owner chooses a path: request an allow-listing from IT, run the Lean lane on a personal machine, or defer phase 2 (spec §4 allows deferral).

The owner chose to ask IT for an allow-list. A request draft was written outside the repo because it names the employer's IT service. HEAD probes found every host reachable: lean-lang.org, the GitHub releases, cache.mathlib.org (the current Mathlib cache host; lakecache.blob.core.windows.net is the legacy one), and PyPI. So the block is Zscaler's sandbox verdict on the downloaded files, not a host block.

**Overlay defect found by the new lint.** `bin/agent_lint.py` run on the `behavioral` tree flagged `theorist.md` and `theorist-critic.md`: the `: ` description defect fixed on main in `a3a22b5` had never reached the overlay, so both agents were silently unregistered there. The four theory agent and skill files were synced from main (`10a0036`, pushed), and the overlay now lints clean (45 files). `bin/` and `templates/theory/` are still absent on the overlay; they come with the full Class A sync (Track A step 3, about 200 files behind main).

**Spike resumed (same day).** The owner reported that the filter flags harmless sites at random (it also blocks Adobe Acrobat), and confirmed with IT that alternative sources are fine. The owner had first downloaded a SourceForge mirror; it held macOS arm64 (Mach-O) binaries, unusable here, and was not used. Instead the official GitHub release was used: `elan-x86_64-pc-windows-msvc.zip` v4.2.4, whose SHA-256 matched GitHub's published asset digest (`fad2e980…6c111`). It was installed per-user with `--default-toolchain none`.

Results, all PASS:
- **Toolchain:** `lake +leanprover-community/mathlib4:lean-toolchain new spike math` in `C:\Users\christina.sun\lean\spike` (`core.autocrlf=input`) fetched Lean v4.35.0-rc4 from GitHub releases, the Mathlib v4.35.0-rc4 sources, and the prebuilt cache (9,004 files).
- **Build:** two small lemmas (quadratic-loss minimum; concavity of −x²) build under `lake build --wfail` (exit 0). Mathlib now expects the module system, so files start with `module` and `public import`, and `set_option linter.style.header false` is needed for scratch files.
- **Axioms:** `#print axioms` gives exactly [propext, Classical.choice, Quot.sound] for both.
- **`sorry`:** fails with `-DwarningAsError=true` ("declaration uses `sorry`", exit 1).
- **`leanchecker`:** exit 0, 51 s.
- **`lean-lsp-mcp` 0.31.0** (pinned, own venv at `C:\Users\christina.sun\lean\_tools\lean-lsp-mcp`): the stdio handshake works on native Windows, with 22 tools including hosted search (leansearch, loogle, leanfinder, hammer premise). `lean_diagnostic_messages` on the spike file returns success with no items.

Outcome: phase 2 proceeds. Not yet done: registering the MCP server with Claude Code (a settings change for the owner to approve), the phase-2 plan, and the machine-local Lean-path setting.

## 9. Phase 2 plan and Task 0 (2026-10-12)

**Plan.** Plan v1 went through blind fit-for-purpose (58/100) and efficiency (64/100) reviews. The owner does not read Lean, so the fit lens judged the card design against that; its Critical was that the statement hash missed helper definitions. Plan v2 adopted every finding but one; the changes table is in the plan. The owner approved v2: a new node for parts (a)–(c), and the auditor calibration kept.

`lean-lsp-mcp` is registered at user scope (`claude mcp add --scope user lean-lsp`), and the health check connects.

**Task 0 (hand-driven slice).**
- **Layout:** the spike project was renamed to `C:\Users\christina.sun\lean\bdd` (package `bdd`, library `Bdd`; `autoImplicit = false`; `/Bdd/Check` gitignored). The layout is `Bdd/Statements/NstarAC.lean` (self-contained: `postVar`, `vStop`, three `_part_x_stmt : Prop`), `Bdd/Proofs/NstarAC.lean` (`sorry`), and a hand-written `Bdd/Check/NstarAC.lean`. The module system works with `noncomputable def`s.
- **Strict build:** `lake build --wfail` fails on the three `sorry`s (exit 1, 79 s cold); a plain rebuild takes 17 s.
- **Check file** (36 s, mostly the Mathlib import): `#print axioms` prints `'Bdd.nstarAC_part_a_check' depends on axioms: [propext, sorryAx, Classical.choice, Quot.sound]`. That is the format to parse.
- **`leanchecker` exits 0 on the sorry proofs** (47 s). It re-checks proofs at the kernel level, and `sorryAx` is just an axiom to the kernel. So the axioms check is what catches `sorry`; `leanchecker` guards against elaborator or kernel-bypass faults only.
- **Versions:** the toolchain is `Lean 4.35.0-rc4, x86_64-w64-windows-gnu, commit c29b6dd`, and `lake-manifest.json` carries the Mathlib rev, which reports will record.
- **`lean-lsp-mcp` with no `LEAN_PROJECT_PATH`,** started from an unrelated directory, finds the project from the file path. Diagnostics list the `sorry`s; `lean_goal` shows `⊢ nstarAC_part_a_stmt`, so proofs should begin with `unfold <stmt>`, which is a layout-doc note.
- **The Lean repo** has a local first commit `426689e`, with the repo-local identity copied from the workflow repo; it is unclassified for the push guard.

**Backup gap** (raised by the owner's side note). The Lean folder is outside OneDrive with local git only, on a temporary laptop. It needs a private remote on the owner's GitHub (classed `personal`, like BDD) once real proofs exist; this was added to plan Task 8.

**Tasks 1–3 built** (`bin/lean_check.py`, its unit and integration suites, the core-Lean fixture `bin/fixtures/lean_check/`, and the validator `formalized`/`verified` rules). Lean facts found while building: def bodies need `@[expose]` under the module system; `decide +native` compiles to a private `_native.decide.ax_*` axiom; the Mathlib header-linter option is unknown in a core-only project.

**Tasks 5–7 built:** the `formalizer` agent, `templates/theory/{lean-layout,fidelity-card}.md`, the `/theory formalize` and `prove` modes, and three practice cards in `quality_reports/calibration/2026-10-12_lean-cards/` with the answers sealed outside the repo. The blind back-translator, given only the Lean text, named both planted defects (B: missing `0 < c`; C: `ConcaveOn` for strict concavity), and noted an unused hypothesis on A. The calibration therefore measures the owner plus the full card, which is the design under test.

**ADR-0002 review, round 1** (fable): red-team 25/100, correctness 62/100; each about 20 min and 210–230k agent tokens.

Three Criticals, each confirmed on the real toolchain to give a full PASS on a fake proof:
1. the check file imported only `Proofs`, so a proof file could redefine every `_stmt` as `True`;
2. `macro_rules` or `notation` in a proof file rewrote the check file's theorems;
3. a kernel-forged theorem (`skipKernelTC` + `addDecl`) in a helper module passed, because only the node's own module was scanned and passed to `leanchecker`.

Highs:
- statement-file lines were classified only at column 0, so indented commands slipped through;
- any `@[…]` prefix exempted the rest of its line from the banned-command check;
- parameterised or unannotated `_stmt`s dropped silently out of the audited set;
- a `_stmt` outside the package namespace was let through;
- the card's part list was not cross-checked.

Mediums:
- the stripper desynced on character and raw-string literals;
- a missing `leanchecker` (the real Windows shape) gave FAIL;
- wrapped axiom lists gave a false FAIL;
- hollow reports were accepted;
- test gaps.

Fixed:
- **Check file:** it imports `Statements` before `Proofs` and uses full names.
- **Project-wide scan** (`.lake/` excluded): syntax extensions, `#` commands, meta code, `import Lean`/`Lake`, axioms, unsafe/extern/implemented_by/native, `skipKernelTC`, and non-whitelisted `set_option`. `sorry`/`admit` stay node-only, since the axiom check covers dependencies.
- **`leanchecker <Pkg>`** over the whole package.
- **Command classifier:** it reads the head word after whitespace, `@[…]` and modifiers, at any indentation. Statement files allow only `@[expose]`, exactly one `namespace <Pkg>`, and no declarations outside it.
- **`_stmt` form and card list:** every `_stmt` must be a closed ASCII `def … : Prop`, and the card carries an `Audited statements` list that `lean_check` compares.
- **Proof file:** it must import its statements and must not declare `_stmt`s.
- **Stripper:** handles character and raw strings.
- **Missing `leanchecker`:** now UNVERIFIED.
- **Axiom lists:** wrapped lists are joined.
- **Settings:** `relaxedAutoImplicit` is checked.
- **Bad input:** non-UTF-8 gives FAIL, not a traceback; a relative `lean.toml` resolves from the repo root.
- **Report:** it carries the proof file's SHA-256.
- **Validator:**
  - it rejects hollow reports (no `Lean (version` toolchain, or a FAIL/UNVERIFIED line, or no PASS line, under a PASS verdict);
  - `Signed off` must be initials and an ISO date;
  - the card's `Node statement hash` must match the node;
  - a newest full report that is UNVERIFIED is a warning, while FAIL is an error;
  - `_1` names are ignored.
- **Formalizer:** it never writes reports; the dispatcher or owner runs `--write-report`.

Tests: `lean_check` unit 112, integration 13 (all three Criticals as real-toolchain regressions), validator 145, tools 74, lint 64. Spot mutations of the eight key defences were all killed.

Accepted, not fixed:
- a deliberately forged full report written by a misbehaving agent remains possible, because the validator cannot re-run Lean. Mitigations: the formalizer may not write reports, the hollow-report rules, and the owner or dispatcher runs `lean_check` at each approval;
- reports omit the Lean project path, which would put a machine path in a tracked file;
- `--timeout` is per tool call, as documented.

Round 2 follows, because the fixes changed the design.

**ADR-0002 round 2** (fable): red-team 32/100, correctness 58/100.
- **Red-team:** three new full-PASS attacks on the real toolchain:
  1. `srcDir = "alt"` in `lakefile.toml`, so Lake compiles a different statement file from the hashed one;
  2. `lakefile.lean`, which overrides the TOML and is never scanned;
  3. a `Fix.Fix` sub-namespace hijacking name resolution in the check file.
- **Correctness:** one Critical: a head-word-only command ban, so `open Nat in macro_rules …` on one line gave a full PASS.
- **The pattern:** each round of text-level patches opened new holes. The owner was asked and chose a spike of Lean FRO's `comparator`.

**Comparator spike (PASS).** The reference manual (Validating Proofs) calls it the "gold standard". `leanprover/comparator` (`ca04cfc`) and `lean4export` (`05d43a2`) are both pinned to v4.35.0-rc4, and both were cloned and built into `C:\Users\christina.sun\lean\_tools\` (36 s).
- **Windows:** comparator spawns its sandbox (`landrun`, Linux-only) as a process. Its non-Linux development shim `scripts/fake-landrun.sh` runs through a one-line `fake-landrun.cmd` calling Git Bash. That means no sandbox, which is acceptable for our threat model (see below).
- **Bundled tests:** 16/16 of comparator's own test projects gave the expected exit codes on Windows, including `olean_issue`, `proj_trick`, `primitive_issue`, `char_ofnat_issue` and the `def_hole` cases. The 4 nanoda tests were skipped.
- **Our fixture**, in Challenge/Solution form: a generated `Fix.Check.Challenge` imports the signed statements plus `theorem Fix.x : Fix.x_stmt := sorry` per statement, and `Fix.Check.Solution` imports the proofs. Dotted module names work. Results:
  - honest: exit 0, "Your solution is okay!";
  - proof file redefines every `_stmt := True`: "Const does not match between challenge and target";
  - `sorry`: "Illegal axiom detected: 'sorryAx'";
  - helper axiom: "Illegal axiom detected: 'Fix.magic'";
  - `Fix.Fix` shadow: "Challenge and solution theorem statement do not match";
  - **`srcDir = "alt"`: exit 0, accepted.** This matches comparator's stated assumption 1 (a trusted lakefile).
- **Design consequence:** lean_check keeps the card, hash and report plumbing and the statement-file readability rules, and hands soundness to comparator. lean_check must:
  - enforce a canonical `lakefile.toml` (one `lean_lib` named `<Pkg>`, `globs = ["<Pkg>.+"]`, no `srcDir`/`roots`/extra args; a single Mathlib `require`) and reject any `lakefile.lean`;
  - delete the project's own `.lake/build` before running comparator (its assumption 2: nothing adversarial compiled beforehand);
  - keep the project scan for code-executing commands as defence in depth, because the Windows build is unsandboxed.

  The threat model, stated plainly: this guards against Lean-level mistakes, shortcuts and tricks inside the project sources and lakefile. It does not guard against an actor with shell access who can edit `.lake/packages`, `lean_check` itself, or the reports.

**lean_check rebuilt on comparator.** Full mode:
1. static checks (canonical lakefile and no `lakefile.lean`, statement-file rules, card, proof imports, project scan);
2. clear `.lake/build`;
3. generate `LeanCheck/<Name>{Challenge,Solution}.lean` and a `.comparator.json`;
4. `lake env <comparator> <config>`. PASS requires exit 0 and "Your solution is okay"; FAIL reports comparator's `uncaught exception` line.

Statements mode builds `<Pkg>.Statements.<Name>` without `--wfail`, so Mathlib style lints no longer fail honest work.

Round-2 classifier fixes:
- keywords are matched anywhere on a line;
- `_stmt` is found at any indentation, and `: Prop` on the next line or without a space is accepted;
- honest forms pass: `@[expose]` on its own line, match arms, `#[…]` arrays, qualified `Foo.extern`, and `set_option linter.* false`;
- `«»` names are handled by the stripper.

The card's `Node statement hash` is now filled by the formalizer and checked by both tools. The formalizer runs `--statements-only` after drafting the card.

Tests:
- unit 158;
- integration 13/13 against real comparator (66 s; full check 14 s), with every attack from both review rounds as a regression and each caught at its intended layer: comparator catches the hidden `sorry`, the namespace shadow and a proof of another statement; static checks catch `srcDir`, `lakefile.lean`, `open … in macro_rules`, redefinition, edited helper and missing companion;
- validator 145, tools 74, lint 64.

Round 3 (the last under three strikes) follows.

**ADR-0002 round 3** (fable): red-team 30/100, correctness 64/100.
- **What held:** the comparator core. No wrong proof got past the Challenge/Solution comparison or the kernel replay.
- **Criticals:**
  1. `lake-manifest.json` was never checked, so a manifest pointing Mathlib at another source gave `verified` for a false statement (red-team);
  2. the statement file's import rule applied only at column 0, so an indented `public import` of an unhashed project module got a full PASS (both lenses).
- **Highs:**
  - `LeanCheck/` was scan-exempt but importable, and planted build-time code ran;
  - helper names could rebind or shadow (dotted names, homoglyphs, `open … renaming`);
  - from PowerShell an honest proof got FAIL, because comparator's `which git` failed without Git's `usr\bin`.
- **Real Mathlib** (correctness, on a copy of bdd): statements mode PASS in 62 s, full PASS in 4 min 26 s.

**Three strikes → owner.** The owner asked what the problem was and how likely agents are to find these workarounds in real work. My answer: the remaining holes need deliberate deception plus specific Lean build-system knowledge, which the stated threat model already excludes; the realistic shortcuts (sorry, an added assumption, a reworded statement, native tactics, a proof of a different statement) are caught. The owner agreed to a **middle path**: fix the real bugs and the cheap holes, one focused check, commit, pilot. The trusted harness is kept as later hardening.

**Middle-path fixes:**
- **Statement-file rules:**
  - imports are checked at any indentation, including `import all`;
  - definition names must be plain ASCII without dots;
  - zero-width characters are rejected;
  - `open … renaming/hiding` is banned.
- **`manifest_problems`:**
  - every package must be git from a `leanprover`/`leanprover-community` GitHub repo, pinned to a 40-hex commit, with no `subDir`/`dir`;
  - Mathlib's `inputRev` must equal the lakefile rev, and `packagesDir`/`lakeDir` must be the defaults;
  - each checked-out package's `.git` HEAD must equal its pin.
- **`LeanCheck/`** is cleared before every build in both modes, and nothing may import it.
- **Clearing is verified:** a `.lake/build` or `LeanCheck/` that cannot be removed gives UNVERIFIED.
- **`tool_env`** puts Git's `usr/bin` (derived from `which git`) on PATH.
- **Time-outs** kill the whole process tree.
- **Comparator output classification:** Lean compile errors give FAIL; "Child exited" or missing tools give UNVERIFIED, with the cause kept.
- **Syntax keywords** stay banned anywhere in the statement file, but in proof and helper files only at command positions, so honest binders such as `prefix` pass. Code-executing keywords stay banned anywhere.
- **Toolchain line:** taken from the `Lean (version` line. Lake's leading `info:` lines would otherwise have made every real report hollow.
- **Docs:** `lean-layout.md` brought in line.

**Tests:**
- unit 193;
- integration 15/15, including the round-3 Critical and the planted-`LeanCheck` case, in both Git Bash and **PowerShell** (with `usr\bin` not on PATH);
- validator 145, tools 74, lint 64.

**Deferred:** the trusted harness (Challenge built in an owner-controlled project with its own Mathlib); capping `set_option` resource values (round-3 red-team Medium 6).

**Focused verification of the middle-path fixes** (fable, 72/100). Every round-3 finding was confirmed FIXED with evidence, or deferred as agreed:
- the bdd manifest passes and all nine packages are at their pins;
- integration passed 15/15 from Git Bash and from PowerShell;
- a time-out left no `lean`/`lake`/`comparator` processes behind.

Two blockers re-opened fixed findings:
1. a second import on the same line (`public import Mathlib public import Pkg.Hidden`), because the import rule read only head words;
2. a two-line `open Nat` / `renaming mul → plus`, which went through comparator to a full PASS.

Both were fixed:
- imports are checked over the whole stripped text;
- `renaming`/`hiding` are banned anywhere in a statement file, as is a line headed `in`.

The cheap notes were also done:
- Mathlib's manifest URL must be exactly `leanprover-community/mathlib4`;
- reserved package names (`Mathlib`, `Lean`, `Std`, `Batteries`, …) give FAIL;
- the formalizer's statements-mode list was updated.

Tests: unit 199, integration 16/16 (real comparator; the two-line renaming case added), validator 145, tools 74, lint 64.

Noted, not blocking (verifier):
- `«…»` names bypass the ASCII rule (they are visible, and no real shadowing results);
- indented `alias`/`unif_hint` pass the static rules;
- a continuation line beginning with a binder named `prefix` is a false positive;
- `meta`/`elab` binders are flagged by design.

The BDD Lean project (`C:\Users\christina.sun\lean\bdd`) now has the canonical lakefile, and its real lakefile and manifest pass.

## 10. Lean lane pilot, up to the owner's card (2026-10-12)

- **Commits.** Workflow `eeea176`: the Lean lane. The review gate was waived once: its Target matcher has no directory support, so the reviewed fixture's `lean-toolchain` needed it; TODO item added. BDD `5f6826c`: tools installed; the validator now gives 34 warnings, all mention judgments, and no errors.
- **Node `prop:nstar-interior-ac`** (decision A), created by the theorist:
  - its statement is byte-identical to the parent's preamble plus (a)–(c), checked by `diff`;
  - its proof is the parent's Steps 0–3;
  - checks: exact SymPy 18/18, and a numeric search over 4,000 triples with exact-rational concavity;
  - two blind proof-verifiers on fable both PASS (one ran 2,000 random draws, the other 20,000), so the node went to `checked` (BDD `957c9c7`).
- **Formalize stage 1** (formalizer, opus; the lean-lsp MCP was unavailable mid-session, so it used shell `lake`):
  - `Bdd/Statements/NstarAC.lean`: three helpers, three parts, four companions (nonvacuous, an interior sanity instance (1, 1, 1/4) → n* = 1 and V = −3/4, a boundary sanity instance (2, 4, 1) → 0 and −2, and a false variant without (b)'s proviso);
  - "the maximizer" is expressed as `∃ nstar, ∀ n, isMaximizer n ↔ n = nstar`;
  - `--statements-only` PASS, re-run by the dispatcher.
- **Blind back-translation** (fable): it was given the Lean with every comment and docstring stripped, so that the docstrings' English could not leak. It matches the paper part by part, and its only notes are redundancies. Its glossary agrees with the formalizer's symbol for symbol. It was pasted into card section 8 (BDD `38bdac4`; Lean repo `f13e17d`).
- **Waiting on the owner:**
  1. the practice cards (calibration);
  2. the pilot card: sections 3, 9 and 10, then Verdict and Signed off.

  After that: `--statements-only --write-report`, the `checked -> formalized` line on approval, `/theory prove`, and the read-out.

## 11. Calibration read-out (2026-10-13)

The owner signed all three practice cards. Answers were unsealed only afterwards and are in `quality_reports/calibration/2026-10-12_lean-cards/ANSWERS.md`.

| Card | Planted | Owner verdict | Owner note | Result |
|---|---|---|---|---|
| A | none (FAITHFUL) | WITH-NOTED-DIFFERENCES | "stronger": the inequality holds without v ≥ 0 | False alarm, mild: the note is mathematically true, but paper and Lean both assume v ≥ 0, so it is not a paper/Lean difference. An extra Lean hypothesis would make Lean *weaker*, not stronger |
| B | dropped `c > 0` | UNFAITHFUL | "stronger": does not state c > 0 | Caught, defect named, direction right (a dropped hypothesis makes the claim stronger, here false) |
| C | `ConcaveOn` for strictly concave | UNFAITHFUL | "weaker": concave is not strictly concave | Caught, defect named, direction right. Owner was unsure of this one |

- **Score:** 2/2 planted defects caught, 1 mild false alarm, 0 misses.
- **Time:** A 20 min, B 10 min, C not recorded.
- **Gaps:** section 9 (concrete instance) left blank on all three cards. For these cards the defect showed in the statement text, so no number was needed to catch it. For the pilot, section 9 has worked values to check against.
- **For the guide (efficiency #8):** the owner found the stronger/weaker direction hard to apply to a hypothesis and doubted whether the difference between strict and plain concavity counts. Both belong in the guide.
- **Acceptance #8 anchor:** recorded. The owner reads cards well enough to catch a dropped hypothesis and a weakened conclusion.

## 12. Lean pilot read-out (2026-10-13 to 2026-10-14)

`prop:nstar-interior-ac` (parts (a)–(c) of BDD Prop 1, split off under decision A) is **`verified`**:
- `checked -> formalized` 2026-10-13, BDD `5da9772`: owner-signed card (FAITHFUL, CS 2026-10-13) plus statements-mode `lean_check` PASS (`lean_check_2026-10-13.md`).
- `formalized -> verified` 2026-10-14, BDD `bef1c6a`: full `lean_check` PASS (`lean_check_2026-10-13_2.md`). The comparator confirmed every proof proves exactly its signed statement, using only propext, Quot.sound and Classical.choice, and the kernel accepted the replay. Proofs are in Lean project `77d1a93`; the statement file is unchanged since signing.
- Each status line was dry-run on a scratch copy before the owner was asked (no new errors; the same 34 pre-existing warnings). A negative control (card dropped from the line) FAILed as it should.

**Costs**

| Stage | Who | Time | Notes |
|---|---|---|---|
| Formalize stage 1 + blind back-translation | formalizer (opus), fable | not recorded in this log | §10 |
| Statements check | lean_check | about 1 min | 62 s on the bdd copy (§9) |
| Calibration (3 practice cards) | owner | 30 min + C unrecorded | §11 |
| Pilot card | owner, with Claude | about 30 min | done one part at a time; see below |
| Prove stage | formalizer (opus) | about 10 min, 101k tokens, 27 tool calls | all 7 statements; no open parts on the first dispatch |
| Full check | lean_check | 165 s | the comparator run |

**What caught what:** in the pilot, nothing needed catching. The back-translation, the companions (two sanity instances, non-vacuity, a refuted false variant) and the owner's checklist all agreed with the paper. In calibration, the owner caught both planted defects (§11).

**Acceptance status (spec 2026-10-11)**
- **#7: met.** The unit suite (199) and the integration suite against the real comparator (16/16) cover `sorry`, hidden `sorryAx`, extra axioms and a statement edited after signing.
- **#8: met in part, not as written.** The node is `verified` and the owner signed the card. But the owner did **not** read it unaided. They found the full card overwhelming, so Claude translated each Lean part into numbered lines in the paper's notation, which the owner compared with the paper, and set out the section 9 arithmetic for the owner to check. The judgments are the owner's (card §10 says how the card was filled in). The pilot is also parts (a)–(c) of Prop 1, not the whole proposition.
- **Lesson for the sign-off ADR (TODO):** "unaided" does not fit an owner with no Lean background. The pilot's working form is the numbered checklist. The owner also questioned the separate status-line approval. Both go into the ADR.

**Still open:** a private remote for the Lean project (`~/lean/bdd`, local git only, unclassified).
- **Backup (2026-10-14):** the owner asked Claude to create the repository. The GitHub CLI is not installed. Claude Code's auto-mode check first blocked use of the stored GitHub login, and the owner then authorised it. Created private `chesun/bdd-lean` through the API. The pre-push guard needed three per-repo settings, set to match BDD: the repository class (personal), the approved-remotes allowlist (the owner's GitHub account) and the declared expected email. The push was clean (4 commits), and the remote `main` equals local `77d1a93`. Plan marked COMPLETED.

## 13. ADR-0005 (lighter Lean sign-off), drafted and reviewed (2026-10-14)

- **v1** reviewed blind on fable: fit-for-purpose 66/100 (1 Critical, 3 High, 4 Medium, 2 Low); efficiency 82/100 (1 High, 4 Medium, 3 Low).
  - The Critical was confirmed in code: `Signed off` is not bound to a statement version (`bin/blueprint_check.py:341`, `:368`). The gap already existed under ADR-0004; the status-line approval was its only backstop.
- **v2** added the hash-bound signature, a report-file audit, a coverage check, no shared symbol table, a sealed calibration set, a retroactive pilot audit and a slimmer card. A fresh fable verify pass gave 78/100: 14 of 18 v1 findings resolved, the Critical partly, and two new Highs:
  - a signature-date rule that breaks re-signing. Confirmed: the validator replays every past line against the current card (`:597-619`);
  - an overclaim about drift between `lean_check` runs.
- **v3** made targeted fixes:
  - dropped the date rule;
  - stated the between-runs limit, with an advisory `--hash` sweep in `/theory status`;
  - no agent writes the sign-off fields;
  - glossary-agreed symbol substitution for the paper notation;
  - a validator check on the checklist marks;
  - a Coverage FAIL cannot be overridden;
  - the auditor computes the section 9 values independently;
  - calibration widened to seven cases, adding quantifier order and junk-value guard.

  v3 was not re-reviewed. It waits for the owner's approval before any implementation plan.
- **Cost:** three fable reviews, about 455k agent tokens and about 19 minutes of wall-clock.

## 14. ADR-0005 Task 1: validator rules (2026-10-14)

- `bin/blueprint_check.py`: a bound signature (`sha:` prefix, ASCII digits only), the checklist (marks, all `same` for FAITHFUL) and the audit report (place, name, newest, header match, coverage, verdict or a bound override). Every past `formalized` / `verified` line is replayed against the current card.
- **Reviews** (fable, blind; ADR-0002): red-team 60/100 (2 Critical, 2 High, 2 Medium, 2 Low); correctness 86/100 (1 High, 3 Medium, 4 Low). Both Criticals have named regression tests.
- **Fixed, each with a test that failed first:**
  - red-team #1 and #2: the checklist parser ignores comments and code fences, and only a `#`/`##` heading ends the section (`rv_checklist_in_comment_ignored`, `rv_checklist_in_fence_ignored`, `rv_subheading_does_not_end_checklist`);
  - red-team #3: a second checklist section is an error (`rv_second_checklist_rejected`);
  - red-team #4: a duplicated card or audit header field is an error (`rv_duplicate_card_field_rejected`, `rv_duplicate_audit_field_rejected`);
  - red-team #5: only tables headed `Part … Mark` count (`rv_later_table_not_checklist`);
  - red-team #6: the newest audit counts (`rv_newer_audit_wins`);
  - red-team #7: ASCII digits only (`rv_signature_ascii_digits_only`);
  - red-team #8 and correctness #6: an empty row is flagged (`rv_empty_row_flagged`);
  - correctness #1–#4: tests that bite (`rv_mark_vocabulary_enforced`, `rv_audit_node_checked`, `rv_audit_lean_checked`, `rv_audit_filename_checked`, `rv_checklist_no_rows_rejected`). A mutation run confirmed each rule's removal is caught;
  - correctness #8: a Coverage PENDING message (`rv_coverage_pending_message`).
- **Accepted:**
  - correctness #5: the PENDING-guard and locator-state branches change only the message, because the card still FAILs through the missing-file or field checks;
  - correctness #7: the `verified` replay cannot be isolated from `formalized`, because both lines cite the same card by design.
- **Suites:** blueprint 182/182, lean_check 199/199, tools 74/74.

## 15. ADR-0005 Task 2: card template, formalizer, /theory flow (2026-10-14)

- **The template:** the header comes first, with `Independent audit:`. Then the checklist (`Part … Mark`, five marks, the direction reminder), the worked instance with formalizer and auditor columns, the owner's notes, and an appendix A–E. The old sections 3, 5 and 8 are gone.
- **`/theory formalize`:** formalizer → statements check → back-translator writes the rows → auditor step 1 → three-way glossary diff → auditor step 2 (coverage) → owner marks and signs, without the audit verdict or its path → verdict compare (agree, override or fix) → statements report → `formalized` appended. `prove` appends `verified` without asking. `status` adds an advisory `--hash` sweep.
- **The formalizer:** resets the sign-off fields in place on any header rewrite; never refreshes a `sha:` prefix.
- **Found while writing the template:** `header_fields` read `**Key:**` lines inside HTML comments, so a commented example override could count. Fixed with `rv_override_in_comment_ignored` (RED→GREEN). The template's examples are now placeholders.
- **Reviews:**
  - header_fields fix (red-team + correctness, one agent): 88/100, no Critical or High;
  - flow docs (correctness): 70/100, 2 High, 3 Medium, 5 Low.
- **Fixed:**
  - docs H1: the auditor gets the node label, Lean name and SHA;
  - docs H2: the override and fix branches lead on to the statements check and the line (step 9);
  - docs M-a: same-day audits are `_2`, `_3`, never `_1`;
  - docs M-b: the override goes in the header block;
  - docs M-c: a stale "section 6";
  - Lows: the companion column is assigned, `<node file stem>` is used, the glossary-disagreement branch is resolved, a stale "at each approval" is gone, and the audit path is kept from the owner until they sign;
  - header-fields M2: a report with an unreadable Mode now competes as the newest, so a commented-out FAIL can no longer hide behind an older PASS (`rv_commented_report_header_not_skipped`, RED→GREEN).
- **Accepted:**
  - header-fields M1: `lean_check.card_fields` still reads raw lines. The plan keeps `lean_check.py` unchanged; the divergence fails closed (lean_check rejects a card with a commented example field before the real one); and the template puts its comment after the header. Added to the TODO backlog;
  - header-fields Lows: `_visible` CommonMark edge cases, which are contrived or fail closed. The inline-comment test documents behaviour and does not discriminate;
  - docs Low: the owner can still open the audit file in `checks/` before signing. That is the owner's own choice, and the path is not handed to them.
- **Suites:** blueprint 185/185, lean_check 204/204, tools 74/74. Agent lint PASS (40 files).

## 16. ADR-0005 Task 3: card-auditor and calibration (2026-10-14)

- **The agent:** `.claude/agents/card-auditor.md` (fable, Read and Write only). Step 1 is a blind map against nine failure patterns. Step 2 checks coverage of the checklist.
- **Calibration:** seven sealed cases, each compiled with `lean_run_code`. The answers were kept outside every repository, at a path no agent was given. One dispatch per case, through a general-purpose fable agent told to follow the agent file (the type was not yet registered).
- **Result:** 6/6 planted defects caught and named, and no false alarm on the faithful case. The bar was met on the first run; no revision was needed.
- **Cost:** about 95k tokens and 4 tool uses per case, 60–90 s each.
- **Record:** `quality_reports/calibration/2026-10-14_card-auditor/` (README, ANSWERS, cases, reports).
- **Limits:** seven short single-part cases; step 2 is not calibrated (the pilot exercises it).

## 17. ADR-0005 Task 4: pilot converted, audited and re-signed (2026-10-14)

- **The new validator copied into BDD:** it FAILed `prop:nstar-interior-ac` on both its `formalized` and `verified` lines with the re-sign message, as planned. That shows the replay works.
- **Formalize steps 3–6 on the unchanged statement file:**
  - the back-translator (fable, comment-stripped Lean only) wrote 31 checklist rows, its glossary and notes;
  - card-auditor step 1 (blind) returned FAITHFUL, with sanity values (1, 1, 1/4) → n\* = 1, V = −3/4 and (2, 4, 1) → n\* = 0, V = −2;
  - the three glossaries agreed, so Claude substituted symbols only;
  - auditor step 2: Coverage PASS (all seven `_stmt`s, no contradicting reading).
- **The owner** reviewed the checklist ("they all look the same to me"; Claude transcribed that as `same` on all 31 rows, and the notes say so) and the worked instance ("the values are the same"). The owner typed `Verdict: FAITHFUL` and `Signed off: CS 2026-10-14 sha:a6cb62a1734a`. The audit verdict was shown only after signing. It agreed.
- **Validator:** no errors, the same 34 pre-existing warnings. Fingerprint sweep: current. BDD `f779e92`; not pushed.
- **Cost:** back-translator 92k tokens, auditor 78k + 95k (two steps); owner time not recorded.
- **Final whole-branch review** (fable, fresh): 88/100, 0 Critical, 1 Important.
  - The Important: a checklist row cut off from its table by a blank or prose line was skipped, so FAITHFUL could pass over a `weaker` row. Fixed with `fr_detached_row_rejected` and `fr_detached_row_after_prose_rejected`, RED→GREEN.
  - Suites: blueprint 187/187, lean_check 204/204, tools 74/74. The BDD pilot passes the fixed validator.
  - Four Minors deferred (glossary-branch wording, a prose-quoted bold field fails closed, "line" vs "row" in a message, the pilot's blanket marks counting as owner-guided). The declined-to-judge items stand as logged residues.

## 18. `/tools sync-status` script (2026-10-14)

- `bin/sync_status.py` (stdlib, `py -I`) replaces the prose steps. Ruling: Python in `bin/` with tests rather than the plan's `.claude/skills/tools/sync-status.sh`, matching the repository's tool convention.
- It checks: commits not pushed or not pulled; branch, upstream, detached and no-remote states; LFS files in unpushed commits when the LFS pre-push hook does not run (this machine's `core.hooksPath`); plain blobs under an LFS rule (the earlier six-PDF case); DVC state; the backup.
- **Review** (red-team + correctness in one agent, on fable; ruling: one agent for a new single-file tool): 58/100, with 1 Critical, 3 High and some Medium findings. All fixed, each with a test that failed first:
  - nested `.gitattributes` (`ss_nested_gitattributes_seen`);
  - git-lfs absent → UNVERIFIED (`ss_lfs_cli_missing_unverified`);
  - hook comments ignored (`ss_hook_comment_not_counted`);
  - no remote, no upstream, unfetched upstream and detached HEAD are not "in sync" (`ss_no_remote_unverified`, `ss_remote_without_upstream_publish`, `ss_upstream_never_fetched_not_clean`, `ss_detached_head_not_clean`);
  - blob check batched into two git calls (BDD, 69 LFS files: 7 s);
  - rev-list failure → UNVERIFIED;
  - exit 1 and behind-only now tested (`ss_fail_main_exit_1`, `ss_behind_flags_pull`);
  - backup reported (`ss_backup_reported`);
  - remote names come from the branch config (slash-safe).
- **Accepted:** a `.dvc` file (not a folder) is skipped (Low); `[attr]` macro lines display oddly (Low).
- **Suite:** 22/22. Real repos: the workflow repo PASS; BDD UNVERIFIED (no `dvc` CLI); the Lean project PASS.

## 19. Track A step 3: `behavioral` overlay synced (2026-10-14)

- **Ruling:** a class-aware sync, not `git merge main`. The merge previewed 42 conflicts and would have carried about 150 of main's Class D files (session logs, reviews, plans, ADRs) into the template overlay. `sync_overlays.py` refuses to run without an `applied-micro` worktree, and that overlay stays frozen by plan. So a one-off scratch script applied the manifest rules instead:
  - Class A: copy where main differs;
  - delete only where main deleted the file (history-aware, which catches the 2026-09-16 hook prune);
  - Classes B, C and D untouched.
- **Result:** 62 Class A files copied (29 new, 33 updated) and 17 deleted. Five Class B files were merged three-way from the common base `5737307`, with each hunk resolved explicitly:
  - `verifier.md`: model `fable` from main, overlay superset elsewhere;
  - `quality.md`: overlay weights kept;
  - `workflow.md`: overlay rows, with the theory row updated per ADR-0004;
  - `review/SKILL.md`: overlay superset, `replicate_<lang>`;
  - `writer.md`: clean.
- **Gate** (plan: hooks load, the tool cycle survives):
  - all 10 registered hooks exist and run (rc 0 on a benign payload);
  - hook and bin suites pass, except `test_derive_lib`, which needs pytest, as on main;
  - agent lint PASS (48 files).
- Committed `behavioral` `ab9f5f0`, locally, in worktree `C:/Users/christina.sun/wt/crw-behavioral` (outside OneDrive). Not pushed.

## 20. Destructive-action guard: false-positive fix grew into a redesign (2026-10-14)

- **The TODO bug:** the fallback for commands `shlex` cannot parse blocked anything containing "git" plus a keyword such as `-f `, labelled it `git filter-repo`, and ignored the bypass.
- **Round 1:** a segment-wise fallback. Reviews: red-team 74, correctness 82. Found:
  - a backslash continuation fail-open;
  - the bypass not logged;
  - an older hole: on parsed commands only the first command of a chain was checked (`echo hi && git filter-repo` got through).
- **Round 2:** every command of a chain is checked; wrappers and git global options are normalized; heredoc bodies are data unless a shell reads them; the bypass covers only its own command. Reviews: red-team 62 (2 Critical: a quoted `<<` swallowing commands, `cat <<EOF | bash` unchecked), correctness 83.
- **Round 3:** quote-aware heredocs; a shell anywhere on the opener line; one per-command check across all three tiers with `cd` tracking; `env -u`, `--`, subshells, braces, `/usr/bin/git`, `git.exe`, glued and unknown git options, `+refspec`. Verification: 74, every earlier Critical and High resolved, plus one new High (`2>&1` split a command) and three Mediums.
- **Final pass after round 3** (the three-strikes limit, so no fourth review), each with a test that failed first:
  - redirects are defused before splitting;
  - quote state is carried across lines;
  - `cd` is tracked before the bypass check;
  - `py` joins the Tier-3 interpreters;
  - `heredoc_shell` is logged.
- **Evidence:**
  - 136/136 tests;
  - an audit-log replay over 1,570 unique commands against HEAD: 0 new blocks, 6 blocked→allowed, all HEAD false positives (heredoc data), each confirmed independently by two reviewers;
  - the other hook suites pass (except `test_derive_lib`, which needs pytest).
- **Accepted and documented** in the rule's Known limits: `$(...)`, backticks, `eval` and `sh -c` strings are not unpacked; nor is `python - <<EOF` calling subprocess; `sudo`, `timeout`, `nice` and `xargs` are not wrappers; the fallback's Tier 2 is fail-open.
- **TODO:** Windows shared-storage prefixes. Tier 2 is inert for OneDrive on this machine, and the scope needs the owner's decision.
- **Lows left:** `git push +main` with no remote allowed; `cp X .claude/settings.json.bak` false-blocks (parity); FPs from comments on the heredoc opener line (fail closed).
- **Note:** a reused scratch-file name once spliced stale code into the hook. It was caught at once by the test run, and the hook was restored from the pre-splice copy. Use unique scratch names.

## 21. Track A step 4: BDD's `.claude/` refreshed (2026-10-14)

- **Method:** a restore-point tag `pre-simplify-2026-10`, then a file-level refresh of `.claude/` from the `behavioral` overlay:
  - a differing file is replaced only if its exact content (blob) exists in the workflow repo's history, which means it is an untouched old upstream copy;
  - otherwise it is kept as a local customization.
- **Result:** 8 added, 50 replaced, 17 deleted (the pruned hooks). Kept: `.claude/references/journal-profiles.md` (the JEBO target) and `.claude/SESSION_REPORT.md`.
- **Sweep:** removed-hook names remain only as history ("former ... pruned", CHANGELOG), plus two stale live references (`protect-files.sh` in the destructive-actions rule and in the deep-audit table). Those were fixed on main (`3733b45`) and synced.
- **Diagnosis:** two BDD bin suites failed. The cause was the ADR-0005 `blueprint_check.py` copied in on 2026-10-14 without its updated tests. Confirmed by running the suites at HEAD with the refresh stashed: same failures. Fixed by bringing `bin/test_blueprint_check.py`, `bin/test_lean_check.py` and `templates/theory/` up to date (187/74/204).
- **Process slip:** `git stash` / `stash pop` during the diagnosis unstaged the refresh, so the first commit (`ef01e01`) held only 13 of its 80 files. It was caught by `git status` and amended before any push (`43ee165`). Lesson: use `stash pop --index`, or don't stash a staged change set.
- **Gate:** all 10 hooks exist and load; hook suites pass (except `test_derive_lib`, which needs pytest); bin suites pass; the blueprint validator is unchanged.
- `bdm_bic` is not on this machine (TODO).

## 22. Track A step 5: propagation tooling retired (2026-10-14)

- Deleted `.claude/skills/tools/propagate.py` and `sync_overlays.py`.
- Removed the `/tools propagate`, `sync-overlays` and `list-consumers` sections and their frontmatter mentions.
- Replaced CLAUDE.md's Cross-Repo Propagation section with a short "Overlays and consumer repos" note: the hand-sync rules by class, pointing at §19 and §21.
- Kept `.claude/file-classes.toml`, header reworded, as the reference for hand syncs.
- No consumers registry is tracked (`.claude/state/` holds none). The applied-micro overlay and the dormant consumers stay frozen.

## 23. `bdm_bic` cloned and refreshed (2026-10-14)

- **Clone:** the full clone failed with "connection was reset … early EOF" partway through the download. A `--depth 1` clone followed by `git fetch --deepen=100` twice got all 122 commits.
- **Checkout:** one file's path (`master_supporting_docs/theory/economical-writing-…-9780226448107.pdf`) is over Windows' 260-character limit inside OneDrive. Fixed with repo-local `core.longpaths true`.
- **Step 4 + 5:** restore tag `pre-simplify-2026-10`; 9 added, 50 replaced (all unmodified upstream copies), 24 deleted (pruned hooks, four rules consolidated upstream in March, `post-merge.sh`, the retired propagation tooling); `SESSION_REPORT.md` and `journal-profiles.html` kept. Gate: 10 hooks load, suites pass, agent lint PASS.
- **Identity slip:** the fresh clone had no repo-local identity, so the first commit carried the machine's global work address. It was caught before the push. The repo-local `user.name` / `user.email` and the three guard settings (repository class personal, approved remotes, expected email) were set to mirror BDD, and the commit was fixed with `--amend --reset-author --only`, leaving the staged files out (`2c10c3f`).
- **LFS:** 29 PDFs committed as plain blobs under the LFS rule were renormalized (`2920761`); all 29 pointers match their files. `git lfs push` ran first, as the LFS hook does not run here. Pushed; `sync_status` PASS.
- **BDD tag not pushed:** a new tag ref makes the guard scan all 376 commits, which hold 124 Office files committed long before the guards existed. The tag stays local; its commit `767f02e` is on GitHub.

## 24. BDD `/theory develop`: the seven conjecture claims (2026-10-14)

Each node got a theorist prove-or-refute pass (examples, counterexample search, exact checks, proof), then two blind fable proof-verifiers on the `verify-input` text alone. All 14 verifier runs were PASS.

| Node | Outcome | BDD commit |
|---|---|---|
| lem:var0 | holds as written; checked | a90b579 |
| prop:gap-closure | fails at n = 0 only (the residual factor is 1 for any variances) → conditional | 0b74460 |
| prop:gap-closure-pos | owner-approved repair: comparative statics for n ≥ 1; checked; cor:gap-rank repointed | 0b74460 |
| prop:seq-vs-commit-bias | holds as written; checked | 7e0d569 |
| prop:cogcons-wedge | holds; the flagged step b_t > 0 for t < T−1 is derived (the hypothesis forces γ < 1, plus a one-step deviation bound); checked | 75d75e1 |
| prop:commit-cogcons | compares the grid maximizer with the continuous n* (σ0² = σd² = 1, c = 25/324, T = 10: n* = 13/5, grid optimum 3) → conditional | b8c5829 |
| prop:commit-cogcons-grid | owner-approved repair (a): benchmark is the rational grid optimum; checked; both dependents repointed | b8c5829 |
| prop:commit-vs-seq-size | holds; prop:vol-commit-equiv is a mention, the dependency is -int; checked | 9b274ec |
| cor:gap-rank | holds on the repaired inputs; "every regime" read as the three regimes; checked | 38dd512 |

- **Validator:** PASS on 54 nodes, the first clean verdict for this blueprint.
- **Statuses:** 11 checked, 1 verified, 13 proved (variants, awaiting verification), 5 conditional, 5 refuted, 19 stated.
- **Paper follow-ups:** recorded on the TODO's paper-wording item. Proposed variant nodes are recorded in each node's run comment; none was created.
- **Hygiene:** parallel theorists shared the repo. One early pass ran `git stash` on its own; nothing was lost (no stash left, the other node untouched). Every later dispatch forbade stash, restore and reset.
- **Environment:** checks that need SymPy, NumPy or Z3 ran from BDD's own `.venv` after the first round; the first round used a temporary venv. BDD's `requirements.txt` and its `.venv` describe different environments (analysis vs theory); this is now an owner question on the TODO.
- **Cost:** about 30 agent runs (theorists about 120–240k tokens each, verifiers about 80–135k).

## 25. BDD: the 13 `proved` variants verified (2026-10-15)

- **Outcome:** no BDD node is left at `proved`. Statuses: 24 checked, 1 verified, 5 conditional, 8 refuted, 1 superseded, 19 stated (58 nodes, validator PASS). BDD pushed to `7f6b053`; later commits through `201c9d5` are local.
- **Checked as written:** `martingale-beta-bernoulli`, `cogcons-wedge-abs-belief-cost`, `-discounting`, `-prior-anchored-forecast`, `-no-objective`.
- **Checked after a self-contained rewrite:** `martingale-no-objective`, `vol-commit-equiv-int-tie-continue`, `band-tie-continue` (its first `checked` was withdrawn), `cogcons-wedge-tie-continue` (on-path reachability written out).
- **Uniform standard (owner's note):** verifiers had judged "Step N of another node's proof" citations unevenly (one FAIL, one split, one double PASS after rebuilding the step). Rule: such a step is a FAIL even when rebuildable. proof-verifier checklist item 11 and a line in theorist.md (workflow `4a14740`, copied to BDD `3b6c455`). A sweep of every checked/proved node found only `band-tie-continue`. TODO backlog: a `verify-input` refusal for it.
- **Refuted, then repaired by owner choice:** `cogcons-wedge-beta-bernoulli` and `-threshold-loss` claimed an on-path wedge but proved only unconditional probabilities; with lopsided priors, or μ₀ far from w, the optimal rule stops before T−1 and the equivalence holds. Repairs: a cap c < G, and |μ₀ − w| < ρ(c). `-location-loss` asserted an optimal report that need not exist (ℓ = 1 + sin d + eᵈ); repaired to the value of the reporting problem. All three repairs checked.
- **Superseded:** `vol-commit-equiv-int-det-variance` ended with an unproved and universally false Beta–Bernoulli remark; successor `-2` drops it (and an unproved comparison) and is checked.
- **Parent claims cleared:** `prop:cogcons-wedge`'s proof already carries the on-path argument (Steps 4–5(b)). `-no-objective`'s closing clause names the superseded `lem:martingale`; the dependency graph confirms the claim with `lem:martingale-horizon`.
- **Paper wording:** say `lem:martingale-horizon` where the text names `lem:martingale`; the Beta–Bernoulli caveat needs the cost cap; the threshold-loss wedge needs μ₀ near w.
- **Cost:** about 50 agent runs (verifiers about 90–125k tokens each, theorists about 105–205k).

## 26. Instruction budget under 150k (2026-10-19)

- **Problem:** session start warned 23 instruction files totalled 163.2k chars, over Claude Code's 150k limit.
- **Change:** `data-version-control.md` path-scoped (data, DVC, LFS and setup files, `.gitignore`); the primary-source filter stack and the destructive guard's Tier 3 and chain-parsing detail moved verbatim to `.claude/references/primary-source-filter-stack.md` and `destructive-actions-detail.md`, with summaries and pointers left in the rules. Always-loaded total about 139k.
- **Review (`/review-build`):** consistency 88, correctness 92, bloat 60. Fixed: `.gitignore` glob; Windows OneDrive caveat and unparseable fail-open restored to the rule summaries; telemetry "fail-open" wording; filter order documented as the code runs it (`primary_source_lib.py`, decomposition before sentence-start); `protect-files.py` matcher is `Edit|Write|MultiEdit`; `Class: A` headers and self-contained intros on both references. Accepted: consistency F4 (Bash-only DVC work does not trigger the path scope; CLAUDE.md and the `tools` skill point to the rule), correctness 4–5 (shorthand, CRLF normalised by autocrlf). Bloat findings 1–18 (about 43k further) are a separate decision for the owner.
- **Cost:** 3 fable reviewers, about 439k agent tokens, about 8.5 min wall-clock (parallel); findings: 0 Critical/High on the change, 3 Medium and 6 Low across consistency and correctness.

## 27. Instruction budget r2: all 18 bloat findings applied (2026-10-19)

- **Outcome:** always-loaded repo instructions 121.4k -> 85.4k chars (with the owner's 17.9k user-scope rules, about 103k of the 150k limit). Sections moved verbatim to 10 new references (`adversarial-default-detail`, `aea-citation-style`, `decision-log-detail`, `derive-lookup-table`, `independent-review-detail`, `no-assumptions-examples`, `orchestration-loop`, `quality-deduction-tables`, `review-plan-lifecycle`, `revision-protocol`) and 3 extended ones; `single-source-of-truth.md` path-scoped; CLAUDE.md storage, overlay and getting-started sections shortened (hand-sync procedure moved into the `file-classes.toml` header, `/discover` step into README Quick Start); stale "Stop hook blocks causal claims" removed from CLAUDE.md (hook pruned in 860fa14).
- **Where the reviewer's duplication claims failed:** orchestrator.md, the critic agents, revise skill and the READMEs were incomplete or divergent copies, so content moved to references, not deleted. READMEs under `quality_reports/` and `decisions/` are Class D, so references (Class A) took the content. `orchestration-loop.md` and `quality-deduction-tables.md` are Class B: the behavioral overlay has its own dispatch rows, pre-registration gate and deduction rows.
- **Review r2:** consistency 87, correctness 92 (0 lines lost across 11 rule/reference pairs), bloat 91. Fixed: Class B headers on the two overlay references; Overleaf note (path scopes do not reach files outside the repo); AEA punctuation line kept inline; UNVERIFIED and diagnosis results in the ledger summary; pruned hook names kept; header wording and deixis in references; `cd X &&` section moved (covered by the chains summary); stale "(UAB)". Accepted: consistency 5 (ledger rows on the moved rules go stale by letter only; moves are content-preserving), correctness 7 (declared duplicates). Remaining bloat residue (about 4k: rationale paragraphs, cross-reference recaps) left as diminishing returns.
- **Open, owner decision:** deduction values differ between `quality-deduction-tables.md` (from quality.md) and the critic agents: compile failure -100 vs writer-critic -20 (a non-compiling paper can score 80 and pass the commit gate), script failure -100 vs coder-critic -25, hedging -3 vs -5, slide count -10 vs -15. Also orchestrator.md escalation routing differs from agents.md §3. Both predate this change.
- **Cost:** 3 opus workers (about 490k tokens) + 3 fable reviewers (about 520k tokens), about 25 min wall-clock.

## 28. Deduction tables: critic agent files authoritative (2026-10-19)

- **Owner decision:** each critic's agent file holds the authoritative deduction table; failure to compile or run costs -100 (was -20 writer-critic, -25 coder-critic, -20 storyteller-critic, so a non-compiling paper could score 80 and pass the commit gate). Agent values kept where they differed (hedging -5, talk length -15).
- **Rows added to agents** that existed only in quality.md § 3: writer-critic (typo in equation, missing figure/table at path, long lines); coder-critic (Stata `esttab`/`outreg2` output); storyteller-critic (talk-only result, overfull hbox, dense slide). `quality-deduction-tables.md` is now an index; `quality.md` § 3 names the agent file as authoritative. Behavioral's three critic files match main, so no overlay conflict; behavioral's own quality.md § 3 rows are reconciled by hand at its next sync (Class B).
- No independent review: mechanical edit of values the owner chose (docs-class change, advisory).
