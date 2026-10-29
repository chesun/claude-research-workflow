# Session Log: 2026-10-22 — Orientation, BDD handover plan, record backlog

## 1. Orientation survey

- **Read:** `TODO.md`, the ADR index, the plans index and the 2026-09/10 plan headers, the previous log `2026-10-11_hook-launcher-fix-and-theory-brainstorm.md` (§1–§30), the infra-survey synthesis and its review, `README.md`, `CHANGELOG.md`, the branches and worktrees, and auto-memory.
- **Brief:** `quality_reports/reviews/2026-10-22_repo-catch-up-survey.md`. It supersedes the 2026-10-11 survey, which was moved to `reviews/archive/`. The reviews index and the one session-log link to it were updated.
- **Git state:** `main` equals `origin/main` at `7ac60cd`, with a clean tree. `behavioral` is at `2c816cf` and pushed.
- **Memory corrected:** the user memory on the work-machine context, with its index line, still described the Copilot / enterprise-only era. They now match the 2026-09-15 reclassing as a personal repo.

## 2. BDD handover plan

- **Owner request:** a plan in BDD so that a session opened there can carry on.
- **New since this repo's TODO** (BDD git, 2026-10-15 to 10-19):
  - the paper-v2 cross-check, theorist-critic 3/100 with 16 rows;
  - the 27-entry edit list, critic 87/100;
  - the edits, applied to the two v2 `.tex` files and **uncommitted**.
- **Written:** BDD `quality_reports/plans/2026-10-22_handover-theory-v2-to-jebo.md`. It holds:
  - the state, checked today (validator `PASS (58 nodes)`, `git status`);
  - a read-first list;
  - four workstreams:
    1. compile on the Mac, `/theory review`, commit, owner push and promotion;
    2. the owner decisions left open by the 2026-09-14 synthesis;
    3. the JEBO draft;
    4. optional further Lean work.
- **Also edited:** BDD's plans index, and a pointer line in its TODO.
- **Left uncommitted in BDD:** a commit there would sit beside the in-flight `.tex` edits, and the owner did not ask for one. The employer-name grep on the three BDD files is clean.
- **Found:** BDD's `.claude/` predates the 2026-10-19 instruction-budget changes, and `.claude/references/` lacks the new files. Added to this repo's TODO Up Next, together with `bdm_bic`.

## 3. Record backlog cleared (the drift listed in the survey's § 4)

- **`CHANGELOG.md` [Unreleased]:**
  - Added: the Lean lane, the theory tooling, ADR-0002, ADR-0003, `sync-status` and the venv default.
  - Changed: the guard redesign, the instruction budget, the authoritative deduction tables and escalation routing, and hand-sync.
  - Removed: the 10 pruned hooks (list from `git log --diff-filter=D`, commit `860fa14`), the propagation tooling (`bc57b16`) and the shell hooks.
  - Fixed: the hook launcher.
- **`README.md`:**
  - counts: 22 agents, 18 skills, 29 rules;
  - overlay sync is by hand;
  - Context Survival no longer names the pruned hooks;
  - the hooks list is the 10 registered in `.claude/settings.json`;
  - the `/tools` subcommands follow its `SKILL.md`.
- **Plan statuses closed:** modernize (Track A), port-mandatory-review, infra survey, and context-tightening. Lever 1 of context-tightening was done 2026-05-28, and Levers 2–3 by the 2026-10-19 work (§26–§27 of the previous log). The plans index gains a 2026-09 section.
- **`TODO.md`:**
  - Track A moved to Done;
  - the BDD paper item now points at the handover plan;
  - the context-tightening backlog item is closed;
  - Done pruned to 10 per `todo-tracking.md`. The 18 older entries are in the session logs and git.
- **`decisions/README.md`:** two pending owner decisions listed, the scope of the Windows guard and whether to keep the card-auditor.
- **No independent review:** these are status and record edits to docs (advisory class, ADR-0002), with every fact taken from git or the logs.

## 4. BDD v2 pair compiled on the laptop

