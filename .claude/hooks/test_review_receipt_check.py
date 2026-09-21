#!/usr/bin/env python3
"""Regression tests for review-receipt-check.py.

Pure-function tests import the module; end-to-end tests build throwaway git
repos and run the deployed hook as a subprocess with a fake PreToolUse event
on stdin. Run:  python .claude/hooks/test_review_receipt_check.py
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOOK = HERE / "review-receipt-check.py"

spec = importlib.util.spec_from_file_location("rrc", HOOK)
rrc = importlib.util.module_from_spec(spec)
sys.modules["rrc"] = rrc
spec.loader.exec_module(rrc)

P, F = 0, 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global P, F
    if ok:
        P += 1
        print(f"ok   {name}")
    else:
        F += 1
        print(f"FAIL {name}")
        if detail:
            print(f"       {detail}")


def sh(*args, cwd, stdin="", env=None):
    return subprocess.run(args, cwd=str(cwd), input=stdin, env=env,
                          capture_output=True, text=True)


def run_hook(cwd, command):
    ev = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    return subprocess.run([sys.executable, str(HOOK)], cwd=str(cwd),
                          input=ev, capture_output=True, text=True)


def make_repo(tmp, name):
    r = tmp / name
    r.mkdir()
    sh("git", "init", "-q", "-b", "main", cwd=r)
    sh("git", "config", "user.name", "T", cwd=r)
    sh("git", "config", "user.email", "t@example.com", cwd=r)
    sh("git", "config", "commit.gpgsign", "false", cwd=r)
    sh("git", "config", "core.hooksPath", "/dev/null", cwd=r)  # no real hooks
    return r


def add(r, rel, text):
    p = r / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    sh("git", "add", rel, cwd=r)


REVIEW_HDR = ("# X Review\n**Date:** {date}\n**Reviewer:** rc\n"
             "**Target:** {target}\n**Score:** 92/100\n**Status:** Active\n")


def main() -> int:
    # --- pure: parse_commit ---
    cases = [
        ("git commit -m x", True, False),
        ("git commit -F - <<'EOF'", True, False),
        ('cd "some/dir" && git commit -m y', True, False),
        ("git -c user.email=a@b commit -m z", True, False),
        ("git commit --amend --no-edit", True, False),
        ("REVIEW_WAIVE=1 git commit -m w", True, True),
        ('git commit -m "document REVIEW_WAIVE=1 escape"', True, False),
        ("git.exe commit -m x", True, False),
        ("ls | git commit -m x", True, False),
        ("(git commit -m x)", True, False),
        ("{ git commit -m x; }", True, False),
        ("git status", False, False),
        ("git log --grep commit", False, False),
        ("echo commit && ls", False, False),
    ]
    for cmd, exp_c, exp_w in cases:
        c, w = rrc.parse_commit(cmd)
        check(f"parse_commit({cmd[:34]!r})", c == exp_c and w == exp_w,
              f"got commit={c} waived={w}")

    # --- pure: classify ---
    cls = [
        (".claude/hooks/foo.py", "code"),
        (".claude/hooks/tests/test_foo.py", "code"),
        (".claude/hooks/lib/helper.py", "code"),
        ("bin/sub/tool.sh", "code"),
        ("bin/mytool", "code"),
        (".githooks/pre-commit", "code"),
        (".claude/rules/x.md", "doc"),
        (".claude/agents/coder.md", "doc"),
        (".claude/skills/tools/SKILL.md", "doc"),
        ("decisions/0002_x.md", "doc"),
        ("quality_reports/plans/2026-09-21_x.md", "doc"),
        ("quality_reports/plans/INDEX.md", None),
        ("README.md", None),
        ("paper/main.tex", None),
    ]
    for path, exp in cls:
        check(f"classify({path})", rrc.classify(path) == exp,
              f"got {rrc.classify(path)}")

    # --- fail-closed behaviour (in-process, monkeypatched) ---
    # git_checked raises GitError on a failing git call (the fail-closed substrate)
    try:
        rrc.git_checked("rev-parse", "--verify",
                        "refs/heads/definitely-no-such-branch-xyz")
        check("git_checked raises on a failing git call", False, "no raise")
    except rrc.GitError:
        check("git_checked raises GitError on a failing git call", True)
    except Exception as e:
        check("git_checked raises GitError on a failing git call", False, repr(e))

    def run_main_inproc(command, *, staged, config_true=True):
        old = (sys.stdin, rrc.staged_changes, rrc.git_soft, rrc._log_failure)
        try:
            sys.stdin = io.StringIO(json.dumps(
                {"tool_name": "Bash", "tool_input": {"command": command}}))
            rrc.staged_changes = staged
            rrc.git_soft = (lambda *a: "true"
                            if "review.required" in a and config_true
                            else "")
            rrc._log_failure = lambda *a, **k: None  # no repo side effects
            return rrc.main()
        finally:
            (sys.stdin, rrc.staged_changes, rrc.git_soft,
             rrc._log_failure) = old

    def boom():
        raise rrc.GitError("simulated git failure")

    rc = run_main_inproc("git commit -m x", staged=boom)
    check("gated commit + git error → FAIL CLOSED (exit 2)", rc == 2,
          f"got {rc}")

    rc = run_main_inproc("REVIEW_WAIVE=1 git commit -m x", staged=boom)
    check("waiver short-circuits BEFORE the failing git call → exit 0",
          rc == 0, f"got {rc}")

    rc = run_main_inproc("git commit -m x", staged=boom, config_true=False)
    check("review.required not set → not gated, no fail-closed (exit 0)",
          rc == 0, f"got {rc}")

    tmp = Path(tempfile.mkdtemp(prefix="rrc-tests-"))
    try:
        today = __import__("datetime").date.today().isoformat()

        # opt-in off → allow even with unreviewed code
        r = make_repo(tmp, "optout")
        add(r, ".claude/hooks/new.py", "print(1)\n")
        p = run_hook(r, "git commit -m x")
        check("opt-in off: unreviewed code commits (exit 0)",
              p.returncode == 0, p.stderr)

        # opt-in on, code, no receipt → block
        r = make_repo(tmp, "codeblock")
        sh("git", "config", "review.required", "true", cwd=r)
        add(r, ".claude/hooks/new.py", "print(1)\n")
        p = run_hook(r, "git commit -m x")
        check("code, no receipt → blocked (exit 2)",
              p.returncode == 2 and "BLOCKED" in p.stderr, p.stderr)

        # with a matching staged receipt → allow
        r = make_repo(tmp, "codeok")
        sh("git", "config", "review.required", "true", cwd=r)
        add(r, ".claude/hooks/new.py", "print(1)\n")
        add(r, "quality_reports/reviews/2026-09-21_new_code_review.md",
            REVIEW_HDR.format(date=today, target=".claude/hooks/new.py"))
        p = run_hook(r, "git commit -m x")
        check("code with staged receipt → allowed (exit 0)",
              p.returncode == 0, p.stderr)

        # doc only, no receipt → advisory, allow
        r = make_repo(tmp, "docadvise")
        sh("git", "config", "review.required", "true", cwd=r)
        add(r, ".claude/rules/new.md", "# rule\n")
        p = run_hook(r, "git commit -m x")
        check("doc, no receipt → advisory, not blocked (exit 0)",
              p.returncode == 0 and "ADVISORY" in p.stderr, p.stderr)

        # mixed: code unreviewed + doc → block on the code
        r = make_repo(tmp, "mixed")
        sh("git", "config", "review.required", "true", cwd=r)
        add(r, ".claude/hooks/new.py", "print(1)\n")
        add(r, ".claude/rules/new.md", "# rule\n")
        p = run_hook(r, "git commit -m x")
        check("mixed code+doc → blocked on code (exit 2)",
              p.returncode == 2, p.stderr)

        # waiver → allow despite unreviewed code
        r = make_repo(tmp, "waive")
        sh("git", "config", "review.required", "true", cwd=r)
        add(r, ".claude/hooks/new.py", "print(1)\n")
        p = run_hook(r, "REVIEW_WAIVE=1 git commit -m x")
        check("REVIEW_WAIVE=1 → allowed (exit 0)",
              p.returncode == 0 and "WAIVED" in p.stderr, p.stderr)

        # waiver honoured ONLY as a leading env token — in the message it does not waive
        r = make_repo(tmp, "waivemsg")
        sh("git", "config", "review.required", "true", cwd=r)
        add(r, ".claude/hooks/new.py", "print(1)\n")
        p = run_hook(r, 'git commit -m "note: REVIEW_WAIVE=1 is the escape"')
        check("REVIEW_WAIVE in the message body → NOT waived, blocked (exit 2)",
              p.returncode == 2, p.stderr)

        # a receipt missing a required header field (no Score) is not valid → block
        r = make_repo(tmp, "badreceipt")
        sh("git", "config", "review.required", "true", cwd=r)
        add(r, ".claude/hooks/new.py", "print(1)\n")
        add(r, "quality_reports/reviews/2026-09-21_new_code_review.md",
            "# X\n**Date:** " + today + "\n**Reviewer:** rc\n"
            "**Target:** .claude/hooks/new.py\n**Status:** Active\n")
        p = run_hook(r, "git commit -m x")
        check("receipt missing **Score** → rejected, blocked (exit 2)",
              p.returncode == 2, p.stderr)

        # stale receipt (dated before the code's last commit) → block
        r = make_repo(tmp, "stale")
        sh("git", "config", "review.required", "true", cwd=r)
        add(r, ".claude/hooks/new.py", "print(1)\n")
        sh("git", "commit", "-q", "-m", "base", cwd=r)  # code now has a commit today
        (r / ".claude/hooks/new.py").write_text("print(2)\n", encoding="utf-8")
        sh("git", "add", ".claude/hooks/new.py", cwd=r)
        add(r, "quality_reports/reviews/old_new_code_review.md",
            REVIEW_HDR.format(date="2020-01-01", target=".claude/hooks/new.py"))
        p = run_hook(r, "git commit -m x")
        check("stale receipt (older than last commit) → blocked (exit 2)",
              p.returncode == 2, p.stderr)

        # non-commit command → allow
        r = make_repo(tmp, "noncommit")
        sh("git", "config", "review.required", "true", cwd=r)
        add(r, ".claude/hooks/new.py", "print(1)\n")
        p = run_hook(r, "git status")
        check("non-commit command → allowed (exit 0)",
              p.returncode == 0, p.stderr)

        # review.required=1 (git --bool truthy, not literal "true") opts in
        r = make_repo(tmp, "boolopt")
        sh("git", "config", "review.required", "1", cwd=r)
        add(r, ".claude/hooks/new.py", "print(1)\n")
        p = run_hook(r, "git commit -m x")
        check("review.required=1 opts in → blocks unreviewed code (exit 2)",
              p.returncode == 2, p.stderr)

        # _log_failure actually writes the durable log (pins the Path import;
        # a NameError would be swallowed and the log silently never created)
        r = make_repo(tmp, "logtest")
        old_cwd = os.getcwd()
        try:
            os.chdir(r)
            rrc._log_failure("simulated reason", "git commit -m x")
        finally:
            os.chdir(old_cwd)
        logf = r / ".claude" / "state" / "review-gate-failures.log"
        check("_log_failure writes the audit log (Path imported)",
              logf.exists()
              and "simulated reason" in logf.read_text(encoding="utf-8"),
              "log not written")

        # fail-open: malformed stdin → allow
        p = subprocess.run([sys.executable, str(HOOK)], cwd=str(tmp),
                           input="not json", capture_output=True, text=True)
        check("malformed stdin → fail open (exit 0)", p.returncode == 0,
              p.stderr)

    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{P}/{P + F} passed")
    return 0 if F == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
