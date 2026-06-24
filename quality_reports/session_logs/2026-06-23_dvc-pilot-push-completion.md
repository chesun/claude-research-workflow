# 2026-06-23 — Resume + finish the DVC pilot push (belief_distortion_discrimination)

## Goal

Resume the paused LFS+DVC migration pilot (plan: `quality_reports/plans/2026-05-05_lfs-dvc-migration-plan.md`). Christina: "get back to working on the dvc setup." Scope chosen via AskUserQuestion: **finish the pilot push.**

## What I found (where it had paused)

The pilot's LFS half was largely done (12 PDFs in LFS); the DVC half was **half-finished with a latent risk**:

- `dvc init` done, remote `storage` configured → `~/Dropbox/research-data/belief_distortion_discrimination/dvc-cache`.
- `dvc add data_local` had run and `data_local.dvc` was committed **and pushed to origin/main** (commit `cfd75b4`)…
- …but **`dvc push` never ran** — the Dropbox cache was **0 B**, `dvc status -c` showed every file "new" (unpushed). **Dangling pointer:** a fresh clone + `dvc pull` would have failed, and the ~1.15 GB of data existed only in this machine's working tree (no off-machine copy).
- `dvc status` also showed `data_local` **modified** since the pointer was made (pointer stale vs working tree).
- `.DS_Store` (×10) were being swept into DVC tracking; no `.dvcignore` patterns.
- No data-doc contract (MANIFEST/PROVENANCE/CHANGELOG) in the pilot.

## What I did

1. **`.dvcignore`** — added `.DS_Store`.
2. **Re-`dvc add data_local`** — captured current state: hash `c77a083c…dir`, **263 files, ~1.15 GB**; `.DS_Store` now excluded (0 in cloud-diff).
3. **`dvc push`** — **256 files pushed; "Cache and remote are in sync"; cache now 1.1 GB** (was 0 B).
4. **Committed + pushed the refreshed pointer** (`eab28aa`) — `data_local.dvc` + `.dvcignore` + the dvc-managed `.gitignore` line. Pointer on origin now matches pushed blobs.
5. **Data-doc contract** (`5f20370`) — `data/MANIFEST.md`, `data/PROVENANCE.md`, `data/CHANGELOG.md`.
6. **Validation (all green):** `dvc status` = up to date; `dvc status -c` = in sync; branch 0 ahead / 0 behind origin/main; LFS intact (12).

## Decisions made (disclosed)

- **Doc-contract placement = tracked `data/`, not `data_local/`.** `data_local/` is wholesale-gitignored and git cannot re-include files beneath an ignored dir; placing docs inside it would also fight DVC's directory hashing. `data/` is unignored and conflict-free. MANIFEST states the actual data path is `data_local/`. Reversible if Christina prefers another spot.
- **PROVENANCE is an honest skeleton**, not fabricated. IRB, fielding dates, PII status, authorized-user list marked **TBD**; design/platform fields marked *(inferred)* from filenames (Prolific DEG/WTP BDM belief elicitation, employer/worker surveys by race, audit study). ⚠️ flagged that raw files likely contain participant identifiers → restricted; replication package will likely need a de-identified extract.
- **Scoped the DVC commit to exclude the PDF churn** — see below.

## Diagnosed (not acted on): pre-LFS PDF churn

`git status` showed ~51–57 PDFs under `master_supporting_docs/literature/papers/` as **modified**, though I touched none. `git lfs status` shows identical Git↔File hashes (e.g. `ac32f4b -> ac32f4b`): these are **pre-LFS binary blobs** (12 of 69 PDFs are actually in LFS; the rest were committed before `.gitattributes` got its LFS rule). The active filter now wants to convert them, so they read as "modified" perpetually. **Not caused by this work; not bundled into any commit here.** Resolution options (deferred to Christina): `git lfs migrate import`, `git add --renormalize`, or leave as-is. Recorded as a follow-up in the pilot's `data/CHANGELOG.md`.

## Open items

