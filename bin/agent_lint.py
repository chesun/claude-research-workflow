#!/usr/bin/env python3
"""Lint the YAML frontmatter of agents and skills.

Claude Code parses `.claude/agents/*.md` and `.claude/skills/*/SKILL.md` frontmatter as
strict YAML and silently drops a file it cannot parse: no error, the agent or skill just
is not registered. A `: ` inside an unquoted description did this to two agents on
2026-10-11. This lint catches that class of fault without a YAML library:

- plain (unquoted) values containing `: ` or ending in `:` (YAML reads a nested mapping);
- plain values containing ` #` (YAML reads a comment and truncates the value);
- values starting with a YAML indicator character; unclosed quotes or flow lists;
- tabs in indentation, duplicate keys, lines that are not `key: value`;
- a missing or empty `description`; an agent `name` that differs from its file name
  (a skill `name`, when present, must match its directory); `model` other than an alias.

Usage: python3 bin/agent_lint.py [repo root]   (exit 0 clean, 1 problems, 2 usage)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

KEY_RE = re.compile(r"^([A-Za-z0-9_][A-Za-z0-9_-]*)[ ]*:(?:[ \t](.*))?$")
MODEL_ALIASES = {"fable", "opus", "sonnet", "haiku", "inherit"}
PLAIN_BAD_START = set(",[]{}#&*!|>'\"%@`")
NULLS = {"", "~", "null", "Null", "NULL"}
COMMENT_TAIL_RE = re.compile(r"[ \t]#.*$")


def _plain_problem(value: str) -> str | None:
    if re.search(r":[ \t]", value) or value.rstrip().endswith(":"):
        return ("contains ': ' or ends in ':' (strict YAML rejects it: mapping values are not allowed here); "
                "quote the value or use a block scalar (|)")
    if re.search(r"[ \t]#", value):
        return ("contains ' #' (YAML treats the rest as a comment and drops it from the value); "
                "quote the value, or put the comment on its own line")
    return None


def _quoted_rest(value: str) -> str | None:
    """Text after the closing quote of a quoted scalar, or None if the quote never closes."""
    q, i = value[0], 1
    while i < len(value):
        c = value[i]
        if q == '"' and c == "\\":
            i += 2
            continue
        if c == q:
            if q == "'" and value[i + 1:i + 2] == "'":
                i += 2
                continue
            return value[i + 1:]
        i += 1
    return None


def _value_problem(value: str) -> tuple[str | None, str]:
    """(problem, mode) for a top-level value; mode is how indented lines after it are read."""
    v = value.strip()
    if not v:
        return None, "nested"
    if v[0] in "|>":
        return None, "block"
    if v[0] in "\"'":
        rest = _quoted_rest(v)
        if rest is None:
            return ("this lint requires a quoted value to close on one line (it does not follow "
                    "multi-line quoted scalars)"), "done"
        rest = rest.strip()
        if rest and not rest.startswith("#"):
            return f"text after the closing quote: {rest!r}", "done"
        return None, "done"
    if v[0] in "[{":
        close = "]" if v[0] == "[" else "}"
        body = COMMENT_TAIL_RE.sub("", v).rstrip()
        if not body.endswith(close):
            return (f"this lint requires a flow collection to close with {close!r} on one line"), "done"
        return None, "done"
    if v[0] in PLAIN_BAD_START or (v[0] in "-?:" and (len(v) == 1 or v[1] == " ")):
        return f"starts with the YAML indicator {v[0]!r}; quote the value", "plain"
    return _plain_problem(v), "plain"


def lint_frontmatter(text: str, kind: str, stem: str) -> list[str]:
    """Problems in one file's frontmatter. kind is 'agent' or 'skill'; stem is the
    file stem (agent) or directory name (skill) that `name` must match."""
    lines = text.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if not lines or lines[0].rstrip() != "---":
        return ["no frontmatter (the first line must be exactly '---', at column 0)"]
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].rstrip() == "---")
    except StopIteration:
        return ["unterminated frontmatter (no closing '---' at column 0)"]

    problems, values, indented = [], {}, {}
    key, mode = None, None
    for no, ln in enumerate(lines[1:end], 2):
        if not ln.strip():
            continue
        if ln[0] in " \t":
            if ln.lstrip(" ").startswith("\t") or ln.startswith("\t"):
                problems.append(f"line {no}: tab in indentation (YAML forbids tabs)")
                continue
            if key is None:
                problems.append(f"line {no}: indented line before any key")
                continue
            indented[key] = indented.get(key, 0) + 1
            if mode == "plain":
                if ln.strip().startswith("#"):
                    problems.append(f"{key} (line {no}): a comment line inside a multi-line value "
                                    f"(YAML ends the value there, so the next line is an error)")
                else:
                    prob = _plain_problem(ln.strip())
                    if prob:
                        problems.append(f"{key} (line {no}): {prob}")
            elif mode == "nested" and key == "description" and not ln.strip().startswith("- "):
                prob = _plain_problem(ln.strip())   # a description is a string, here a plain scalar
                if prob:
                    problems.append(f"{key} (line {no}): {prob}")
            elif mode == "done":
                problems.append(f"{key} (line {no}): indented line after a complete value")
            continue
        if ln.startswith("#"):
            continue
        m = KEY_RE.match(ln)
        if not m:
            problems.append(f"line {no}: not a 'key: value' line: {ln!r}")
            key, mode = None, None
            continue
        key, value = m.group(1), (m.group(2) or "")
        if key in values:
            problems.append(f"duplicate key {key!r} (line {no})")
        prob, mode = _value_problem(value)
        if prob:
            problems.append(f"{key} (line {no}): {prob}")
        values.setdefault(key, value.strip())

    desc = values.get("description")
    if desc is None:
        problems.append("missing 'description' (required)")
    elif COMMENT_TAIL_RE.sub("", desc).strip() in NULLS and not indented.get("description"):
        problems.append("empty 'description' (YAML reads it as null)")
    elif desc[:1] in ("|", ">") and not indented.get("description"):
        problems.append("empty 'description' block")
    name = values.get("name")
    if name is not None:
        name = COMMENT_TAIL_RE.sub("", name).strip().strip("\"'")
    if kind == "agent" and not name:
        problems.append("missing 'name' (required for agents)")
    if name and name != stem:
        where = "file name" if kind == "agent" else "directory name"
        problems.append(f"name {name!r} does not match the {where} {stem!r}")
    model = values.get("model")
    if model is not None:
        model = COMMENT_TAIL_RE.sub("", model).strip().strip("\"'")
    if model is not None and model not in MODEL_ALIASES:
        problems.append(f"model {model!r} is not an alias ({', '.join(sorted(MODEL_ALIASES))}); "
                        f"use aliases, never dated model IDs (ADR-0003)")
    return problems


def targets(root: Path) -> list[tuple[Path, str, str]]:
    agents = [(p, "agent", p.stem) for p in sorted((root / ".claude" / "agents").glob("*.md"))
              if p.name.lower() != "readme.md"]
    skills = [(p, "skill", p.parent.name) for p in sorted((root / ".claude" / "skills").glob("*/SKILL.md"))]
    return agents + skills


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    if len(argv) > 1 or (argv and argv[0].startswith("-")):
        print("usage: python3 bin/agent_lint.py [repo root]")
        return 2
    root = Path(argv[0]) if argv else Path.cwd()
    if not (root / ".claude").is_dir():
        print(f"usage: python3 bin/agent_lint.py [repo root]\nno .claude/ directory under {root}")
        return 2
    files = targets(root)
    bad = 0
    for path, kind, stem in files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            problems = [f"cannot read: {e}"]
        else:
            try:
                problems = lint_frontmatter(text, kind, stem)
            except Exception as e:  # a lint bug must not stop the other files being checked
                problems = [f"lint error (please report): {e!r}"]
        for p in problems:
            print(f"  {path.relative_to(root).as_posix()}: {p}")
        bad += bool(problems)
    verdict = "FAIL" if bad else "PASS"
    print(f"AGENT LINT: {verdict} ({len(files)} files, {bad} with problems)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
