# TODO — claude-code-my-workflow

Last updated: 2026-05-06

Project-wide tracker per `.claude/rules/todo-tracking.md`. Active session-tracker tasks (TaskCreate) are working memory; this file is the persistent cross-session record.

## Active (doing now)

- *(nothing actively being worked on — BDD pilot paused on user; comprehensive propagation plan deferred to fresh-context session)*

## Up Next

- [ ] **Write comprehensive propagation plan** — universal vs overlay file taxonomy; how `propagate.py` routes per file class; how `main → overlay` itself stays in sync. Save to `quality_reports/plans/2026-05-NN_comprehensive-propagation-plan.md`. Will supersede the partial `2026-05-06_tools-propagate-plan.md`. (Identified 2026-05-06 evening when cherry-pick attempt surfaced parallel-history complexity in overlays.)
- [ ] **After comprehensive plan lands**: bootstrap `workflow-sync.json` across the 7 consumers via the now-correct propagate routing; verify idempotency with a re-run.
- [ ] **Resume BDD pilot** — wait for user "resume" signal. Tasks #5–#12 in tracker; first action is soft-migrate 60 existing PDFs to LFS pointers (already approved 2026-05-06).

## Waiting On

- [ ] **BDD pilot resumption** — user actively running tasks in BDD; will signal "resume" when done. State preserved: 2 BDD commits already landed locally (`ec8d2e8` LFS enable, `c2c41f0` DVC init), 1.1 GB cached in `.dvc/cache/`, `data_local.dvc` pointer uncommitted. Tag `pre-lfs-dvc-migration-2026-05-06` is the rollback target.
- [ ] **D6 — pilot exit decision** (after pilot's 7-day run) — go/no-go on bulk migration based on the five §6.6 metrics in the LFS+DVC plan.

## Backlog

- [ ] **`~/.claude/settings.json` drift** — diverged ~50 days from `claude-config/settings.json` (193 vs 81 bytes). Per `sync-global-config.md`, the live file should be copied to the repo and committed. Small task; ~10 min.
- [ ] **Add `Resolved` / `Pending` / `Deferred` / `Open` to `NEVER_SURNAMES` blocklist** in `.claude/hooks/primary_source_lib.py`. Caught as a false-positive twice today on bracketed-year text like `[Resolved 2026-05-05]`. ~5 lines + test.
- [ ] **Overlay-branch sync** — applied-micro and behavioral lag main on today's universal-infrastructure commits. Cherry-pick attempt aborted 2026-05-06 due to parallel-history conflicts on `INDEX.md`, `CLAUDE.md`, `tools/SKILL.md`, etc. Properly addressed by the comprehensive propagation plan (above).
- [ ] **Possibly: `/tools sync-overlays` skill** — automate cherry-picking from main onto overlays once the universal-vs-overlay framework is in place. Out of scope until the comprehensive plan settles.
- [ ] **Replication of LFS migration to other research repos** — once BDD pilot exits successfully (D6), bulk-migrate the other research repos: `belief_distortion_discrimination_audit`, `bdm_bic`, `tx_peer_effects_local`, `va_consolidated`, etc. Per `2026-05-05_lfs-dvc-migration-plan.md` §8.
- [ ] **`/tools data-status`** — DVC-only dashboard, separate from `/tools sync-status`. Deferred until BDD pilot reveals whether the catch-all is enough.
- [ ] **Pre-commit hook to block `git push` if `dvc push` is pending** — addresses the "forgot dvc push" failure mode. Per `data-version-control.md` mitigations §3 — listed as "future" because it adds a failure mode (hook fails → push blocked). Revisit if the issue actually bites.

## Done (recent)

- [x] 2026-05-06 — propagate.py implemented (`e0425b3`); SKILL.md updated with `/tools propagate` and `/tools list-consumers` subcommands; consumers.toml created with 7 entries (gitignored)
- [x] 2026-05-06 — context-monitor.py v2 with token-based real measurement (`ad6c547`); propagated to 7 consumer repos manually; tested against BDD's transcript (matched 840.9k figure)
- [x] 2026-05-06 — comprehensive `/tools propagate` design plan written (`8a995bc`), revised to fix code-fence pairing (`4dad002`) and tx_peer_effects_paper scope (`47164b2`)
- [x] 2026-05-06 — BDD pilot Phase 1: backup, tag, dvc install, LFS enable + DVC init committed locally (`ec8d2e8`, `c2c41f0`); `dvc add data_local/` ran — 1.1 GB cached
- [x] 2026-05-06 — Phase 1 of LFS+DVC migration plan §7: data-version-control rule (`c48096a`), templates (`9cbbdac`), /tools sync-status (`ad63028`), CLAUDE.md update (`6910e84`)
- [x] 2026-05-05 — LFS+DVC migration plan + explainer (`b6b759a`); copyright reasoning stripped from workflow (`ad34e4e`); D3+D8 user-confirmed
- [x] 2026-05-05 — MacDown markdown-compat rule v2 (no space inside `$...$` delimiters); 7 broken spans fixed in BDD analysis-upgrade-memo
- [x] 2026-05-05 — Dropbox-symlink plan archived (superseded by LFS+DVC migration plan)