- **LFS PDF churn** (above) — decide and resolve.
- **PROVENANCE backfill** — the TBD fields.
- **`/tools sync-status` skill (§7.5) still unbuilt** — the one remaining workflow-template gap from the migration plan. Notably, it's exactly the tool whose "Pending uploads: N files" line would have surfaced the dangling pointer before it was committed. Good candidate for next session.
- **Pilot 7-day exit decision (D6)** — the go/no-go for bulk migration to other repos was never formally taken.

## Commits (belief_distortion_discrimination)

| Commit | What |
|---|---|
| `eab28aa` | dvc: refresh data_local pointer + push 1.1 GB to remote cache |
| `5f20370` | data: add MANIFEST / PROVENANCE / CHANGELOG contract |

All pushed to `origin/main` (0 ahead / 0 behind).

---

## Continuation — DVC lab-guide infrastructure (same day)

After the pilot push, the work shifted to designing + building the self-contained DVC infrastructure for the CEL **Scribe** server, toward a guide for the lab. **This is a personal passion project**; lab adoption is the lab's prerogative.

### Design doc

`quality_reports/dvc-setup-learnings.md` — living design doc. Covers: the gitignore/DVC relationship (root vs nested `.gitignore`, the wholesale-ignore descend rule), cache-vs-remote, the **scribe environment** (`/home/research/ca_ed_lab/`, `go_sbac` group, shared project folder, single FS, Stata, public GitHub repos, the existing data-safety model + `.githooks/pre-push`), the **per-project on-Scribe architecture**, audiences (Kramer/lab-wide vs project teams), cache growth + `dvc gc`. Context pulled from the `cel_resource_hub` repo (the lab's MkDocs site — **do not edit it; Christina ports**).

### The #1 safety finding

`dvc push` is a **second data-egress channel** the lab's existing git `.githooks/pre-push` hook can't see. So: the DVC remote **must** stay on Scribe; `.dvc` pointers are safe on public GitHub; and the existing pre-push hook needs a carve-out to allow pointers.

### Built + tested (`templates/dvc/`)

- `dvc-egress-guard.sh` — refuse off-server DVC remotes (the egress analog of the git hook).
- `dvc-sync-check.sh` — catch the dangling-pointer (unpushed-blobs) failure.
- `setup-dvc-server.sh` — idempotent per-project setup (**git required**; git-mode `dvc init`; hardlink+group cache; on-server remote; installs hook+guards into `.githooks/`, never clobbering an existing hook).
- `githooks-pre-push` — DVC-aware combined hook = lab data-block + `.dvc`/`.gitignore`/contract carve-out + the two guard calls. Faithful extension of `va_consolidated/.githooks/pre-push`.
- `README.md` — usage + operational gotchas.

### Decisions

- **git is a prerequisite** ("no point using DVC without git") — guide written with git alongside; dropped `--no-scm`.
- **Lab-deployment facts (backup, group mechanism) = out of scope** — not blockers; per-lab config.

### Validation

End-to-end **29/29**: 14 carve-out cases (real data blocked; pointers/`.gitignore`/contract/code allowed) + a 15-step Scribe simulation (pointer pushes through carve-out, `dvc push` to on-server remote, real-data push BLOCKED, off-server remote BLOCKED, old-version restore survives `dvc gc -A`). Two findings: (a) hardlink cache → tracked files read-only, edit via `dvc unprotect`; (b) parsing bug — use `dvc config --list`, never `dvc remote list` (wraps URLs).

### Commits (workflow repo)

`e844e85` (learnings doc) · `2689abb` (server arch) · `211245d` (scribe facts + egress rule) · `1ebaa2e` (guard+setup scripts) · `5b6769a` (git prerequisite) · `410f25e` (pre-push carve-out + e2e) · `458e924` (out-of-scope scoping).

### State / next

Infrastructure **complete and validated**. Remaining: draft the guide page as portable markdown in this repo (hub voice) for Christina to port to `cel_resource_hub` — not yet started. BDD's pre-LFS PDF churn remains a separate, parked LFS loose end.
