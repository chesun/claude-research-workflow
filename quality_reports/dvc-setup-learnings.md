# DVC Setup — Learnings & Lab-Guide Draft

**Status:** DRAFT (living doc) — capturing learnings from the `belief_distortion_discrimination` DVC pilot, with the goal of producing a data-version-control guide for the Education Lab (CEL, UC Davis) server.
**Started:** 2026-06-23
**Companions:** `.claude/rules/data-version-control.md` (the rule), `quality_reports/plans/2026-05-05_lfs-dvc-migration-plan.md` (the plan), `quality_reports/plans/2026-05-05_lfs-vs-dvc-explainer.md` (concept primer), `quality_reports/session_logs/2026-06-23_dvc-pilot-push-completion.md` (the pilot session).

> **Promotion path:** once this matures, the polished version can move to `docs/` (template-user-facing) and/or be exported to a CEL-owned repo as the lab's server guide. Server-specific sections are marked **[SERVER — TBD]** until we pin down the lab's setup.

---

## 1. Purpose & scope

This doc captures what we learned setting up DVC on a real project, so the lab guide is grounded in actual mechanics rather than tutorial defaults. The immediate trigger was a question worth answering precisely (§3): *what's the difference between a `.gitignore` inside the data folder vs. the root `.gitignore`* — and how does that interact with DVC.

---

## 2. The core mental model: DVC *requires* gitignored data

DVC is **not** incompatible with gitignored data folders — it depends on them. That is the whole mechanism:

- **Git tracks** a tiny pointer file (`<data>.dvc`, ~5 lines: content hash + size + file count) and the `.gitignore` entry.
- **DVC tracks** the actual bytes, stored in a content-addressed cache and pushed to a **remote**.

When you run `dvc add <path>`, DVC itself **writes `<path>` into a `.gitignore` for you** — you don't do it manually. So "the data folder is gitignored" is the correct, healthy end state. If the data were *not* gitignored, you'd be committing gigabytes into git — exactly what DVC exists to prevent.

**The two-push rhythm (most important operational habit):**

```
git add <path>.dvc <path>/.gitignore   # stage the pointer + ignore rule
git commit -m "..."
git push        # pushes the POINTER (to GitHub/GitLab)
dvc push        # pushes the BYTES (to the DVC remote)   ← easy to forget
```

`git push` and `dvc push` are **two separate operations**. Forgetting `dvc push` is the #1 DVC failure mode — see §5.

---

## 3. `.gitignore`: root vs. nested (the direct question)

Git reads **every `.gitignore` in the path** from the repo root down to the directory containing a file. They differ in three ways that matter for DVC.

### 3a. Pattern paths are anchored to the `.gitignore`'s own location

A leading-slash pattern anchors to **the directory that `.gitignore` lives in**, not the repo root.

| To ignore `data/raw/` … | in **root** `.gitignore` write | in **`data/.gitignore`** write |
|---|---|---|
| | `/data/raw/`  (full path from root) | `/raw/`  (relative to `data/`) |

A non-anchored pattern (`raw/` with no leading slash) matches at **any depth**, which is why root patterns can accidentally over-match. `data/.gitignore` with `/raw/` only ever affects `data/raw/` — locality reduces blast radius.

### 3b. The decisive rule: git won't descend into a *wholesale-ignored* directory

This is the rule that bit the pilot. From the git docs:

> *"It is not possible to re-include a file if a parent directory of that file is excluded. Git doesn't list excluded directories for performance reasons, so any patterns on contained files have no effect, no matter where they are defined."*

Consequence:

- **Root `.gitignore` has `/data_local`** (the *directory itself* excluded) → git **never looks inside** `data_local/`. Any `data_local/.gitignore` is **dead** (never read), and you **cannot** track a doc file inside (`!data_local/MANIFEST.md` has no effect). This is the wholesale form.
- **Root `.gitignore` has `/data_local/*`** (the *contents* excluded, not the directory) → git **does descend**, *does* read a nested `data_local/.gitignore`, and negations like `!data_local/MANIFEST.md` **work**.

