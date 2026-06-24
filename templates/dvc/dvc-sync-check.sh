#!/usr/bin/env bash
# dvc-sync-check.sh — warn if local DVC data isn't pushed to the remote.
#
# Catches the dangling-pointer failure: a `.dvc` pointer was created/committed
# but the bytes were never `dvc push`ed, so the cache exists only on this machine
# and a fresh checkout/pull elsewhere would break. (This is exactly what bit the
# belief_distortion_discrimination pilot — cache 0 B while the pointer was pushed.)
#
#   default          warn, exit 0  (advisory — safe in any workflow)
#   DVC_SYNC_BLOCK=1 exit 1 on pending uploads (for a blocking pre-push hook)
set -uo pipefail

command -v dvc >/dev/null 2>&1 || { echo "dvc-sync-check: dvc not found — skipping" >&2; exit 0; }

out="$(dvc status --cloud 2>&1)" || true

# Wordings DVC uses when there is nothing to push:
if printf '%s\n' "$out" | grep -qiE "are in sync|up to date|no data or pipelines|nothing to"; then
  echo "dvc-sync-check: OK — cache and remote in sync." >&2
  exit 0
fi
if [ -z "${out//[[:space:]]/}" ]; then
  echo "dvc-sync-check: OK — nothing to push." >&2
  exit 0
fi

echo "⚠ dvc-sync-check: local DVC blobs are NOT pushed to the remote:" >&2
printf '%s\n' "$out" | sed 's/^/     /' >&2
echo "   Run:  dvc push" >&2
[ "${DVC_SYNC_BLOCK:-0}" = "1" ] && exit 1
exit 0
