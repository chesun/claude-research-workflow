#!/usr/bin/env python3
"""
Integration tests for diagnostic-claim-audit.py (Stop hook, block-once).

Invokes the hook as a subprocess with synthetic transcripts.

Run:  python3 -m pytest .claude/hooks/test_diagnostic_claim_audit.py -q
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parent / "diagnostic-claim-audit.py"


def _transcript(tmp_path: Path, events: list[dict]) -> Path:
    p = tmp_path / "t.jsonl"
    p.write_text("\n".join(json.dumps(e) for e in events))
    return p


def _assistant(blocks: list[dict]) -> dict:
    return {"type": "assistant", "message": {"role": "assistant", "content": blocks}}


def _user(text: str) -> dict:
    return {"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": text}]}}


def _text(t: str) -> dict:
    return {"type": "text", "text": t}


def _tool(name: str, **inp) -> dict:
    return {"type": "tool_use", "name": name, "input": inp}


def _run(transcript: Path, stop_active: bool = False) -> tuple[int, str]:
    payload = {"transcript_path": str(transcript), "stop_hook_active": stop_active}
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
    )
    return proc.returncode, proc.stdout


def test_blocks_unverified_diagnosis(tmp_path):
    t = _transcript(tmp_path, [
        _user("why does it crash?"),
        _assistant([_text("The crash is caused by the off-by-one at utils.py:42.")]),
    ])
    code, out = _run(t)
    assert code == 0
    assert json.loads(out)["decision"] == "block"


def test_allows_when_investigated_this_turn(tmp_path):
    t = _transcript(tmp_path, [
        _user("why does it crash?"),
        _assistant([_tool("Read", file_path="utils.py")]),
        _assistant([_text("The crash is caused by the off-by-one at utils.py:42.")]),
    ])
    code, out = _run(t)
    assert code == 0
    assert out.strip() == ""


def test_allows_when_ledger_consulted(tmp_path):
    t = _transcript(tmp_path, [
        _user("why does it crash?"),
        _assistant([_tool("Bash", command="grep diagnosis .claude/state/verification-ledger.md")]),
        _assistant([_text("Per the ledger, the failure is caused by the cluster level.")]),
    ])
    code, out = _run(t)
    assert code == 0
    assert out.strip() == ""


def test_allows_benign_causal_prose(tmp_path):
    t = _transcript(tmp_path, [
        _user("why cluster there?"),
        _assistant([_text("We cluster at classroom level because of the assignment mechanism.")]),
    ])
    code, out = _run(t)
    assert code == 0
    assert out.strip() == ""


def test_escape_hatch(tmp_path):
    t = _transcript(tmp_path, [
        _user("why does it crash?"),
        _assistant([_text(
            "The crash is caused by the off-by-one at utils.py:42. "
            "<!-- diagnosis-ok: confirmed in issue #123 -->"
        )]),
    ])
    code, out = _run(t)
    assert code == 0
    assert out.strip() == ""


def test_loop_guard(tmp_path):
    t = _transcript(tmp_path, [
        _user("why does it crash?"),
        _assistant([_text("The crash is caused by the off-by-one at utils.py:42.")]),
    ])
    code, out = _run(t, stop_active=True)
    assert code == 0
    assert out.strip() == ""


def test_malformed_json_fail_open(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input="not json{",
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
    )
    assert proc.returncode == 0
    assert proc.stdout.strip() == ""


if __name__ == "__main__":
    # These tests use the pytest `tmp_path` fixture and CANNOT run under a bare
    # `python3 test_diagnostic_claim_audit.py` — doing so would exit 0 with no
    # assertions run, which falsely reads as a green suite. Fail loudly instead.
    raise SystemExit(
        "This is a pytest suite (uses the tmp_path fixture). Run it with:\n"
        "    python3 -m pytest .claude/hooks/test_diagnostic_claim_audit.py -q\n"
        "A bare `python3` invocation runs zero assertions and must not be "
        "mistaken for a passing suite."
    )
