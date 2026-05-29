# Deterministic Gate as a First-Class Workflow Stage — Investigation & Options

**Date:** 2026-05-28
**Author:** investigation (no implementation)
**Trigger:** `tx_peer_effects` ADR-0011 — coder-critic passed a contaminated mechanical refactor (`no_logic_change: true, 96/100`); an external normalized-content diff caught the injected sample restriction + macro rename. Failure axis = LLM *judgment* used to verify a *deterministically-checkable* property.
**Status:** Active — options for decision, nothing built
**Superseding frame:** the options here are the *Tier-1 slice* of a broader discipline. See `2026-05-28_whole-picture-critic-gates-dispatch.md` §7 (The Unified Evidence-Gating Discipline) for the generalization to judgment-class verdicts; read that doc as the current design of record.

---

## The lesson, restated

For any property that has a cheap deterministic check, a deterministic gate should run as a first-class pipeline step that *fails/drops the item* — `generate → gate (deterministic, drops on fail) → LLM critic (judgment residue only)`. The LLM verdict must never be the sole arbiter of a checkable property, and when a critic does render judgment it must **emit** the evidence (grep/diff), per `adversarial-default.md`.

---

## Q1 — What the current Workflow tooling supports

### Item-failure / drop semantics: already present
- `pipeline(items, s1, s2, …)` — **"a stage that throws drops that item to `null` and skips its remaining stages."** This is exactly the drop-on-gate-fail primitive. A gate stage that `throw`s on a dirty item removes it before the critic stage runs.
- `parallel(thunks)` — a thunk that throws resolves to `null`; caller does `.filter(Boolean)`.
- So *the mechanism to fail an item already exists*. What's missing is a deterministic *thing to put in that first stage*.

### Structured/validated output: already present
- `agent(prompt, {schema})` forces the subagent to call `StructuredOutput` and returns a **validated** object — the model retries on mismatch. This is the lever to *require* an evidence field rather than accept a bare verdict.

