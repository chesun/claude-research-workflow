# TODO — claude-code-my-workflow

Last updated: 2026-05-11

Project-wide tracker per `.claude/rules/todo-tracking.md`. Active session-tracker tasks (TaskCreate) are working memory; this file is the persistent cross-session record.

## Active (doing now)

- *(nothing actively in flight — comprehensive propagation plan fully executed and documented; ready for next initiative)*

## Up Next
- [ ] **Resume BDD pilot** — wait for user "resume" signal. Tasks #5–#12 in tracker; first action is soft-migrate 60 existing PDFs to LFS pointers (already approved 2026-05-06).

## Waiting On

- [ ] **BDD pilot resumption** — user actively running tasks in BDD; will signal "resume" when done. State preserved: 2 BDD commits already landed locally (`ec8d2e8` LFS enable, `c2c41f0` DVC init), 1.1 GB cached in `.dvc/cache/`, `data_local.dvc` pointer uncommitted. Tag `pre-lfs-dvc-migration-2026-05-06` is the rollback target.
- [ ] **D6 — pilot exit decision** (after pilot's 7-day run) — go/no-go on bulk migration based on the five §6.6 metrics in the LFS+DVC plan.

## Backlog

- [ ] **`~/.claude/settings.json` drift** — diverged ~50 days from `claude-config/settings.json` (193 vs 81 bytes). Per `sync-global-config.md`, the live file should be copied to the repo and committed. Small task; ~10 min.
- [ ] **Extend `NEVER_SURNAMES` blocklist** in `.claude/hooks/primary_source_lib.py` with two clusters of false positives encountered in real session-log writing: (a) status words `Resolved` / `Pending` / `Deferred` / `Open` (bracketed-year like `[Resolved 2026-05-05]`); (b) common changes-table verbs `Added` / `New` / `Fixed` / `Removed` / `Inserted` / `Replaced` / `Changed` / `Extended` / `Deleted` / `Dropped` / `Copied` / `Merged` / `Patched` (table-cell-start verbs followed by date-like strings). ~10 lines + tests.
- [ ] **Refine anti-AI-prose catalog: carve out academic-prose false positives.** The humanizer / writer-critic / storyteller-critic currently flag three patterns that are legitimate in academic and experimental-design writing. Skip them in future audits:
  1. **Sentence-start `Importantly,` / `Critically,` / `Notably,`** — standard literature signals, NOT R1 signposting filler. The R1 catalog should distinguish these (academic signal) from `Of course,` / `Clearly,` / `Obviously,` (genuine filler).
  2. **`implement` for experiments** — "implement an experiment / treatment / protocol" is the field-standard verb. L3 "fancy synonyms" rule should NOT rewrite to "run" in experimental contexts.
  3. **`serves as` for role-assignment of treatments/conditions** — "Condition X serves as the control" is field-standard syntax. L4 copula-avoidance rule should NOT rewrite to "is" when the predicate names a role / function / treatment label.

  Update `.claude/rules/anti-ai-prose.md` with the carve-outs (probably as exception notes on R1, L3, L4 catalog rows). Also extend deductions in `agents/writer-critic.md` + `agents/storyteller-critic.md` to honor the carve-outs. ~30 min.
- [ ] **Land user's draft proposal at `quality_reports/plans/proposals/2026-05-07_primary-source-hook-unicode-fix.md`** — copied from BDD repo. Addresses a unicode handling gap in the primary-source regex. Distinct from the blocklist-extension TODO above; both should land together for a coherent regex hardening pass.
- [ ] **Overlay-branch sync** — applied-micro and behavioral lag main on today's universal-infrastructure commits. Cherry-pick attempt aborted 2026-05-06 due to parallel-history conflicts on `INDEX.md`, `CLAUDE.md`, `tools/SKILL.md`, etc. Properly addressed by the comprehensive propagation plan (above).
- [ ] **Possibly: `/tools sync-overlays` skill** — automate cherry-picking from main onto overlays once the universal-vs-overlay framework is in place. Out of scope until the comprehensive plan settles.
- [ ] **Replication of LFS migration to other research repos** — once BDD pilot exits successfully (D6), bulk-migrate the other research repos: `belief_distortion_discrimination_audit`, `bdm_bic`, `tx_peer_effects_local`, `va_consolidated`, etc. Per `2026-05-05_lfs-dvc-migration-plan.md` §8.
- [ ] **`/tools data-status`** — DVC-only dashboard, separate from `/tools sync-status`. Deferred until BDD pilot reveals whether the catch-all is enough.
- [ ] **Pre-commit hook to block `git push` if `dvc push` is pending** — addresses the "forgot dvc push" failure mode. Per `data-version-control.md` mitigations §3 — listed as "future" because it adds a failure mode (hook fails → push blocked). Revisit if the issue actually bites.

## Done (recent)

- [x] 2026-05-11 — Phase E: CLAUDE.md updated across all 3 branches (Skills Quick Reference row + Cross-Repo Propagation section on main); CHANGELOG entry under [Unreleased] for the comprehensive propagation infrastructure + stata skill migration; bootstrap_manifest.py deleted (throwaway per plan §6.1); related TODOs closed.
- [x] 2026-05-10 — Phase D complete + all 7 consumers pushed to origin (1417c23 / 2b865de / 535b71c / 10d6073 / cab0b7d / 5a92a04 / 287b8df). Workflow main + both overlays + tag `bootstrap-2026-05-10` all pushed. Universe consistent.
- [x] 2026-05-10 — Phase D: bootstrap complete. sync-overlays --force on applied-micro (`0def252`) + behavioral (`4f260b1`); propagate --force-initial on 7 consumers (193 file copies, 0 errors); catch-up sync-overlays --force after the resolve_patterns fix (`67b7437` / `f32f49e`). Idempotency PASS on both. Tag `bootstrap-2026-05-10` (commit `c10e276`).
- [x] 2026-05-07 — Phase C: `/tools sync-overlays` skill (`sync_overlays.py` + SKILL.md update); dry-run validates Phase A classification — applied-micro shows exactly the 5 stale-of-main files identified during the audit; behavioral pre-flight surfaced uncommitted-state blocker for Phase D
- [x] 2026-05-07 — Phase B: propagate.py class-aware routing (Manifest class + resolve_source_branch); 433 → 580 LOC; smoke-tested across all 4 routing cases (A/B/C/D) on multiple consumers; SKILL.md updated
- [x] 2026-05-07 — Phase A: `bootstrap_manifest.py` audit ran (240 paths, 118 A / 0 B / 34 C / 77 D / 16 ambiguous); user-reviewed the 16 ambiguous paths; final split = 118 A / 11 B / 34 C / 77 D; `.claude/file-classes.toml` committed; sanity-check PASS
- [x] 2026-05-07 — comprehensive propagation plan APPROVED (`9bbaeea` drafted, walked through section-by-section, all 9 reviewable decisions signed off — D5 + D7 resolved by bootstrap audit)
- [x] 2026-05-07 — comprehensive propagation plan drafted: `2026-05-07_comprehensive-propagation-plan.md`; INDEX + v1 plan status updated
- [x] 2026-05-07 — stata skill migrated from `claude-config` to workflow with Stata 14 dropped + `stata17` mandated; `.claude/rules/stata-code-conventions.md` updated with Invocation section; doc_lookup.md scoped to Stata 17 with portable paths
- [x] 2026-05-06 — propagate.py implemented (`e0425b3`); SKILL.md updated with `/tools propagate` and `/tools list-consumers` subcommands; consumers.toml created with 7 entries (gitignored)
- [x] 2026-05-06 — context-monitor.py v2 with token-based real measurement (`ad6c547`); propagated to 7 consumer repos manually; tested against BDD's transcript (matched 840.9k figure)
- [x] 2026-05-06 — comprehensive `/tools propagate` design plan written (`8a995bc`), revised to fix code-fence pairing (`4dad002`) and tx_peer_effects_paper scope (`47164b2`)
- [x] 2026-05-06 — BDD pilot Phase 1: backup, tag, dvc install, LFS enable + DVC init committed locally (`ec8d2e8`, `c2c41f0`); `dvc add data_local/` ran — 1.1 GB cached
- [x] 2026-05-06 — Phase 1 of LFS+DVC migration plan §7: data-version-control rule (`c48096a`), templates (`9cbbdac`), /tools sync-status (`ad63028`), CLAUDE.md update (`6910e84`)
- [x] 2026-05-05 — LFS+DVC migration plan + explainer (`b6b759a`); copyright reasoning stripped from workflow (`ad34e4e`); D3+D8 user-confirmed
- [x] 2026-05-05 — MacDown markdown-compat rule v2 (no space inside `$...$` delimiters); 7 broken spans fixed in BDD analysis-upgrade-memo
- [x] 2026-05-05 — Dropbox-symlink plan archived (superseded by LFS+DVC migration plan)
