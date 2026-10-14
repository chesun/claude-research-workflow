#!/usr/bin/env python3
"""Blueprint maintenance tools (ADR-0004), built on bin/blueprint_check.py.

    verify-input <node file> [--out FILE]   blind /theory verify input for a `proved` node
    dependents   <node file>                nodes that use or cite this node
    repoint      <node file> [--apply]      move a superseded/conditional node's dependents
                                            to its successor (dry run without --apply)

Stdlib only; cross-platform. Exit codes: 0 done, 1 refused (reasons printed), 2 usage.
"""
from __future__ import annotations

import dataclasses
import importlib.util
import os
import sys
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
REPOINT_ACTOR = "blueprint-tools"


def load_nodes(bp: Path) -> tuple[dict, dict]:
    """Parse every node file in bp; returns (nodes by label, parse errors by file name)."""
    nodes, errors = {}, {}
    for path in sorted(Path(bp).glob("*.md")):
        if path.name in bc.NON_NODE_FILES:
            continue
        try:
            n = bc.parse_node(path)
        except bc.NodeError as e:
            errors[path.name] = str(e)
            continue
        nodes.setdefault(n.label, n)
    return nodes, errors


def _clean(text: str) -> str:
    """Drop <!-- comments --> so nothing but the mathematics reaches a blind verifier."""
    return bc._normalize(bc.COMMENT_RE.sub("", text))


def _ready(dep) -> bool:
    if dep.kind in bc.BASE_KINDS:
        return dep.status == "stated"
    return dep.status in bc.CHECKED_OR_ABOVE


def _closure(n, nodes: dict) -> list[str]:
    """Every label reachable through `uses` from n (n excluded), in discovery order."""
    seen, stack, out = {n.label}, list(reversed(n.uses)), []
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
        if u in nodes:
            stack.extend(reversed(nodes[u].uses))
    return out


# --- verify-input ------------------------------------------------------------------

def verify_input(node_path: Path) -> tuple[list[str], str]:
    """(problems, text). Text is the blind verifier input; it is empty unless problems is empty.

    Ready means: the node is `proved` with a non-empty, gap-free proof; the validator reports no
    error on it or on anything it rests on; every direct dependency is ready (claims `checked`
    or above, definitions and assumptions `stated`); and every node its statement or proof
    cites is in `uses` or declared as a mention.
    """
    node_path = Path(node_path)
    try:
        n = bc.parse_node(node_path)
    except bc.NodeError as e:
        return [str(e)], ""
    bp = node_path.parent
    nodes, _ = load_nodes(bp)
    problems = []
    if n.status != "proved":
        problems.append(f"{n.label} is at {n.status!r}; verify needs a node at 'proved'")
    if bc.GAP_RE.search(n.proof):
        problems.append(f"{n.label}: the proof still contains a [GAP: ...] marker")
    if not _clean(n.proof):
        problems.append(f"{n.label}: the proof is empty")
    for u in n.uses:
        dep = nodes.get(u)
        if dep is None:
            problems.append(f"{n.label} uses {u}, which has no parseable node file")
        elif not _ready(dep):
            need = "stated" if dep.kind in bc.BASE_KINDS else "checked or above"
            problems.append(f"dependency {u} ({dep.kind}) is at {dep.status!r}, needs {need}")
    for c, where in bc.undeclared_citations(n, nodes):
        problems.append(f"the {where} cites {c}, which is not in uses (add it to uses, or declare "
                        f"<!-- mentions: {c} --> above '## Statement')")
    for m in n.mentions:
        if m not in nodes:
            problems.append(f"mentions {m}, but there is no such node (a typo leaves a dangling label)")
    closure = _closure(n, nodes)
    subjects = {n.label, *closure}
    for e in bc.check_blueprint(bp).errors:
        if e.partition(": ")[0] in subjects:
            problems.append(f"validator: {e}")
        elif e.startswith("dependency cycle:") and subjects & set(e.split(": ", 1)[1].split(" -> ")):
            problems.append(f"validator: {e}")

    # What the verifier is shown: the uses, the definitions/assumptions under them, and (as
    # context only) any other node that the statement, the proof or a shown statement names.
    base = [u for u in closure if u not in n.uses and u in nodes and nodes[u].kind in bc.BASE_KINDS]
    shown = [u for u in [*n.uses, *base] if u in nodes]
    cited = bc.cited_labels("\n".join([n.statement, n.proof, *(nodes[u].statement for u in shown)]))
    named = sorted(c for c in cited if c in nodes and c != n.label and c not in shown)
    texts = [n.statement, n.proof] + [nodes[u].statement for u in [*shown, *named]]
    if any("<!--" in _clean(t) or "-->" in _clean(t) for t in texts):
        problems.append("an HTML comment survives stripping (unbalanced '<!--' / '-->'); fix it so "
                        "no commentary reaches the verifier")
    if problems:
        return problems, ""

    h = bc.proof_hash(n.proof, n.uses)
    used = "\n\n".join(f"**{u} ({nodes[u].kind}).** {_clean(nodes[u].statement)}" for u in n.uses)
    under = "\n\n".join(f"**{u} ({nodes[u].kind}).** {_clean(nodes[u].statement)}" for u in base)
    text = (f"# Blind verification input\n\n"
            f"Copy these two lines into your report header exactly:\n\n"
            f"**Target:** {n.label}\n**Proof:** {h}\n\n"
            f"## Statement under review ({n.label})\n\n{_clean(n.statement)}\n\n"
            f"## Statements of the nodes it uses\n\n{used or 'None.'}\n\n")
    if under:
        text += f"## Definitions and assumptions those results rest on\n\n{under}\n\n"
    if named:
        ctx = "\n\n".join(f"**{c} ({nodes[c].kind}).** {_clean(nodes[c].statement)}" for c in named)
        text += (f"## Nodes named but not used (context only)\n\n"
                 f"The statements or the proof above name these nodes without depending on them. Their results "
                 f"are not established for this proof and are not premises: a step that relies on "
                 f"one is unjustified.\n\n{ctx}\n\n")
    text += f"## Proof submitted for verification\n\n{_clean(n.proof)}\n"
    return [], text


