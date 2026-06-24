#!/usr/bin/env bash
# setup-dvc-server.sh — one-time, idempotent per-project DVC setup for the CEL
# Scribe server. Self-contained: plain dvc + git + bash, no Claude Code needed.
# Run it from inside the project folder. Safe to re-run.
#
# Required:
#   REMOTE_PATH   on-Scribe directory for the DVC remote, under the lab root, e.g.
#                 /home/research/ca_ed_lab/data/<proj>/dvc-remote
# Optional:
#   DVC_ALLOWED_REMOTE_PREFIX  default /home/research/ca_ed_lab/ — egress allowlist
#   INSTALL_HOOK=1             also wire a git pre-push hook (only if this is a git repo)
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
ALLOWED="${DVC_ALLOWED_REMOTE_PREFIX:-/home/research/ca_ed_lab/}"

command -v dvc >/dev/null || { echo "dvc not installed — pip install dvc / module load dvc"; exit 1; }
: "${REMOTE_PATH:?set REMOTE_PATH to an on-Scribe dir under $ALLOWED}"

# Hard stop: the remote you are configuring must be on approved storage.
case "$REMOTE_PATH" in
  "$ALLOWED"*) : ;;
  *) echo "🛑 REMOTE_PATH ($REMOTE_PATH) is not under $ALLOWED — refusing (data-egress risk)."; exit 1 ;;
esac

# 1. init — --no-scm so it works whether or not git is used here (most CEL users don't)
[ -d .dvc ] || dvc init --no-scm -q
echo "✓ dvc initialized"

# 2. cache: link instead of copy (single FS on Scribe → hardlink), group-shared
dvc config cache.type "hardlink,symlink"
dvc config cache.shared group
echo "✓ cache: hardlink + group-shared"

# 3. remote — on Scribe only (idempotent: modify if it exists, else add)
mkdir -p "$REMOTE_PATH"
if dvc config --list 2>/dev/null | grep -q '^remote\.storage\.url='; then
  dvc remote modify storage url "$REMOTE_PATH"
else
  dvc remote add -d storage "$REMOTE_PATH"
fi
echo "✓ remote 'storage' → $REMOTE_PATH"

# 4. verify the egress guard is satisfied for this configuration
DVC_ALLOWED_REMOTE_PREFIX="$ALLOWED" "$here/dvc-egress-guard.sh"

# 5. optional git pre-push hook (egress + dangling-pointer), only where git is used
if [ "${INSTALL_HOOK:-0}" = "1" ] && git rev-parse --git-dir >/dev/null 2>&1; then
  hookdir="$(git rev-parse --git-path hooks)"
  mkdir -p "$hookdir"
  cat > "$hookdir/pre-push" <<HOOK
#!/usr/bin/env bash
# auto-installed by setup-dvc-server.sh — DVC egress + dangling-pointer guards.
set -e
DVC_ALLOWED_REMOTE_PREFIX="$ALLOWED" "$here/dvc-egress-guard.sh"
"$here/dvc-sync-check.sh"   # advisory; set DVC_SYNC_BLOCK=1 here to block on unpushed data
HOOK
  chmod +x "$hookdir/pre-push"
  echo "✓ git pre-push hook installed → $hookdir/pre-push"
fi

echo "✅ DVC server setup complete."
echo "   Daily: edit data → dvc add <path> → dvc push"
echo "   Before logging off: $here/dvc-sync-check.sh"
