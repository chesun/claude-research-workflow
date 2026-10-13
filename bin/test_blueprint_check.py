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
        date = e[6] if len(e) > 6 else "2026-01-15"  # fixed past date
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
    (bp / "checks" / "prop-a").mkdir(parents=True)
    (bp / "checks" / "prop-a" / "s.py").write_text("print('ok')\n", encoding="utf-8")
    rev = root / "quality_reports" / "reviews"
    rev.mkdir(parents=True)
    for r in ("r1.md", "r2.md"):
        (rev / r).write_text("# review\n", encoding="utf-8")
    return root, bp


CHECK = "theory/blueprint/checks/prop-a/s.py"  # the check file for prop:a


def check_loc(root: Path | None, label: str) -> str:
    """Create (if root is given) and return the check-file locator in a node's own folder."""
    rel = f"theory/blueprint/checks/{label.replace(':', '-')}/s.py"
    if root is not None:
        f = root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("print('ok')\n", encoding="utf-8")
    return rel
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


LEAN = "Pkg.Thing"
LEAN_SHA = "ab" * 32


CHECKLIST = ("## Checklist (owner marks)\n\n"
             "| Part | # | Lean clause (verbatim) | Reading (paper symbols) | Mark |\n"
             "|---|---|---|---|---|\n"
             "| (a) | 1 | `0 < s0` | the prior variance is positive | same |\n"
             "| (a) | 2 | `f s0 = 1` | f at the prior variance is 1 | same |\n")


def checklist(*marks: str) -> str:
    """A checklist whose part (a) rows carry `marks`, in order."""
    rows = "".join(f"| (a) | {i} | `c{i}` | clause {i} | {m} |\n" for i, m in enumerate(marks, 1))
    return ("## Checklist (owner marks)\n\n| Part | # | Lean clause (verbatim) | Reading (paper symbols) | Mark |\n"
            "|---|---|---|---|---|\n" + rows)


def write_card_audit(root: Path, label: str, sha: str = LEAN_SHA, verdict: str = "FAITHFUL",
                     coverage: str = "PASS", node: str | None = None, lean: str = LEAN,
                     stamp: str = "2026-10-12", k: int = 1) -> str:
    """A card-auditor report; returns its repo-relative locator."""
    suffix = "" if k == 1 else f"_{k}"
    rel = f"theory/blueprint/checks/{label.replace(':', '-')}/card_audit_{stamp}{suffix}.md"
    f = root / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(f"# Card audit\n**Node:** {node or label}\n**Lean:** {lean}\n**Statement SHA-256:** {sha}\n"
                 f"**Verdict:** {verdict}\n**Coverage:** {coverage}\n\n## Map\n", encoding="utf-8")
    return rel


def write_card(root: Path, label: str, lean: str = LEAN, sha: str = LEAN_SHA, verdict: str = "FAITHFUL",
               signed: str | None = None, node: str | None = None, statement: str = "S",
               node_hash: str | None = None, checklist: str | None = CHECKLIST, audit: str | None = "default",
               override: str | None = None) -> str:
    """A fidelity card; returns its repo-relative locator.

    `signed` defaults to a signature bound to `sha`; `audit="default"` writes a matching audit report,
    None leaves the field out; `checklist=None` leaves the checklist out.
    """
    rel = f"theory/blueprint/cards/{label.replace(':', '-')}.md"
    f = root / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    if signed is None:
        signed = f"CS 2026-10-12 sha:{sha[:12]}"
    if audit == "default":
        audit = write_card_audit(root, label, sha=sha, node=node, lean=lean)
    head = (f"# Card\n**Node:** {node or label}\n"
            f"**Node statement hash:** {node_hash or bc.statement_hash(statement)}\n"
            f"**Lean:** {lean}\n**Statement SHA-256:** {sha}\n")
    if audit is not None:
        head += f"**Independent audit:** {audit}\n"
    head += f"**Verdict:** {verdict}\n**Signed off:** {signed}\n"
    if override is not None:
        head += f"**Audit override:** {override}\n"
    f.write_text(head + "\n" + (checklist or ""), encoding="utf-8")
    return rel


