# TODO — claude-research-workflow

Last updated: 2026-10-14

Project-wide tracker per `.claude/rules/todo-tracking.md`. Details live in plans and session logs; this file tracks what is left.

## Active (doing now)


## Up Next

- [ ] **card-auditor review point (ADR-0005 item 3):** after five audited nodes, count the auditor's catches and false alarms in the session log; the owner decides whether it stays. Audited so far: 1 (`prop:nstar-interior-ac`, 2026-10-14, FAITHFUL, agreed with the owner).
- [ ] **BDD theory: verify the 13 `proved` variant nodes** (the develop loop's step 3). All 7 conjecture claims were settled on 2026-10-14 (session log §24); 13 variant nodes from earlier passes sit at `proved` and need two blind verifiers each, in dependency order.
- [ ] **Modernize Track A, remaining steps** (plan `quality_reports/plans/2026-09-16_modernize-and-simplify-plan.md`):
  - step 3: DONE locally 2026-10-14 (`behavioral` `ab9f5f0`, worktree `~/wt/crw-behavioral`; Class A sync 62 copied + 17 deleted, 5 Class B hand-merged; gate passed). Push of `behavioral` awaits the owner. Guard redesign re-synced too;
  - step 4: DONE 2026-10-14 for both live projects: BDD `43ee165`, `bdm_bic` `2c10c3f` (tags `pre-simplify-2026-10`, local only; session log §21, §23).
  - step 5: DONE 2026-10-14 (propagate.py and sync_overlays.py deleted; `/tools` subcommands and CLAUDE.md section retired; manifest kept as the hand-sync reference).
- [ ] **Voice preservation** (the committed next build from the 2026-09-22 infra survey): two per-paradigm voice profiles; needs the owner's exemplar papers. Folds in the anti-AI-prose academic carve-outs (Backlog).

## Waiting On

- [ ] **BDD Python environments — owner decision** (found 2026-10-14): `requirements.txt` pins the analysis environment (pandas, statsmodels, numba, numpy 2.2.4), but the `.venv` on this machine holds the theory-check environment (sympy, z3, hypothesis, numpy 2.5.3), and sympy is pinned nowhere. Recommendation: keep `requirements.txt` for the analysis and add a pinned `theory/requirements.txt` (with the python version line) for the checks, each with its own environment; merging may not resolve (numba 0.61.2 needs numpy < 2.3). Theorists should run checks with BDD's theory environment, not a temp venv.
- [ ] **Model-routing experiment read-out** (ADR-0003/0004) — waiting on the voice-preservation build, which ADR-0003 names as the revisit point. Pilot evidence so far: verifier fable vs opus near-identical; opus slightly stricter in calibration round 1 and about twice as fast (session log 2026-10-11 §6). Revisit the `writer` exception after the voice build. Per-review severity counts and fix rounds keep accumulating in the session logs (2026-10-14: §13–§17, all reviewers on fable; no new fable-vs-opus pair).

- [ ] **Paper wording, BDD Props 1–2** — the author (or the writer) rewords `theory/quadratic_loss_model_paper_v2.tex` from the checked nodes `prop:nstar-interior` and `prop:vol-commit-equiv-int`; the martingale lemma also needs its edge-case wording (`lem:martingale-horizon`). Also from the 2026-10-14 round, `theory/quadratic_loss_model_paper_v2.tex`: gap closure's comparative statics hold for n ≥ 1 only (:726, `prop:gap-closure-pos`); the Commitment benchmark is the rational optimum on the grid, not the closed-form n* (:507, `prop:commit-cogcons-grid`); :650 cites Proposition prop:vol-commit-equiv, which should point at the integer form; the wedge's 'histories each of positive probability' should read 'sets of histories' (:600); cor:gap-rank(4)'s 'every regime' should name the three regimes; seq-vs-commit-bias part 3's q ∈ (0,1) qualifier is redundant.
- [ ] **Work-repo fixes** (in a session opened in the consulting repo; prompt given 2026-10-11): guard launchers that trust the Store stub; recognising the `personal` repo class. Pushing from this machine depends on the second.
- [ ] **BDD `data/PROVENANCE.md` backfill** — IRB, fielding dates, PII status and authorized users need facts only Christina has.
- [ ] **csac2026 year-specific CLAUDE.md fields** — fill when the 2026 survey specifics are known.

## Backlog

- [ ] **Destructive guard: Windows shared-storage prefixes** — `_shared_prefixes()` lists macOS mount points only, so on this Windows machine `rm -rf` / `find -delete` inside OneDrive or Dropbox folders is not blocked (red-team, 2026-10-14). Adding `%OneDrive%`, `%OneDriveCommercial%` and `~/Dropbox` would also block routine scratch deletes inside repos that live in OneDrive; decide the scope first. ADR-0002 review.
- [ ] **Unclosed `<!--` or code fence in a card** (lean_check review M1, 2026-10-14): `blueprint_check.COMMENT_RE` needs the closing `-->`, so fields after an unclosed comment are still read, while a renderer hides them. Both checkers agree; the owner signs in a raw editor, so the impact is limited. The fix (blank an unclosed comment or fence to the end of the file) must not change node hashing, which also uses `COMMENT_RE`. ADR-0002 review.
- [ ] **Review gate: accept directory targets** — `review-receipt-check.py` matches `**Target:**` by exact path or unique basename only, so files inside a reviewed directory (e.g. `bin/fixtures/lean_check/lean-toolchain`) need a waiver (used once, 2026-10-12). Needs an ADR-0002 review.

- [ ] **lean_check trusted harness** (deferred 2026-10-12, owner's middle path): build the Challenge in an owner-controlled project with its own Mathlib, so the formalizer's lakefile/manifest/folders cannot matter; cap `set_option` resource values. Revisit if the pilot or later work shows the need.

- [ ] **Destructive-action guard on Windows OneDrive** — hardening SHELVED by the owner 2026-10-11 on branch `guard-windows-shared` (`d6d84c2`) after 3 review cycles. Four merge-blockers are listed in that branch's `quality_reports/reviews/2026-10-11_guard-windows-shared-r3_*`. Until then, `main`'s guard does not path-gate deletes inside OneDrive on Windows.
- [ ] **Bulk LFS (+ selective DVC) migration** of the remaining research repos (ADR-0001: GO, forward-only, no history rewrites).
- [ ] **Citation guard**: re-propagate the 07-02 lib/test/rule changes if any consumer still uses them; review the block telemetry periodically and route false positives.
- [ ] **Context-tightening, remaining levers** (plan `quality_reports/plans/2026-05-28_context-tightening-plan.md`): Lever 2 and the hook-rule prose trims.
- [ ] **Anti-AI-prose academic carve-outs**: `Importantly,` / `Notably,` as literature signals; "implement an experiment"; "serves as the control". Update `anti-ai-prose.md`, `writer-critic.md` and `storyteller-critic.md`.
- [ ] **Housekeeping automation** and **atomic commits as default discipline** (both added 2026-07-01; design TBD).
- [ ] **derive-dont-guess / diagnostic-claim follow-ups** (plans 2026-05-28): overlay CLAUDE.md bullets; `/write` → `writer-critic`; file-granular evidence check; `diagnosis:` ledger rows from critics.
- [ ] **Quarto normalizer** for the evidence-gating Tier-1 gate (with a future Quarto + R migration).
- [ ] **`~/.claude/settings.json` drift** versus `claude-config/settings.json`.
- [ ] **`/tools data-status`**, and a pre-push block when `dvc push` is pending (revisit only if it bites).

## Done (recent)

- [x] 2026-10-14 — **BDD theory: all 7 conjecture claims settled.** Checked as written: `lem:var0`, `prop:seq-vs-commit-bias`, `prop:cogcons-wedge`, `prop:commit-vs-seq-size`, `cor:gap-rank`. Repaired with the owner's approval, then checked: `prop:gap-closure` → `prop:gap-closure-pos` (n ≥ 1), `prop:commit-cogcons` → `prop:commit-cogcons-grid` (grid benchmark). Validator PASS (54 nodes).
- [x] 2026-10-14 — **lean_check `card_fields` ignores comments and fences**, matching `blueprint_check` (review 88/100).
- [x] 2026-10-14 — **Destructive-action guard**: the unparseable-command false positive fixed, and the guard redesigned over three review rounds (every command of a chain, quote-aware heredocs, per-command bypass); 136 tests; audit-log replay 0 new blocks (session log §20).
- [x] 2026-10-14 — **`/tools sync-status`**: `bin/sync_status.py` + 22 tests; catches unpushed LFS when the LFS hook is bypassed, plain blobs under LFS rules, missing upstreams (session log §18).
- [x] 2026-10-14 — **BDD tidy-up closed, no change**: the three refuted variants' `uses` of the superseded `lem:martingale` are history by design; `blueprint_tools.py repoint` skips terminal nodes (dry run: nothing to repoint).
- [x] 2026-10-14 — **BDD mentions pass**: 32 named-not-used citations on 15 nodes declared as mentions; no hash changed; warnings 34 → 2 (both on conjecture claims, left for the theorist). Tools already current in BDD.
- [x] 2026-10-14 — **ADR-0005 implemented**: bound signature, checklist, card-auditor (calibration 6/6, no false alarm), `/theory` flow; pilot converted, audited (FAITHFUL, coverage PASS) and re-signed (BDD `f779e92`). Session log §14–§17.
- [x] 2026-10-14 — **Theory phase 2 Lean pilot COMPLETED**: `prop:nstar-interior-ac` `verified` (BDD `bef1c6a`); acceptance #7 met, #8 met in part (owner guided, not unaided); Lean project backed up to private `chesun/bdd-lean` (`77d1a93`). Read-out: session log 2026-10-11 §12.
- [x] 2026-10-13 — **BDD: six recursive-methods PDFs moved into LFS** (BDD `e29e62e`; content unchanged, each file's hash matches its pointer).
- [x] 2026-10-13 — **Lean card calibration**: owner caught both planted defects (B dropped `c > 0`, C `ConcaveOn` for strictly concave), one mild false alarm on A (session log §11).
- [x] 2026-10-12 — **Lean setup spike PASSED** on native Windows: elan 4.2.4 (GitHub release, digest-verified), Lean v4.35.0-rc4 + Mathlib cache, `lake build --wfail`, `#print axioms`, `sorry` detection, `leanchecker`, `lean-lsp-mcp` 0.31.0 (session log 2026-10-11 §8). Also: the overlay's dropped theory agents restored (`10a0036`).
- [x] 2026-10-12 — **Theory phase 2 prep**: `bin/blueprint_tools.py` (verify-input, dependents, repoint with cascade), cited-label + mentions check in the validator, `bin/agent_lint.py`; two ADR-0002 review rounds, all findings fixed or accepted (session log 2026-10-11 §7). Also: history scrubbed and pushed; BDD classified personal and pushed.
- [x] 2026-10-12 — **Theory workflow phase 1 COMPLETE** (ADR-0004; merged; plan `quality_reports/plans/2026-10-11_theory-workflow-phase1-plan.md` COMPLETED). The BDD pilot found 3 statement defects in the paper, rediscovered the referees' findings blind, and ended with 4 checked nodes (51 total); calibration met spec acceptance #2. Read-out: session log 2026-10-11 §6.
- [x] 2026-10-11 — **Hook test suites pass on Windows** (all 8; citation-lib backslash paths and `sys.executable` runner; UTF-8 output; junction fallback; pinned pytest dev env). Reviewed under ADR-0002.
- [x] 2026-10-11 — **Hooks were silently failing open** (the `python3` Store stub): the launcher now probes python3/python/py and forces UTF-8 output. App Execution Aliases turned off.
- [x] 2026-10-11 — **Theory agents re-registered**: a `: ` in their `description:` had made strict YAML drop them.
- [x] 2026-10-11 — **BDD clone repaired** (a `|` filename broke the Windows checkout; renamed upstream; index rebuilt from HEAD).
- [x] 2026-09-24 — **Model routing** (ADR-0003): reviewers on `fable`, workers on `opus`.
- [x] 2026-09-22 — **Review gate fails closed, escapably** (ADR-0002 amendment).
- [x] 2026-09-21 — **Mandatory independent review** gate for code (ADR-0002).
- [x] 2026-09-16 — **Modernize Track A steps 1–2**: nag hooks pruned; `notify` / `protect-files` ported to Python.
- [x] 2026-07-03 — **LFS for PDFs ratified**; ADR-0001 GO for bulk migration.
