# Active plans

Index of `Active` and `Approved` plans. See [`README.md`](README.md) for lifecycle conventions.

When creating a new plan, consult this index first. If an `Active` entry covers the same scope, follow the supersession protocol in `README.md`.

---

## 2026-06

- [2026-06-23_port-applied-micro-to-csac2026.md](2026-06-23_port-applied-micro-to-csac2026.md) — COMPLETED 2026-06-23: seeded new project repo `~/github_repos/csac2026` from the applied-micro overlay (synced overlay current first), filled csac2026 identity (CEL / UC Davis, CSAC + C2C, Stata), registered as an applied-micro consumer with propagate baseline. Local-only by design (no remote). Session log: `session_logs/2026-06-23_port-applied-micro-to-csac2026.md`.

## 2026-05

- [2026-05-29_evidence-gating-build-plan.md](2026-05-29_evidence-gating-build-plan.md) — COMPLETED 2026-05-30: unified evidence-gating discipline (design of record `reviews/2026-05-28_whole-picture-critic-gates-dispatch.md` §7). All 5 phases built + adversarially reviewed + verified: Tier-1 normdiff recorder (Stata/R/Python/LaTeX, CLAUDE.md-configurable roots) → rule + `{PASS,UNVERIFIED,FAIL}` vocabulary + ledger schema + the gate → Tier-2 citation-existence + schema evidence → operationalization gate (advisory) + Tier-3 panel → distributed to all 7 consumers + 2 overlays. Merged to main; status `reviews/2026-05-30_evidence-gating-distribution-status.md`.
- [2026-05-28_context-tightening-plan.md](2026-05-28_context-tightening-plan.md) — DRAFT (awaiting approval): cut the ~165KB/~41k-token always-on rule footprint. Primary lever = add `paths:` frontmatter to 8 convention rules (lazy-load, ~28% off always-on, zero rewiring); secondary = references/ split for data-version-control + trim/dedup of universal rules. Projected ~42–47% reduction. Companion audit: `reviews/2026-05-28_workflow-context-audit.md`. On branch `audit/workflow-context-tightening`.
- [2026-05-28_diagnostic-claim-enforcement.md](2026-05-28_diagnostic-claim-enforcement.md) — COMPLETED 2026-05-28: enforce verification of bug/error *causation* claims (the class beyond file paths). Block-once Stop-audit (`diagnostic-claim-audit.py`) when a cause is asserted with no investigation this turn and no consult of the verification ledger; `diagnosis:<slug>` rows in `.claude/state/verification-ledger.md` are the recorded-findings store (hash-staleness handles "code moved on"). Gives `adversarial-default.md` its first hook.
- [2026-05-28_derive-dont-guess-enforcement.md](2026-05-28_derive-dont-guess-enforcement.md) — COMPLETED 2026-05-28: gave `derive-dont-guess` hook teeth (advisory PostToolUse path-literal check + opt-in PreToolUse block + propagation fix via settings.json→universal + non-hook elevations) and extended trigger-based enforcement to plan-persistence (blocking Stop hook) and output-length (advisory Stop hook). 5 commits, 59 tests. Companion audit: `reviews/2026-05-28_derive-dont-guess-binding-audit.md`
- [2026-05-07_comprehensive-propagation-plan.md](2026-05-07_comprehensive-propagation-plan.md) — APPROVED 2026-05-07: extends v1 propagate plan with three-class file taxonomy (universal / overlay-customized / overlay-only), `.claude/file-classes.toml` manifest, modified routing in propagate.py, new `/tools sync-overlays` skill for main → overlay sync; in execution, Phase A starting
- [2026-05-06_tools-propagate-plan.md](2026-05-06_tools-propagate-plan.md) — v1 `/tools propagate` skill: registry-driven feature propagation; **extended by 2026-05-07 plan**; v1 implementation (propagate.py, consumers.toml, divergence-skip) preserved and still load-bearing
- [2026-05-05_lfs-dvc-migration-plan.md](2026-05-05_lfs-dvc-migration-plan.md) — concrete plan: Git LFS for PDFs + DVC for data + periodic Dropbox backup; supersedes Dropbox-symlink approach; D3 + D8 resolved 2026-05-05. **DVC pilot push completed 2026-06-23** (closed a dangling pointer in `belief_distortion_discrimination`: re-add + first `dvc push` of 1.15 GB + data-doc contract; see `session_logs/2026-06-23_dvc-pilot-push-completion.md`). Still open: `/tools sync-status` skill (§7.5), pre-LFS PDF churn, pilot 7-day exit decision (D6).
- [2026-05-05_lfs-vs-dvc-explainer.md](2026-05-05_lfs-vs-dvc-explainer.md) — concept-level explainer for Git LFS and DVC (companion to migration plan)
- [2026-05-01_v0.2-tutorial-scope.md](2026-05-01_v0.2-tutorial-scope.md) — v0.2.x tutorial track: function-by-function demos, behavioral overlay priority, orchestrator de-emphasized
- ~~[2026-05-01_dropbox-symlink-setup-explainer.md]~~ — superseded by 2026-05-05 LFS+DVC migration plan; archived to `archive/`

## 2026-04

- [2026-04-21_universal-gitignore.md](2026-04-21_universal-gitignore.md) — universal `.gitignore` (likely Completed; backfill status)
- [2026-04-28_adversarial-default-rule-proposal.md](2026-04-28_adversarial-default-rule-proposal.md) — adversarial-default rule + verification ledger (Completed; backfill status)
- [2026-04-28_derive-dont-guess-rule-proposal.md](2026-04-28_derive-dont-guess-rule-proposal.md) — derive-don't-guess rule (Completed; backfill status)

## 2026-03

- [2026-03-17_workflow-adaptation-plan-v2.md](2026-03-17_workflow-adaptation-plan-v2.md) — initial workflow adaptation plan v2
- [2026-03-17_workflow-adaptation-plan.md](2026-03-17_workflow-adaptation-plan.md) — initial workflow adaptation plan (likely superseded by v2)
- [2026-03-18_agent-gap-analysis.md](2026-03-18_agent-gap-analysis.md) — agent gap analysis
- [2026-03-18_applied-micro-plan-v2-hugo-base.md](2026-03-18_applied-micro-plan-v2-hugo-base.md) — applied-micro plan v2 (Hugo base)
- [2026-03-18_behavioral-workflow-plan.md](2026-03-18_behavioral-workflow-plan.md) — behavioral workflow plan
- [2026-03-18_clarifying-questions-round3.md](2026-03-18_clarifying-questions-round3.md) — clarifying questions round 3
- [2026-03-18_consolidated-decisions-and-applied-micro-plan.md](2026-03-18_consolidated-decisions-and-applied-micro-plan.md) — consolidated decisions + applied-micro plan
- [2026-03-18_followup-questions-q11-q14.md](2026-03-18_followup-questions-q11-q14.md) — follow-up questions Q11–Q14
- [2026-03-18_strategist-vs-rule-comparison.md](2026-03-18_strategist-vs-rule-comparison.md) — strategist vs rule comparison
- [2026-03-18_tx-project-memory-revision.md](2026-03-18_tx-project-memory-revision.md) — TX project memory revision
- [swift_lit_review_output.md](swift_lit_review_output.md) — swift lit review output (no date prefix; likely needs renaming)

---

*These were written before the lifecycle convention; their headers do not yet declare a `Status` field. Treat as `Active` until backfilled, completed, or superseded. Many of the March entries are likely `Completed` — sweep on next cleanup.*
