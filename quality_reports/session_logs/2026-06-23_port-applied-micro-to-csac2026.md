# 2026-06-23 — Port applied-micro overlay to new repo `csac2026`

## Goal

Seed a new project repo at `~/github_repos/csac2026` from the **applied-micro overlay** of `claude-code-my-workflow`, register it as an applied-micro consumer, and bring the overlay current first so the seed carries current infrastructure. Plan: `quality_reports/plans/2026-06-23_port-applied-micro-to-csac2026.md`.

## What happened

1. **Phase A — overlay currency.** Ran `sync_overlays.py` to push current Class A files from `main` into the `applied-micro` (and `behavioral`) overlay worktrees. The overlay was stale (24 hooks) and came current (35 real hooks) before seeding.
2. **Phase B — seed.** `git archive applied-micro | tar -x` into `~/github_repos/csac2026` — clean working tree of the current overlay, no `.git`, no gitignored `.claude/state/*`.
3. **Phase C — reset workflow-meta state.** Filled `CLAUDE.md` / `README.md` with csac2026 identity (CEL / UC Davis, CSAC + C2C partners, Stata, applied-micro framing) modeled on csac2025's stable identity; year-specific fields left as TBD. Reset `TODO.md` / `MEMORY.md` / `CHANGELOG.md`; cleared workflow-dev plans and session logs.
4. **Phase D — git init (local only).** Fresh history, default branch `main`, no remote.
5. **Phase E — register consumer.** Added the csac2026 entry to `consumers.toml` (`overlay = "applied-micro"`) and established the propagate baseline (`workflow-sync.json`).
6. **Post-seed.** Two follow-on commits in csac2026: a `workflow-sync` propagation (`b152655`) and a data-gitignore commit for restricted survey data (`a919a09`).

## Verification (all pass)

| Check | Result |
|---|---|
| applied-micro Class C skills present | ✅ `strategize`, `balance`, `event-study` |
| `strategist` agent present, `designer` absent (no behavioral bleed) | ✅ |
| Hook parity with overlay/main | ✅ 35 real hooks (main's "36" was `__pycache__`) |
| Consumer registered as applied-micro | ✅ `consumers.toml` entry, note "seeded 2026-06-23" |
| `workflow-sync.json` baseline written | ✅ 39 KB, per-file `source_branch` records |
| csac2026 git history clean | ✅ 3 commits, fresh history, working tree clean |
| CLAUDE.md reflects csac2026 identity | ✅ CEL / UC Davis / CSAC + C2C / Stata |

## State / open items

- **csac2026 is local-only by design** (decision 2: no GitHub remote, no push). Adding a remote later is a one-liner.
- Year-specific CLAUDE.md fields (deliverables, status, dataset year) remain TBD placeholders — to fill when 2026 survey specifics are known.

## Loose ends tied up this session

- Committed the plan (was untracked) and added it to `quality_reports/plans/INDEX.md`.
- Wrote this session log (the port had none).
- **Consumer recovery-push audit** (open question from `2026-05-31_consumer-claudemd-recovery`): re-checked push state of all 7 recovery commits. **6 of 7 are already pushed** to their GitHub remotes (BDD, bdm_bic, csac, csac2025, tx_peer_effects_local, va_consolidated — all 0 ahead / 0 behind on the recovered branch). **1 remains local-only:** `belief_distortion_discrimination_audit` `audit-fix` is 3 commits ahead of `origin/audit-fix` — those 3 are exactly the recovery sequence (`4e7962a` initial restore → `155c1e0` documented intermediate mistake → `cd985f7` correction; net CLAUDE.md restored, README removed). Pending user authorization to push to the shared remote.

## Files touched (this repo)

- `quality_reports/plans/2026-06-23_port-applied-micro-to-csac2026.md` (committed)
- `quality_reports/plans/INDEX.md` (added 2026-06 entry)
- `quality_reports/session_logs/2026-06-23_port-applied-micro-to-csac2026.md` (this file)
- `.claude/state/consumers.toml` (csac2026 entry — gitignored, local)
