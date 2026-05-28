#!/usr/bin/env python3
"""
Unit tests for derive_lib.py (derive-dont-guess detection).

Run:  python3 -m pytest .claude/hooks/test_derive_lib.py -q
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_LIB_PATH = Path(__file__).resolve().parent / "derive_lib.py"
_spec = importlib.util.spec_from_file_location("derive_lib", _LIB_PATH)
lib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lib)


# ---------------------------------------------------------------------------
# language_for_path
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "path,expected",
    [
        ("scripts/01_clean.do", "stata"),
        ("do/helpers/util.doh", "stata"),
        ("scripts/R/fig.R", "r"),
        ("scripts/r/fig.r", "r"),
        ("scripts/sim.py", "python"),
        ("paper/main.tex", "latex"),
        ("README.md", None),
        ("data/raw.csv", None),
        (".claude/settings.json", None),
    ],
)
def test_language_for_path(path, expected):
    assert lib.language_for_path(path) == expected


# ---------------------------------------------------------------------------
# reconstruct_delta
# ---------------------------------------------------------------------------

def test_reconstruct_delta_write():
    assert lib.reconstruct_delta("Write", {"content": "abc"}) == "abc"


def test_reconstruct_delta_edit():
    assert lib.reconstruct_delta("Edit", {"new_string": "xyz"}) == "xyz"


def test_reconstruct_delta_multiedit():
    ti = {"edits": [{"new_string": "a"}, {"new_string": "b"}]}
    assert lib.reconstruct_delta("MultiEdit", ti) == "a\nb"


def test_reconstruct_delta_unknown_tool():
    assert lib.reconstruct_delta("Bash", {"command": "x"}) == ""


# ---------------------------------------------------------------------------
# escape_hatch
# ---------------------------------------------------------------------------

def test_escape_hatch_absent():
    assert lib.escape_hatch("use \"data/x.dta\"") == (False, set())


def test_escape_hatch_bare():
    present, subs = lib.escape_hatch("* derive-ok: trust me\nuse \"x.dta\"")
    assert present is True
    # "trust me" has no comma so it's treated as one substring token
    assert subs == {"trust me"}


def test_escape_hatch_bare_no_reason():
    present, subs = lib.escape_hatch("<!-- derive-ok -->")
    assert present is True
    assert subs == set()


def test_escape_hatch_with_list():
    present, subs = lib.escape_hatch("# derive-ok: a.dta, b.csv")
    assert present is True
    assert subs == {"a.dta", "b.csv"}


# ---------------------------------------------------------------------------
# extract_read_paths — read verbs matched, write verbs NOT matched
# ---------------------------------------------------------------------------

def test_stata_read_verbs():
    text = (
        'use "data/cleaned/main.dta", clear\n'
        'merge 1:1 id using "data/aux.dta"\n'
        'import delimited "raw/extract.csv", clear\n'
        'include "do/helpers/palette.doh"\n'
    )
    paths = lib.extract_read_paths(text, "stata")
    assert "data/cleaned/main.dta" in paths
    assert "data/aux.dta" in paths
    assert "raw/extract.csv" in paths
    assert "do/helpers/palette.doh" in paths


def test_stata_write_verbs_not_matched():
    text = (
        'save "data/out.dta", replace\n'
        'export delimited "out/results.csv", replace\n'
        'esttab using "tables/t1.tex", replace\n'
        'graph export "figures/f1.pdf", replace\n'
        'outreg2 using "tables/t2.tex"\n'
    )
    assert lib.extract_read_paths(text, "stata") == []


def test_r_read_verbs():
    text = (
        'df <- read_csv("data/x.csv")\n'
        'd2 <- readRDS("data/y.rds")\n'
        'source("scripts/R/helpers.R")\n'
    )
    paths = lib.extract_read_paths(text, "r")
    assert set(paths) == {"data/x.csv", "data/y.rds", "scripts/R/helpers.R"}


def test_r_write_verbs_not_matched():
    text = (
        'write_csv(df, "out/x.csv")\n'
        'saveRDS(m, "out/m.rds")\n'
        'ggsave("figures/f.pdf", p)\n'
    )
    assert lib.extract_read_paths(text, "r") == []


def test_python_read_verbs():
    text = (
        'df = pd.read_stata("data/x.dta")\n'
        'arr = np.load("data/a.npy")\n'
        'f = open("config/params.txt")\n'
    )
    paths = lib.extract_read_paths(text, "python")
    assert set(paths) == {"data/x.dta", "data/a.npy", "config/params.txt"}


def test_python_write_open_not_matched():
    # open in write mode must not be flagged
    text = 'f = open("out/log.txt", "w")\n' 'df.to_csv("out/x.csv")\n'
    assert lib.extract_read_paths(text, "python") == []


def test_latex_read_verbs():
    text = (
        "\\input{sections/intro.tex}\n"
        "\\includegraphics[width=0.8\\linewidth]{figures/fig1}\n"
        "\\addbibresource{references.bib}\n"
    )
    paths = lib.extract_read_paths(text, "latex")
    assert "sections/intro.tex" in paths
    assert "figures/fig1" in paths
    assert "references.bib" in paths


# ---------------------------------------------------------------------------
# Stata macro detection
# ---------------------------------------------------------------------------

def test_macro_refs():
    assert lib.macro_refs("$datadir/main.dta") == ["datadir"]
    assert lib.macro_refs("${root}/x.dta") == ["root"]
    assert lib.macro_refs("`tmp'/y.dta") == ["tmp"]
    assert lib.macro_refs("data/plain.dta") == []


def test_repo_defined_macros(tmp_path):
    (tmp_path / "settings.do").write_text(
        'global datadir "/some/path"\nlocal tmpvar = 3\n'
    )
    (tmp_path / "run.do").write_text('tempfile scratch\n')
    macros = lib.repo_defined_macros(tmp_path)
    assert "datadir" in macros
    assert "tmpvar" in macros
    assert "scratch" in macros


# ---------------------------------------------------------------------------
# resolve_path
# ---------------------------------------------------------------------------

def test_resolve_existing_relative(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "x.dta").write_text("")
    ok, _ = lib.resolve_path("data/x.dta", tmp_path, "stata")
    assert ok is True


def test_resolve_missing_relative(tmp_path):
    ok, reason = lib.resolve_path("data/ghost.dta", tmp_path, "stata")
    assert ok is False
    assert "not found" in reason


def test_resolve_dotslash(tmp_path):
    (tmp_path / "f.csv").write_text("")
    ok, _ = lib.resolve_path("./f.csv", tmp_path, "r")
    assert ok is True


def test_resolve_macro_defined(tmp_path):
    ok, _ = lib.resolve_path("$datadir/x.dta", tmp_path, "stata", {"datadir"})
    assert ok is True


def test_resolve_macro_undefined(tmp_path):
    ok, reason = lib.resolve_path("$ghostdir/x.dta", tmp_path, "stata", set())
    assert ok is False
    assert "undefined" in reason


def test_resolve_latex_no_extension(tmp_path):
    (tmp_path / "figures").mkdir()
    (tmp_path / "figures" / "fig1.pdf").write_text("")
    ok, _ = lib.resolve_path("figures/fig1", tmp_path, "latex")
    assert ok is True


def test_resolve_glob(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "wave1.dta").write_text("")
    ok, _ = lib.resolve_path("data/wave*.dta", tmp_path, "stata")
    assert ok is True


# ---------------------------------------------------------------------------
# analyze — end to end
# ---------------------------------------------------------------------------

def test_analyze_flags_fabricated_path(tmp_path):
    ti = {
        "file_path": str(tmp_path / "scripts" / "01.do"),
        "content": 'use "data/cleaned/fabricated.dta", clear\n',
    }
    out = lib.analyze("Write", ti, ti["file_path"], tmp_path)
    assert len(out) == 1
    assert out[0][0] == "data/cleaned/fabricated.dta"


def test_analyze_silent_on_existing(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "real.dta").write_text("")
    ti = {
        "file_path": str(tmp_path / "01.do"),
        "content": 'use "data/real.dta", clear\n',
    }
    assert lib.analyze("Write", ti, ti["file_path"], tmp_path) == []


def test_analyze_silent_on_output_path(tmp_path):
    ti = {
        "file_path": str(tmp_path / "01.do"),
        "content": 'save "data/out/never_made.dta", replace\n',
    }
    assert lib.analyze("Write", ti, ti["file_path"], tmp_path) == []


def test_analyze_escape_hatch_bare(tmp_path):
    ti = {
        "file_path": str(tmp_path / "01.do"),
        "content": '<!-- derive-ok -->\nuse "data/ghost.dta", clear\n',
    }
    assert lib.analyze("Write", ti, ti["file_path"], tmp_path) == []


def test_analyze_escape_hatch_specific(tmp_path):
    # Non-overlapping stems so the substring match targets only the named one.
    ti = {
        "file_path": str(tmp_path / "01.do"),
        "content": (
            "* derive-ok: alpha.dta\n"
            'use "data/alpha.dta", clear\n'
            'use "data/beta.dta", clear\n'
        ),
    }
    out = lib.analyze("Write", ti, ti["file_path"], tmp_path)
    flagged = [p for p, _ in out]
    assert "data/alpha.dta" not in flagged
    assert "data/beta.dta" in flagged


def test_analyze_macro_undefined_flagged(tmp_path):
    ti = {
        "file_path": str(tmp_path / "01.do"),
        "content": 'use "$ghostdir/x.dta", clear\n',
    }
    out = lib.analyze("Write", ti, ti["file_path"], tmp_path)
    assert len(out) == 1
    assert "undefined" in out[0][1]


def test_analyze_macro_defined_silent(tmp_path):
    (tmp_path / "settings.do").write_text('global datadir "/p"\n')
    ti = {
        "file_path": str(tmp_path / "01.do"),
        "content": 'use "$datadir/x.dta", clear\n',
    }
    assert lib.analyze("Write", ti, ti["file_path"], tmp_path) == []


def test_analyze_non_code_file_ignored(tmp_path):
    ti = {
        "file_path": str(tmp_path / "notes.md"),
        "content": 'use "data/ghost.dta"\n',
    }
    assert lib.analyze("Write", ti, ti["file_path"], tmp_path) == []


def test_analyze_multiedit(tmp_path):
    ti = {
        "file_path": str(tmp_path / "01.do"),
        "edits": [
            {"new_string": 'use "data/ghost1.dta", clear\n'},
            {"new_string": 'merge 1:1 id using "data/ghost2.dta"\n'},
        ],
    }
    out = lib.analyze("MultiEdit", ti, ti["file_path"], tmp_path)
    flagged = {p for p, _ in out}
    assert flagged == {"data/ghost1.dta", "data/ghost2.dta"}
