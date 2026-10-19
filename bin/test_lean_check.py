#!/usr/bin/env python3
"""Tests for bin/lean_check.py (Lean evidence for a blueprint node).

Plain check() style, as in bin/test_blueprint_check.py. External tools (lake, comparator)
are replaced by a fake runner here; bin/test_lean_check_integration.py drives the real
toolchain and comparator. Run:
    python3 bin/test_lean_check.py      # exit 0 = all pass
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
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


bc = lc = None  # set in main()

HEADER = ("module\n\npublic import Mathlib\n\nset_option linter.style.header false\n\n@[expose] public section\n\n"
          "namespace Pkg\n\n")
STATEMENTS = HEADER + (
    "/-- A helper. -/\nnoncomputable def f (x : ℝ) : ℝ := x ^ 2\n\n"
    "def thing_part_a_stmt : Prop := ∀ x : ℝ, 0 ≤ f x\n\n"
    "def thing_nonvacuous_stmt : Prop := ∃ x : ℝ, 0 < x\n\n"
    "def thing_sanity_1_stmt : Prop := f 2 = 4\n\n"
    "def thing_false_variant_stmt : Prop := ¬ ∀ x : ℝ, 0 < f x\n\n"
    "end Pkg\n")
PARTS = ["thing_part_a", "thing_nonvacuous", "thing_sanity_1", "thing_false_variant"]
PROOFS = ("module\n\npublic import Pkg.Statements.Thing\n\npublic section\n\nnamespace Pkg\n\n"
          + "".join(f"theorem {p} : {p}_stmt := by\n  unfold {p}_stmt\n  positivity\n\n" for p in PARTS)
          + "end Pkg\n")
LAKEFILE = ('name = "pkg"\nversion = "0.1.0"\ndefaultTargets = ["Pkg"]\n\n[leanOptions]\nautoImplicit = false\n'
            'relaxedAutoImplicit = false\nweak.linter.mathlibStandardSet = true\n\n'
            '[[require]]\nname = "mathlib"\nscope = "leanprover-community"\nrev = "v4.35.0-rc4"\n\n'
            '[[lean_lib]]\nname = "Pkg"\nglobs = ["Pkg.+"]\n\n[[lean_lib]]\nname = "LeanCheck"\nglobs = ["LeanCheck.+"]\n')
MATHLIB_REV = "1f414401f69059aa7eead47b53ee40bd38455eeb"
MANIFEST = {"version": "1.3.0", "packagesDir": ".lake/packages", "name": "pkg", "lakeDir": ".lake", "packages": [
    {"name": "mathlib", "type": "git", "url": "https://github.com/leanprover-community/mathlib4", "rev": MATHLIB_REV,
     "inputRev": "v4.35.0-rc4", "scope": "leanprover-community", "inherited": False, "manifestFile": "lake-manifest.json"},
    {"name": "Cli", "type": "git", "url": "https://github.com/leanprover/lean4-cli", "rev": "82c11b9717083154aefc5fe8d4cba4bbf046298f",
     "inputRev": "v4.35.0-rc4", "scope": "leanprover", "inherited": True, "manifestFile": "lake-manifest.json"}]}
TOOLCHAIN = "Lean (version 4.35.0-rc4, x86_64-w64-windows-gnu, commit c29b6dd, Release)"
TOOLS = {"comparator": Path("comparator.exe"), "lean4export": Path("lean4export.exe"), "landrun": Path("landrun.cmd")}
OKAY = "Running Lean default kernel on solution.\nLean default kernel accepts the solution\nYour solution is okay!\n"

_n = 0


def setup(tmp: Path, statements: str = STATEMENTS, proofs: str = PROOFS, lakefile: str = LAKEFILE,
          card_sha: str | None = "auto", config: bool = True, lean: str = "Pkg.Thing", node_hash: str | None = None):
    """A throwaway repo with one blueprint node, a Lean project, a card and lean.toml."""
    global _n
    _n += 1
    root = tmp / f"repo{_n}"
    (root / ".git").mkdir(parents=True)
    bp = root / "theory" / "blueprint"
    bp.mkdir(parents=True)
    proj = tmp / f"lean proj {_n}"            # a space, as on Windows home paths
    (proj / "Pkg" / "Statements").mkdir(parents=True)
    (proj / "Pkg" / "Proofs").mkdir(parents=True)
    (proj / "lakefile.toml").write_text(lakefile, encoding="utf-8")
    (proj / "lean-toolchain").write_text("leanprover/lean4:v4.35.0-rc4\n", encoding="utf-8")
    (proj / "lake-manifest.json").write_text(json.dumps(MANIFEST), encoding="utf-8")
    sfile = proj / "Pkg" / "Statements" / "Thing.lean"
    sfile.write_text(statements, encoding="utf-8", newline="")
    (proj / "Pkg" / "Proofs" / "Thing.lean").write_text(proofs, encoding="utf-8", newline="")
    node = bp / "prop-thing.md"
    node.write_text("---\nlabel: prop:thing\nkind: claim\nstatus: checked\nuses: []\nsupersedes:\n"
                    f"superseded_by:\nlean: {lean}\npaper_ref:\n---\n## Statement\nS\n## Proof\nP\n"
                    "## Evidence log\n- 2026-01-15 | new -> conjecture | theorist |  | stmt:000000000000\n",
                    encoding="utf-8")
    if card_sha is not None:
        sha = lc.statement_sha256(sfile) if card_sha == "auto" else card_sha
        (bp / "cards").mkdir()
        (bp / "cards" / "prop-thing.md").write_text(
            f"# Card\n**Node:** prop:thing\n**Node statement hash:** {node_hash or bc.statement_hash('S')}\n"
            f"**Lean:** {lean}\n**Statement SHA-256:** {sha}\n**Audited statements:** {', '.join(PARTS)}\n"
            "**Verdict:** FAITHFUL\n**Signed off:** CS 2026-10-12\n", encoding="utf-8")
    if config:
        (root / ".claude" / "state").mkdir(parents=True)
        (root / ".claude" / "state" / "lean.toml").write_text("project = '" + str(proj) + "'\n", encoding="utf-8")
    return root, node, proj, sfile


def fake_runner(build_rc=0, build_out="Build completed successfully.", comp_rc=0, comp_out=OKAY,
                timeout_on=None, calls=None):
    def run(cmd, cwd, timeout):
        joined = " ".join(str(c) for c in cmd)
        if calls is not None:
            calls.append(joined)
        if timeout_on and timeout_on in joined:
            raise lc.ToolTimeout(joined)
        if "--version" in joined:
            return 0, "info: pkg: no previous manifest, creating one from scratch\n" + TOOLCHAIN
        if " build" in joined:
            return build_rc, build_out
        if "comparator" in joined:
            return comp_rc, comp_out
        return 0, ""
    return run


def result(node, **kw):
    runner = kw.pop("runner", None) or fake_runner()
    kw.setdefault("tools", TOOLS)
    return lc.check_node(node, runner=runner, lake=Path("lake"), **kw)


def failed(res, word: str) -> bool:
    return res.verdict == "FAIL" and any(v == "FAIL" and word in (n + " " + d) for n, v, d in res.checks)


def unverified(res, word: str) -> bool:
    return res.verdict == "UNVERIFIED" and any(v == "UNVERIFIED" and word in d for _, v, d in res.checks)


def stmt_problems(extra: str) -> list[str]:
    return lc.parse_statement_file(STATEMENTS.replace("end Pkg", extra + "\nend Pkg"), pkg="Pkg")[1]


# --- statement file -------------------------------------------------------------------

def test_statement_file(tmp: Path) -> None:
    root, node, proj, sfile = setup(tmp)
    h = lc.statement_sha256(sfile)
    check("lc_sha_full_hex", len(h) == 64 and all(ch in "0123456789abcdef" for ch in h), h)
    sfile.write_bytes(b"\xef\xbb\xbf" + STATEMENTS.replace("\n", "\r\n").encode("utf-8"))
    check("lc_crlf_bom_hash_stable", lc.statement_sha256(sfile) == h)
    sfile.write_text(STATEMENTS.replace("x ^ 2", "x ^ 4"), encoding="utf-8")
    check("lc_helper_def_edit_changes_hash", lc.statement_sha256(sfile) != h)

    stmts, problems = lc.parse_statement_file(STATEMENTS, pkg="Pkg")
    check("lc_enumerates_stmts", stmts == PARTS and problems == [], f"{stmts} {problems}")
    for word, bad in (("import", "import Pkg.Other"), ("variable", "variable (y : ℝ)"),
                      ("notation", 'notation "σ" => Real.sqrt'), ("macro", "macro \"m\" : term => `(1)"),
                      ("set_option", "set_option pp.all true"), ("open", "open Real in"),
                      ("import", "public import Lean")):
        _, problems = lc.parse_statement_file(STATEMENTS.replace("namespace Pkg\n", bad + "\nnamespace Pkg\n"), pkg="Pkg")
        check(f"lc_statement_restriction_{word}_{len(bad)}", any(word in p for p in problems), str(problems))
    _, problems = lc.parse_statement_file(STATEMENTS.replace("thing_false_variant_stmt", "thing_other_stmt"), pkg="Pkg")
    check("lc_missing_companion_named", any("false_variant" in p for p in problems), str(problems))
    root, node, proj, sfile = setup(tmp, statements=STATEMENTS.replace("namespace Pkg", "namespace Other")
                                    .replace("end Pkg", "end Other"))
    check("lc_namespace_must_match_package", failed(result(node), "namespace"), str(result(node).checks))
    for name, extra in (("theorem", "theorem t : True := trivial"), ("instance", "instance : Inhabited ℝ := ⟨0⟩"),
                        ("indented_instance", "  instance : Inhabited ℝ := ⟨0⟩"), ("tab_variable", "\tvariable (y : ℝ)"),
                        ("comment_then_variable", "/- c -/ variable (y : ℝ)"),
                        ("attr_theorem", "@[simp] theorem t : True := trivial"),
                        ("attr_instance_def", "@[instance] def i : Inhabited ℝ := ⟨0⟩"),
                        ("noncomputable_instance", "noncomputable instance : Inhabited ℝ := ⟨0⟩"),
                        ("attr_simp_def", "@[simp] def g (x : ℝ) : ℝ := x"), ("deriving", "deriving instance Repr for Nat")):
        check(f"lc_statement_rejects_{name}", stmt_problems(extra) != [], str(stmt_problems(extra)))
    for name, extra in (("param", "def thing_part_b_stmt (c : ℝ) : Prop := 0 < c"),
                        ("untyped", "def thing_part_b_stmt := False"),
                        ("abbrev", "abbrev thing_part_b_stmt : Prop := False"),
                        ("unicode", "def thing_partσ_stmt : Prop := False"),
                        ("indented_param", "  def thing_part_b_stmt (c : ℝ) : Prop := 0 < c")):
        check(f"lc_statement_stmt_{name}_rejected", any("_stmt" in p for p in stmt_problems(extra)),
              str(stmt_problems(extra)))
    for name, text in (("sub_namespace", STATEMENTS.replace("namespace Pkg\n", "namespace Pkg\nnamespace Sub\n")
                        .replace("end Pkg", "end Sub\nend Pkg")),
                       ("after_end", STATEMENTS + "def thing_part_z_stmt : Prop := True\n")):
        check(f"lc_statement_{name}", lc.parse_statement_file(text, pkg="Pkg")[1] != [], "")
    # Round 2: honest forms that must pass, and a `_stmt` that must not drop out of the audited set.
    for name, text in (("expose_own_line", STATEMENTS.replace("@[expose] public section", "@[expose]\npublic section")),
                       ("no_space_colon", STATEMENTS.replace("thing_part_a_stmt : Prop", "thing_part_a_stmt: Prop")),
                       ("prop_next_line", STATEMENTS.replace("thing_part_a_stmt : Prop :=", "thing_part_a_stmt :\n    Prop :=")),
                       ("match_arm", STATEMENTS.replace("end Pkg", "def g : ℕ → ℕ\n| 0 => 1\n| n + 1 => n\nend Pkg")),
                       ("linter_option", STATEMENTS.replace("end Pkg", "set_option linter.unusedVariables false\nend Pkg")),
                       ("open_scoped", STATEMENTS.replace("namespace Pkg\n", "namespace Pkg\nopen scoped BigOperators\n"))):
        stmts, problems = lc.parse_statement_file(text, pkg="Pkg")
        check(f"lc_statement_honest_{name}", problems == [] and stmts == PARTS, f"{stmts} {problems}")
    stmts, _ = lc.parse_statement_file(STATEMENTS.replace("end Pkg", "  def thing_part_b_stmt : Prop := True\nend Pkg"), pkg="Pkg")
    check("lc_indented_stmt_enumerated", "thing_part_b" in stmts, str(stmts))
    stmts, _ = lc.parse_statement_file(STATEMENTS.replace("end Pkg", "/-- h -/ def thing_part_c_stmt : Prop := True\nend Pkg"),
                                       pkg="Pkg")
    check("lc_commented_stmt_enumerated", "thing_part_c" in stmts, str(stmts))


def test_token_scan(tmp: Path) -> None:
    clean = PROOFS
    check("lc_scan_clean", lc.scan_tokens(clean, allow_sorry=False) == [], str(lc.scan_tokens(clean, allow_sorry=False)))
    p = lc.scan_tokens(clean.replace("positivity", "sorry", 1), allow_sorry=False)
    check("lc_scan_sorry", any("sorry" in x for x in p), str(p))
    check("lc_scan_sorry_allowed_statements_stage",
          lc.scan_tokens(clean.replace("positivity", "sorry", 1), allow_sorry=True) == [])
    check("lc_scan_ignores_comments_and_strings",
          lc.scan_tokens(clean + "-- sorry\n/- axiom admit -/\n/-- native_decide -/\ndef s := \"sorry\"\n",
                         allow_sorry=False) == [])
    for name, src in (("axiom", "axiom bad : False"), ("implemented_by", "@[implemented_by g] def h := 1"),
                      ("extern", "@[extern \"c\"] opaque k : Nat"), ("unsafe", "unsafe def u := 1"),
                      ("skip_kernel", "set_option debug.skipKernelTC true"), ("native", "theorem t : 1 = 1 := by native_decide"),
                      ("plus_native", "theorem t : 1 = 1 := by decide +native"), ("admit", "theorem t : 1 = 1 := by admit"),
                      ("notation", 'notation "thing_part_a_stmt" => True'),
                      ("macro_rules", "macro_rules | `(tactic| trivial) => `(tactic| rfl)"),
                      ("indented_notation", "  local notation \"σ\" => Real.sqrt"),
                      ("attr_macro", "@[simp] macro \"m\" : term => `(1)"), ("syntax", "syntax \"foo\" : term"),
                      ("elab", "elab \"foo\" : term => pure default"), ("initialize", "initialize registerTraceClass `x"),
                      ("run_cmd", "run_cmd pure ()"), ("eval", "#eval 1"), ("check_cmd", "#check Nat"),
                      ("import_lean", "import Lean.Elab"), ("set_option_other", "set_option pp.all true"),
                      ("open_in_macro_rules", "open Nat in macro_rules | `(tactic| omega) => `(tactic| trivial)"),
                      ("set_option_in_notation", "set_option maxRecDepth 100 in notation \"q\" => True"),
                      ("notation_prec", "notation:50 a \" ≺ \" b => a < b"), ("infixl_prec", "infixl:65 \" +++ \" => HAdd.hAdd"),
                      ("macro_prec", "macro:max \"m\" : term => `(1)"), ("syntax_prec", "syntax:max \"s\" : term"),
                      ("scoped_notation", "scoped[Real] notation \"π'\" => Real.pi"),
                      ("export", "export Pkg.Sub (thing_part_a)"), ("meta", "meta def m : Nat := 1"),
                      ("guillemet_desync", "def «q\"» := 1\ntheorem t : True := by sorry"),
                      ("char_quote", "def q : Char := '\"'\ntheorem t : True := by sorry"),
                      ("raw_string", 'def r : String := r"\\"\ntheorem t : True := by sorry'),
                      ("raw_hash", 'def r : String := r#"a"b"#\ntheorem t : True := by sorry')):
        check(f"lc_scan_forbidden_{name}", bool(lc.scan_tokens(clean + src + "\n", allow_sorry=False)), src)
    for name, src in (("word_boundary", "def sorryish := 1\ndef axioms_x := 2\n"),
                      ("qualified_extern", "theorem t := Foo.extern\n"), ("array_literal", "def a := #[1, 2]\n"),
                      ("heartbeats", "set_option maxHeartbeats 400000 in\ntheorem h : True := trivial\n"),
                      ("linter_off", "set_option linter.unusedVariables false\n"),
                      ("prime_identifier", "def x' := 1\ndef y'' := x'\n"), ("guillemet_name", "def «my name» := 1\n")):
        check(f"lc_scan_allows_{name}", lc.scan_tokens(clean + src, allow_sorry=False) == [],
              str(lc.scan_tokens(clean + src, allow_sorry=False)))


def test_lakefile(tmp: Path) -> None:
    root, node, proj, sfile = setup(tmp)
    check("lk_canonical_ok", lc.lakefile_problems(proj, "Pkg") == [], str(lc.lakefile_problems(proj, "Pkg")))
    for name, text, word in (
            ("srcdir", LAKEFILE.replace('name = "Pkg"\nglobs', 'name = "Pkg"\nsrcDir = "alt"\nglobs'), "lean_lib"),
            ("roots", LAKEFILE.replace('name = "Pkg"\nglobs', 'name = "Pkg"\nroots = ["X"]\nglobs'), "lean_lib"),
            ("no_check_lib", LAKEFILE.split("[[lean_lib]]\nname = \"LeanCheck\"")[0], "lean_lib"),
            ("default_globs", LAKEFILE.replace('globs = ["Pkg.+"]\n', ""), "lean_lib"),
            ("other_require", LAKEFILE.replace('name = "mathlib"', 'name = "evil"'), "require"),
            ("path_require", LAKEFILE.replace('rev = "v4.35.0-rc4"', 'rev = "v4"\npath = "../x"'), "require"),
            ("skip_kernel_option", LAKEFILE.replace("relaxedAutoImplicit = false\n",
                                                    "relaxedAutoImplicit = false\n\"debug.skipKernelTC\" = true\n"), "leanOptions"),
            ("auto_implicit", LAKEFILE.replace("autoImplicit = false\nrelaxed", "relaxed"), "autoImplicit"),
            ("relaxed", LAKEFILE.replace("relaxedAutoImplicit = false\n", ""), "relaxedAutoImplicit"),
            ("lean_exe", LAKEFILE + '\n[[lean_exe]]\nname = "x"\nroot = "Main"\n', "keys")):
        root, node, proj, sfile = setup(tmp, lakefile=text)
        probs = lc.lakefile_problems(proj, "Pkg")
        check(f"lk_rejects_{name}", any(word in p for p in probs), str(probs))
        check(f"lk_rejects_{name}_in_check", failed(result(node), "lakefile"), "")
    root, node, proj, sfile = setup(tmp)
    (proj / "lakefile.lean").write_text("import Lake\nopen Lake DSL\npackage x\n", encoding="utf-8")
    check("lk_rejects_lakefile_lean", failed(result(node), "lakefile.lean"), str(result(node).checks))


def test_resolver_and_config(tmp: Path) -> None:
    home = tmp / "home"
    (home / ".elan" / "bin").mkdir(parents=True)
    exe = home / ".elan" / "bin" / ("lake.exe" if sys.platform == "win32" else "lake")
    exe.write_text("", encoding="utf-8")
    check("lc_resolver_finds_elan_home", lc.resolve_lake(which=lambda n: None, home=home) == exe)
    check("lc_resolver_none", lc.resolve_lake(which=lambda n: None, home=tmp / "nohome") is None)
    check("lc_resolver_prefers_path", lc.resolve_lake(which=lambda n: "/x/lake", home=home) == Path("/x/lake"))

    root, node, proj, _ = setup(tmp)
    res = lc.check_node(node, runner=fake_runner(), lake=None, home=tmp / "nohome", which=lambda n: None, tools=TOOLS)
    check("lc_no_lake_unverified", unverified(res, "lake"), str(res.checks))
    root, node, proj, _ = setup(tmp, config=False)
    check("lc_no_project_unverified", unverified(result(node), "project"), str(result(node).checks))
    check("lc_dangling_project_unverified", unverified(result(node, project=tmp / "missing"), "project"), "")
    check("lc_project_flag_overrides", result(node, project=proj).verdict == "PASS", str(result(node, project=proj).checks))
    root, node, proj, _ = setup(tmp)
    (root / ".claude" / "state" / "lean.toml").write_text(
        f"project = '{(Path('..') / proj.name).as_posix()}'\ncomparator = 'tools/comparator.exe'\n", encoding="utf-8")
    check("lc_relative_project_from_repo_root", result(node).verdict == "PASS", str(result(node).checks))
    t = lc.tools_from_config(root)
    check("lc_tools_relative_to_repo_root", t["comparator"] == (root / "tools" / "comparator.exe").resolve(), str(t))
    os.environ["COMPARATOR_LANDRUN"] = str(tmp / "shim.cmd")
    try:
        check("lc_tools_from_environment", lc.tools_from_config(root)["landrun"] == tmp / "shim.cmd", "")
    finally:
        del os.environ["COMPARATOR_LANDRUN"]
    res = result(node, tools={"comparator": None, "lean4export": None, "landrun": None})
    check("lc_comparator_not_configured_unverified", unverified(res, "comparator"), str(res.checks))


def test_verdicts(tmp: Path) -> None:
    root, node, proj, sfile = setup(tmp)
    (proj / ".lake" / "build" / "lib").mkdir(parents=True)
    (proj / ".lake" / "packages" / "mathlib").mkdir(parents=True)
    calls: list[str] = []
    res = result(node, runner=fake_runner(calls=calls))
    check("lc_clean_pass", res.verdict == "PASS", f"{res.verdict} {res.checks}")
    check("lc_records_versions", "4.35.0-rc4" in res.toolchain and res.mathlib == MATHLIB_REV, f"{res.toolchain} {res.mathlib}")
    check("lc_cleans_project_build_keeps_packages",
          not (proj / ".lake" / "build").exists() and (proj / ".lake" / "packages" / "mathlib").exists(), "")
    check("lc_runs_comparator_with_config", any("comparator" in c and c.endswith("Thing.comparator.json") for c in calls),
          str(calls))
    ch = (proj / "LeanCheck" / "ThingChallenge.lean").read_text(encoding="utf-8")
    so = (proj / "LeanCheck" / "ThingSolution.lean").read_text(encoding="utf-8")
    cfg = json.loads((proj / "LeanCheck" / "Thing.comparator.json").read_text(encoding="utf-8"))
    check("lc_challenge_is_signed_statements",
          "public import Pkg.Statements.Thing" in ch and "Proofs" not in ch
          and all(f"theorem Pkg.{p} : Pkg.{p}_stmt := sorry" in ch for p in PARTS), ch)
    check("lc_solution_imports_proofs", "public import Pkg.Proofs.Thing" in so, so)
    check("lc_comparator_config",
          cfg == {"challenge_module": "LeanCheck.ThingChallenge", "solution_module": "LeanCheck.ThingSolution",
                  "theorem_names": [f"Pkg.{p}" for p in PARTS],
                  "permitted_axioms": ["propext", "Quot.sound", "Classical.choice"]}, str(cfg))

    for name, out, rc in (("mismatch", "uncaught exception: Const does not match between challenge and target 'Pkg.f'", 1),
                          ("axiom", "uncaught exception: Illegal axiom detected: 'sorryAx'", 1),
                          ("ok_text_missing", "Build completed", 0)):
        res = result(node, runner=fake_runner(comp_rc=rc, comp_out=out))
        check(f"lc_comparator_{name}_fails", failed(res, "comparator"), str(res.checks))
    res = result(node, runner=fake_runner(comp_rc=1, comp_out="uncaught exception: Illegal axiom detected: 'sorryAx'"))
    check("lc_comparator_reason_reported", any("sorryAx" in d for _, _, d in res.checks), str(res.checks))
    res = result(node, runner=fake_runner(comp_rc=127, comp_out="comparator.exe: not found"))
    check("lc_comparator_missing_unverified", unverified(res, "comparator"), str(res.checks))
    res = result(node, runner=fake_runner(timeout_on="comparator"))
    check("lc_timeout_unverified", unverified(res, "timed out"), str(res.checks))

    root, node, proj, sfile = setup(tmp, card_sha="0" * 64)
    check("lc_statement_edited_after_signing_fails", failed(result(node), "SHA-256"), str(result(node).checks))
    root, node, proj, sfile = setup(tmp, card_sha=None)
    check("lc_missing_card_fails", failed(result(node), "card"), str(result(node).checks))
    root, node, proj, sfile = setup(tmp, node_hash="0" * 12)
    check("lc_card_node_statement_hash_checked", failed(result(node), "Node statement hash"), str(result(node).checks))
    root, node, proj, sfile = setup(tmp)
    card = node.parent / "cards" / "prop-thing.md"
    card.write_text(card.read_text(encoding="utf-8").replace("thing_false_variant", "thing_other"), encoding="utf-8")
    check("lc_card_statement_list_mismatch", failed(result(node), "Audited statements"), str(result(node).checks))
    card.write_text("\n".join(ln for ln in card.read_text(encoding="utf-8").splitlines()
                              if not ln.startswith("**Audited")) + "\n", encoding="utf-8")
    check("lc_card_statement_list_required", failed(result(node), "Audited statements"), "")
    root, node, proj, sfile = setup(tmp, proofs=PROOFS.replace("positivity", "sorry", 1))
    calls = []
    res = result(node, runner=fake_runner(calls=calls))
    check("lc_full_mode_sorry_text_fails", failed(res, "sorry"), str(res.checks))
    check("lc_static_fail_skips_tools", not any("comparator" in c or " build" in c for c in calls), str(calls))
    root, node, proj, sfile = setup(tmp, proofs=PROOFS.replace("public import Pkg.Statements.Thing\n", ""))
    check("lc_proof_must_import_statements", failed(result(node), "import"), str(result(node).checks))
    root, node, proj, sfile = setup(tmp, lean="Pkg.Missing")
    check("lc_missing_statement_file_fails", failed(result(node), "Statements"), str(result(node).checks))
    for name, src in (("notation", 'notation "thing_part_a_stmt" => True'), ("run_cmd", "run_cmd pure ()"),
                      ("skip_kernel", "set_option debug.skipKernelTC true in\ntheorem f : True := trivial")):
        root, node, proj, sfile = setup(tmp)
        (proj / "Pkg" / "Helper.lean").write_text(f"module\n\n{src}\n", encoding="utf-8")
        check(f"lc_project_scan_{name}", failed(result(node), "Helper.lean"), str(result(node).checks))
    root, node, proj, sfile = setup(tmp)
    (proj / "Pkg" / "Helper.lean").write_text("module\n\nset_option maxHeartbeats 400000 in\ntheorem h : True := trivial\n",
                                             encoding="utf-8")
    (proj / ".lake" / "packages" / "mathlib").mkdir(parents=True)
    (proj / ".lake" / "packages" / "mathlib" / "X.lean").write_text("axiom fine_in_deps : True\n", encoding="utf-8")
    (proj / "Pkg" / "x.lake").mkdir()
    check("lc_project_scan_skips_dependencies_only", result(node).verdict == "PASS", str(result(node).checks))
    (proj / "Pkg" / "x.lake" / "Y.lean").write_text("axiom hidden : False\n", encoding="utf-8")
    check("lc_project_scan_nested_lake_named_dir_scanned", failed(result(node), "hidden") or failed(result(node), "axiom"),
          str(result(node).checks))
    root, node, proj, sfile = setup(tmp)
    sfile.write_bytes(b"\xff\xfe not utf-8")
    try:
        res = result(node)
        ok = res.verdict == "FAIL"
    except Exception as e:
        ok, res = False, e
    check("lc_non_utf8_is_fail_not_traceback", ok, str(res))


def test_statements_mode(tmp: Path) -> None:
    root, node, proj, sfile = setup(tmp, proofs=PROOFS.replace("positivity", "sorry"))
    calls: list[str] = []
    res = result(node, statements_only=True, runner=fake_runner(calls=calls))
    check("lc_statements_mode_pass_with_sorry_proofs", res.verdict == "PASS", f"{res.verdict} {res.checks}")
    check("lc_statements_mode_builds_statements_only",
          any(c.endswith("build Pkg.Statements.Thing") for c in calls)
          and not any("Proofs" in c or "comparator" in c for c in calls), str(calls))
    res = result(node, statements_only=True, tools={"comparator": None, "lean4export": None, "landrun": None})
    check("lc_statements_mode_needs_no_comparator", res.verdict == "PASS", str(res.checks))
    root, node, proj, sfile = setup(tmp, card_sha="1" * 64)
    check("lc_statements_mode_checks_card_hash", failed(result(node, statements_only=True), "SHA-256"), "")
    res = result(node, statements_only=True, runner=fake_runner(build_rc=1, build_out="error: unknown identifier"))
    check("lc_statements_mode_build_failure", res.verdict == "FAIL", str(res.checks))


def test_report(tmp: Path) -> None:
    root, node, proj, sfile = setup(tmp)
    res = result(node)
    p1 = lc.write_report(res, node, today=date(2026, 10, 12))
    p2 = lc.write_report(res, node, today=date(2026, 10, 12))
    check("lc_report_dated_never_overwritten",
          p1.name == "lean_check_2026-10-12.md" and p2.name == "lean_check_2026-10-12_2.md"
          and p1.parent == node.parent / "checks" / "prop-thing", f"{p1} {p2}")
    text = p1.read_text(encoding="utf-8")
    check("lc_report_header",
          "**Node:** prop:thing" in text and "**Lean:** Pkg.Thing" in text
          and f"**Statement SHA-256:** {lc.statement_sha256(sfile)}" in text and "**Mode:** full" in text
          and "**Verdict:** PASS" in text and "**Toolchain:** Lean (version 4.35.0-rc4" in text
          and f"**Mathlib:** {MATHLIB_REV}" in text and "**Checker:** comparator" in text
          and f"**Proof SHA-256:** {lc.statement_sha256(proj / 'Pkg' / 'Proofs' / 'Thing.lean')}" in text, text)
    n = bc.parse_node(node)
    check("lc_report_round_trips_through_validator",
          bc._lean_report_problem(bc.header_fields(p1), n, "full", lc.statement_sha256(sfile), p1) is None,
          str(bc._lean_report_problem(bc.header_fields(p1), n, "full", lc.statement_sha256(sfile), p1)))


def test_round3_fixes(tmp: Path) -> None:
    """Round-3 reviews (2026-10-12): the agreed middle-path fixes."""
    # Critical: the statement file's Mathlib-only import rule applies at any indentation.
    for name, line in (("indented", "  public import Pkg.Hidden"), ("comment_prefixed", "/- c -/ public import Pkg.Hidden"),
                       ("import_all", "import all Pkg.Hidden")):
        text = STATEMENTS.replace("public import Mathlib\n", "public import Mathlib\n" + line + "\n")
        _, problems = lc.parse_statement_file(text, pkg="Pkg")
        check(f"r3_statement_import_{name}", any("Pkg.Hidden" in p for p in problems), str(problems))
    check("r3_import_all_mathlib_ok", lc.parse_statement_file(
        STATEMENTS.replace("public import Mathlib", "import all Mathlib"), pkg="Pkg")[1] == [], "")
    # Critical: the dependency manifest must point at the canonical sources, pinned, matching the lakefile.
    root, node, proj, sfile = setup(tmp)
    check("r3_manifest_canonical_ok", lc.manifest_problems(proj) == [], str(lc.manifest_problems(proj)))
    for name, edit, word in (
            ("url", lambda m: m["packages"][0].update(url="https://github.com/evil/mathlib4"), "url"),
            ("path_type", lambda m: m["packages"][0].update(type="path", dir="../fake"), "git"),
            ("subdir", lambda m: m["packages"][1].update(subDir="x"), "subDir"),
            ("short_rev", lambda m: m["packages"][0].update(rev="main"), "rev"),
            ("input_rev", lambda m: m["packages"][0].update(inputRev="master"), "inputRev"),
            ("packages_dir", lambda m: m.update(packagesDir="vendor"), "packagesDir"),
            ("no_mathlib", lambda m: m.update(packages=m["packages"][1:]), "mathlib")):
        root, node, proj, sfile = setup(tmp)
        m = json.loads(json.dumps(MANIFEST))
        edit(m)
        (proj / "lake-manifest.json").write_text(json.dumps(m), encoding="utf-8")
        probs = lc.manifest_problems(proj)
        check(f"r3_manifest_rejects_{name}", any(word in p for p in probs), str(probs))
        check(f"r3_manifest_rejects_{name}_in_check", failed(result(node), "manifest"), "")
    root, node, proj, sfile = setup(tmp)
    git = proj / ".lake" / "packages" / "mathlib" / ".git"
    git.mkdir(parents=True)
    (git / "HEAD").write_text(MATHLIB_REV + "\n", encoding="utf-8")
    check("r3_checkout_matches_manifest", lc.manifest_problems(proj) == [], str(lc.manifest_problems(proj)))
    (git / "HEAD").write_text("0" * 40 + "\n", encoding="utf-8")
    check("r3_checkout_differs_from_manifest", any("checked out" in p for p in lc.manifest_problems(proj)),
          str(lc.manifest_problems(proj)))
    (git / "HEAD").write_text("ref: refs/heads/master\n", encoding="utf-8")
    (git / "refs" / "heads").mkdir(parents=True)
    (git / "refs" / "heads" / "master").write_text(MATHLIB_REV + "\n", encoding="utf-8")
    check("r3_checkout_symbolic_ref", lc.manifest_problems(proj) == [], str(lc.manifest_problems(proj)))
    # High: LeanCheck/ is rebuilt from empty each run, and nothing may import it.
    root, node, proj, sfile = setup(tmp)
    (proj / "LeanCheck").mkdir()
    (proj / "LeanCheck" / "Planted.lean").write_text("module\n\n#eval 1\n", encoding="utf-8")
    res = result(node)
    check("r3_leancheck_dir_regenerated", res.verdict == "PASS" and not (proj / "LeanCheck" / "Planted.lean").exists(),
          f"{res.verdict} {res.checks}")
    root, node, proj, sfile = setup(tmp, proofs=PROOFS.replace("public import Pkg.Statements.Thing",
                                                                "public import Pkg.Statements.Thing\npublic import LeanCheck.X"))
    check("r3_import_leancheck_forbidden", failed(result(node), "LeanCheck"), str(result(node).checks))
    # High: statement-file names the owner reads are plain: ASCII, undotted, no renaming, no invisible characters.
    for name, extra in (("dotted_helper", "def Nat.succ' (n : ℕ) : ℕ := n"), ("greek_helper", "def ƒ (x : ℝ) : ℝ := x"),
                        ("zero_width", "def f​ (x : ℝ) : ℝ := x"), ("open_renaming", "open Real renaming pi → e"),
                        ("open_hiding", "open Real hiding pi")):
        check(f"r3_statement_rejects_{name}", stmt_problems(extra) != [], str(stmt_problems(extra)))
    # High: Git's usr/bin goes on PATH for comparator (it calls `which`), derived from where git is.
    gitroot = tmp / "Git"
    (gitroot / "cmd").mkdir(parents=True)
    (gitroot / "usr" / "bin").mkdir(parents=True)
    env = lc.tool_env(Path("lake"), {}, which=lambda n: str(gitroot / "cmd" / "git.exe") if n == "git" else None)
    check("r3_git_usr_bin_on_path", str(gitroot / "usr" / "bin") in env["PATH"].split(os.pathsep), env["PATH"][:200])
    # Medium: tool failures inside comparator are UNVERIFIED with the cause kept; proof errors stay FAIL.
    root, node, proj, sfile = setup(tmp)
    res = result(node, runner=fake_runner(comp_rc=1, comp_out="uncaught exception: Child exited with 127\n"
                                                                 "landrun: cannot execute shim"))
    check("r3_tool_failure_unverified", unverified(res, "Child exited") and any("landrun" in d for _, _, d in res.checks),
          str(res.checks))
    res = result(node, runner=fake_runner(comp_rc=1, comp_out="error: Pkg/Proofs/Thing.lean:9:2: unsolved goals\n"
                                                                 "error: build failed\nuncaught exception: Child exited with 1"))
    check("r3_proof_build_error_is_fail", failed(res, "comparator") and "unsolved goals" in str(res.checks), str(res.checks))
    # Medium: a .lake/build that cannot be cleared stops the run (UNVERIFIED), never silently continues.
    root, node, proj, sfile = setup(tmp)
    real = lc.shutil.rmtree
    lc.shutil.rmtree = lambda p, ignore_errors=False: None
    (proj / ".lake" / "build").mkdir(parents=True)
    try:
        res = result(node)
    finally:
        lc.shutil.rmtree = real
    check("r3_uncleared_build_unverified", unverified(res, ".lake/build"), str(res.checks))
    # Low: honest names that look like keywords are fine in proof and helper files (not in the statement file).
    honest = PROOFS.replace("end Pkg", "theorem t (prefix syntax : ℕ) : prefix + syntax = syntax + prefix := by omega\nend Pkg")
    check("r3_proof_binder_named_prefix_ok", lc.scan_source(honest, node_file=False) == [] and
          lc.scan_source(honest.replace("theorem t", "notation \"x\" => 1\ntheorem t"), node_file=False) != [],
          str(lc.scan_source(honest, node_file=False)))
    check("r3_statement_termination_by_ok",
          stmt_problems("def g : ℕ → ℕ\n  | 0 => 0\n  | n + 1 => g n\ntermination_by n => n") == [],
          str(stmt_problems("def g : ℕ → ℕ\n  | 0 => 0\n  | n + 1 => g n\ntermination_by n => n")))


def test_fix_verification_blockers(tmp: Path) -> None:
    """Focused verification of the round-3 fixes (2026-10-12): two residual blockers, plus cheap notes."""
    text = STATEMENTS.replace("public import Mathlib\n", "public import Mathlib public import Pkg.Hidden\n")
    _, problems = lc.parse_statement_file(text, pkg="Pkg")
    check("vf_same_line_second_import", any("Pkg.Hidden" in p for p in problems), str(problems))
    for name, extra in (("renaming_next_line", "open Nat\n  renaming mul → plus"), ("hiding_next_line", "open Real\n  hiding pi"),
                        ("in_next_line", "open Real\n  in\ndef g : ℝ := pi")):
        check(f"vf_open_{name}", stmt_problems(extra) != [], str(stmt_problems(extra)))
    root, node, proj, sfile = setup(tmp)
    m = json.loads(json.dumps(MANIFEST))
    m["packages"][0]["url"] = "https://github.com/leanprover-community/batteries"
    (proj / "lake-manifest.json").write_text(json.dumps(m), encoding="utf-8")
    check("vf_mathlib_url_exact", any("mathlib4" in p for p in lc.manifest_problems(proj)), str(lc.manifest_problems(proj)))
    root, node, proj, sfile = setup(tmp, lean="Mathlib.Thing")
    check("vf_reserved_package_name", failed(result(node), "lean name"), str(result(node).checks))


def test_cli(tmp: Path) -> None:
    root, node, proj, sfile = setup(tmp)

    def cli(args, tools=TOOLS):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = lc.main(args, runner=fake_runner(), lake=Path("lake"), tools=tools)
        return rc, buf.getvalue()
    rc, out = cli([str(node)])
    check("lc_cli_pass_0", rc == 0 and "LEAN CHECK: PASS" in out, f"{rc} {out}")
    rc, out = cli([str(node), "--hash"])
    check("lc_cli_hash", rc == 0 and lc.statement_sha256(sfile) in out, f"{rc} {out}")
    rc, out = cli([str(node)], tools={"comparator": None, "lean4export": None, "landrun": None})
    check("lc_cli_unverified_3", rc == 3, f"{rc} {out}")
    check("lc_cli_usage_2", cli([])[0] == 2)
    check("lc_cli_missing_node_2", cli([str(tmp / "nope.md")])[0] == 2)
    root2, node2, _, _ = setup(tmp, card_sha="2" * 64)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lc.main([str(node2), "--write-report"], runner=fake_runner(), lake=Path("lake"), tools=TOOLS)
    check("lc_cli_fail_1_and_report", rc == 1 and any((node2.parent / "checks" / "prop-thing").glob("lean_check_*.md")),
          buf.getvalue())
    node3 = node.parent / "prop-nolean.md"
    node3.write_text(node.read_text(encoding="utf-8").replace("label: prop:thing", "label: prop:nolean")
                     .replace("lean: Pkg.Thing", "lean:"), encoding="utf-8")
    rc, out = cli([str(node3)])
    check("lc_cli_node_without_lean_2", rc == 2 and "lean:" in out, f"{rc} {out}")


def test_card_fields_ignore_comments(tmp: Path) -> None:
    """A commented-out example field above the real one is not read (as in blueprint_check.header_fields)."""
    root, node, proj, sfile = setup(tmp)
    card = root / "theory" / "blueprint" / "cards" / "prop-thing.md"
    real = card.read_text(encoding="utf-8")
    card.write_text("<!--\nExample header, not the card's own:\n**Node:** prop:example\n"
                    f"**Statement SHA-256:** {'0' * 64}\n-->\n" + real, encoding="utf-8")
    f = lc.card_fields(card)
    check("lc_card_fields_skip_comment", f.get("Node") == "prop:thing"
          and f.get("Statement SHA-256") == lc.statement_sha256(sfile), str(f))
    res = result(node, statements_only=True)
    check("lc_card_check_passes_with_comment", not failed(res, "card"),
          str([c for c in res.checks if c[0] == "card"]))
    card.write_text("```\n**Node:** prop:example\n```\n" + real, encoding="utf-8")
    check("lc_card_fields_skip_fence", lc.card_fields(card).get("Node") == "prop:thing", str(lc.card_fields(card)))
    card.write_text("<!--\n" + real + "-->\n", encoding="utf-8")
    res = result(node, statements_only=True)
    check("lc_card_header_in_comment_fails", failed(res, "card"), str([c for c in res.checks if c[0] == "card"]))


def test_card_template_readable(tmp: Path) -> None:
    """ADR-0005: both checkers read every header field of the card template; its checklist is unmarked."""
    tpl = (Path(__file__).resolve().parent.parent / "templates" / "theory" / "fidelity-card.md").read_text(
        encoding="utf-8")
    card = (tpl.replace("<node label>", "prop:zz-sentinel").replace("<Pkg>.<Name>", "Pkg.Sentinel")
            .replace("<from `python3 bin/lean_check.py <node> --hash`>", "a" * 64))
    f = tmp / "card_template_sentinel.md"
    f.write_text(card, encoding="utf-8")
    want = ("Node", "Node statement hash", "Lean", "Statement SHA-256", "Audited statements",
            "Independent audit", "Verdict", "Signed off")
    lf, bf = lc.card_fields(f), bc.header_fields(f)
    check("lc_template_header_fields_lean_check", all(k in lf for k in want), str(sorted(lf)))
    check("lc_template_header_fields_validator", all(k in bf for k in want), str(sorted(bf)))
    check("lc_template_sha_read", lf.get("Statement SHA-256") == "a" * 64, str(lf.get("Statement SHA-256")))
    prob = bc.checklist_problem(card)
    check("lc_template_checklist_unmarked", prob is not None and "has mark" in prob, str(prob))
    check("lc_template_no_duplicate_fields", bc.duplicated_fields(card, bc.CARD_KEYS) == [],
          str(bc.duplicated_fields(card, bc.CARD_KEYS)))


def main() -> int:
    global bc, lc
    try:
        bc = load("blueprint_check")
        lc = load("lean_check")
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