### The hard constraint: the script sandbox cannot shell out
- Workflow `script` is **pure JS** — "No filesystem or Node.js API access," and even `Date.now()`/`Math.random()` throw.
- Therefore a deterministic check (`git show`, `grep`, `fu00c_normdiff.py`) **cannot execute in the script body.** It must run in one of two places that *do* have Bash:
  1. **inside an `agent()`** (workflow subagents reach Bash), or
  2. **in the main loop, before `Workflow()` is called** (the tool's recommended "scout inline first, then pipeline over the work-list" pattern).

### What this repo currently has
- **No `.claude/workflows/` library, no checked-in gate scripts, no `bin/`.** The Workflow tool is used ad-hoc/inline.
- Closest existing "evidence" convention: `adversarial-default.md`'s **verification ledger** + `coder-critic.md`'s "Compliance Evidence" section (lines 188–206), which require citing ledger rows with grep evidence. Gaps: (a) it's *ledger-citation*, not *re-run-and-paste of the property under review*; (b) nothing stops the critic from asserting `no_logic_change` as plain judgment — the exact 7G failure.

---

## Q2 — A first-class verification-gate helper/convention?

Four options, cheapest to heaviest.

### 2a — Gate-agent stage + small reusable gate-script library  ★ recommended primary
A checked-in, generalized property-gate script (the `normdiff.py` pattern, parameterized) lives in the repo (e.g. `.claude/skills/tools/` or a new `bin/gates/`). The pipeline's **first stage dispatches a thin "gate" agent** whose only job is: run the script via Bash, parse exit code, return `{pass, residue, evidence}` via `schema`. The stage `throw`s on `!pass` → item dropped before the critic.
- **Pro:** wires the gate *into* the pipeline (`generate → gate → critic`); the drop happens automatically, removing the "orchestrator remembered to run it" fragility ADR-0011 calls out. Reusable across refactor batches.
- **Con:** interposes an agent between the check and the verdict — small trust surface (a thin executor agent could in principle misreport). Mitigate: schema requires the raw script stdout + exit code be pasted into `evidence`, so the determinism is auditable in the return value. Needs a gate-script library to exist.

### 2b — Pre-gate in the main loop (hybrid), pass survivors via `args`
Orchestrator runs the gate deterministically in the main loop (real Bash, no agent), filters the item list, passes only-clean items + their evidence into `Workflow(..., {args})`.
- **Pro:** maximally deterministic — *no agent anywhere in the gate path*. Matches the tool's documented "scout inline first" hybrid.
- **Con:** the gate lives *outside* the pipeline → reintroduces exactly the "depends on the orchestrator remembering" fragility ADR-0011 wants gone. Good for a one-shot batch; weak as a durable convention.

### 2c — Propose a harness-level `gate()` primitive (upstream)
Ask for a Workflow-tool addition: a sandboxed `gate(items, scriptPath)` that runs a *whitelisted* deterministic command per item and returns pass/fail — no agent, inside the pipeline.
- **Pro:** truly first-class, deterministic, in-pipeline. Best end-state.
- **Con:** changes the harness/tool, which this repo does not own; biggest lift; uncertain it lands. Flag upstream, don't block on it.

### 2d — Convention-only: document the pattern in a rule
Codify "for deterministically-checkable properties, the first pipeline stage is a gate that throws-to-drop, before any LLM critic" in `workflow.md` (or a new `verification-gate.md`), relying on the existing `pipeline` throw + a gate agent.
- **Pro:** lowest cost; no new code.
- **Con:** prose without a trigger doesn't bind (same gap `derive-dont-guess`/`adversarial-default` had pre-hooks).

**Recommendation:** 2a as the primary (gate-agent + a small gate-script library), documented via 2d (a rule so the pattern is required, not optional), with 2b noted as the acceptable shortcut for one-off batches and 2c flagged upstream. This mirrors the workflow's own "defense-in-depth, no single layer trusted" stance.

---

## Q3 — Requiring critics to EMIT evidence, not assert a verdict

### 3a — Schema-enforced evidence (mechanical)  ★
When a critic runs inside a Workflow, route it through `agent(…, {schema})` with a schema that **requires** a populated evidence object per checked property — e.g. `findings: [{property, command, raw_output, verdict}]`. The validation layer rejects a verdict with an empty `command`/`raw_output`, and the model retries. Strongest lever: you cannot return `no_logic_change: true` without pasting the diff that proves it.

### 3b — Remove the deterministic property from the critic's remit (structural)  ★
The ADR's core insight: `no_logic_change` is **not a critic judgment** — it's the gate's output. The critic should only judge the *residue* a diff can't check (latent-bug reality, label/semantic accuracy, severity). Update `coder-critic.md`: "do not assert deterministically-checkable properties; consume the gate's verdict; for the judgment residue, emit the grep/diff." This is what actually prevents the 7G class of failure — you stop *asking the LLM the checkable question*.

### 3c — Deduction-row backstop in `coder-critic.md`
Add a row: "asserted a deterministically-checkable property (`no_logic_change`, count parity, path-only) without the gate's evidence attached → Critical deduction." Cheap, consistent with existing ledger rows (lines 196–200), but fires only when a critic is dispatched.

**Recommendation:** 3b + 3a + 3c together — *move* the checkable property to the gate (3b, structural fix), *schema-force* evidence on the residual judgment the critic still makes (3a, mechanical), and keep 3c as the prose/deduction backstop. Headline: **the critic is never the one who asserts a deterministically-checkable property; the gate is.**

---

## Suggested shape (for the eventual decision — not built)

1. `generate → gate-agent (deterministic script, throws-to-drop) → coder-critic (residue only, schema-forced evidence)` as the canonical mechanical-refactor pipeline.
2. A small, reusable, checked-in gate-script library (generalize `normdiff.py`: scaffolding-strip + path-normalize + command/`keep if` count parity).
3. A `verification-gate.md` rule making the gate-first pattern required for mechanical/deterministically-checkable batches.
4. `coder-critic.md` edits: stop asserting checkable properties; emit evidence (schema) for judgment.
5. Flag the harness-level `gate()` primitive (2c) upstream as the clean end-state.

## Open questions for the user
- Where should the gate-script library live — `.claude/skills/tools/` (alongside `stata_sweep.py`/`propagate.py`) or a new `bin/gates/`?
- Is the gate-agent acceptable (2a), or do you want the pure-determinism pre-gate (2b) despite the "remember to run it" fragility?
- Should this become a new rule (`verification-gate.md`) or fold into `workflow.md` §2 (orchestrator loop)?
