# Plan: Port applied-micro overlay to new repo `csac2026`

## Context

Christina wants a new project repo at `~/github_repos/csac2026` seeded with the **applied-micro overlay** of the `claude-code-my-workflow` template. `csac` is an annual project (CSAC = California Student Aid Commission High School Senior Survey, run by the California Education Lab at UC Davis with partners CSAC + C2C). `csac2026` is the 2026 iteration. Unlike `csac2025` (registered as `overlay = main`), this one should use the richer **applied-micro** overlay (adds `/strategize`, `/balance`, `/event-study` skills, the `strategist` agent, identification checklists, and applied-micro journal profiles).

The overlay lives on the `applied-micro` branch / worktree (`~/github_repos/claude-code-my-workflow-applied-micro`). It is currently **stale vs `main`** — 24 hooks vs main's 40, missing recent Class A infrastructure (`derive_lib.py`, `evidence-gate-recorder.py`, `normdiff_lib.py`, `citation_existence_lib.py`, etc.). So the overlay must be brought current before seeding.

The workflow has a propagation system (`.claude/state/consumers.toml` + per-consumer `workflow-sync.json`) that keeps consumer repos in sync via `/tools propagate`. csac2026 should be registered as a new applied-micro consumer so future workflow updates flow to it. Routing is driven by the **declared `overlay` field** in `consumers.toml`, not the consumer's git branch — confirmed by `va_consolidated` (git branch `main`, declared `applied-micro`, carries all Class C files). So csac2026 will be its own fresh-history repo on its own `main` branch, declared `applied-micro`.

## Confirmed decisions

1. **Overlay currency** — sync the `applied-micro` overlay to current `main` *first*, then seed (csac2026 gets current infrastructure).
2. **Git remote** — local only: fresh `git init` + initial commit, no GitHub repo, no push.
3. **Project identity** — pre-fill `CLAUDE.md` / `README.md` from csac2025's stable identity (CEL / UC Davis, CSAC + C2C partners, Stata, server execution, applied-micro framing); mark year-specific fields (deliverables, status, dataset year) as TBD placeholders. No fabricated 2026 specifics.

## Approach

### Phase A — Bring the applied-micro overlay current (workflow-source maintenance)

Run from `~/github_repos/claude-code-my-workflow` (main):

```
python3 .claude/skills/tools/sync_overlays.py --dry-run    # review
python3 .claude/skills/tools/sync_overlays.py              # apply
```

