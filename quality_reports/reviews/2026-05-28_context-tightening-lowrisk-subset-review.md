# Context-Tightening — Low-Risk Subset Review

**Date:** 2026-05-28
**Reviewer:** (working session, not a critic dispatch)
**Target:** Levers 2/3 of `quality_reports/plans/2026-05-28_context-tightening-plan.md`, restricted to the low-risk subset
**Status:** Active — items A + B EXECUTED 2026-05-28 (see Outcome below); C/D/E pending

## Outcome — executed 2026-05-28

User decided to drop **both** logging sections, not just A. Rationale for also dropping B (`research_journal.md`): the orchestrated agent pipeline the journal serves isn't run in practice either — same dead-requirement logic as SESSION_REPORT. Executed: removed `logging.md` §2 + §3 (5,445 → 1,972 B, −3,473 B / ~870 tokens off always-on), cleaned 5 incidental pointers (file-classes.toml, quality.md, decision-log.md, agents.md, tools/SKILL.md). The 2 live "logged in research journal" instructions retargeted to the session log. Verified 0 dangling refs; no hook rules touched.

**C (epistemic-table dedup) — DONE, but byte-neutral.** The full table lived in two always-on files that had *diverged* (no-assumptions: 2 columns; derive-dont-guess: 3 columns, different row wording). Consolidated to one canonical 3-column table in `no-assumptions.md`; `derive-dont-guess.md` now points to it. Net bytes ≈ +82 B (enriching the canonical + leaving a real pointer ≈ what the duplicate cost), so this is a **maintainability/anti-drift win, not a context win**. derive-dont-guess Enforcement (hook) section untouched.

**D (crosswalk dedup) — MOOT.** Its target was a triplicated "relationship to other records/logs" crosswalk across logging/decision-log/todo-tracking. Removing logging §3 already deleted logging's copy; `todo-tracking.md` never had a crosswalk (only integral cross-mentions in its rules); the one in `decision-log.md` legitimately belongs there (decision-centric). No real duplication left — skipped rather than manufacture a trivial edit.

**E (misc) — not done.** revision.md ASCII diagram worth keeping for readability; verification-protocol↔single-source-of-truth overlap minor. Left as-is.

## Scope of this review

User decisions that bound the subset:

- **Lever 2 (data-version-control split) — EXCLUDED.** DVC not yet used in any live repo, so relocated setup/rollback procedure can't be field-tested. Not touching it.
- **Hook-rule prose trims (#13–16: destructive-actions, workflow, adversarial-default, primary-source-first) — EXCLUDED.** Risk concentrated in hook-referenced remediation strings; not worth it for this pass.

What remains: dedup + dead-rule removal in **non-hook files** (or trim-in-place on a hook file where the target is plain documentation, not a remediation string).

## Findings (grounded in actual current bytes, not plan estimates)

| Item | What it is | Real bytes | File (hook?) | Risk | Recommend |
|------|-----------|-----------|--------------|------|-----------|
| **A** | Drop `logging.md` §2 "Session Report (Consolidated)" — the `SESSION_REPORT.md` master-log requirement | ~1,790 | logging.md (no) | low | **DO** |
| **B** | `logging.md` §3 Research Journal — `research_journal.md` | ~1,670 | logging.md (no) | **med** | **KEEP** (see note) |
| **C** | #12 epistemic-table dedup — `derive-dont-guess.md` carries a richer 3-col copy; `no-assumptions.md` has the 2-col canonical | ~650 (not 1,400) | derive-dont-guess (yes, trim-in-place OK) | low | DO (small) |
| **D** | #17 crosswalk dedup — `logging`/`decision-log`/`todo-tracking` each restate "relationship to other logs" | ~1,100 est | non-hook | low | DO |
| **E** | #18 misc — `revision.md` ASCII diagram; `verification-protocol`↔`single-source-of-truth` overlap | ~2,000 est | mixed (output-length IS a hook) | low-mixed | review item-by-item |

### Key evidence

- **A & B:** `find` for `SESSION_REPORT.md` and `research_journal.md` → **neither exists** anywhere in the repo. Both rule sections describe practices never once instantiated across many sessions. Actual practice = per-session logs in `quality_reports/session_logs/` + `TODO.md`.
- **A vs B asymmetry:** `SESSION_REPORT.md` is a Claude-session consolidated log — a personal-workflow artifact the user has implicitly rejected (redundant with per-session logs). Safe to drop. **`research_journal.md` is different**: `logging.md` §3 makes it load-bearing in the *orchestrated agent pipeline* ("after every agent produces a report, append…"). A fork running `/new-project` would generate it. It's unused *here* only because this meta/template repo rarely runs the full pipeline. Per meta-governance ("would a forker benefit?"), keep it.
- **C:** the two tables aren't byte-identical — `derive-dont-guess`'s has an extra "What it prevents" column the canonical lacks. Clean dedup = enrich the `no-assumptions` canonical to 3 columns, then replace `derive-dont-guess`'s table with a one-line pointer. Net saving smaller than the plan's 1,400 B estimate (~650 B), and it touches a hook file (trim-in-place, documentation only — permitted).

## Honest bottom line on magnitude

Realistic low-risk saving = **A + C + D ≈ 3,500 B (~875 tokens, ~0.7% of pre-Lever-1 always-on / ~1% of current)**. With B it'd be ~5,200 B, but B should stay.

This is a **small byte win** — the large wins (DVC ~6%, hook-rule trims ~7%) are exactly the ones we're deliberately *not* doing. So the case for the low-risk subset is **not primarily about context**:

- **A (drop SESSION_REPORT)** is worth doing *independent of bytes* — it removes a rule requirement that's never been followed and contradicts actual practice. Dead rules cause confusion and erode the credibility of the rule file. This is a correctness/simplicity win.
- **D (crosswalk dedup)** reduces "three places to update" maintenance drift.
- **C** is marginal — do it only if we're already in `derive-dont-guess` for another reason.

## Recommendation

Two tiers, your call:

1. **Worth doing for correctness, not just bytes:** A (drop SESSION_REPORT §2). One file, non-hook, removes a never-used requirement. ~10 min.
2. **Optional polish:** C + D if we want the dedup tidy-up while we're here. E reviewed item-by-item first (the `revision.md` diagram may be worth keeping for readability).

If the goal is "stop diluting always-on context," A is the only item that clearly pays for its churn. C/D/E are tidy-ups with modest payoff.
