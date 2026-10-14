#!/usr/bin/env python3
"""Block accidental edits to protected files (PreToolUse Edit|Write|MultiEdit).

Cross-platform; replaces protect-files.sh (no `jq`). Exit 2 = block the edit;
exit 0 = allow. Fail-open on unparseable input, matching the shell original:
if the target file can't be identified, don't block legitimate edits.

Customize PROTECTED (basename match) for the files this repo wants guarded.
"""
from __future__ import annotations

import json
import os
import sys

PROTECTED = {"settings.json"}  # basename match


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0  # can't identify the target → allow (fail open)
    if data.get("tool_name") not in ("Edit", "Write", "MultiEdit"):
        return 0
    path = (data.get("tool_input") or {}).get("file_path") or ""
    if not path:
        return 0
    base = os.path.basename(path)
    if base in PROTECTED:
        print(f"Protected file: {base}. Edit it via a script, or remove it "
              "from PROTECTED in .claude/hooks/protect-files.py.",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
