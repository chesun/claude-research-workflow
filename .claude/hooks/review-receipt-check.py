#!/usr/bin/env python3
"""Independent-review receipt gate — PreToolUse (matcher: Bash).

Fires when Claude Code is about to run `git commit`. Blocks the commit when a
staged CODE artefact lacks an independent-review receipt; for staged DOC
artefacts it prints a non-blocking advisory. See .claude/rules/independent-review.md
and decisions/0002_mandatory-independent-review.md.

Opt-in: does nothing unless `git config review.required` is `true`.
Waiver: prefix the commit with `REVIEW_WAIVE=1` (visible in the command, so
auditable in shell history) to skip the code block for one commit. Note that
`--no-verify` does NOT bypass a PreToolUse hook, so this env prefix is the
deliberate escape.

FAILS OPEN. A PreToolUse hook that failed closed on an internal error would
block every commit in the session with no --no-verify escape — a lockout. So
any git error / parse error / unexpected exception exits 0 (the gate silently
disables until noticed). Exit 2 happens ONLY for the deliberate policy result:
a staged code path with no receipt.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

_EXT = r"\.(?:py|pyw|ps1|psm1|sh)$"
GATED_CODE = [re.compile(p, re.I) for p in (
    r"^\.claude/hooks/(?:[^/]+/)*[^/]+" + _EXT,   # allow nested (tests/, lib/)
    r"^bin/(?:[^/]+/)*[^/]+" + _EXT,
    r"^bin/(?:[^/]+/)*[^/.]+$",   # extensionless bin/ scripts (e.g. bin/mytool)
    r"^\.githooks/[^/]+$",
)]
ADVISE_DOC = [re.compile(p, re.I) for p in (
    r"^\.claude/rules/[^/]+\.md$",
    r"^\.claude/agents/[^/]+\.md$",
    r"^\.claude/skills/.+",
    r"^\.claude/references/[^/]+\.md$",
    r"^decisions/\d{4}_[^/]+\.md$",
    r"^quality_reports/plans/(?!INDEX\.md$)[^/]+\.md$",
    r"^templates/.+",
)]
REVIEW_DIR = "quality_reports/reviews/"
GENERIC_BASENAMES = {"skill.md", "readme.md", "index.md", "__init__.py"}
HEADER_LINES = 40

_TARGET = re.compile(r"^\*\*Target:\*\*[ \t]*(.+)$", re.M)
_SCORE = re.compile(r"^\*\*Score:\*\*[ \t]*\d{1,3}[ \t]*/[ \t]*100", re.M)
_STATUS = re.compile(r"^\*\*Status:\*\*[ \t]*(Active|Completed)\b", re.M | re.I)
_DATE = re.compile(r"^\*\*Date:\*\*[ \t]*(\d{4}-\d{2}-\d{2})", re.M)


def git_soft(*args: str) -> str:
    """git that returns '' on any failure — the fail-open substrate."""
    try:
        p = subprocess.run(("git",) + args, capture_output=True)
        return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else ""
    except Exception:
        return ""


def git_soft_bytes(*args: str) -> bytes:
    try:
        p = subprocess.run(("git",) + args, capture_output=True)
        return p.stdout if p.returncode == 0 else b""
    except Exception:
        return b""


class GitError(Exception):
    """A git call that the gate depends on failed — evaluation is unreliable."""


def git_checked_bytes(*args: str) -> bytes:
    """git that RAISES GitError on failure. Used on the calls the block
    decision depends on, so a git failure fails CLOSED (via main's handler)
    rather than silently returning empty and letting a gated commit through.
    """
    try:
        p = subprocess.run(("git",) + args, capture_output=True)
    except Exception as exc:
        raise GitError(f"git {' '.join(args[:3])}: {exc}") from exc
    if p.returncode != 0:
        raise GitError(f"git {' '.join(args[:3])} exit {p.returncode}: "
                       + p.stderr.decode('utf-8', 'replace').strip())
    return p.stdout


def git_checked(*args: str) -> str:
    return git_checked_bytes(*args).decode("utf-8", "replace")


# --- command parsing ---------------------------------------------------------

_ENV = re.compile(r"^\w+=")
_PREFIX = {"sudo", "command", "nice", "nohup", "time", "env"}
_GIT_GLOBAL_ARG = {"-c", "-C", "--git-dir", "--work-tree", "--namespace"}


_WAIVE_TOKEN = re.compile(r"^REVIEW_WAIVE=(?:1|true|yes)$", re.I)


def _is_git(tok: str) -> bool:
    return tok in ("git", "git.exe") or tok.endswith(("/git", "/git.exe"))


def parse_commit(command: str) -> "tuple[bool, bool]":
    """Return (is_git_commit, waived) for a Bash command string.

    The waiver is honoured ONLY as a leading environment-assignment token of
    the same segment that runs the commit (`REVIEW_WAIVE=1 git commit ...`),
    never as a free-text match — otherwise a commit message that merely
    mentions REVIEW_WAIVE would silently waive the gate.
    """
    is_commit = False
    waived = False
    # Split on &&, ||, single | (pipelines), ; and newlines; then strip any
    # leading subshell/brace/paren so `(git commit)`, `{ git commit; }` and
    # `ls | git commit` are still detected rather than silently missed.
    for seg in re.split(r"&&|[|;\n]", command):
        seg = seg.lstrip("({ \t")
        try:
            toks = shlex.split(seg, posix=True)
        except Exception:
            toks = seg.split()
        i = 0
        seg_waive = False
        while i < len(toks) and (_ENV.match(toks[i]) or toks[i] in _PREFIX):
            if _WAIVE_TOKEN.match(toks[i]):
                seg_waive = True
            i += 1
        if i >= len(toks) or not _is_git(toks[i]):
            continue
        j = i + 1
        while j < len(toks) and toks[j].startswith("-"):
            j += 2 if toks[j] in _GIT_GLOBAL_ARG else 1
        if j < len(toks) and toks[j] == "commit":
            is_commit = True
            if seg_waive:
                waived = True
    return is_commit, waived


# --- staged changes + classification ----------------------------------------

def staged_changes() -> "list[tuple[str, str, str | None]]":
    raw = git_checked_bytes("-c", "core.quotePath=false", "diff", "--cached",
                            "--name-status", "-z", "-M",
                            "--diff-filter=ACMRD").decode("utf-8", "replace")
    parts = raw.split("\x00")
    out: list[tuple[str, str, str | None]] = []
    i = 0
    while i < len(parts) and parts[i]:
        status = parts[i]
        if status[:1] in ("R", "C"):
            out.append((status[0], parts[i + 2], parts[i + 1]))
            i += 3
        else:
            out.append((status[0], parts[i + 1], None))
            i += 2
    return out


def classify(path: str) -> "str | None":
    if any(g.match(path) for g in GATED_CODE):
        return "code"
    if any(g.match(path) for g in ADVISE_DOC):
        return "doc"
    return None


# --- receipts ----------------------------------------------------------------

def indexed_reviews() -> "list[tuple[str, str]]":
    raw = git_checked_bytes("-c", "core.quotePath=false", "ls-files", "--cached",
                            "-z", REVIEW_DIR).decode("utf-8", "replace")
    paths = [p for p in raw.split("\x00")
             if p and p.lower().endswith(".md")
             and os.path.basename(p).lower() not in GENERIC_BASENAMES]
    out = []
    for p in paths:
        body = git_checked("cat-file", "-p", f":{p}")
        if body:
            out.append((p, "\n".join(body.splitlines()[:HEADER_LINES])))
    return out


def basename_counts() -> "dict[str, int]":
    raw = git_checked_bytes("-c", "core.quotePath=false", "ls-files", "--cached",
                            "-z").decode("utf-8", "replace")
    counts: dict[str, int] = {}
    for p in raw.split("\x00"):
        if p:
            b = os.path.basename(p).lower()
            counts[b] = counts.get(b, 0) + 1
    return counts


def target_matches(path: str, target_line: str, counts: "dict[str, int]") -> bool:
    t = target_line.replace("\\", "/")
    t = re.sub(r"(?<![\w/])\./", "", t)
    if re.search(r"(?<![\w./-])" + re.escape(path) + r"(?![\w/-])", t, re.I):
        return True
    base = os.path.basename(path)
    if base.lower() not in GENERIC_BASENAMES and counts.get(base.lower(), 0) <= 1:
        if re.search(r"(?<![\w./-])" + re.escape(base) + r"(?![\w-])", t, re.I):
            return True
    m = re.match(r"^decisions/(\d{4})_", path)
    if m and re.search(r"(?:ADR-|#)" + m.group(1) + r"(?!\d)", t, re.I):
        return True
    return False


def last_commit_date(*paths: str) -> "_dt.date | None":
    latest = None
    for p in paths:
        if not p:
            continue
        # Tolerant on purpose: `git log` exits non-zero on an empty repo
        # ("no commits yet") and that legitimately means "no prior commit for
        # this path" → None → freshness is vacuously satisfied. A failure here
        # only weakens freshness (a secondary check), never receipt existence,
        # so it must NOT fail closed and block a legitimate first commit.
        s = git_soft("log", "-1", "--format=%cs", "--", p).strip()
        try:
            d = _dt.date.fromisoformat(s) if s else None
        except ValueError:
            d = None
        if d and (latest is None or d > latest):
            latest = d
    return latest


def has_receipt(path: str, old_path: "str | None",
                reviews: "list[tuple[str, str]]", counts: "dict[str, int]",
                today: _dt.date) -> bool:
    since = last_commit_date(path, old_path or "")
    for _rpath, header in reviews:
        tm = _TARGET.search(header)
        if not tm or not _SCORE.search(header) or not _STATUS.search(header):
            continue
        if not target_matches(path, tm.group(1), counts):
            continue
        dm = _DATE.search(header)
        if not dm:
            continue
        try:
            rdate = _dt.date.fromisoformat(dm.group(1))
        except ValueError:
            continue
        if rdate > today:
            continue
        if since is not None and rdate < since:
            continue
        return True
    return False


def _log_failure(reason: str, command: str) -> None:
    """Durable, greppable record of a gate error so it is auditable even if
    the stderr banner scrolls away."""
    try:
        root = git_soft("rev-parse", "--show-toplevel").strip() or "."
        d = Path(root) / ".claude" / "state"
        d.mkdir(parents=True, exist_ok=True)
        rec = {
            "ts": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "reason": reason, "command": command[:200],
        }
        with (d / "review-gate-failures.log").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
    except Exception:
        pass


def _fail_closed(reason: str, command: str) -> int:
    """A gated commit whose receipt could not be evaluated. Block LOUDLY and
    tell the user the escape — the waiver is parsed before any fallible call,
    so this is never a lockout, only a demand to look."""
    _log_failure(reason, command)
    print("\n" + "=" * 64, file=sys.stderr)
    print("review-receipt: GATE ERROR — COMMIT BLOCKED (fail-closed)",
          file=sys.stderr)
    print(f"  The gate could not evaluate this commit: {reason}",
          file=sys.stderr)
    print("  Fix the guard (see .claude/state/review-gate-failures.log), or "
          "proceed deliberately with: REVIEW_WAIVE=1 git commit ...",
          file=sys.stderr)
    print("=" * 64 + "\n", file=sys.stderr)
    return 2


def main() -> int:
    # Reading the event and parsing the command are string-only and cannot
    # fail on a gate-relevant path. If they do, this is NOT a gated commit we
    # can identify, and this hook runs on EVERY Bash call — so allow, to avoid
    # bricking all shell use. Fail-closed is scoped strictly to a confirmed
    # gated commit (below), never to unrelated Bash.
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") != "Bash":
        return 0
    command = (data.get("tool_input") or {}).get("command") or ""
    is_commit, waived = parse_commit(command)
    if not is_commit:
        return 0
    # Waiver is honoured BEFORE any git call, so a broken guard is always
    # escapable — this is what makes fail-closed safe (no lockout).
    if waived:
        print("review-receipt: code review WAIVED via REVIEW_WAIVE.",
              file=sys.stderr)
        return 0
    # `--bool` normalises truthy forms (1/yes/on/true) so `review.required=1`
    # opts in too; unset returns non-zero → "" → not gated.
    if git_soft("config", "--bool", "review.required").strip().lower() != "true":
        return 0

    # From here we KNOW it is a gated, opt-in, non-waived commit. Any failure
    # to evaluate it fails CLOSED (block + escape), never silently open.
    try:
        code, docs = [], []
        for _status, path, old in staged_changes():
            kind = classify(path)
            if kind == "code":
                code.append((path, old))
            elif kind == "doc":
                docs.append((path, old))
        if not code and not docs:
            return 0

        reviews = indexed_reviews()
        counts = basename_counts()
        today = _dt.date.today()
        code_missing = [p for p, old in code
                        if not has_receipt(p, old, reviews, counts, today)]
        doc_missing = [p for p, old in docs
                       if not has_receipt(p, old, reviews, counts, today)]
    except GitError as exc:
        return _fail_closed(str(exc), command)
    except Exception as exc:
        return _fail_closed(f"unexpected: {exc}", command)

    if doc_missing:
        print("review-receipt: ADVISORY — no independent-review receipt for "
              "these doc changes (not blocking): "
              + ", ".join(doc_missing), file=sys.stderr)
    if code_missing:
        print("\nreview-receipt: COMMIT BLOCKED — no independent-review "
              "receipt for staged code:", file=sys.stderr)
        for p in code_missing:
            print(f"  {p}", file=sys.stderr)
        print("\n  A review under quality_reports/reviews/ must name the path "
              "in its **Target:** header, carry **Score:** NN/100 and "
              "**Status:** Active|Completed, and be dated no earlier than the "
              "path's last commit. Stage it, then commit.", file=sys.stderr)
        print("  Run /review-build <path>, or waive once with a visible "
              "prefix: REVIEW_WAIVE=1 git commit ...", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:
        # Backstop for an error BEFORE the commit was confirmed gated (this
        # hook runs on every Bash call). Allow, to avoid bricking all shell
        # use, but log so it is not silent. The scoped fail-closed above is
        # what guards a confirmed gated commit.
        print(f"review-receipt: pre-check error, allowing this Bash call: "
              f"{exc}", file=sys.stderr)
        _log_failure(f"pre-check error: {exc}", "")
        sys.exit(0)
