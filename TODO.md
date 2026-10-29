# TODO — claude-research-workflow

Last updated: 2026-10-29

Project-wide tracker per `.claude/rules/todo-tracking.md`. Details live in plans and session logs; this file tracks what is left.

## Active (doing now)


## Up Next

- [ ] **Copy the proof-rewrite route docs to `behavioral`, BDD and `bdm_bic`** once committed here (Class A: `.claude/skills/theory/SKILL.md`, `.claude/agents/theorist.md`, `templates/theory/blueprint-node.md`; `bdm_bic` has no template). In BDD, wait until the owner's `lem:band` session is committed.
- [ ] **BDD `lem:band` (checked) points into another node's proof** (red-team r1, 2026-10-28). Line 33 calls the variance identity "its Step 1(ii)", which is a step of lem:martingale-horizon's proof. This is the pronoun form, which the tool does not catch. Owner: rewrite the step from the statement and re-verify, or accept it.
- [ ] **card-auditor review point (ADR-0005 item 3):** after five audited nodes, count the auditor's catches and false alarms in the session log; the owner decides whether it stays. Audited so far: 1 (`prop:nstar-interior-ac`, 2026-10-14, FAITHFUL, agreed with the owner).
- [ ] **Voice preservation** (the committed next build from the 2026-09-22 infra survey): two per-paradigm voice profiles; needs the owner's exemplar papers. Folds in the anti-AI-prose academic carve-outs (Backlog).

## Waiting On

- [ ] **Mac worktrees** (owner, on the Mac) — the `beh` and `wt-behavioral` worktree entries were removed from `.git/worktrees/` on 2026-10-19 (stale here; git could not delete the folders itself). If those worktrees still exist on the Mac, run `git worktree repair` inside each, or `git worktree prune` if they are gone.
- [ ] **Model-routing experiment read-out** (ADR-0003/0004) — waiting on the voice-preservation build, which ADR-0003 names as the revisit point. Pilot evidence so far: verifier fable vs opus near-identical; opus slightly stricter in calibration round 1 and about twice as fast (session log 2026-10-11 §6). Revisit the `writer` exception after the voice build. Per-review severity counts and fix rounds keep accumulating in the session logs (2026-10-14: §13–§17, all reviewers on fable; no new fable-vs-opus pair).

- [ ] **BDD theory v2 pair: owner merge and sign-off.** The BDD branch `theory-v2-edits` is reviewed, fixed and pushed:
  - `5289b9d`: the 27 edits;
  - `53e718f`: the handover docs;
  - `a93f41b` (2026-10-22): the review round, theorist-critic 86 → 99/100 PASS, seven fixes, 0 overfull hboxes, 53 pages.

  Next, all with the owner: merge the branch into BDD `main` (no rebase), push, read the compiled pair and promote v2 over the canonical filenames. Tracked in BDD's handover plan `quality_reports/plans/2026-10-22_handover-theory-v2-to-jebo.md`, Workstream 1 steps 4–5.
- [ ] **Work-repo fixes** (in a session opened in the consulting repo; prompt given 2026-10-11): guard launchers that trust the Store stub; recognising the `personal` repo class. Pushing from this machine depends on the second.
- [ ] **BDD `data/PROVENANCE.md` backfill** — IRB, fielding dates, PII status and authorized users need facts only Christina has.
- [ ] **csac2026 year-specific CLAUDE.md fields** — fill when the 2026 survey specifics are known.

## Backlog

- [ ] **Destructive guard: Windows shared-storage prefixes** — `_shared_prefixes()` lists macOS mount points only, so on this Windows machine `rm -rf` / `find -delete` inside OneDrive or Dropbox folders is not blocked (red-team, 2026-10-14). Adding `%OneDrive%`, `%OneDriveCommercial%` and `~/Dropbox` would also block routine scratch deletes inside repos that live in OneDrive; decide the scope first. ADR-0002 review.
- [ ] **Unclosed `<!--` or code fence in a card** (lean_check review M1, 2026-10-14): `blueprint_check.COMMENT_RE` needs the closing `-->`, so fields after an unclosed comment are still read, while a renderer hides them. Both checkers agree; the owner signs in a raw editor, so the impact is limited. The fix (blank an unclosed comment or fence to the end of the file) must not change node hashing, which also uses `COMMENT_RE`. ADR-0002 review. In the same change, make the "proof changed after it was logged" message name the route (down to `survived-search`, not `proved`).
- [ ] **Review gate: accept directory targets** — `review-receipt-check.py` matches `**Target:**` by exact path or unique basename only, so files inside a reviewed directory (e.g. `bin/fixtures/lean_check/lean-toolchain`) need a waiver (used once, 2026-10-12). Needs an ADR-0002 review.

