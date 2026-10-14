#!/usr/bin/env python3
"""Integration tests for bin/lean_check.py against a real Lean toolchain and comparator (spec acceptance #7).

Each case copies the core-Lean fixture bin/fixtures/lean_check/ (no Mathlib; pinned to the
installed toolchain) into a temp dir, plants one defect, and runs lean_check for real.
Tools: COMPARATOR_BIN / COMPARATOR_LEAN4EXPORT / COMPARATOR_LANDRUN, else the standard
build under ~/lean/_tools/comparator (templates/theory/lean-layout.md). Run:
    python3 bin/test_lean_check_integration.py
Exit 0 = all pass, 1 = a failure, 3 = SKIPPED because lake or comparator was not found (never a pass).
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "lean_check"
FAILS: list[str] = []
PASSES = 0
STMTS = ("thing_part_a", "thing_nonvacuous", "thing_sanity_1", "thing_false_variant")


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


lc = bc = None
_n = 0


def find_tools() -> dict:
    base = Path.home() / "lean" / "_tools" / "comparator"
    exe = ".exe" if sys.platform == "win32" else ""
    default = {"comparator": base / ".lake" / "build" / "bin" / f"comparator{exe}",
               "lean4export": base / ".lake" / "packages" / "lean4export" / ".lake" / "build" / "bin" / f"lean4export{exe}",
               "landrun": base / "scripts" / ("fake-landrun.cmd" if sys.platform == "win32" else "fake-landrun.sh")}
    env = {"comparator": "COMPARATOR_BIN", "lean4export": "COMPARATOR_LEAN4EXPORT", "landrun": "COMPARATOR_LANDRUN"}
    return {k: Path(os.environ[env[k]]) if os.environ.get(env[k]) else default[k] for k in default}


def case(tmp: Path, tools: dict, edit=None, sign: bool = True):
    """A repo with node + card + lean.toml, and a fresh fixture copy; `edit(proj)` plants the defect."""
    global _n
    _n += 1
    root = tmp / f"repo{_n}"
    (root / ".git").mkdir(parents=True)
    bp = root / "theory" / "blueprint"
    (bp / "cards").mkdir(parents=True)
    proj = tmp / f"lean fix {_n}"
    shutil.copytree(FIXTURE, proj, ignore=shutil.ignore_patterns(".lake", "LeanCheck"))
    sfile = proj / "Fix" / "Statements" / "Thing.lean"
    node = bp / "prop-thing.md"
    node.write_text("---\nlabel: prop:thing\nkind: claim\nstatus: checked\nuses: []\nsupersedes:\n"
                    "superseded_by:\nlean: Fix.Thing\npaper_ref:\n---\n## Statement\nS\n## Proof\nP\n"
                    "## Evidence log\n- 2026-01-15 | new -> conjecture | theorist |  | stmt:000000000000\n",
                    encoding="utf-8")
    if sign:
        (bp / "cards" / "prop-thing.md").write_text(
            f"# Card\n**Node:** prop:thing\n**Node statement hash:** {bc.statement_hash('S')}\n**Lean:** Fix.Thing\n"
            f"**Statement SHA-256:** {lc.statement_sha256(sfile)}\n**Audited statements:** {', '.join(STMTS)}\n"
            "**Verdict:** FAITHFUL\n**Signed off:** CS 2026-10-12\n", encoding="utf-8")
    (root / ".claude" / "state").mkdir(parents=True)
    (root / ".claude" / "state" / "lean.toml").write_text(
        f"project = '{proj}'\n" + "".join(f"{k} = '{v}'\n" for k, v in tools.items()), encoding="utf-8")
    if edit:
        edit(proj)
    return node, proj


def sub(path: Path, old: str, new: str) -> None:
    s = path.read_text(encoding="utf-8")
    assert old in s, old
    path.write_text(s.replace(old, new, 1), encoding="utf-8")


def proofs(proj: Path) -> Path:
    return proj / "Fix" / "Proofs" / "Thing.lean"


def helper(proj: Path, body: str) -> None:
    (proj / "Fix" / "Helper.lean").write_text(f"module\n\npublic section\n\nnamespace Fix\n\n{body}\n\nend Fix\n",
                                              encoding="utf-8")
    sub(proofs(proj), "public import Fix.Statements.Thing", "public import Fix.Statements.Thing\npublic import Fix.Helper")


def run(node, **kw):
    t0 = time.time()
    res = lc.check_node(node, timeout=900, **kw)
    return res, time.time() - t0


def failed(res, check_name: str) -> bool:
    return res.verdict == "FAIL" and any(n == check_name and v == "FAIL" for n, v, _ in res.checks)


def detail(res) -> str:
    return " || ".join(f"{v} {n}: {d}" for n, v, d in res.checks)[:900]


def main() -> int:
    global lc, bc
    bc = load("blueprint_check")
    lc = load("lean_check")
    lake = lc.resolve_lake()
    tools = find_tools()
    missing = [k for k, p in tools.items() if not p.is_file()]
    if lake is None or missing:
        print(f"SKIPPED: lake={lake} missing tools={missing}; acceptance #7 is UNVERIFIED here")
        return 3
    print(f"using {lake}; comparator {tools['comparator']}")
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)

        node, proj = case(tmp, tools)
        res, secs = run(node)
        check("int_clean_pass", res.verdict == "PASS", detail(res))
        print(f"        (full check {secs:.0f}s; {res.toolchain})")
        res, _ = run(node, statements_only=True)
        check("int_statements_mode_pass", res.verdict == "PASS", detail(res))

        node, proj = case(tmp, tools, lambda p: sub(proofs(p), "  intro n\n  omega", "  sorry"))
        res, _ = run(node)
        check("int_sorry_fails", res.verdict == "FAIL" and "sorry" in detail(res), detail(res))
        node, proj = case(tmp, tools, lambda p: sub(proofs(p), "  intro n\n  omega", "  sorry"))
        res, _ = run(node, statements_only=True)
        check("int_statements_mode_ignores_proof_sorry", res.verdict == "PASS", detail(res))

        # Comparator-level catches: nothing here trips the static scan.
        def hidden_sorry(p):
            helper(p, "theorem helper_lemma : ∀ n : Nat, n + n = 2 * n := by\n  sorry")
            sub(proofs(p), "  intro n\n  omega", "  exact helper_lemma")
        node, proj = case(tmp, tools, hidden_sorry)
        res, _ = run(node)
        check("int_hidden_sorry_in_helper_fails_in_comparator",
              failed(res, "comparator") and "sorryAx" in detail(res), detail(res))

        def shadow(p):
            sub(proofs(p), "namespace Fix\n", "namespace Fix\nnamespace Fix\ndef thing_part_a_stmt : Prop := True\nend Fix\n")
            sub(proofs(p), "theorem thing_part_a : thing_part_a_stmt := by\n  unfold thing_part_a_stmt double\n  intro n\n  omega",
                "theorem thing_part_a : Fix.thing_part_a_stmt := trivial")
        node, proj = case(tmp, tools, shadow)
        res, _ = run(node)
        check("int_rt2_namespace_shadow_fails_in_comparator", failed(res, "comparator"), detail(res))

        node, proj = case(tmp, tools, lambda p: sub(proofs(p), "theorem thing_sanity_1 : thing_sanity_1_stmt := by\n"
                                                    "  unfold thing_sanity_1_stmt double\n  decide",
                                                    "theorem thing_sanity_1 : double 2 = 4 := by\n  decide"))
        res, _ = run(node)
        check("int_proof_of_other_statement_fails_in_comparator", failed(res, "comparator"), detail(res))

        # Static catches (the configuration comparator trusts, and defence in depth).
        def srcdir(p):
            (p / "alt" / "Fix" / "Statements").mkdir(parents=True)
            (p / "alt" / "Fix" / "Statements" / "Thing.lean").write_text(
                "module\n\n@[expose] public section\n\nnamespace Fix\n\n"
                + "".join(f"def {s}_stmt : Prop := True\n" for s in STMTS) + "\nend Fix\n", encoding="utf-8")
            sub(p / "lakefile.toml", 'name = "Fix"\n', 'name = "Fix"\nsrcDir = "alt"\n')
        node, proj = case(tmp, tools, srcdir)
        res, _ = run(node)
        check("int_rt2_srcdir_fails", failed(res, "lakefile"), detail(res))
        node, proj = case(tmp, tools, lambda p: (p / "lakefile.lean").write_text(
            "import Lake\nopen Lake DSL\npackage fix\n@[default_target] lean_lib Fix\n", encoding="utf-8"))
        res, _ = run(node)
        check("int_rt2_lakefile_lean_fails", failed(res, "lakefile"), detail(res))
        node, proj = case(tmp, tools, lambda p: sub(proofs(p), "namespace Fix\n",
                                                    "open Nat in macro_rules | `(tactic| omega) => `(tactic| trivial)\n"
                                                    "namespace Fix\n"))
        res, _ = run(node)
        check("int_rt2_open_in_macro_rules_fails", failed(res, "proof file") and "macro_rules" in detail(res), detail(res))

        def redefine(p):
            txt = proofs(p).read_text(encoding="utf-8").replace("public import Fix.Statements.Thing\n", "")
            txt = txt.replace("namespace Fix\n", "namespace Fix\n\n" + "".join(
                f"def {s}_stmt : Prop := True\n" for s in STMTS), 1)
            proofs(p).write_text(txt, encoding="utf-8")
        node, proj = case(tmp, tools, redefine)
        res, _ = run(node)
        check("int_rt1_proof_redefines_statements_fails", res.verdict == "FAIL", detail(res))
        node, proj = case(tmp, tools, lambda p: sub(p / "Fix" / "Statements" / "Thing.lean", "n + n", "n + n + 0"))
        res, _ = run(node)
        check("int_helper_edited_after_signing_fails", failed(res, "card"), detail(res))
        node, proj = case(tmp, tools, lambda p: (sub(p / "Fix" / "Statements" / "Thing.lean", "thing_false_variant_stmt",
                                                     "thing_other_stmt"),
                                                 sub(proofs(p), "thing_false_variant : thing_false_variant_stmt",
                                                     "thing_other : thing_other_stmt"),
                                                 sub(proofs(p), "unfold thing_false_variant_stmt", "unfold thing_other_stmt")),
                          sign=False)
        res, _ = run(node)
        check("int_missing_companion_fails", failed(res, "statement file") and "false_variant" in detail(res),
              detail(res))

        # Round 3 (2026-10-12) Critical: an indented import of an unhashed project module.
        def hidden_import(p):
            (p / "Fix" / "Hidden.lean").write_text("module\n\n@[expose] public section\n\nnamespace Fix\n\n"
                                                    "def hidden_hyp : Prop := False\n\nend Fix\n", encoding="utf-8")
            sub(p / "Fix" / "Statements" / "Thing.lean", "module\n", "module\n\n  public import Fix.Hidden\n")
        node, proj = case(tmp, tools, hidden_import)
        res, _ = run(node)
        check("int_rt3_indented_import_fails", failed(res, "statement file") and "Fix.Hidden" in detail(res), detail(res))
        node, proj = case(tmp, tools, lambda p: (p / "LeanCheck").mkdir() or (p / "LeanCheck" / "Planted.lean").write_text(
            "module\n\n#eval IO.println \"planted\"\n", encoding="utf-8"))
        res, _ = run(node)
        check("int_rt3_planted_leancheck_removed", res.verdict == "PASS" and not (proj / "LeanCheck" / "Planted.lean").exists(),
              detail(res))

        # Fix verification (2026-10-12): a two-line `open ... renaming` passed comparator before the fix.
        node, proj = case(tmp, tools, lambda p: sub(p / "Fix" / "Statements" / "Thing.lean", "namespace Fix\n",
                                                    "namespace Fix\n\nopen Nat\n  renaming mul → plus\n"))
        res, _ = run(node)
        check("int_vf_two_line_open_renaming_fails", failed(res, "statement file") and "renaming" in detail(res), detail(res))

    print(f"\n{PASSES} passed, {len(FAILS)} failed")
    if FAILS:
        print("failed: " + ", ".join(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
