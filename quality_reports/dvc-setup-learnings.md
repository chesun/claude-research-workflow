# DVC Setup — Learnings & Lab-Guide Draft

**Status:** DRAFT (living doc) — capturing learnings from the `belief_distortion_discrimination` DVC pilot, toward a data-version-control guide for the Education Lab (CEL, UC Davis) server. **This is a personal passion project**; lab adoption is the lab's prerogative, so lab-deployment specifics (backup, group mechanism) are presented as per-lab config, not blockers.
**Started:** 2026-06-23
**Companions:** `.claude/rules/data-version-control.md` (the rule), `quality_reports/plans/2026-05-05_lfs-dvc-migration-plan.md` (the plan), `quality_reports/plans/2026-05-05_lfs-vs-dvc-explainer.md` (concept primer), `quality_reports/session_logs/2026-06-23_dvc-pilot-push-completion.md` (the pilot session).

> **Promotion path:** this is the design/scratch doc. The polished guide belongs in the lab's existing MkDocs site — the **`cel_resource_hub` repo**, `docs/workflow-tips/` — as a sibling to `data-safety.md` / `gitignore-setup.md` / `local-server-sync.md` (see §8 for audiences & placement).

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

### 7.2 The scribe environment (concrete facts)

Source: the lab's own resource hub repo `cel_resource_hub` (`docs/workflow-tips/{working-on-scribe,data-safety,gitignore-setup,local-server-sync}.md`, `docs/resources/tools.md`).

- **Server:** `Scribe.ssds.ucdavis.edu` — UC Davis SSDS, Linux. Reachable only over the **DSS VPN** with **Kerberos** login.
- **Lab root:** `/home/research/ca_ed_lab/`; projects live under `projects/<proj>/`. Some projects keep a `data/` subfolder.
- **Group permissions:** members run **`go_sbac`** each login to set the **CA Education Lab group** so files are lab-readable. So there is a lab-wide group mechanism already; the per-project access restriction on the canonical datastore sits on top of it (exact mechanism — extra groups / dir perms — TBD).
- **Analysis:** **Stata**, run in batch (`stata-mp -b do …`); no local install — Stata runs on Scribe.
- **Clone model — confirmed:** *one shared project folder per project* that all members work in (not per-user clones). So a project's in-repo `.dvc/cache` is automatically shared by everyone who uses that folder — the simple case.
- **Filesystem — confirmed:** everything is one filesystem → hardlinks work for cache dedup.
- **git posture — confirmed:** git is *optional* lab-wide ("recommended, not required"); most members sync code by **FileZilla**, not git. **Only Christina uses git on Scribe**, so far only for `va_consolidated`. This is decisive for §7.6.
- **Two data locations:** canonical lab datasets in `<lab>/data/` (access-restricted per project); project-specific data in `projects/<proj>/data/`. The latter is DVC's natural per-project target.

**The lab already has a mature data-safety model that DVC must not break:**

> *"Code lives on GitHub. Confidential student data lives only on Scribe. The two never mix."*

GitHub repos are **public**. `data/`, `estimates/`, `output/` are gitignored; **a pre-push hook (`.githooks/pre-push`) aborts any `git push` carrying a `data/`/`estimates/` file** off the server (logs are tracked, scrubbed of PII). Restricted sources: CALPADS, CSAC, CalSCHLS, NSC, surveys with respondent emails.

### 7.3 ⚠️ The #1 DVC rule for this lab: `dvc push` is a second data channel the pre-push hook can't see

This is the most important thing in this section. The lab's entire safety model guards the **git → public-GitHub** channel (gitignore + the pre-push hook). **DVC introduces a *separate* channel — `dvc push` to a DVC *remote* — that those guards never inspect.** If a DVC remote is ever pointed off-Scribe (S3, Google Drive, a laptop, GitHub LFS), `dvc push` **exfiltrates restricted student data**, and the existing pre-push hook does **not** fire (it only scans git pushes). That is a FERPA-class incident.

Non-negotiables for DVC in this lab:

