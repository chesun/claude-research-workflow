# Repo catch-up survey — where things stand

**Date:** 2026-10-22
**Reviewer:** main session (orientation survey, read-only)
**Target:** repository state
**Score:** n/a (orientation)
**Status:** Active
**Supersedes:** `quality_reports/reviews/archive/2026-10-11_repo-catch-up-survey.md`

**Sources read:** `TODO.md` (updated 2026-10-19), `decisions/README.md` (ADR-0001–0005), `quality_reports/plans/INDEX.md` and the headers of the 2026-09 and 2026-10 plans, session log `2026-10-11_hook-launcher-fix-and-theory-brainstorm.md` (§1–§30, through 2026-10-19), `2026-09-22_infra-survey_synthesis.md` and its 2026-09-23 review, `README.md`, `CHANGELOG.md`, git branches and worktrees, auto-memory.

## 1. What this repo is now

- A **personal** research-workflow template (origin = personal `chesun` account). Live surface: `main` + the `behavioral` overlay. `applied-micro` and the dormant consumers are frozen.
- Propagation tooling was retired 2026-10-14; overlays and live projects are synced **by hand**, per the class procedure in `.claude/file-classes.toml`.
- Live projects: `belief_distortion_discrimination` (BDD, where the theory work runs) and `bdm_bic`.
- The consulting layer lives in a sibling work repository. Work on it happens in a session opened there, not from here.

**Git state (verified 2026-10-22):** `main` at `7ac60cd`, equal to `origin/main`, tree clean. `behavioral` at `2c816cf`, pushed, in worktree `~/wt/crw-behavioral`. Local-only branches: the work-branch archive (2026-09-15), `copilot-port` (2026-09-09), `guard-windows-shared` (shelved 2026-10-11), `main-backup-unscrubbed-2026-10-12` (pre-scrub backup).

## 2. The arc since September

| When | What | Record |
|---|---|---|
| 09-16 | Modernize plan: Track A (prune nag hooks, port shell hooks to Python, sync overlay and live projects, retire propagation); Track B deferred | plan `2026-09-16_modernize-and-simplify-plan.md` |
| 09-21/22 | Mandatory independent review gate for code, fails closed but escapable | ADR-0002 |
| 09-22/23 | Infra survey: **voice preservation** is the one committed next build; a candidate list is held uncommitted | synthesis, review 78/100 |
| 09-24 | Model routing: reviewers on `fable`, workers on `opus` | ADR-0003 |
| 10-11 | Hooks had been failing open silently (the `python3` Store stub); launcher fixed; hook suites pass on Windows | log §2, §5 |
| 10-11/12 | Theory workflow phase 1: blueprint, validator, blind proof-verifier, BDD pilot | ADR-0004 |
| 10-12/14 | Phase 2 Lean lane: pilot `prop:nstar-interior-ac` `verified`; lighter sign-off plus `card-auditor` | ADR-0005, log §8–§17 |
| 10-14 | Destructive guard redesign (136 tests); `/tools sync-status`; Track A steps 3–5 **done** | log §18–§23 |
| 10-14/15 | BDD theory: 7 conjectures settled, 13 variants verified; 58 nodes, validator PASS, none left at `proved` | log §24–§25 |
| 10-19 | Always-loaded instructions cut from 165.8k to 103.4k chars (limit 150k); critic agent files hold the authoritative deduction tables (-100 for a compile or run failure); `agents.md` § 3 holds the authoritative escalation routing; `behavioral` synced | log §26–§30 |

## 3. What is open (from `TODO.md`)

**Up Next**
- **Voice preservation**: the committed next build. Blocked on the owner's exemplar papers (two per-paradigm voice profiles). The mechanism design is in `2026-09-22_infra-survey_C-voice.md`.
- **card-auditor review point**: 1 of 5 audited nodes so far. The owner decides whether the auditor stays after five.

**Waiting on the owner**
- Mac worktrees (`git worktree repair` or `prune` on the Mac).
- BDD paper wording for Props 1–2 plus six smaller fixes in `theory/quadratic_loss_model_paper_v2.tex`.
- Work-repo guard fixes (done in the work repo's own session).
- BDD `data/PROVENANCE.md` facts.
- csac2026 fields.
- Model-routing read-out, which waits on the voice build.

**Backlog, notable items**
- `verify-input` refusal for cross-node proof citations (gated code).
- Destructive guard Windows scope: on this machine `rm -rf` inside OneDrive is **not** path-gated. Known, and documented in the rule.
- Review gate to accept directory targets.
- Bulk LFS migration (ADR-0001).

**Uncommitted candidates after voice** (synthesis § Next build): `/verify-claims` is the likeliest second pick. Then `/audit-reproducibility`, Bash-write coverage for `.claude/hooks/`, and an AEA replication README.

## 4. Drift found in the records (none of it affects code)

1. **`TODO.md`:** "Modernize Track A, remaining steps" sits in Up Next, but all three of its steps are marked DONE. It belongs in Done.
2. **Plan headers are stale:**
   - The modernize plan still reads "DRAFT v2 … Awaiting approval", though Track A is complete.
   - `2026-09-21_port-mandatory-review.md` reads "DRAFT v2 … Awaiting go to build", though ADR-0002 shipped.
   - The infra-survey plan reads "RUNNING (v5)", though the synthesis was delivered and reviewed.
3. **`plans/INDEX.md` has no 2026-09 section.** It is missing the modernize, port-mandatory-review and infra-survey plans.
4. **The context-tightening plan is still listed DRAFT,** and its TODO backlog item ("remaining levers") survives. The 2026-10-19 instruction-budget work did most of what that plan covered, so the plan is probably superseded. That is the owner's call.
5. **`CHANGELOG.md` [Unreleased] stops at theory phase 1.** It does not record:
   - ADR-0002, ADR-0003 and ADR-0005;
   - the Lean lane;
   - the hook pruning, the guard redesign and `sync-status`;
   - the retirement of propagation, which it still lists under "Added";
   - the instruction-budget cut.
6. **`README.md` is out of date:**
   - it says "Last Updated 2026-04-28";
   - it counts "20 agents … ~18 rules", but `.claude/agents/` now holds 22 files and `.claude/rules/` 29;
   - it says overlays are updated "via rebase", where the current procedure is a hand-sync per `file-classes.toml`.
7. **The single session log `2026-10-11_…` has grown to 813 lines across nine days (§1–§30).** Starting a new dated log at the next work session would keep it navigable.
8. **The pending-decisions list in `decisions/README.md` reads "none".** Two owner decisions are live, though: the scope of the Windows guard, and whether to keep the card-auditor after five nodes.
9. **Auto-memory was stale:** it described the repo as a Copilot port pushed only to enterprise. It was corrected on 2026-10-22 to match the 2026-09-15 reclassing as a personal repo.