- **Correction from the owner (via a side agent):** the plan's "compile on the Mac" step could not work, since the 27 edits are uncommitted here. Step 1 and this repo's TODO now say to compile on the laptop (`15b7cfe`).
- **TeX Live 2026** installed by the owner at `C:\texlive\2026`. It is not on PATH in shells opened before the install.
- **Result:** three `pdflatex` passes from `theory/`, 0 errors, 0 undefined references, 52 pages. Appendix A and the band figure (Figure 3) render.
- **Carried into the `/theory review` round:** the Figure 3 legend covers the `+√b1` label; four overfull hboxes over 1pt (28, 73, 1.4 and 70pt), all in edited lines. Locations are in BDD's handover plan, step 1. Not fixed here: the plan reserves edits to the pair for compile errors.
- **Owner OK to push.** On BDD branch `theory-v2-edits`:
  - `5289b9d`: the two `.tex` files and the recompiled PDF;
  - `53e718f`: the handover plan, its index line and the TODO pointer.
  - The branch was pushed, and the pre-push guard passed both commits. `main` is untouched at `6017123`.
- **The handover plan gains a "Pick up here" block.** It covers switching to the branch, and says step 1 is done and step 2 is next. Steps 3–4 now commit on the branch, then merge to `main` with the owner's OK.

## 5. BDD and `bdm_bic` synced with the instruction-budget changes (2026-10-28)

- **TODO first:** the BDD v2 item now records `a93f41b` (review round 86 → 99/100 PASS, seven fixes), pushed on `theory-v2-edits`. What remains is the owner's merge, push and sign-off.
- **Method (§21 of the 2026-10-11 log):** each project's `.claude/` was compared file by file with `behavioral` `2c816cf`, skipping `.claude/state/` (Class D).
  - A missing file is added.
  - A file that differs is replaced only when the project's blob appears in the workflow repo's history, which marks it as an untouched upstream copy. Otherwise it is kept.
  - A file the project has but `behavioral` lacks is deleted only when it is an upstream copy of a path upstream has deleted.
  - Scratch scripts: `sync_plan.py` (dry run), `sync_apply.py` (copy or `git rm`, then stage) and `sync_gate.py`.
- **Where:**
  - BDD is on a new branch, `claude-sync-2026-10-28`, cut from BDD `main` (`6017123`) in the worktree `~/wt/bdd-claude-sync`, outside OneDrive. This left the checked-out `theory-v2-edits` alone, and the two branches touch no file in common.
  - `bdm_bic` was changed in its own tree, on `main`.
- **Result:**
  - BDD: 12 added, 27 replaced. Kept: the JEBO `references/journal-profiles.md` and `SESSION_REPORT.md`, as in §21. One project-owned (Class D) fix in `CLAUDE.md` line 156: the deduction-table pointer, in main's wording.
  - `bdm_bic`: 12 added, 29 replaced, 1 deleted. The extra two replaced files are `proof-verifier.md` and `theorist.md`, from the 2026-10-15 change. The deleted file is `references/journal-profiles.html`, stale HTML upstream removed in `43545d8`. Kept: `SESSION_REPORT.md`. Its `CLAUDE.md` holds none of the stale text.
  - Re-running the classifier on each staged index leaves only the keeps.
- **Gate:**
  - Always-loaded project instructions: BDD 153.2k → 94.2k characters, `bdm_bic` 148.4k → 89.4k. With the 26.5k of user-scope rules that is about 121k and 116k, against the 150k limit.
  - All 10 registered hooks are present on disk.
  - Agent lint PASS (48 files) in both.
  - All seven hook suites exit 0 in both (guard 136, review receipt 45, normdiff 58, citation existence 26). `test_derive_lib` prints nothing, as on main.
  - Unresolved reference pointers: 4, the same four as on the workflow's main. They are `applied-micro`-only references, so not a regression.
- **Left behind:** running `test_derive_lib` created a `.pytest_cache` folder in the BDD worktree and in `bdm_bic`. It cannot be read or removed from the session, git cannot read it either, and it is not gitignored, so the owner deletes it by hand.
- **Not independently reviewed:** these are file copies of content reviewed on main (r2) and synced to `behavioral`, plus one pointer line.
- **Committed with the owner's OK:** BDD `5dd2de7` on `claude-sync-2026-10-28`, and `bdm_bic` `a9f0023` on `main`. Neither is pushed or merged yet.
  - The owner's BDD session, on `theory-v2-edits`, still warned at 184.2k. That is expected: a session loads the branch checked out in the folder.
  - Proposed: merge the sync branch into `theory-v2-edits` with a merge commit and no rebase, then push.
