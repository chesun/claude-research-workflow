# LFS + DVC Migration Plan — Replacing Dropbox-Symlink Approach

**Date:** 2026-05-05
**Status:** Active (DRAFT — pending user approval at decision points marked **[USER]**)
**Supersedes:** `quality_reports/plans/archive/2026-05-01_dropbox-symlink-setup-explainer.md`
**Authors:** Christina + Claude
**Companion explainer:** `2026-05-05_lfs-vs-dvc-explainer.md` (concept-level overview; this plan is the execution doc)
**Dependencies:** none blocking; coauthor coordination required for repos with shared collaborators

Concrete plan to migrate gitignored bulk content (paper PDFs, raw and cleaned data) into proper version control. Replaces the prior Dropbox-symlink proposal with a Git LFS (paper PDFs) + DVC (data) split, plus a periodic Dropbox push as a no-tool-required backup tier.

---

## 0. Decisions settled in this plan

These were open in the explainer; this plan locks proposed answers and flags which ones need explicit **[USER]** approval before execution.

| # | Decision | Locked answer | Needs user approval? |
|---|---|---|---|
| D1 | LFS pricing tier | Start on GitHub free tier (1 GB storage + 1 GB/mo bandwidth). Self-host only if pilot exceeds free tier within 30 days. | No — reversible |
| D2 | Pilot project | `belief_distortion_discrimination` (PRIVATE; PDFs gitignored; no coauthors blocking) | No — explainer already proposed this |
| D3 | History migration of pre-existing committed PDFs | Skip `git lfs migrate import`. Fresh-start: new PDFs from migration date go to LFS; any PDFs already in normal git history stay there. Migrate history only if a specific repo's `.git/` becomes problematically large. | **[USER]** — coauthor history-rewrite implications |
| D4 | Workflow integration scope | Add `data/MANIFEST.md` + `data/PROVENANCE.md` + `data/CHANGELOG.md` templates. Add new rule `data-version-control.md`. Add `/tools sync-status` skill (replaces idea of `/tools sync-dropbox`; reports LFS + DVC + Dropbox state in one view). Defer `/tools data-status` until after pilot. | No — reversible |
| D5 (NEW) | Per-repo LFS opt-in | Workflow template ships with PDFs gitignored by default (repo-bloat reasons; not all forks have LFS configured). Each project decides per-repo whether to enable LFS. No public/private distinction in the policy. | No — design choice |
| D6 (NEW) | Pilot exit criteria | After 7 days of pilot use, decide go / no-go for bulk migration based on: (i) zero hook regressions, (ii) zero `dvc push` failures, (iii) workflow disruption felt as "low" by Christina, (iv) GitHub LFS bandwidth consumption < 200 MB/wk. | No |
| D7 (NEW) | DVC remote location | Local Dropbox folder (`~/Dropbox/research-data/<proj>/dvc-cache/`). Reuses existing Dropbox plan, no new cloud account. | No — change later if needed |
| D8 (NEW) | Coauthor onboarding policy | For repos with active coauthors, notify before migration with a one-paragraph email + a setup-machine.sh script they run once. No silent rewrites. | **[USER]** — per-project list |

The two **[USER]** decisions are flagged in §13. Everything else proceeds on Christina's go-ahead.

---

## 1. Background and motivation

### 1.1 What we're solving

Three content classes currently mishandled:

1. **Paper PDFs.** Load-bearing (the `primary-source-first` hook gates citations on their presence) but gitignored to keep template repo size down. Result: every fresh clone is missing the PDFs; sessions block on hook failures until the user manually re-supplies them. No version history of which papers were in scope at which paper revision.
2. **Data files (raw and cleaned).** Gitignored due to PII and size concerns. Result: zero version control. Coming back to a project after years means losing track of which dataset version produced which result. No reproducibility across time.
3. **Generated bulk artifacts** (`.rds` caches, build outputs, intermediate plots). Currently gitignored. Result: regenerable from scripts; no fix needed. *Out of scope for this plan.*

### 1.2 Why not Dropbox-symlink (the prior plan)

The prior plan proposed `~/.../master_supporting_docs/literature/papers/` symlinking into Dropbox. Three problems:

