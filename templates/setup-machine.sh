#!/usr/bin/env bash
# =============================================================================
# setup-machine.sh — bootstrap this repo on a new machine
# =============================================================================
#
# Usage on a new machine, AFTER `git clone`:
#
#   cd <repo>
#   ./bin/setup-machine.sh
#
# This script:
#   1. Verifies git-lfs and dvc are installed (errors with install hint if not)
#   2. Initializes LFS and pulls LFS-tracked blobs (paper PDFs, etc.)
#   3. Pulls DVC-tracked data files from the configured remote (e.g., Dropbox)
#   4. Reports the final state so you can confirm success
#
# Per-project customization: append project-specific setup steps below the
# "Project-specific" marker (Stata version, R packages, Python venv, etc.).
#
# Reference: .claude/rules/data-version-control.md
# =============================================================================

set -euo pipefail

PROJECT="$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")"
echo "Setting up $PROJECT for this machine..."
echo

# -----------------------------------------------------------------------------
# 1. Verify required tools
# -----------------------------------------------------------------------------
missing=()
command -v git-lfs >/dev/null 2>&1 || missing+=("git-lfs")
command -v dvc >/dev/null 2>&1 || missing+=("dvc")

if [ ${#missing[@]} -gt 0 ]; then
  echo "ERROR: missing required tools: ${missing[*]}"
  echo "Install with:  brew install ${missing[*]}"
  exit 1
fi

# -----------------------------------------------------------------------------
# 2. Initialize LFS and pull blobs
# -----------------------------------------------------------------------------
if [ -f .gitattributes ] && grep -q "filter=lfs" .gitattributes; then
  echo "==> Initializing Git LFS"
  git lfs install --local
  echo "==> Pulling LFS-tracked files"
  git lfs pull
else
  echo "==> No LFS patterns in .gitattributes; skipping LFS step"
fi

# -----------------------------------------------------------------------------
# 3. Pull DVC-tracked data
# -----------------------------------------------------------------------------
if [ -d .dvc ]; then
  echo
  echo "==> Pulling DVC-tracked data"
  if dvc pull 2>&1; then
    echo "DVC pull complete."
  else
    echo
    echo "WARNING: dvc pull reported errors. The DVC remote may be unreachable"
    echo "(e.g., Dropbox not yet synced on this machine). Re-run after Dropbox"
    echo "finishes syncing, or check the remote config: dvc remote list"
  fi
else
  echo "==> No .dvc/ directory; skipping DVC step"
fi

# -----------------------------------------------------------------------------
# 4. Report final state
# -----------------------------------------------------------------------------
echo
echo "=== Setup verification ==="
if [ -f .gitattributes ] && grep -q "filter=lfs" .gitattributes; then
  echo "LFS files:    $(git lfs ls-files | wc -l | tr -d ' ') tracked"
fi
if [ -d .dvc ]; then
  echo "DVC status:   $(dvc status 2>&1 | head -1)"
fi

echo
echo "Done. Safe to start working in $PROJECT."

# -----------------------------------------------------------------------------
# Project-specific (uncomment / extend per repo)
# -----------------------------------------------------------------------------
# Example: install Stata packages
# stata -b "do bin/install-packages.do"
#
# Example: create R venv
# Rscript -e 'renv::restore()'
#
# Example: create Python venv
# python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
