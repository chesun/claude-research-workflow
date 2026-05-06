# Git LFS vs DVC — Explainer

**Date:** 2026-05-05
**Status:** Active (explanatory; pre-decision)
**Supersedes:** —

Written so you can decide which tool to adopt for which content class. Both solve the same general problem ("git is bad at large/binary files") with different tradeoffs.

## The shared problem

Git was designed for source code: small text files with line-level diffs. Two things break when you put binary files in a normal git repo:

1. **Repo bloat.** Git stores every version of every file forever in `.git/`. A 5 MB PDF revised 10 times = 50 MB in `.git/`, even after a `git pull` of the latest. Clones get slow; GitHub starts complaining around 1 GB; pushes refuse around 100 MB per file.
2. **No useful diff.** `git diff foo.pdf` is meaningless. Binary deltas don't compress well across versions.

Both Git LFS and DVC fix this with the same trick: **store a tiny pointer in git, store the actual bytes elsewhere.** They differ in *where elsewhere* is and *how tightly coupled to git* the workflow feels.

## Git LFS — the lightweight option

**What it is.** A git extension. You mark patterns (`*.pdf`, `*.png`) as "LFS-tracked." Behind the scenes, git stores a 130-byte pointer file in your repo's commits; the actual file content lives on an LFS server (GitHub provides one; self-hosted versions exist).

**The mental model.** Your repo *looks identical* to a normal repo. `ls`, editors, build tools all see normal files. Only `git` itself knows the file is special.

**Setup (one-time per machine):**

```bash
brew install git-lfs        # macOS
git lfs install             # registers LFS hooks in your git config
```

**Setup (per repo):**

```bash
cd ~/github_repos/myproject
git lfs track "*.pdf"       # writes .gitattributes
git lfs track "master_supporting_docs/literature/papers/*.pdf"
git add .gitattributes
git commit -m "Track PDFs in LFS"

# now any PDF you add gets routed to LFS automatically
git add master_supporting_docs/literature/papers/chetty_2014.pdf
git commit -m "Add Chetty 2014"
git push                    # pushes pointer to GitHub + blob to LFS server
```

**Daily workflow:** completely unchanged. `git add` / `commit` / `push` / `pull` work the same. The LFS extension hooks into them.

**On a new machine:**

```bash
git clone https://github.com/you/myproject.git
# clone fetches pointers + blobs automatically (LFS pull is implicit)
```

**Cost (GitHub):**

- Free tier: 1 GB storage + 1 GB/month bandwidth — tight for a project with 100+ PDFs averaging 2 MB each (~200 MB, fine).
- Paid: \$5/month buys "data packs" of 50 GB storage + 50 GB bandwidth.
- Self-hosted: free if you run your own LFS server (Gitea, GitLab CE include one).

**Strengths:**

- Zero workflow disruption — you don't *think* about LFS, it just works.
- Universal — every git host (GitHub, GitLab, Bitbucket, Gitea) speaks LFS.
- Simple mental model: "git for big files."

**Weaknesses:**

- Bandwidth cost on heavy projects. If you clone a 50 GB LFS repo three times, you've used 150 GB of bandwidth.
- Designed for *files that are part of the codebase deliverable*, not for *data that evolves*. No real notion of "data state at this analysis run."
- `git lfs migrate` is needed if PDFs are already committed normally (rewrites history; coauthor coordination needed).

## DVC — the data-versioning option

**What it is.** A separate CLI tool (`dvc`) that creates `.dvc` pointer files alongside your data files. The pointers are committed to git; the actual content is stored in a "remote" you configure (S3, GCS, Azure, SSH, HTTP, *or just a local Dropbox path*).

**The mental model.** Every data file has two parts:

- The blob (actual bytes) → lives in a content-addressed cache, replicated to the remote.
- The pointer (a `.dvc` YAML file with hash + size) → lives in git.

When you `git checkout` an old commit, the `.dvc` pointers reflect that commit's data state. Then `dvc checkout` restores the matching blobs from the cache. So git history *includes* data history without git ever seeing the bytes.

**Setup (one-time per machine):**

```bash
pip install dvc            # or: brew install dvc
```

**Setup (per repo):**

```bash
cd ~/github_repos/myproject
dvc init
dvc remote add -d storage ~/Dropbox/research-data/myproject/dvc-cache
git add .dvc/
git commit -m "Initialize DVC, remote = Dropbox"
```

**Daily workflow:**

```bash
# add a data file (creates data/raw/cps.csv.dvc; cps.csv goes to .gitignore)
dvc add data/raw/cps.csv
git add data/raw/cps.csv.dvc data/raw/.gitignore
git commit -m "Add CPS extract (2026-05-05)"

# push to remote (the Dropbox cache, in our case)
dvc push
git push
```

**Restoring an old data state:**

```bash
git checkout 2026-jmp-draft   # checks out old commits including .dvc pointers
dvc checkout                   # downloads matching data blobs from remote
# now data/raw/cps.csv is the exact bytes from JMP-draft time
```

**Cost:** DVC itself is free (open source). Storage cost depends on the remote you choose. Local Dropbox path = whatever Dropbox costs you anyway. S3 = pennies per GB. SSH to a lab server = free.

**Strengths:**

- True data version control. `git log` for data. Reproducibility across years.
- Storage-backend flexibility — Dropbox, S3, GCS, SSH, HTTP all work.
- Designed for the "what was the data when I ran this analysis" problem.
- Solves the PII problem cleanly: the pointer is in git, the data is in private cloud storage that nobody but you accesses.
- Adds pipeline tracking (`dvc.yaml`) if you ever want it — describes which scripts produce which outputs from which inputs. Optional but powerful.

