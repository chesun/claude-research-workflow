#!/usr/bin/env python3
"""Tests for bin/agent_lint.py (agent and skill frontmatter lint).

Plain check() style, matching bin/test_blueprint_check.py. Run:
    python3 bin/test_agent_lint.py      # exit 0 = all pass
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILS: list[str] = []
PASSES = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASSES
    if ok:
        PASSES += 1
        print(f"  PASS  {name}")
    else:
        FAILS.append(name)
        print(f"  FAIL  {name}  {detail}")


al = None  # set in main()


def lint(body: str, kind: str = "agent", stem: str = "demo") -> list[str]:
    return al.lint_frontmatter(body, kind, stem)


GOOD = "---\nname: demo\ndescription: Does one thing well. Use for demos.\nmodel: fable\ntools: Read, Grep\n---\n# Body\n"


def has(problems: list[str], *words: str) -> bool:
    return any(all(w in p for w in words) for p in problems)


def test_plain_scalars() -> None:
    check("al_good_agent_clean", lint(GOOD) == [], str(lint(GOOD)))
    p = lint(GOOD.replace("Does one thing well.", "Does one thing: well."))
    check("al_colon_space_in_description", has(p, "description", "': '"), str(p))
    p = lint(GOOD.replace("Use for demos.", "Use for demos:"))
    check("al_trailing_colon", has(p, "description"), str(p))
    p = lint(GOOD.replace("well.", "well. #1 choice"))
    check("al_hash_comment_truncates", has(p, "description", "#"), str(p))
    check("al_hash_without_space_ok", lint(GOOD.replace("well.", "well.#1 and C# too")) == [],
          str(lint(GOOD.replace("well.", "well.#1 and C# too"))))
    check("al_url_colon_ok", lint(GOOD.replace("well.", "well (see https://x.org/a:b).")) == [],
          str(lint(GOOD.replace("well.", "well (see https://x.org/a:b)."))))
    for ch in ("*", "&", "!", "%", "@", "`", ",", "[x", "{x", "- x", "? x"):
        body = GOOD.replace("description: Does", f"description: {ch}Does")
        if ch in ("[x", "{x"):
            body = GOOD.replace("description: Does", f"description: {ch} Does")
        p = lint(body)
        check(f"al_indicator_start_{ch.strip()[:1]}", has(p, "description"), str(p))


def test_quoted_and_block() -> None:
    check("al_double_quoted_colon_ok", lint(GOOD.replace("Does one thing well. Use for demos.", '"Does one: thing."')) == [])
    check("al_single_quoted_ok", lint(GOOD.replace("Does one thing well. Use for demos.", "'It''s fine: yes.'")) == [])
    p = lint(GOOD.replace("Does one thing well.", '"Not closed'))
    check("al_unclosed_quote", has(p, "description", "quote"), str(p))
    p = lint(GOOD.replace("Does one thing well.", '"closed" then more'))
    check("al_text_after_quote", has(p, "description"), str(p))
    block = "---\nname: demo\ndescription: |\n  Line one: with colon.\n  Line two.\n---\n"
    check("al_block_scalar_ok", lint(block) == [], str(lint(block)))
    folded = "---\nname: demo\ndescription: >-\n  Folded: fine.\n---\n"
    check("al_folded_scalar_ok", lint(folded) == [], str(lint(folded)))
    cont = "---\nname: demo\ndescription: First line\n  continues: badly\n---\n"
    check("al_plain_continuation_checked", has(lint(cont), "description"), str(lint(cont)))
    lst = "---\nname: demo\ndescription: d\ntools:\n  - Read\n  - Grep\n---\n"
    check("al_block_list_ok", lint(lst) == [], str(lint(lst)))
    flow = GOOD.replace("tools: Read, Grep", "tools: [Read, Grep]")
    check("al_flow_list_ok", lint(flow) == [], str(lint(flow)))
    check("al_flow_unclosed", has(lint(GOOD.replace("tools: Read, Grep", "tools: [Read, Grep")), "tools"))


def test_structure() -> None:
    check("al_no_frontmatter", has(lint("# Just a body\n"), "frontmatter"))
    check("al_unterminated", has(lint("---\nname: demo\ndescription: d\n"), "unterminated"))
    check("al_duplicate_key", has(lint(GOOD.replace("model: fable", "model: fable\nmodel: opus")), "duplicate", "model"))
    check("al_tab_indent", has(lint("---\nname: demo\ndescription: |\n\tTabbed.\n---\n"), "tab"))
    check("al_bad_line", has(lint(GOOD.replace("model: fable", "just words")), "just words"))
    check("al_agent_needs_name", has(lint(GOOD.replace("name: demo\n", "")), "name"))
    check("al_agent_name_matches_file", has(lint(GOOD, stem="other"), "name", "other"))
    check("al_description_required", has(lint(GOOD.replace("description: Does one thing well. Use for demos.\n", "")),
                                         "description"))
    check("al_empty_description", has(lint(GOOD.replace("Does one thing well. Use for demos.", "")), "description"))
    check("al_skill_name_optional", lint(GOOD.replace("name: demo\n", ""), kind="skill") == [])
    check("al_skill_name_matches_dir", has(lint(GOOD, kind="skill", stem="other"), "name", "other"))
    check("al_model_alias_only", has(lint(GOOD.replace("model: fable", "model: claude-opus-5-5")), "model"))
    check("al_model_inherit_ok", lint(GOOD.replace("model: fable", "model: inherit")) == [])
    crlf = GOOD.replace("\n", "\r\n")
    check("al_crlf_ok", lint(crlf) == [], str(lint(crlf)))
    check("al_bom_ok", lint("﻿" + GOOD) == [], str(lint("﻿" + GOOD)))


def test_review_fixes() -> None:
    """2026-10-12 red-team and correctness reviews."""
    # Medium: an empty description is judged on its own lines, not on another key's block.
    p = lint("---\nname: demo\ndescription:\ntools:\n  - Read\n---\n")
    check("rl_empty_description_before_block_key", has(p, "description"), str(p))
    p = lint("---\nname: demo\ndescription: |\ntools:\n  - Read\n---\n")
    check("rl_empty_block_description", has(p, "description"), str(p))
    for v in ("null", "~", "Null"):
        p = lint(GOOD.replace("Does one thing well. Use for demos.", v))
        check(f"rl_null_description_{v}", has(p, "description"), str(p))
    # Low: shapes strict YAML rejects or mangles.
    p = lint("  ---\nname: demo\ndescription: d\n---\n")
    check("rl_indented_opening_fence", has(p, "frontmatter"), str(p))
    p = lint(GOOD.replace("Does one thing well.", "Does one thing:\tbadly."))
    check("rl_colon_tab", has(p, "description"), str(p))
    p = lint(GOOD.replace("Does one thing well.", "Does one thing\t# trailing"))
    check("rl_tab_hash", has(p, "description"), str(p))
    p = lint("---\nname: demo\ndescription: |\n  intro\n  ---\n  more\nmodel: claude-opus-5-5\n---\n")
    check("rl_indented_fence_in_block", has(p, "model"), str(p))
    p = lint("---\nname: demo\ndescription: First line\n  # note\n  more text\n---\n")
    check("rl_comment_inside_plain_continuation", has(p, "description"), str(p))
    p = lint('---\nname: demo\ndescription: "ok"\n  stray: line\n---\n')
    check("rl_indented_after_quoted", has(p, "description"), str(p))
    # Low: valid YAML no longer wrongly failed, and messages do not claim YAML misreads it.
    p = lint(GOOD.replace("name: demo", "name : demo"))
    check("rl_space_before_colon_ok", p == [], str(p))
    p = lint(GOOD.replace("model: fable", "model: fable # pinned"))
    check("rl_comment_not_double_flagged", not has(p, "alias"), str(p))
    p = lint(GOOD.replace("Does one thing well. Use for demos.", '"He said \\"a: b\\" twice."'))
    check("rl_double_quote_escapes", p == [], str(p))
    p = lint(GOOD.replace("Does one thing well. Use for demos.", '"First line: ok\n  second line"'))
    check("rl_multiline_quote_message_honest", has(p, "one line") and not has(p, "misread"), str(p))


def test_review_round2() -> None:
    """2026-10-12 round-2 red-team review."""
    body = "---\nname: demo\ndescription:\n  Does one thing well.\n---\n"
    try:
        p = lint(body)
        ok = p == []
    except Exception as e:  # the High: an IndexError aborted the whole run
        p, ok = repr(e), False
    check("r2_description_on_next_line_ok", ok, str(p))
    try:
        p = lint("---\nname: demo\ndescription:\n  Does one: thing.\n---\n")
        ok = has(p, "description")
    except Exception as e:
        p, ok = repr(e), False
    check("r2_description_next_line_checked", ok, str(p))
    p = lint(GOOD.replace("name: demo", "name: demo # the demo"))
    check("r2_name_comment_not_double_flagged", not has(p, "does not match"), str(p))
    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        (root / ".claude" / "agents").mkdir(parents=True)
        (root / ".claude" / "agents" / "README.md").write_text("# Agents\n", encoding="utf-8")
        (root / ".claude" / "agents" / "demo.md").write_text(GOOD, encoding="utf-8")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = al.main([str(root)])
        check("r2_agents_readme_skipped", rc == 0, f"{rc} {buf.getvalue()}")


def test_cli() -> None:
    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        (root / ".claude" / "agents").mkdir(parents=True)
        (root / ".claude" / "skills" / "demo-skill").mkdir(parents=True)
        (root / ".claude" / "agents" / "demo.md").write_text(GOOD, encoding="utf-8")
        (root / ".claude" / "skills" / "demo-skill" / "SKILL.md").write_text(
            "---\nname: demo-skill\ndescription: A skill.\n---\n", encoding="utf-8")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = al.main([str(root)])
        check("al_cli_clean_exit_0", rc == 0 and "2 files" in buf.getvalue(), f"{rc} {buf.getvalue()}")
        (root / ".claude" / "agents" / "bad.md").write_text(
            GOOD.replace("name: demo", "name: bad").replace("thing well", "thing: well"), encoding="utf-8")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = al.main([str(root)])
        out = buf.getvalue()
        check("al_cli_problem_exit_1", rc == 1 and "bad.md" in out and "description" in out, f"{rc} {out}")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = al.main([str(root / "nope")])
        check("al_cli_missing_dir_exit_2", rc == 2, f"{rc}")


def main() -> int:
    global al
    try:
        spec = importlib.util.spec_from_file_location("agent_lint", HERE / "agent_lint.py")
        al = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(al)
    except Exception as e:
        print(f"FAIL  cannot load agent_lint.py: {e!r}")
        return 1
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            print(name)
            fn()
    print(f"\n{PASSES} passed, {len(FAILS)} failed")
    if FAILS:
        print("failed: " + ", ".join(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