def write_lean_report(root: Path, label: str, mode: str = "full", verdict: str = "PASS", lean: str = LEAN,
                      sha: str = LEAN_SHA, stamp: str = "2026-10-12", k: int = 1,
                      toolchain: str = "Lean (version 4.35.0-rc4, x86_64-w64-windows-gnu, commit c29b6dd, Release)",
                      body: str | None = None) -> str:
    """A lean_check report; returns its repo-relative locator."""
    suffix = "" if k == 1 else f"_{k}"
    rel = f"theory/blueprint/checks/{label.replace(':', '-')}/lean_check_{stamp}{suffix}.md"
    f = root / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    if body is None:
        body = f"- {verdict} — build: lake build --wfail\n"
    f.write_text(f"# lean_check\n**Node:** {label}\n**Lean:** {lean}\n**Statement SHA-256:** {sha}\n"
                 f"**Mode:** {mode}\n**Verdict:** {verdict}\n**Toolchain:** {toolchain}\n**Mathlib:** x\n\n"
                 f"## Checks\n\n{body}", encoding="utf-8")
    return rel


def climb(target: str, root: Path | None = None, label: str | None = None,
          proof: str = PROOF, uses=(), statement: str = "S") -> list[tuple]:
    """A valid evidence log climbing the ladder from new to `target`."""
    reports = write_reports(root, label, proof, uses=uses) if root is not None else PLAIN
    chk = check_loc(root, label) if label else CHECK
    form = verif = ""
    if root is not None and label and target in ("formalized", "verified"):
        card = write_card(root, label, statement=statement)
        form = card + ";" + write_lean_report(root, label, mode="statements")
        verif = card + ";" + write_lean_report(root, label, mode="full", k=2)
    steps = [("new", "conjecture", "theorist", ""),
             ("conjecture", "survived-search", "theorist", chk),
             ("survived-search", "proved", "theorist", ""),
             ("proved", "checked", "proof-verifier", reports),
             ("checked", "formalized", "user", form),
             ("formalized", "verified", "user", verif)]
    out = []
    for s in steps:
        out.append(s)
        if s[1] == target:
            return out
    raise ValueError(target)


def claim_at(bp: Path, label: str, target: str, uses=(), root: Path | None = None, **kw) -> Path:
    kw.setdefault("proof", PROOF if target in ("proved", "checked", "formalized", "verified") else "")
    if target in ("formalized", "verified"):
        kw.setdefault("lean", LEAN)
    if root is None:
        root = bp.parent.parent
    return write_node(bp, label, status=target, uses=uses,
                      log=climb(target, root, label, kw["proof"] or PROOF, uses, kw.get("statement", "S")), **kw)


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
                    ("conjecture", "survived-search", "theorist", "theory\\blueprint\\checks\\prop-a\\s.py:3-5")])
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
    base[1] = base[1][:3] + (check_loc(root, label),)
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
                    ("conjecture", "survived-search", "theorist", "theory/blueprint/checks/prop-a")])
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
    try:
        os.link(root / one, root / "quality_reports" / "reviews" / "linked_review.md")
        have_links = True
    except (OSError, NotImplementedError, AttributeError):
        have_links = False  # filesystem without hard links: skip rather than crash the suite
    write_node(bp, "prop:a", status="checked", proof="P.",
               log=checked_log(root, "prop:a", "P.", f"{one};quality_reports/reviews/linked_review.md"))
    rep = verdict(bp, root)
    if have_links:
        check("rt_hardlink_not_distinct", fails_naming(rep, "prop:a"), str(rep.errors))
    else:
        check("rt_hardlink_not_distinct (skipped: no hard links on this filesystem)", True)

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
    (nr / "checks" / "prop-a").mkdir(parents=True)
    (nr / "checks" / "prop-a" / "s.py").write_text("x\n", encoding="utf-8")
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


