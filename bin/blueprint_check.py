#!/usr/bin/env python3
"""Validate a theory blueprint (ADR-0004; spec 2026-10-11 section 1).

A blueprint is a directory of node files, `<label with ':' -> '-'>.md`, each a
small header between `---` lines plus `## Statement`, `## Proof` and
`## Evidence log` sections. See templates/theory/blueprint-node.md.

Stdlib only; cross-platform. Verdict vocabulary: PASS / UNVERIFIED / FAIL.
"""
from __future__ import annotations

import hashlib
import os
import re
import sys
from datetime import date
from dataclasses import dataclass, field
from pathlib import Path

HEADER_KEYS = ("label", "kind", "status", "uses", "supersedes", "superseded_by",
               "lean", "paper_ref")
REQUIRED_KEYS = ("label", "kind", "status", "uses")

LADDER = ("conjecture", "survived-search", "proved", "checked", "formalized", "verified")
TERMINAL = ("refuted", "conditional", "superseded")
CLAIM_KINDS = ("claim", "variant", "imported")
BASE_KINDS = ("definition", "assumption")
STATUSES_BY_KIND = {
    "definition": ("stated", "superseded"),
    "assumption": ("stated", "superseded"),
    "claim": LADDER + TERMINAL,
    "variant": LADDER + TERMINAL,
    "imported": LADDER[:LADDER.index("checked") + 1] + TERMINAL,
}

LABEL_RE = re.compile(r"^[a-z]+:[a-z0-9][a-z0-9-]*$")
LOG_RE = re.compile(
    r"^- (\d{4}-\d{2}-\d{2}) \| (\S+) -> (\S+) \| ([a-z-]+) \| (.*?) \| "
    r"stmt:([0-9a-f]{12})(?: proof:([0-9a-f]{12}))?$")
SECTION_RE = re.compile(r"^## (Statement|Proof|Evidence log)\s*$")
# Anything a reader could take for one of the three section headings, but isn't exact.
LOOKALIKE_RE = re.compile(r"^\s{0,3}#{1,6}\s*(statement|proof|evidence\s*log)\s*:?\s*$", re.I)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
GAP_RE = re.compile(r"\[\s*gap\s*:", re.I)


class NodeError(Exception):
    """A node file that cannot be parsed into a valid node."""


@dataclass
class LogEntry:
    date: str
    frm: str
    to: str
    actor: str
    locators: list[str]
    stmt_hash: str
    proof_hash: str | None = None


@dataclass
class Node:
    label: str
    kind: str
    status: str
    uses: list[str]
    supersedes: str | None
    superseded_by: str | None
    lean: str | None
    paper_ref: str | None
    statement: str
    proof: str
    log: list[LogEntry] = field(default_factory=list)
    path: Path | None = None


def _normalize(text: str) -> str:
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def statement_hash(text: str) -> str:
    """First 12 hex chars of SHA-256 over the normalized statement text."""
    return hashlib.sha256(_normalize(text).encode("utf-8")).hexdigest()[:12]


def proof_hash(text: str, uses=()) -> str:
    """Hash of what a verifier checked: the normalized proof plus the sorted `uses` labels.

    Covering `uses` means a checked node cannot be repointed at different
    dependencies without re-verification. With no uses it equals statement_hash(text).
    """
    body = _normalize(text)
    if uses:
        body += "\n\x00uses:" + ",".join(sorted(uses))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]


def label_to_filename(label: str) -> str:
    return label.replace(":", "-") + ".md"


def _parse_value(raw: str):
    v = raw.strip()
    if not v:
        return None
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [x.strip() for x in inner.split(",") if x.strip()] if inner else []
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1].strip()
        return v or None
    return v


