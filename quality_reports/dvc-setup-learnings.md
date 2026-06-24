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

## 7. Server-specific design (scribe)

The gitignore/DVC mechanics above are **identical on a laptop and a server**. This section is the server-specific design. **Hard constraint: the server will not have Claude Code.** Everything must be self-contained — plain `git` + `dvc` commands, shell scripts, and native git hooks. No `/tools` skills, no Claude Code hooks.

### 7.1 First, untangle two stores DVC keeps separate

"A data cache directory on the server" is the right instinct, but DVC has **two** directory-shaped stores with different jobs. Conflating them is the main source of confusion:

| Store | What it is | Touched by | Default location |
|---|---|---|---|
| **Cache** | Content-addressed blob store that the *workspace* is materialized from (checkout links files out of here) | `dvc add`, `dvc checkout`, `dvc pull` | `.dvc/cache` inside each repo |
| **Remote** | The push/pull target — the "share + backup" store, the source of truth to pull from | `dvc push`, `dvc pull`, `dvc fetch` | none (must configure) |

On a single shared server you want to make a deliberate choice about **both**, not just one.

### 7.2 The scribe environment (known facts)

CEL's server is a **Linux box named `scribe`**. The lab root contains three subfolders:

```
<LAB_ROOT>/                  (exact absolute path on scribe — TBD)
├── projects/
│   └── <proj>/              project code + git clone(s); some have a data/ subfolder
│       └── data/{raw,cleaned}/   ← project-specific data (natural DVC-track target)
├── data/                    lab-maintained CANONICAL datasets — the shared datastore
│   └── <proj-or-dataset>/   ← access-restricted: only members of the relevant project can read
└── users/
    └── <user>/              per-user space
```

Two facts drive the design:

1. **There are two data locations.** Canonical lab datasets live in `<LAB_ROOT>/data/` (shared, durable). Project-specific data lives in `<LAB_ROOT>/projects/<proj>/data/`. DVC's natural per-project track target is the latter; the former is shared source data (see §7.4 for how to treat it).
2. **`<LAB_ROOT>/data/` is access-restricted per project** — only people on a project can read its datasets. This is almost certainly enforced by **per-project Unix groups**. This is the single most important constraint, and it rules out the lab-wide shared cache I'd sketched earlier.

### 7.3 Revised architecture: per-project, scoped to the project's access group

**Correction (driven by §7.2 fact 2):** do **not** use one lab-wide shared cache. A DVC cache/remote is content-addressed blobs in a directory; **access to the directory = access to the data** (DVC has no per-blob ACLs). Pooling all projects into one cache would let anyone with cache access read every project's restricted data — breaking the access model the lab already maintains. So scope DVC **per project**, reusing each project's existing access group:

```
<LAB_ROOT>/projects/<proj>/        git clone + code (data/{raw,cleaned} are DVC-tracked)
<LAB_ROOT>/data/<proj>/dvc-remote/ ← per-project DVC REMOTE (own group = project's group; backed up with the datastore)
<cache>                            ← per-project cache, same FS as the clone, same group
```

- **Remote → a dedicated subdir under the access-controlled datastore.** `dvc remote add -d storage <LAB_ROOT>/data/<proj>/dvc-remote`. It inherits the project's existing group/permissions and rides the datastore's backup. Keep it a *dedicated* `dvc-remote/` dir of opaque hash-named blobs — do **not** point DVC at the human-readable canonical dataset folders.
- **Cache → per project (or per project's shared clone), `cache.shared group` with the project group.** Dedup happens *within* the project's members (the correct scope); cross-project dedup is intentionally given up because it would cross an access boundary.
- **Keep cache and remote separate** even within a project: the cache is prunable by `dvc gc` and is not a source of truth; the remote is what `dvc pull` reconstructs from. Cache-only = one `dvc gc` or disk hiccup from loss.

```bash
# per project, run in the project repo:
dvc remote add -d storage <LAB_ROOT>/data/<proj>/dvc-remote
dvc config cache.type "hardlink,symlink"   # ext4/NFS → hardlink (reflink needs CoW FS)
dvc config cache.shared group              # group-writable cache so project members can write
# + sysadmin: project group owns the cache/remote dirs, `chmod g+s` (setgid) so new blobs inherit it
```

### 7.4 What still gates the concrete config (narrowed by scribe facts)

- **Clone model — the big open one.** Does each project have **one shared clone** under `<LAB_ROOT>/projects/<proj>/` that members all work in, or does **each user clone** into `<LAB_ROOT>/users/<user>/`? This decides cache placement: one shared clone → the in-repo `.dvc/cache` is already shared, simplest; per-user clones → need a per-project shared cache dir on a common filesystem so the N clones dedup. **[TBD]**
- **Filesystem layout.** Are `projects/`, `data/`, `users/` the **same filesystem/mount** or separate? Hard/reflinks only dedup within one FS; if the cache and the clones are on different mounts, DVC falls back to copy (no dedup) or symlink. What FS is it (ext4 / XFS / ZFS / NFS)? — ext4/NFS → hardlink; XFS/ZFS → reflink possible. **[TBD]**
- **Backup of `<LAB_ROOT>/data/`.** Putting the remote there assumes the datastore is backed up. Confirm, and ideally an **off-server** copy (the whole point of a remote is durability beyond one box). **[TBD]**
- **Access groups.** Confirm the per-project groups exist and their names, since `cache.shared group` + setgid must use them. **[TBD: group naming convention; who administers groups on scribe.]**
- **Canonical `<LAB_ROOT>/data/` datasets** — should these be DVC-tracked too, or only project-specific data? Options: (a) leave them as-is (human-readable canonical store) and have projects reference them; (b) DVC-track a project's *copy/extract* of them under `projects/<proj>/data/`. Tracking the shared canonical store centrally is possible but heavier — likely defer. **[TBD]**

### 7.5 Self-contained guardrails (the "no Claude Code" answer)

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

### 7.6 Install & environment **[TBD]**

- Is `dvc` installable lab-wide (pip in a shared venv / conda / an environment module)? Pin one version across users (the pilot used 3.67.1). **[TBD]**
- A `setup-dvc-server.sh` (plain bash, no Claude Code) should do, idempotently: set `cache.dir` / `cache.type` / `cache.shared`, add the remote, run `dvc install`, install the check hook, and `dvc pull`. This is the server analog of the laptop `templates/setup-machine.sh`.

---

## 8. Open questions / next steps

1. **Pin the scribe facts in §7.4** — clone model (one shared clone per project vs. per-user clones), filesystem layout of `projects/`/`data/`/`users/`, backup of `<LAB_ROOT>/data/`, per-project group naming, whether canonical datasets get DVC-tracked. These gate the concrete config.
2. **Write `setup-dvc-server.sh`** (§7.6) and the `pre-push` check hook (§7.5) — the self-contained setup + guardrail, replacing the Claude Code `/tools sync-status` idea on the server.
3. Decide whether the lab guide lives in `docs/` here, or a CEL-owned repo (likely the latter, since it's institution-specific and server-coupled).
4. Resolve the pilot's separate LFS loose end (pre-LFS PDF churn) — unrelated to DVC, tracked in the pilot CHANGELOG.
