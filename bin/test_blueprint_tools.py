#!/usr/bin/env python3
"""Tests for bin/blueprint_tools.py (verify-input, dependents, repoint).

Same plain check() style as bin/test_blueprint_check.py, whose fixture helpers
it reuses. Run:
    python3 bin/test_blueprint_tools.py      # exit 0 = all pass
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
from datetime import date
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


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


bc = bt = fx = None  # set in main()


def run_cli(args: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = bt.main(args)
    return rc, buf.getvalue()


def node_file(bp: Path, label: str) -> Path:
    return bp / bc.label_to_filename(label)


# --- verify-input ------------------------------------------------------------------

def ready_blueprint(tmp: Path):
    """prop:a proved on def:x (stated) and lem:b (checked)."""
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "def:x", kind="definition", statement="Let x be <!-- secret motive --> real.")
    fx.claim_at(bp, "lem:b", "checked", root=root, statement="b holds.", proof="Short.")
    p = fx.claim_at(bp, "prop:a", "proved", uses=["def:x", "lem:b"], root=root,
                    statement="a holds.", proof="By lem:b and def:x. <!-- the paper wants this -->",
                    paper_ref="paper.tex:99")
    return root, bp, p


def test_verify_input(tmp: Path) -> None:
    root, bp, p = ready_blueprint(tmp)
    problems, text = bt.verify_input(p)
    n = bc.parse_node(p)
    h = bc.proof_hash(n.proof, n.uses)
    check("vi_ready_no_problems", problems == [], str(problems))
    check("vi_has_statement_proof_uses_hash",
          "a holds." in text and "By lem:b and def:x." in text and "b holds." in text
          and "**lem:b (claim).**" in text and "**def:x (definition).**" in text
          and f"**Proof:** {h}" in text and "**Target:** prop:a" in text, text)
    check("vi_blind_no_log_paper_or_comments",
          "paper.tex" not in text and "stmt:" not in text and "secret motive" not in text
          and "paper wants" not in text and "Evidence log" not in text and "<!--" not in text, text)

    rc, out = run_cli(["verify-input", str(p)])
    check("vi_cli_prints_input_exit_0", rc == 0 and "a holds." in out, f"{rc} {out}")
    dest = bp.parent / "vi.md"
    rc, out = run_cli(["verify-input", str(p), "--out", str(dest)])
    check("vi_cli_out_file", rc == 0 and dest.is_file()
          and b"\r\n" not in dest.read_bytes() and "a holds." in dest.read_text(encoding="utf-8"),
          f"{rc} {out}")

    # Not ready: the node itself is not at `proved`.
    root, bp = fx.mkrepo(tmp)
    p = fx.claim_at(bp, "prop:a", "survived-search", root=root)
    problems, _ = bt.verify_input(p)
    check("vi_refuses_unproved", any("proved" in x for x in problems), str(problems))
    # Not ready: a claim dependency below checked.
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "lem:b")
    p = fx.claim_at(bp, "prop:a", "proved", uses=["lem:b"], root=root)
    problems, _ = bt.verify_input(p)
    check("vi_refuses_unchecked_dependency", any("lem:b" in x and "conjecture" in x for x in problems),
          str(problems))
    rc, out = run_cli(["verify-input", str(p)])
    check("vi_cli_not_ready_exit_1_no_input", rc == 1 and "lem:b" in out and "Proof submitted" not in out,
          f"{rc} {out}")
    # Not ready: a uses label with no node.
    root, bp = fx.mkrepo(tmp)
    p = fx.claim_at(bp, "prop:a", "proved", uses=["def:gone"], root=root)
    problems, _ = bt.verify_input(p)
    check("vi_refuses_missing_dependency", any("def:gone" in x for x in problems), str(problems))
    # Not ready: the proof cites a node missing from uses (the lem:band defect).
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "def:x", kind="definition")
    p = fx.claim_at(bp, "prop:a", "proved", root=root, proof="By def:x.")
    problems, _ = bt.verify_input(p)
    check("vi_refuses_cited_not_in_uses", any("def:x" in x and "uses" in x for x in problems), str(problems))
    # ...unless it is a declared mention.
    txt = p.read_text(encoding="utf-8").replace("---\n## Statement", "---\n<!-- mentions: def:x -->\n## Statement", 1)
    p.write_text(txt, encoding="utf-8")
    problems, text = bt.verify_input(p)
    check("vi_declared_mention_ok", problems == [] and "mentions" not in text, f"{problems} {text}")
    # A deprecated dependency: superseded definitions are not ready.
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "def:new", kind="definition")
    fx.write_node(bp, "def:old", kind="definition", status="superseded", superseded_by="def:new",
                  log=[("new", "stated", "theorist", ""), ("stated", "superseded", "theorist", "")])
    p = fx.claim_at(bp, "prop:a", "proved", uses=["def:old"], root=root)
    problems, _ = bt.verify_input(p)
    check("vi_refuses_superseded_base", any("def:old" in x for x in problems), str(problems))

    rc, out = run_cli(["verify-input"])
    check("vi_cli_usage_exit_2", rc == 2, f"{rc} {out}")
    rc, out = run_cli(["verify-input", str(tmp / "nope.md")])
    check("vi_cli_missing_file_exit_2", rc == 2, f"{rc} {out}")


# --- dependents + repoint -------------------------------------------------------------

def repoint_blueprint(tmp: Path):
    """lem:old superseded by lem:new; dependents at several statuses."""
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "def:x", kind="definition")
    fx.claim_at(bp, "lem:new", "checked", root=root, statement="new lemma", proof="P new.")
    fx.write_node(bp, "lem:old", status="superseded", superseded_by="lem:new", statement="old lemma",
                  log=[("new", "conjecture", "theorist", ""),
                       ("conjecture", "superseded", "theorist", "")])
    fx.write_node(bp, "prop:c", uses=["lem:old", "def:x"], statement="c")                  # conjecture
    fx.claim_at(bp, "prop:p", "proved", uses=["def:x", "lem:old"], root=root,
                statement="p", proof="By lem:old.")
    fx.claim_at(bp, "prop:k", "checked", uses=["lem:old"], root=root, statement="k", proof="K.")
    fx.claim_at(bp, "prop:both", "survived-search", uses=["lem:old", "lem:new"], root=root, statement="both")
    fx.write_node(bp, "var:r", kind="variant", status="refuted", uses=["lem:old"], statement="r",
                  log=[("new", "conjecture", "theorist", ""),
                       ("conjecture", "refuted", "theorist", fx.CHECK)])
    fx.write_node(bp, "prop:named", uses=["def:x"], statement="n", proof="Unlike lem:old, ...")
    return root, bp


def test_dependents(tmp: Path) -> None:
    root, bp = repoint_blueprint(tmp)
    deps = bt.dependents(bp, "lem:old")
    got = {(d.label, how) for d, how in deps}
    check("dep_lists_uses_and_cites",
          got == {("prop:c", "uses"), ("prop:p", "uses"), ("prop:k", "uses"), ("prop:both", "uses"),
                  ("var:r", "uses"), ("prop:named", "cites")}, str(got))
    rc, out = run_cli(["dependents", str(node_file(bp, "lem:old"))])
    check("dep_cli", rc == 0 and "prop:k" in out and "checked" in out and "prop:named" in out
          and "var:r" in out and "terminal" in out, f"{rc} {out}")


def test_repoint(tmp: Path) -> None:
    root, bp = repoint_blueprint(tmp)
    before = {f.name: f.read_bytes() for f in bp.glob("*.md")}
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old"))])
    check("rp_dry_run_writes_nothing",
          rc == 0 and before == {f.name: f.read_bytes() for f in bp.glob("*.md")}
          and "prop:k" in out and "dry run" in out.lower(), f"{rc} {out}")

    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old")), "--apply"])
    n = {L: bc.parse_node(node_file(bp, L)) for L in ("prop:c", "prop:p", "prop:k", "prop:both", "var:r")}
    check("rp_conjecture_uses_rewritten_in_place",
          n["prop:c"].uses == ["lem:new", "def:x"] and n["prop:c"].status == "conjecture"
          and len(n["prop:c"].log) == 1, f"{n['prop:c'].uses} {n['prop:c'].status}")
    check("rp_proved_demoted_with_log",
          n["prop:p"].uses == ["def:x", "lem:new"] and n["prop:p"].status == "survived-search"
          and n["prop:p"].log[-1].frm == "proved" and n["prop:p"].log[-1].to == "survived-search"
          and n["prop:p"].log[-1].date == date.today().isoformat()
          and n["prop:p"].log[-1].proof_hash is None, str(n["prop:p"].log[-1]))
    check("rp_checked_demoted", n["prop:k"].status == "survived-search" and n["prop:k"].uses == ["lem:new"],
          f"{n['prop:k'].status} {n['prop:k'].uses}")
    check("rp_dedupes_existing_successor", n["prop:both"].uses == ["lem:new"], str(n["prop:both"].uses))
    check("rp_terminal_untouched", n["var:r"].uses == ["lem:old"], str(n["var:r"].uses))
    check("rp_proof_prose_untouched", n["prop:p"].proof == "By lem:old.", n["prop:p"].proof)
    rep = bc.check_blueprint(bp, repo_root=root)
    check("rp_result_validates_no_errors",
          not rep.errors and any("prop:p" in w and "cites lem:old" in w for w in rep.warnings),
          f"{rep.verdict} {rep.errors} {rep.warnings}")
    check("rp_cli_reports_validator_verdict", rc == 0 and "BLUEPRINT:" in out, f"{rc} {out}")

    # CRLF files keep their line endings.
    root, bp = repoint_blueprint(tmp)
    f = node_file(bp, "prop:c")
    f.write_bytes(f.read_bytes().replace(b"\n", b"\r\n"))
    bt.repoint(node_file(bp, "lem:old"), apply=True)
    raw = f.read_bytes()
    check("rp_keeps_crlf", b"\r\n" in raw and b"\n" not in raw.replace(b"\r\n", b""), repr(raw[:80]))

    # Refusals: the node is not conditional/superseded; the repoint would create a cycle.
    root, bp = repoint_blueprint(tmp)
    rc, out = run_cli(["repoint", str(node_file(bp, "prop:c"))])
    check("rp_refuses_live_node", rc == 1 and "superseded" in out, f"{rc} {out}")
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "lem:new", uses=["prop:d"], statement="new")
    fx.write_node(bp, "lem:old", status="superseded", superseded_by="lem:new", statement="old",
                  log=[("new", "conjecture", "theorist", ""), ("conjecture", "superseded", "theorist", "")])
    fx.write_node(bp, "prop:d", uses=["lem:old"], statement="d")
    before = {f.name: f.read_bytes() for f in bp.glob("*.md")}
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old")), "--apply"])
    check("rp_refuses_cycle", rc == 1 and "cycle" in out
          and before == {f.name: f.read_bytes() for f in bp.glob("*.md")}, f"{rc} {out}")
    # A statement that names the old node cannot be rewritten; it is reported.
    root, bp = repoint_blueprint(tmp)
    fx.write_node(bp, "prop:s", uses=["lem:old"], statement="Under lem:old, s.")
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old")), "--apply"])
    check("rp_reports_statement_mention", "prop:s" in out and "statement" in out.lower()
          and bc.parse_node(node_file(bp, "prop:s")).uses == ["lem:new"], f"{rc} {out}")
    rc, out = run_cli(["repoint"])
    check("rp_cli_usage_exit_2", rc == 2, f"{rc} {out}")


def retired(bp: Path, label: str, successor: str, statement: str = "old") -> Path:
    return fx.write_node(bp, label, status="superseded", superseded_by=successor, statement=statement,
                         log=[("new", "conjecture", "theorist", ""), ("conjecture", "superseded", "theorist", "")])


def test_review_fixes_verify_input(tmp: Path) -> None:
    """2026-10-12 red-team and correctness reviews: verify-input."""
    # High: the validator's errors on the node (here, a proof edited after it was logged) block it.
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "def:x", kind="definition")
    p = fx.claim_at(bp, "prop:a", "proved", uses=["def:x"], root=root, proof="Original proof by def:x.")
    p.write_text(p.read_text(encoding="utf-8").replace("Original", "Edited"), encoding="utf-8")
    problems, _ = bt.verify_input(p)
    check("rv_validator_error_blocks", any("proof changed" in x for x in problems), str(problems))
    # ...and its errors on a dependency (a checked node resting on an unchecked one).
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "lem:c")
    fx.claim_at(bp, "lem:b", "checked", uses=["lem:c"], root=root, statement="b", proof="B.")
    p = fx.claim_at(bp, "prop:a", "proved", uses=["lem:b"], root=root, statement="a")
    problems, _ = bt.verify_input(p)
    check("rv_dependency_validator_error_blocks", any(x.startswith("validator: lem:b") for x in problems),
          str(problems))
    # High: a statement that names a node missing from uses.
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "asm:zz-sentinel", kind="assumption", statement="The sentinel assumption holds.")
    p = fx.claim_at(bp, "prop:a", "proved", root=root, statement="Under asm:zz-sentinel, V is concave.",
                    proof="Immediate.")
    problems, _ = bt.verify_input(p)
    check("rv_statement_citation_blocks", any("asm:zz-sentinel" in x for x in problems), str(problems))
    # Medium: a declared mention reaches the verifier as context only, never as a premise.
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "def:x", kind="definition")
    fx.write_node(bp, "lem:zz-key", statement="The key sentinel lemma.")
    p = fx.claim_at(bp, "prop:a", "proved", uses=["def:x"], root=root, proof="By lem:zz-key and def:x.")
    p.write_text(p.read_text(encoding="utf-8").replace("---\n## Statement",
                 "---\n<!-- mentions: lem:zz-key -->\n## Statement", 1), encoding="utf-8")
    problems, text = bt.verify_input(p)
    ctx = text.split("## Nodes named but not used (context only)")[-1].split("## Proof submitted")[0]
    check("rv_mention_given_as_context_only", problems == [] and "not premises" in text
          and "**lem:zz-key (claim).** The key sentinel lemma." in ctx
          and "key sentinel" not in text.split("## Nodes named")[0], f"{problems} {text}")
    # Medium: definitions and assumptions under the used claims are included; their proofs and statuses are not.
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "def:zz-v", kind="definition", statement="The sentinel value function.")
    fx.claim_at(bp, "lem:b", "checked", uses=["def:zz-v"], root=root, statement="V as in def:zz-v rises.",
                proof="SECRET-PROOF-TEXT.")
    p = fx.claim_at(bp, "prop:a", "proved", uses=["lem:b"], root=root, statement="a", proof="By lem:b.")
    problems, text = bt.verify_input(p)
    check("rv_transitive_base_statements", problems == [] and "sentinel value function" in text
          and "**def:zz-v (definition).**" in text, f"{problems} {text}")
    check("rv_no_dependency_proof_or_status", "SECRET-PROOF-TEXT" not in text and "checked" not in text, text)
    # Test gaps (correctness lens): GAP marker, empty proof.
    root, bp = fx.mkrepo(tmp)
    p = fx.claim_at(bp, "prop:a", "proved", root=root, proof="Step one. [GAP: step two]")
    problems, _ = bt.verify_input(p)
    check("rv_gap_refused", any("[GAP" in x for x in problems), str(problems))
    root, bp = fx.mkrepo(tmp)
    p = fx.claim_at(bp, "prop:a", "proved", root=root, proof="<!-- nothing yet -->")
    problems, _ = bt.verify_input(p)
    check("rv_empty_proof_refused", any("empty" in x for x in problems), str(problems))
    # Low: a comment that survives stripping (unbalanced nesting) is refused, not leaked.
    root, bp = fx.mkrepo(tmp)
    p = fx.claim_at(bp, "prop:a", "proved", root=root,
                    proof="Done. <!-- outer <!-- inner --> SENTINEL-LEAK -->")
    problems, text = bt.verify_input(p)
    check("rv_comment_leak_refused", any("comment" in x for x in problems) and "SENTINEL-LEAK" not in text,
          f"{problems} {text}")
    # Low: --out may not write into the blueprint (it could overwrite the node itself).
    root, bp, p = ready_blueprint(tmp)
    before = p.read_bytes()
    rc, out = run_cli(["verify-input", str(p), "--out", str(p)])
    check("rv_out_onto_node_refused", rc == 2 and p.read_bytes() == before, f"{rc} {out}")
    rc, out = run_cli(["verify-input", str(p), "--out", str(bp / "input.md")])
    check("rv_out_into_blueprint_refused", rc == 2 and not (bp / "input.md").exists(), f"{rc} {out}")


def test_review_fixes_repoint(tmp: Path) -> None:
    """2026-10-12 red-team and correctness reviews: repoint and dependents."""
    # High: the demotion cascades to checked nodes that rest on a demoted dependent.
    root, bp = fx.mkrepo(tmp)
    fx.claim_at(bp, "lem:new", "checked", root=root, statement="new", proof="P new.")
    retired(bp, "lem:old", "lem:new")
    fx.claim_at(bp, "prop:k", "checked", uses=["lem:old"], root=root, statement="k", proof="K.")
    fx.claim_at(bp, "prop:top", "checked", uses=["prop:k"], root=root, statement="top", proof="T.")
    fx.claim_at(bp, "prop:top2", "checked", uses=["prop:top"], root=root, statement="top2", proof="T2.")
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old"))])
    check("rr_dry_run_lists_cascade", rc == 0 and "prop:top:" in out and "prop:top2:" in out
          and "checked -> proved" in out, f"{rc} {out}")
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old")), "--apply"])
    st = {L: bc.parse_node(node_file(bp, L)) for L in ("prop:k", "prop:top", "prop:top2")}
    rep = bc.check_blueprint(bp, repo_root=root)
    check("rr_cascade_applied",
          st["prop:k"].status == "survived-search" and st["prop:top"].status == "proved"
          and st["prop:top2"].status == "proved" and st["prop:top"].uses == ["prop:k"], str(st))
    check("rr_cascade_validates", rc == 0 and not rep.errors, f"{rc} {rep.errors}")
    # Medium: no partial write; a read-only dependent stops the whole apply before anything is written.
    import os, stat
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "lem:new", statement="new")
    retired(bp, "lem:old", "lem:new")
    for L in ("prop:a1", "prop:a2", "prop:a3"):
        fx.write_node(bp, L, uses=["lem:old"], statement=L)
    before = {f.name: f.read_bytes() for f in bp.glob("*.md")}
    ro = node_file(bp, "prop:a2")
    os.chmod(ro, stat.S_IREAD)
    try:
        rc, out = run_cli(["repoint", str(node_file(bp, "lem:old")), "--apply"])
    finally:
        os.chmod(ro, stat.S_IREAD | stat.S_IWRITE)
    check("rr_read_only_refused_atomically",
          rc == 1 and "writ" in out and before == {f.name: f.read_bytes() for f in bp.glob("*.md")},
          f"{rc} {out}")
    # Medium/Low: lone-CR files work, and mixed line endings are kept line by line.
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "lem:new", statement="new")
    retired(bp, "lem:old", "lem:new")
    cr = fx.write_node(bp, "prop:cr", uses=["lem:old"], statement="cr")
    cr.write_bytes(cr.read_bytes().replace(b"\n", b"\r"))
    mixed = fx.write_node(bp, "prop:mx", uses=["lem:old"], statement="mx")
    mixed.write_bytes(mixed.read_bytes().replace(b"## Proof\n", b"## Proof\r\n"))
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old")), "--apply"])
    raw_cr, raw_mx = cr.read_bytes(), mixed.read_bytes()
    check("rr_lone_cr_ok", rc == 0 and b"\n" not in raw_cr and bc.parse_node(cr).uses == ["lem:new"],
          f"{rc} {out}")
    check("rr_mixed_endings_kept", raw_mx.count(b"\r\n") == 1 and bc.parse_node(mixed).uses == ["lem:new"],
          repr(raw_mx))
    # Low: a chain of retired nodes is followed to the first live successor.
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "lem:c", statement="c")
    retired(bp, "lem:b", "lem:c", statement="b")
    retired(bp, "lem:a", "lem:b", statement="a")
    fx.write_node(bp, "prop:d", uses=["lem:a"], statement="d")
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:a")), "--apply"])
    check("rr_follows_chain", rc == 0 and bc.parse_node(node_file(bp, "prop:d")).uses == ["lem:c"]
          and "lem:a -> lem:b -> lem:c" in out, f"{rc} {out}")
    # Low: a successor of another kind is reported; a refuted successor is refused.
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "def:new", kind="definition")
    retired(bp, "lem:old", "def:new")
    fx.write_node(bp, "prop:d", uses=["lem:old"], statement="d")
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old"))])
    check("rr_kind_change_reported", rc == 0 and "kind" in out, f"{rc} {out}")
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "lem:r", status="refuted", statement="r",
                  log=[("new", "conjecture", "theorist", ""), ("conjecture", "refuted", "theorist", fx.CHECK)])
    retired(bp, "lem:old", "lem:r")
    fx.write_node(bp, "prop:d", uses=["lem:old"], statement="d")
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old"))])
    check("rr_refuted_successor_refused", rc == 1 and "refuted" in out, f"{rc} {out}")
    # Test gap: no enclosing repo means no locators can be written.
    bp = tmp / "norepo" / "blueprint"
    bp.mkdir(parents=True)
    fx.write_node(bp, "lem:new", statement="new")
    retired(bp, "lem:old", "lem:new")
    fx.write_node(bp, "prop:d", uses=["lem:old"], statement="d")
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old"))])
    check("rr_no_repo_refused", rc == 1 and "repo" in out, f"{rc} {out}")
    # Low: a dependent whose last log entry is future-dated is refused before writing.
    root, bp = fx.mkrepo(tmp)
    fx.claim_at(bp, "lem:new", "checked", root=root, statement="new", proof="P new.")
    retired(bp, "lem:old", "lem:new")
    log = fx.climb("proved", root, "prop:p", "P.", ["lem:old"])
    log[-1] = log[-1] + ("", bc.proof_hash("P.", ["lem:old"]), "2099-01-01")
    p = fx.write_node(bp, "prop:p", status="proved", uses=["lem:old"], statement="p", proof="P.", log=log)
    before = p.read_bytes()
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old")), "--apply"])
    check("rr_future_date_refused", rc == 1 and "future" in out and p.read_bytes() == before, f"{rc} {out}")
    # Low: a demoted node that carries a Lean declaration is reported.
    root, bp = fx.mkrepo(tmp)
    fx.claim_at(bp, "lem:new", "checked", root=root, statement="new", proof="P new.")
    retired(bp, "lem:old", "lem:new")
    fx.claim_at(bp, "prop:v", "verified", uses=["lem:old"], root=root, statement="v", proof="V.")  # lean: defaults to fx.LEAN, matching the card climb() writes
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old"))])
    check("rr_lean_reported", rc == 0 and "lean" in out.lower() and fx.LEAN in out, f"{rc} {out}")
    # Low: dependents on an unparseable node reports, no traceback.
    root, bp = fx.mkrepo(tmp)
    (bp / "prop-bad.md").write_text("---\nlabel: prop:bad\n", encoding="utf-8")
    rc, out = run_cli(["dependents", str(bp / "prop-bad.md")])
    check("rr_dependents_bad_node", rc == 1 and "prop-bad.md" in out, f"{rc} {out}")


def test_review_round2(tmp: Path) -> None:
    """2026-10-12 round-2 red-team review."""
    # High: a checked node whose proof was edited after logging is not laundered by the cascade.
    root, bp = fx.mkrepo(tmp)
    fx.claim_at(bp, "lem:new", "checked", root=root, statement="new", proof="P new.")
    retired(bp, "lem:old", "lem:new")
    fx.claim_at(bp, "prop:k", "checked", uses=["lem:old"], root=root, statement="k", proof="K.")
    top = fx.claim_at(bp, "prop:top", "checked", uses=["prop:k"], root=root, statement="top", proof="T.")
    top.write_text(top.read_text(encoding="utf-8").replace("\nT.\n", "\nT edited.\n"), encoding="utf-8")
    before = {f.name: f.read_bytes() for f in bp.glob("*.md")}
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old")), "--apply"])
    check("r2_refuses_node_with_own_errors", rc == 1 and "prop:top" in out
          and before == {f.name: f.read_bytes() for f in bp.glob("*.md")}, f"{rc} {out}")
    # ...and a clean cascade line carries no new proof hash (the logged one stays authoritative).
    root, bp = fx.mkrepo(tmp)
    fx.claim_at(bp, "lem:new", "checked", root=root, statement="new", proof="P new.")
    retired(bp, "lem:old", "lem:new")
    fx.claim_at(bp, "prop:k", "checked", uses=["lem:old"], root=root, statement="k", proof="K.")
    fx.claim_at(bp, "prop:top", "checked", uses=["prop:k"], root=root, statement="top", proof="T.")
    bt.repoint(node_file(bp, "lem:old"), apply=True)
    last = bc.parse_node(node_file(bp, "prop:top")).log[-1]
    check("r2_cascade_line_no_proof_hash", last.to == "proved" and last.proof_hash is None, str(last))
    # Medium: the cascade touches only nodes resting on what this repoint lowered.
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "lem:new", statement="new")
    retired(bp, "lem:old", "lem:new")
    fx.write_node(bp, "prop:d", uses=["lem:old"], statement="d")
    fx.write_node(bp, "lem:zz-c", statement="unrelated conjecture")
    fx.claim_at(bp, "prop:zz-u", "checked", uses=["lem:zz-c"], root=root, statement="u", proof="U.")
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old")), "--apply"])
    check("r2_cascade_scoped", bc.parse_node(node_file(bp, "prop:zz-u")).status == "checked"
          and "prop:zz-u" not in out.split("BLUEPRINT:")[0], f"{rc} {out}")
    # Medium: an unparseable node file makes repoint refuse; dependents warns.
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "lem:new", statement="new")
    retired(bp, "lem:old", "lem:new")
    (bp / "prop-broken.md").write_text("---\nlabel: prop:broken\nuses: [lem:old]\n", encoding="utf-8")
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old"))])
    check("r2_repoint_refuses_unparseable", rc == 1 and "prop-broken.md" in out, f"{rc} {out}")
    rc, out = run_cli(["dependents", str(node_file(bp, "lem:old"))])
    check("r2_dependents_warns_unparseable", "prop-broken.md" in out, f"{rc} {out}")
    # Medium: a dependency cycle among the used nodes blocks verify-input.
    root, bp = fx.mkrepo(tmp)
    fx.claim_at(bp, "lem:x", "checked", uses=["lem:y"], root=root, statement="x", proof="X.")
    fx.claim_at(bp, "lem:y", "checked", uses=["lem:x"], root=root, statement="y", proof="Y.")
    p = fx.claim_at(bp, "prop:a", "proved", uses=["lem:x"], root=root, statement="a", proof="By lem:x.")
    problems, _ = bt.verify_input(p)
    check("r2_cycle_blocks", any("cycle" in x for x in problems), str(problems))
    # Medium: a comment leak in a mentioned node's statement is refused too.
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "lem:zz-m", statement="m <!-- a <!-- b --> SENTINEL-LEAK -->")
    p = fx.claim_at(bp, "prop:a", "proved", root=root, statement="a", proof="Unlike lem:zz-m, done.")
    p.write_text(p.read_text(encoding="utf-8").replace("---\n## Statement",
                 "---\n<!-- mentions: lem:zz-m -->\n## Statement", 1), encoding="utf-8")
    problems, text = bt.verify_input(p)
    check("r2_mention_leak_refused", problems and "SENTINEL-LEAK" not in text, f"{problems} {text}")
    # Low: a label in uses is never also listed as context-only; a used statement's own citations get context.
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "def:x", kind="definition", statement="x def.")
    fx.write_node(bp, "lem:zz-far", statement="far lemma")
    fx.claim_at(bp, "lem:b", "checked", root=root, statement="b, unlike lem:zz-far.", proof="B.")
    p = fx.claim_at(bp, "prop:a", "proved", uses=["def:x", "lem:b"], root=root, statement="a",
                    proof="By def:x and lem:b.")
    p.write_text(p.read_text(encoding="utf-8").replace("---\n## Statement",
                 "---\n<!-- mentions: def:x -->\n## Statement", 1), encoding="utf-8")
    problems, text = bt.verify_input(p)
    ctx = text.split("## Nodes named but not used (context only)")
    check("r2_used_not_also_context", problems == [] and (len(ctx) == 1 or "def:x" not in ctx[1].split("## Proof")[0]),
          f"{problems} {text}")
    check("r2_used_statement_citation_in_context", len(ctx) == 2 and "far lemma" in ctx[1], text)
    # Low: a mention naming no node blocks verify-input.
    root, bp = fx.mkrepo(tmp)
    p = fx.claim_at(bp, "prop:a", "proved", root=root, statement="a", proof="Done.")
    p.write_text(p.read_text(encoding="utf-8").replace("---\n## Statement",
                 "---\n<!-- mentions: lem:zz-typo -->\n## Statement", 1), encoding="utf-8")
    problems, _ = bt.verify_input(p)
    check("r2_bad_mention_blocks", any("lem:zz-typo" in x for x in problems), str(problems))
    # Low: the future-date refusal applies only to nodes that get a log line.
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "lem:new", statement="new")
    retired(bp, "lem:old", "lem:new")
    fx.write_node(bp, "prop:d", uses=["lem:old"], statement="d",
                  log=[("new", "conjecture", "theorist", "", "", None, "2099-01-01")])
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old")), "--apply"])
    check("r2_future_date_only_when_logging", rc == 0 and bc.parse_node(node_file(bp, "prop:d")).uses == ["lem:new"],
          f"{rc} {out}")
    # Low: --out naming a directory is a usage error, not a traceback.
    root, bp, p = ready_blueprint(tmp)
    rc, out = run_cli(["verify-input", str(p), "--out", str(tmp)])
    check("r2_out_directory_usage", rc == 2, f"{rc} {out}")


def test_review_round2_pins(tmp: Path) -> None:
    """Behaviours the round-2 correctness review found unpinned (each mutation left the suites green)."""
    # The cascade line's locator is the node that caused it, not the retired chain.
    root, bp = fx.mkrepo(tmp)
    fx.claim_at(bp, "lem:new", "checked", root=root, statement="new", proof="P new.")
    retired(bp, "lem:old", "lem:new")
    fx.claim_at(bp, "prop:k", "checked", uses=["lem:old"], root=root, statement="k", proof="K.")
    fx.claim_at(bp, "prop:top", "checked", uses=["prop:k"], root=root, statement="top", proof="T.")
    bt.repoint(node_file(bp, "lem:old"), apply=True)
    last = bc.parse_node(node_file(bp, "prop:top")).log[-1]
    check("p2_cascade_locator_is_cause", last.locators == ["theory/blueprint/prop-k.md"], str(last.locators))
    # The cascade runs to a fixpoint even when the deeper node sorts first.
    root, bp = fx.mkrepo(tmp)
    fx.claim_at(bp, "lem:new", "checked", root=root, statement="new", proof="P new.")
    retired(bp, "lem:old", "lem:new")
    fx.claim_at(bp, "prop:k", "checked", uses=["lem:old"], root=root, statement="k", proof="K.")
    fx.claim_at(bp, "prop:b-mid", "checked", uses=["prop:k"], root=root, statement="mid", proof="M.")
    fx.claim_at(bp, "prop:a-top", "checked", uses=["prop:b-mid"], root=root, statement="top", proof="T.")
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old")), "--apply"])
    check("p2_cascade_fixpoint", rc == 0 and bc.parse_node(node_file(bp, "prop:a-top")).status == "proved",
          f"{rc} {out}")
    # A write failure part-way restores the files already written.
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "lem:new", statement="new")
    retired(bp, "lem:old", "lem:new")
    for L in ("prop:a1", "prop:a2"):
        fx.write_node(bp, L, uses=["lem:old"], statement=L)
    before = {f.name: f.read_bytes() for f in bp.glob("*.md")}
    real, calls = Path.write_bytes, []

    def flaky(self, data):
        calls.append(self.name)
        if len(calls) == 2:
            raise OSError("injected")
        return real(self, data)
    Path.write_bytes = flaky
    try:
        ok, msgs = bt.repoint(node_file(bp, "lem:old"), apply=True)
    finally:
        Path.write_bytes = real
    check("p2_restore_on_write_failure",
          not ok and before == {f.name: f.read_bytes() for f in bp.glob("*.md")}, f"{ok} {msgs}")
    # The successor itself is never repointed at its predecessor; a superseded_by loop is refused.
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "lem:new", uses=["lem:old"], statement="new")
    retired(bp, "lem:old", "lem:new")
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:old"))])
    check("p2_successor_self_skipped", "skip: lem:new is the successor itself" in out, f"{rc} {out}")
    root, bp = fx.mkrepo(tmp)
    retired(bp, "lem:a", "lem:b", statement="a")
    retired(bp, "lem:b", "lem:a", statement="b")
    rc, out = run_cli(["repoint", str(node_file(bp, "lem:a"))])
    check("p2_supersession_loop_refused", rc == 1 and "loops" in out, f"{rc} {out}")
    # verify-input: a validator error two levels down blocks; an imported node is ready only at checked.
    root, bp = fx.mkrepo(tmp)
    fx.write_node(bp, "lem:d")
    fx.claim_at(bp, "lem:c", "checked", uses=["lem:d"], root=root, statement="c", proof="C.")
    fx.claim_at(bp, "lem:b", "checked", uses=["lem:c"], root=root, statement="b", proof="B.")
    p = fx.claim_at(bp, "prop:a", "proved", uses=["lem:b"], root=root, statement="a", proof="By lem:b.")
    problems, _ = bt.verify_input(p)
    check("p2_transitive_validator_error_blocks", any(x.startswith("validator: lem:c") for x in problems),
          str(problems))
    root, bp = fx.mkrepo(tmp)
    fx.claim_at(bp, "imp:t", "proved", root=root, kind="imported", statement="t", proof="Source.")
    p = fx.claim_at(bp, "prop:a", "proved", uses=["imp:t"], root=root, statement="a", proof="By imp:t.")
    problems, _ = bt.verify_input(p)
    check("p2_imported_needs_checked", any("imp:t" in x and "proved" in x for x in problems), str(problems))
    # The context-only section carries statements only: no status, no proof.
    root, bp = fx.mkrepo(tmp)
    fx.claim_at(bp, "lem:zz-m", "proved", root=root, statement="m statement", proof="M-PROOF-SENTINEL.")
    p = fx.claim_at(bp, "prop:a", "proved", root=root, statement="a", proof="Unlike lem:zz-m, done.")
    p.write_text(p.read_text(encoding="utf-8").replace("---\n## Statement",
                 "---\n<!-- mentions: lem:zz-m -->\n## Statement", 1), encoding="utf-8")
    problems, text = bt.verify_input(p)
    check("p2_context_no_status_or_proof", problems == [] and "m statement" in text
          and "M-PROOF-SENTINEL" not in text and "proved" not in text, f"{problems} {text}")


def main() -> int:
    global bc, bt, fx
    try:
        bc = load("blueprint_check")
        bt = load("blueprint_tools")
        fx = load("test_blueprint_check")
        fx.bc = bc
    except Exception as e:
        print(f"FAIL  cannot load modules: {e!r}")
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