def parse_node(path: Path) -> Node:
    """Parse one node file; raise NodeError naming the file and the problem."""
    path = Path(path)

    def err(msg: str) -> NodeError:
        return NodeError(f"{path.name}: {msg}")

    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as e:
        raise err(f"cannot read: {e}")
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    if not lines or lines[0].strip() != "---":
        raise err("missing header (first line must be '---')")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise err("unterminated header")

    header: dict = {}
    for ln in lines[1:end]:
        if not ln.strip():
            continue
        if ":" not in ln:
            raise err(f"bad header line: {ln!r}")
        key, _, raw = ln.partition(":")
        key = key.strip()
        if key not in HEADER_KEYS:
            raise err(f"unknown header key {key!r}")
        if key in header:
            raise err(f"duplicate header key {key!r}")
        header[key] = _parse_value(raw)
    for key in REQUIRED_KEYS:
        if header.get(key) is None and key != "uses":
            raise err(f"missing required header key {key!r}")
    if "uses" not in header:
        raise err("missing required header key 'uses'")
    uses = header.get("uses") or []
    if not isinstance(uses, list):
        raise err("'uses' must be a list like [a, b]")
    for key in HEADER_KEYS:
        if key != "uses" and isinstance(header.get(key), list):
            raise err(f"{key!r} must be a scalar")

    label, kind, status = header["label"], header["kind"], header["status"]
    if not LABEL_RE.match(label):
        raise err(f"label {label!r} does not match {LABEL_RE.pattern}")
    if path.name != label_to_filename(label):
        raise err(f"filename must be {label_to_filename(label)!r} for label {label!r}")
    if kind not in STATUSES_BY_KIND:
        raise err(f"unknown kind {kind!r}")
    if status not in STATUSES_BY_KIND[kind]:
        raise err(f"status {status!r} not allowed for kind {kind!r}")

    sections: dict[str, list[str]] = {}
    preamble: list[str] = []
    current = None
    for ln in lines[end + 1:]:
        m = SECTION_RE.match(ln)
        if m:
            current = m.group(1)
            if current in sections:
                raise err(f"duplicate section '## {current}'")
            sections[current] = []
            continue
        if LOOKALIKE_RE.match(ln):
            raise err(f"malformed section heading {ln!r} (use exactly '## Statement', "
                      f"'## Proof' or '## Evidence log')")
        if current is None:
            preamble.append(ln)
        else:
            sections[current].append(ln)
    if COMMENT_RE.sub("", "\n".join(preamble)).strip():
        raise err("text between the header and '## Statement' (only blank lines or "
                  "<!-- comments --> are allowed there)")
    if "Statement" not in sections:
        raise err("missing '## Statement' section")
    if "Evidence log" not in sections:
        raise err("missing '## Evidence log' section")
    if not COMMENT_RE.sub("", "\n".join(sections["Statement"])).strip():
        raise err("empty '## Statement'")

    log: list[LogEntry] = []
    for ln in sections["Evidence log"]:
        if not ln.strip():
            continue
        m = LOG_RE.match(ln.rstrip())
        if not m:
            raise err(f"malformed evidence-log line: {ln!r}")
        date, frm, to, actor, locs, h, ph = m.groups()
        locators = [x.strip() for x in locs.split(";") if x.strip()]
        log.append(LogEntry(date, frm, to, actor, locators, h, ph))

    return Node(
        label=label, kind=kind, status=status, uses=list(uses),
        supersedes=header.get("supersedes"), superseded_by=header.get("superseded_by"),
        lean=header.get("lean"), paper_ref=header.get("paper_ref"),
        statement=_normalize("\n".join(sections["Statement"])),
        proof=_normalize("\n".join(sections.get("Proof", []))),
        log=log, path=path,
    )


# --- Blueprint-level checks (graph, status, evidence) ---------------------------

NON_NODE_FILES = {"STATUS.md", "README.md"}
CHECKED_OR_ABOVE = ("checked", "formalized", "verified")
LINE_SUFFIX_RE = re.compile(r":\d+(-\d+)?$")
DRIVE_RE = re.compile(r"^[A-Za-z]:")          # C:/x and drive-relative C:x
URL_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")
# Windows device names resolve as "existing" anywhere; they are never evidence.
RESERVED_NAMES = {"con", "prn", "aux", "nul", "conin$", "conout$",
                  *(f"com{i}" for i in range(10)), *(f"lpt{i}" for i in range(10))}
REPORT_FIELD_RE = re.compile(r"^\*\*(Reviewer|Target|Score|Proof):\*\*\s*(.*?)\s*$")


@dataclass
class Report:
    verdict: str
    errors: list[str]
    warnings: list[str]
    nodes: dict[str, Node]


