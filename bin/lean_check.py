#!/usr/bin/env python3
"""Lean evidence for one blueprint node (ADR-0004; plan 2026-10-12 phase 2).

The node's header names its Lean statement file, `lean: <Pkg>.<Name>`, which is
`<project>/<Pkg>/Statements/<Name>.lean`. Every `def <x>_stmt : Prop` there is an audited
statement and must be proved by `theorem <x>` in `<Pkg>/Proofs/<Name>.lean`.

Soundness is judged by Lean FRO's `comparator` (the reference manual's "gold standard").
It builds a Challenge (the signed statements, with `sorry` proofs) and a Solution (the
proofs), exports both compiled environments, checks that every declaration the statements
use is identical in the Solution, checks axioms (only propext, Classical.choice and
Quot.sound), and replays the Solution into the Lean kernel.

`lean_check` adds the checks comparator leaves to its user:
- the whole statement file's SHA-256 against the owner's fidelity card, and the card's list
  of audited statements;
- statement-file readability rules (self-contained, Mathlib imports only, one
  `namespace <Pkg>`, plain definitions only), so that what the owner reads is all there is;
- a canonical `lakefile.toml` and no `lakefile.lean` (comparator trusts the lakefile, so a
  `srcDir` could otherwise point the build at a different statement file);
- a clean project build directory before each run (comparator assumes nothing adversarial
  was compiled before it);
- a scan of every project source for code that runs during a build, syntax extensions,
  axioms and kernel bypasses (defence in depth: on Windows, comparator's sandbox is a shim).

Threat model: this catches mistakes, shortcuts and tricks inside the Lean sources and the
lakefile. It does not protect against an actor with shell access who edits `.lake/packages`,
this script, or the reports.

Verdicts: PASS / FAIL / UNVERIFIED. A missing tool, project or time-out is UNVERIFIED,
never PASS. `--statements-only` (the formalize stage) checks the statement file, its hash
and its build, and does not read the proofs.

Usage: python3 bin/lean_check.py <node file> [--project DIR] [--statements-only]
           [--write-report] [--timeout S] [--hash]
`--timeout` is per tool call. Exit codes: 0 PASS, 1 FAIL, 3 UNVERIFIED, 2 usage.
Stdlib only; never edits the node. Tool paths come from the theory repo's gitignored
`.claude/state/lean.toml` (`project`, `comparator`, `lean4export`, `landrun`) or from the
environment variables COMPARATOR_BIN, COMPARATOR_LEAN4EXPORT and COMPARATOR_LANDRUN.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load_checker():
    if "blueprint_check" in sys.modules:
        return sys.modules["blueprint_check"]
    spec = importlib.util.spec_from_file_location("blueprint_check", HERE / "blueprint_check.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["blueprint_check"] = mod
    spec.loader.exec_module(mod)
    return mod


bc = _load_checker()

ALLOWED_AXIOMS = ("propext", "Quot.sound", "Classical.choice")
CHECK_LIB = "LeanCheck"                     # generated Challenge/Solution modules live here
# Words forbidden anywhere in project sources (outside comments and strings). The first
# group may appear qualified (`debug.skipKernelTC`, `Lean.ofReduceBool`); the second may not
# (so `Foo.extern` is just a name).
FORBIDDEN_QUALIFIED = ("skipKernelTC", "ofReduceBool", "trustCompiler")
FORBIDDEN_BARE = ("native_decide", "implemented_by", "extern")
NODE_ONLY_WORDS = ("sorry", "admit")              # forbidden in the node's own files
# Keywords forbidden anywhere in project sources: they run code during a build, add axioms,
# or leave the kernel's checks.
FORBIDDEN_KEYWORDS = ("axiom", "unsafe", "elab", "elab_rules", "initialize", "builtin_initialize", "run_cmd",
                      "run_elab", "run_meta", "meta", "register_option", "add_decl_doc")
# Syntax extensions: forbidden anywhere in the statement file (what the owner reads); in proof
# and helper files only where a command can start (line start, after `in`, after `]`), so an
# honest binder named `prefix` is fine. comparator judges proofs from the compiled
# environment, so syntax tricks in proofs cannot change its verdict.
SYNTAX_KEYWORDS = ("notation", "notation3", "infix", "infixl", "infixr", "prefix", "postfix", "syntax", "macro",
                   "macro_rules", "declare_syntax_cat", "binder_predicate", "export")
ALLOWED_OPTIONS = ("maxHeartbeats", "maxRecDepth", "synthInstance.maxHeartbeats")
MODIFIERS = {"private", "protected", "noncomputable", "partial", "nonrec", "public", "local", "scoped"}
ZERO_WIDTH_RE = re.compile("[​‌‍⁠﻿­]")
# Statement files: allowed top-level commands, and commands banned at any indentation.
STATEMENT_TOP = {"module", "import", "section", "namespace", "end", "def", "abbrev", "structure", "inductive",
                 "open", "set_option", "", "termination_by", "decreasing_by", "where"}
CANONICAL_URL_RE = re.compile(r"^https://github\.com/(leanprover-community|leanprover)/[A-Za-z0-9._-]+?(\.git)?$")
STATEMENT_BANNED = {"variable", "universe", "instance", "theorem", "lemma", "example", "attribute",
                    "opaque", "class", "deriving", "omit", "include", "mutual"}
LEAN_OPTIONS_OK = re.compile(r"^(pp\..+|autoImplicit|relaxedAutoImplicit|weak\.linter\..+|linter\..+|"
                             r"maxSynthPendingDepth|maxHeartbeats|maxRecDepth)$")
RESERVED_PACKAGES = {"Mathlib", "Lean", "Lake", "Init", "Std", "Batteries", "Aesop", "Qq", "ProofWidgets", "Plausible",
                     "ImportGraph", "LeanSearchClient", "Cli", "LeanCheck"}
LEAN_NAME_RE = re.compile(r"^([A-Z][A-Za-z0-9_]*)\.([A-Z][A-Za-z0-9_]*)$")
ASCII_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_']*$")
MISSING_TOOL_RE = re.compile(r"cannot find the file|no such file|not found|is not recognized|cannot execute", re.I)
LEAN_ERROR_RE = re.compile(r"^error: .+\.lean:\d+:\d+:")
REQUIRED_COMPANIONS = (("_nonvacuous", re.compile(r"_nonvacuous$")),
                       ("_sanity_<k>", re.compile(r"_sanity_[A-Za-z0-9_]+$")),
                       ("_false_variant", re.compile(r"_false_variant$")))
FIELD_RE = re.compile(r"^\*\*([A-Za-z0-9 -]+):\*\*\s*(.*?)\s*$")


class ToolTimeout(Exception):
    """A tool ran past its time limit."""


class UsageError(Exception):
    """Bad arguments, or a node that cannot be checked at all."""


@dataclass
class Result:
    label: str
    lean: str
    mode: str
    checks: list = field(default_factory=list)        # (name, PASS|FAIL|UNVERIFIED, detail)
    sha: str = ""
    proof_sha: str = ""
    toolchain: str = "(not run)"
    mathlib: str = "(unknown)"
    checker: str = "(not run)"

    @property
    def verdict(self) -> str:
        vs = [v for _, v, _ in self.checks]
        return "FAIL" if "FAIL" in vs else ("UNVERIFIED" if "UNVERIFIED" in vs else "PASS")

    def add(self, name: str, verdict: str, detail: str = "") -> None:
        self.checks.append((name, verdict, detail))


# --- Lean text ----------------------------------------------------------------------

def _ident_char(ch: str) -> bool:
    return ch.isalnum() or ch in "_'!?."


def _blank(s: str) -> str:
    return "".join("\n" if ch == "\n" else " " for ch in s)


CHAR_LIT_RE = re.compile(r"'(?:\\(?:x[0-9A-Fa-f]{2}|u[0-9A-Fa-f]{4}|.)|[^\\'\n])'")


def strip_comments_strings(text: str) -> str:
    """Blank out Lean comments (`--`, nested `/- -/`, doc comments), string literals
    (ordinary, raw `r"…"` / `r#"…"#`) and character literals; replace `«…»` names with
    underscores. Newlines are kept, so line structure survives."""
    out, i, n, depth = [], 0, len(text), 0
    while i < n:
        c, nxt = text[i], text[i + 1] if i + 1 < n else ""
        if depth:
            if c == "/" and nxt == "-":
                depth, i = depth + 1, i + 2
            elif c == "-" and nxt == "/":
                depth, i = depth - 1, i + 2
            else:
                out.append("\n" if c == "\n" else " ")
                i += 1
            continue
        if c == "/" and nxt == "-":
            depth, i = 1, i + 2
            continue
        if c == "-" and nxt == "-":
            while i < n and text[i] != "\n":
                i += 1
            continue
        prev = text[i - 1] if i else ""
        if c == "«":
            end = text.find("»", i + 1)
            end = n if end < 0 else end + 1
            out.append("_" * (end - i))
            i = end
            continue
        if c == "r" and not _ident_char(prev):
            j = i + 1
            while j < n and text[j] == "#":
                j += 1
            if j < n and text[j] == '"':
                close = '"' + "#" * (j - i - 1)
                end = text.find(close, j + 1)
                end = n if end < 0 else end + len(close)
                out.append(_blank(text[i:end]))
                i = end
                continue
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(_blank(text[i:j + 1]))
            i = j + 1
            continue
        if c == "'" and not _ident_char(prev):
            m = CHAR_LIT_RE.match(text, i)
            if m:
                out.append(" " * (m.end() - i))
                i = m.end()
                continue
        out.append(c)
        i += 1
    return "".join(out)


def _skip_attrs(s: str) -> tuple[list[str], str]:
    """Leading `@[...]` blocks (bracket-balanced) and the rest of the line."""
    attrs = []
    while s.startswith("@["):
        depth, j = 0, 1
        while j < len(s):
            if s[j] == "[":
                depth += 1
            elif s[j] == "]":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        attrs.append(s[2:j].strip())
        s = s[j + 1:].lstrip()
    return attrs, s


def commands(clean: str):
    """Per non-blank line of comment-stripped text: (line no, column-0?, attrs, head, words, line offset).

    The head is the first word after attributes and modifiers, whatever the indentation.
    """
    offset = 0
    for no, ln in enumerate(clean.split("\n"), 1):
        start = offset
        offset += len(ln) + 1
        s = ln.strip()
        if not s:
            continue
        attrs, rest = _skip_attrs(s)
        words = rest.split()
        while words and words[0] in MODIFIERS:
            words.pop(0)
        yield no, not ln[:1].isspace(), attrs, (words[0] if words else ""), words, start


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def statement_sha256(path: Path) -> str:
    """SHA-256 (64 hex) of the whole file, normalized as the validator does."""
    return hashlib.sha256(bc._normalize(_read(Path(path))).encode("utf-8")).hexdigest()


def _decl_name(words: list[str]) -> str:
    return re.split(r"[\s:({\[]", words[1], maxsplit=1)[0] if len(words) > 1 else ""


def _norm(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def parse_statement_file(text: str, pkg: str | None = None) -> tuple[list[str], list[str]]:
    """(audited statement names without `_stmt`, problems)."""
    clean = strip_comments_strings(_norm(text))
    problems, stmts, inside, seen_ns = [], [], False, False
    for no, top, attrs, head, words, start in commands(clean):
        for a in attrs:
            if a != "expose":
                problems.append(f"line {no}: attribute `@[{a}]` is not allowed in a statement file")
        if head in STATEMENT_BANNED:
            problems.append(f"line {no}: `{head}` is not allowed in a statement file")
            continue
        if top and head not in STATEMENT_TOP and not head.startswith("|"):
            problems.append(f"line {no}: unexpected command `{head}` in a statement file")
            continue
        if head == "in":
            problems.append(f"line {no}: a line starting with `in` (an `open ... in` split across lines) "
                            f"is not allowed in a statement file")
        if head == "set_option" and not (len(words) >= 3 and words[1].startswith("linter.") and words[2] == "false"):
            problems.append(f"line {no}: only `set_option linter.<name> false` is allowed in a statement file")
        if head == "open" and ({"in", "renaming", "hiding"} & set(words) or "→" in words or "->" in words):
            problems.append(f"line {no}: `open ... in/renaming/hiding` is not allowed in a statement file")
        if pkg and head == "namespace":
            ns = words[1] if len(words) > 1 else ""
            if ns != pkg or inside:
                problems.append(f"line {no}: only one `namespace {pkg}` is allowed, not `namespace {ns}`")
            inside, seen_ns = True, True
        if pkg and head == "end" and inside and words[1:2] == [pkg]:
            inside = False
        if head in ("def", "abbrev", "structure", "inductive"):
            name = _decl_name(words)
            if pkg and not inside:
                problems.append(f"line {no}: `{name}` is declared outside `namespace {pkg}`")
            if not ASCII_NAME_RE.match(name):
                problems.append(f"line {no}: `{name}` must be a plain ASCII name without dots, so it cannot "
                                f"pass for, or shadow, another name")
                continue
            if name.endswith("_stmt"):
                pos = clean.find(name, start) + len(name)
                closed = re.match(r"\s*:\s*Prop\s*:=", clean[pos:])
                if head != "def" or not closed or not ASCII_NAME_RE.match(name):
                    problems.append(f"line {no}: `{name}` must be an ASCII-named `def {name} : Prop := ...` "
                                    f"with no parameters")
                else:
                    stmts.append(name[:-len("_stmt")])
    if pkg and not seen_ns:
        problems.append(f"the statement file must declare `namespace {pkg}`")
    # Imports anywhere in the text (Lean accepts indented imports and several on one line).
    for m in re.finditer(r"(?<![\w'.])import\s+(?:all\s+)?([^\s]+)", clean):
        target = m.group(1)
        if not (target == "Mathlib" or target.startswith("Mathlib.")):
            problems.append(f"line {_line(clean, m.start())}: statement files may import only Mathlib, not `{target}`")
    for m in re.finditer(r"(?<![\w'.])(renaming|hiding)(?![\w'])", clean):
        problems.append(f"line {_line(clean, m.start())}: `open ... {m.group(1)}` is not allowed in a statement file")
    for m in ZERO_WIDTH_RE.finditer(_norm(text)):
        problems.append(f"line {_line(_norm(text), m.start())}: invisible character U+{ord(m.group(0)):04X}")
    problems += [p for p in scan_source(text, node_file=True, strict=True)]
    for kind, pat in REQUIRED_COMPANIONS:
        if not any(pat.search(s) for s in stmts):
            problems.append(f"no companion statement named `<name>{kind}_stmt`")
    if not any(not any(pat.search(s) for _, pat in REQUIRED_COMPANIONS) for s in stmts):
        problems.append("no audited part statement (`<name>_part_<x>_stmt`)")
    return stmts, problems


def _line(clean: str, pos: int) -> int:
    return clean.count("\n", 0, pos) + 1


COMMAND_POS = (r"(?m)(?:^[ \t]*|\bin[ \t]+|\][ \t]*)"
               r"(?:(?:private|protected|noncomputable|partial|nonrec|public|local|scoped)[ \t]+)*"
               r"(?:@\[[^\]\n]*\][ \t]*)*")


def scan_source(text: str, node_file: bool, strict: bool = False) -> list[str]:
    """Forbidden words, keywords, `#` commands, imports and options in one project source.

    `strict` (the statement file) bans syntax keywords anywhere; otherwise only where a command
    can start.
    """
    clean = strip_comments_strings(_norm(text))
    found = []
    for tok in FORBIDDEN_QUALIFIED:
        for m in re.finditer(rf"(?<![\w']){re.escape(tok)}(?![\w'])", clean):
            found.append(f"line {_line(clean, m.start())}: forbidden `{tok}`")
    for tok in FORBIDDEN_BARE + (NODE_ONLY_WORDS if node_file else ()) + FORBIDDEN_KEYWORDS:
        for m in re.finditer(rf"(?<![\w'.]){re.escape(tok)}(?![\w'])", clean):
            found.append(f"line {_line(clean, m.start())}: forbidden `{tok}`")
    for tok in SYNTAX_KEYWORDS:
        pat = rf"(?<![\w'.]){re.escape(tok)}(?![\w'])" if strict else rf"{COMMAND_POS}({re.escape(tok)})(?![\w'])"
        for m in re.finditer(pat, clean):
            found.append(f"line {_line(clean, m.end())}: forbidden `{tok}` (syntax extension)")
    for m in re.finditer(r"(?<![\w'.])import\s+(?:all\s+)?(LeanCheck(?:\.[\w.]+)?)\b", clean):
        found.append(f"line {_line(clean, m.start())}: forbidden `import {m.group(1)}` (generated by lean_check)")
    for m in re.finditer(r"\+native\b", clean):
        found.append(f"line {_line(clean, m.start())}: forbidden `+native`")
    for m in re.finditer(r"(?<![\w'.#])#[a-z][A-Za-z_]*", clean):
        found.append(f"line {_line(clean, m.start())}: forbidden command `{m.group(0)}`")
    for m in re.finditer(r"(?<![\w'.])import\s+((?:Lean|Lake)(?:\.[\w.]+)?)\b", clean):
        found.append(f"line {_line(clean, m.start())}: forbidden `import {m.group(1)}` (meta-level library)")
    for m in re.finditer(r"(?<![\w'.])set_option\s+([\w.]+)(\s+\S+)?", clean):
        opt, val = m.group(1), (m.group(2) or "").strip()
        if not (opt in ALLOWED_OPTIONS or (opt.startswith("linter.") and val == "false")):
            found.append(f"line {_line(clean, m.start())}: `set_option {opt}` is not allowed (allowed: "
                         f"{', '.join(ALLOWED_OPTIONS)}, and `linter.<name> false`)")
    return found


def scan_tokens(text: str, allow_sorry: bool) -> list[str]:
    """A node file's scan, with `sorry`/`admit` optionally allowed."""
    return scan_source(text, node_file=not allow_sorry)


