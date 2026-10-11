---
label: prop:example
kind: claim
status: survived-search
uses: [def:objective, asm:example]
supersedes:
superseded_by:
lean:
paper_ref: theory/model.tex:120
---
<!--
Blueprint node template (ADR-0004). Copy to theory/blueprint/<label with ':' replaced by '-'>.md,
e.g. prop:example -> prop-example.md. Validate with:
    python3 bin/blueprint_check.py theory/blueprint [--write-status]

Header (exactly these keys; label, kind, status and uses are required):
  label         lowercase "prefix:name", e.g. prop:nstar, lem:band, asm:objective, def:vstop
  kind          definition | assumption        -> status: stated | superseded
                claim | variant | imported     -> status ladder below (imported stops at checked)
  status        conjecture -> survived-search -> proved -> checked -> formalized -> verified
                off-ladder (terminal): refuted | conditional | superseded
  uses          labels this node depends on, as [a, b] (use [] for none)
  supersedes / superseded_by   label of the predecessor / successor node (conditional and superseded need superseded_by)
  lean          Lean declaration name (phase 2), empty until formalized
  paper_ref     path:line of the matching result in the paper, used by theorist-critic's cross-check

Rules the validator enforces:
  - The ## Statement text never changes. Rewording it means a NEW node; this one becomes superseded.
    Every evidence-log line carries the statement hash, so an edit is detected.
  - Status moves up one rung at a time, down any number, or to a terminal status. Nothing leaves a terminal status.
  - status must equal the last log line's target.
  - -> survived-search needs a check file under theory/blueprint/checks/.
  - -> proved needs actor theorist, a non-empty proof, and no [GAP: ...] marker.
  - -> checked needs actor proof-verifier and two distinct verifier reports.
  - -> formalized / verified need actor user.
  - A node at checked or above may depend only on definitions/assumptions or on nodes at checked or above.

Evidence-log line format (one per status change; locators are repo-relative, separated by ';'):
  - YYYY-MM-DD | <from> -> <to> | <actor> | <locator>[;<locator>] | stmt:<12-hex statement hash>
The first line's <from> is "new". Get the hash with:
  python3 -c "import sys; sys.path.insert(0,'bin'); import blueprint_check as b; print(b.statement_hash(open('STATEMENT.txt',encoding='utf-8').read()))"
(/theory writes these lines for you.)
-->
## Statement
For every c > 0 and prior variance s0 > 0, the value function V(n) is strictly concave in n on n >= 0.
## Proof
<!-- Proof text. Mark any unresolved step inline as [GAP: what is missing]. -->
## Evidence log
- 2026-10-12 | new -> conjecture | theorist | theory/model.tex:120 | stmt:d860e523ca97
- 2026-10-12 | conjecture -> survived-search | theorist | theory/blueprint/checks/prop-example/search.py;theory/blueprint/checks/prop-example/search.out | stmt:d860e523ca97
