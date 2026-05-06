<!-- primary-source-ok: chetty_2014 -->
<!-- chetty_2014 used only as an illustrative placeholder filename in the
     layout diagram; no framing claim about the paper. -->

# Dropbox Symlink Setup — Explainer
**Date:** 2026-05-01
**Status:** Superseded by `quality_reports/plans/2026-05-05_lfs-dvc-migration-plan.md`
**Supersedes:** —

Reference doc explaining the proposed Dropbox-symlink setup for managing gitignored bulk content (paper PDFs, raw data) across multiple research repos. Pre-decision — written so the user can evaluate before committing.

## The core idea

A symbolic link (`ln -s`) is a filesystem pointer: one path *appears* to be at another location. From inside the repo, `master_supporting_docs/literature/papers/` looks like a normal directory; the actual bytes live in Dropbox.

The repo (.git + tracked code) stays in `~/github_repos/` — outside Dropbox. Only the gitignored bulk paths get symlinked into Dropbox. This avoids Dropbox + .git race conditions (which corrupt repos) while still continuously syncing the PDFs.

## Layout

```
~/Dropbox/research-data/                                  (Dropbox-synced; content lives here)
├── belief_distortion_discrimination/
│   └── papers/
│       ├── chetty_2014.pdf                               (illustrative filename only)
│       └── ...
├── tx_peer_effects/
│   └── papers/
└── csac2025/
    └── papers/

~/github_repos/                                            (NOT in Dropbox; code only)
├── belief_distortion_discrimination/
│   └── master_supporting_docs/literature/papers ──→ symlink ──→ ~/Dropbox/research-data/belief_distortion_discrimination/papers/
├── tx_peer_effects/
│   └── master_supporting_docs/literature/papers ──→ symlink ──→ ~/Dropbox/research-data/tx_peer_effects/papers/
└── ...
```

## Setup on the original machine (one-time, per repo)

```bash
PROJ=belief_distortion_discrimination
REPO=~/github_repos/$PROJ
DROP=~/Dropbox/research-data/$PROJ

# 1. Move existing papers into Dropbox (preserves all content)
mkdir -p $DROP
mv $REPO/master_supporting_docs/literature/papers $DROP/papers

# 2. Create the symlink at the original repo path
ln -s $DROP/papers $REPO/master_supporting_docs/literature/papers

# 3. Verify
ls $REPO/master_supporting_docs/literature/papers/    # should show the PDFs
readlink $REPO/master_supporting_docs/literature/papers   # should show the Dropbox path
```

Dropbox starts syncing automatically on step 1.

## Setup on a new machine (the migration story)

```bash
# 1. Install Dropbox; wait for ~/Dropbox/research-data/ to fully sync.
# 2. Clone the repo as usual.
git clone https://github.com/chesun/belief_distortion_discrimination.git ~/github_repos/belief_distortion_discrimination

# 3. Recreate the symlink. (The repo arrives without one — the path is gitignored.)
PROJ=belief_distortion_discrimination
ln -s ~/Dropbox/research-data/$PROJ/papers \
      ~/github_repos/$PROJ/master_supporting_docs/literature/papers

# 4. Verify, then start working — PDFs are present, hooks see them, everything works.
```

A per-repo `setup-machine.sh` automates step 3 (one line per symlink restored).

## What git sees

The symlink lives at a path that is already in `.gitignore` (per the public-release PDF policy). Git does not track the link, the link's target, or the bytes inside it. Tools that walk the directory (the `primary-source-first` hook, find, ls, the workflow's reading-notes resolver) all follow the symlink transparently and find the PDFs as if they lived in the repo.

## Why not just put the whole repo in Dropbox

Dropbox sync threads write to `.git/index` from a different process than the git command currently running. The race produces "fatal: bad index" errors and occasional silent corruption. The same applies to OneDrive, iCloud, Google Drive — any continuous-sync tool. The split (repo outside, content inside Dropbox via symlink) avoids this without sacrificing the auto-sync benefit for bulk content.

## Failure modes

| What can go wrong | Symptom | Fix |
|---|---|---|
| Dropbox not yet synced on new machine | `ls papers/` shows empty | Wait; check `~/Dropbox/research-data/<proj>/papers/` directly |
| Forgot to symlink on new machine | `papers/` is missing entirely; hooks block citations | Run setup-machine.sh; one-line fix |
| Symlink target renamed | Symlink dangles, points nowhere | `ln -sf` to recreate with correct target |
| Dropbox conflicted-copy on rare simultaneous edit | `paper (Christina's conflicted copy 2026-05-01).pdf` | PDFs are reference content; rarely edited. Pick one, delete the other. |
| Backup tool that doesn't follow symlinks | Backup misses the actual PDFs | Either configure tool to follow symlinks, or back up `~/Dropbox/research-data/` directly |
| Tool that refuses symlinks | Rare; usually sandboxed apps | Workaround per-tool; not encountered in this workflow's stack |

## Refinement worth knowing about

If the same PDF appears in 3+ projects (heavy citation overlap), the per-project layout duplicates storage:

```
~/Dropbox/research-data/_shared-papers/    # canonical home
~/Dropbox/research-data/belief_distortion_discrimination/papers/foo_2014.pdf  →  symlink to _shared-papers/foo_2014.pdf
```

Useful when citation overlap is heavy. Overkill for distinct projects with different literature. Recommendation: start per-project; restructure to shared only after noticing real duplication. Symlinks-of-symlinks work fine; the workflow doesn't care.

## What this does not solve

- **`data/cleaned/`, intermediate outputs, `.rds` caches:** still regenerable from scripts. Don't symlink these — keep them gitignored and ephemeral, regenerate after migration.
- **`data/raw/` if it's big:** depends on size. If <5 GB and stable, same Dropbox-symlink pattern works. If >5 GB or actively changing, use rsync-over-SSH at migration time instead.
- **Drift detection:** Dropbox sync is best-effort, not transactional. The migration-audit script (separate proposal) gives you a periodic check that catches drift between repo and Dropbox.

## Decision points

1. **Adopt for all 5+ projects, or pilot on one first?** Recommend: pilot on `belief_distortion_discrimination` for a week, then bulk-migrate the rest.
2. **Per-project or shared-papers structure?** Recommend: per-project initially; revisit if you notice >20% duplication.
3. **Where does the setup-machine.sh script live?** Two options: (a) committed in each project repo as `bin/setup-machine.sh` listing that project's symlinks, (b) one global `~/bin/setup-machine.sh` in claude-config that loops over a manifest. (a) is more portable; (b) is less duplication. Recommend (a) since project-specific paths belong with the project.
