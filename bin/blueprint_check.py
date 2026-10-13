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
# `<!-- mentions: a, b -->` before `## Statement`: labels the node names without using them.
# It sits outside both hashed sections, so declaring a mention never forces re-verification.
MENTIONS_RE = re.compile(r"<!--\s*mentions\s*:(.*?)-->", re.S | re.I)
# A node label cited in prose: not glued to a preceding word, longest match (lem:b-two, not lem:b).
# A leading `_` is allowed so Markdown italics (_lem:b_) still count.
CITED_RE = re.compile(r"(?<![A-Za-z0-9:-])([a-z]+:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)")


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
    mentions: list[str] = field(default_factory=list)


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


def cited_labels(text: str) -> set[str]:
    """Label-shaped tokens in text, ignoring <!-- comments -->. Not all are nodes."""
    return set(CITED_RE.findall(COMMENT_RE.sub(" ", text)))


def undeclared_citations(n: "Node", nodes: dict) -> list[tuple[str, str]]:
    """[(label, 'statement' | 'proof')]: existing nodes cited but in neither uses nor mentions."""
    out, seen = [], set()
    for where, text in (("statement", n.statement), ("proof", n.proof)):
        for c in sorted(cited_labels(text)):
            if (c in nodes and c != n.label and c not in n.uses and c not in n.mentions
                    and c not in seen):
                seen.add(c)
                out.append((c, where))
    return out


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
    mentions: list[str] = []
    for block in MENTIONS_RE.findall("\n".join(preamble)):
        for item in (x.strip() for x in block.split(",")):
            if not item:
                continue
            if not LABEL_RE.match(item):
                raise err(f"mentions: {item!r} is not a node label")
            if item not in mentions:
                mentions.append(item)
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
        log=log, path=path, mentions=mentions,
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


HEADER_FIELD_RE = re.compile(r"^\*\*([A-Za-z0-9 -]+):\*\*\s*(.*?)\s*$")
# lean_check never writes `_1` (the first report of a day has no suffix), so `_1` is not one of its names.
LEAN_REPORT_RE = re.compile(r"^lean_check_(\d{4}-\d{2}-\d{2})(?:_([2-9]|[1-9]\d+))?\.md$")
SIGNED_VERDICTS = ("FAITHFUL", "WITH-NOTED-DIFFERENCES")
# ADR-0005: the owner's signature is bound to the statement it was given for, by the first 12 hex
# of the card's Statement SHA-256.
SIGNED_OFF_RE = re.compile(r"^[A-Za-z][A-Za-z.\-]{0,9}\s+[0-9]{4}-[0-9]{2}-[0-9]{2}\s+sha:([0-9a-fA-F]{12})$")
OLD_SIGNED_OFF_RE = re.compile(r"^[A-Za-z][A-Za-z.\-]{0,9}\s+[0-9]{4}-[0-9]{2}-[0-9]{2}$")
OVERRIDE_RE = re.compile(r"^[A-Za-z][A-Za-z.\-]{0,9}\s+[0-9]{4}-[0-9]{2}-[0-9]{2}\s+sha:([0-9a-fA-F]{12}):\s+\S.*$")
CARD_AUDIT_RE = re.compile(r"^card_audit_([0-9]{4}-[0-9]{2}-[0-9]{2})(?:_([2-9]|[1-9][0-9]+))?\.md$")
MARKS = ("same", "missing", "added", "weaker", "stronger")
CHECKLIST_HEAD_RE = re.compile(r"^##\s+(?:\d+\.\s*)?Checklist\b", re.I)
SECTION_END_RE = re.compile(r"^#{1,2}\s")
FENCE_RE = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.M | re.S)
CARD_KEYS = ("Node", "Node statement hash", "Lean", "Statement SHA-256", "Audited statements",
             "Independent audit", "Verdict", "Signed off", "Audit override")
AUDIT_KEYS = ("Node", "Lean", "Statement SHA-256", "Verdict", "Coverage")


def _visible(text: str) -> str:
    """Markdown with HTML comments and fenced code blocks blanked out, keeping line numbers."""
    blank = lambda m: "\n" * m.group(0).count("\n")
    return FENCE_RE.sub(blank, COMMENT_RE.sub(blank, text.lstrip("﻿").replace("\r\n", "\n")))