def find_repo_root(start: Path) -> Path | None:
    start = Path(start).resolve()
    for p in (start, *start.parents):
        if (p / ".git").exists():
            return p
    return None


def resolve_locator(loc: str, root: Path | None) -> tuple[str, Path]:
    """Classify one evidence locator.

    Returns (state, path) with state one of: "ok" (an existing regular file inside
    the repo), "missing", "directory", "reserved" (a Windows device name), or
    "outside" (absolute, drive-relative, URL, outside the repo, or no repo root;
    unverifiable here, never a pass).
    """
    s = loc.strip().replace("\\", "/")
    if URL_RE.match(s):
        return "outside", Path(s)
    s = LINE_SUFFIX_RE.sub("", s)
    p = Path(s)
    if DRIVE_RE.match(s) or s.startswith("/") or p.is_absolute() or root is None:
        return "outside", p
    for part in s.split("/"):
        if part.split(".")[0].strip().lower() in RESERVED_NAMES:
            return "reserved", p
    full = (root / s).resolve()
    try:
        full.relative_to(root.resolve())
    except ValueError:
        return "outside", full
    if full.is_dir():
        return "directory", full
    return ("ok" if full.is_file() else "missing"), full


def _file_identity(path: Path):
    try:
        st = path.stat()
        return (st.st_dev, st.st_ino) if st.st_ino else str(path.resolve()).lower()
    except OSError:
        return str(path)


def report_fields(path: Path) -> dict[str, str]:
    """The header fields of a review report (first 60 lines)."""
    fields: dict[str, str] = {}
    try:
        with path.open(encoding="utf-8-sig", errors="replace") as fh:
            for _, ln in zip(range(60), fh):
                m = REPORT_FIELD_RE.match(ln.rstrip("\r\n"))
                if m and m.group(1) not in fields:
                    fields[m.group(1)] = m.group(2)
    except OSError:
        pass
    return fields


def _report_problem(path: Path, label: str, proof_h: str | None) -> str | None:
    f = report_fields(path)
    if not f.get("Reviewer", "").startswith("proof-verifier"):
        return "is not a proof-verifier report (no '**Reviewer:** proof-verifier' line)"
    if f.get("Target", "") != label:
        return f"targets {f.get('Target', '(none)')!r}, not {label!r}"
    if f.get("Score", "").strip() != "PASS":
        return f"verdict is {f.get('Score', '(none)')!r}, not PASS"
    if not proof_h or f.get("Proof", "") != proof_h:
        return f"was written for proof {f.get('Proof', '(none)')!r}, not the logged proof {proof_h!r}"
    return None


def classify_transition(kind: str, frm: str, to: str) -> str:
    """'start' | 'up' | 'down' | 'terminal'; raise ValueError if not allowed."""
    if kind in BASE_KINDS:
        if (frm, to) == ("new", "stated"):
            return "start"
        if (frm, to) == ("stated", "superseded"):
            return "terminal"
        raise ValueError(f"{frm} -> {to} not allowed for {kind}")
    if frm == "new":
        if to == "conjecture":
            return "start"
        raise ValueError(f"first entry must be new -> conjecture, got new -> {to}")
    if frm in TERMINAL:
        raise ValueError(f"cannot leave terminal status {frm!r}")
    if frm not in LADDER:
        raise ValueError(f"unknown status {frm!r}")
    if to in TERMINAL:
        return "terminal"
    if to not in LADDER:
        raise ValueError(f"unknown status {to!r}")
    i, j = LADDER.index(frm), LADDER.index(to)
    if j == i + 1:
        return "up"
    if j < i:
        return "down"
    raise ValueError(f"{frm} -> {to} skips or repeats a rung (move up one rung at a time)")


def _find_cycle(nodes: dict[str, Node]) -> list[str] | None:
    """Iterative DFS (no recursion limit); returns one cycle path or None."""
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {k: WHITE for k in nodes}
    for start in sorted(nodes):
        if colour[start] != WHITE:
            continue
        stack: list[tuple[str, int]] = [(start, 0)]
        path: list[str] = [start]
        colour[start] = GREY
        while stack:
            u, i = stack[-1]
            uses = [v for v in nodes[u].uses if v in nodes and v != u]
            if i < len(uses):
                stack[-1] = (u, i + 1)
                v = uses[i]
                if colour[v] == GREY:
                    return path[path.index(v):] + [v]
                if colour[v] == WHITE:
                    colour[v] = GREY
                    stack.append((v, 0))
                    path.append(v)
            else:
                colour[u] = BLACK
                stack.pop()
                path.pop()
    return None


