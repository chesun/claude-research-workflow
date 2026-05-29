#!/usr/bin/env python3
"""
Diagnostic-Claim audit Stop hook (BLOCKING, block-once).

Enforces the diagnostic slice of `.claude/rules/adversarial-default.md`: a
causal claim about a bug/error ("X is caused by line B in file C") is a
positive claim and needs positive evidence. At turn-end this hook scans the
CURRENT turn's assistant prose for bug/error causation claims; if one was made
but the turn shows no investigation (Read/Grep/Glob/Bash) AND the session
never consulted the verification ledger, it blocks the stop once with a
remediation pointing at both paths: investigate, or read the recorded
`diagnosis:` finding in the ledger (which may already hold the answer).

Mirrors primary-source-audit.py (claim-in-prose → require evidence → block-once).
Honest limit: it gates the PROCEDURE (did you investigate / consult), not the
truth of the claim, and matches evidence at turn granularity. It catches the
dominant failure (a diagnosis with zero investigation and no prior-record
consult), not every wrong diagnosis.

Escape hatch: `<!-- diagnosis-ok: <reason> -->` in the turn's prose.

Stop-loop safety: respects `stop_hook_active`. Fail-open on exception.

Install (in .claude/settings.json, Stop block):
    python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/diagnostic-claim-audit.py
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

_ESCAPE_RE = re.compile(r"diagnosis-ok", re.IGNORECASE)


def _load_lib():
    p = Path(__file__).resolve().parent / "stop_hooks_lib.py"
    spec = importlib.util.spec_from_file_location("stop_hooks_lib", p)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {p}")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _build_reason(claims: list[str]) -> str:
    preview = "\n".join(f"  • {c}" for c in claims[:3])
    return (
        "DIAGNOSTIC CLAIM NOT VERIFIED.\n\n"
        "This turn asserted a bug/error cause without investigating it here and "
        "without consulting the verification ledger:\n\n"
        f"{preview}\n\n"
        "Per .claude/rules/adversarial-default.md, a diagnosis is a positive "
        "claim that needs positive evidence. Before this claim ships, do ONE of:\n"
        "  1. Investigate now — read the file, run a repro, or grep — then record "
        "a `diagnosis:<slug>` row in .claude/state/verification-ledger.md.\n"
        "  2. Consult the ledger — `grep diagnosis .claude/state/verification-ledger.md` "
        "— the exact issue may already be investigated and recorded; cite that row "
        "instead of re-guessing.\n\n"
        "If you are restating an already-recorded finding or a cause confirmed "
        "outside this repo, add `<!-- diagnosis-ok: <reason> -->` to your message."
    )


def main() -> None:
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    if hook_input.get("stop_hook_active"):
        sys.exit(0)

    transcript_path_str = hook_input.get("transcript_path", "") or ""
    if not transcript_path_str:
        sys.exit(0)
    transcript_path = Path(transcript_path_str)
    if not transcript_path.is_file():
        sys.exit(0)

    lib = _load_lib()

    prose = lib.current_turn_assistant_text(transcript_path)
    if not prose.strip():
        sys.exit(0)

    # Escape hatch anywhere in this turn's prose suppresses the audit.
    if _ESCAPE_RE.search(prose):
        sys.exit(0)

    claims = lib.detect_bug_causation_claims(prose)
    if not claims:
        sys.exit(0)

    # Evidence: investigation this turn, OR ledger consulted this session.
    if lib.investigation_this_turn(transcript_path):
        sys.exit(0)
    if lib.ledger_consulted_this_session(transcript_path):
        sys.exit(0)

    json.dump({"decision": "block", "reason": _build_reason(claims)}, sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
