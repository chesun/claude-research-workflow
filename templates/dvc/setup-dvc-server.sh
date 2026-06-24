#!/usr/bin/env bash
# setup-dvc-server.sh — one-time, idempotent per-project DVC setup for the CEL
# Scribe server. Self-contained: plain dvc + git + bash, no Claude Code needed.
# Run it from inside the project folder. Safe to re-run.
#
# PREREQUISITE: this must be a git repo. DVC's versioning value comes from git
# tracking the pointer over time — there's no point running DVC without git.
#
# Required:
#   REMOTE_PATH   on-Scribe directory for the DVC remote, under the lab root, e.g.
#                 /home/research/ca_ed_lab/data/<proj>/dvc-remote
# Optional:
#   DVC_ALLOWED_REMOTE_PREFIX  default /home/research/ca_ed_lab/ — egress allowlist
#
# Wires the egress + dangling-pointer guards into the repo's pre-push hook
# (core.hooksPath-aware; never clobbers an existing hook like the lab's egress hook).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
ALLOWED="${DVC_ALLOWED_REMOTE_PREFIX:-/home/research/ca_ed_lab/}"

command -v dvc >/dev/null || { echo "dvc not installed — pip install dvc / module load dvc"; exit 1; }

# git is a PREREQUISITE. DVC's versioning value comes from git tracking the
# pointer over time; there's no point running DVC without it. So no --no-scm.
git rev-parse --git-dir >/dev/null 2>&1 || {
  echo "🛑 This folder is not a git repo. DVC here requires git (the prerequisite)."
  echo "   Set up git first (see the hub's git-for-newcomers guide), then re-run."
  exit 1
}

: "${REMOTE_PATH:?set REMOTE_PATH to an on-Scribe dir under $ALLOWED}"

# Hard stop: the remote you are configuring must be on approved storage.
case "$REMOTE_PATH" in
  "$ALLOWED"*) : ;;
  *) echo "🛑 REMOTE_PATH ($REMOTE_PATH) is not under $ALLOWED — refusing (data-egress risk)."; exit 1 ;;
esac

# 1. init in git mode — integrates DVC with git so the pointer is versioned
[ -d .dvc ] || dvc init -q
echo "✓ dvc initialized (git-tracked)"

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

# 5. wire the guards into the repo's pre-push hook — SAFELY.
#    Respect core.hooksPath (the CEL convention is `.githooks/`), and NEVER
#    clobber an existing pre-push (e.g. the lab's data-egress hook). Create one
#    if absent; otherwise print the lines to add by hand.
hookdir="$(git config --get core.hooksPath || true)"
[ -n "$hookdir" ] || hookdir="$(git rev-parse --git-path hooks)"
hook="$hookdir/pre-push"
guard_block="# --- DVC guards (added by setup-dvc-server.sh) ---
DVC_ALLOWED_REMOTE_PREFIX=\"$ALLOWED\" \"$here/dvc-egress-guard.sh\" || exit 1   # block off-server remotes
\"$here/dvc-sync-check.sh\" || true                                              # warn on unpushed data"

if [ ! -e "$hook" ]; then
  mkdir -p "$hookdir"
  { printf '#!/usr/bin/env bash\nset -e\n\n'; printf '%s\n' "$guard_block"; } > "$hook"
  chmod +x "$hook"
  echo "✓ created pre-push hook with DVC guards → $hook"
elif grep -q 'dvc-egress-guard.sh' "$hook" 2>/dev/null; then
  echo "✓ DVC guards already present in $hook"
else
  echo "ℹ️  $hook already exists (e.g. the lab's data-egress hook) — NOT overwriting."
  echo "    Add these lines to it so DVC is guarded too:"
  echo "    ----"
  printf '%s\n' "$guard_block" | sed 's/^/    /'
  echo "    ----"
fi

echo "✅ DVC server setup complete."
echo "   Daily: edit data → dvc add <path> → dvc push"
echo "   Before logging off: $here/dvc-sync-check.sh"