def _check_node(n: Node, nodes: dict[str, Node], bp: Path, root: Path | None,
                errors: list[str], warnings: list[str]) -> None:
    L = n.label
    current_hash = statement_hash(n.statement)

    for u in n.uses:
        if u == L:
            errors.append(f"{L}: uses itself")
        elif u not in nodes:
            errors.append(f"{L}: uses unknown node {u}")

    if not n.log:
        errors.append(f"{L}: evidence log is empty")
    else:
        if n.log[0].frm != "new":
            errors.append(f"{L}: first evidence entry must start from 'new', got {n.log[0].frm!r}")
        if n.log[-1].to != n.status:
            errors.append(f"{L}: status {n.status!r} does not match last evidence entry ({n.log[-1].to!r})")
    if any(e.stmt_hash != current_hash for e in n.log):
        errors.append(f"{L}: statement changed after it was logged (hash now {current_hash}); "
                      f"statements are immutable, create a new node instead")

    node_checks = f"checks/{L.replace(':', '-')}/"
    checks_dir = (bp / node_checks).resolve()
    reviews_dir = (root / "quality_reports" / "reviews").resolve() if root else None
    today = date.today()
    prev_to = None
    prev_date = None
    last_proved_hash = None
    for k, e in enumerate(n.log, 1):
        where = f"{L}: evidence entry {k} ({e.frm} -> {e.to})"
        if prev_to is not None and e.frm != prev_to:
            errors.append(f"{where}: does not continue from previous status {prev_to!r}")
        prev_to = e.to
        try:
            d = date.fromisoformat(e.date)
            if prev_date is not None and d < prev_date:
                errors.append(f"{where}: date {e.date} is earlier than the previous entry")
            if d > today:
                warnings.append(f"{where}: date {e.date} is in the future")
            prev_date = d
        except ValueError:
            errors.append(f"{where}: invalid date {e.date!r}")
        if e.to not in STATUSES_BY_KIND[n.kind]:
            errors.append(f"{where}: status {e.to!r} not allowed for kind {n.kind!r}")
        try:
            move = classify_transition(n.kind, e.frm, e.to)
        except ValueError as ex:
            errors.append(f"{where}: {ex}")
            move = None

        resolved = []
        for loc in e.locators:
            state, full = resolve_locator(loc, root)
            resolved.append((state, full))
            if state == "missing":
                errors.append(f"{where}: evidence locator not found: {loc}")
            elif state == "directory":
                errors.append(f"{where}: evidence locator is a directory, not a file: {loc}")
            elif state == "reserved":
                errors.append(f"{where}: evidence locator is a reserved device name, not a file: {loc}")
            elif state == "outside":
                warnings.append(f"{where}: locator outside the repo, cannot be verified here: {loc}")
        existing = [full for state, full in resolved if state == "ok"]
        unverifiable = any(state == "outside" for state, _ in resolved)

        def unmet(msg: str) -> None:
            # A requirement that might be met by locators we cannot see is UNVERIFIED, not FAIL.
            if unverifiable:
                warnings.append(f"{where}: {msg} (cannot be confirmed: locators outside the repo)")
            else:
                errors.append(f"{where}: {msg}")

        if e.to in ("proved", "checked") and move == "up" and not e.proof_hash:
            errors.append(f"{where}: must record the proof hash (' proof:<hash>' after stmt:)")
        if move == "up":
            if e.to == "survived-search":
                in_checks = []
                for full in existing:
                    try:
                        full.relative_to(checks_dir)
                        in_checks.append(full)
                    except ValueError:
                        pass
                if not in_checks:
                    unmet(f"needs an existing check file under {bp.name}/{node_checks}")
            elif e.to == "proved":
                if e.actor != "theorist":
                    errors.append(f"{where}: only the theorist may set 'proved' (actor {e.actor!r})")
                last_proved_hash = e.proof_hash
            elif e.to == "checked":
                if e.actor != "proof-verifier":
                    errors.append(f"{where}: only proof-verifier may set 'checked' (actor {e.actor!r})")
                if e.proof_hash and last_proved_hash and e.proof_hash != last_proved_hash:
                    errors.append(f"{where}: proof hash {e.proof_hash} differs from the proof that "
                                  f"was logged as proved ({last_proved_hash})")
                valid, seen, problems = 0, set(), []
                for full in existing:
                    ident = _file_identity(full)
                    if ident in seen:
                        problems.append(f"{full.name} is the same file as another report")
                        continue
                    seen.add(ident)
                    try:
                        full.relative_to(reviews_dir)
                        prob = _report_problem(full, L, e.proof_hash)
                    except (ValueError, TypeError):
                        prob = "is not under quality_reports/reviews/"
                    if prob:
                        problems.append(f"{full.name} {prob}")
                    else:
                        valid += 1
                if valid < 2:
                    detail = ("; ".join(problems)) if problems else "none given"
                    unmet(f"needs two distinct proof-verifier PASS reports for this node and "
                          f"this proof ({valid} valid; {detail})")
            elif e.to in ("formalized", "verified"):
                if e.actor != "user":
                    errors.append(f"{where}: only the user may set {e.to!r} (actor {e.actor!r})")
        elif move == "down":
            if not existing:
                unmet("a downgrade needs an existing evidence locator (e.g. the failing report)")
        elif move == "terminal" and e.to == "refuted":
            if not existing:
                unmet("'refuted' needs an existing counterexample or report")

    if n.status in LADDER and LADDER.index(n.status) >= LADDER.index("proved"):
        if not COMMENT_RE.sub("", n.proof).strip():
            errors.append(f"{L}: status {n.status!r} but the proof section is empty")
        if GAP_RE.search(n.proof):
            errors.append(f"{L}: status {n.status!r} but the proof still contains a [GAP: ...] marker")
        logged = [e.proof_hash for e in n.log if e.proof_hash]
        if logged and logged[-1] != proof_hash(n.proof, n.uses):
            errors.append(f"{L}: proof changed after it was logged (hash now {proof_hash(n.proof, n.uses)}); "
                          f"move the node back down and re-verify")

    if n.supersedes and n.supersedes not in nodes:
        errors.append(f"{L}: supersedes names unknown node {n.supersedes}")
    if n.status in ("conditional", "superseded"):
        succ = n.superseded_by
        if not succ:
            errors.append(f"{L}: status {n.status!r} needs superseded_by naming the successor node")
        elif succ == L:
            errors.append(f"{L}: superseded_by names the node itself")
        elif succ not in nodes:
            errors.append(f"{L}: superseded_by names unknown node {succ}")
        elif nodes[succ].status == "refuted":
            errors.append(f"{L}: superseded_by names refuted node {succ}")

    # Terminal nodes are history: what they used no longer matters.
    if n.status not in TERMINAL:
        for u in n.uses:
            dep = nodes.get(u)
            if dep is None or u == L:
                continue
            if dep.status == "refuted":
                errors.append(f"{L}: uses refuted node {u}")
            elif dep.status in ("superseded", "conditional"):
                successor = dep.superseded_by or "(none)"
                warnings.append(f"{L}: uses {dep.status} node {u}; point to its successor {successor}")
            if n.status in CHECKED_OR_ABOVE:
                base_ok = dep.kind in BASE_KINDS and dep.status == "stated"
                claim_ok = dep.kind in CLAIM_KINDS and dep.status in CHECKED_OR_ABOVE
                if not (base_ok or claim_ok):
                    errors.append(f"{L}: is {n.status!r} but depends on {u} at {dep.status!r} "
                                  f"(a checked node may rest only on checked claims or stated "
                                  f"definitions/assumptions)")


