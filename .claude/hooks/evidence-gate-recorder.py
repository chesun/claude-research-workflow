#!/usr/bin/env python3
"""
Evidence-gate recorder — Tier-1 always-on PostToolUse hook (evidence-gating Phase 1).

Fires after Edit/Write/MultiEdit to a supported research-artifact file and
SILENTLY records, to the verification ledger, the normalized-content diff
("residue") of the file versus its `HEAD` baseline. One row per file, updated
in place, with Check = `no-logic-change`.

This is the recorder half of the evidence-gating architecture (plan
`quality_reports/plans/2026-05-29_evidence-gating-build-plan.md`):

  - Record (this hook): always-on, silent, non-blocking. It gathers evidence
    continuously and never nags. The edit has already landed (PostToolUse), so
    there is nothing to simulate and nothing to block.
  - Gate (Phase 2 critic, optional commit hook): the *claim* of a clean
    refactor is blocked when this hook recorded a non-empty residue.

The recorder alone does not block — that is honest and intended. Its standalone
value is a deterministic evidence trail.

Scope:
  - LANGUAGE FILTER: only .do/.doh/.r/.R/.py/.tex (via derive_lib.language_for_path).
    Everything else (incl. all .md) → exit 0.
  - PATH SCOPE: only research-artifact roots. The default roots
    (DEFAULT_RESEARCH_ROOTS below) are derived from the CLAUDE.md Folder
    Structure, but each repo MAY override them via an `**Analysis roots:**`
    header line in its CLAUDE.md (see `_research_roots`). This makes the
    recorder configurable per-repo: consumers with heterogeneous layouts
    (e.g. Stata code in `do/` instead of `scripts/`) declare their analysis
    dirs and the recorder scopes to them. CLAUDE.md is Class B (not
    propagated), so each repo's declaration persists. The workflow's own infra
    (.claude/**), quality_reports/**, templates/**, master_supporting_docs/**,
    decisions/**, data/**, explorations/** are EXCLUDED by default — a
    no-logic-change claim is meaningful for research artifacts, not
    infrastructure.

Conventions mirrored from derive-check-advisory.py and
stata-comment-balance-check.py: stdin JSON, fail-open everywhere, exit 0,
never emit a block decision.

Install (in .claude/settings.json, PostToolUse, matcher "Write|Edit|MultiEdit"):
    python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/evidence-gate-recorder.py
(Registration is a SEPARATE manual step — this hook does not edit settings.json.)
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Default research-artifact roots (repo-relative). A no-logic-change record is
# only written when the edited file lives under one of these. Derived from the
# CLAUDE.md Folder Structure. Used as the fallback when a repo's CLAUDE.md does
# not declare an `**Analysis roots:**` header (see _research_roots).
DEFAULT_RESEARCH_ROOTS = (
    "paper/",
    "talks/",
    "scripts/",
    "replication/",
    "figures/",
    "tables/",
    "preambles/",
)

# Matches a CLAUDE.md header line declaring analysis roots, e.g.
#   **Analysis roots:** do/, paper/, tables/
#   Analysis roots: scripts/ paper/
# Tolerates optional surrounding ** markdown on the label and optional leading
# list markers. The value (group 1) is parsed separately by _research_roots.
_ANALYSIS_ROOTS_RE = re.compile(
    r"^\s*[-*]?\s*\*{0,2}\s*analysis roots\s*:\s*\*{0,2}\s*(.+?)\s*$",
    re.IGNORECASE,
)

_LEDGER_REL = ".claude/state/verification-ledger.md"
_CHECK_SLUG = "no-logic-change"


def _load_lib(name: str):
    lib_path = Path(__file__).resolve().parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, lib_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {lib_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _repo_relative(file_path: str, project_root: Path) -> str | None:
    """Return the repo-relative path, or None if outside the repo."""
    try:
        return str(Path(file_path).resolve().relative_to(project_root.resolve()))
    except (ValueError, OSError):
        return None


def _research_roots(project_dir) -> tuple[str, ...]:
    """Return the research-artifact roots for this repo.

    Reads `<project_dir>/CLAUDE.md` and looks for a header line of the form
    `**Analysis roots:** dir1/, dir2/, ...` (case-insensitive label; optional
    surrounding `**`; comma- or space-separated; optional trailing slashes).
    Each parsed root is normalized to end with `/`.

    Falls back to DEFAULT_RESEARCH_ROOTS when:
      - CLAUDE.md is absent or unreadable,
      - the header is missing,
      - the value is only a bracketed placeholder (e.g. `[optional — ...]`,
        meaning "unset"),
      - or any parse error occurs (fail-open).
    """
    try:
        claude_md = Path(project_dir) / "CLAUDE.md"
        if not claude_md.is_file():
            return DEFAULT_RESEARCH_ROOTS
        for line in claude_md.read_text(encoding="utf-8", errors="ignore").splitlines():
            # Length cap: skip pathologically long lines before running the
            # regex. Real header lines are short; this bounds per-line regex
            # work on a maliciously large CLAUDE.md (DOS hardening).
            if len(line) > 200:
                continue
            m = _ANALYSIS_ROOTS_RE.match(line)
            if not m:
                continue
            value = m.group(1).strip()
            # Strip a trailing markdown-bold closer the greedy label match may
            # have left on the value (e.g. "**Analysis roots:**" → value "**").
            value = value.strip("*").strip()
            # A bracketed placeholder means "unset" — treat as default.
            if value.startswith("["):
                return DEFAULT_RESEARCH_ROOTS
            # Split on commas and/or whitespace.
            tokens = [t for t in re.split(r"[,\s]+", value) if t]
            # Validate each token is a sensible in-repo directory. Reject path
            # traversal (`..`) and absolute paths (leading `/`): such tokens
            # would otherwise be parsed as roots and used for startswith()
            # matching, bloating scope or causing confusion. Fail open to the
            # default rather than honoring a malformed/hostile declaration.
            for t in tokens:
                if ".." in t or t.startswith("/"):
                    return DEFAULT_RESEARCH_ROOTS
            roots = tuple(t.rstrip("/") + "/" for t in tokens)
            return roots if roots else DEFAULT_RESEARCH_ROOTS
        return DEFAULT_RESEARCH_ROOTS
    except Exception:
        return DEFAULT_RESEARCH_ROOTS


def _in_scope(rel_path: str, project_dir=None) -> bool:
    """True iff rel_path is under one of the research-artifact roots.

    Roots are resolved per-repo via _research_roots(project_dir); when
    project_dir is None they fall back to DEFAULT_RESEARCH_ROOTS.
    """
    roots = DEFAULT_RESEARCH_ROOTS if project_dir is None else _research_roots(project_dir)
    norm = rel_path.replace("\\", "/")
    return any(norm == r.rstrip("/") or norm.startswith(r) for r in roots)


def _git_head_baseline(rel_path: str, project_root: Path) -> str:
    """Return `git show HEAD:<rel_path>` content, or "" if not in HEAD.

    A non-zero git exit (e.g. 128: path not in HEAD, new file) yields an empty
    baseline so that a new file's entire content becomes residue. This is a
    deliberate path — NOT collapsed into generic fail-open.
    """
    try:
        result = subprocess.run(
            ["git", "show", f"HEAD:{rel_path}"],
            cwd=str(project_root),
            capture_output=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if result.returncode != 0:
        return ""
    try:
        return result.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return ""


def _file_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:12]


def _upsert_ledger_row(
    ledger_path: Path,
    rel_path: str,
    file_hash: str,
    result: str,
    evidence: str,
) -> None:
    """Insert or update the (rel_path, no-logic-change) row in the ledger.

    The ledger is a markdown table. We find an existing data row whose first
    column == rel_path AND second column == _CHECK_SLUG and replace it; else
    append a new row after the last table row. Wrapped by the caller in
    try/except for fail-open.
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    cells = [rel_path, _CHECK_SLUG, ts, file_hash, result, evidence]
    new_row = "| " + " | ".join(cells) + " |"

    lines = ledger_path.read_text(encoding="utf-8").splitlines()

    # Identify table data rows: start with "|", and we skip the header row and
    # the separator row (the |---|---| line).
    def _row_cells(line: str) -> list[str]:
        inner = line.strip()
        if inner.startswith("|"):
            inner = inner[1:]
        if inner.endswith("|"):
            inner = inner[:-1]
        return [c.strip() for c in inner.split("|")]

    last_table_idx = -1
    target_idx = -1
    for i, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        if set(line.strip()) <= set("|-: "):  # separator row
            last_table_idx = i
            continue
        last_table_idx = i
        rc = _row_cells(line)
        if len(rc) >= 2 and rc[0] == rel_path and rc[1] == _CHECK_SLUG:
            target_idx = i

    if target_idx >= 0:
        lines[target_idx] = new_row
    elif last_table_idx >= 0:
        lines.insert(last_table_idx + 1, new_row)
    else:
        # No table found — append at end (degenerate; preserves fail-open).
        lines.append(new_row)

    ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "")
    if tool_name not in {"Edit", "Write", "MultiEdit"}:
        sys.exit(0)

    tool_input = hook_input.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "") or ""
    if not file_path:
        sys.exit(0)

    derive_lib = _load_lib("derive_lib")
    language = derive_lib.language_for_path(file_path)
    if language is None:
        sys.exit(0)

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", hook_input.get("cwd", ""))
    if not project_dir:
        sys.exit(0)
    project_root = Path(project_dir)

    rel_path = _repo_relative(file_path, project_root)
    if rel_path is None or not _in_scope(rel_path, project_dir):
        sys.exit(0)

    normdiff_lib = _load_lib("normdiff_lib")

    # CURRENT = file from disk (PostToolUse: edit already landed). Fail-open
    # decode policy lives in read_text_or_empty.
    current = normdiff_lib.read_text_or_empty(file_path)

    # BASELINE = git HEAD content; empty if new / not-in-HEAD.
    baseline = _git_head_baseline(rel_path, project_root)

    try:
        diff = normdiff_lib.normdiff(baseline, current, language)
    except Exception:
        sys.exit(0)

    if normdiff_lib.residue_is_empty(diff):
        result = "PASS"
    else:
        result = "UNVERIFIED"
    evidence = normdiff_lib.summarize_residue(diff)
    file_hash = _file_hash(current)

    # Wrap the whole ledger read/write in try/except; fail-open on any IO error.
    try:
        ledger_path = project_root / _LEDGER_REL
        if ledger_path.is_file():
            _upsert_ledger_row(ledger_path, rel_path, file_hash, result, evidence)
    except Exception:
        sys.exit(0)

    # Non-blocking always: emit nothing user-facing.
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
