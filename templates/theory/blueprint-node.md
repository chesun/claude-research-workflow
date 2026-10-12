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
                claim | variant | imported     -> status ladder below (imported stops at checked; its check file
                quotes the source from the reading notes, and its proof section cites where the result is proved)
  status        conjecture -> survived-search -> proved -> checked -> formalized -> verified
                off-ladder (terminal): refuted | conditional | superseded
  uses          labels this node depends on, as [a, b] (use [] for none)
  supersedes / superseded_by   label of the predecessor / successor node. When a claim needs an extra hypothesis, the
                original node becomes conditional (or superseded if reworded) with superseded_by naming a NEW
                claim node at conjecture that states the repaired result; the repair climbs as that new node.
  lean          <Pkg>.<Name>: the node's Lean statement file <Pkg>/Statements/<Name>.lean (phase 2;
                templates/theory/lean-layout.md). Set by the formalizer; required at formalized and above.
  paper_ref     path:line of the matching result in the paper, used by theorist-critic's cross-check

Rules the validator enforces:
  - The ## Statement text never changes. Rewording it means a NEW node; this one becomes superseded.
    Every evidence-log line carries the statement hash, so an edit is detected.
  - Status moves up one rung at a time, down any number, or to a terminal status. Nothing leaves a terminal status.
  - status must equal the last log line's target.
  - -> survived-search needs a check file under theory/blueprint/checks/.
  - -> proved needs actor theorist, a non-empty proof, no [GAP: ...] marker (any case), and the proof hash.
  - -> checked needs actor proof-verifier, the same proof hash, and two distinct proof-verifier
    reports whose headers name this label, Score PASS and that proof hash.
  - While a node is proved or above, its proof must still match the last logged proof hash.
  - A downgrade (e.g. a verifier FAIL) needs an existing evidence file, normally the failing report.
  - Locators must be regular files inside the repo. URLs, absolute paths and paths outside the repo
    give UNVERIFIED, never PASS. Windows device names (nul, con, ...) and directories are errors.
  - Only blank lines and HTML comments may sit between the header and ## Statement. A separate comment there whose
    text starts "mentions:" lists, comma-separated, the nodes the node names without depending on them
    (e.g. a comment holding "mentions: asm:objective, prop:other"). It is outside both hashes.
  - A statement or proof that cites a node label found in neither uses nor mentions gives a warning (UNVERIFIED).
    A label is read as the longest label-shaped token, so write "lem:b's bound", not "lem:b-based bound".
  - -> formalized / verified need actor user (the owner); no tool or agent writes these lines.
  - -> formalized also needs locators to the node's card (cards/<node>.md: Node and Lean match, Verdict FAITHFUL or
    WITH-NOTED-DIFFERENCES, signed off) and a statements-mode lean_check PASS report with the card's SHA-256.
  - -> verified needs the card and a full-mode lean_check PASS report with the card's SHA-256; while a node is
    verified, its newest full-mode report must still be that PASS.
  - A node at checked or above may depend only on definitions/assumptions or on nodes at checked or above.

Evidence-log line format (one per status change; locators are repo-relative, separated by ';'):
  - YYYY-MM-DD | <from> -> <to> | <actor> | <locator>[;<locator>] | stmt:<12-hex statement hash>[ proof:<12-hex proof hash>]
The first line's <from> is "new". Dates are real and never decrease. "proof:" is required on -> proved and -> checked.
Get both hashes for a node file with:
  python3 bin/blueprint_check.py --hashes theory/blueprint/<node>.md
(/theory writes these lines for you.)

Maintenance tools (bin/blueprint_tools.py):
  verify-input <node>.md [--out FILE]   blind verifier input for a proved node; refuses unless the node is proved,
                                        gap-free, free of validator errors (its own or its dependencies'), rests on
                                        ready dependencies, and cites only nodes in uses or mentions
  dependents <node>.md                  nodes that use or cite this one
  repoint <node>.md [--apply]           move a superseded/conditional node's dependents to its first live successor.
                                        Dependents at proved+ drop to survived-search; checked+ nodes resting on them
                                        drop to proved. Its log lines carry the actor blueprint-tools.
-->
## Statement
For every c > 0 and prior variance s0 > 0, the value function V(n) is strictly concave in n on n >= 0.
## Proof
<!-- Proof text. Mark any unresolved step inline as [GAP: what is missing]. -->
## Evidence log
- 2026-10-12 | new -> conjecture | theorist | theory/model.tex:120 | stmt:d860e523ca97
- 2026-10-12 | conjecture -> survived-search | theorist | theory/blueprint/checks/prop-example/search.py;theory/blueprint/checks/prop-example/search.out | stmt:d860e523ca97