def test_deferred_minors(tmp: Path) -> None:
    """Deferred minors from the whole-branch review, fixed before merge."""
    # Minor 7: a check file must sit in the node's own checks/<label>/ folder.
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:b", status="survived-search",
               log=[("new", "conjecture", "theorist", ""),
                    ("conjecture", "survived-search", "theorist", CHECK)])  # prop:a's folder
    rep = verdict(bp, root)
    check("dm_check_file_in_own_folder", fails_naming(rep, "prop:b"), str(rep.errors))
    # Minor 8: verifier reports count only from quality_reports/reviews/.
    root, bp = mkrepo(tmp)
    locs = write_reports(root, "prop:a", "P.")
    moved = []
    for i, loc in enumerate(locs.split(";")):
        dst = root / "theory" / "blueprint" / "checks" / "prop-a" / f"r{i}.md"
        dst.write_text((root / loc).read_text(encoding="utf-8"), encoding="utf-8")
        moved.append(f"theory/blueprint/checks/prop-a/r{i}.md")
    write_node(bp, "prop:a", status="checked", proof="P.",
               log=checked_log(root, "prop:a", "P.", ";".join(moved)))
    rep = verdict(bp, root)
    check("dm_reports_only_from_reviews", fails_naming(rep, "prop:a"), str(rep.errors))
    # Minor 9: a future date is flagged (UNVERIFIED), not silently accepted.
    root, bp = mkrepo(tmp)
    write_node(bp, "prop:a", log=[("new", "conjecture", "theorist", "", "", None, "2099-01-01")])
    rep = verdict(bp, root)
    check("dm_future_date_warns", rep.verdict == "UNVERIFIED" and not rep.errors
          and any("future" in w for w in rep.warnings), f"{rep.verdict} {rep.errors} {rep.warnings}")


def test_phase2_cited_labels(tmp: Path) -> None:
    """Phase 2 prep: a proof that cites a node missing from `uses` is flagged (lem:band, 2026-10-11)."""
    def setup(proof: str, uses=("def:x",), status: str = "proved"):
        root, bp = mkrepo(tmp)
        write_node(bp, "def:x", kind="definition")
        write_node(bp, "lem:b")
        write_node(bp, "lem:b-two")
        claim_at(bp, "prop:a", status, uses=list(uses), root=root, proof=proof)
        return verdict(bp, root)

    rep = setup("By lem:b and def:x, done.")
    check("cl_cited_not_in_uses_warns",
          rep.verdict == "UNVERIFIED" and not rep.errors
          and any("prop:a" in w and "lem:b" in w and "uses" in w for w in rep.warnings),
          f"{rep.verdict} {rep.errors} {rep.warnings}")
    rep = setup("By `lem:b`, done.", uses=("def:x", "lem:b"), status="survived-search")
    check("cl_cited_in_uses_silent", rep.verdict == "PASS", f"{rep.verdict} {rep.errors} {rep.warnings}")
    rep = setup("As prop:a claims; see foo:bar and https://example.org.")
    check("cl_self_and_unknown_tokens_ignored", rep.verdict == "PASS", f"{rep.verdict} {rep.warnings}")
    rep = setup("Apply lem:b-two.")
    check("cl_longest_label_wins",
          any("cites lem:b-two," in w for w in rep.warnings) and not any("cites lem:b," in w for w in rep.warnings),
          str(rep.warnings))
    rep = setup("Apply lem:b-two.", uses=("def:x", "lem:b-two"), status="survived-search")
    check("cl_prefix_label_not_matched", rep.verdict == "PASS", f"{rep.verdict} {rep.warnings}")
    rep = setup("Done by lem:b's bound.")
    check("cl_possessive_and_punctuation", any("lem:b" in w for w in rep.warnings), str(rep.warnings))
    rep = setup("By lem:b: the bound holds.")
    check("cl_label_before_colon", any("cites lem:b," in w for w in rep.warnings), str(rep.warnings))
    rep = setup("Done. <!-- compare lem:b -->")
    check("cl_comment_ignored", rep.verdict == "PASS", f"{rep.verdict} {rep.warnings}")
    root, bp = mkrepo(tmp)
    write_node(bp, "lem:b")
    write_node(bp, "prop:a", status="refuted", proof="Uses lem:b.",
               log=[("new", "conjecture", "theorist", ""), ("conjecture", "refuted", "theorist", CHECK)])
    rep = verdict(bp, root)
    check("cl_terminal_node_skipped", rep.verdict == "PASS", f"{rep.verdict} {rep.errors} {rep.warnings}")
    # A declared mention (named, not depended on) is silent and leaves both hashes unchanged.
    root, bp = mkrepo(tmp)
    write_node(bp, "def:x", kind="definition")
    write_node(bp, "lem:b")
    write_node(bp, "lem:c")
    p = claim_at(bp, "prop:a", "proved", uses=["def:x"], root=root,
                 proof="lem:b is not used here; nor is lem:c.",
                 raw_prefix="")
    before = bc.parse_node(p)
    txt = p.read_text(encoding="utf-8").replace("---\n## Statement", "---\n<!-- mentions: lem:b -->\n## Statement", 1)
    p.write_text(txt, encoding="utf-8")
    after = bc.parse_node(p)
    rep = verdict(bp, root)
    check("cl_mention_declared_silent",
          after.mentions == ["lem:b"] and not any("cites lem:b," in w for w in rep.warnings)
          and any("cites lem:c," in w for w in rep.warnings), f"{after.mentions} {rep.warnings}")
    check("cl_mention_keeps_hashes",
          (bc.statement_hash(before.statement), bc.proof_hash(before.proof, before.uses))
          == (bc.statement_hash(after.statement), bc.proof_hash(after.proof, after.uses)))
    txt = txt.replace("<!-- mentions: lem:b -->", "<!--\n  mentions: lem:b,\n  lem:c\n-->")
    p.write_text(txt, encoding="utf-8")
    check("cl_mentions_multiline", bc.parse_node(p).mentions == ["lem:b", "lem:c"]
          and verdict(bp, root).verdict == "PASS", str(bc.parse_node(p).mentions))
    p.write_text(txt.replace("lem:c\n-->", "Lem C\n-->"), encoding="utf-8")
    ok, msg = raises(lambda: bc.parse_node(p))
    check("cl_mentions_bad_label_rejected", ok and "mentions" in msg, msg)
    check("cl_cited_labels_helper",
          bc.cited_labels("x lem:b, lem:b-two; (def:x) <!-- asm:z --> Xlem:q x-lem:r a::lem:t _lem:s_") == {"lem:b", "lem:b-two", "def:x", "lem:s"},
          str(bc.cited_labels("x lem:b, lem:b-two; (def:x) <!-- asm:z --> Xlem:q x-lem:r a::lem:t _lem:s_")))


