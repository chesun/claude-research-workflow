#!/usr/bin/env python3
"""
Integration tests for derive-check-block.py (opt-in blocking hook).

Invokes the hook as a subprocess with synthetic stdin against a temp project,
exercising the opt-in flag gate, block decision, escape hatch, and audit log.

Run:  python3 -m pytest .claude/hooks/test_derive_check_block.py -q
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parent / "derive-check-block.py"


def _run(payload: dict, project_root: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={"CLAUDE_PROJECT_DIR": str(project_root), "PATH": "/usr/bin:/bin"},
    )
    return proc.returncode, proc.stdout


def _enable(project_root: Path) -> None:
    state = project_root / ".claude" / "state"
    state.mkdir(parents=True, exist_ok=True)
    (state / "derive-guess-block.enabled").touch()


def _payload(project_root: Path, content: str) -> dict:
    return {
        "tool_name": "Write",
        "tool_input": {
            "file_path": str(project_root / "01.do"),
            "content": content,
        },
    }


def test_inert_when_flag_absent(tmp_path):
    # No flag → no-op even with a fabricated path.
    code, out = _run(_payload(tmp_path, 'use "data/ghost.dta", clear\n'), tmp_path)
    assert code == 0
    assert out.strip() == ""


def test_blocks_when_enabled(tmp_path):
    _enable(tmp_path)
    code, out = _run(_payload(tmp_path, 'use "data/ghost.dta", clear\n'), tmp_path)
    assert code == 0
    decision = json.loads(out)
    assert decision["decision"] == "block"
    assert "data/ghost.dta" in decision["reason"]


def test_allows_existing_path_when_enabled(tmp_path):
    _enable(tmp_path)
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "real.dta").write_text("")
    code, out = _run(_payload(tmp_path, 'use "data/real.dta", clear\n'), tmp_path)
    assert code == 0
    assert out.strip() == ""


def test_escape_hatch_when_enabled(tmp_path):
    _enable(tmp_path)
    code, out = _run(
        _payload(tmp_path, '<!-- derive-ok -->\nuse "data/ghost.dta", clear\n'),
        tmp_path,
    )
    assert code == 0
    assert out.strip() == ""


def test_audit_log_written_on_block(tmp_path):
    _enable(tmp_path)
    _run(_payload(tmp_path, 'use "data/ghost.dta", clear\n'), tmp_path)
    log = tmp_path / ".claude" / "state" / "derive-guard.log"
    assert log.exists()
    entry = json.loads(log.read_text().strip().splitlines()[-1])
    assert entry["decision"] == "BLOCK"
    assert "data/ghost.dta" in entry["paths"]


def test_malformed_json_fail_open(tmp_path):
    _enable(tmp_path)
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input="not json{",
        capture_output=True,
        text=True,
        env={"CLAUDE_PROJECT_DIR": str(tmp_path), "PATH": "/usr/bin:/bin"},
    )
    assert proc.returncode == 0
    assert proc.stdout.strip() == ""