# --- dependents --------------------------------------------------------------------

def dependents(bp: Path, label: str) -> list[tuple]:
    """[(node, 'uses' | 'cites')] for every node that lists label in uses or names it in its text."""
    nodes, _ = load_nodes(bp)
    out = []
    for L in sorted(nodes):
        d = nodes[L]
        if L == label:
            continue
        if label in d.uses:
            out.append((d, "uses"))
        elif label in bc.cited_labels(d.statement + "\n" + d.proof):
            out.append((d, "cites"))
    return out


# --- repoint -----------------------------------------------------------------------

def _rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _rewritten(path: Path, new_uses: list[str] | None, new_status: str | None,
               log_line: str | None) -> bytes:
    """The file's new bytes: `uses`/`status` header lines replaced, one log line appended.

    Each line keeps its own terminator (LF, CRLF or CR); nothing else changes.
    """
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    lines = raw.decode("utf-8-sig").splitlines(keepends=True)
    body = [ln.rstrip("\r\n") for ln in lines]

    def put(i: int, text: str) -> None:
        lines[i] = text + lines[i][len(body[i]):]

    end = next(i for i in range(1, len(body)) if body[i].strip() == "---")
    for i in range(1, end):
        key = body[i].partition(":")[0].strip()
        if key == "uses" and new_uses is not None:
            put(i, f"uses: [{', '.join(new_uses)}]")
        elif key == "status" and new_status:
            put(i, f"status: {new_status}")
    if log_line:
        start = next(i for i, ln in enumerate(body) if ln.strip() == "## Evidence log")
        stop = next((i for i in range(start + 1, len(body)) if bc.SECTION_RE.match(body[i])), len(body))
        last = max((i for i in range(start, stop) if body[i].strip()), default=start)
        term = lines[last][len(body[last]):] or next(
            (ln[len(b):] for ln, b in zip(lines, body) if ln != b), "\n")
        if lines[last] == body[last]:          # the last line had no terminator
            lines[last] += term
        lines.insert(last + 1, log_line + term)
    return (b"\xef\xbb\xbf" if bom else b"") + "".join(lines).encode("utf-8")


def _successor(old, nodes: dict) -> tuple[str | None, list[str], str | None]:
    """(first live successor, chain of labels, problem)."""
    chain, cur = [old.label], old
    while cur.status in ("superseded", "conditional"):
        nxt = cur.superseded_by
        if not nxt or nxt not in nodes:
            return None, chain, f"{cur.label}: superseded_by names no existing node ({nxt!r})"
        if nxt in chain:
            return None, chain, "superseded_by chain loops: " + " -> ".join(chain + [nxt])
        chain.append(nxt)
        cur = nodes[nxt]
        if cur.status == "refuted":
            return None, chain, f"successor {nxt} is refuted"
    return cur.label, chain, None


def _rank(status: str) -> int:
    return bc.LADDER.index(status) if status in bc.LADDER else -1