def duplicated_fields(text: str, keys: tuple[str, ...]) -> list[str]:
    """Header-field keys that appear as a `**Key:**` line more than once outside comments and code."""
    seen: dict[str, int] = {}
    for ln in _visible(text).splitlines():
        m = HEADER_FIELD_RE.match(ln.strip())
        if m and m.group(1) in keys:
            seen[m.group(1)] = seen.get(m.group(1), 0) + 1
    return [k for k in keys if seen.get(k, 0) > 1]


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def checklist_rows(text: str) -> list[tuple[str, str, str]] | None:
    """(part, number, mark) for each row of the card's checklist tables; None if there is no checklist.

    The checklist is the one `## Checklist` section outside comments and code fences. It runs to the next
    `#` or `##` heading, so `###` sub-headings per part stay inside it. Only tables whose header row starts
    with `Part` and ends with `Mark` are checklist tables; any other table in the section is skipped.
    Raises ValueError if there is more than one checklist section.
    """
    lines = _visible(text).splitlines()
    heads = [i for i, ln in enumerate(lines) if CHECKLIST_HEAD_RE.match(ln.strip())]
    if not heads:
        return None
    if len(heads) > 1:
        raise ValueError(f"the card has {len(heads)} `## Checklist` sections (lines "
                         f"{', '.join(str(i + 1) for i in heads)}); keep exactly one")
    rows: list[tuple[str, str, str]] = []
    in_table = is_checklist = False
    for ln in lines[heads[0] + 1:]:
        s = ln.strip()
        if SECTION_END_RE.match(s):
            break
        if not s.startswith("|"):
            in_table = False
            continue
        cells = _cells(s)
        if not in_table:
            in_table = True
            is_checklist = bool(cells) and cells[0].lower() == "part" and cells[-1].lower() == "mark"
            continue
        if not is_checklist or (cells and all(re.fullmatch(r":?-{3,}:?", c) for c in cells)):
            continue
        rows.append((cells[0] or "?", cells[1] if len(cells) > 1 and cells[1] else "?",
                     cells[-1] if len(cells) >= 5 else ""))
    return rows


def checklist_problem(text: str) -> str | None:
    """None if the card has one checklist with at least one row and every row carries one of MARKS."""
    try:
        rows = checklist_rows(text)
    except ValueError as e:
        return str(e)
    if rows is None:
        return "the card has no `## Checklist` section (ADR-0005: the owner marks a checklist)"
    if not rows:
        return "the card's checklist has no rows"
    for part, num, mark in rows:
        if mark.lower() not in MARKS:
            return (f"checklist part {part} line {num} has mark {mark!r}; expected one of "
                    f"{', '.join(MARKS)}")
    return None


def newest_card_audit(checks_dir: Path) -> Path | None:
    """The newest card_audit report, by the date and counter in its file name."""
    best, key = None, None
    for p in checks_dir.glob("card_audit_*.md") if checks_dir.is_dir() else []:
        m = CARD_AUDIT_RE.match(p.name)
        if m:
            k = (m.group(1), int(m.group(2) or 1))
            if key is None or k > key:
                best, key = p, k
    return best


def header_fields(path: Path) -> dict[str, str]:
    """`**Key:** value` lines in the first 60 lines of a card, audit or lean_check report.

    Lines inside HTML comments and code fences do not count, so a commented-out example field
    (say, a template's sample `Audit override`) is never read as the real one.
    """
    fields: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return fields
    for ln in _visible(text).splitlines()[:60]:
        m = HEADER_FIELD_RE.match(ln.strip())
        if m and m.group(1) not in fields:
            fields[m.group(1)] = m.group(2)
    return fields


