#!/usr/bin/env bash
# dvc-egress-guard.sh — refuse if any configured DVC remote points OFF approved
# on-server storage.
#
# Why: restricted CEL student data must never leave Scribe. The lab's git
# `.githooks/pre-push` hook blocks data egress through the *git* channel, but it
# cannot see `dvc push`, which is a *separate* channel to a DVC remote. If a DVC
# remote ever points off-Scribe (S3, Drive, a laptop, GitHub LFS), `dvc push`
# would exfiltrate restricted data silently. This guard is the DVC analog.
#
# Exit 0  every remote is under the approved prefix (safe), or no remote exists.
# Exit 1  some remote points off the approved prefix.
#
# Approved prefix (default = CEL Scribe lab root; override for other sites/tests):
#   DVC_ALLOWED_REMOTE_PREFIX=/home/research/ca_ed_lab/
set -uo pipefail

ALLOWED="${DVC_ALLOWED_REMOTE_PREFIX:-/home/research/ca_ed_lab/}"

command -v dvc >/dev/null 2>&1 || { echo "dvc-egress-guard: dvc not found — skipping" >&2; exit 0; }

# Parse machine-readable config, NOT `dvc remote list` (which wraps its output to
# terminal width and splits long URLs across lines). Each line: remote.<name>.url=<url>
bad=0
found=0
while IFS='=' read -r key url; do
  case "$key" in
    remote.*.url)
      found=1
      name="${key#remote.}"; name="${name%.url}"
      case "$url" in
        "$ALLOWED"*) : ;;                   # on approved storage — OK
        *)
          echo "🛑 dvc-egress-guard: remote '$name' is OFF approved storage" >&2
          echo "     url:     ${url:-<unset>}" >&2
          echo "     allowed: ${ALLOWED}*" >&2
          bad=1 ;;
      esac ;;
  esac
done < <(dvc config --list 2>/dev/null)

if [ "$found" -eq 0 ]; then
  echo "dvc-egress-guard: no DVC remotes configured (nothing to push)." >&2
  exit 0
fi

if [ "$bad" -ne 0 ]; then
  echo "🛑 Refusing — a DVC remote points off-server; restricted data must stay on Scribe." >&2
  echo "   Fix: dvc remote modify <name> url <path under ${ALLOWED}>" >&2
  exit 1
fi
echo "dvc-egress-guard: OK — all remotes under ${ALLOWED}" >&2
exit 0
