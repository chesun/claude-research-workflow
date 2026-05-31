# Re-Review — Evidence-Gating Build Plan v2

**Date:** 2026-05-29
**Reviewer:** re-review workflow (closure audit + adversarial re-attack on C1 + new-issues sweep), grounded against repo HEAD on `main`
**Target:** `quality_reports/plans/2026-05-29_evidence-gating-build-plan.md`
**Prior review:** `2026-05-29_evidence-gating-build-plan_synthesis_review.md` (REVISE-FIRST; C1–C2, M1–M12, m1–m4)
**Status:** Active

---

## 1. Executive verdict

**REVISE-AGAIN.** v2 is a markedly better *specification* and resolves most design-level findings, but its headline fix — C1's "robust establishment" — rests entirely on two systems (`/tools refactor-mode` and a `bin/setup-machine.sh` pre-commit backstop) that do not exist anywhere in the repo, so the exact ADR-0011 failure mode (a contaminated refactor shipping uncaught) remains live in the default state, just behind a new precondition.

## 2. Closure scorecard

18 findings tracked (m1 excluded as pre-confirmed). **6 fully closed, 11 partial, 1 effectively not-closed.**

- **CLOSED (6):** M5 (normdiff interface), M10 *decision-level* (but see §4), M11 (extend-in-place + content split), m2 (six suffixes), m3 (BYPASS_SHARED_GUARD Tier-3 cite), m4 (file-classes verify step).
- **PARTIAL — sound spec, no code (8):** C2, M1, M2, M3, M6, M7, M8, M12. (Expected — nothing is implemented yet.)
- **PARTIAL — deferred design choice, not made (2):** **M4** ("extract predicates *or* write fresh" — never decided), **M9** ("co-ship Phase 3 *or* soften" — deferred).
- **NOT CLOSED (1):** **C1** — see §3.

Repo verification confirms nothing implemented: no `evidence-gate-check.py`, no `normdiff_lib.py`, no `references/evidence-gating-detail.md`, no `refactor-mode.enabled`, no `.claude/state/README`, no `bin/`, no executable `.git/hooks/pre-commit`, zero `refactor` matches in `.claude/skills/`.

## 3. Does the C1 fix HOLD? No. (#1 blocker)

The synthesis review's verdict — "silently void by default" — stands, because both legs of the new mitigation are vapor:

- **C1a (tooling auto-enables):** `/tools refactor-mode` + `/tools normdiff` are NEW but unbuilt — `tools/SKILL.md` lists 12 subcommands, none of them; `grep -r refactor .claude/skills/` returns zero; no existing skill calls it.
- **C1b (commit-time backstop):** depends on `bin/setup-machine.sh`, but `bin/` does not exist; `setup-machine.sh` lives only in `templates/` and does LFS/DVC only. `.git/hooks/` has only `.sample` files.

So in the default state (refactor-mode off, no manifest, no pre-commit hook) the per-edit hook hits its silent `exit 0` and ships the contaminated refactor — ADR-0011 verbatim. **The memory-dependency is relocated, not eliminated** ("remember to enable refactor-mode" replaces "remember to verify").

Compounding gaps: **"refactor-shaped commit" is undefined** (the backstop has no operational predicate); the **external-editor / `--no-verify` bypass** must be stated plainly as a known limit (only Edit/Write-tool-mediated refactors can ever be gated).

## 4. New issues introduced by v2 (ranked, only those that hold)

1. **(major) M10 misstates `agents.md`'s class.** `file-classes.toml [overlay-customized]` lists `rules/quality.md` and `rules/workflow.md` but **not** `agents.md` → it defaults Class A and would propagate universally. (Phase 2 actually edits `coder-critic.md`, also Class A; line 105 conflates the two.) Fix the claim or add `agents.md` to the overlay list.
2. **(major) `bin/setup-machine.sh` install path is aspirational** — `bin/` doesn't exist; the file is a template. Decide: create `bin/`, extend the template, or document post-clone copy.
3. **(major) Two NEW `/tools` subcommands unregistered** (refactor-mode, normdiff) — the "single entry point" is absent from `tools/SKILL.md`.
4. **(major) Lazy-load mechanism for `references/evidence-gating-detail.md` undocumented** — existing `references/` docs load via explicit Read instructions in agent frontmatter, not a "lazy-load" system. Clarify; add the split-content pointer inside `adversarial-default.md`.
5. **(minor) M11 inbound-ref count stale** — plan says "12"; load-bearing refs in `rules/`+`agents/` ≈ 8 (45 total mentions). Re-audit; add a step confirming refs survive the split.
6. **(minor) `refactor-mode.enabled` not git-ignored** — no `.gitignore` entry; `.claude/state/README` also absent (M1 doc TO-DO).
7. **(minor) M9 interim-binding decision deferred** — pick co-ship vs soften before Phase 2 edits land.

## 5. Blocking before Phase 1

1. **Decide M4** — extract `is_path_glob_open/close` as a pure utility vs. fresh path-char normalizer (blocks `normdiff_lib.py`).
2. **Build C1a** — implement + register `/tools refactor-mode` + `/tools normdiff`; integrate into a named real refactor entry point.
3. **Define "refactor-shaped commit"**, then build C1b (resolve `bin/` + `setup-machine.sh` + the `pre-commit` script).
4. **Create `.claude/state/README` convention** + add the manifest to `.gitignore`.
5. **State the external-editor / `--no-verify` limit plainly** in the rule (honest gap, not a fix).
6. **Correct the M10 class claim** (agents.md) and the M11 inbound-ref count.

## 6. Recommended alternative (reviewer's)

If the project prefers to ship deterministic value sooner, adopt the synthesis review's original C1 design — make the per-edit hook **advisory-always**: on a detected logic change with refactor-mode off, emit an `UNVERIFIED` ledger row + advisory instead of silent `exit 0`. That collapses blockers 2–3 and 5 (no refactor-mode dependency, no pre-commit hook, no external-editor reliance), leaving only M4 + the documentation fixes as Phase-1 blockers.