def _card_problem(f: dict, n: "Node", card: Path, bp: Path, root: Path | None) -> str | None:
    """Everything a cited fidelity card must satisfy (ADR-0004, ADR-0005), or None."""
    prob = _card_header_problem(f, n)
    if prob:
        return prob
    sha = f["Statement SHA-256"]
    signed = f.get("Signed off", "")
    m = SIGNED_OFF_RE.match(signed)
    if not m:
        if OLD_SIGNED_OFF_RE.match(signed):
            return (f"the card is signed in the pre-ADR-0005 form ({signed!r}); re-sign as "
                    f"`<initials> <date> sha:{sha[:12]}` after the card is converted and audited")
        return (f"the card is not signed off (Signed off {signed!r}; expected "
                f"`<initials> <YYYY-MM-DD> sha:<first 12 of Statement SHA-256>`)")
    if m.group(1).lower() != sha[:12]:
        return (f"the signature is bound to sha:{m.group(1).lower()}, not this card's statement sha:{sha[:12]}; "
                f"the statement changed since it was signed, so the owner re-signs (never repair the prefix)")
    try:
        text = card.read_text(encoding="utf-8-sig", errors="replace")
    except OSError as e:
        return f"cannot read the card ({e})"
    dup = duplicated_fields(text, CARD_KEYS)
    if dup:
        return (f"the card has {', '.join(dup)} more than once; keep exactly one of each header field "
                f"(a reset to PENDING replaces the line, it is not added below it)")
    prob = checklist_problem(text)
    if prob:
        return prob
    if f.get("Verdict") == "FAITHFUL":
        off = [(p, k, mk) for p, k, mk in checklist_rows(text) or [] if mk.lower() != "same"]
        if off:
            p, k, mk = off[0]
            return (f"the verdict is FAITHFUL but checklist part {p} line {k} is marked {mk!r}; FAITHFUL needs "
                    f"every line `same` (use WITH-NOTED-DIFFERENCES and say why in the notes)")
    loc = f.get("Independent audit", "")
    if not loc or loc.upper() == "PENDING":
        return "the card has no `Independent audit:` report (ADR-0005: a card-auditor report is required)"
    state, apath = resolve_locator(loc, root)
    want_dir = (bp / "checks" / label_to_filename(n.label)[:-3]).resolve()
    if state != "ok":
        return f"the card's Independent audit {loc!r} is {state}"
    if apath.resolve().parent != want_dir or not CARD_AUDIT_RE.match(apath.name):
        return (f"the card's Independent audit {loc!r} is not a card_audit_<date>.md report in "
                f"checks/{want_dir.name}/")
    newest = newest_card_audit(want_dir)
    if newest is not None and newest.name != apath.name:
        return (f"the card cites {apath.name}, but a newer audit report {newest.name} exists; the newest audit "
                f"is the one that counts, so cite it (or resolve its finding)")
    try:
        adup = duplicated_fields(apath.read_text(encoding="utf-8-sig", errors="replace"), AUDIT_KEYS)
    except OSError as e:
        return f"cannot read the audit report {apath.name} ({e})"
    if adup:
        return f"the audit report {apath.name} has {', '.join(adup)} more than once; it must have exactly one"
    af = header_fields(apath)
    for key in ("Node", "Lean", "Statement SHA-256"):
        want = n.label if key == "Node" else f.get(key)
        if af.get(key) != want:
            return f"the audit report {apath.name} has {key} {af.get(key, '(none)')!r}, not {want!r}"
    if af.get("Coverage") == "PENDING":
        return (f"the audit report {apath.name} has Coverage 'PENDING'; run the auditor's step 2 (coverage) "
                f"on the card's checklist")
    if af.get("Coverage") != "PASS":
        return (f"the audit report {apath.name} has Coverage {af.get('Coverage', '(none)')!r}; a checklist line is "
                f"missing, so regenerate the checklist and re-run coverage (an override cannot cover this)")
    if af.get("Verdict") not in SIGNED_VERDICTS:
        om = OVERRIDE_RE.match(f.get("Audit override", ""))
        if not om:
            return (f"the audit verdict is {af.get('Verdict', '(none)')!r}; the node stops until the owner "
                    f"decides (an `Audit override: <initials> <date> sha:<12 hex>: <reason>` line, or a fix)")
        if om.group(1).lower() != sha[:12]:
            return f"the Audit override is bound to sha:{om.group(1).lower()}, not this card's sha:{sha[:12]}"
    return None


def _card_header_problem(f: dict, n: "Node") -> str | None:
    if f.get("Node") != n.label:
        return f"the card is for {f.get('Node', '(none)')!r}, not {n.label!r}"
    if not n.lean or f.get("Lean") != n.lean:
        return f"the card's Lean {f.get('Lean', '(none)')!r} differs from the node's lean: {n.lean!r}"
    if f.get("Node statement hash") != statement_hash(n.statement):
        return (f"the card's Node statement hash {f.get('Node statement hash', '(none)')!r} is not the node's "
                f"statement hash {statement_hash(n.statement)} (a card for another statement?)")
    if f.get("Verdict") not in SIGNED_VERDICTS:
        return f"the card's verdict is {f.get('Verdict', '(none)')!r}, not FAITHFUL or WITH-NOTED-DIFFERENCES"
    if not re.fullmatch(r"[0-9a-f]{64}", f.get("Statement SHA-256", "")):
        return "the card has no 64-hex Statement SHA-256"
    return None


