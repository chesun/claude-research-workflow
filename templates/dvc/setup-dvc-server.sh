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

# 5. install the DVC-aware pre-push hook + guard scripts into the repo's hooks dir.
#    core.hooksPath-aware (CEL convention is `.githooks/`); NEVER clobbers an
#    existing pre-push (e.g. the lab's data-egress hook) — instructs instead.
hookdir="$(git config --get core.hooksPath || true)"
if [ -z "$hookdir" ]; then
  if [ -d .githooks ]; then
    # lab convention: tracked hooks in .githooks/ — target it and make git use it
    hookdir=".githooks"; git config core.hooksPath .githooks
    echo "  set core.hooksPath=.githooks (lab convention) so hooks fire"
  else
    hookdir="$(git rev-parse --git-path hooks)"
  fi
fi
mkdir -p "$hookdir"
# guard scripts live next to the hook so it can call them via $(dirname) (idempotent)
cp "$here/dvc-egress-guard.sh" "$here/dvc-sync-check.sh" "$hookdir/"
chmod +x "$hookdir/dvc-egress-guard.sh" "$hookdir/dvc-sync-check.sh"

hook="$hookdir/pre-push"
if [ ! -e "$hook" ]; then
  cp "$here/githooks-pre-push" "$hook"; chmod +x "$hook"
  echo "✓ installed DVC-aware pre-push hook + guards → $hookdir/"
elif grep -q 'dvc-egress-guard.sh' "$hook" 2>/dev/null; then
  echo "✓ DVC already wired into $hook"
else
  echo "ℹ️  $hook already exists (e.g. the lab's data-egress hook) — NOT overwriting."
  echo "    Make it DVC-aware (reference: $here/githooks-pre-push):"
  echo "      1) extend its allowed_pattern to permit *.dvc, data/.gitignore, and"
  echo "         the MANIFEST/PROVENANCE/CHANGELOG contract (so pointers can push);"
  echo "      2) add near the top (guard scripts were just copied into $hookdir/):"
  echo '           "$(dirname "$0")/dvc-egress-guard.sh" || exit 1'
  echo '           "$(dirname "$0")/dvc-sync-check.sh" || true'
fi

echo "✅ DVC server setup complete."
echo "   Daily: edit data → dvc add <path> → dvc push"
echo "   Before logging off: $here/dvc-sync-check.sh"
