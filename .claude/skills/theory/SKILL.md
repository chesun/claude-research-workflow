---
name: theory
description: |
  Rigorous theory development on a blueprint (ADR-0004). Breaks a model into
  small nodes (definitions, assumptions, claims, variants), runs each claim
  through prove-or-refute with examples and counterexample search first,
  checks proofs with two blind proof-verifiers, and reviews the paper against
  the blueprint. Modes: explore, node, variants, verify, status, review, develop.
argument-hint: "[explore <question or .tex> | node <label> | variants <label> | verify <label> [--model fable|opus] | status | review [file] | develop]"
allowed-tools: Read,Grep,Glob,Write,Edit,Bash,Task
---

# Theory

Develop and check economic theory one small step at a time. The working record is the project's **blueprint**, `theory/blueprint/`: one node file per definition, assumption, claim or variant, with an immutable statement, a status, and an append-only evidence log. The node format is in `templates/theory/blueprint-node.md`. The validator is `python3 bin/blueprint_check.py theory/blueprint`.

**Input:** `$ARGUMENTS`, a mode keyword followed by its argument.

**Agents:** `theorist` (worker; may raise a node only as far as `proved`), `proof-verifier` (blind critic; two per node), `theorist-critic` (paper-level critic).

**Status ladder:** `conjecture → survived-search → proved → checked → formalized → verified`, plus the terminal statuses `refuted`, `conditional`, `superseded`. `checked` needs two blind verifier PASSes. `formalized` and `verified` are set only by the user (phase 2, Lean).

---

## Modes

### `/theory explore <question | path to .tex>`

Turn a research question, or an existing theory section, into nodes.

1. If `theory/blueprint/` does not exist, create it and `theory/blueprint/checks/`.
2. Dispatch **theorist** with the question or file. It:
   - creates `definition` and `assumption` nodes (`stated`) for the primitives;
   - creates a `claim` node for each candidate result, at `conjecture`. Existing results from a paper also enter at `conjecture`, whatever earlier reviews said, and their `paper_ref` points at the paper;
   - writes first example checks under `checks/`.
3. Run **status** (below) and show the table.

### `/theory node <label>`

One prove-or-refute pass on one claim or variant node. Dispatch **theorist** with the label. It decides whether the statement holds and, if not, finds a counterexample and the weakest repair. The order is examples, then counterexample search, then exact sub-claim checks, then a proof attempt. It records each status change it makes (at most up to `proved`), and finishes by running the validator. Report the node's new status and the validator verdict.

### `/theory variants <label>`

Dispatch **theorist** to create one `variant` node for each assumption in the node's `uses` (drop, weaken, or swap it), and run each through a prove-or-refute pass. Summarize which assumptions the result needs (it collapses without them) and which are superfluous (it survives without them).

### `/theory verify <label> [--model fable|opus]`

Blind two-verifier check of a node at `proved`. **You** (the dispatcher) build the blind input, so the verifiers never open the node file:

1. Read `theory/blueprint/<label with ':' replaced by '-'>.md`. Confirm the status is `proved` (otherwise stop and say why).
2. Build the input text:
   - the `## Statement`;
   - the `## Proof` with every `[GAP:` line removed (a `proved` node should have none);
   - for each label in `uses`, that node's kind and `## Statement` only.
   
   Do not include the evidence log, `paper_ref`, the paper, or any other verdict. Do include the node's **proof hash** (from `python3 bin/blueprint_check.py --hashes <node file>`), which each verifier copies into its report's `**Proof:**` line.
3. Dispatch **two** `proof-verifier` agents **in parallel** (one message, two Task calls), each a fresh agent with the same input. Pass `model` from `--model` (default `fable`), and give each a distinct run suffix (`-a`, `-b`) for its report filename. Neither agent is told about the other.
4. Read the two `VERDICT:` lines.
   - **Both PASS:** append to the node's evidence log
     `- YYYY-MM-DD | proved -> checked | proof-verifier | <report-a>;<report-b> | stmt:<stmt hash> proof:<proof hash>`
     and set `status: checked`.
   - **Any FAIL:** append `- YYYY-MM-DD | proved -> survived-search | proof-verifier | <failing report> | stmt:<stmt hash>`, set `status: survived-search`, and hand the failing report to the theorist on the next `node` pass.
   - **Split, or any UNVERIFIED:** dispatch a third verifier with the same input. If it still isn't two PASSes, leave the status unchanged and ask the user.
   
   Get both hashes with `python3 bin/blueprint_check.py --hashes <node file>`.
5. Run the validator. A FAIL here means the log edit was wrong: fix the log line, not the rule.

For the fable-versus-opus comparison (ADR-0003/0004 experiment), run `verify` once with each model on the same node, and record the verdicts and findings by severity in the session log.

### `/theory status`

Run `python3 bin/blueprint_check.py theory/blueprint --write-status`. Show the verdict line, any errors and warnings, and the status table from `theory/blueprint/STATUS.md`.

### `/theory review [file]`

Dispatch **theorist-critic** on the paper's theory section (default: the `.tex` that the most nodes' `paper_ref`s point to). Besides its 16-item checklist and architecture checks, it cross-checks every result in the paper against the blueprint.

Flags (narrow the critic's focus):
- `--proofs`: proof presentation (proof correctness is carried by the blueprint, not this review);
- `--assumptions`: independence, necessity, non-vacuity, boundary examples;
- `--predictions`: whether predictions follow from `checked` nodes and are testable.

### `/theory develop`

Loop over the open claim and variant nodes in dependency order (a node's `uses` first):

1. `node <label>` until the node is `proved`, `refuted`, `conditional`, or the theorist reports no confident proof;
2. `variants <label>` once per claim node;
3. `verify <label>` for each `proved` node.

Stop and ask the user whenever a decision is theirs: a modeling choice (which assumption to keep, how to repair a refuted claim), a split verifier verdict, or anything a node's evidence can't settle. Never loop on one node more than three passes without reporting.

---

## Principles

- **Prove or refute.** No instruction to an agent is ever "prove X". Refuted, conditional and "no confident proof" are real results.
- **Statements are immutable.** A reworded statement is a new node; the validator detects edits by hash.
- **Explore before proving.** Examples and counterexample search first. A search that finds nothing is evidence, not proof.
- **Vary the assumptions.** The variant step shows which assumptions do the identifying work.
- **Verification is blind and doubled.** Two fresh verifiers who never see the paper or the motivation.
- **Simplest version first.** Two agents, two goods, linear utility: if the idea fails there, it fails in general.
- **Theorems are English takeaways that are also mathematically true**, and the paper states only what the blueprint has checked.
- **Predictions feed design.** Testable predictions cite the node labels they rest on.