def _lean_report_problem(f: dict, n: "Node", mode: str, sha: str, path: Path | None = None) -> str | None:
    if f.get("Node") != n.label or f.get("Lean") != n.lean:
        return f"is for {f.get('Node')!r} / {f.get('Lean')!r}, not {n.label!r} / {n.lean!r}"
    if f.get("Mode") != mode:
        return f"is a {f.get('Mode', '(no mode)')!r} report, not {mode!r}"
    if f.get("Verdict") != "PASS":
        return f"has verdict {f.get('Verdict', '(none)')!r}, not PASS"
    if f.get("Statement SHA-256") != sha:
        return f"was run on statement {f.get('Statement SHA-256')!r}, not the card's {sha!r}"
    # A hollow report (hand-written, or from a run that never reached the tools) is not evidence.
    if not f.get("Toolchain", "").startswith("Lean (version"):
        return f"names no toolchain that ran (Toolchain {f.get('Toolchain', '(none)')!r})"
    if path is not None:
        try:
            body = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            body = ""
        if re.search(r"^- (FAIL|UNVERIFIED) ", body, re.M) or not re.search(r"^- PASS ", body, re.M):
            return "has a FAIL or UNVERIFIED check line (or no check lines) under a PASS verdict"
    return None


def newest_lean_report(checks_dir: Path, mode: str) -> Path | None:
    """The newest lean_check report of a mode, by the date and counter in its file name."""
    best, key = None, None
    for p in checks_dir.glob("lean_check_*.md") if checks_dir.is_dir() else []:
        m = LEAN_REPORT_RE.match(p.name)
        # A report whose Mode cannot be read (hidden in a comment, say) still competes as newest, so the
        # caller sees it and fails on it rather than falling back to an older PASS.
        got = header_fields(p).get("Mode") if m else None
        if not m or (got is not None and got != mode):
            continue
        k = (m.group(1), int(m.group(2) or 1))
        if key is None or k > key:
            best, key = p, k
    return best


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
                card_path = (bp / "cards" / label_to_filename(L)).resolve()
                lean_dir = (bp / "checks" / label_to_filename(L)[:-3]).resolve()
                card = next((p for p in existing if _file_identity(p) == _file_identity(card_path)), None)
                if card is None:
                    unmet(f"needs the node's fidelity card cards/{label_to_filename(L)} as a locator")
                else:
                    cf = header_fields(card)
                    prob = _card_problem(cf, n, card, bp, root)
                    if prob:
                        errors.append(f"{where}: {prob}")
                    else:
                        mode = "statements" if e.to == "formalized" else "full"
                        reports = [p for p in existing if p.parent == lean_dir and LEAN_REPORT_RE.match(p.name)]
                        verdicts = {p: _lean_report_problem(header_fields(p), n, mode, cf["Statement SHA-256"], p)
                                    for p in reports}
                        probs = [f"{p.name} {v}" for p, v in verdicts.items()]
                        if not any(v is None for v in verdicts.values()):
                            detail = "; ".join(probs) if probs else "none given"
                            unmet(f"needs a {mode}-mode lean_check PASS report for the card's statement "
                                  f"({detail})")
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

    if n.status in ("formalized", "verified"):
        if not n.lean:
            errors.append(f"{L}: status {n.status!r} needs a `lean:` header naming its Lean statement file")
        if n.status == "verified":
            # A later failing run (say, after a toolchain bump) takes the node's verification away.
            newest = newest_lean_report((bp / "checks" / label_to_filename(L)[:-3]), "full")
            card = bp / "cards" / label_to_filename(L)
            sha = header_fields(card).get("Statement SHA-256", "") if card.is_file() else ""
            nf = header_fields(newest) if newest else {}
            prob = (_lean_report_problem(nf, n, "full", sha, newest) if newest
                    else "no full-mode lean_check report")
            if prob:
                where = newest.name if newest else "checks/"
                msg = f"{L}: is 'verified' but the newest full lean_check report ({where}) {prob}"
                # A run that could not finish (no tool, time-out) leaves the node unconfirmed, not refuted.
                (warnings if nf.get("Verdict") == "UNVERIFIED" else errors).append(msg)

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
        # A statement or proof that leans on a node missing from `uses` escapes the dependency
        # checks, and its blind verifier never sees that node's statement.
        for c, where in undeclared_citations(n, nodes):
            warnings.append(f"{L}: {where} cites {c}, which is not in uses; add it to uses, or "
                            f"declare <!-- mentions: {c} --> above '## Statement' if it is only named")
        for m in n.mentions:
            if m == L:
                warnings.append(f"{L}: mentions itself")
            elif m not in nodes:
                warnings.append(f"{L}: mentions {m}, but there is no such node")
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
