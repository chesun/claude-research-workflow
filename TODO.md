# TODO — claude-research-workflow

Last updated: 2026-10-12

Project-wide tracker per `.claude/rules/todo-tracking.md`. Details live in plans and session logs; this file tracks what is left.

## Active (doing now)

- [ ] (none: next is the Lean lane, below)

## Up Next

- [ ] **Theory workflow — phase 2: Lean lane** (spec `quality_reports/specs/2026-10-11_theory-proof-workflow-spec.md` §4): setup spike first (elan + Mathlib outside OneDrive, `lean-lsp-mcp` and `leanchecker` on native Windows), then `formalizer`, fidelity cards, `bin/lean_check.py`. Pilot: BDD `prop:nstar-interior`.
- [ ] **BDD theory: remaining claims** — 7 nodes still at `conjecture` (the wedge, gap-closure and bias results). Run `/theory develop` in BDD. The wedge proof's unstated step (b_t > 0 for t < T−1) was flagged by the known-answer theorist.
- [ ] **BDD: install the phase-2 tools and declare mentions** — copy `bin/blueprint_tools.py` and the updated `bin/blueprint_check.py`; the new checks give ~32 warnings on 51 nodes, mostly variant statements naming their parent claim or dropped assumption. Each needs a judgment (dependency → `uses`, or `<!-- mentions: -->`); adding to `uses` changes the proof hash of a proved node.
- [ ] **BDD tidy-ups**: three refuted variant nodes (`var:cogcons-wedge-{held-belief,terminal-belief,update}-cost`) still list the superseded `lem:martingale` in `uses`. Six PDFs under `master_supporting_docs/literature/papers/recursive/` show as modified only because they were committed as plain files under an LFS rule; decide whether to renormalize them to LFS.
- [ ] **Modernize Track A, remaining steps** (plan `quality_reports/plans/2026-09-16_modernize-and-simplify-plan.md`):
  - step 3: mirror the hook prune and Python ports onto the `behavioral` overlay; the overlay's own Class-B rules still call `theorist` overlay-only;
  - step 4: one-time `.claude/` update of the live projects (`bdm_bic`, `belief_distortion_discrimination`);
  - step 5: retire `/tools propagate`, `sync-overlays` and `consumers.toml`.
- [ ] **Model-routing experiment read-out** (ADR-0003/0004). Pilot evidence so far: verifier fable vs opus near-identical; opus slightly stricter in calibration round 1 and about twice as fast (session log 2026-10-11 §6). Revisit the `writer` exception after the voice build.
- [ ] **Voice preservation** (the committed next build from the 2026-09-22 infra survey): two per-paradigm voice profiles; needs the owner's exemplar papers. Folds in the anti-AI-prose academic carve-outs (Backlog).
- [ ] **Destructive-action guard false positive**: the shlex-failure fallback in `.claude/hooks/destructive-action-guard.py` blocks any command containing an apostrophe plus a keyword (`--force`, `update-ref -d`) and labels it `git filter-repo`. Workaround: commit with `-F <file>`. Needs an ADR-0002 review.
- [ ] **`/tools sync-status` script** (§7.5 of the LFS/DVC plan): the subcommand exists only as prose steps.

## Waiting On

- [ ] **Paper wording, BDD Props 1–2** — the author (or the writer) rewords `theory/quadratic_loss_model_paper_v2.tex` from the checked nodes `prop:nstar-interior` and `prop:vol-commit-equiv-int`; the martingale lemma also needs its edge-case wording (`lem:martingale-horizon`).
- [ ] **Work-repo fixes** (in a session opened in the consulting repo; prompt given 2026-10-11): guard launchers that trust the Store stub; recognising the `personal` repo class. Pushing from this machine depends on the second.
- [ ] **BDD `data/PROVENANCE.md` backfill** — IRB, fielding dates, PII status and authorized users need facts only Christina has.
- [ ] **csac2026 year-specific CLAUDE.md fields** — fill when the 2026 survey specifics are known.

## Backlog

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