def test_phase2_review_fixes(tmp: Path) -> None:
    """Fixes from the 2026-10-12 red-team and correctness reviews of the phase-2 tools."""
    # High: a statement that names a node missing from `uses` is flagged like a proof citation.
    root, bp = mkrepo(tmp)
    write_node(bp, "asm:zz-sentinel", kind="assumption", statement="The sentinel assumption holds.")
    claim_at(bp, "prop:a", "proved", uses=[], root=root, statement="Under asm:zz-sentinel, V is concave.",
             proof="Immediate.")
    rep = verdict(bp, root)
    check("rf_statement_citation_warns",
          any("prop:a" in w and "statement cites asm:zz-sentinel," in w for w in rep.warnings),
          f"{rep.verdict} {rep.warnings}")
    # Low: a mention that is the node itself or names no node is reported.
    root, bp = mkrepo(tmp)
    p = write_node(bp, "prop:a")
    p.write_text(p.read_text(encoding="utf-8").replace("---\n## Statement",
                 "---\n<!-- mentions: prop:a, lem:zz-nope -->\n## Statement", 1), encoding="utf-8")
    rep = verdict(bp, root)
    check("rf_mention_self_and_unknown_warn",
          any("mentions itself" in w for w in rep.warnings)
          and any("lem:zz-nope" in w and "no such node" in w for w in rep.warnings), str(rep.warnings))