This pushes current Class A files from `main` into the `applied-micro` (and `behavioral`) overlay worktrees and **auto-commits one sync commit per overlay** (`sync_overlays.py:219-244`). Only Class A files are touched; Class B/C overlay files are untouched by design. After this, `~/github_repos/claude-code-my-workflow-applied-micro` is a complete, current applied-micro overlay tree. Fully reversible (it's a normal git commit on the worktree branch).

### Phase B — Seed csac2026 from the synced overlay tree (fresh history)

```
mkdir ~/github_repos/csac2026
git -C ~/github_repos/claude-code-my-workflow archive applied-micro | tar -x -C ~/github_repos/csac2026
```

`git archive applied-micro` exports the committed tree of the (now-current) overlay branch — no `.git`, no `.claude/state/*` (gitignored, so `consumers.toml` / `verification-ledger.md` do **not** carry over). csac2026 starts as a clean working tree of the full applied-micro overlay.

### Phase C — Reset workflow-meta state to a clean project starting point

The overlay branch carries the *workflow template's own* project state. Reset these so csac2026 starts empty:

| Path | Action |
|---|---|
| `CLAUDE.md` | Fill placeholders; applied-micro framing; identity pre-filled from csac2025, year-specific fields = TBD |
| `README.md` | Replace with csac2026 project README (modeled on csac2025) |
| `TODO.md` | Reset to clean 4-section template (remove workflow "Guide site" backlog) |
| `MEMORY.md` | Reset to project stub |
| `CHANGELOG.md` | Reset to a single "project initialized" entry |
| `CONTRIBUTING.md` | Remove (it's the workflow template's contributor guide; csac2025 has none) |
| `quality_reports/plans/*` | Remove workflow-dev plans; keep `README.md`, `.gitkeep`, `archive/.gitkeep`; reset `INDEX.md` to empty |
| `quality_reports/session_logs/*` | Remove workflow-dev logs; keep `.gitkeep` |
| `decisions/` | Already clean (`README.md` only) — leave |
| `master_supporting_docs/stata-block-comment-bug-field-guide.md` | Keep (useful universal Stata field guide, Class A) |
| `.claude/skills/tools/bootstrap_manifest.py` | Keep (inert in a consumer; harmless) |

Empty scaffold dirs (`scripts/{stata,R,python}`, `paper/`, `talks/`, `tables/`, `figures/`, `data/`, `replication/`, `explorations/`) keep their `.gitkeep`s as-is.

### Phase D — Initialize git (local only)

```
cd ~/github_repos/csac2026
git init
git add -A
git commit -m "Initialize csac2026 from applied-micro overlay"
```

Fresh history; default branch `main`; no remote.

### Phase E — Register csac2026 as an applied-micro consumer

1. Append to `~/github_repos/claude-code-my-workflow/.claude/state/consumers.toml` (gitignored, local only):

   ```
   [[consumer]]
   path = "~/github_repos/csac2026"
   overlay = "applied-micro"
   note = "2026 CSAC HS senior survey; applied-micro overlay"
   ```

2. Establish the sync baseline so future `/tools propagate` tracks csac2026:

   ```
   python3 .claude/skills/tools/propagate.py --dry-run --force-initial \
     '.claude/**' 'templates/**' '.gitignore' '.gitattributes' 'LICENSE'
   # review (expect ~all "in-sync" since the seed already came from these branches), then:
   python3 .claude/skills/tools/propagate.py --force-initial \
     '.claude/**' 'templates/**' '.gitignore' '.gitattributes' 'LICENSE'
   ```

   This writes `~/github_repos/csac2026/.claude/state/workflow-sync.json` (the per-file tracking baseline with `class` + `source_branch`). Project-identity files (`CLAUDE.md`, `README.md`) are Class D — never touched by propagate, so the Phase-C custom versions survive. If propagate auto-commits the baseline in csac2026, that's expected; otherwise the `workflow-sync.json` is gitignored and needs no commit.

## Files created / modified

- **New repo:** `~/github_repos/csac2026/` (full applied-micro overlay tree, fresh git history)
- **Modified in workflow source:** `applied-micro` (+ `behavioral`) overlay worktree branches get one `sync(overlays)` commit each (Phase A); `~/github_repos/claude-code-my-workflow/.claude/state/consumers.toml` gains the csac2026 entry (gitignored, local).

## Verification

1. `ls ~/github_repos/csac2026/.claude/skills/` shows `strategize`, `balance`, `event-study` (applied-micro Class C present).
2. `ls ~/github_repos/csac2026/.claude/agents/strategist.md` exists; `ls .../designer.md` does **not** (no behavioral bleed).
3. `ls ~/github_repos/csac2026/.claude/hooks/ | wc -l` == 40 (current main count) — confirms overlay was synced, not stale.
4. `python3 -c "import tomllib; ..."` or a `grep` confirms csac2026 appears in `consumers.toml` with `overlay = "applied-micro"`.
5. `cat ~/github_repos/csac2026/.claude/state/workflow-sync.json | python3 -m json.tool | head` shows `"overlay": "applied-micro"` and per-file `source_branch` records.
6. `git -C ~/github_repos/csac2026 log --oneline` shows a clean single initial commit (fresh history, no workflow meta-history).
7. `TODO.md`, `CLAUDE.md` reflect csac2026 identity (no leftover "Guide site v1" / template `[PLACEHOLDERS]` for filled fields).
8. `python3 .claude/skills/tools/propagate.py --dry-run '.claude/rules/*.md'` from the source lists csac2026 and reports its rules `in-sync`.

## Notes / out of scope

- No GitHub remote, no push (per decision 2). Adding a remote later is a one-liner.
- Phase A also advances the `behavioral` overlay (sync_overlays processes all overlays); that's a harmless, intended side effect of keeping overlays current.
- Data/PII: only `.gitkeep`s are seeded under `data/`; no real data is created or moved.
- The destructive-action guard is not triggered (no `rm -rf` on shared storage, no history rewrite, no force-push).
