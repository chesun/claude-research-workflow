# ADR-0005 validator Review — red-team
**Date:** 2026-10-14
**Reviewer:** red-team critic (independent, general-purpose agent)
**Target:** bin/blueprint_check.py, bin/test_blueprint_check.py
**Score:** 60/100
**Status:** Active

## Verdict

The bound-signature and audit-locator plumbing is solid: `..` traversal, URLs, symlinked or relocated audit files, wrong-directory and `_1`-suffixed names, lowercase `pass` Coverage, mixed-case verdicts, empty override reasons, uppercase card SHA, and header fields pushed below line 60 all fail closed, with clear messages; the suite's 166 tests pass, and no crash input was found. The weak point is `checklist_rows` (bin/blueprint_check.py:351-368): it is a raw line scanner that neither strips HTML comments or code fences nor distinguishes heading levels, and it accepts only the *first* `## Checklist` heading. Five independent probes made the validator PASS a card that should FAIL — including FAITHFUL cards whose checklist contains a `weaker` mark — using only the card-format mistakes the threat model names (an agent-drafted card with a commented/fenced template block, a `###` sub-heading per part, a second checklist heading, or a `#`-prefixed prose line). The duplicate-header-field behavior (first wins, no error) also silently defeats ADR-0005's "formalizer resets `Signed off`/`Verdict` to PENDING" protection when the reset is appended rather than edited in place. These are deterministic Tier-1 bypasses of the change's central new control, so the change should not land until the checklist extraction is hardened.

Repro harness used by all findings (synthetic sentinels only; run from the repo root):

```bash
py -I - <<'EOF'
import importlib.util, sys, tempfile
from pathlib import Path
def load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s)
    sys.modules[n] = m; s.loader.exec_module(m); return m
bc = load("blueprint_check", Path("bin/blueprint_check.py"))
t = load("tbc", Path("bin/test_blueprint_check.py")); t.bc = bc
tmp = Path(tempfile.mkdtemp())
def node_at(form):
    root, bp = t.mkrepo(tmp)
    log = t.climb("formalized", root, "prop:a", t.PROOF)
    i = next(k for k, e in enumerate(log) if e[1] == "formalized")
    log[i] = log[i][:3] + (form(root),)
    t.write_node(bp, "prop:a", status="formalized", proof=t.PROOF, log=log, lean=t.LEAN)
    return t.verdict(bp, root)
def form_with(**kw):
    return lambda root: (t.write_card(root, "prop:a", **kw) + ";"
                         + t.write_lean_report(root, "prop:a", mode="statements"))
# F1: checklist only inside an HTML comment -> PASS (should FAIL)
commented = ("<!--\n## Checklist (template)\n\n|Part|#|Lean clause|Reading|Mark|\n"
             "|---|---|---|---|---|\n| (a) | 1 | `0 < s0` | sentinel | same |\n-->\n")
print("F1", node_at(form_with(checklist=commented)).verdict)                      # PASS
print("F1b", node_at(form_with(checklist=commented + "\n" + t.checklist("same", "weaker"))).verdict)  # PASS
# F2: '###' sub-heading hides a weaker row from the FAITHFUL gate -> PASS
sub = (t.checklist("same") + "\n### Part (b)\n\n|Part|#|Lean clause|Reading|Mark|\n"
       "|---|---|---|---|---|\n| (b) | 1 | `c-b` | sentinel | weaker |\n")
print("F2", node_at(form_with(checklist=sub)).verdict)                            # PASS
print("F2b", node_at(form_with(checklist=t.checklist("same").rstrip()
      + "\n#1 note\n| (a) | 2 | `c2` | r | weaker |\n")).verdict)                 # PASS
# F3: second '## Checklist' heading ignored -> PASS
print("F3", node_at(form_with(checklist=t.checklist("same") + "\n" + t.checklist("same", "weaker"))).verdict)
# F4: appended PENDING reset ignored (first field wins)
def dup(root):
    loc = form_with()(root); card = root / loc.split(";")[0]
    card.write_text(card.read_text(encoding="utf-8").replace("\n## Checklist",
        "\n**Verdict:** PENDING\n**Signed off:** PENDING\n**Independent audit:** PENDING\n\n## Checklist"),
        encoding="utf-8")
    return loc
print("F4", node_at(dup).verdict)                                                 # PASS
# F5: glossary table after the checklist (no heading between) -> FAIL on a legitimate card
good = t.checklist("same") + "\n**Glossary**\n\n| Lean | Means |\n|---|---|\n| `s0` | prior variance |\n"
print("F5", node_at(form_with(checklist=good)).verdict)                           # FAIL (false positive)
EOF
```