1. **The DVC remote MUST be an on-Scribe path** (or an institution-approved on-prem store) — **never** an external/cloud remote for restricted data. The on-Scribe remote in §7.4 isn't just convenient; it's a hard safety requirement.
2. **Add a `dvc push` guard analogous to the git pre-push hook** — e.g., a wrapper / pre-`dvc push` check that the configured `remote.*.url` resolves under `/home/research/ca_ed_lab/` and refuses otherwise. The git pre-push hook cannot cover this; DVC needs its own.
3. **`.dvc` pointer files are SAFE to commit to public GitHub** (they're just md5 + size + path — no data). But the existing pre-push hook blocks everything under `data/`; it needs a **carve-out to allow `*.dvc` pointers and `data/.gitignore`** while still blocking real data, or DVC pointers placed under `data/` will trip the guard (false positive).

### 7.4 Architecture: per-project, on-Scribe, scoped to the project's access group

A DVC cache/remote is content-addressed blobs in a directory; **directory access = data access** (DVC has no per-blob ACLs). So a lab-wide shared cache would let anyone with cache access read every project's restricted data. Scope DVC **per project**, reusing each project's existing access group, with the remote on Scribe (per §7.3):

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

### 7.5 What still gates the concrete config

Resolved by the scribe facts (§7.2): **clone model** = one shared project folder → the in-repo `.dvc/cache` is already shared, no separate shared-cache dir needed; **filesystem** = single FS → hardlink dedup works (`cache.type "hardlink,symlink"`). Still open:

- **Backup of `/home/research/ca_ed_lab/data/`.** Putting the remote there assumes the datastore is backed up (user believes so; details unknown). Confirm, and ideally an **on-prem off-server** copy — but remember §7.3: any off-Scribe copy of restricted data must be institution-approved, never a personal cloud. **[TBD: backup details.]**
- **The per-project access mechanism on `<lab>/data/`.** `go_sbac` sets a lab-wide group; the per-project restriction on the datastore sits on top (extra groups? dir perms?). `cache.shared group` + setgid need the right group name. **[TBD: how per-project restriction is enforced + group names.]**
- **FS type** (ext4 / ZFS / XFS) — only affects whether reflink is available *on top of* hardlink; hardlink already works, so this is a nice-to-have. **[minor]**
- **Canonical `<lab>/data/` datasets** — DVC-track centrally (Kramer's lab-wide use case, §7.0/audiences) or only project-specific data? Tracking the shared canonical store in place is heavier and changes how everyone reads those files — likely defer; start with project-folder data. **[TBD]**

### 7.6 Self-contained guardrails (the "no Claude Code" answer)

**git is a prerequisite** (decided 2026-06-23 — "no point using DVC without git"; the guide teaches git alongside, cross-linking the hub's `git-for-newcomers.md`). That settles the guardrail home: both guards wire into the repo's **git `pre-push` hook**, sitting alongside the lab's existing `.githooks/pre-push` data-egress hook. `setup-dvc-server.sh` does this safely — it is `core.hooksPath`-aware and never clobbers an existing hook (prints add-by-hand lines instead). The guards are also plain scripts runnable by hand (e.g. `dvc-sync-check.sh` before logging off). Two things to guard:

**Guard A — data egress (the safety guard, from §7.3).** Before any `dvc push`, verify the remote stays on Scribe:

```bash
# refuse dvc push if the default remote points off /home/research/ca_ed_lab/
url=$(dvc remote list | awk '$1=="storage"{print $2}')
case "$url" in
  /home/research/ca_ed_lab/*) : ;;                    # OK — on Scribe
  *) echo "🛑 DVC remote is OFF-Scribe ($url) — refusing push of restricted data" >&2; exit 1 ;;
esac
```

This is the DVC analog of the lab's `.githooks/pre-push` data-egress guard, covering the channel that hook can't see. Ship it as a tracked script and/or a `pre-push` git hook.

**Guard B — dangling pointer (the durability guard, from §5).** The dangling-pointer risk was going to be caught by `/tools sync-status` — which won't exist on the server. Self-contained replacements, in order of preference:

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

### 7.7 Install & environment **[TBD]**

- Is `dvc` installable lab-wide (pip in a shared venv / conda / an environment module)? Pin one version across users (the pilot used 3.67.1). **[TBD]**
- A `setup-dvc-server.sh` (plain bash, no Claude Code) should do, idempotently: set `cache.dir` / `cache.type` / `cache.shared`, add the remote, run `dvc install`, install the check hook, and `dvc pull`. This is the server analog of the laptop `templates/setup-machine.sh`.

### 7.8 Cache growth & cleanup (`dvc gc`)

Yes — by default the cache keeps **every** version's bytes (content-addressed), so it grows monotonically. But it grows with **churn, not total-size × versions**, and there's a cleanup valve:

- **Dedup bounds it.** Identical files across versions are stored once. Re-`dvc add` after editing 2 of 263 files adds ~2 files' worth of blobs, not another 1.15 GB. So a dataset that's appended/tweaked grows slowly; one that's fully regenerated each run grows fast (each regen may rewrite every file → a full new copy).
- **`dvc gc` prunes unreferenced versions.** Scope it by what you want to keep:
  - `dvc gc -w` — keep only the **current workspace** version (aggressive).
  - `dvc gc -A` — keep versions referenced by **all git branches/tags/commits** (conservative — preserves full history; the right default).
  - add `-c` / `--cloud` to also prune the **remote**, not just the local cache.
  - `dvc gc` **deletes** — anything not referenced by the chosen scope is gone. Pair it with git-tag discipline: tag the data versions you must never lose, then `gc -A` can't drop them.
- **On the shared server this needs an owner.** The shared project cache accumulates every member's edits. Manage by: a periodic `dvc gc -A` (keeps everything git still points to, drops true orphans), and watching `du -sh .dvc/cache`. This is a natural data-steward (Kramer) responsibility.
- **Retention is a policy choice**, not a default to accept silently: "keep every version forever" (max reproducibility, max space) vs. "gc to tagged releases only" (lean, but you can only return to tagged states). Decide per project and write it down. **[TBD for the guide: recommend a default — likely `gc -A` quarterly + tag every version cited in a paper.]**

---

## 8. Audiences & where the guide lives

The guide's home is the lab's existing MkDocs site, the **`cel_resource_hub` repo** — a DVC page belongs in `docs/workflow-tips/` as a sibling to `data-safety.md`, `gitignore-setup.md`, `local-server-sync.md`, `reproducible-pipelines.md` (match the hub's first-person, admonition-heavy voice; ADR 0003 "personal-project-voice"). It should cross-link the egress story to `data-safety.md`/`local-server-sync.md#…pre-push-hook`.

**git is a prerequisite for either track** (decided 2026-06-23): the guide is written *with git alongside* and presents DVC as a layer on top of git, cross-linking `git-for-newcomers.md`. No `--no-scm` path — DVC without git loses its whole point (the version history lives in git's history of the pointer, §2/§5).

Two audiences (per Christina), which the page should serve as two tracks:

1. **Kramer (lab data manager, has access to *all* lab data).** Awareness-level: DVC *could* version/dedup/integrity-check the whole `<lab>/data/` store, with Kramer owning the git repo of pointers (git is the prerequisite). Caveat: tracking the canonical store in place changes how everyone currently reads those files — likely defer; start with project-folder data. Frame as "here's the tool, your call."
2. **Project teams maintaining data in project folders.** Concrete: per-project DVC (the §7.4 architecture), remote on Scribe, pointers safe on public GitHub. Each adopting project uses git (Method B in `local-server-sync.md`), so DVC slots onto the git-on-Scribe pattern Christina already runs for `va_consolidated`.

## 9. Open questions / next steps

1. ⛔ **OUT OF SCOPE (2026-06-23)** — the remaining lab-deployment facts (datastore backup details, the per-project group mechanism on `<lab>/data/`, central tracking of canonical datasets) are **not blockers**. This is a personal passion project; whether and how the lab adopts DVC is the lab's prerogative. The guide presents these as "configure per your lab's setup" notes, not open questions. Clone model + filesystem are resolved; everything else needed to *use* the tooling is built.
2. ✅ **DECIDED (2026-06-23)** — git is a **prerequisite**; the guide is written *with git alongside it* (cross-link `git-for-newcomers.md`). No `--no-scm` path. `setup-dvc-server.sh` now requires a git repo and uses git-mode `dvc init`. Reflected in §7.6 / §8 and the scripts.
3. ✅ **DONE (2026-06-23)** — the three self-contained scripts are built and tested (13/13 cases against the BDD pilot + a throwaway repo): `templates/dvc/{dvc-egress-guard,dvc-sync-check,setup-dvc-server}.sh` (+ `README.md`). Egress guard (Guard A), dangling-pointer check (Guard B), idempotent setup. Bug found & fixed in testing: never parse `dvc remote list` (it wraps URLs to terminal width) — use `dvc config --list`. These replace the Claude Code `/tools sync-status` idea server-side.
4. ✅ **DONE (2026-06-23)** — the `.githooks/pre-push` carve-out is built + validated: `templates/dvc/githooks-pre-push` (DVC-aware combined hook = lab data-block + `.dvc`/`.gitignore`/contract carve-out + the two guard calls). `setup-dvc-server.sh` installs it into `.githooks/` (lab convention) and never clobbers an existing hook. **Validated end-to-end (29/29):** 14 carve-out cases + a 15-step Scribe simulation (pointer pushes through, on-server `dvc push`, real-data push blocked, off-server remote blocked, old-version restore survives `dvc gc -A`). Two operational findings recorded in `templates/dvc/README.md`: (a) hardlink cache → tracked files are read-only, edit via `dvc unprotect`; (b) set `core.hooksPath` before/at setup or `.git/hooks` installs won't fire.
5. ✅ **DONE (2026-06-23)** — single-page guide drafted at `quality_reports/dvc-guide-draft.md` (hub MkDocs voice, admonitions, cross-links to `data-safety.md` / `git-for-newcomers.md` / `local-server-sync.md`; covers model → safety rule → layout → setup → daily → restore → gc → gotchas → guards → when-not-to). Portable; Christina ports to `cel_resource_hub/docs/workflow-tips/` (do not edit the hub directly). A "porting note" at the bottom lists the fix-ups (script paths, link check, `mkdocs build --strict`, nav).
6. Resolve the pilot's separate LFS loose end (pre-LFS PDF churn) — unrelated to DVC, tracked in the pilot CHANGELOG.