def check_blueprint(bp_dir: Path, repo_root: Path | None = None) -> Report:
    """Validate every node in bp_dir. Never raises on bad node files."""
    bp = Path(bp_dir)
    errors: list[str] = []
    warnings: list[str] = []
    nodes: dict[str, Node] = {}
    if not bp.is_dir():
        return Report("FAIL", [f"{bp}: not a directory"], [], {})
    root = Path(repo_root).resolve() if repo_root else find_repo_root(bp)
    if root is None:
        warnings.append(f"{bp}: no enclosing repo (.git) found; evidence locators cannot be verified")

    for path in sorted(bp.glob("*.md")):
        if path.name in NON_NODE_FILES:
            continue
        try:
            n = parse_node(path)
        except NodeError as e:
            errors.append(str(e))
            continue
        if n.label in nodes:
            errors.append(f"{n.label}: duplicate label ({path.name})")
            continue
        nodes[n.label] = n

    if not nodes and not errors:
        errors.append(f"{bp}: no nodes found")
    for label in sorted(nodes):
        _check_node(nodes[label], nodes, bp.resolve(), root, errors, warnings)
    cycle = _find_cycle(nodes)
    if cycle:
        errors.append("dependency cycle: " + " -> ".join(cycle))

    verdict = "FAIL" if errors else ("UNVERIFIED" if warnings else "PASS")
    return Report(verdict, errors, warnings, nodes)


