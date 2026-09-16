#!/usr/bin/env python3
"""Desktop notification hook — cross-platform (macOS / Windows / Linux).

Fires on Notification events (permission prompts, idle prompts, auth events).
Replaces notify.sh: no `jq`, no macOS-only `osascript`; the OS is detected at
runtime. FAIL-OPEN by contract — any error exits 0. A notification must never
break a turn.
"""
from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys


def _read() -> "tuple[str, str]":
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    title = str(data.get("title") or "Claude Code")
    message = str(data.get("message") or "Claude needs attention")
    return title, message


def _notify(title: str, message: str) -> None:
    system = platform.system()
    if system == "Darwin":
        t = title.replace('"', '\\"')
        m = message.replace('"', '\\"')
        subprocess.run(
            ["osascript", "-e",
             f'display notification "{m}" with title "{t}"'],
            capture_output=True, timeout=5)
    elif system == "Windows":
        # Prefer a real toast via BurntToast if installed; otherwise fall back
        # to a console line so the message is never lost.
        t = title.replace("'", "''")
        m = message.replace("'", "''")
        ps = (
            "if (Get-Module -ListAvailable -Name BurntToast) { "
            "Import-Module BurntToast; "
            f"New-BurntToastNotification -Text '{t}','{m}' }} else {{ exit 3 }}"
        )
        r = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            capture_output=True, timeout=8)
        if r.returncode != 0:
            print(f"[{title}] {message}", file=sys.stderr)
    elif system == "Linux" and shutil.which("notify-send"):
        subprocess.run(["notify-send", title, message],
                       capture_output=True, timeout=5)
    else:
        print(f"[{title}] {message}", file=sys.stderr)


def main() -> int:
    try:
        _notify(*_read())
    except Exception:
        pass  # fail open — never break a turn over a notification
    return 0


if __name__ == "__main__":
    sys.exit(main())