def test_phase2_lean_rules(tmp: Path) -> None:
    """Phase 2 (Lean lane): `formalized` needs a signed card + statements report; `verified` adds a full report."""
    def node_at(target: str, form=None, verif=None, lean=LEAN):
        root, bp = mkrepo(tmp)
        log = climb(target, root, "prop:a", PROOF)
        if form is not None:
            i = next(k for k, e in enumerate(log) if e[1] == "formalized")
            log[i] = log[i][:3] + (form(root),)
        if verif is not None:
            i = next(k for k, e in enumerate(log) if e[1] == "verified")
            log[i] = log[i][:3] + (verif(root),)
        write_node(bp, "prop:a", status=target, proof=PROOF, log=log, lean=lean or "")
        return root, bp, verdict(bp, root)

    _, _, rep = node_at("formalized")
    check("ln_formalized_valid", rep.verdict == "PASS", f"{rep.verdict} {rep.errors} {rep.warnings}")
    _, _, rep = node_at("verified")
    check("ln_verified_valid", rep.verdict == "PASS", f"{rep.verdict} {rep.errors} {rep.warnings}")

    def card_then_report(**card_kw):
        return lambda root: write_card(root, "prop:a", **card_kw) + ";" + write_lean_report(root, "prop:a", mode="statements")
    for name, kw in (("pending", dict(signed="PENDING")), ("unfaithful", dict(verdict="UNFAITHFUL")),
                     ("verdict_pending", dict(verdict="PENDING")), ("other_node", dict(node="prop:b")),
                     ("lean_mismatch", dict(lean="Pkg.Other"))):
        _, _, rep = node_at("formalized", form=card_then_report(**kw))
        check(f"ln_formalized_rejects_{name}", fails_naming(rep, "prop:a"), str(rep.errors))
    _, _, rep = node_at("formalized", form=lambda root: write_card(root, "prop:a"))
    check("ln_formalized_needs_statements_report", fails_naming(rep, "prop:a"), str(rep.errors))
    _, _, rep = node_at("formalized", form=lambda root: write_card(root, "prop:a") + ";"
                        + write_lean_report(root, "prop:a", mode="statements", verdict="FAIL"))
    check("ln_formalized_rejects_failed_report", fails_naming(rep, "prop:a"), str(rep.errors))
    _, _, rep = node_at("formalized", form=lambda root: write_card(root, "prop:a") + ";"
                        + write_lean_report(root, "prop:a", mode="statements", sha="cd" * 32))
    check("ln_formalized_rejects_hash_mismatch", fails_naming(rep, "prop:a"), str(rep.errors))
    _, _, rep = node_at("formalized", form=lambda root: write_lean_report(root, "prop:a", mode="statements"))
    check("ln_formalized_needs_card", fails_naming(rep, "prop:a"), str(rep.errors))
    _, _, rep = node_at("formalized", lean=None)
    check("ln_formalized_needs_lean_header", fails_naming(rep, "prop:a") and any("lean" in e for e in rep.errors),
          str(rep.errors))

    _, _, rep = node_at("verified", verif=lambda root: write_card(root, "prop:a") + ";"
                        + write_lean_report(root, "prop:a", mode="full", verdict="UNVERIFIED", k=2))
    check("ln_verified_rejects_unverified_report", fails_naming(rep, "prop:a"), str(rep.errors))
    _, _, rep = node_at("verified", verif=lambda root: write_card(root, "prop:a") + ";"
                        + write_lean_report(root, "prop:a", mode="statements", k=2))
    check("ln_verified_needs_full_mode", fails_naming(rep, "prop:a"), str(rep.errors))
    _, _, rep = node_at("verified", verif=lambda root: write_card(root, "prop:a") + ";"
                        + write_lean_report(root, "prop:a", mode="full", sha="cd" * 32, k=2))
    check("bc_verified_hash_mismatch_fails", fails_naming(rep, "prop:a"), str(rep.errors))
    root, bp, rep = node_at("verified")
    write_lean_report(root, "prop:a", mode="full", verdict="FAIL", stamp="2026-10-13")
    rep = verdict(bp, root)
    check("bc_newest_report_wins", fails_naming(rep, "prop:a") and any("newest" in e for e in rep.errors),
          str(rep.errors))
    root, bp, rep = node_at("verified")
    write_lean_report(root, "prop:a", mode="statements", verdict="FAIL", stamp="2026-10-13")
    rep = verdict(bp, root)
    check("bc_newest_full_report_only", rep.verdict == "PASS", f"{rep.errors}")

    # Review round 1 (2026-10-12) fixes.
    _, _, rep = node_at("verified", verif=lambda root: write_card(root, "prop:a") + ";"
                        + write_lean_report(root, "prop:a", mode="full", k=2, toolchain="(not run)"))
    check("ln_hollow_report_no_toolchain", fails_naming(rep, "prop:a"), str(rep.errors))
    _, _, rep = node_at("verified", verif=lambda root: write_card(root, "prop:a") + ";"
                        + write_lean_report(root, "prop:a", mode="full", k=2,
                                            body="- PASS — build: ok\n- UNVERIFIED — leanchecker: skipped\n"))
    check("ln_hollow_report_unverified_line", fails_naming(rep, "prop:a"), str(rep.errors))
    for name, signed in (("tbd", "TBD"), ("dash", "-"), ("no_date", "CS")):
        _, _, rep = node_at("formalized", form=lambda root, s=signed: write_card(root, "prop:a", signed=s) + ";"
                            + write_lean_report(root, "prop:a", mode="statements"))
        check(f"ln_signed_off_{name}_rejected", fails_naming(rep, "prop:a"), str(rep.errors))
    _, _, rep = node_at("formalized", form=lambda root: write_card(root, "prop:a", node_hash="0" * 12) + ";"
                        + write_lean_report(root, "prop:a", mode="statements"))
    check("ln_card_node_statement_hash_checked", fails_naming(rep, "prop:a"), str(rep.errors))
    root, bp, rep = node_at("verified")
    write_lean_report(root, "prop:a", mode="full", verdict="UNVERIFIED", stamp="2026-10-13",
                      body="- UNVERIFIED — leanchecker: not available\n")
    rep = verdict(bp, root)
    check("ln_newest_unverified_is_warning", rep.verdict == "UNVERIFIED" and not rep.errors
          and any("newest" in w for w in rep.warnings), f"{rep.verdict} {rep.errors} {rep.warnings}")
    root, bp, rep = node_at("verified")
    write_lean_report(root, "prop:a", mode="full", verdict="FAIL", stamp="2026-10-13", k=1)
    (root / "theory/blueprint/checks/prop-a/lean_check_2026-10-13.md").rename(
        root / "theory/blueprint/checks/prop-a/lean_check_2026-10-13_1.md")
    rep = verdict(bp, root)
    check("ln_suffix_1_ignored", rep.verdict == "PASS", f"{rep.errors}")
    root, bp, rep = node_at("verified")
    write_lean_report(root, "prop:a", mode="full", verdict="FAIL", stamp="2026-10-12", k=3)
    rep = verdict(bp, root)
    check("ln_same_date_counter_ordering", fails_naming(rep, "prop:a"), str(rep.errors))

    # ADR-0005: bound signature, checklist marks, independent audit.
    def form_with(**card_kw):
        return lambda root: (write_card(root, "prop:a", **card_kw) + ";"
                             + write_lean_report(root, "prop:a", mode="statements"))

    def errs(rep):
        return " | ".join(rep.errors)
    good_override = f"CS 2026-10-12 sha:{LEAN_SHA[:12]}: owner accepts the auditor's note"
    _, _, rep = node_at("formalized", form=form_with(signed="CS 2026-10-12"))
    check("ln_signed_without_sha_rejected", fails_naming(rep, "prop:a"), errs(rep))
    check("ln_old_format_card_message", "re-sign" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=form_with(signed="CS 2026-10-12 sha:cdcdcdcdcdcd"))
    check("ln_signed_wrong_prefix_rejected", fails_naming(rep, "prop:a") and "re-signs" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=form_with(signed="CS  2026-10-12  sha:" + LEAN_SHA[:12].upper()))
    check("ln_signed_prefix_case_and_spaces", rep.verdict == "PASS", errs(rep))
    _, _, rep = node_at("formalized", form=form_with(checklist=None))
    check("ln_checklist_missing_rejected", fails_naming(rep, "prop:a") and "checklist" in errs(rep).lower(),
          errs(rep))
    _, _, rep = node_at("formalized", form=form_with(checklist=checklist("same", "smae")))
    check("ln_checklist_bad_mark_named", fails_naming(rep, "prop:a") and "line 2" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=form_with(checklist=checklist("same", "")))
    check("ln_checklist_empty_mark_named", fails_naming(rep, "prop:a") and "line 2" in errs(rep), errs(rep))

    def crlf_bom(root):
        loc = form_with()(root)
        card = root / loc.split(";")[0]
        card.write_bytes(b"\xef\xbb\xbf" + card.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8"))
        return loc
    _, _, rep = node_at("formalized", form=crlf_bom)
    check("ln_checklist_crlf_bom", rep.verdict == "PASS", errs(rep))
    _, _, rep = node_at("formalized", form=form_with(checklist=checklist("same", "weaker")))
    check("ln_faithful_needs_all_same", fails_naming(rep, "prop:a") and "same" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=form_with(checklist=checklist("same", "Weaker"),
                                                      verdict="WITH-NOTED-DIFFERENCES"))
    check("ln_noted_differences_allows_other_marks", rep.verdict == "PASS", errs(rep))
    _, _, rep = node_at("formalized", form=form_with(audit=None))
    check("ln_audit_missing_rejected", fails_naming(rep, "prop:a") and "audit" in errs(rep).lower(), errs(rep))
    _, _, rep = node_at("formalized", form=lambda root: form_with(
        audit=write_card_audit(root, "prop:b", node="prop:a"))(root))
    check("ln_audit_wrong_place_other_node", fails_naming(rep, "prop:a") and "checks/prop-a/" in errs(rep), errs(rep))

    def audit_in_cards(root):
        src = root / write_card_audit(root, "prop:a")
        dst = root / "theory/blueprint/cards/card_audit_2026-10-12.md"
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        src.unlink()
        return form_with(audit="theory/blueprint/cards/card_audit_2026-10-12.md")(root)
    _, _, rep = node_at("formalized", form=audit_in_cards)
    check("ln_audit_wrong_place_cards", fails_naming(rep, "prop:a") and "checks/prop-a/" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=lambda root: form_with(
        audit=write_card_audit(root, "prop:a", sha="cd" * 32))(root))
    check("ln_audit_sha_mismatch_rejected", fails_naming(rep, "prop:a") and "has Statement SHA-256" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=lambda root: form_with(
        audit=write_card_audit(root, "prop:a", coverage="FAIL"))(root))
    check("ln_audit_coverage_fail_rejected", fails_naming(rep, "prop:a") and "Coverage" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=lambda root: form_with(
        audit=write_card_audit(root, "prop:a", coverage="FAIL"), override=good_override)(root))
    check("ln_audit_coverage_fail_not_overridable", fails_naming(rep, "prop:a") and "Coverage" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=lambda root: form_with(
        audit=write_card_audit(root, "prop:a", verdict="UNFAITHFUL"))(root))
    check("ln_audit_unfaithful_rejected", fails_naming(rep, "prop:a") and "audit verdict" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=lambda root: form_with(
        audit=write_card_audit(root, "prop:a", verdict="UNFAITHFUL"), override=good_override)(root))
    check("ln_audit_unfaithful_with_override_passes", rep.verdict == "PASS", errs(rep))
    _, _, rep = node_at("formalized", form=lambda root: form_with(
        audit=write_card_audit(root, "prop:a", verdict="UNFAITHFUL"),
        override="CS 2026-10-12 sha:cdcdcdcdcdcd: owner accepts")(root))
    check("ln_override_wrong_prefix_rejected", fails_naming(rep, "prop:a") and "Audit override is bound" in errs(rep), errs(rep))
    _, _, rep = node_at("verified", verif=lambda root: write_card(root, "prop:a", audit=None) + ";"
                        + write_lean_report(root, "prop:a", mode="full", k=2))
    check("ln_verified_replays_card_rules", fails_naming(rep, "prop:a") and "audit" in errs(rep).lower(),
          errs(rep))
    # Review fixes (2026-10-14 red-team and correctness reviews of the ADR-0005 rules).
    def _append(loc, root, extra):
        card = root / loc.split(";")[0]
        card.write_text(card.read_text(encoding="utf-8") + extra, encoding="utf-8")
        return loc
    rows_ok = "| (a) | 1 | `c1` | clause 1 | same |\n"
    head = ("## Checklist (owner marks)\n\n| Part | # | Lean clause (verbatim) | Reading (paper symbols) | Mark |\n"
            "|---|---|---|---|---|\n")
    weak = "| (b) | 1 | `c2` | clause 2 | weaker |\n"
    _, _, rep = node_at("formalized", form=form_with(checklist="<!--\n" + head + rows_ok + "-->\n\n" + head + weak))
    check("rv_checklist_in_comment_ignored", fails_naming(rep, "prop:a") and "weaker" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=form_with(checklist="```\n" + head + rows_ok + "```\n\n" + head + weak))
    check("rv_checklist_in_fence_ignored", fails_naming(rep, "prop:a") and "weaker" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=form_with(
        checklist=head + rows_ok + "\n### Part (b)\n\n| Part | # | Lean clause | Reading | Mark |\n|---|---|---|---|---|\n"
        + weak))
    check("rv_subheading_does_not_end_checklist", fails_naming(rep, "prop:a") and "weaker" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=form_with(checklist=head + rows_ok + "\n" + head + weak))
    check("rv_second_checklist_rejected", fails_naming(rep, "prop:a") and "Checklist" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=lambda root: _append(form_with()(root), root,
                                                                "\n**Signed off:** PENDING\n"))
    check("rv_duplicate_card_field_rejected", fails_naming(rep, "prop:a") and "Signed off" in errs(rep)
          and "more than once" in errs(rep), errs(rep))

    def dup_audit(root):
        loc = write_card_audit(root, "prop:a")
        (root / loc).write_text((root / loc).read_text(encoding="utf-8") + "**Verdict:** UNFAITHFUL\n",
                                encoding="utf-8")
        return form_with(audit=loc)(root)
    _, _, rep = node_at("formalized", form=dup_audit)
    check("rv_duplicate_audit_field_rejected", fails_naming(rep, "prop:a") and "more than once" in errs(rep),
          errs(rep))
    _, _, rep = node_at("formalized", form=form_with(checklist=head + rows_ok + "\n**Glossary**\n\n"
                                                      "| Lean | Means |\n|---|---|\n| `s0` | prior variance |\n"))
    check("rv_later_table_not_checklist", rep.verdict == "PASS", errs(rep))
    def older_audit_cited(root):
        old = write_card_audit(root, "prop:a")
        write_card_audit(root, "prop:a", verdict="UNFAITHFUL", k=2)
        return form_with(audit=old)(root)
    _, _, rep = node_at("formalized", form=older_audit_cited)
    check("rv_newer_audit_wins", fails_naming(rep, "prop:a") and "newer" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=form_with(checklist=head + rows_ok + "| | | | | |\n"))
    check("rv_empty_row_flagged", fails_naming(rep, "prop:a") and "mark" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=form_with(signed=f"CS ２０２６-10-12 sha:{LEAN_SHA[:12]}"))
    check("rv_signature_ascii_digits_only", fails_naming(rep, "prop:a"), errs(rep))
    _, _, rep = node_at("formalized", form=form_with(checklist=checklist("same", "wekaer"),
                                                      verdict="WITH-NOTED-DIFFERENCES"))
    check("rv_mark_vocabulary_enforced", fails_naming(rep, "prop:a") and "wekaer" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=lambda root: form_with(
        audit=write_card_audit(root, "prop:a", node="prop:b"))(root))
    check("rv_audit_node_checked", fails_naming(rep, "prop:a") and "has Node" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=lambda root: form_with(
        audit=write_card_audit(root, "prop:a", lean="Pkg.Other"))(root))
    check("rv_audit_lean_checked", fails_naming(rep, "prop:a") and "has Lean" in errs(rep), errs(rep))

    def audit_bad_name(root):
        src = root / write_card_audit(root, "prop:a")
        dst = src.with_name("audit.md")
        src.rename(dst)
        return form_with(audit="theory/blueprint/checks/prop-a/audit.md")(root)
    _, _, rep = node_at("formalized", form=audit_bad_name)
    check("rv_audit_filename_checked", fails_naming(rep, "prop:a") and "card_audit_" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=form_with(checklist=head))
    check("rv_checklist_no_rows_rejected", fails_naming(rep, "prop:a") and "no rows" in errs(rep), errs(rep))
    _, _, rep = node_at("formalized", form=lambda root: form_with(
        audit=write_card_audit(root, "prop:a", coverage="PENDING"))(root))
    check("rv_coverage_pending_message", fails_naming(rep, "prop:a") and "step 2" in errs(rep)
          and "missing" not in errs(rep), errs(rep))
    check("ln_checklist_helper_skips_header",
          bc.checklist_problem(CHECKLIST) is None and bc.checklist_problem("# no checklist\n") is not None,
          str(bc.checklist_problem(CHECKLIST)))


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