- [ ] **lean_check trusted harness** (deferred 2026-10-12, owner's middle path): build the Challenge in an owner-controlled project with its own Mathlib, so the formalizer's lakefile/manifest/folders cannot matter; cap `set_option` resource values. Revisit if the pilot or later work shows the need.

- [ ] **Destructive-action guard on Windows OneDrive** — hardening SHELVED by the owner 2026-10-11 on branch `guard-windows-shared` (`d6d84c2`) after 3 review cycles. Four merge-blockers are listed in that branch's `quality_reports/reviews/2026-10-11_guard-windows-shared-r3_*`. Until then, `main`'s guard does not path-gate deletes inside OneDrive on Windows.
- [ ] **Bulk LFS (+ selective DVC) migration** of the remaining research repos (ADR-0001: GO, forward-only, no history rewrites).
- [ ] **Citation guard**: re-propagate the 07-02 lib/test/rule changes if any consumer still uses them; review the block telemetry periodically and route false positives.
- [ ] **Anti-AI-prose academic carve-outs**: `Importantly,` / `Notably,` as literature signals; "implement an experiment"; "serves as the control". Update `anti-ai-prose.md`, `writer-critic.md` and `storyteller-critic.md`.
- [ ] **Housekeeping automation** and **atomic commits as default discipline** (both added 2026-07-01; design TBD).
- [ ] **derive-dont-guess / diagnostic-claim follow-ups** (plans 2026-05-28): overlay CLAUDE.md bullets; `/write` → `writer-critic`; file-granular evidence check; `diagnosis:` ledger rows from critics.
- [ ] **Quarto normalizer** for the evidence-gating Tier-1 gate (with a future Quarto + R migration).
- [ ] **`~/.claude/settings.json` drift** versus `claude-config/settings.json`.
- [ ] **`/tools data-status`**, and a pre-push block when `dvc push` is pending (revisit only if it bites).

## Done (recent)

- [x] 2026-10-28 — **`verify-input` refuses a proof that points into another node's proof** (proof-verifier item 11): steps, cases, "proof/argument of", possessives, read through emphasis and LaTeX; statement parts and own steps allowed; linear time. Reviews r2: red-team 87, correctness 92 (round 1: 68, 88; ReDoS fixed). 141 tests; live blueprint flags only 2 refuted variants. Committed `0faab45`; synced and pushed 2026-10-29 to `behavioral` `cacb58d` (review waived: byte-identical copy), BDD `theory-v2-edits` `9685b8e` and `bdm_bic` `93de622` (docs only; no theory tooling). Session log `2026-10-22_orientation-and-record-backlog.md` §6.
- [x] 2026-10-28 — **BDD and `bdm_bic` synced with the instruction-budget changes** (from `behavioral` `2c816cf`; gates pass). BDD: `5dd2de7`, merged into `theory-v2-edits` as `50f61f1` and pushed; it reaches BDD `main` with that branch. `bdm_bic`: `a9f0023` on `main`, pushed. Always-loaded instructions: BDD 153.2k → 94.2k, `bdm_bic` 148.4k → 89.4k. Session log `2026-10-22_orientation-and-record-backlog.md` §5.

- [x] 2026-10-22 — **Records caught up**: CHANGELOG [Unreleased] and README brought current; stale plan headers closed (modernize, port-mandatory-review, infra survey, context-tightening) and 2026-09 added to the plans index; catch-up survey `quality_reports/reviews/2026-10-22_repo-catch-up-survey.md`; BDD handover plan written. Session log `2026-10-22_orientation-and-record-backlog.md`.
- [x] 2026-10-14 — **Modernize Track A complete**: steps 3–5 (`behavioral` synced, BDD and `bdm_bic` refreshed, propagation retired); steps 1–2 were 2026-09-16. Session log §19, §21–§23.
- [x] 2026-10-19 — **`behavioral` synced with the instruction-budget changes** (`2c816cf`, pushed): 38 Class A files copied; quality, workflow, orchestrator, verifier and new-project merged by hand, keeping behavioral's weights, dispatch rows and pre-registration gate. Session log §30.
- [x] 2026-10-19 — **Always-loaded instructions cut from 165.8k to 103.4k chars** (limit 150k): on-demand detail moved verbatim to 13 references, two rules path-scoped, no behavioural rule removed (reviews r2: 87, 92, 91). Critic agent files made the authoritative deduction tables (compile/run failure -100); `agents.md` § 3 made the authoritative escalation routing. Session log §26–§29.
- [x] 2026-10-15 — **BDD Python environments settled** (owner): the analysis stays in `requirements.txt` (Mac, `myvenv`); the theory checks use the root `.venv`, pinned in full in `theory/requirements-theory.txt` (BDD `8727073`). That file already pinned sympy; the 2026-10-14 note saying otherwise was wrong.
- [x] 2026-10-15 — **BDD theory: the 13 `proved` variants verified.** 9 checked (3 after self-contained rewrites); 3 refuted on reachability or attainment and repaired by owner choice (`-beta-bernoulli-cap`, `-threshold-loss-reach`, `-location-loss-value`, all checked); det-variance superseded by `-2` (checked). No node left at `proved`. Session log §25.
- [x] 2026-10-14 — **BDD theory: all 7 conjecture claims settled.** Checked as written: `lem:var0`, `prop:seq-vs-commit-bias`, `prop:cogcons-wedge`, `prop:commit-vs-seq-size`, `cor:gap-rank`. Repaired with the owner's approval, then checked: `prop:gap-closure` → `prop:gap-closure-pos` (n ≥ 1), `prop:commit-cogcons` → `prop:commit-cogcons-grid` (grid benchmark). Validator PASS (54 nodes).
- [x] 2026-10-14 — **lean_check `card_fields` ignores comments and fences**, matching `blueprint_check` (review 88/100).