**Weaknesses:**

- One more tool to learn. Two state systems (git + dvc) instead of one.
- Two-step commits (`git push` + `dvc push`) — easy to forget the `dvc push`, leaving collaborators with broken pointers.
- Overkill for files that don't change. If you only add PDFs but never modify them, the version control is wasted machinery.
- Less universal than git — coauthors need DVC installed and configured.

## Side-by-side

| Property | Git LFS | DVC |
|---|---|---|
| Mental model | "git for big files" | "git for data, pointers in git, blobs in remote" |
| Setup complexity | Low (1 install + `git lfs track`) | Medium (install + `dvc init` + remote config) |
| Workflow impact | Invisible (uses normal git commands) | Visible (separate `dvc add/push/pull`) |
| Best for | Binary files in the codebase deliverable | Data that changes over time |
| Storage backend | LFS server (GitHub's, or self-hosted) | Anything (S3, GCS, Dropbox, SSH, HTTP, local) |
| PII handling | Whoever has repo access has LFS access | Independent — repo can be public, data backend private |
| Cost | GitHub: \$0 to ~\$5/month for typical projects | Free tool; storage cost is whatever your remote costs |
| Universal? | Yes — every git host speaks LFS | No — coauthors need DVC installed |
| Versioning quality for data | Crude (just commits) | Real (branch, checkout, restore matching state) |

## Recommendation for your stack

Given how you described the three content classes:

**Class 1 — Paper PDFs (load-bearing, rarely modified, small-medium):**
Git LFS. Zero workflow disruption, everyone who clones the repo gets the PDFs automatically, reproducibility is "just clone the repo at this commit." GitHub free tier handles a typical economics project's literature footprint.

**Class 2 — Data (PII concerns, evolves over years, "what was the data in 2026?"):**
DVC with Dropbox as the remote. The `.dvc` pointers go in git (small, no PII). The actual data blobs go to `~/Dropbox/research-data/<proj>/dvc-cache/`. When you come back in 2029 and check out the JMP-draft tag, `dvc checkout` restores the exact 2026 data. Dropbox is your existing backup; DVC adds the version-tracking layer on top.

**Class 3 — Ephemeral (intermediate `.rds`, build outputs, log files):**
Stay gitignored. No version control, no backup. Regenerable from scripts.

## What this would look like in practice

```
~/github_repos/belief_distortion_discrimination/
├── .git/                         (repo with code + LaTeX + ADRs)
├── .gitattributes                (LFS patterns: *.pdf, *.png)
├── .dvc/                         (DVC config; remote = Dropbox path)
├── master_supporting_docs/literature/papers/
│   ├── chetty_2014.pdf           (LFS-tracked; pointer in git, blob on GitHub LFS)
│   └── card_krueger_1994.pdf     (LFS-tracked)
├── data/
│   ├── raw/
│   │   ├── cps_2024.csv.dvc      (DVC pointer, in git)
│   │   └── cps_2024.csv          (gitignored; in DVC cache → Dropbox)
│   ├── cleaned/
│   │   └── analysis_sample.dta.dvc
│   ├── MANIFEST.md               (in git: human-readable inventory)
│   ├── PROVENANCE.md             (in git: source, license, access date per file)
│   └── CHANGELOG.md              (in git: when data changed and why)
├── paper/main.tex                (normal git)
└── ...
```

The four "contract" files in `data/` (`MANIFEST`, `PROVENANCE`, `CHANGELOG`, plus `.dvc` pointers) are what makes 2029-you able to navigate 2026-data without spelunking. They're in git so they version naturally with the analysis.

## Open decisions

1. **GitHub LFS pricing tier.** Free 1 GB is enough for ~500 average-size PDFs. If you expect more across all projects, decide between GitHub paid (\$5/month per data pack) or self-hosted LFS (free, more setup). Suggest: start free, upgrade only if you hit the limit.
2. **Adopt DVC project-by-project, or once globally.** DVC is per-repo. Suggest: pilot on `belief_distortion_discrimination` since the data there is most stable, learn the workflow, then bulk-migrate the others.
3. **Migration of existing committed PDFs.** If any project already has PDFs in git history (not gitignored), `git lfs migrate import` rewrites history to move them. Coauthor coordination needed since it changes commit hashes. Decide per-project whether this matters or whether a fresh-start LFS adoption (only new PDFs go to LFS, old ones stay in normal git history) is fine.
4. **Workflow integration.** Hooks/skills/agents that touch PDFs (the `primary-source-first` hook, `pdf-learnings` skill) need no changes — LFS is invisible to them. Hooks/skills that touch data would benefit from a `data/MANIFEST.md` template and a `/tools data-status` command that shows DVC state. Worth scoping after pilot.

## What this does NOT solve

- **Data privacy in the cloud.** DVC doesn't encrypt blobs at rest in your remote. If `~/Dropbox/research-data/<proj>/dvc-cache/` contains PII, Dropbox's standard encryption is what's protecting it. For higher sensitivity, point DVC at an encrypted remote (S3 with SSE, or local-only with no cloud sync).
- **Coauthor onboarding.** Coauthors need to install both git-lfs and dvc, and get access to the DVC remote (Dropbox-shared folder, or whatever you choose). Document in repo `README.md`.
- **Regenerable derived files.** Don't track these in either system. Scripts + raw data should reproduce them. If they don't, the issue is the scripts, not the storage layer.
