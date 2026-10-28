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
