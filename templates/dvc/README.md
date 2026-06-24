# DVC server scripts (self-contained)

Three plain-bash scripts for running DVC on a shared analysis server **without Claude Code** — built for the CEL Scribe setup but parameterized for any site. They make `dvc push` safe for restricted data and catch the dangling-pointer failure mode. Design rationale: `quality_reports/dvc-setup-learnings.md` (esp. §7).

All three require `bash` + `dvc` only. Tested against the `belief_distortion_discrimination` pilot and a throwaway repo (13/13 cases, 2026-06-23).

## The scripts

| Script | Guards against | Use |
|---|---|---|
| `dvc-egress-guard.sh` | **Data egress.** Restricted data leaving the server via a misconfigured (off-site) DVC remote — the channel the git pre-push hook can't see. | Refuses (exit 1) if any DVC remote is not under the approved prefix. |
| `dvc-sync-check.sh` | **Dangling pointer.** A `.dvc` pointer committed/used but the bytes never `dvc push`ed (cache exists only locally). | Warns (exit 0), or blocks (exit 1) with `DVC_SYNC_BLOCK=1`. |
| `setup-dvc-server.sh` | — | Idempotent per-project setup: `dvc init --no-scm`, hardlink+group-shared cache, on-server remote, egress verification, optional git pre-push hook. |

## Configuration

- `DVC_ALLOWED_REMOTE_PREFIX` — approved on-server storage prefix. **Default: `/home/research/ca_ed_lab/`** (CEL Scribe lab root). Override for other sites or testing.
- `REMOTE_PATH` (setup only, required) — the on-server directory for this project's DVC remote, e.g. `/home/research/ca_ed_lab/data/<proj>/dvc-remote`. Setup refuses a `REMOTE_PATH` outside the allowed prefix.
- `INSTALL_HOOK=1` (setup only) — also install a git `pre-push` hook running both guards (only meaningful where git is used; most CEL users sync by FileZilla, so the scripts also work standalone via `--no-scm`).
- `DVC_SYNC_BLOCK=1` (sync-check) — make a pending state a hard failure instead of a warning.

## Why egress is a separate guard

The lab's existing `.githooks/pre-push` blocks restricted data on the **git → GitHub** channel. `dvc push` is a **separate** channel to a DVC remote; the git hook never inspects it. If a DVC remote is ever pointed off-server, `dvc push` would exfiltrate restricted student data silently. `dvc-egress-guard.sh` is the DVC-channel analog: it enforces that every remote stays on approved on-server storage. See `data-safety.md` / `local-server-sync.md` in `cel_resource_hub`.

## Notes / limits

- `dvc-egress-guard.sh` parses `dvc config --list` (machine-readable), **not** `dvc remote list` — the latter wraps long URLs to terminal width and is unsafe to parse.
- The egress prefix match is a literal string prefix; keep `REMOTE_PATH` absolute and canonical.
- `setup-dvc-server.sh` embeds the script directory path into the generated git hook; if you relocate these scripts, re-run setup.
