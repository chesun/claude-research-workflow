#!/usr/bin/env python3
"""Tests for bin/blueprint_check.py (theory blueprint validator).

Plain-Python check() style, matching .claude/hooks/test_*.py. Run:
    python3 bin/test_blueprint_check.py      # exit 0 = all pass
Fixtures are built in throwaway temp dirs; nothing in the repo is touched.
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD = HERE / "blueprint_check.py"

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


def load():
    spec = importlib.util.spec_from_file_location("blueprint_check", MOD)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["blueprint_check"] = mod
    spec.loader.exec_module(mod)
    return mod


bc = None  # set in main()


# --- fixture helpers ---------------------------------------------------------

def fmt_list(items) -> str:
    return "[" + ", ".join(items) + "]"


def write_node(d: Path, label: str, kind: str = "claim", status: str | None = None,
               uses=(), statement: str = "S", proof: str = "", log=None,
               filename: str | None = None, raw_prefix: str = "",
               **header) -> Path:
    """Write a node file. log=None writes one valid `new -> status` entry.

    log may be a list of (frm, to, actor, locators) tuples; the statement hash
    is filled in automatically unless a 5th element overrides it.
    """
    if status is None:
        status = "stated" if kind in ("definition", "assumption") else "conjecture"
    h = bc.statement_hash(statement)
    if log is None:
        log = [("new", status, "theorist", "")]
    lines = []
    for e in log:
        frm, to, actor, loc = e[:4]
        hh = e[4] if len(e) > 4 and e[4] else h
        ph = e[5] if len(e) > 5 else (bc.proof_hash(proof, uses) if to in ("proved", "checked") else None)
        date = e[6] if len(e) > 6 else "2026-10-12"
        suffix = f" proof:{ph}" if ph else ""
        lines.append(f"- {date} | {frm} -> {to} | {actor} | {loc} | stmt:{hh}{suffix}")
    fields = {
        "label": label, "kind": kind, "status": status, "uses": fmt_list(uses),
        "supersedes": "", "superseded_by": "", "lean": "", "paper_ref": "",
    }
    fields.update(header)
    head = "\n".join(f"{k}: {v}".rstrip() for k, v in fields.items())
    text = (f"{raw_prefix}---\n{head}\n---\n## Statement\n{statement}\n"
            f"## Proof\n{proof}\n## Evidence log\n" + "\n".join(lines) + "\n")
    p = d / (filename or (label.replace(":", "-") + ".md"))
    p.write_text(text, encoding="utf-8", newline="")
    return p


def raises(fn) -> tuple[bool, str]:
    try:
        fn()
    except bc.NodeError as e:
        return True, str(e)
    except Exception as e:  # wrong exception type is a failure
        return False, f"wrong exception {type(e).__name__}: {e}"
    return False, "no exception"


# --- Task 1: format + parser --------------------------------------------------

def test_task1(tmp: Path) -> None:
    d = tmp / "t1"; d.mkdir()

    p = write_node(d, "prop:a", uses=["def:x", "asm:y"], statement="For all n, f(n) >= 0.",
                   proof="By induction.", lean="Foo.bar", paper_ref="paper.tex:12")
    n = bc.parse_node(p)
    check("parse_minimal_claim",
          n.label == "prop:a" and n.kind == "claim" and n.status == "conjecture"
          and n.uses == ["def:x", "asm:y"] and n.lean == "Foo.bar"
          and n.paper_ref == "paper.tex:12" and n.supersedes is None
          and n.statement == "For all n, f(n) >= 0." and n.proof == "By induction."
          and len(n.log) == 1 and n.log[0].frm == "new" and n.log[0].to == "conjecture"
          and n.log[0].actor == "theorist",
          repr(n) if n else "")

    check("hash_crlf_stable", bc.statement_hash("a\r\nb  \r\n") == bc.statement_hash("a\nb"))
    check("hash_is_12_hex", len(bc.statement_hash("x")) == 12
          and all(c in "0123456789abcdef" for c in bc.statement_hash("x")))

    stmt = "n* = σ_d/√c − σ_d²/σ₀²"
    p = write_node(d, "prop:bom", statement=stmt, raw_prefix="﻿")
    try:
        n = bc.parse_node(p)
        check("parse_bom_and_unicode", n.label == "prop:bom" and n.statement == stmt, repr(n.statement))
    except Exception as e:
        check("parse_bom_and_unicode", False, repr(e))

    crlf = d / "prop-crlf.md"
    body = write_node(d, "prop:crlf", statement="line1\nline2").read_text(encoding="utf-8")
    crlf.write_bytes(body.replace("\n", "\r\n").encode("utf-8"))
    try:
        n = bc.parse_node(crlf)
        check("parse_crlf_file", n.statement == "line1\nline2" and len(n.log) == 1, repr(n.statement))
    except Exception as e:
        check("parse_crlf_file", False, repr(e))

    p = write_node(d, "prop:y", filename="prop-x.md")
    ok, msg = raises(lambda: bc.parse_node(p))
    check("filename_label_mismatch", ok, msg)

    p = write_node(d, "prop:k", colour="blue")
    ok, msg = raises(lambda: bc.parse_node(p))
    check("unknown_header_key", ok, msg)

    p = write_node(d, "asm:z", kind="assumption", status="proved",
                   log=[("new", "proved", "theorist", "")])
    ok, msg = raises(lambda: bc.parse_node(p))
    check("bad_kind_status_combo", ok, msg)

    p = write_node(d, "prop:badlog")
    p.write_text(p.read_text(encoding="utf-8").replace(" | stmt:", " stmt:"), encoding="utf-8")
    ok, msg = raises(lambda: bc.parse_node(p))
    check("malformed_log_line", ok, msg)

    p = write_node(d, "Prop:Upper", filename="Prop-Upper.md")
    ok, msg = raises(lambda: bc.parse_node(p))
    check("bad_label_pattern", ok, msg)


# --- Task 2: graph, status and evidence rules ---------------------------------

_repo_n = 0


def mkrepo(tmp: Path) -> tuple[Path, Path]:
    """A throwaway 'repo' (has .git/) with theory/blueprint/ and fixture files."""
    global _repo_n
    _repo_n += 1
    root = tmp / f"repo{_repo_n}"
    (root / ".git").mkdir(parents=True)
    bp = root / "theory" / "blueprint"
    (bp / "checks" / "a").mkdir(parents=True)
    (bp / "checks" / "a" / "s.py").write_text("print('ok')\n", encoding="utf-8")
    rev = root / "quality_reports" / "reviews"
    rev.mkdir(parents=True)
    for r in ("r1.md", "r2.md"):
        (rev / r).write_text("# review\n", encoding="utf-8")
    return root, bp


CHECK = "theory/blueprint/checks/a/s.py"
PLAIN = "quality_reports/reviews/r1.md;quality_reports/reviews/r2.md"  # files, but not verifier reports
PROOF = "Proof text."


def write_reports(root: Path, label: str, proof: str = PROOF, verdict: str = "PASS",
                  runs: str = "ab", target: str | None = None, uses=()) -> str:
    """Verifier reports with the header the validator reads; returns ';'-joined locators."""
    locs = []
    for s in runs:
        name = f"2026-10-12_{label.replace(':', '-')}_proof-verifier-{s}_review.md"
        (root / "quality_reports" / "reviews" / name).write_text(
            f"# {label} Review — proof-verifier\n**Date:** 2026-10-12\n"
            f"**Reviewer:** proof-verifier (blind)\n**Target:** {target or label}\n"
            f"**Score:** {verdict}\n**Proof:** {bc.proof_hash(proof, uses)}\n**Status:** Active\n\nBody.\n",
            encoding="utf-8")
        locs.append(f"quality_reports/reviews/{name}")
    return ";".join(locs)


def climb(target: str, root: Path | None = None, label: str | None = None,
          proof: str = PROOF, uses=()) -> list[tuple]:
    """A valid evidence log climbing the ladder from new to `target`."""
    reports = write_reports(root, label, proof, uses=uses) if root is not None else PLAIN
    steps = [("new", "conjecture", "theorist", ""),
             ("conjecture", "survived-search", "theorist", CHECK),
             ("survived-search", "proved", "theorist", ""),
             ("proved", "checked", "proof-verifier", reports),
             ("checked", "formalized", "user", ""),
             ("formalized", "verified", "user", "")]
    out = []
    for s in steps:
        out.append(s)
        if s[1] == target:
            return out
    raise ValueError(target)


def claim_at(bp: Path, label: str, target: str, uses=(), root: Path | None = None, **kw) -> Path:
    kw.setdefault("proof", PROOF if target in ("proved", "checked", "formalized", "verified") else "")
    if root is None:
        root = bp.parent.parent
    return write_node(bp, label, status=target, uses=uses,
                      log=climb(target, root, label, kw["proof"] or PROOF, uses), **kw)


def verdict(bp: Path, root: Path | None = None):
    return bc.check_blueprint(bp, repo_root=root)


def fails_naming(rep, label: str) -> bool:
    return rep.verdict == "FAIL" and any(label in e for e in rep.errors)


def test_task2(tmp: Path) -> None:
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", uses=["def:missing"])
    rep = verdict(bp, root)
    check("g1_missing_use", fails_naming(rep, "def:missing"), str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", uses=["prop:b"])
    write_node(bp, "prop:b", uses=["prop:a"])
    rep = verdict(bp, root)
    check("g1_cycle", rep.verdict == "FAIL" and any("cycle" in e for e in rep.errors), str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", uses=["prop:a"])
    rep = verdict(bp, root)
    check("g1_self_use", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    claim_at(bp, "prop:a", "checked", uses=["prop:b"])
    write_node(bp, "prop:b")
    rep = verdict(bp, root)
    check("g3_checked_on_conjecture", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    claim_at(bp, "prop:a", "checked", uses=["asm:x", "def:y"])
    write_node(bp, "asm:x", kind="assumption")
    write_node(bp, "def:y", kind="definition")
    rep = verdict(bp, root)
    check("g3_checked_on_assumption_ok", rep.verdict == "PASS", str(rep.errors + rep.warnings))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", uses=["prop:b"])
    write_node(bp, "prop:b", status="refuted",
               log=[("new", "conjecture", "theorist", ""), ("conjecture", "refuted", "theorist", CHECK)])
    rep = verdict(bp, root)
    check("g4_uses_refuted", fails_naming(rep, "prop:b"), str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", uses=["prop:b"])
    write_node(bp, "prop:b", status="superseded", superseded_by="prop:c",
               log=[("new", "conjecture", "theorist", ""), ("conjecture", "superseded", "theorist", "")])
    write_node(bp, "prop:c")
    rep = verdict(bp, root)
    check("g4_uses_superseded_warns", rep.verdict == "UNVERIFIED"
          and any("prop:b" in w for w in rep.warnings), f"{rep.verdict} {rep.errors} {rep.warnings}")

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="proved", proof="P.", log=climb("survived-search"))
    rep = verdict(bp, root)
    check("s1_status_log_mismatch", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="proved", proof="P.",
               log=[("conjecture", "proved", "theorist", "")])
    rep = verdict(bp, root)
    check("s1_first_entry_not_new", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="proved", proof="P.",
               log=[("new", "conjecture", "theorist", ""), ("conjecture", "proved", "theorist", "")])
    rep = verdict(bp, root)
    check("s2_skip_rung", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="survived-search", proof="P.",
               log=climb("proved") + [("proved", "survived-search", "proof-verifier", "quality_reports/reviews/r1.md")])
    rep = verdict(bp, root)
    check("s2_downgrade_ok", rep.verdict == "PASS", str(rep.errors + rep.warnings))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="conjecture",
               log=[("new", "conjecture", "theorist", ""), ("conjecture", "refuted", "theorist", CHECK),
                    ("refuted", "conjecture", "theorist", "")])
    rep = verdict(bp, root)
    check("s2_leave_terminal", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    old = bc.statement_hash("old statement")
    write_node(bp, "prop:a", statement="new statement",
               log=[("new", "conjecture", "theorist", "", old)])
    rep = verdict(bp, root)
    check("statement_changed_after_log", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="survived-search",
               log=[("new", "conjecture", "theorist", ""),
                    ("conjecture", "survived-search", "theorist", "quality_reports/reviews/r1.md")])
    rep = verdict(bp, root)
    check("e1_search_without_checks_file", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    claim_at(bp, "prop:a", "proved", proof="Step 1 holds. [GAP: why is f concave?]")
    rep = verdict(bp, root)
    check("e2_gap_in_proved", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="proved", proof="",
               log=climb("proved"))
    rep = verdict(bp, root)
    check("e2_empty_proof", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    log = climb("survived-search") + [("survived-search", "proved", "proof-verifier", "")]
    write_node(bp, "prop:a", status="proved", proof="P.", log=log)
    rep = verdict(bp, root)
    check("e2_wrong_actor", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    one = write_reports(root, "prop:a", "P.", runs="a")
    log = climb("proved") + [("proved", "checked", "proof-verifier", one)]
    write_node(bp, "prop:a", status="checked", proof="P.", log=log)
    rep = verdict(bp, root)
    check("e3_single_verifier", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    one = write_reports(root, "prop:a", "P.", runs="a")
    log = climb("proved") + [("proved", "checked", "proof-verifier", f"{one};{one}")]
    write_node(bp, "prop:a", status="checked", proof="P.", log=log)
    rep = verdict(bp, root)
    check("e3_duplicate_reports", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    log = climb("proved") + [("proved", "checked", "theorist", write_reports(root, "prop:a", "P."))]
    write_node(bp, "prop:a", status="checked", proof="P.", log=log)
    rep = verdict(bp, root)
    check("e3_wrong_actor", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    log = climb("checked", root, "prop:a", "P.") + [("checked", "formalized", "theorist", "")]
    write_node(bp, "prop:a", status="formalized", proof="P.", log=log)
    rep = verdict(bp, root)
    check("e4_formalized_by_theorist", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="superseded",
               log=[("new", "conjecture", "theorist", ""), ("conjecture", "superseded", "theorist", "")])
    rep = verdict(bp, root)
    check("e5_superseded_without_successor", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="refuted",
               log=[("new", "conjecture", "theorist", ""), ("conjecture", "refuted", "theorist", "")])
    rep = verdict(bp, root)
    check("e5_refuted_without_evidence", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="survived-search",
               log=[("new", "conjecture", "theorist", "theory/missing.tex:12"),
                    ("conjecture", "survived-search", "theorist", CHECK)])
    rep = verdict(bp, root)
    check("l1_missing_locator", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="survived-search",
               log=[("new", "conjecture", "theorist", ""),
                    ("conjecture", "survived-search", "theorist", "theory\\blueprint\\checks\\a\\s.py:3-5")])
    rep = verdict(bp, root)
    check("locator_backslash_and_linesuffix", rep.verdict == "PASS", str(rep.errors + rep.warnings))

    root, bp = mkrepo(tmp)
    outside = tmp / "outside.txt"
    outside.write_text("x", encoding="utf-8")
    write_node(bp, "prop:a", log=[("new", "conjecture", "theorist", str(outside))])
    rep = verdict(bp, root)
    check("locator_outside_repo_unverified", rep.verdict == "UNVERIFIED" and not rep.errors,
          f"{rep.verdict} {rep.errors} {rep.warnings}")

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", log=[("new", "conjecture", "theorist", "../../../escape.txt")])
    (root.parent / "escape.txt").write_text("x", encoding="utf-8")
    rep = verdict(bp, root)
    check("locator_dotdot_escape_unverified", rep.verdict == "UNVERIFIED" and not rep.errors,
          f"{rep.verdict} {rep.errors} {rep.warnings}")

    root, bp = mkrepo(tmp)
    rep = verdict(bp, root)
    check("empty_blueprint_fail", rep.verdict == "FAIL", str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a")
    (bp / "prop-bad.md").write_text("no header here\n", encoding="utf-8")
    try:
        rep = verdict(bp, root)
        check("nodeerror_becomes_error", fails_naming(rep, "prop-bad.md"), str(rep.errors))
    except Exception as e:
        check("nodeerror_becomes_error", False, repr(e))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a")
    (bp / "STATUS.md").write_text("| table |\n", encoding="utf-8")
    (bp / "README.md").write_text("# notes\n", encoding="utf-8")
    rep = verdict(bp, root)
    check("status_and_readme_ignored", rep.verdict == "PASS", str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a")
    rep = bc.check_blueprint(bp)  # repo root auto-detected from .git
    check("repo_root_autodetect", rep.verdict == "PASS", str(rep.errors + rep.warnings))

    # full chain: def -> asm -> claim(checked) ; variant refuted ; claim conditional -> successor
    root, bp = mkrepo(tmp)
    write_node(bp, "def:v", kind="definition")
    write_node(bp, "asm:n", kind="assumption", uses=["def:v"])
    claim_at(bp, "prop:main", "checked", uses=["def:v", "asm:n"])
    write_node(bp, "var:main-no-n", kind="variant", status="refuted", uses=["def:v"],
               log=[("new", "conjecture", "theorist", ""), ("conjecture", "refuted", "theorist", CHECK)])
    write_node(bp, "prop:guess", status="conditional", superseded_by="prop:main",
               log=[("new", "conjecture", "theorist", ""), ("conjecture", "conditional", "theorist", CHECK)])
    rep = verdict(bp, root)
    check("full_valid_blueprint_pass", rep.verdict == "PASS" and len(rep.nodes) == 5,
          f"{rep.verdict} {rep.errors} {rep.warnings}")


# --- Review fixes (2026-10-11 red-team + correctness reviews) --------------------

def checked_log(root: Path, label: str, proof: str, reports: str | None = None) -> list[tuple]:
    base = climb("proved", proof=proof)
    return base + [("proved", "checked", "proof-verifier",
                    reports if reports is not None else write_reports(root, label, proof))]


def test_review_fixes(tmp: Path) -> None:
    import os
    # Critical: Windows device names must not count as evidence files.
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="checked", proof="P.",
               log=checked_log(root, "prop:a", "P.", "nul;NUL"))
    rep = verdict(bp, root)
    check("rt_nul_reports_rejected", fails_naming(rep, "prop:a"), str(rep.errors))
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="survived-search",
               log=[("new", "conjecture", "theorist", ""),
                    ("conjecture", "survived-search", "theorist", "theory/blueprint/checks/nul")])
    rep = verdict(bp, root)
    check("rt_nul_check_rejected", fails_naming(rep, "prop:a"), str(rep.errors))

    # High: directories are not evidence files.
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="survived-search",
               log=[("new", "conjecture", "theorist", ""),
                    ("conjecture", "survived-search", "theorist", "theory/blueprint/checks/a")])
    rep = verdict(bp, root)
    check("rt_directory_locator_rejected", fails_naming(rep, "prop:a"), str(rep.errors))

    # High: `checked` needs two real verifier reports for this node and this proof.
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="checked", proof="P.", log=checked_log(root, "prop:a", "P.", PLAIN))
    rep = verdict(bp, root)
    check("rt_plain_files_not_reports", fails_naming(rep, "prop:a"), str(rep.errors))
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="checked", proof="P.",
               log=checked_log(root, "prop:a", "P.", write_reports(root, "prop:a", "P.", target="prop:other")))
    rep = verdict(bp, root)
    check("rt_report_wrong_target", fails_naming(rep, "prop:a"), str(rep.errors))
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="checked", proof="P.",
               log=checked_log(root, "prop:a", "P.", write_reports(root, "prop:a", "P.", verdict="FAIL")))
    rep = verdict(bp, root)
    check("rt_report_not_pass", fails_naming(rep, "prop:a"), str(rep.errors))
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="checked", proof="P.", log=checked_log(root, "prop:a", "P."))
    rep = verdict(bp, root)
    check("rt_valid_reports_pass", rep.verdict == "PASS", str(rep.errors + rep.warnings))

    # High: the proof is hashed; replacing it after `checked` fails.
    root, bp = mkrepo(tmp)
    p = write_node(bp, "prop:a", status="checked", proof="P.", log=checked_log(root, "prop:a", "P."))
    p.write_text(p.read_text(encoding="utf-8").replace("\nP.\n", "\nA different proof.\n"), encoding="utf-8")
    rep = verdict(bp, root)
    check("rt_proof_replaced_after_checked", fails_naming(rep, "prop:a"), str(rep.errors))

    # High: downgrade then re-climb cannot reuse reports written for the old proof.
    root, bp = mkrepo(tmp)
    old = write_reports(root, "prop:a", "Old proof.")
    log = climb("proved", proof="Old proof.")
    log[-1] = log[-1][:4] + ("", bc.proof_hash("Old proof."))
    log += [("proved", "checked", "proof-verifier", old, "", bc.proof_hash("Old proof.")),
            ("checked", "survived-search", "theorist", CHECK),
            ("survived-search", "proved", "theorist", "", "", bc.proof_hash("New proof.")),
            ("proved", "checked", "proof-verifier", old, "", bc.proof_hash("New proof."))]
    write_node(bp, "prop:a", status="checked", proof="New proof.", log=log)
    rep = verdict(bp, root)
    check("rt_reclimb_reuses_old_reports", fails_naming(rep, "prop:a"), str(rep.errors))

    # Low: a hard link is not a second report.
    root, bp = mkrepo(tmp)
    one = write_reports(root, "prop:a", "P.", runs="a")
    os.link(root / one, root / "quality_reports" / "reviews" / "linked_review.md")
    write_node(bp, "prop:a", status="checked", proof="P.",
               log=checked_log(root, "prop:a", "P.", f"{one};quality_reports/reviews/linked_review.md"))
    rep = verdict(bp, root)
    check("rt_hardlink_not_distinct", fails_naming(rep, "prop:a"), str(rep.errors))

    # Medium: gap markers in any case/spacing; comment-only proofs are empty.
    for i, gap in enumerate(("[gap: x]", "[ GAP : x ]", "[Gap:x]")):
        root, bp = mkrepo(tmp)
        claim_at(bp, "prop:a", "proved", proof=f"Step 1. {gap}")
        rep = verdict(bp, root)
        check(f"rt_gap_variant_{i}", fails_naming(rep, "prop:a"), str(rep.errors))
    root, bp = mkrepo(tmp)
    claim_at(bp, "prop:a", "proved", proof="<!-- nothing here -->")
    rep = verdict(bp, root)
    check("rt_comment_only_proof", fails_naming(rep, "prop:a"), str(rep.errors))

    # Medium: look-alike headings and stray preamble text are rejected; comments allowed.
    d = tmp / "rtparse"; d.mkdir()
    p = write_node(d, "prop:h1")
    p.write_text(p.read_text(encoding="utf-8").replace("## Proof", "##  Statement\nfake\n## Proof"), encoding="utf-8")
    ok, msg = raises(lambda: bc.parse_node(p))
    check("rt_lookalike_heading", ok, msg)
    p = write_node(d, "prop:h2")
    p.write_text(p.read_text(encoding="utf-8").replace("---\n## Statement", "---\nA hidden claim.\n## Statement"), encoding="utf-8")
    ok, msg = raises(lambda: bc.parse_node(p))
    check("rt_preamble_text_rejected", ok, msg)
    p = write_node(d, "prop:h3")
    p.write_text(p.read_text(encoding="utf-8").replace("---\n## Statement", "---\n<!--\nnotes\n-->\n## Statement"), encoding="utf-8")
    try:
        bc.parse_node(p)
        check("rt_preamble_comment_ok", True)
    except Exception as e:
        check("rt_preamble_comment_ok", False, repr(e))

    # Medium: deep chains do not hit the recursion limit.
    root, bp = mkrepo(tmp)
    prev = None
    for i in range(1500):
        lab = f"prop:c{i}"
        write_node(bp, lab, uses=[prev] if prev else [])
        prev = lab
    try:
        rep = verdict(bp, root)
        check("rt_long_chain_no_recursion", rep.verdict == "PASS", str(rep.errors[:2]))
    except RecursionError as e:
        check("rt_long_chain_no_recursion", False, repr(e))

    # Low: dates are real and non-decreasing.
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", log=[("new", "conjecture", "theorist", "", "", None, "2026-13-40")])
    rep = verdict(bp, root)
    check("rt_bad_date", fails_naming(rep, "prop:a"), str(rep.errors))
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="survived-search",
               log=[("new", "conjecture", "theorist", "", "", None, "2026-10-12"),
                    ("conjecture", "survived-search", "theorist", CHECK, "", None, "2026-10-01")])
    rep = verdict(bp, root)
    check("rt_decreasing_dates", fails_naming(rep, "prop:a"), str(rep.errors))

    # Medium/Low: empty statement; succession links must make sense.
    p = write_node(d, "prop:empty", statement="")
    ok, msg = raises(lambda: bc.parse_node(p))
    check("rt_empty_statement", ok, msg)
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="superseded", superseded_by="prop:a",
               log=[("new", "conjecture", "theorist", ""), ("conjecture", "superseded", "theorist", "")])
    rep = verdict(bp, root)
    check("rt_superseded_by_self", fails_naming(rep, "prop:a"), str(rep.errors))
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="superseded", superseded_by="prop:b",
               log=[("new", "conjecture", "theorist", ""), ("conjecture", "superseded", "theorist", "")])
    write_node(bp, "prop:b", status="refuted",
               log=[("new", "conjecture", "theorist", ""), ("conjecture", "refuted", "theorist", CHECK)])
    rep = verdict(bp, root)
    check("rt_superseded_by_refuted", fails_naming(rep, "prop:a"), str(rep.errors))
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", supersedes="prop:ghost")
    rep = verdict(bp, root)
    check("rt_supersedes_unknown", fails_naming(rep, "prop:ghost"), str(rep.errors))

    # Low: drive-relative and URL locators are unverifiable, never PASS.
    for name, loc in (("rt_drive_relative_outside", "C:foo.txt"),
                      ("cr_url_locator_unverified", "https://example.org/paper.pdf")):
        root, bp = mkrepo(tmp)
        write_node(bp, "prop:a", log=[("new", "conjecture", "theorist", loc)])
        rep = verdict(bp, root)
        check(name, rep.verdict == "UNVERIFIED" and not rep.errors, f"{rep.verdict} {rep.errors} {rep.warnings}")

    # Medium: no enclosing repo -> UNVERIFIED, not a misleading FAIL; --repo-root fixes it.
    nr = tmp / "norepo" / "theory" / "blueprint"
    (nr / "checks" / "a").mkdir(parents=True)
    (nr / "checks" / "a" / "s.py").write_text("x\n", encoding="utf-8")
    write_node(nr, "prop:a", status="survived-search",
               log=[("new", "conjecture", "theorist", ""),
                    ("conjecture", "survived-search", "theorist", CHECK)])
    rep = bc.check_blueprint(nr)
    check("cr_no_repo_root_unverified", rep.verdict == "UNVERIFIED" and not rep.errors,
          f"{rep.verdict} {rep.errors}")
    rc, out = run_cli([str(nr), "--repo-root", str(tmp / "norepo")])
    check("cr_repo_root_flag", rc == 0 and "BLUEPRINT: PASS" in out, f"{rc} {out}")

    # High: non-ASCII output must not crash the CLI on a cp1252 console.
    import subprocess
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", log=[("new", "conjecture", "theorist", "https://example.org/σ₀²")])
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONIOENCODING", "PYTHONUTF8")}
    env["PYTHONIOENCODING"] = "cp1252"
    r = subprocess.run([sys.executable, str(MOD), str(bp)], capture_output=True, env=env)
    out = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    check("cr_stdout_non_ascii", r.returncode == 3 and "Traceback" not in out, f"{r.returncode} {out[-300:]}")

    # Low: STATUS.md uses LF and escapes pipes; quoted header values parse.
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a")
    run_cli([str(bp), "--write-status"])
    check("cr_status_md_lf", b"\r\n" not in (bp / "STATUS.md").read_bytes())
    fake = bc.Report("FAIL", ["x: a|b"], [], {})
    check("rt_status_md_pipe_escaped", "a\\|b" in bc.render_status(fake), bc.render_status(fake))
    p = write_node(d, "prop:q")
    p.write_text(p.read_text(encoding="utf-8").replace("label: prop:q", 'label: "prop:q"')
                 .replace("kind: claim", "kind: 'claim'"), encoding="utf-8")
    try:
        n = bc.parse_node(p)
        check("cr_quoted_header_values", n.label == "prop:q" and n.kind == "claim", repr(n.label))
    except Exception as e:
        check("cr_quoted_header_values", False, repr(e))

    # Hash helper on the CLI (used by /theory verify and the theorist).
    p = write_node(d, "prop:hc", statement="S1", proof="P1")
    rc, out = run_cli(["--hashes", str(p)])
    check("cli_hashes", rc == 0 and f"stmt:{bc.statement_hash('S1')} proof:{bc.proof_hash('P1')}" in out, out)


def test_mutation_killers(tmp: Path) -> None:
    """Each test fails only if its single rule is removed (correctness review, Medium)."""
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="survived-search",
               log=[("conjecture", "survived-search", "theorist", CHECK)])
    rep = verdict(bp, root)
    check("mk_s1_first_entry_not_new", rep.verdict == "FAIL"
          and any("first evidence entry" in e for e in rep.errors), str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="conjecture",
               log=[("new", "conjecture", "theorist", ""), ("conjecture", "refuted", "theorist", CHECK),
                    ("refuted", "conjecture", "theorist", "")])
    rep = verdict(bp, root)
    check("mk_leave_terminal_message", any("terminal" in e for e in rep.errors), str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="proved", proof="P.", log=[("new", "proved", "theorist", "")])
    rep = verdict(bp, root)
    check("mk_new_must_go_to_conjecture", any("first entry must be new -> conjecture" in e for e in rep.errors),
          str(rep.errors))

    root, bp = mkrepo(tmp)
    log = climb("formalized", root, "prop:a", "P.") + [("formalized", "verified", "theorist", "")]
    write_node(bp, "prop:a", status="verified", proof="P.", log=log)
    rep = verdict(bp, root)
    check("mk_verified_by_theorist", any("only the user" in e for e in rep.errors), str(rep.errors))

    root, bp = mkrepo(tmp)
    p = write_node(bp, "imp:a", kind="imported", status="checked", proof="P.",
                   log=checked_log(root, "imp:a", "P."))
    rep = verdict(bp, root)
    check("mk_imported_can_reach_checked", rep.verdict == "PASS", str(rep.errors))
    (tmp / "mkparse").mkdir(exist_ok=True)
    p = write_node(tmp / "mkparse", "imp:b", kind="imported", status="formalized",
                   log=[("new", "formalized", "user", "")])
    ok, msg = raises(lambda: bc.parse_node(p))
    check("mk_imported_capped_at_checked", ok and "not allowed" in msg, msg)

    root, bp = mkrepo(tmp)
    claim_at(bp, "prop:a", "checked", uses=["asm:x"])
    write_node(bp, "asm:x", kind="assumption", status="superseded", superseded_by="asm:y",
               log=[("new", "stated", "theorist", ""), ("stated", "superseded", "theorist", "")])
    write_node(bp, "asm:y", kind="assumption")
    rep = verdict(bp, root)
    check("mk_g3_needs_stated_assumption", fails_naming(rep, "prop:a"), str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", status="superseded", superseded_by="prop:zzz",
               log=[("new", "conjecture", "theorist", ""), ("conjecture", "superseded", "theorist", "")])
    rep = verdict(bp, root)
    check("mk_e5_unknown_successor", any("prop:zzz" in e for e in rep.errors), str(rep.errors))

    root, bp = mkrepo(tmp)
    write_node(bp, "prop:z-b")
    write_node(bp, "def:a-b", kind="definition")
    out = bc.render_status(verdict(bp, root))
    check("mk_mermaid_dash_id", "prop_z_b" in out and "def_a_b" in out, out)
    check("mk_render_sorted", out.index("| def:a-b |") < out.index("| prop:z-b |"), out)

    d = tmp / "mkparse"; d.mkdir(exist_ok=True)
    for key in ("kind", "status", "uses", "label"):
        p = write_node(d, f"prop:m-{key}")
        txt = "\n".join(ln for ln in p.read_text(encoding="utf-8").split("\n")
                        if not ln.startswith(f"{key}:"))
        p.write_text(txt, encoding="utf-8")
        ok, msg = raises(lambda: bc.parse_node(p))
        check(f"mk_missing_required_{key}", ok, msg)


def test_final_review_fixes(tmp: Path) -> None:
    """Fixes from the 2026-10-11 whole-branch review."""
    # Important 1: the proof hash covers `uses`, so a checked node cannot be repointed silently.
    root, bp = mkrepo(tmp)
    p = claim_at(bp, "prop:a", "checked", uses=["asm:x"])
    write_node(bp, "asm:x", kind="assumption")
    write_node(bp, "asm:y", kind="assumption")
    rep0 = verdict(bp, root)
    p.write_text(p.read_text(encoding="utf-8").replace("uses: [asm:x]", "uses: [asm:y]"), encoding="utf-8")
    rep = verdict(bp, root)
    check("fr_uses_changed_after_checked", rep0.verdict == "PASS" and fails_naming(rep, "prop:a"),
          f"{rep0.verdict} {rep0.errors} / {rep.errors}")
    check("fr_proof_hash_depends_on_uses",
          bc.proof_hash("P", ["a:b"]) != bc.proof_hash("P", ["a:c"])
          and bc.proof_hash("P", ["a:b", "a:c"]) == bc.proof_hash("P", ["a:c", "a:b"])
          and bc.proof_hash("P") == bc.statement_hash("P"))
    # Re-graded Minor 1: the template's placeholder Score line is not a PASS.
    root, bp = mkrepo(tmp)
    reports = write_reports(root, "prop:a", "P.", verdict="PASS | FAIL | UNVERIFIED")
    write_node(bp, "prop:a", status="checked", proof="P.", log=checked_log(root, "prop:a", "P.", reports))
    rep = verdict(bp, root)
    check("fr_score_placeholder_not_pass", fails_naming(rep, "prop:a"), str(rep.errors))


# --- Task 3: CLI + STATUS.md -----------------------------------------------------

def run_cli(args: list[str]) -> tuple[int, str]:
    import contextlib, io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = bc.main(args)
    return rc, buf.getvalue()


def test_task3(tmp: Path) -> None:
    root, bp = mkrepo(tmp)
    write_node(bp, "def:a", kind="definition")
    write_node(bp, "prop:b", uses=["def:a"])
    rep = bc.check_blueprint(bp, repo_root=root)
    out = bc.render_status(rep)
    check("render_has_table_and_mermaid",
          "| label | kind | status | uses |" in out and "def:a" in out and "prop:b" in out
          and "graph TD" in out and "def_a --> prop_b" in out and "```mermaid" in out, out)

    rc, out = run_cli([str(bp)])
    check("cli_pass_exit_0", rc == 0 and "BLUEPRINT: PASS (2 nodes)" in out, f"{rc} {out}")

    root2, bp2 = mkrepo(tmp)
    write_node(bp2, "prop:a", uses=["def:missing"])
    rc, out = run_cli([str(bp2)])
    check("cli_fail_exit_1", rc == 1 and "BLUEPRINT: FAIL" in out and "def:missing" in out, f"{rc} {out}")

    root3, bp3 = mkrepo(tmp)
    write_node(bp3, "prop:a", log=[("new", "conjecture", "theorist", str(tmp / "outside.txt"))])
    (tmp / "outside.txt").write_text("x", encoding="utf-8")
    rc, out = run_cli([str(bp3)])
    check("cli_unverified_exit_3", rc == 3 and "BLUEPRINT: UNVERIFIED" in out, f"{rc} {out}")

    rc, out = run_cli([])
    check("cli_usage_exit_2", rc == 2, f"{rc} {out}")
    rc, out = run_cli([str(tmp / "nope")])
    check("cli_missing_dir_exit_2", rc == 2, f"{rc} {out}")

    rc, out = run_cli([str(bp), "--write-status"])
    st = bp / "STATUS.md"
    check("cli_write_status", rc == 0 and st.exists() and "graph TD" in st.read_text(encoding="utf-8"),
          f"{rc} {out}")
    rc, out = run_cli([str(bp)])
    check("status_md_not_a_node", rc == 0 and "(2 nodes)" in out, f"{rc} {out}")


def main() -> int:
    global bc
    try:
        bc = load()
    except Exception as e:
        print(f"FAIL  cannot load {MOD.name}: {e!r}")
        return 1
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        for name, fn in sorted(globals().items()):
            if name.startswith("test_") and callable(fn):
                print(name)
                fn(tmp)
    print(f"\n{PASSES} passed, {len(FAILS)} failed")
    if FAILS:
        print("failed: " + ", ".join(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