- **Merged and pushed (owner's OK):** BDD `claude-sync-2026-10-28` merged into `theory-v2-edits` as `50f61f1`, with a merge commit and no conflicts. The BDD folder now loads 94.2k characters of project instructions.
  - Pushed: BDD `theory-v2-edits` (`a93f41b..50f61f1`) and `bdm_bic` `main` (`2920761..a9f0023`). The pre-push guard passed every commit.
  - The worktree and its local branch were removed on the owner's request (branch was `5dd2de7`, merged). Left: an unreadable `.pytest_cache` in `~/wt/bdd-claude-sync` and in `bdm_bic`, for the owner to delete in Explorer.

## 6. `verify-input` refuses cross-node proof citations (2026-10-28)

- **Owner request:** the backlog item from 2026-10-15. On that date, verifiers judged citations like "Step 2 of lem:x" unevenly: one passed, one failed, two passed after rebuilding the step. Item 11 in `proof-verifier.md` already made such a step a FAIL. This change refuses it in the tool, before any verifier runs.
- **Design:** the BDD verifier reports set the line between the two cases.
  - Refused: "Step N of <label>" and "proof of <label>". These point into a proof the verifier never sees.
  - Allowed: "part 1 of lem:martingale-horizon" and "Part (2) of prop:cogcons-wedge". These cite parts of a statement, which the verifier is shown, and they passed legitimately.
  - So the check covers step references (`of` or `in`, with an optional "the proof of"), "proof(s) of/for <label>" and "<label>'s proof". It runs on the proof after comments are stripped, and the node's own label is exempt.
- **Tests first:** 17 refusal cases failed before the change; with it, `test_blueprint_tools` is 97/97. The other bin suites are unchanged (blueprint_check 187, lean_check 208, agent_lint 64, sync_status 22).
- **Live check:** across BDD's 58 nodes, only `var:band-gamma-zero` is flagged. It is `refuted`, so `verify-input` never runs on it. There are no false positives. The first versions of the three 2026-10-15 variants are each caught: `var:band-tie-continue`, `var:martingale-no-objective` and `var:vol-commit-equiv-int-tie-continue`.
- **Docs:** the `/theory` SKILL verify refusal list, one clause in the `theorist.md` "stands on its own" bullet, the CHANGELOG [Unreleased] Added, and the TODO backlog item removed.
- **Review (ADR-0002):** red-team and correctness lenses, on fable, dispatched in parallel.
- **Review round 1:** red-team 68/100 (10 findings, 3 High); correctness 88/100 (6 WEAK, none High). The reports are `quality_reports/reviews/archive/2026-10-28_verify-input-cross-proof_{red-team,correctness}_review.md`.
- **Resolutions:**
  - **Fixed:**
    - RT1 High, ReDoS. Confirmed: about 4× slower per 4 extra characters. Items and separators now cannot overlap: an item is a number, a roman numeral, one letter, a number word or a bracketed tag, and "to"/"and" need spaces around them. "step " + "to"×4000 now runs in about 0 s; 9 more adversarial inputs and the red team's `redos.py` all run in milliseconds. Pinned by the `xp_linear_on_adversarial_text` check.
    - RT4 emphasis, RT6 label wrappers and RT8 exotic whitespace: a scanning view drops `*`, `_`, braces, brackets, LaTeX macros, `\,` and zero-width spaces.
    - RT5 / CO1 unnumbered steps and cases: a qualifier word is accepted ("final", "base", "induction", "each"…), and Case and Subcase are covered.
    - RT7: "argument/derivation", "given/used/written", "for/in/as", and "Lemma lem:x".
    - CO3: "AND" matches in any case.
    - CO4: "proofs of lem:b and lem:c" now reports every listed label.
    - CO5: the first phrase is chosen in text order.
    - CO2 / RT9a, the definition-steps false positive: `verify_input` skips definition and assumption labels, which have no proof.
    - CO6 / RT10: regression tests for each of these.
  - **Declined: RT2, the comma form.** It is what the corpus uses for a proof's *own* step. `cor-gap-rank.md:51` reads "(def:voluntary-cogcons, Step 1(b))", where the definition has no steps and Step 1(b) is the node's own. Pinned allowed by `xp_ok_comma_own_step`.
  - **Accepted as a known limit:**
    - RT3, pronoun references ("its Step 1(ii)"), now documented in the code comment and in SKILL.md. The verifiers' item 11 still applies.
    - Claim references: "the claim of lem:x" usually means its statement.
    - RT9b, contrastive remarks ("Unlike the proof of lem:b"): these are refused, and the message now names the HTML-comment escape.
- **Found while fixing:** my own extension to a bare "step of <label>" flagged a live `checked` node. `var:cogcons-wedge-no-objective` frames its proof as "the $T-1$ step of prop:cogcons-wedge … re-derived", and that proof passed blind verification. A step or case now needs a number or a qualifier word, pinned allowed by `xp_ok_framing_step`.
  - Live scan: 2 refuted variants flagged, no checked or proved node. The three 2026-10-15 originals are still caught.
  - Tests: 126/126, with 52 cross-proof checks.
- **For BDD (not this change):** the red team found a genuine cross-proof pointer in the `checked` node `lem:band`. Line 33 calls the variance identity "its Step 1(ii)", meaning lem:martingale-horizon's proof; it is the pronoun form, which the tool does not catch. Raise with the owner.
- **The fix changed the design**, so review round 2 runs with fresh lenses.
- **Review round 2:** red-team 87/100 and correctness 92/100. Neither has a Critical or High finding, and both confirm every round-1 fix and both declines.
- **Round-2 resolutions:**
  - **Fixed:**
    - CO1: a list tail now needs its "and", so a bare comma no longer pulls in a label (pinned by `xp_ok_comma_not_list`).
    - CO2: a label that is not a node gets its own message ("no node has that label"), not a claim about its statement.
    - CO3 / RT1–RT5: possessive step, derivation and plural ("lem:b's Step 2", "lem:b's proofs"); the bare plural "the steps of"; ordinals ("fourth", "2nd", "penultimate", "next"); a qualifier with a count ("final two steps"); "through"; `$2$`; `\(lem:b\)`; "the lemma lem:b". 13 new refusal checks.
    - CO4: `xp_bare_step` is renamed `xp_each_step`, and the timing check now also asserts that a reference after the adversarial text is found.
    - RT9: the code comment lists every known limit, and the docstring no longer claims more than a floor.
  - **Declined:**
    - "Step 2 from lem:b": "from" reads as "derived from", for example "(Step 2 from lem:b)".
    - Bare plural "the cases of": a statement can have cases.
  - **Accepted, documented in the code comment:**
    - RT6: other nouns, words merged by a zero-width space, intra-word emphasis.
    - RT7: a lone-letter time index ("step t in lem:x").
    - RT8: statement cases; escape with "case 2 of the statement of lem:x".
    - A latent false positive with no live instance: "the proof as lem:b states".
- **Final state:** `test_blueprint_tools` 141/141 (67 cross-proof checks). The other bin suites are unchanged.
  - Live: 2 refuted variants flagged, no checked or proved node. The three 2026-10-15 originals are caught.
  - Timing: worst 102 ms on the red team's 100 KB shapes.
  - The round-1 reports were superseded and archived. The r2 reports are the receipts.
- **Cost:** 4 lenses on fable, about 565k agent tokens and 54 min of agent wall-clock. Findings: High 3 and Medium 4 in round 1; Medium 3 in round 2; the rest Low.
- **Synced and pushed (2026-10-29):** Class A copies, each byte-identical to `0faab45`, and each target blob matched main's previous version, so there was no local customization to keep.
  - `behavioral` `cacb58d`: four files; 141 tests pass. `REVIEW_WAIVE=1`, since the code is unchanged from the version reviewed on main.
  - BDD `theory-v2-edits` `9685b8e`: four files; `test_blueprint_tools` 141 and `test_blueprint_check` 187 pass.
  - `bdm_bic` `93de622`: the theory skill and `theorist.md` only; it has no `bin/` or `theory/`.
  - Next, in BDD, by the owner: rewrite `lem:band`'s "its Step 1(ii)" step.

## 7. Proof-rewrite route documented; voice preservation planned (2026-10-29)

- **From a BDD side agent (owner relayed it):** rewriting `lem:band` (checked) by logging `checked -> proved` made the validator refuse re-verification.
  - Confirmed in `bin/blueprint_check.py:748-757`: `-> checked` is compared with the hash of the last upward move to `proved`.
  - Walked both routes in a temporary blueprint (scratchpad `reprove/route.py`): `checked -> proved -> checked` FAILs; `checked -> survived-search -> proved -> checked` PASSes.
  - Documented the second route in the `/theory` skill (§ `node`), `theorist.md` and the node template; docs only, suites unchanged (187, 141, 64, 208; agent lint PASS).
  - The validator message change goes with the `COMMENT_RE` backlog fix. Copying the docs downstream is queued in TODO, BDD after the owner's session.
- **Voice preservation:** owner answers, 2026-10-29:
  - corpus: the JMP draft plus more of their own papers to come, and other authors' papers as style models;
  - AI-assisted text exists in later drafts;
  - one author profile, kept private.
  - Correction: the "July 2023" draft is dated 24 July 2025 on its title page (misread filename). Corpus confirmation is pending.
  - Plan v1 `quality_reports/plans/2026-10-29_voice-preservation.md`, out for fit-for-purpose and efficiency reviews.
- **Plan v1 reviews:** fit-for-purpose 72 (3 High, 5 Medium, 4 Low), efficiency 80 (1 High, 3 Medium, 4 Low). About 247k agent tokens, 6 min.
  - All adopted in v2 except one. Declined: "no LaTeX here, so `pdftotext` is unavailable", from a stale memory note (TeX Live 2026 installed 2026-10-22; `pdftotext` ran on the corpus PDF). The note is corrected.
  - Main changes: A4 rebuilt; a standing privacy rule; the Backlog closure made true; the sync list corrected; `bin/voice_features.py` deferred; one schema home.
  - Plan v2 awaits owner approval and corpus confirmation.
- **Owner, 2026-10-29:** commit and push automatically at checkpoints (saved to memory). The July 2025 draft was written with ChatGPT help, so the corpus is:
  - the parts of it the owner declares their own (which parts is pending);
  - older unaided writing, to be supplied.

  Plan v2 approved; the template part goes ahead now. Checkpoint `c8ad95e` pushed.
- **Template part built (deliverables 1–6):**
  - new files: ADR-0006; `.claude/references/voice-profile.md`, the single home of the schema, the carve-out list, the floor and the privacy rule; `/voice-profile` (build, audit, status);
  - `anti-ai-prose.md`: § Register profiles, plus the R1/L3/L4 field conventions;
  - wiring: `writer` (voice step), `writer-critic` (advisory Voice conformance; Cochrane item 8 carve-out; profile-aware deductions), `storyteller-critic`, `/humanize`, `/write` and `/review` (the dispatcher passes the profile path, since `writer-critic` has no shell);
  - CLAUDE.md and `docs/reference/skills.md` rows.

  Agent lint PASS (41 files). Reviews running: correctness (docs), and consistency + bloat (rule).
- **Durable home** (a side agent's note, owner agreed): the profile lived only on this laptop, and a missing profile was skipped silently.
  - With the owner's explicit OK, created the private repo `chesun/voice-profile` via the GitHub API and cloned it to `~/.claude/voice`, with the three guard settings and the personal identity set. The initial commit was pushed.
  - Wired in: the reference, ADR-0006 and `/voice-profile` (build pushes; status checks the clone).
  - A missing profile is now reported ("Voice: no profile at <path>").
- **Reviews of the template part:**
  - **Rule, consistency + bloat 86.** Fixed: the leftover rename in `storyteller.md:64` and `docs/concepts/upstream-differences.md:126`; R1/L3/L4 cells point to § Register profiles; the cross-reference; the L3 attribution. Kept: `CHANGELOG.md:99` (a dated release record).
  - **Docs, correctness 74.** All fixed:
    - High: `/write` and `/humanize` have no shell to resolve the path. Agents with a shell resolve it themselves, and `/review` passes it to `writer-critic`.
    - Mediums: the profile reached slides through `/humanize` (now papers only); `/write` passed the path to a `writer-critic` it never dispatches.
    - Lows: the floor pointer in `writer.md`; the audit report's score header; R4 says stacks are still flagged; `signature_vocab` split into phrase and count; the ADR's reason for advisory-only.
  - No second cycle: the fixes change wiring, not the design.
  - Cost: two agents, about 295k tokens, 8 min.
- **Slides (owner):** the owner asked why slides were excluded, and will supply decks made by them.
  - The paper profile is not applied to slides (its prose rhythm does not fit a deck). A separate `slides.md` is added instead, with its own schema, per ADR-0007, which supersedes ADR-0006 item 6's papers-only scope.
  - Wired into `storyteller`, `storyteller-critic`, `/talk`, `/humanize` and `/voice-profile build --slides`. The private repo now ignores PowerPoint originals (`3859a13`).
  - **Review, correctness 86 (3 Medium, 6 Low).** Fixed:
    - the resolve line now names both files;
    - the gitignore wording agrees;
    - the PowerPoint recipe keeps titles, bullets and the presentation order (`p:sldIdLst`);
    - the critics' "none passed" line;
    - dispatchers pass a missing-file line;
    - the `within-deck` value;
    - `audit` infers the register from the path;
    - the rule cites ADR-0007.
  - Accepted:
    - #4: the carve-out sparing has no effect against the slide table today, but is harmless and works if rows are added;
    - #7: ADR-0006 item 1 stands as the location and privacy decision, and a Decided ADR is not edited.
  - The PowerPoint recipe is untested until the owner's first deck arrives.