# --- STATUS.md + CLI ----------------------------------------------------------------

def _mermaid_id(label: str) -> str:
    return label.replace(":", "_").replace("-", "_")


def _cell(text: str) -> str:
    return str(text).replace("|", r"\|").replace("\r", " ").replace("\n", " ")


def render_status(report: Report) -> str:
    """Markdown status table plus a Mermaid dependency graph (renders without LaTeX)."""
    out = [f"# Blueprint status — {report.verdict}", "",
           "Generated by `bin/blueprint_check.py --write-status`; do not edit by hand.", "",
           "| label | kind | status | uses |", "|---|---|---|---|"]
    for label in sorted(report.nodes):
        n = report.nodes[label]
        out.append(f"| {_cell(label)} | {_cell(n.kind)} | {_cell(n.status)} | {_cell(', '.join(n.uses))} |")
    out += ["", "```mermaid", "graph TD"]
    for label in sorted(report.nodes):
        n = report.nodes[label]
        out.append(f'  {_mermaid_id(label)}["{label}<br/>{n.status}"]')
    for label in sorted(report.nodes):
        for u in report.nodes[label].uses:
            if u in report.nodes:
                out.append(f"  {_mermaid_id(u)} --> {_mermaid_id(label)}")
    out.append("```")
    if report.errors or report.warnings:
        out += ["", "## Findings", ""]
        out += [f"- ERROR: {_cell(e)}" for e in report.errors]
        out += [f"- WARNING: {_cell(w)}" for w in report.warnings]
    return "\n".join(out) + "\n"


EXIT_CODES = {"PASS": 0, "FAIL": 1, "UNVERIFIED": 3}
USAGE = ("usage: python3 bin/blueprint_check.py <blueprint_dir> [--write-status] [--repo-root DIR]\n"
         "       python3 bin/blueprint_check.py --hashes <node file>")


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    args = list(argv)
    if args[:1] == ["--hashes"]:
        if len(args) != 2:
            print(USAGE)
            return 2
        try:
            n = parse_node(Path(args[1]))
        except NodeError as e:
            print(f"ERROR: {e}")
            return 1
        print(f"stmt:{statement_hash(n.statement)} proof:{proof_hash(n.proof, n.uses)}")
        return 0
    write = "--write-status" in args
    args = [a for a in args if a != "--write-status"]
    root = None
    if "--repo-root" in args:
        i = args.index("--repo-root")
        if i + 1 >= len(args):
            print(USAGE)
            return 2
        root = Path(args[i + 1])
        del args[i:i + 2]
        if not root.is_dir():
            print(f"{USAGE}\nnot a directory: {root}")
            return 2
    if len(args) != 1 or args[0].startswith("-"):
        print(USAGE)
        return 2
    bp = Path(args[0])
    if not bp.is_dir():
        print(f"{USAGE}\nnot a directory: {bp}")
        return 2
    report = check_blueprint(bp, repo_root=root)
    print(f"BLUEPRINT: {report.verdict} ({len(report.nodes)} nodes)")
    for e in report.errors:
        print(f"  ERROR: {e}")
    for w in report.warnings:
        print(f"  WARNING: {w}")
    if write:
        with (bp / "STATUS.md").open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(render_status(report))
        print(f"wrote {bp / 'STATUS.md'}")
    return EXIT_CODES[report.verdict]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