Observed output: `F1 PASS`, `F1b PASS`, `F2 PASS`, `F2b PASS`, `F3 PASS`, `F4 PASS`, `F5 FAIL` (error: `checklist part Lean line Means has mark ''`).

## Findings

| # | Rank | Finding | Evidence | Verdict | Recommendation |
|---|------|---------|----------|---------|----------------|
| 1 | Critical | `CHECKLIST_HEAD_RE` matches a `## Checklist` line inside an HTML comment or fenced code block, and the rows inside it are read as the owner's marks. A commented-out or fenced template block (a realistic agent-drafted-card residue; the current `templates/theory/fidelity-card.md` already carries a long `<!-- -->` block in exactly that position) satisfies the checklist requirement with no real checklist, and masks a real checklist below it that contains a `weaker` row under a FAITHFUL verdict. | Repro F1/F1b above (both PASS); `bin/blueprint_check.py:353-367` scans raw lines; contrast `parse_node`, which strips `COMMENT_RE` (`:218`). | WRONG (validator PASSes a card that must FAIL) | In `checklist_rows`, strip `COMMENT_RE` and fenced ``` blocks before scanning (the comment regex already exists at `:43`); add regression tests. |
| 2 | Critical | The row scan breaks at *any* line starting with `#` (`:360-361`). A `###` sub-heading per part — a natural way for the back-translator to structure a multi-part checklist — or a `#`-prefixed prose line hides every later row from both the mark check and the FAITHFUL-all-same gate, so a FAITHFUL card with `weaker`/`missing` marks in part (b) PASSes. | Repro F2/F2b above (both PASS). | WRONG | Break only on a level-1/2 heading (`^##?[^#]` after strip), or on the next `SECTION`-style `## ` heading; include `###` content in the scan; add a test with a weaker row after `### Part (b)`. |
| 3 | High | A second `## Checklist` heading is silently ignored: the parser takes the first section only. A stale or template all-`same` checklist left above the owner's real one (which carries non-`same` marks) wins, and the FAITHFUL gate reads the wrong table. | Repro F3 above (PASS); `:354` takes `next(...)` over the first match. | WRONG | Return a problem ("more than one `## Checklist` section") when the heading matches twice, mirroring `parse_node`'s duplicate-section error (`:207-208`). |
| 4 | High | `header_fields` keeps the *first* occurrence of a duplicated field and never errors (`:392-393`), unlike `parse_node`, which rejects duplicate header keys (`:175-176`). ADR-0005 relies on the formalizer "resetting `Verdict`, `Signed off` and `Independent audit` to PENDING" to invalidate a card; if the reset is *appended* below the existing lines (a classic agent edit mistake), the old bound signature and FAITHFUL verdict still win and the card stays valid. Same first-wins behavior on the audit report's `Statement SHA-256`. | Repro F4 above (PASS with `**Verdict:** PENDING`, `**Signed off:** PENDING`, `**Independent audit:** PENDING` present in the card); probe R4 (duplicate audit SHA, first wins) PASSed likewise. | WRONG | For the ADR-0005-critical keys (`Signed off`, `Verdict`, `Statement SHA-256`, `Independent audit`, `Audit override`), detect duplicates in `_card_problem` (and for the audit file) and return a problem; or make `header_fields` report duplicates to callers. |
| 5 | Medium | The section-end rule is also too greedy in the fail-closed direction: any later table in the same section (a glossary or notes table after the checklist, separated only by bold text or prose) is parsed as checklist rows, FAILing a legitimate card with the confusing message `checklist part Lean line Means has mark ''`. Separator rows with fewer than 3 dashes (`|:-:|`, `|-|`) are likewise flagged as data rows. | Repro F5 above (FAIL, false positive); `:358-367`. | SOUND (false positive, not a bypass) | Fixing #2's end-of-section rule plus requiring the 5-column shape (or anchoring on the checklist's own header row) removes this; at minimum improve the message. Keep the template's checklist section free of trailing tables until then. |
| 6 | Medium | No newest-audit rule: the card cites one audit report, and an older FAITHFUL audit stays valid after a newer UNFAITHFUL re-audit of the same statement (same SHA, so no re-sign is forced). This contrasts with the validator's own newest-wins principle for lean reports ("a later failing run takes the node's verification away", `:737-748`). Matches ADR-0005's letter, so a spec-level gap, not an implementation bug. | Probe R7: card citing `card_audit_..._2.md` (FAITHFUL) PASSes with `card_audit_....md` (UNFAITHFUL) present in the same directory. | WEAK (spec-conformant; hurried-owner window is real) | Consider checking the newest `card_audit_*` in the node's checks dir the way `verified` checks the newest full lean report; or record the accepted residue in the ADR's Known limits. |
| 7 | Low | `\d` in `SIGNED_OFF_RE`/`OVERRIDE_RE` (`:343`, `:345`) matches non-ASCII digits, so a fullwidth-digit "date" signs cleanly. Harmless today (the date is never interpreted; the sha group is ASCII-only `[0-9a-fA-F]`), but a latent trap if date logic is ever added. | Probe Q11: `Signed off: CS ２０２６-１０-１２ sha:<correct 12>` → PASS. | SOUND (cosmetic) | Use `[0-9]` instead of `\d`, matching the node-label regexes' ASCII discipline. |
| 8 | Low | A checklist row of entirely empty cells (`| | | | | |`) is skipped as a separator (`:365`: the `all(...)` over non-empty cells is vacuously true) instead of being flagged as an unmarked row. An empty row carries no Lean clause, so nothing is hidden; rows with an empty *mark* but content are correctly flagged (test `ln_checklist_empty_mark_named`). | Probe Q9: `checklist_problem` on a table whose only row is all-empty returns "no rows" rather than naming the row. | SOUND (minor) | Treat an all-empty row as a bad row, or leave as-is; cosmetic either way. |

