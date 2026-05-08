# Data Version Control

**Scope:** all research projects with paper PDFs as load-bearing content, or with data files that need versioning beyond plain backup.

**Companion files:**

- `templates/gitattributes-lfs.txt` — LFS routing patterns
- `templates/setup-machine.sh` — per-machine bootstrap
- `templates/data-MANIFEST.md` / `data-PROVENANCE.md` / `data-CHANGELOG.md` — data documentation contract

This rule defines the three-tier storage architecture the workflow uses for content that doesn't fit neatly in plain git: paper PDFs (load-bearing binary), data files (large or PII-sensitive), and ephemeral artifacts (regenerable). Each tier has a different storage mechanism, a different versioning model, and a different daily workflow.

---

## The three content classes

| Class | Storage | Versioning | Examples |
|---|---|---|---|
| **A — Tracked in git directly** | `.git/` | Real (git history) | Code, LaTeX, ADRs, plans, reading notes (`*.md`), `data/MANIFEST.md`, `data/PROVENANCE.md`, `data/CHANGELOG.md`, the `.dvc/` config, individual `.dvc` pointer files |
| **B — Tracked via Git LFS** | LFS server (GitHub LFS or self-hosted); pointer in repo | Real (git history; pointers commit normally) | Paper PDFs (`master_supporting_docs/literature/papers/*.pdf`), talk PDFs, large generated figure PDFs |
| **C — Tracked via DVC** | DVC cache in private remote (Dropbox / S3 / SSH); pointer (`*.dvc`) in repo | Real (git history of pointers + content-addressed cache) | Raw data (`data/raw/*`), cleaned data (`data/cleaned/*`), large derived datasets that are slow to regenerate |
| **D — Gitignored, periodic backup** | Local repo path + Dropbox mirror (rsync) | None | `.rds` caches, build artifacts, intermediate plots — anything regenerable from scripts |

Class B and C share the same structural pattern (pointer in git + blob elsewhere) but use different tools because they have different access patterns. LFS is filesystem-transparent and ideal for read-mostly binaries; DVC is explicit and ideal for evolving data with version-checkout semantics.

---

## When to enable each tier

**Class A (plain git):** default for everything. Always.

**Class B (LFS):** opt-in per project. Enable when:

- The `primary-source-first` hook gates citations on PDFs in `master_supporting_docs/literature/papers/` AND
- Coauthors / new machines need PDFs to clone automatically AND
- The PDF library is more than ~50 files (below that threshold, plain-git tracking is fine and simpler)

**Class C (DVC):** opt-in per project. Enable when:

- The project has data files in `data/raw/` or `data/cleaned/` AND
- You want to be able to ask "what was the data state when I wrote the JMP draft" — i.e., you anticipate revisiting old paper versions and needing matching data

**Class D (gitignored backup-only):** for everything that can be regenerated from scripts. Don't track these in any tier; let them rebuild.

---

## Daily LFS workflow

After a project has enabled LFS (see §"Enabling LFS" below), the daily workflow is **identical to plain git** — LFS hooks intercept relevant operations transparently.

```bash
# Add a new paper PDF — routes to LFS automatically per .gitattributes
cp ~/Downloads/smith_2024.pdf master_supporting_docs/literature/papers/
git add master_supporting_docs/literature/papers/smith_2024.pdf
git commit -m "Add Smith 2024 — relevant for §3 mechanism"
git push
# `git push` uploads the LFS blob to the LFS server in the same operation.
# You don't run anything separate.
```

The only command that's distinctively LFS:

```bash
git lfs ls-files          # list LFS-tracked files in this repo
git lfs env               # show LFS endpoint and storage stats
git lfs pull              # if you cloned --filter=blob:none or otherwise
                          # need to fetch blobs after the fact
```

### What changes about clones

```bash
git clone <url>           # clone fetches LFS blobs by default; same UX
                          # as a normal clone, slower if many blobs
```

If clones are unacceptably slow on a CI machine, partial-clone:

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone <url>
# then later:  git lfs pull --include="paths I actually need"
```

---

## Daily DVC workflow

DVC requires explicit two-step pushes: git commands handle pointers, `dvc` commands handle blobs.

```bash
# Add a new data file
dvc add data/raw/new_extract.csv
# This creates data/raw/new_extract.csv.dvc (pointer) and adds the actual
# file to data/.gitignore.

git add data/raw/new_extract.csv.dvc data/raw/.gitignore
git commit -m "Add new IPUMS extract"
git push                  # pushes pointer to GitHub
dvc push                  # pushes blob to remote (Dropbox cache, S3, etc.)