So a nested `.gitignore` is only meaningful if the parent directory is **not** wholesale-ignored.

### 3c. Precedence: deeper `.gitignore` wins

For a given file, git applies patterns from shallowest to deepest; **a lower-level `.gitignore` overrides a higher-level one**, and within one file the **last matching pattern wins**. This lets a `data/.gitignore` make local exceptions to a broad root rule (only when the parent isn't wholesale-excluded — see 3b).

### 3d. How DVC chooses where to write the ignore entry

DVC writes the ignore rule into the `.gitignore` **in the directory containing the tracked target**:

| Command | Pointer created | `.gitignore` touched | Form |
|---|---|---|---|
| `dvc add data/raw`     | `data/raw.dvc`    | **`data/.gitignore`** ← nested | `/raw` (contents of `data/` minus `raw`) |
| `dvc add data_local`   | `data_local.dvc`  | **root `.gitignore`** ← wholesale | `/data_local` (whole top-level dir) |

This is exactly what we observed in the pilot: `dvc add data_local` appended `/data_local` to the **root** `.gitignore`, making `data_local/` wholesale-ignored — which is why git-tracked docs couldn't live inside it.

### 3e. Practical takeaway for the lab

**Prefer DVC-tracking *subdirectories* of a data folder, not the data folder wholesale.** Then:

- DVC writes a **nested `data/.gitignore`** that ignores only the data subdirs (`/raw`, `/cleaned`).
- The parent `data/` stays git-tracked, so **pointers, the nested `.gitignore`, and human-readable docs (MANIFEST/PROVENANCE/CHANGELOG) all live next to the data**.
- No wholesale-ignore trap, no need for a sibling docs folder.

---

## 4. Recommended layout (seed for the lab guide)

```
data/                  ← git-tracked (NOT ignored)
├── raw/               ← dvc add data/raw   → bytes in DVC, "/raw" in data/.gitignore
├── raw.dvc            ← git-tracked pointer
├── cleaned/           ← dvc add data/cleaned → "/cleaned" in data/.gitignore
├── cleaned.dvc        ← git-tracked pointer
├── MANIFEST.md        ← git-tracked (what's there now)
├── PROVENANCE.md      ← git-tracked (where it came from; IRB/license/PII)
├── CHANGELOG.md       ← git-tracked (why versions changed)
└── .gitignore         ← DVC-managed: /raw, /cleaned
```

Contrast with the pilot's `data_local/` (one wholesale-ignored top-level dir): it works for DVC, but forces docs into a sibling `data/` folder because nothing git-tracked can live inside `data_local/`.

---

## 5. The dangling-pointer lesson (biggest operational learning)

**What happened in the pilot:** `dvc add data_local` created `data_local.dvc`, and that pointer was **committed and pushed to GitHub** — but **`dvc push` was never run**. The DVC remote cache was **0 B**. Result: the pointer existed on the remote, but the bytes it pointed to existed **only on one laptop's working tree**. A fresh `git clone` + `dvc pull` would have failed outright, and there was no off-machine backup of ~1.15 GB.

**Why it's insidious:** `git status` and a normal `git push` look completely clean. Nothing flags the missing bytes. Only `dvc status -c` (cloud status) reveals it.

**Detection & habits for the guide:**

- After every data change: `git push` **and** `dvc push` — always both.
- Before declaring a session done: run `dvc status -c`. "Cache and remote are in sync" = safe; a list of "new" files = unpushed bytes.
- A `/tools sync-status` helper (planned in the migration plan §7.5, still unbuilt) would surface "pending uploads: N" automatically. It is exactly the guardrail that would have caught this. **Strong candidate to build before the lab relies on DVC** — humans forget `dvc push`.

---

## 6. Other pilot learnings

- **`.dvcignore` for junk.** macOS `.DS_Store` files were being swept into DVC tracking. Add a `.dvcignore` (same syntax as `.gitignore`, at repo root) with `.DS_Store`. DVC respects it on `dvc add`.
- **Re-add after the data changes.** A `.dvc` pointer is a snapshot. If the tracked directory changes after `dvc add`, `dvc status` shows it `modified`; you must **re-`dvc add`** to capture the new state, then `dvc push`. The pointer is not auto-updating.
- **Data-doc contract placement** (see §3e/§4): keep MANIFEST/PROVENANCE/CHANGELOG git-tracked and next to the data, which the subdir layout allows.
- **Don't fabricate provenance.** The pilot's PROVENANCE.md was scaffolded with IRB / fielding dates / PII status / authorized-users marked **TBD** rather than guessed. For a discrimination experiment with participant identifiers, the provenance + de-identification plan are load-bearing for the eventual replication package.

---

## 7. Server-specific topics  **[SERVER — TBD]**

The gitignore/DVC mechanics above are **identical on a laptop and a server**. This section is the server-specific design. **Hard constraint: the server will not have Claude Code.** Everything must be self-contained — plain `git` + `dvc` commands, shell scripts, and native git hooks. No `/tools` skills, no Claude Code hooks.

### 7.1 First, untangle two stores DVC keeps separate

"A data cache directory on the server" is the right instinct, but DVC has **two** directory-shaped stores with different jobs. Conflating them is the main source of confusion:

| Store | What it is | Touched by | Default location |
|---|---|---|---|
| **Cache** | Content-addressed blob store that the *workspace* is materialized from (checkout links files out of here) | `dvc add`, `dvc checkout`, `dvc pull` | `.dvc/cache` inside each repo |
| **Remote** | The push/pull target — the "share + backup" store, the source of truth to pull from | `dvc push`, `dvc pull`, `dvc fetch` | none (must configure) |

On a single shared server you want to make a deliberate choice about **both**, not just one.

### 7.2 Recommended architecture for one shared analysis server

Assuming the common CEL case — everyone SSHes into the *same* server and runs analysis there:

```
/data/cel/dvc-cache/              ← ONE shared cache for the lab (dedup across users + projects)
/backup/cel/dvc-remotes/<proj>/   ← per-project local-filesystem REMOTE, on a BACKED-UP volume
~/<user>/projects/<proj>/data/raw/   ← each user's workspace, hard/sym-linked from the shared cache
```

Two moves:

1. **Shared cache (the dedup win).** Point every user's DVC at one cache dir:

   ```bash
   dvc config --global cache.dir /data/cel/dvc-cache
   dvc config cache.type "reflink,hardlink,symlink"   # link, don't copy
   dvc config cache.shared group                      # group-writable cache files
   ```

   With a shared cache + links, ten users each "holding" a 50 GB dataset consume **50 GB once**, not 500 GB — `dvc checkout` materializes the workspace as links into the shared cache, not copies.

2. **Local-filesystem remote on a backed-up volume (the durability win).** This is your "dedicated directory," used as the `dvc push`/`pull` target:

   ```bash
   dvc remote add -d storage /backup/cel/dvc-remotes/<proj>
   ```

   `dvc push` then copies new blobs cache → remote (a fast local copy, since both are on the server). The remote is the durable source of truth; the cache is the fast working store.

**Why keep both (don't collapse to just a shared cache):** the cache is subject to `dvc gc` (garbage collection prunes blobs not referenced by the current workspace) and isn't a "source of truth." The remote is what `dvc pull` reconstructs from. Skipping the remote makes the lab one `dvc gc` or one disk hiccup away from data loss.

### 7.3 The decision that actually gates this: which volumes?

The architecture above is sound; the open variables are physical:

- **Same-filesystem requirement for dedup.** Hard/reflinks only work when the shared **cache** and the users' **working dirs** are on the *same* filesystem/mount. If `~/` (home) and `/data` are different mounts, hard/reflink fails and DVC falls back to `copy` (no dedup) or `symlink` (works cross-FS but cache files are read-only and a stray edit can confuse things). **[TBD: are home dirs and the data volume the same filesystem? what FS — ext4/ZFS/XFS/NFS?]** (reflink needs CoW: XFS/Btrfs/ZFS/APFS; ext4 → hardlink.)
- **The remote must be on a backed-up volume**, ideally *different* from the cache volume — otherwise cache and "backup" share a failure domain. **[TBD: which path is actually backed up?]**
- **Off-server copy?** A purely on-server remote dies with the server room. If the institution has S3/MinIO or a second host, a *second* remote (`dvc remote add backup s3://…` / `ssh://…`) gives off-site durability. **[TBD: any cloud/object storage or second host available?]**
- **Permissions.** Shared cache + remote on a multi-user box need a common Unix group (e.g. `cel`), `chmod g+s` (setgid) on the dirs so new blobs inherit the group, and a sane `umask`. `cache.shared group` handles the file mode; the group + setgid is a sysadmin step. **[TBD: is there a `cel` group? who administers it?]**
- **PII / restricted data.** A discrimination experiment's raw files with participant IDs on a *shared* cache means every lab member can read them. May warrant a separate restricted cache/remote with tighter group membership. **[TBD: access-control requirements for restricted data.]**

### 7.4 Self-contained guardrails (the "no Claude Code" answer)

The dangling-pointer risk (§5) was going to be caught by `/tools sync-status` — which won't exist on the server. The self-contained replacements, in order of preference:

1. **`dvc install` — native git hooks (DVC's built-in, fully self-contained).** Wires DVC into plain git hooks so the two-step rhythm stops depending on memory:

   ```bash
   dvc install      # installs git hooks (verify exact set on the lab's DVC version):
                    #   post-checkout → dvc checkout   (materialize data after git checkout)
                    #   post-merge    → dvc checkout   (after git pull)
                    #   pre-push      → dvc push        (push blobs when you git push)
   ```

   The `pre-push → dvc push` hook is the direct dangling-pointer guard: you cannot `git push` a pointer without the blobs going too. **Caveat:** auto-pushing on every `git push` can be slow/surprising for large data. The lighter alternative is a custom `pre-push` that only *checks*:

2. **A plain `pre-push` (or standalone) check script** — the self-contained analog of `/tools sync-status`, no auto-push:

   ```bash
   #!/usr/bin/env bash
   # .git/hooks/pre-push (or bin/dvc-sync-check.sh, run before declaring done)
   if dvc status -c 2>/dev/null | grep -q .; then
     echo "⚠ DVC: local blobs not pushed. Run: dvc push" >&2
     # exit 1   # uncomment to BLOCK the push until dvc push runs
   fi
   ```

   Ship this as a tracked file in the repo + an install line in `setup-dvc-server.sh`, so it travels with the project and needs no Claude Code.

3. **Documented habit + a one-line health check.** `dvc status -c` ("Cache and remote are in sync" = safe) before ending a session. Belt-and-suspenders behind the hook.

### 7.5 Install & environment **[TBD]**

- Is `dvc` installable lab-wide (pip in a shared venv / conda / an environment module)? Pin one version across users (the pilot used 3.67.1). **[TBD]**
- A `setup-dvc-server.sh` (plain bash, no Claude Code) should do, idempotently: set `cache.dir` / `cache.type` / `cache.shared`, add the remote, run `dvc install`, install the check hook, and `dvc pull`. This is the server analog of the laptop `templates/setup-machine.sh`.

---

## 8. Open questions / next steps

1. **Pin the server volume facts in §7.3** — filesystem type, which path is backed up, same-FS-as-home, common group, any off-server/cloud option, restricted-data access controls. These gate the concrete config.
2. **Write `setup-dvc-server.sh`** (§7.5) and the `pre-push` check hook (§7.4) — the self-contained setup + guardrail, replacing the Claude Code `/tools sync-status` idea on the server.
3. Decide whether the lab guide lives in `docs/` here, or a CEL-owned repo (likely the latter, since it's institution-specific and server-coupled).
4. Resolve the pilot's separate LFS loose end (pre-LFS PDF churn) — unrelated to DVC, tracked in the pilot CHANGELOG.