def lakefile_problems(proj: Path, pkg: str) -> list[str]:
    """The project's lakefile must be the canonical TOML one (comparator trusts it)."""
    if (proj / "lakefile.lean").exists():
        return ["`lakefile.lean` is not allowed (Lake prefers it over lakefile.toml, and it is code); "
                "use only lakefile.toml"]
    try:
        cfg = tomllib.loads(_read(proj / "lakefile.toml"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as e:
        return [f"lakefile.toml cannot be read: {e}"]
    probs = []
    extra = set(cfg) - {"name", "version", "defaultTargets", "keywords", "leanOptions", "require", "lean_lib"}
    if extra:
        probs.append(f"lakefile.toml has keys outside the canonical set: {', '.join(sorted(extra))}")
    def flat(d, prefix=""):
        # TOML reads `weak.linter.x = true` as nested tables; Lean's option names are dotted.
        out = {}
        for k, v in d.items():
            out.update(flat(v, f"{prefix}{k}.") if isinstance(v, dict) else {f"{prefix}{k}": v})
        return out
    opts = flat(cfg.get("leanOptions", {}))
    for k in ("autoImplicit", "relaxedAutoImplicit"):
        if opts.get(k) is not False:
            probs.append(f"lakefile.toml must set `{k} = false` under [leanOptions]")
    bad = [k for k in opts if not LEAN_OPTIONS_OK.match(k)]
    if bad:
        probs.append(f"leanOptions not allowed: {', '.join(sorted(bad))}")
    reqs = cfg.get("require", [])
    if len(reqs) > 1 or any(set(r) - {"name", "scope", "rev"} or r.get("name") != "mathlib"
                            or r.get("scope") != "leanprover-community" for r in reqs):
        probs.append("[[require]] may only be Mathlib (name = \"mathlib\", scope = \"leanprover-community\", rev)")
    libs = {lib.get("name"): lib for lib in cfg.get("lean_lib", [])}
    want = {pkg: {"name": pkg, "globs": [f"{pkg}.+"]}, CHECK_LIB: {"name": CHECK_LIB, "globs": [f"{CHECK_LIB}.+"]}}
    if libs != want:
        probs.append(f"[[lean_lib]] must be exactly {{name = \"{pkg}\", globs = [\"{pkg}.+\"]}} and "
                     f"{{name = \"{CHECK_LIB}\", globs = [\"{CHECK_LIB}.+\"]}} (no srcDir, roots or extra args)")
    return probs


def _git_head(pkg_dir: Path) -> str | None:
    """The commit a checked-out package is at, read from its .git directory (no git needed)."""
    git = pkg_dir / ".git"
    try:
        head = (git / "HEAD").read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if re.fullmatch(r"[0-9a-f]{40}", head):
        return head
    m = re.match(r"ref:\s*(\S+)", head)
    if not m:
        return None
    ref = git / m.group(1)
    try:
        return ref.read_text(encoding="utf-8").strip()
    except OSError:
        pass
    try:
        for ln in (git / "packed-refs").read_text(encoding="utf-8").splitlines():
            parts = ln.split()
            if len(parts) == 2 and parts[1] == m.group(1):
                return parts[0]
    except OSError:
        pass
    return None


def manifest_problems(proj: Path) -> list[str]:
    """lake-manifest.json must fetch every dependency from its canonical GitHub source, pinned
    to a commit, with Mathlib at the lakefile's version; checked-out copies must be at those commits."""
    try:
        cfg = tomllib.loads(_read(proj / "lakefile.toml"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        cfg = {}
    want_rev = next((r.get("rev") for r in cfg.get("require", []) if r.get("name") == "mathlib"), None)
    path = proj / "lake-manifest.json"
    if not path.is_file():
        return [] if want_rev is None else ["lake-manifest.json is missing, so Mathlib's source is not pinned"]
    try:
        man = json.loads(_read(path))
    except (OSError, ValueError, UnicodeDecodeError) as e:
        return [f"lake-manifest.json cannot be read: {e}"]
    probs = []
    if man.get("packagesDir", ".lake/packages") != ".lake/packages":
        probs.append(f"packagesDir must be .lake/packages, not {man.get('packagesDir')!r}")
    if man.get("lakeDir", ".lake") != ".lake":
        probs.append(f"lakeDir must be .lake, not {man.get('lakeDir')!r}")
    names = set()
    for p in man.get("packages", []):
        name = p.get("name", "?")
        names.add(name)
        if p.get("type") != "git":
            probs.append(f"package {name} must be a git dependency, not {p.get('type')!r}")
        if not CANONICAL_URL_RE.match(str(p.get("url", ""))):
            probs.append(f"package {name} url {p.get('url')!r} is not a leanprover / leanprover-community GitHub repo")
        if p.get("subDir") or p.get("dir"):
            probs.append(f"package {name} may not set subDir or dir")
        if not re.fullmatch(r"[0-9a-f]{40}", str(p.get("rev", ""))):
            probs.append(f"package {name} rev {p.get('rev')!r} is not a pinned 40-hex commit")
        elif (proj / ".lake" / "packages" / name / ".git").exists():
            head = _git_head(proj / ".lake" / "packages" / name)
            if head != p.get("rev"):
                probs.append(f"package {name} is checked out at {head or '(unreadable HEAD)'}, not the manifest's {p.get('rev')}")
        if name == "mathlib" and not re.fullmatch(r"https://github\.com/leanprover-community/mathlib4(\.git)?",
                                                  str(p.get("url", ""))):
            probs.append(f"package mathlib url {p.get('url')!r} is not https://github.com/leanprover-community/mathlib4")
        if name == "mathlib" and want_rev is not None and p.get("inputRev") != want_rev:
            probs.append(f"Mathlib inputRev {p.get('inputRev')!r} is not the lakefile's rev {want_rev!r}")
    if want_rev is not None and "mathlib" not in names:
        probs.append("lake-manifest.json has no mathlib package")
    return probs


# --- tools and config -----------------------------------------------------------------

def resolve_lake(which=shutil.which, home: Path | None = None) -> Path | None:
    """`lake` on PATH, else elan's default home (`~/.elan/bin`)."""
    w = which("lake")
    if w:
        return Path(w)
    home = Path.home() if home is None else Path(home)
    for name in ("lake.exe", "lake"):
        p = home / ".elan" / "bin" / name
        if p.is_file():
            return p
    return None


def tool_env(lake: Path, extra_env: dict | None = None, which=shutil.which) -> dict:
    """The environment for lake and comparator: elan's bin first, and on Windows Git's usr/bin
    (comparator calls `which` and `git`; PowerShell sessions often lack them on PATH)."""
    env = dict(os.environ)
    front = [str(Path(lake).parent)]
    git = which("git")
    if git:
        g = Path(git).resolve() if Path(git).exists() else Path(git)
        for cand in (g.parent.parent / "usr" / "bin", g.parent):
            if cand.is_dir() and str(cand) not in front:
                front.append(str(cand))
    env["PATH"] = os.pathsep.join(front + [env.get("PATH", "")])
    env.update(extra_env or {})
    return env


def _kill_tree(p: subprocess.Popen) -> None:
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True, timeout=60)
        else:
            os.killpg(p.pid, 9)
    except (OSError, subprocess.SubprocessError):
        p.kill()


def real_runner(lake: Path, extra_env: dict | None = None):
    env = tool_env(lake, extra_env)

    def run(cmd, cwd, timeout):
        try:
            p = subprocess.Popen([str(c) for c in cmd], cwd=str(cwd), stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", env=env,
                                 start_new_session=(sys.platform != "win32"))
        except FileNotFoundError:
            return 127, f"{cmd[0]}: not found"
        try:
            out, _ = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill_tree(p)                 # lake and lean children too, not just the top process
            p.communicate()
            raise ToolTimeout(" ".join(str(c) for c in cmd))
        return p.returncode, out or ""
    return run


def _config(repo_root: Path | None) -> dict:
    if repo_root is None:
        return {}
    cfg = repo_root / ".claude" / "state" / "lean.toml"
    try:
        return tomllib.loads(_read(cfg)) if cfg.is_file() else {}
    except (tomllib.TOMLDecodeError, OSError, UnicodeDecodeError):
        return {}


def _cfg_path(repo_root: Path | None, value) -> Path | None:
    if not (isinstance(value, str) and value):
        return None
    p = Path(value)
    return p if p.is_absolute() or repo_root is None else (repo_root / p).resolve()


def project_from_config(repo_root: Path | None) -> Path | None:
    return _cfg_path(repo_root, _config(repo_root).get("project"))


def tools_from_config(repo_root: Path | None) -> dict:
    """comparator, lean4export and landrun paths: lean.toml first, then the environment."""
    cfg = _config(repo_root)
    out = {}
    for key, env in (("comparator", "COMPARATOR_BIN"), ("lean4export", "COMPARATOR_LEAN4EXPORT"),
                     ("landrun", "COMPARATOR_LANDRUN")):
        out[key] = _cfg_path(repo_root, cfg.get(key)) or (Path(os.environ[env]) if os.environ.get(env) else None)
    return out


def card_fields(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    try:
        for ln in _read(path).splitlines()[:60]:
            m = FIELD_RE.match(ln.strip())
            if m and m.group(1) not in fields:
                fields[m.group(1)] = m.group(2)
    except (OSError, UnicodeDecodeError):
        pass
    return fields


def _tail(text: str, n: int = 6) -> str:
    lines = [ln for ln in text.strip().splitlines() if ln.strip() and not ln.startswith("trace:")
             and "NOT REAL LANDRUN" not in ln and not ln.startswith("Exporting #[")]
    return " | ".join(lines[-n:])[:600]


def project_sources(proj: Path, pkg: str) -> list[Path]:
    """Every project `.lean` file except dependencies (`.lake/`) and the generated check library."""
    out = []
    for p in sorted(proj.rglob("*.lean")):
        rel = p.relative_to(proj).parts
        if rel[0] in (".lake", CHECK_LIB):
            continue
        out.append(p)
    return out


# --- the check ------------------------------------------------------------------------

def check_node(node_path: Path, project: Path | None = None, statements_only: bool = False,
               timeout: int = 1800, runner=None, lake: Path | None = None, home: Path | None = None,
               which=shutil.which, tools: dict | None = None) -> Result:
    node_path = Path(node_path)
    try:
        node = bc.parse_node(node_path)
    except bc.NodeError as e:
        raise UsageError(str(e))
    if not node.lean:
        raise UsageError(f"{node.label}: the node has no `lean:` header (set it to <Pkg>.<Name>)")
    res = Result(node.label, node.lean, "statements" if statements_only else "full")
    m = LEAN_NAME_RE.match(node.lean)
    if not m:
        res.add("lean name", "FAIL", f"`lean: {node.lean}` must be <Pkg>.<Name>, e.g. Bdd.NstarAC")
        return res
    pkg, name = m.groups()
    if pkg in RESERVED_PACKAGES:
        res.add("lean name", "FAIL", f"package `{pkg}` is reserved: a project called that could pass its own "
                                     f"modules off as the library's")
        return res

    root = bc.find_repo_root(node_path.parent)
    proj = Path(project) if project else project_from_config(root)
    if proj is None:
        res.add("project", "UNVERIFIED", "no Lean project configured (--project DIR or "
                                         ".claude/state/lean.toml `project = ...`)")
        return res
    if not proj.is_dir():
        res.add("project", "UNVERIFIED", f"the Lean project path does not exist: {proj}")
        return res
    if lake is None:
        lake = resolve_lake(which=which, home=home)
    if lake is None:
        res.add("toolchain", "UNVERIFIED", "lake not found on PATH or in ~/.elan/bin")
    tools = tools if tools is not None else tools_from_config(root)

    def read(p: Path) -> str | None:
        try:
            return _read(p)
        except UnicodeDecodeError:
            res.add("encoding", "FAIL", f"{p.relative_to(proj).as_posix()} is not UTF-8")
        except OSError as e:
            res.add("read", "FAIL", f"cannot read {p.name}: {e}")
        return None

    # Static checks: lakefile, statement file, hash, card, proofs, every project source.
    probs = lakefile_problems(proj, pkg)
    res.add("lakefile", "FAIL" if probs else "PASS", "; ".join(probs) if probs else "canonical lakefile.toml")
    probs = manifest_problems(proj)
    res.add("manifest", "FAIL" if probs else "PASS", "; ".join(probs) if probs else
            "every dependency is a pinned leanprover / leanprover-community GitHub repo, checked out at its pin")
    sfile = proj / pkg / "Statements" / f"{name}.lean"
    pfile = proj / pkg / "Proofs" / f"{name}.lean"
    if not sfile.is_file():
        res.add("statement file", "FAIL", f"no statement file {pkg}/Statements/{name}.lean")
        return res
    stext = read(sfile)
    if stext is None:
        return res
    stmts, problems = parse_statement_file(stext, pkg=pkg)
    res.add("statement file", "FAIL" if problems else "PASS",
            "; ".join(problems) if problems else f"{len(stmts)} audited statements: {', '.join(stmts)}")
    res.sha = statement_sha256(sfile)
    card = node_path.parent / "cards" / bc.label_to_filename(node.label)
    if not card.is_file():
        res.add("card", "FAIL", f"no fidelity card at {card.parent.name}/{card.name}")
    else:
        f = card_fields(card)
        bad = []
        if f.get("Node") != node.label:
            bad.append(f"card Node is {f.get('Node')!r}, not {node.label!r}")
        if f.get("Node statement hash") != bc.statement_hash(node.statement):
            bad.append(f"card Node statement hash {f.get('Node statement hash')!r} is not the node's "
                       f"{bc.statement_hash(node.statement)} (python3 bin/blueprint_check.py --hashes <node>)")
        if f.get("Lean") != node.lean:
            bad.append(f"card Lean is {f.get('Lean')!r}, not {node.lean!r}")
        if f.get("Statement SHA-256") != res.sha:
            bad.append(f"card Statement SHA-256 {f.get('Statement SHA-256')!r} differs from the statement "
                       f"file's {res.sha} (edited after the card was written?)")
        listed = {x.strip() for x in f.get("Audited statements", "").split(",") if x.strip()}
        if not listed:
            bad.append("the card has no `Audited statements` line listing every `<x>` of the statement file")
        elif listed != set(stmts):
            bad.append(f"card Audited statements {sorted(listed)} differ from the statement file's {sorted(stmts)}")
        res.add("card", "FAIL" if bad else "PASS", "; ".join(bad) if bad else "card matches node, Lean, SHA-256 "
                                                                         "and the audited statements")
    if not statements_only:
        if not pfile.is_file():
            res.add("proof file", "FAIL", f"no proof file {pkg}/Proofs/{name}.lean")
            return res
        ptext = read(pfile)
        if ptext is None:
            return res
        res.proof_sha = statement_sha256(pfile)
        found = scan_source(ptext, node_file=True)
        pclean = strip_comments_strings(_norm(ptext))
        if not re.search(rf"^\s*(?:public\s+)?import\s+{re.escape(pkg)}\.Statements\.{re.escape(name)}\s*$",
                         pclean, re.M):
            found.append(f"the proof file must import {pkg}.Statements.{name}")
        res.add("proof file", "FAIL" if found else "PASS", "; ".join(found) if found else "imports its statements; "
                                                                                       "no forbidden tokens")
    others = []
    for src in project_sources(proj, pkg):
        if src in (sfile, pfile):
            continue
        text = read(src)
        if text is None:
            continue
        for prob in scan_source(text, node_file=False):
            others.append(f"{src.relative_to(proj).as_posix()} {prob}")
    res.add("project files", "FAIL" if others else "PASS",
            "; ".join(others[:20]) if others else "no code run during builds, syntax extensions, axioms or "
                                                  "kernel bypasses")

    try:
        manifest = json.loads(_read(proj / "lake-manifest.json"))
        res.mathlib = next((p.get("rev", "?") for p in manifest.get("packages", []) if p.get("name") == "mathlib"),
                           "(no mathlib)")
    except (OSError, ValueError, UnicodeDecodeError):
        pass
    if lake is None or res.verdict == "FAIL":
        return res                                  # do not build a project that already failed

    missing = [k for k in ("comparator", "lean4export", "landrun") if not statements_only
               and not (tools.get(k) and (runner is not None or Path(tools[k]).is_file()))]
    run = runner or real_runner(lake, {"COMPARATOR_LEAN4EXPORT": str(tools.get("lean4export") or ""),
                                       "COMPARATOR_LANDRUN": str(tools.get("landrun") or "")})
    try:
        rc, out = run([lake, "env", "lean", "--version"], proj, 120)
        # Lake may print `info:` lines first; the version line is the one Lean prints.
        version = next((ln.strip() for ln in out.splitlines() if ln.strip().startswith("Lean (version")), None)
        res.toolchain = version if rc == 0 and version else f"(lean --version failed: {_tail(out)})"
        # Comparator assumes nothing adversarial was compiled before it: start from clean
        # project build outputs (dependencies in .lake/packages are kept), and from an empty
        # generated library, so nothing planted there is built.
        for d in (proj / ".lake" / "build", proj / CHECK_LIB):
            shutil.rmtree(d, ignore_errors=True)
            if d.exists():
                res.add("clean", "UNVERIFIED", f"could not clear {d.relative_to(proj).as_posix()} (a file is locked?); "
                                               f"comparator needs a clean start, so nothing was checked")
                return res
        if statements_only:
            target = f"{pkg}.Statements.{name}"
            rc, out = run([lake, "build", target], proj, timeout)
            res.add("build", "PASS" if rc == 0 else "FAIL",
                    f"lake build {target}" if rc == 0 else f"`lake build {target}` failed: {_tail(out)}")
            return res
        if missing:
            res.add("comparator", "UNVERIFIED", f"not configured or not found: {', '.join(missing)} "
                                                f"(set them in .claude/state/lean.toml)")
            return res
        chk = proj / CHECK_LIB
        chk.mkdir()
        challenge = "".join(f"theorem {pkg}.{s} : {pkg}.{s}_stmt := sorry\n" for s in stmts)
        (chk / f"{name}Challenge.lean").write_text(
            f"module\n\npublic import {pkg}.Statements.{name}\n\npublic section\n\n{challenge}",
            encoding="utf-8", newline="\n")
        (chk / f"{name}Solution.lean").write_text(f"module\n\npublic import {pkg}.Proofs.{name}\n",
                                                  encoding="utf-8", newline="\n")
        config = chk / f"{name}.comparator.json"
        config.write_text(json.dumps({"challenge_module": f"{CHECK_LIB}.{name}Challenge",
                                      "solution_module": f"{CHECK_LIB}.{name}Solution",
                                      "theorem_names": [f"{pkg}.{s}" for s in stmts],
                                      "permitted_axioms": list(ALLOWED_AXIOMS)}, indent=2), encoding="utf-8")
        res.checker = f"comparator ({Path(tools['comparator']).name})"
        rc, out = run([lake, "env", tools["comparator"], config], proj, timeout)
        if rc == 0 and "Your solution is okay" in out:
            res.add("comparator", "PASS", "every proof proves exactly its signed statement, uses only "
                                          f"{', '.join(ALLOWED_AXIOMS)}, and the kernel accepts the solution")
        elif (errs := [ln.strip() for ln in out.splitlines() if LEAN_ERROR_RE.match(ln.strip())]):
            res.add("comparator", "FAIL", "the proofs do not compile: " + " | ".join(errs[:6])[:600])
        elif rc == 127 or MISSING_TOOL_RE.search(out) or "Child exited" in out:
            # A tool inside comparator failed (shim, lean4export, git): no verdict on the proofs.
            res.add("comparator", "UNVERIFIED", f"comparator could not run its tools: {_tail(out, 8)}")
        else:
            reason = next((ln.strip() for ln in out.splitlines() if "uncaught exception" in ln), _tail(out))
            res.add("comparator", "FAIL", reason)
    except ToolTimeout as e:
        res.add("time limit", "UNVERIFIED", f"timed out after {timeout}s: {e}")
    return res


# --- report and CLI -------------------------------------------------------------------

def render_report(res: Result) -> str:
    out = [f"# lean_check — {res.label}", "",
           f"**Node:** {res.label}", f"**Lean:** {res.lean}", f"**Statement SHA-256:** {res.sha}",
           f"**Proof SHA-256:** {res.proof_sha or '(not read)'}",
           f"**Mode:** {res.mode}", f"**Verdict:** {res.verdict}", f"**Toolchain:** {res.toolchain}",
           f"**Mathlib:** {res.mathlib}", f"**Checker:** {res.checker}", "", "## Checks", ""]
    out += [f"- {v} — {name}: {detail}" for name, v, detail in res.checks]
    return "\n".join(out) + "\n"


def write_report(res: Result, node_path: Path, today: date | None = None) -> Path:
    """Write a dated report beside the node's other evidence; never overwrite one."""
    d = Path(node_path).parent / "checks" / bc.label_to_filename(res.label)[:-3]
    d.mkdir(parents=True, exist_ok=True)
    stamp = (today or date.today()).isoformat()
    path, k = d / f"lean_check_{stamp}.md", 1
    while path.exists():
        k += 1
        path = d / f"lean_check_{stamp}_{k}.md"
    with path.open("x", encoding="utf-8", newline="\n") as fh:
        fh.write(render_report(res))
    return path


USAGE = ("usage: python3 bin/lean_check.py <node file> [--project DIR] [--statements-only] "
         "[--write-report] [--timeout S] [--hash]")
EXIT = {"PASS": 0, "FAIL": 1, "UNVERIFIED": 3}


def main(argv: list[str], runner=None, lake: Path | None = None, tools: dict | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    args = list(argv)
    flags = {"--statements-only", "--write-report", "--hash"}
    opts = {f: f in args for f in flags}
    args = [a for a in args if a not in flags]
    vals = {}
    for key in ("--project", "--timeout"):
        if key in args:
            i = args.index(key)
            if i + 1 >= len(args):
                print(USAGE)
                return 2
            vals[key] = args[i + 1]
            del args[i:i + 2]
    if len(args) != 1 or args[0].startswith("-"):
        print(USAGE)
        return 2
    node = Path(args[0])
    if not node.is_file():
        print(f"{USAGE}\nnot a file: {node}")
        return 2
    try:
        timeout = int(vals.get("--timeout", 1800))
    except ValueError:
        print(USAGE)
        return 2
    project = Path(vals["--project"]) if "--project" in vals else None
    try:
        if opts["--hash"]:
            n = bc.parse_node(node)
            m = LEAN_NAME_RE.match(n.lean or "")
            proj = project or project_from_config(bc.find_repo_root(node.parent))
            if not m or proj is None:
                print("ERROR: needs `lean: <Pkg>.<Name>` on the node and a configured Lean project")
                return 2
            sfile = proj / m.group(1) / "Statements" / f"{m.group(2)}.lean"
            if not sfile.is_file():
                print(f"ERROR: no statement file {sfile}")
                return 1
            print(statement_sha256(sfile))
            return 0
        res = check_node(node, project=project, statements_only=opts["--statements-only"], timeout=timeout,
                         runner=runner, lake=lake, tools=tools)
    except (UsageError, bc.NodeError) as e:
        print(f"{USAGE}\n{e}")
        return 2
    print(f"LEAN CHECK: {res.verdict} ({res.mode}) — {res.label} [{res.lean}]")
    for name, v, detail in res.checks:
        print(f"  {v}: {name}: {detail}")
    if opts["--write-report"]:
        print(f"wrote {write_report(res, node)}")
    return EXIT[res.verdict]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