# The two pushes can happen in either order, but BOTH must happen.
# Forgetting `dvc push` leaves coauthors with broken pointers.
```

When data evolves:

```bash
# Edit data/cleaned/analysis_sample.dta (e.g., re-run cleaning)
dvc add data/cleaned/analysis_sample.dta   # updates the pointer
git add data/cleaned/analysis_sample.dta.dvc
git commit -m "Re-run cleaning with corrected restriction"
git push
dvc push
```

Updating `data/CHANGELOG.md` for non-trivial data changes is part of the workflow (per the data-doc contract below).

### Restoring an old data state

```bash
git checkout <old-commit-or-tag>
dvc checkout                           # restores data/ to match the pointers
                                       # in this commit
# work, then:
git checkout main && dvc checkout      # restore current state
```

This is the use-case that justifies DVC over plain Dropbox backup. Without DVC: "what data was here in 2026?" requires manual snapshotting. With DVC: it's a `git checkout` away.

---

## Two-step push: forgetting `dvc push`

The most common DVC failure mode: `git push` succeeds, `dvc push` is forgotten, coauthor pulls and gets broken pointers.

Mitigations (in order of strength):

1. **Run `/tools sync-status` before declaring a session done.** Will show `Pending uploads: N files` if `dvc push` is needed.
2. **Make `dvc push` muscle memory after `git push`.** Same way you remember `--tags` for new tags.
3. **(Optional, future)** Pre-commit hook that blocks `git push` if there are pending DVC uploads. Not enabled by default — adds a failure mode (hook fails → push blocked, requires bypass).

---

## The data documentation contract

Every project with `data/` under DVC should maintain three tracked-in-git files:

| File | Records | When updated |
|---|---|---|
| `data/MANIFEST.md` | What's in `data/` right now (one row per file) | Adding/removing/renaming a dataset |
| `data/PROVENANCE.md` | Where each dataset came from (source, license, access, who, when) | New dataset, license change, agreement renewal |
| `data/CHANGELOG.md` | Why the data changed (append-only) | Substantive data change with rationale |

These three files together let 2029-you understand what 2026-you was doing without spelunking. Templates ship in `templates/data-*.md`. Copy at project setup; backfill from current state if adopting mid-project.

---

## Enabling LFS in a project

```bash
cd <project>

# 1. Comment out PDF lines in .gitignore (the pair under "Academic PDFs")
$EDITOR .gitignore

# 2. Add the LFS routing
cp ~/github_repos/claude-code-my-workflow/templates/gitattributes-lfs.txt .gitattributes
$EDITOR .gitattributes        # remove the header block, keep the patterns

# 3. Initialize LFS
git lfs install --local

# 4. Commit setup
git add .gitignore .gitattributes
git commit -m "Enable Git LFS for paper PDFs"

# 5. Add existing PDFs to LFS
git add master_supporting_docs/literature/papers/
git commit -m "Add paper PDFs to LFS"
git push
```

## Enabling DVC in a project

```bash
cd <project>

# 1. Initialize DVC in the repo
dvc init

# 2. Configure remote — Dropbox-cache pattern is the default
mkdir -p ~/Dropbox/research-data/$(basename $PWD)/dvc-cache
dvc remote add -d storage ~/Dropbox/research-data/$(basename $PWD)/dvc-cache

# 3. Commit DVC scaffolding
git add .dvc/
git commit -m "Initialize DVC; remote = Dropbox"

# 4. Add data files (whole directories OK)
dvc add data/raw/
dvc add data/cleaned/
git add data/raw.dvc data/cleaned.dvc data/.gitignore
git commit -m "Track data/ under DVC"

# 5. Push blobs and pointers
dvc push
git push