- **No version control.** Dropbox sync gives you the latest version; it doesn't let you ask "what PDFs did I have when I wrote the JMP draft." Same data-history blind spot.
- **`rm -rf` blast radius.** A delete inside the symlinked path propagates to Dropbox and to all coauthors. The destructive-action-guard catches this *if* realpath resolution works as documented, but the failure mode is severe enough that avoiding it entirely is worth more than mitigating it.
- **Hook entanglement.** Three workflow hooks touch this path. Each one is a place for symlink-aware vs symlink-unaware behavior to diverge silently.

LFS solves all three: real version control, no shared-storage blast radius (LFS is a separate HTTP store), zero hook entanglement (filesystem semantics are unchanged from a normal repo).

### 1.3 Why not Dropbox-only periodic sync (the user's earlier suggestion)

Periodic sync is fine as a *backup* (and we'll keep it as a tier-3 safety net) but doesn't solve the version control gap. "What was the data in 2026" still requires manual snapshotting. DVC adds a thin layer on top of the same Dropbox storage to give you that.

---

## 2. Architecture: three content classes

| Class | Storage | Versioning | Examples |
|---|---|---|---|
| **A — Tracked in git directly** | `.git/` (this repo's normal storage) | Real (git history) | All code, LaTeX, ADRs, plans, session logs, reading notes (`*.md`), `data/MANIFEST.md`, `data/PROVENANCE.md`, `data/CHANGELOG.md`, the `.dvc/` config, individual `.dvc` pointer files |
| **B — Tracked via Git LFS** | LFS server (GitHub LFS for free tier; pointer in repo) | Real (git history; pointers commit normally) | Paper PDFs (`master_supporting_docs/literature/papers/*.pdf`), talk PDFs (`talks/*.pdf` if compiled outputs are kept), any large generated figure PDFs explicitly chosen to be tracked |
| **C — Tracked via DVC** | DVC cache in `~/Dropbox/research-data/<proj>/dvc-cache/`; pointer (`*.dvc`) in repo | Real (git history of pointers + content-addressed cache) | Raw data (`data/raw/*`), cleaned data (`data/cleaned/*`), large derived datasets that are expensive to regenerate |
| **D — Gitignored, periodic backup** | Local repo path + `~/Dropbox/research-data/<proj>/backup/` (rsync mirror) | None | `.rds` caches, build artifacts, intermediate plots, anything regenerable from scripts |

Class B and C share the same structural pattern (pointer in git + blob elsewhere) but use different tools because they have different access patterns and tooling needs. Class D is the no-tool-required tier — same as the periodic-sync proposal you raised earlier.

---

## 3. Settling the four explainer decisions

### D1: GitHub LFS pricing tier — **start free**

Free tier is 1 GB storage + 1 GB/month bandwidth. Estimate: 200 PDFs averaging 2 MB = 400 MB. Three clones per month = 1.2 GB bandwidth (over but close). If we exceed during pilot, two cheap fallbacks: (a) GitHub data pack \$5/mo, (b) self-hosted LFS via Gitea on a personal server (~2 hours setup). Decide at pilot exit (D6).

### D2: Pilot project — **`belief_distortion_discrimination`**

Reasons: active project so realistic workload; no other live coauthors blocking the migration; literature is stable (PDFs rarely added/changed) so first-week chaos is bounded.

### D3: History migration — **fresh-start, skip `git lfs migrate`**

`git lfs migrate import --include="*.pdf"` rewrites repo history to retroactively move all PDFs to LFS. It changes commit hashes — every coauthor must `git fetch && git reset --hard origin/main` (or rebase their work). For repos with active coauthors this is disruptive.

Fresh-start instead: enable LFS, ungitignore PDFs, add new PDFs going forward to LFS. Old PDFs in normal git history (if any) stay there — they're the price of the unmigrated past. Reversible: if a specific repo's `.git/` becomes problematically large later, run `git lfs migrate` then.

### D4: Workflow integration — **specific scope**

In scope for this plan:

- New `.gitattributes` template with LFS patterns
- New `data/MANIFEST.md` + `data/PROVENANCE.md` + `data/CHANGELOG.md` templates
- New rule: `.claude/rules/data-version-control.md`
- New skill: `/tools sync-status` (one command that reports LFS state, DVC state, and Dropbox-backup freshness)
- Update existing template `.gitignore` to no longer ignore PDFs in private-repo case (and add comment explaining the public/private distinction)

Out of scope for this plan:

- `/tools data-status` (a more interactive DVC-only command). Defer until pilot reveals whether the catch-all `/tools sync-status` is enough.
- Auto-pre-commit-hook for `dvc push`. Tempting, but adds a failure mode (hook fails → commit blocked). Manual `dvc push` after `git push` is fine for now.

---

## 4. Per-repo LFS opt-in

Each project decides whether paper PDFs are load-bearing enough to enable LFS. The workflow template ships with PDFs gitignored by default — not because of any legal concern, but because:

- Forks vary in whether they have LFS configured at all (default-off avoids breaking new users).
- PDFs don't diff well; tracking them in normal (non-LFS) git bloats history fast.
- Some forks may not have a substantial paper library worth versioning.

**The opt-in is a one-time per-repo decision.** When a project has paper PDFs that the `primary-source-first` hook depends on, enable LFS:

1. Comment out the two PDF lines in `.gitignore`.
2. Add the LFS pattern to `.gitattributes` (template ships in §7.2).
3. Stage and commit the existing PDFs — they go to LFS automatically.

No visibility-based distinction. The plan applies the same way to public and private repos that have a real PDF library.

---

## 5. Pre-flight: per-machine tooling install

One-time per machine (Christina's laptop, any other dev machine).

```bash
# Install both tools
brew install git-lfs dvc

# Register LFS hooks in your global git config (one-time per user)
git lfs install

# Verify
git lfs version
dvc --version
```

Coauthors on shared projects need the same install. We'll ship a `bin/setup-machine.sh` per project for this (§7.7).

---

## 6. Pilot phase: `belief_distortion_discrimination`

Estimated duration: 7 days. Goal: prove the workflow on one project before bulk migration.

### 6.1 Pre-pilot checklist

Before any commands run:

- [ ] User approval on **[USER]** decisions D3, D5, D8 (§3, §4, §13)
- [ ] Coauthor list for `belief_distortion_discrimination` — confirm: any active coauthors who'd be disrupted? (Plan assumes none; verify.)
- [ ] Backup snapshot of current repo state: `cp -R ~/github_repos/belief_distortion_discrimination ~/backups/belief_distortion_discrimination_pre-lfs-$(date +%Y%m%d)`
- [ ] Confirm Dropbox has space for DVC cache: `du -sh ~/Dropbox` and check Dropbox quota
- [ ] Confirm GitHub LFS not yet enabled on this repo: `git lfs ls-files` should show empty output

### 6.2 LFS migration steps (PDFs)

```bash
cd ~/github_repos/belief_distortion_discrimination

# Step 1 — Enable LFS on this repo and declare which patterns to track
git lfs track "master_supporting_docs/literature/papers/*.pdf"
git lfs track "master_supporting_docs/literature/papers/**/*.pdf"

# This creates/updates .gitattributes with the LFS patterns.
# Track .gitattributes itself in git (it's the source of truth for LFS routing):
git add .gitattributes
git commit -m "Enable Git LFS for paper PDFs"

# Step 2 — Remove the PDF-gitignore lines (PDFs now go to LFS instead)
# Edit .gitignore: comment out or delete:
#   master_supporting_docs/literature/papers/*.pdf
#   master_supporting_docs/literature/papers/**/*.pdf
# (Done via Edit tool; commit:)
git add .gitignore
git commit -m "Stop gitignoring paper PDFs (now LFS-tracked)"

# Step 3 — Add the existing PDFs (they're sitting locally, not in git)
git add master_supporting_docs/literature/papers/
git status   # should show new files; LFS pointers will appear in the commit
git commit -m "Add paper PDFs to LFS"

# Step 4 — Push to GitHub
git push
# This pushes commits + uploads LFS blobs. First push can be slow.

# Step 5 — Verify
git lfs ls-files   # lists LFS-tracked files with their hashes
git lfs env        # shows LFS endpoint, storage stats
```

### 6.3 DVC migration steps (data)

```bash
cd ~/github_repos/belief_distortion_discrimination

# Step 1 — Initialize DVC in the repo
dvc init
git add .dvc/.gitignore .dvc/config
git commit -m "Initialize DVC"

# Step 2 — Configure the remote (Dropbox cache path)
dvc remote add -d storage ~/Dropbox/research-data/belief_distortion_discrimination/dvc-cache
git add .dvc/config
git commit -m "Configure DVC remote (Dropbox)"

# Step 3 — Add data files to DVC
# For each path under data/raw/ and data/cleaned/ that you want versioned:
dvc add data/raw/                  # adds the whole directory
# OR file-by-file:
# dvc add data/raw/cps_2024.csv

# This creates data/raw.dvc (or data/raw/cps_2024.csv.dvc) — the pointer files.
# DVC also adds data/raw to data/.gitignore automatically, so the actual files
# don't end up in git.

git add data/raw.dvc data/.gitignore
git commit -m "Track data/raw under DVC"

# Repeat for data/cleaned/:
dvc add data/cleaned/
git add data/cleaned.dvc data/.gitignore
git commit -m "Track data/cleaned under DVC"

# Step 4 — Push blobs to remote (Dropbox cache)
dvc push

# Step 5 — Push git changes (pointers travel with git)
git push

# Step 6 — Verify
dvc status -c   # cloud status: should show "Cache and remote are in sync"
ls -la data/raw.dvc data/cleaned.dvc   # pointer files exist
```

### 6.4 Add the documentation contract files

These are normal git-tracked markdown files. Templates ship from §7.

```bash
# Copy templates from the workflow repo (after §7 lands them)
cp ~/github_repos/claude-code-my-workflow/templates/data-MANIFEST.md  data/MANIFEST.md
cp ~/github_repos/claude-code-my-workflow/templates/data-PROVENANCE.md data/PROVENANCE.md
cp ~/github_repos/claude-code-my-workflow/templates/data-CHANGELOG.md  data/CHANGELOG.md

# Fill in: what's in each file/folder, where it came from, what changed.
# For pilot: backfill from current state of data/ as best as memory allows;
# don't try to reconstruct full provenance for files >6 months old.

git add data/MANIFEST.md data/PROVENANCE.md data/CHANGELOG.md
git commit -m "Add data documentation contract"
git push
```

### 6.5 Validation

After §6.2 + §6.3 complete:

- [ ] `git lfs ls-files` lists all PDFs that should be LFS-tracked
- [ ] `git lfs env` shows endpoint and reasonable storage size
- [ ] `dvc status` shows clean (no uncommitted changes)
- [ ] `dvc status -c` shows "everything is up to date" (cloud in sync)
- [ ] Run `pdf-learnings` skill on one PDF to confirm transparent access (LFS file appears as a normal file)
- [ ] Trigger `primary-source-first` hook with a citation to a paper — should pass (PDF found via LFS)
- [ ] `du -sh ~/Dropbox/research-data/belief_distortion_discrimination/dvc-cache` shows reasonable size
- [ ] Fresh clone test: `cd /tmp && git clone <url> test-clone && cd test-clone && dvc pull` — confirm PDFs and data both materialize correctly

If any check fails, do not proceed to bulk migration; debug first.

### 6.6 Pilot duration and exit criteria (D6)

Run for 7 days of normal workflow use. Track:

| Metric | Target | How to measure |
|---|---|---|
| Hook regressions | 0 | Daily check: did `primary-source-first.py` block any legitimate citation? Did any session crash? |
| `dvc push` failures | 0 | Track in pilot session log: any `dvc push` errors |
| Workflow disruption | "Low" (subjective) | Christina rates daily 1-5; goal: avg ≥ 4 |
| LFS bandwidth consumption | < 200 MB/wk | Check via GitHub repo settings → LFS usage |
| DVC remote storage | < 5 GB | `du -sh ~/Dropbox/research-data/.../dvc-cache` |

If all five hold at day 7 → proceed to bulk migration (§8). If any fail → diagnose, possibly extend pilot, possibly back out.

---

## 7. Workflow-template changes (BEFORE bulk migration)

These changes go into `claude-code-my-workflow` first. The pilot in §6 happens in `belief_distortion_discrimination`, *using these templates*. Order:

1. Land §7 changes in `claude-code-my-workflow` on `main` (and overlay branches).
2. Pull templates into pilot repo (`belief_distortion_discrimination`) at the start of §6.
3. Pilot for 7 days.
4. Refine templates based on pilot learnings.
5. Bulk migrate remaining repos using refined templates.

### 7.1 Update `.gitignore` template

Replace the PDF block with:

```gitignore
# --- Academic PDFs ---
# Default: gitignored to keep the template repo small (PDFs don't diff well
# and bloat git history). In a fork where paper PDFs are load-bearing,
# enable Git LFS and comment these lines out — see
# .claude/rules/data-version-control.md.
master_supporting_docs/literature/papers/*.pdf
master_supporting_docs/literature/papers/**/*.pdf
```

Same gitignore lines remain by default; comment makes the LFS opt-in path discoverable. Already applied to `claude-code-my-workflow/.gitignore` on `main`; overlay branches (`applied-micro`, `behavioral`) still need syncing per the universal-gitignore plan's three-commit pattern.

### 7.2 Add `.gitattributes` template

New file: `templates/gitattributes-lfs.txt` (template; not active in the workflow repo itself since it's PUBLIC).

```gitattributes
# Git LFS routing — paper PDFs
master_supporting_docs/literature/papers/*.pdf filter=lfs diff=lfs merge=lfs -text
master_supporting_docs/literature/papers/**/*.pdf filter=lfs diff=lfs merge=lfs -text

# Optional: large generated figures (uncomment per project as needed)
# figures/**/*.pdf filter=lfs diff=lfs merge=lfs -text
# figures/**/*.png filter=lfs diff=lfs merge=lfs -text
```

Document in `templates/README.md` how to copy this into a private fork as `.gitattributes`.

### 7.3 Update `CLAUDE.md` template

Add a section after "Folder Structure":

```markdown
## Bulk Content Storage

This repo uses three content tiers:

- **Code, LaTeX, plans, ADRs, reading notes** → tracked normally in git
- **Paper PDFs** → Git LFS (see `.gitattributes`)
- **Data (`data/raw/`, `data/cleaned/`)** → DVC with Dropbox remote (see `.dvc/config`)

New machine setup:

\```bash
brew install git-lfs dvc
git lfs install
git clone <repo>
cd <repo>
dvc pull   # downloads data files from Dropbox cache
\```

For a full architecture description and rollback procedures, see
`.claude/rules/data-version-control.md`.
```

### 7.4 New rule: `.claude/rules/data-version-control.md`

A canonical reference for the LFS+DVC architecture. Sections:

- Three content classes (the table from §2 of this plan)
- LFS workflow (daily commands, when LFS kicks in, what changes about `git push`)
- DVC workflow (daily commands, the two-step `git push && dvc push` rhythm)
- The data-doc contract (`MANIFEST.md`, `PROVENANCE.md`, `CHANGELOG.md`)
- Coauthor onboarding
- Rollback (LFS off, DVC off)
- Failure modes table (LFS bandwidth exceeded, DVC remote unreachable, pointer-without-blob, etc.)

Length target: ~150 lines. Patterned on existing rules.

### 7.5 New skill: `/tools sync-status`

Sub-skill of the existing `/tools` skill. Output (one screen):

```
=== Git LFS ===
Tracked patterns:    [list from .gitattributes]
LFS files in repo:   N files, M MB total
Endpoint:            <url>
This-month bandwidth: X MB used / 1024 MB free tier
This-month storage:  Y MB used / 1024 MB free tier

=== DVC ===
Remote:              <path>
Pending uploads:     N files (run: dvc push)
Pending downloads:   N files (run: dvc pull)
Pointer count:       M

=== Periodic Dropbox backup (Class D) ===
Last run:            YYYY-MM-DD HH:MM
Mirror size:         X GB
Stale paths:         [if any path is in repo but not in mirror]
```

Implementation: a Bash script that wraps `git lfs ls-files`, `git lfs env`, `dvc status -c`, and a stat on the Dropbox backup dir. Lives in `.claude/skills/tools/sync-status.sh` (called by `/tools sync-status`).

### 7.6 Hook compatibility verification (no changes expected)

LFS is invisible at the filesystem layer — `Read`, `ls`, `find`, and Python `open()` all see the LFS-materialized file as a normal file. So no hook changes expected. But verify:

- [ ] `primary-source-check.py` (PreToolUse on Edit/Write) — runs `Read` on PDFs. Should work transparently. **Test:** with a pilot PDF, edit a markdown file with a citation; hook should pass.
- [ ] `primary-source-audit.py` (Stop hook) — scans transcript for citations, looks up reading notes (which are in regular git, unaffected). **Test:** session-end with a citation should not block.
- [ ] `destructive-action-guard.py` (PreToolUse on Bash) — checks `realpath()` of paths. LFS file's realpath is `<repo>/master_supporting_docs/literature/papers/foo.pdf` (no Dropbox involvement). DVC files' realpath is `<repo>/data/raw/...` (the materialized file in the working tree, also no Dropbox involvement). **Test:** `rm -rf data/raw/test-file` from inside a DVC repo should NOT trigger the guard, since the working tree is in `~/github_repos/`, not in shared storage.
- [ ] `pdf-learnings` skill (calls Ghostscript on PDFs) — should work transparently. **Test:** run on one pilot PDF and confirm chunked extraction succeeds.

If any test fails during pilot, escalate; this plan does not commit to silently working around hook regressions.

### 7.7 Per-repo `bin/setup-machine.sh`

A one-shot script in each research repo that bootstraps a new machine for that repo. Generated from a template with project-specific bits filled in.

Template (`templates/setup-machine.sh`):

```bash
#!/usr/bin/env bash
# setup-machine.sh — bootstrap this repo on a new machine
set -euo pipefail

PROJECT="$(basename "$(git rev-parse --show-toplevel)")"
echo "Setting up $PROJECT for this machine..."

# 1. Verify tools
command -v git-lfs >/dev/null || { echo "Install git-lfs first: brew install git-lfs"; exit 1; }
command -v dvc >/dev/null || { echo "Install dvc first: brew install dvc"; exit 1; }

# 2. Initialize LFS (idempotent)
git lfs install --local
git lfs pull

# 3. Initialize DVC pull (idempotent)
if [ -d .dvc ]; then
  dvc pull
fi

# 4. Verify
echo "=== Setup verification ==="
echo "LFS files:  $(git lfs ls-files | wc -l) tracked"
[ -d .dvc ] && echo "DVC status: $(dvc status -c 2>&1 | head -1)"

echo "Done. Safe to start working."
```

Per-repo `bin/setup-machine.sh` is a copy with PROJECT-specific notes appended (e.g., "this repo uses Stata 17; install via Stata website").

Lives in each project's `bin/` (gitignored otherwise — empty by default; populated only if the project has a setup script).

---

## 8. Bulk migration (after pilot exits)

### 8.1 Repo inventory

Research repos likely needing migration (from `~/github_repos/`):

| Repo | Has PDFs? | Has data? | Coauthors? | LFS migrate | DVC init |
|---|---|---|---|---|---|
| `belief_distortion_discrimination` | Yes | Yes | TBD | Yes (pilot) | Yes (pilot) |
| `tx_peer_effects_paper` | Yes | Yes | Yes (3) | Yes | Yes |
| `tx_peer_effects_local` | TBD | TBD | TBD | TBD | TBD |
| `bdm_bic` / `bdm_bic_paper` | TBD | TBD | TBD | TBD | TBD |
| `belief_distortion` | TBD | TBD | TBD | TBD | TBD |
| `csac` / `csac_2024` / `csac2025` | TBD | TBD | TBD | TBD | TBD |
| `jmp_paper_overleaf` | TBD (LaTeX-only?) | No | TBD | TBD | No |
| `va_paper_clone` / `va_consolidated` / `cde_va_project_fork` | TBD | TBD | TBD | TBD | TBD |

Repos confirmed to skip (no load-bearing PDFs / no project data):

- `claude-code-my-workflow` (template — no own PDFs)
- `chesun.github.io` (Jekyll site — no academic content)
- `latex_templates`, `dissertation_template`, `replications`, `stata-binscatter2` (utility / template repos)

**[USER]** Per-repo confirmation needed in §13 before §8.2 runs.

### 8.2 Per-repo playbook

For each in-scope repo, in order of priority (Christina decides priority):

1. **Coauthor notify** (per D8). Email template in §9.1.
2. **Pre-flight backup** (cp -R to ~/backups/).
3. **Run LFS migration steps** (§6.2 lifted as a script: `bin/migrate-lfs.sh`).
4. **Run DVC migration steps** (§6.3 as `bin/migrate-dvc.sh`).
5. **Add doc contract** (§6.4).
6. **Validation** (§6.5).
7. **Coauthor notify** (migration complete; pull instructions).
8. **Update INDEX.md** in this workflow repo with migration date per project.

Estimated time per repo: 30–60 minutes including coauthor notify + validation. Can parallelize 2–3 per session if no shared coauthors.

### 8.3 Coauthor coordination

For each repo with active coauthors:

- Send email at least 24 hours before migration.
- Tag the pre-migration commit so coauthors can checkout if migration breaks them.
- After migration, send the setup-machine.sh + a one-paragraph "what changed" summary.
- Be available for 1 day to debug coauthor setup issues.

Email template in §9.

---

## 9. Coauthor onboarding

### 9.1 Notification email template

```
Subject: [<Project>] Storage migration scheduled <date>: Git LFS + DVC

Hi <coauthor>,

I'm migrating <project> to use Git LFS for paper PDFs and DVC for data
files starting <date>. This means:

- Paper PDFs (currently gitignored — you've been adding them locally)
  will move into the repo via Git LFS, so they auto-clone. No more
  manual PDF management on new machines.
- Data files in `data/raw/` and `data/cleaned/` will be tracked via
  DVC. The actual data still lives off-GitHub (in my Dropbox cache,
  shared with you), but git will track which data version corresponds
  to which paper version.

What you need to do AFTER the migration completes:

  brew install git-lfs dvc
  git lfs install
  cd <project>
  git pull
  ./bin/setup-machine.sh

That last script does `git lfs pull` and `dvc pull` for you. ~5 minutes.

I'll send a follow-up when migration is done. If anything breaks for you
afterward, reply to this thread and I'll fix it.

Pre-migration commit tag (in case we need to roll back): <tag>

Best,
Christina
```

### 9.2 Per-machine setup doc

In each repo: `bin/SETUP.md` describing:

- Required tools (`git-lfs`, `dvc`)
- Run `./bin/setup-machine.sh`
- Daily workflow (when to `dvc push`, when to `git lfs pull`)
- Troubleshooting (common errors and fixes)

Template ships from §7.7.

---

## 10. Rollback plans

### 10.1 LFS rollback (single repo)

If LFS proves problematic in pilot or in a specific repo:

```bash
# 1. Convert LFS files back to normal git blobs
git lfs migrate export --include="*.pdf" --everything

# 2. Disable LFS tracking
git lfs uninstall
rm .gitattributes   # or edit out the LFS lines

# 3. Force-push (coauthor coordination required — same hash-rewrite issue as migrate import)
git push --force-with-lease

# 4. Re-add the gitignore lines for PDFs (or just live with PDFs in normal git history,
#    which is the no-LFS state pre-migration)
```

**Cost:** for repos with substantial PDF history, this rewrites history and disrupts coauthors. Worth the cost only if LFS is causing real problems.

### 10.2 DVC rollback (single repo)

```bash
# 1. Materialize all DVC-tracked files into the repo
dvc unprotect data/

# 2. Remove DVC pointers from git
git rm data/raw.dvc data/cleaned.dvc
rm -rf .dvc/

# 3. Add data/ back to .gitignore (PII concern — don't accidentally commit data)
echo "data/raw/" >> .gitignore
echo "data/cleaned/" >> .gitignore

# 4. Commit + push
git add .gitignore
git commit -m "Roll back DVC; data is gitignored again"
git push
```

DVC rollback is cleaner than LFS rollback — no history rewrite needed.

### 10.3 Full plan rollback

If the whole approach proves wrong: roll back per-repo (10.1 + 10.2), revert workflow-template changes (§7), restore the prior `.gitignore` from `2026-04-21_universal-gitignore.md`. Resurrect the Dropbox-symlink plan from `archive/` if Christina wants to retry that approach instead.

---

## 11. Cost monitoring

### 11.1 GitHub LFS

Check monthly via GitHub repo Settings → Git LFS:

- Storage used / 1024 MB free
- Bandwidth used (this month) / 1024 MB free

If approaching 80%: decide between (a) data pack purchase \$5/month for 50 GB, (b) self-hosted LFS server, (c) prune unused LFS history (`git lfs prune`).

### 11.2 Dropbox

Check via Dropbox app → Account → Storage:

- Total used / quota
- DVC cache size: `du -sh ~/Dropbox/research-data/*/dvc-cache`

### 11.3 Reporting

Add to weekly session log if anything notable. No automation needed for now — manual check during normal Dropbox/GitHub UI use is fine.

---

## 12. Timeline

Realistic, assuming Christina has ~1-2 hours/day for migration work:

| Phase | Estimated duration | Calendar dates (target) |
|---|---|---|
| Phase 0: User approval on **[USER]** decisions | 1 day | 2026-05-05 to 2026-05-06 |
| Phase 1: Workflow-template updates (§7) | 2-3 days | 2026-05-07 to 2026-05-09 |
| Phase 2: Pilot setup (§6.1–§6.4) on `belief_distortion_discrimination` | 1 day | 2026-05-10 |
| Phase 3: Pilot run (§6.5–§6.6) | 7 days | 2026-05-10 to 2026-05-17 |
| Phase 4: Pilot exit decision | 1 day | 2026-05-18 |
| Phase 5: Bulk migration (§8) | ~1 hour per repo, parallelized | 2026-05-19 onward |
| Phase 6: Final docs + retrospective | 1 day | After Phase 5 |

Total: ~3-4 weeks calendar time, ~10-15 hours of focused work.

---

## 13. Open questions for user approval **[USER]**

Two items need explicit yes/no before §6 begins:

1. **D3 — History migration.** Confirm: skip `git lfs migrate import`; live with whatever PDFs are in normal git history pre-migration. Yes / No.
2. **D8 — Coauthor list.** Confirm which repos have active coauthors who need notification. List per repo. (Plan will not migrate any repo with active coauthors until you confirm notification is sent.)

Three additional items become relevant only at pilot exit (D6) — not blocking now:

3. Pilot exit decision — go / no-go for bulk migration, based on the five metrics in §6.6.
4. Bulk migration order — which repo first after pilot.
5. Whether to add `/tools data-status` (DVC-only command separate from `/tools sync-status`).

---

## 14. What this does NOT solve

- **PII leakage from prior commits.** If `data/raw/` contained PII and was *ever* committed in any prior history (now-gitignored but still in `.git/objects/`), this plan does not scrub it. Audit `git log --all --diff-filter=A -- 'data/**'` per repo to check; use `git filter-repo` if needed (a destructive operation — see `destructive-actions.md`).
- **DVC remote encryption.** DVC blobs in Dropbox are protected by Dropbox's standard encryption. For higher sensitivity, configure DVC with an encrypted S3 remote (out of scope for v1).
- **Backup of the LFS server.** GitHub LFS storage relies on GitHub's reliability. For belt-and-suspenders, mirror periodically: `git lfs fetch --all && git lfs push <secondary-remote>`. Out of scope until first incident.
- **Coauthors who refuse to install DVC.** This plan assumes coauthors will install. If a coauthor refuses, fall back: that repo stays in the gitignore + Dropbox-backup model (Class D for everything), and we accept the version-control gap.
- **Migration of the workflow repo's own session-log PDFs / artifacts.** `claude-code-my-workflow` is public; doesn't need LFS for PDFs. No DVC either since it has no `data/`. This plan only changes its `templates/` and `.claude/rules/` and `.gitignore` template — not its content storage architecture.

---

## Cross-references

- **Companion explainer:** `2026-05-05_lfs-vs-dvc-explainer.md` — concept-level Git LFS / DVC primer
- **Superseded:** `archive/2026-05-01_dropbox-symlink-setup-explainer.md` — prior approach
- **Universal gitignore:** `2026-04-21_universal-gitignore.md` — template currently in force; §7.1 of this plan revises one block
- **Destructive actions rule:** `.claude/rules/destructive-actions.md` — relevant to history-rewrite operations (D3, §10.1)
- **Primary-source-first rule:** `.claude/rules/primary-source-first.md` — hooks that depend on PDFs being readable; verified compatible with LFS in §7.6
