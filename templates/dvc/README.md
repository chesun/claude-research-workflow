# DVC server scripts (self-contained)

Three plain-bash scripts for running DVC on a shared analysis server **without Claude Code** — built for the CEL Scribe setup but parameterized for any site. They make `dvc push` safe for restricted data and catch the dangling-pointer failure mode. Design rationale: `quality_reports/dvc-setup-learnings.md` (esp. §7).

All require `bash` + `dvc` (and `setup-dvc-server.sh` requires a git repo). Validated 2026-06-23: 14 carve-out cases (real data blocked; pointers/`.gitignore`/contract/code allowed) + a 15-step end-to-end Scribe simulation (git + on-server remote + the real hook: pointer pushes through, `dvc push` to on-server remote, real-data push blocked, off-server remote blocked, old-version restore survives `dvc gc -A`).

## Operational gotchas (worth surfacing in the guide)

- **Read-only working files.** With a hardlink/symlink cache, DVC-tracked files are checked out **read-only** to protect the cache. To edit one in place, `dvc unprotect <path>` first (or just have your script regenerate it). Then `dvc add` the new version.
- **Hook path ordering.** `setup-dvc-server.sh` installs into `.githooks/` when that dir exists (and sets `core.hooksPath`). If you set `core.hooksPath` *after* running setup, hooks installed into `.git/hooks/` won't fire. Configure the hooks path (or have `.githooks/`) before/at setup.

## The scripts

| Script | Guards against | Use |
|---|---|---|
| `dvc-egress-guard.sh` | **Data egress.** Restricted data leaving the server via a misconfigured (off-site) DVC remote — the channel the git pre-push hook can't see. | Refuses (exit 1) if any DVC remote is not under the approved prefix. |
| `dvc-sync-check.sh` | **Dangling pointer.** A `.dvc` pointer committed/used but the bytes never `dvc push`ed (cache exists only locally). | Warns (exit 0), or blocks (exit 1) with `DVC_SYNC_BLOCK=1`. |
| `setup-dvc-server.sh` | — | Idempotent per-project setup (**git repo required**): `dvc init`, hardlink+group-shared cache, on-server remote, egress verification, and safe pre-push hook wiring (targets `.githooks/` per lab convention). |
| `githooks-pre-push` | Both, in one hook | DVC-aware replacement for the lab's `.githooks/pre-push`: blocks real data on the git channel **with a carve-out** for `*.dvc` / `data/.gitignore` / the doc contract, and calls the two guards above. Install for a new project; for an existing lab hook, apply the carve-out + add the two guard calls. |

## Configuration

- `DVC_ALLOWED_REMOTE_PREFIX` — approved on-server storage prefix. **Default: `/home/research/ca_ed_lab/`** (CEL Scribe lab root). Override for other sites or testing.
- `REMOTE_PATH` (setup only, required) — the on-server directory for this project's DVC remote, e.g. `/home/research/ca_ed_lab/data/<proj>/dvc-remote`. Setup refuses a `REMOTE_PATH` outside the allowed prefix.
- `DVC_SYNC_BLOCK=1` (sync-check) — make a pending state a hard failure instead of a warning.

**git is a prerequisite.** DVC's versioning value comes from git tracking the pointer over time, so `setup-dvc-server.sh` requires a git repo (no `--no-scm`) and wires the guards into the repo's `pre-push` hook. It is `core.hooksPath`-aware and never overwrites an existing hook (e.g. the lab's data-egress hook) — if one exists, it prints the lines to add by hand.

## Why egress is a separate guard

The lab's existing `.githooks/pre-push` blocks restricted data on the **git → GitHub** channel. `dvc push` is a **separate** channel to a DVC remote; the git hook never inspects it. If a DVC remote is ever pointed off-server, `dvc push` would exfiltrate restricted student data silently. `dvc-egress-guard.sh` is the DVC-channel analog: it enforces that every remote stays on approved on-server storage. See `data-safety.md` / `local-server-sync.md` in `cel_resource_hub`.

## Notes / limits

- `dvc-egress-guard.sh` parses `dvc config --list` (machine-readable), **not** `dvc remote list` — the latter wraps long URLs to terminal width and is unsafe to parse.
- The egress prefix match is a literal string prefix; keep `REMOTE_PATH` absolute and canonical.
- `setup-dvc-server.sh` embeds the script directory path into the generated git hook; if you relocate these scripts, re-run setup.
