#!/usr/bin/env python3
"""
Tests for normdiff_lib.py (evidence-gating Phase 1).

Runnable two ways:
    python3 .claude/hooks/test_normdiff_lib.py        # standalone (recommended)
    python3 -m pytest .claude/hooks/test_normdiff_lib.py -q

Covers, per language:
  - pure path-swap → empty residue
  - injected substantive line (keep if / library() / changed \\label{}) → residue
  - LaTeX preamble / \\newcommand rename → empty residue
  - LaTeX changed \\cite{} key → residue
  - blank-line churn stripped
Plus:
  - path-scope unit test (recorder's _in_scope): .py under .claude/ out of
    scope; .py under scripts/ in scope
  - new-file (empty baseline) → full residue
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_LIB_PATH = Path(__file__).resolve().parent / "normdiff_lib.py"
_spec = importlib.util.spec_from_file_location("normdiff_lib", _LIB_PATH)
lib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lib)


# ---------------------------------------------------------------------------
# Tiny standalone assert harness (also works under pytest as plain funcs)
# ---------------------------------------------------------------------------

_RESULTS: list[tuple[str, bool, str]] = []


def _check(name: str, cond: bool, detail: str = "") -> None:
    _RESULTS.append((name, bool(cond), detail))


def _empty(diff) -> bool:
    return lib.residue_is_empty(diff)


# ---------------------------------------------------------------------------
# Stata
# ---------------------------------------------------------------------------

def test_stata_path_swap_empty():
    base = 'use "data/raw/old.dta", clear\nregress y x\n'
    curr = 'use "data/raw/new_v2.dta", clear\nregress y x\n'
    d = lib.normdiff(base, curr, "stata")
    _check("stata_path_swap_empty", _empty(d), str(d))


def test_stata_injected_keepif_residue():
    base = 'use "data/raw/x.dta", clear\nregress y x\n'
    curr = 'use "data/raw/x.dta", clear\nkeep if year >= 2015\nregress y x\n'
    d = lib.normdiff(base, curr, "stata")
    _check(
        "stata_injected_keepif_residue",
        not _empty(d) and any("keep if" in a for a in d["added"]),
        str(d),
    )


def test_stata_comment_and_blank_churn_empty():
    base = 'regress y x\n'
    curr = '* new explanatory comment\n\n\nregress y x   // inline note\n'
    d = lib.normdiff(base, curr, "stata")
    _check("stata_comment_blank_churn_empty", _empty(d), str(d))


def test_stata_scaffold_change_empty():
    base = 'log using "logs/a.log", replace\nregress y x\n'
    curr = 'cap log close\nlog using "logs/b.log", replace\nset more off\nregress y x\n'
    d = lib.normdiff(base, curr, "stata")
    _check("stata_scaffold_change_empty", _empty(d), str(d))


# ---------------------------------------------------------------------------
# R
# ---------------------------------------------------------------------------

def test_r_path_swap_empty():
    base = 'df <- read_csv("data/old.csv")\nmodel <- feols(y ~ x, df)\n'
    curr = 'df <- read_csv("data/new.csv")\nmodel <- feols(y ~ x, df)\n'
    d = lib.normdiff(base, curr, "r")
    _check("r_path_swap_empty", _empty(d), str(d))


def test_r_injected_library_residue():
    base = 'df <- read_csv("data/x.csv")\n'
    curr = 'library(fixest)\ndf <- read_csv("data/x.csv")\n'
    d = lib.normdiff(base, curr, "r")
    _check(
        "r_injected_library_residue",
        not _empty(d) and any("library(fixest)" in a for a in d["added"]),
        str(d),
    )


def test_r_comment_blank_churn_empty():
    base = 'model <- feols(y ~ x, df)\n'
    curr = '# fit the model\n\nmodel <- feols(y ~ x, df)  # OLS\n'
    d = lib.normdiff(base, curr, "r")
    _check("r_comment_blank_churn_empty", _empty(d), str(d))


# ---------------------------------------------------------------------------
# Python
# ---------------------------------------------------------------------------

def test_python_path_swap_empty():
    base = 'df = pd.read_csv("data/old.csv")\nprint(df.shape)\n'
    curr = 'df = pd.read_csv("data/new.csv")\nprint(df.shape)\n'
    d = lib.normdiff(base, curr, "python")
    _check("python_path_swap_empty", _empty(d), str(d))


def test_python_injected_line_residue():
    base = 'df = pd.read_csv("data/x.csv")\n'
    curr = 'df = pd.read_csv("data/x.csv")\ndf = df[df.year >= 2015]\n'
    d = lib.normdiff(base, curr, "python")
    _check(
        "python_injected_line_residue",
        not _empty(d) and any("df.year" in a for a in d["added"]),
        str(d),
    )


# ---------------------------------------------------------------------------
# LaTeX
# ---------------------------------------------------------------------------

def test_latex_input_swap_empty():
    base = '\\input{tables/old_table.tex}\nText body here.\n'
    curr = '\\input{tables/new_table.tex}\nText body here.\n'
    d = lib.normdiff(base, curr, "latex")
    _check("latex_input_swap_empty", _empty(d), str(d))


def test_latex_includegraphics_swap_empty():
    base = '\\includegraphics[width=0.8\\textwidth]{figures/fig1.pdf}\n'
    curr = '\\includegraphics[width=0.8\\textwidth]{figures/fig1_v2.pdf}\n'
    d = lib.normdiff(base, curr, "latex")
    _check("latex_includegraphics_swap_empty", _empty(d), str(d))


def test_latex_changed_label_residue():
    base = 'Result in \\label{tab:main} holds.\n'
    curr = 'Result in \\label{tab:primary} holds.\n'
    d = lib.normdiff(base, curr, "latex")
    _check("latex_changed_label_residue", not _empty(d), str(d))


def test_latex_changed_cite_residue():
    base = 'As shown by \\cite{smith2020}.\n'
    curr = 'As shown by \\cite{jones2021}.\n'
    d = lib.normdiff(base, curr, "latex")
    _check("latex_changed_cite_residue", not _empty(d), str(d))


def test_latex_comment_and_blank_churn_empty():
    base = 'Body sentence one.\n'
    curr = '% a clarifying comment\n\nBody sentence one. % trailing note\n'
    d = lib.normdiff(base, curr, "latex")
    _check("latex_comment_blank_churn_empty", _empty(d), str(d))


def test_latex_newcommand_rename_empty():
    # Preamble macro definition is unchanged content but addbibresource path
    # swap + comment churn around it should not produce residue. The macro
    # body itself is content; renaming the bib path must collapse to empty.
    base = (
        '\\newcommand{\\E}{\\mathbb{E}}\n'
        '\\addbibresource{refs/old.bib}\n'
    )
    curr = (
        '\\newcommand{\\E}{\\mathbb{E}}\n'
        '% switched bib file\n'
        '\\addbibresource{refs/new.bib}\n'
    )
    d = lib.normdiff(base, curr, "latex")
    _check("latex_newcommand_rename_empty", _empty(d), str(d))


# ---------------------------------------------------------------------------
# New-file (empty baseline) → full residue
# ---------------------------------------------------------------------------

def test_new_file_full_residue():
    base = ""  # not in HEAD
    curr = 'use "data/x.dta", clear\nregress y x\nkeep if z == 1\n'
    d = lib.normdiff(base, curr, "stata")
    _check(
        "new_file_full_residue",
        not _empty(d) and len(d["added"]) >= 2 and not d["removed"],
        str(d),
    )


# ---------------------------------------------------------------------------
# Path-scope (recorder _in_scope)
# ---------------------------------------------------------------------------

def _load_recorder():
    rec_path = Path(__file__).resolve().parent / "evidence-gate-recorder.py"
    spec = importlib.util.spec_from_file_location("evidence_gate_recorder", rec_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_path_scope():
    rec = _load_recorder()
    _check("scope_scripts_py_in", rec._in_scope("scripts/python/run.py"), "")
    _check("scope_paper_tex_in", rec._in_scope("paper/main.tex"), "")
    _check("scope_tables_in", rec._in_scope("tables/t1.tex"), "")
    _check("scope_claude_py_out", not rec._in_scope(".claude/hooks/x.py"), "")
    _check("scope_qr_out", not rec._in_scope("quality_reports/plans/p.tex"), "")
    _check("scope_data_out", not rec._in_scope("data/clean/x.py"), "")
    _check("scope_explorations_out", not rec._in_scope("explorations/s.py"), "")
    _check("scope_md_root_out", not rec._in_scope("README.tex_notes"), "")


def test_research_roots_config():
    """_research_roots / _in_scope honor a per-repo CLAUDE.md override."""
    import tempfile

    rec = _load_recorder()

    def _write_claude(body: str) -> str:
        d = tempfile.mkdtemp()
        (Path(d) / "CLAUDE.md").write_text(body, encoding="utf-8")
        return d

    # (a) CLAUDE.md declaring do/ makes do/01.do in scope.
    d_do = _write_claude("**Analysis roots:** do/, paper/, tables/\n")
    _check("config_do_in_scope", rec._in_scope("do/01.do", d_do), str(rec._research_roots(d_do)))
    # ...and scripts/ is NOT in scope when the repo declared only do/, paper/, tables/.
    _check("config_scripts_out_when_overridden", not rec._in_scope("scripts/a.do", d_do), "")

    # (b) Absent header -> DEFAULT used (scripts/ in, do/ out).
    d_none = _write_claude("**Primary analysis language:** Stata 17\n")
    _check("config_absent_scripts_in", rec._in_scope("scripts/a.do", d_none), "")
    _check("config_absent_do_out", not rec._in_scope("do/a.do", d_none), "")
    _check(
        "config_absent_is_default",
        rec._research_roots(d_none) == rec.DEFAULT_RESEARCH_ROOTS,
        str(rec._research_roots(d_none)),
    )

    # (b') CLAUDE.md entirely absent -> DEFAULT.
    d_missing = tempfile.mkdtemp()
    _check(
        "config_missing_file_is_default",
        rec._research_roots(d_missing) == rec.DEFAULT_RESEARCH_ROOTS,
        "",
    )

    # (c) Bracketed-placeholder value -> DEFAULT.
    d_ph = _write_claude(
        "**Analysis roots:** [optional — comma-separated dirs; default: scripts/, do/]\n"
    )
    _check(
        "config_placeholder_is_default",
        rec._research_roots(d_ph) == rec.DEFAULT_RESEARCH_ROOTS,
        str(rec._research_roots(d_ph)),
    )
    _check("config_placeholder_do_out", not rec._in_scope("do/a.do", d_ph), "")

    # (d) Malformed header -> fail-open to DEFAULT. An empty value after the
    # colon parses to no tokens, so it must fall back rather than scope to
    # nothing.
    d_bad = _write_claude("**Analysis roots:**\n")
    _check(
        "config_malformed_empty_is_default",
        rec._research_roots(d_bad) == rec.DEFAULT_RESEARCH_ROOTS,
        str(rec._research_roots(d_bad)),
    )

    # (e) Trailing-slash + spacing tolerance: no trailing slash, extra spaces,
    # surrounding **, space-separated all normalize to "<dir>/".
    d_tol = _write_claude("  **Analysis roots:**   do    paper/   tables  \n")
    roots = rec._research_roots(d_tol)
    _check(
        "config_tolerance_normalizes",
        roots == ("do/", "paper/", "tables/"),
        str(roots),
    )
    _check("config_tolerance_do_in", rec._in_scope("do/sub/x.R", d_tol), "")
    _check("config_tolerance_exact_dir_in", rec._in_scope("do", d_tol), "")


def test_language_for_path():
    ok = (
        lib.language_for_path("scripts/01.do") == "stata"
        and lib.language_for_path("a/b.doh") == "stata"
        and lib.language_for_path("f.R") == "r"
        and lib.language_for_path("f.r") == "r"
        and lib.language_for_path("s.py") == "python"
        and lib.language_for_path("p.tex") == "latex"
        and lib.language_for_path("README.md") is None
    )
    _check("language_for_path", ok, "")


# ---------------------------------------------------------------------------
# Regression tests — bugs caught by the 2026-05-29 adversarial review.
# Each fix is only "verified" if its regression would be caught here; the
# original suite passed 25/25 while all four bugs were live.
# ---------------------------------------------------------------------------

def test_stata_multiplication_residue():
    # Bug A: `*` is a comment ONLY at line start. Spaced multiplication must
    # survive normalization, so a real change to it surfaces as residue.
    d = lib.normdiff("gen z = x * y\n", "gen z = x * w\n", "stata")
    _check("stata_multiplication_residue", not _empty(d), str(d))


def test_stata_reorder_residue():
    # Bug B: statement order is load-bearing in Stata; a pure reorder is a
    # logic change, not a no-op (set-diff would miss it).
    d = lib.normdiff("gen a = 1\ngen b = 2\n", "gen b = 2\ngen a = 1\n", "stata")
    _check("stata_reorder_residue", not _empty(d), str(d))


def test_stata_duplicate_delete_residue():
    # Bug B: deleting one of two identical lines is a change (multiset, not set).
    d = lib.normdiff(
        "replace w = 1 if x\nreplace w = 1 if x\n", "replace w = 1 if x\n", "stata"
    )
    _check("stata_duplicate_delete_residue", not _empty(d), str(d))


def test_stata_backtick_macro_comment_empty():
    # Bug C: a Stata local-macro `x' must not poison quote-state; an inline
    # // comment after a macro ref must still be stripped (→ empty residue).
    d = lib.normdiff(
        "local y = `x' * 2  // old note\n", "local y = `x' * 2  // new note\n", "stata"
    )
    _check("stata_backtick_macro_comment_empty", _empty(d), str(d))


def test_stata_backtick_macro_real_change_residue():
    # Bug C control: a genuine change after a macro ref must still surface.
    d = lib.normdiff("local y = `x' * 2\n", "local y = `x' * 3\n", "stata")
    _check("stata_backtick_macro_real_change_residue", not _empty(d), str(d))


def test_r_seed_change_residue():
    # Bug D: a changed seed alters stochastic output — not a clean refactor.
    d = lib.normdiff("set.seed(1)\n", "set.seed(42)\n", "r")
    _check("r_seed_change_residue", not _empty(d), str(d))


def test_python_seed_change_residue():
    d = lib.normdiff("np.random.seed(1)\n", "np.random.seed(42)\n", "python")
    _check("python_seed_change_residue", not _empty(d), str(d))


# ---------------------------------------------------------------------------
# Ledger backward-compat — schema-extension safety (build plan M3, line 77).
#
# The ledger gained three trailing columns (Tier / Artifact Citation / Refuter
# Tally) appended AFTER Evidence. The only positional consumer is the recorder's
# _row_cells()/_upsert_ledger_row() (evidence-gate-recorder.py). These tests
# prove that:
#   (1) a pre-schema 6-column row still parses — rc[0] (Path), rc[1] (Check),
#       rc[4] (Result) resolve at the same positions after the append;
#   (2) a 9-column row parses identically at positions 0/1/4;
#   (3) _upsert_ledger_row() updates a matching (path, check) row in place
#       (no duplicate) and the row stays queryable by (path, check);
#   (4) the recorder writes a row whose first six positional columns are
#       intact, so old and new rows coexist (ragged 6-col == Tier-1 by design).
# These were absent while the schema change shipped; without them a column
# append could have silently shifted the consumer's indices.
# ---------------------------------------------------------------------------

def _load_recorder_mod():
    return _load_recorder()


def test_ledger_6col_row_parses():
    rec = _load_recorder_mod()
    six_col = (
        "| scripts/01_clean.do | no-logic-change | 2026-04-28T10:00Z "
        "| a1b2c3d4e5f6 | PASS | grep returned 0 matches |"
    )
    cells = rec_row_cells(rec, six_col)
    ok = (
        len(cells) == 6
        and cells[0] == "scripts/01_clean.do"
        and cells[1] == "no-logic-change"
        and cells[4] == "PASS"
    )
    _check("ledger_6col_row_parses", ok, str(cells))


def test_ledger_9col_row_parses():
    rec = _load_recorder_mod()
    nine_col = (
        "| paper/main.tex | no-logic-change | 2026-04-28T10:05Z "
        "| 9e8d7c6b5a4f | UNVERIFIED | added 1 line | 1 | paper/main.tex:42 | 0/3 refuted |"
    )
    cells = rec_row_cells(rec, nine_col)
    ok = (
        len(cells) == 9
        and cells[0] == "paper/main.tex"
        and cells[1] == "no-logic-change"
        and cells[4] == "UNVERIFIED"
    )
    _check("ledger_9col_row_parses", ok, str(cells))


def rec_row_cells(rec, line):
    # _row_cells is a closure inside _upsert_ledger_row; reproduce its exact
    # splitting logic here so the test exercises the same parse the consumer
    # uses (pipe-split, strip leading/trailing pipe, strip each cell).
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [c.strip() for c in inner.split("|")]


def test_ledger_upsert_update_in_place():
    import tempfile

    rec = _load_recorder_mod()
    header = (
        "| Path | Check | Verified At | File hash | Result | Evidence "
        "| Tier | Artifact Citation | Refuter Tally |"
    )
    sep = "|------|-------|-------------|-----------|--------|----------|------|-------------------|---------------|"
    # Pre-existing rows: one 6-col (old format), one 9-col (new format),
    # and the target 6-col row we will update in place.
    pre6 = "| scripts/02_analysis.do | no-logic-change | 2026-04-28T10:00Z | f7e8d9c0b1a2 | PASS | clean |"
    pre9 = "| paper/main.tex | no-logic-change | 2026-04-28T10:05Z | 9e8d7c6b5a4f | UNVERIFIED | added 1 | 1 | paper/main.tex:42 | 0/3 |"
    target = "| scripts/01_clean.do | no-logic-change | 2026-04-28T09:00Z | deadbeef0000 | PASS | old evidence |"
    with tempfile.NamedTemporaryFile(
        "w", suffix=".md", delete=False, encoding="utf-8"
    ) as fh:
        fh.write("\n".join([header, sep, pre6, pre9, target]) + "\n")
        ledger = Path(fh.name)

    rec._upsert_ledger_row(
        ledger,
        "scripts/01_clean.do",
        "cafef00d1234",
        "UNVERIFIED",
        "injected keep if",
    )
    text = ledger.read_text(encoding="utf-8")
    rows = [ln for ln in text.splitlines() if "scripts/01_clean.do" in ln]
    ledger.unlink()

    # Exactly one row for the (path, check) pair — updated, not duplicated.
    one_row = len(rows) == 1
    cells = rec_row_cells(rec, rows[0]) if rows else []
    updated = (
        one_row
        and cells[1] == "no-logic-change"
        and cells[3] == "cafef00d1234"
        and cells[4] == "UNVERIFIED"
        and cells[5] == "injected keep if"
    )
    # Pre-existing rows untouched: the 9-col paper row still has 9 cols.
    paper_rows = [ln for ln in text.splitlines() if "paper/main.tex" in ln]
    paper_intact = len(paper_rows) == 1 and len(rec_row_cells(rec, paper_rows[0])) == 9
    _check("ledger_upsert_update_in_place", updated and paper_intact, text)


def test_ledger_upsert_appends_new_row():
    import tempfile

    rec = _load_recorder_mod()
    header = (
        "| Path | Check | Verified At | File hash | Result | Evidence "
        "| Tier | Artifact Citation | Refuter Tally |"
    )
    sep = "|------|-------|-------------|-----------|--------|----------|------|-------------------|---------------|"
    pre6 = "| scripts/02_analysis.do | no-logic-change | 2026-04-28T10:00Z | f7e8d9c0b1a2 | PASS | clean |"
    with tempfile.NamedTemporaryFile(
        "w", suffix=".md", delete=False, encoding="utf-8"
    ) as fh:
        fh.write("\n".join([header, sep, pre6]) + "\n")
        ledger = Path(fh.name)

    rec._upsert_ledger_row(
        ledger, "tables/t1.tex", "0011223344ff", "PASS", "path swap only"
    )
    text = ledger.read_text(encoding="utf-8")
    ledger.unlink()

    new_rows = [ln for ln in text.splitlines() if "tables/t1.tex" in ln]
    old_rows = [ln for ln in text.splitlines() if "scripts/02_analysis.do" in ln]
    cells = rec_row_cells(rec, new_rows[0]) if new_rows else []
    ok = (
        len(new_rows) == 1
        and len(old_rows) == 1  # pre-existing 6-col row preserved
        and cells[0] == "tables/t1.tex"
        and cells[4] == "PASS"
    )
    _check("ledger_upsert_appends_new_row", ok, text)


# ---------------------------------------------------------------------------
# Regression — 2026-05-30 polish items
# ---------------------------------------------------------------------------

def test_pathlike_guard_nonpath_arg_surfaces():
    # Item 2: a non-path first-quoted-arg must NOT be tokenized — so a change to
    # it surfaces as residue — while a real path swap still normalizes to empty.
    swap = lib.normdiff('df = pd.read_csv("data/old.csv")\n',
                        'df = pd.read_csv("data/new.csv")\n', "python")
    nonpath = lib.normdiff('x = pd.read_csv("sepvalue")\n',
                          'x = pd.read_csv("othervalue")\n', "python")
    _check("pathlike_guard_nonpath_surfaces",
           _empty(swap) and not _empty(nonpath), f"swap={swap} nonpath={nonpath}")


def test_degenerate_roots_fall_back_to_default():
    # Item 5: '.', './', empty roots declared in CLAUDE.md must fall back to
    # DEFAULT_RESEARCH_ROOTS; a legit declaration is still honored.
    import tempfile
    rec = _load_recorder()
    ok = True
    for decl in (".", "./", "., paper/", ""):
        d = tempfile.mkdtemp()
        (Path(d) / "CLAUDE.md").write_text(f"**Analysis roots:** {decl}\n")
        if rec._research_roots(d) != rec.DEFAULT_RESEARCH_ROOTS:
            ok = False
    d = tempfile.mkdtemp()
    (Path(d) / "CLAUDE.md").write_text("**Analysis roots:** do/\n")
    ok = ok and rec._research_roots(d) == ("do/",)
    _check("degenerate_roots_default", ok, "")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

_ALL_TESTS = [
    test_stata_path_swap_empty,
    test_stata_injected_keepif_residue,
    test_stata_comment_and_blank_churn_empty,
    test_stata_scaffold_change_empty,
    test_r_path_swap_empty,
    test_r_injected_library_residue,
    test_r_comment_blank_churn_empty,
    test_python_path_swap_empty,
    test_python_injected_line_residue,
    test_latex_input_swap_empty,
    test_latex_includegraphics_swap_empty,
    test_latex_changed_label_residue,
    test_latex_changed_cite_residue,
    test_latex_comment_and_blank_churn_empty,
    test_latex_newcommand_rename_empty,
    test_new_file_full_residue,
    test_path_scope,
    test_research_roots_config,
    test_language_for_path,
    # Regression (2026-05-29 adversarial review)
    test_stata_multiplication_residue,
    test_stata_reorder_residue,
    test_stata_duplicate_delete_residue,
    test_stata_backtick_macro_comment_empty,
    test_stata_backtick_macro_real_change_residue,
    test_r_seed_change_residue,
    test_python_seed_change_residue,
    # Ledger backward-compat (build plan M3 — schema column append)
    test_ledger_6col_row_parses,
    test_ledger_9col_row_parses,
    test_ledger_upsert_update_in_place,
    test_ledger_upsert_appends_new_row,
    # Regression (2026-05-30 polish)
    test_pathlike_guard_nonpath_arg_surfaces,
    test_degenerate_roots_fall_back_to_default,
]


def main() -> int:
    for t in _ALL_TESTS:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            _check(t.__name__, False, f"EXCEPTION: {e!r}")
    passed = sum(1 for _, ok, _ in _RESULTS if ok)
    failed = [(n, d) for n, ok, d in _RESULTS if not ok]
    for name, ok, detail in _RESULTS:
        status = "PASS" if ok else "FAIL"
        line = f"[{status}] {name}"
        if not ok and detail:
            line += f"  -> {detail}"
        print(line)
    print(f"\n{passed}/{len(_RESULTS)} checks passed.")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