def repoint(node_path: Path, apply: bool = False) -> tuple[bool, list[str]]:
    """Plan (and with apply=True, make) the move of a retired node's dependents to its successor.

    Direct dependents get their `uses` repointed; one at `proved` or above drops to
    `survived-search` (its proof hash covers `uses`, so the theorist re-proves it). Then every
    node at `checked` or above that rests on a node now below `checked` drops to `proved`: its
    proof and verifier reports stay valid, and it returns to `checked` once its foundations do.
    Proof prose and statements are never edited. Every file is prepared before any is written.
    """
    node_path = Path(node_path)
    try:
        old = bc.parse_node(node_path)
    except bc.NodeError as e:
        return False, [str(e)]
    bp = node_path.parent
    nodes, parse_errors = load_nodes(bp)
    if parse_errors:
        return False, [f"refused: {name} does not parse ({err}); fix it first, since it may use "
                       f"{old.label}" for name, err in sorted(parse_errors.items())]
    if old.status not in ("superseded", "conditional"):
        return False, [f"{old.label} is at {old.status!r}; repoint needs a superseded or conditional node"]
    new, chain, problem = _successor(old, nodes)
    if problem:
        return False, [f"refused: {problem}"]
    root = bc.find_repo_root(bp)
    if root is None:
        return False, [f"refused: {bp} has no enclosing repo (.git), so evidence locators cannot be written"]

    msgs = []
    if len(chain) > 2:
        msgs.append(f"successor chain: {' -> '.join(chain)}")
    if nodes[new].kind != old.kind:
        msgs.append(f"note: the successor {new} is a {nodes[new].kind}, but {old.label} is a {old.kind} "
                    f"(kind changes); check that the dependents still make sense")

    edits: dict[str, dict] = {}            # label -> {"uses", "status", "log", "why"}
    for d, how in dependents(bp, old.label):
        if how != "uses":
            msgs.append(f"note: {d.label} ({d.status}) names {old.label} but does not use it")
            continue
        if d.status in bc.TERMINAL:
            msgs.append(f"skip: {d.label} is {d.status} (terminal; its uses are history)")
            continue
        if d.label == new:
            msgs.append(f"skip: {new} is the successor itself")
            continue
        new_uses = []
        for u in d.uses:
            u = new if u == old.label else u
            if u not in new_uses:
                new_uses.append(u)
        e = {"uses": new_uses, "status": None, "why": f"re-prove against {new}"}
        if _rank(d.status) >= _rank("proved"):
            e["status"] = "survived-search"
        edits[d.label] = e
        if old.label in bc.cited_labels(d.statement):
            msgs.append(f"warning: {d.label}'s statement names {old.label}; statements are immutable, "
                        f"so make a new node if the statement itself depends on it")

    trial = dict(nodes)
    for L, e in edits.items():
        trial[L] = dataclasses.replace(nodes[L], uses=e["uses"], status=e["status"] or nodes[L].status)
    cycle = bc._find_cycle(trial)
    if cycle:
        return False, msgs + ["refused: repointing would create a dependency cycle: " + " -> ".join(cycle)]

    # Cascade: a checked node may rest only on checked claims. Only what this repoint lowers
    # propagates; an unrelated pre-existing error elsewhere is left for the validator to report.
    lowered = {L for L, e in edits.items() if e["status"]}
    changed = True
    while changed:
        changed = False
        for L in sorted(trial):
            t = trial[L]
            if t.status not in bc.CHECKED_OR_ABOVE:
                continue
            low = [u for u in t.uses if u in lowered and trial[u].kind in bc.CLAIM_KINDS
                   and trial[u].status not in bc.CHECKED_OR_ABOVE]
            if low:
                lowered.add(L)
                edits.setdefault(L, {"uses": None})
                edits[L].update(status="proved", why=f"rests on {low[0]}, now {trial[low[0]].status}",
                                cause=low[0])
                trial[L] = dataclasses.replace(t, status="proved")
                changed = True

    # A node that already fails the validator for its own reasons (say, a proof edited after it
    # was logged) is not rewritten: a down-move line would hide the fault.
    own = []
    for e in bc.check_blueprint(bp).errors:
        subject = e.partition(": ")[0]
        if subject in edits and not any(c in e for c in chain):
            own.append(e)
    if own:
        return False, msgs + ["refused: fix these validator errors first:"] + [f"  {e}" for e in own]

    today = date.today()
    retired_locs = [_rel(nodes[c].path, root) for c in chain]
    verb = "" if apply else "would "
    prepared = []
    for L in sorted(edits):
        d, e = nodes[L], edits[L]
        if d.log and e.get("status"):
            try:
                if date.fromisoformat(d.log[-1].date) > today:
                    return False, msgs + [f"refused: {L}'s last evidence entry is dated {d.log[-1].date}, "
                                          f"in the future; a line dated today would break the log order"]
            except ValueError:
                pass
        log_line = None
        if e.get("status"):
            if "cause" in e:
                locs = _rel(nodes[e["cause"]].path, root)
            else:
                locs = ";".join(retired_locs)
            # No proof hash on a down-move: the last logged hash stays the one verifiers checked.
            log_line = (f"- {today.isoformat()} | {d.status} -> {e['status']} | {REPOINT_ACTOR} | {locs} | "
                        f"stmt:{bc.statement_hash(d.statement)}")
        what = []
        if e.get("uses") is not None:
            what.append(f"uses [{', '.join(d.uses)}] -> [{', '.join(e['uses'])}]")
        if e.get("status"):
            what.append(f"{d.status} -> {e['status']} ({e['why']})")
            if d.lean:
                what.append(f"keeps lean: {d.lean}, set when it was {d.status}; the user decides whether "
                            f"the formalization still stands")
        msgs.append(f"{verb}repoint {L}: " + "; ".join(what))
        try:
            data = _rewritten(d.path, e.get("uses"), e.get("status"), log_line)
        except (OSError, UnicodeDecodeError, StopIteration) as ex:
            return False, msgs + [f"refused: cannot prepare {d.path.name}: {ex!r}"]
        if apply and not os.access(d.path, os.W_OK):
            return False, msgs + [f"refused: {d.path.name} is not writable; nothing was written"]
        prepared.append((d.path, data))

    if not edits:
        msgs.append(f"nothing to repoint: no live node uses {old.label}")
    if not apply:
        msgs.append("dry run: nothing written; re-run with --apply")
        return True, msgs

    originals = {}
    try:
        for path, data in prepared:
            originals[path] = path.read_bytes()
            path.write_bytes(data)
    except OSError as ex:
        for path, data in originals.items():
            try:
                path.write_bytes(data)
            except OSError:
                pass
        return False, msgs + [f"refused: write failed ({ex!r}); files already written were restored"]
    return True, msgs