# 6. Set up the data-doc contract
cp ~/github_repos/claude-code-my-workflow/templates/data-MANIFEST.md   data/MANIFEST.md
cp ~/github_repos/claude-code-my-workflow/templates/data-PROVENANCE.md data/PROVENANCE.md
cp ~/github_repos/claude-code-my-workflow/templates/data-CHANGELOG.md  data/CHANGELOG.md
# Fill in current state. Don't try to perfect-history-reconstruct old datasets.
git add data/MANIFEST.md data/PROVENANCE.md data/CHANGELOG.md
git commit -m "Add data documentation contract"
git push
```

## Setup on a new machine

```bash
brew install git-lfs dvc
git lfs install                  # one-time per machine (registers global hooks)
git clone <url> && cd <repo>
./bin/setup-machine.sh           # if present; otherwise:
# git lfs pull && dvc pull
```

The `setup-machine.sh` template (`templates/setup-machine.sh`) handles this idempotently and reports state.

---

## Coauthor onboarding

When migrating an existing project to LFS+DVC, coordinate with active coauthors:

1. **Notify in advance** with a setup email (template in the migration plan).
2. **Tag the pre-migration commit** so coauthors can roll back if needed: `git tag pre-lfs-migration && git push --tags`.
3. **Migrate, push, notify "done"** with a one-paragraph "what you need to do" instruction.
4. **Be available for ~24 hours** to debug coauthor setup issues.
5. **Provide DVC remote access** to the Dropbox cache (or alternative remote) — coauthors need read access to the `~/Dropbox/research-data/<proj>/dvc-cache/` shared folder.

---

## Rollback procedures

### LFS rollback (single repo)

```bash
# Convert LFS blobs back to normal git blobs
git lfs migrate export --include="*.pdf" --everything

# Disable LFS for this repo
git lfs uninstall
$EDITOR .gitattributes        # remove the LFS lines

# Coauthor coordination required: history is rewritten.
git push --force-with-lease
```

Cost: history rewrite, coauthors must reset. Worth doing only if LFS is actively causing problems.

### DVC rollback (single repo)

```bash
# Materialize all DVC-tracked files into the repo
dvc unprotect data/

# Remove DVC pointers from git
git rm data/raw.dvc data/cleaned.dvc
rm -rf .dvc/

# Add data/ back to .gitignore (PII concern — don't accidentally commit data)
echo "data/raw/" >> .gitignore
echo "data/cleaned/" >> .gitignore

git add .gitignore
git commit -m "Roll back DVC; data is gitignored again"
git push
```

DVC rollback is cleaner — no history rewrite, no coauthor disruption.

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| `git lfs ls-files` shows nothing after migration | `.gitattributes` not committed before adding PDFs | Re-add the PDFs after committing `.gitattributes` |
| Coauthor sees broken LFS pointers (smudge filter error) | Coauthor doesn't have git-lfs installed | Tell them: `brew install git-lfs && git lfs install && git lfs pull` |
| `dvc pull` fails with "remote unreachable" | Dropbox not yet synced on this machine | Wait for Dropbox; check `~/Dropbox/research-data/<proj>/dvc-cache/` exists |
| Coauthor sees `.dvc` pointers but no actual files | Forgot `dvc push`, OR coauthor doesn't have DVC remote access | Verify `dvc push` ran post-commit; verify coauthor has Dropbox-share permission |
| GitHub LFS bandwidth alert | Heavy clones / pulls eating free-tier monthly bandwidth | (a) Buy data pack \$5/mo, (b) self-host LFS, (c) use partial-clone for CI |
| `data/raw.dvc` shows clean status but file is missing | DVC cache was cleared or moved | `dvc fetch && dvc checkout` to restore from remote |
| Reverting a commit doesn't restore old data | Need explicit `dvc checkout` after `git checkout` | Run `dvc checkout` after every `git checkout` of a commit that touched DVC-tracked files |
| Pre-LFS-migration PDFs still bloat `.git/` | History wasn't rewritten (intentional per migration plan D3) | Acceptable cost. Run `git lfs migrate import` per repo if it becomes a real problem |

---

## What this rule does NOT cover

- **Encryption of data at rest in the DVC remote.** DVC + Dropbox uses Dropbox's standard encryption. For higher sensitivity, configure DVC with an encrypted S3 remote (out of scope here).
- **PII scrubbing of pre-existing committed data.** If `data/` was ever committed plainly before DVC adoption, those bytes are still in `.git/objects/`. `git filter-repo` can scrub but is destructive (see `destructive-actions.md`).
- **Backup of the LFS server itself.** GitHub LFS storage is GitHub's responsibility. For belt-and-suspenders, periodically `git lfs fetch --all && git lfs push <secondary-remote>`.
- **Coauthors who refuse to install DVC.** No workaround — that project falls back to plain backup-only (Class D for everything).

## Cross-references

- `quality_reports/plans/2026-05-05_lfs-dvc-migration-plan.md` — concrete migration plan
- `quality_reports/plans/2026-05-05_lfs-vs-dvc-explainer.md` — concept-level primer
- `.claude/rules/destructive-actions.md` — relevant to history-rewrite operations (LFS rollback)
- `.claude/rules/primary-source-first.md` — hook that depends on PDFs being readable; LFS is transparent to it
- `.claude/rules/replication-protocol.md` — replication packages should document DVC pointer commits along with code commits