## Probes that held (fail-closed, no finding)

- **Audit locator:** `..` traversal to another node's dir, URL, subdirectory of the right dir, `card_audit_<date>_1.md`, audit in `cards/` — all FAIL (`:432-438`); backslash paths and `:line` suffixes resolve to the right file and PASS (benign). Symlinks are neutralized structurally: `resolve_locator` and the `apath.resolve().parent != want_dir` check operate on the resolved target (`:305`, `:436`), and the deliberate-forgery actor is outside ADR-0005's threat model.
- **Signature:** old `initials date` form gets the dedicated re-sign message; wrong 12-hex prefix FAILs with "never repair the prefix"; uppercase prefix and runs of spaces PASS; uppercase card SHA FAILs at the 64-hex check; trailing junk after the sha FAILs.
- **Audit header:** fields below line 60 FAIL (Node `(none)`); `Coverage: pass` and `Verdict: Faithful` case variants FAIL; `Coverage: FAIL` is not overridable; override with empty/whitespace reason FAILs; override bound to the wrong prefix FAILs.
- **Marks/FAITHFUL:** pipes and escaped pipes inside backticked Lean clauses parse correctly because the mark is read from the last cell (`:367`); `Same`/trailing-space marks accepted; a FAITHFUL card whose only non-`same` row is `missing` FAILs; CRLF+BOM cards PASS.
- **Robustness:** six malformed-checklist crash probes (NUL byte, lone pipes, heading at EOF) returned problems without raising; the `verified` path replays the same card rules (`ln_verified_replays_card_rules`); `py -I bin/test_blueprint_check.py` → 166 passed, 0 failed.

## Test-suite gaps (bin/test_blueprint_check.py)

The new tests cover the happy paths and the single-field mutations well, but none of the five bypass shapes above: no test for a checklist inside a comment/fence, a `###` sub-heading or duplicate `## Checklist`, duplicated header fields, or a trailing table in the checklist section. A numbered heading (`## 2. Checklist`) is accepted by `CHECKLIST_HEAD_RE` but untested. Add regression tests alongside the fixes for findings 1-4.