# --- CLI ---------------------------------------------------------------------------

USAGE = ("usage: python3 bin/blueprint_tools.py verify-input <node file> [--out FILE]\n"
         "       python3 bin/blueprint_tools.py dependents <node file>\n"
         "       python3 bin/blueprint_tools.py repoint <node file> [--apply]")


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    args = list(argv)
    if len(args) < 2 or args[0] not in ("verify-input", "dependents", "repoint"):
        print(USAGE)
        return 2
    cmd, target, rest = args[0], Path(args[1]), args[2:]
    if not target.is_file():
        print(f"{USAGE}\nnot a file: {target}")
        return 2

    if cmd == "verify-input":
        out = None
        if rest[:1] == ["--out"] and len(rest) == 2:
            out = Path(rest[1])
            if out.is_dir():
                print(f"{USAGE}\n--out names a directory: {out}")
                return 2
            try:
                out.resolve().relative_to(target.parent.resolve())
                print(f"{USAGE}\n--out may not write inside the blueprint directory: {out}")
                return 2
            except ValueError:
                pass
        elif rest:
            print(USAGE)
            return 2
        problems, text = verify_input(target)
        if problems:
            print("NOT READY for verification:")
            for p in problems:
                print(f"  - {p}")
            return 1
        if out:
            with out.open("w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
            print(f"wrote {out}")
        else:
            print(text, end="")
        return 0

    if cmd == "dependents":
        if rest:
            print(USAGE)
            return 2
        try:
            label = bc.parse_node(target).label
        except bc.NodeError as e:
            print(f"ERROR: {e}")
            return 1
        deps = dependents(target.parent, label)
        for name, err in sorted(load_nodes(target.parent)[1].items()):
            print(f"warning: {name} does not parse, so it is not listed ({err})")
        if not deps:
            print(f"no node uses or cites {label}")
        for d, how in deps:
            tag = " (terminal)" if d.status in bc.TERMINAL else ""
            print(f"{d.label}\t{d.status}{tag}\t{how}")
        return 0

    if rest not in ([], ["--apply"]):
        print(USAGE)
        return 2
    apply = rest == ["--apply"]
    ok, msgs = repoint(target, apply=apply)
    for m in msgs:
        print(m)
    if not ok:
        return 1
    if apply:
        rep = bc.check_blueprint(target.parent)
        print(f"BLUEPRINT: {rep.verdict} ({len(rep.nodes)} nodes)")
        for e in rep.errors:
            print(f"  ERROR: {e}")
        for w in rep.warnings:
            print(f"  WARNING: {w}")
        return 1 if rep.verdict == "FAIL" else 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
