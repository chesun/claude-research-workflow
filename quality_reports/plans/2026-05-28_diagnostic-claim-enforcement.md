# Plan — Enforce verification of diagnostic/causal claims (adversarial-default teeth)

**Status:** APPROVED 2026-05-28
**Builds on:** the completed `derive-dont-guess` enforcement (`quality_reports/plans/2026-05-28_derive-dont-guess-enforcement.md`). This is the *next* class of violation: claims that go beyond references.
**Decisions confirmed with user:** findings store = the **existing** `.claude/state/verification-ledger.md` (not a new substrate) · strictness = **block-once** Stop-audit · scope = **bug/error causation claims only**.

---

## Context

The recurring, higher-value failure (just hit in the tx-peer-effects repo): a **causal/diagnostic claim** — "bug A is caused by line B in file C" — asserted as a plausible guess without investigation, *even when the exact issue was previously investigated and the finding recorded*. Two stacked failure modes:

1. **Asserted-without-investigating** — a cause claimed with zero read/grep/test in the session.
2. **Re-guessed what was already recorded** — prior findings existed and weren't consulted (the worse one — the answer already existed).

Why the `derive-dont-guess` hook doesn't catch this: that hook gates **references** (entities with an on-disk anchor — "does path C resolve"). A diagnosis is a claim about **behavior/causation**; the cited file/line *do* resolve, so it sails through. This claim-class belongs to **`adversarial-default.md`** ("a positive claim requires positive evidence") — which, like `derive-dont-guess` was until today, is prose-only with no trigger.

The honest detection limit: you can't mechanically check whether a causal claim is *true*. But you can check the **procedure** — did the session investigate (read/grep/test) or consult the recorded findings before asserting? That's the enforceable proxy, identical in shape to the existing `primary-source-audit.py` (claim in prose → require evidence-of-consultation this session → block-once).

**The ledger is the right store** (user's correction — I initially proposed inventing a new one despite the ledger being in context): a diagnosis fits `.claude/state/verification-ledger.md`'s `| Path | Check | Verified At | File hash | Result | Evidence |` schema as a `diagnosis:<symptom-slug>` row keyed to file C — and the **File-hash staleness mechanism auto-invalidates a recorded diagnosis when C changes**, which is exactly the "we recorded findings but the code moved on" problem.

**Intended outcome:** when a bug/error cause is asserted without investigation *and* without consulting the ledger, the turn is blocked once with a remediation that points at both paths (investigate, or read the recorded `diagnosis:` finding).

---

## Recommended approach

### Component 1 — `diagnosis:` convention in the verification ledger (the store)

Documentation only; no code. In `.claude/rules/adversarial-default.md` § Verification ledger and the `.claude/state/verification-ledger.md` header:

- Define a new check-type: `diagnosis:<symptom-slug>` (e.g. `diagnosis:peer-se-cluster-mismatch`).
  - **Path** = the file (or `file:line`) where the cause lives.
  - **Result** = `DIAGNOSED` (cause confirmed) or `RULED-OUT`.
  - **Evidence** = the root cause in one line + how it was confirmed (test/grep/repro).
  - **File hash** = `sha256(file)` → the diagnosis goes stale (re-investigate) when the file changes — the built-in answer to "findings recorded but code moved on."
- Add a protocol paragraph: *before asserting a cause for a bug/error, grep the ledger for a `diagnosis:` row on that file/symptom; after investigating, record one.* This is the consultation loop that fixes failure mode #2.

### Component 2 — `diagnostic-claim-audit.py` (Stop hook, block-once)

New `.claude/hooks/diagnostic-claim-audit.py`, mirroring `primary-source-audit.py:44-111` structure exactly (load lib → read stdin → respect `stop_hook_active` → transcript → detect claims → check evidence → `{"decision":"block","reason":...}`).

- **Scope to the current turn** for the claim (a diagnosis made *this* turn needs backing this turn). Add `current_turn_assistant_text(transcript)` to `stop_hooks_lib.py` (reuse `current_turn_events` already there).
- **Detect** bug/error causation claims, conservatively, to keep precision high: require a causal connective (`caused by`, `due to`, `because of`, `root cause`, `stems from`, `the (bug|issue|problem|error|failure) is`, `fails because`, `responsible for`, `the culprit`, `the reason ... is`) co-occurring in the same sentence-window with EITHER a defect indicator (`bug|error|fail|crash|broken|exception|wrong|incorrect|NaN|NA|missing|regression|doesn't work`) OR a `file:line` / filename reference.
- **Evidence check** — allow (no block) if EITHER:
  - investigation happened **this turn**: any `Read`/`Grep`/`Glob`/`Bash` tool-use in the current turn (reuse `stop_hooks_lib.iter_tool_uses` scoped to `current_turn_events`); OR
  - the **ledger was consulted this session**: a `Read` of `.claude/state/verification-ledger.md`, or a `Bash` command referencing it.
- **Block-once** otherwise, with remediation: "You asserted a cause without investigating this turn. Read the file / run a repro / grep, OR consult `.claude/state/verification-ledger.md` for a prior `diagnosis:` finding on this symptom — it may already be recorded. Then record/confirm a `diagnosis:` row." Respects `stop_hook_active` (never loops; a false positive costs one cycle).
- **Escape hatch**: `<!-- diagnosis-ok: <reason> -->` in the turn's prose (mirrors `primary-source-ok` / `derive-ok`; auditable via grep).
- **Fail-open** on any exception.

**Documented limitation** (honest, like the path hook): evidence is checked at turn granularity, not tied to the *specific* cited file — an agent that investigates file X then guesses about file Y passes. v1 catches the dominant case (a diagnosis with zero investigation and no ledger consult). Tightening to per-file is a future refinement.

### Component 3 — register + Core Principles + tests

- Register `diagnostic-claim-audit.py` in `settings.json` Stop array (via the documented `BYPASS_SHARED_GUARD` mechanism; audit-logged).
- `adversarial-default.md`: add an `## Enforcement` subsection (it currently has only "Critic enforcement") documenting the hook, the `diagnosis:` ledger convention, and the escape hatch. Optional one-line cross-link from CLAUDE.md Core Principles.
- Tests `.claude/hooks/test_diagnostic_claim_audit.py`: detection precision (causal+defect → detected; benign causal prose → not), evidence pass (investigation this turn → allow; ledger Read this session → allow), block-once, escape hatch, fail-open. Plus unit tests for the new `current_turn_assistant_text` in `test_stop_hooks_lib.py`.

---

## Files

- New: `.claude/hooks/diagnostic-claim-audit.py`, `.claude/hooks/test_diagnostic_claim_audit.py`
- Edit: `.claude/hooks/stop_hooks_lib.py` (+`current_turn_assistant_text`, +`ledger_consulted_this_session`), `.claude/hooks/test_stop_hooks_lib.py`
- Edit: `.claude/rules/adversarial-default.md` (Enforcement + `diagnosis:` convention), `.claude/state/verification-ledger.md` (header note), `settings.json` (register), optional `CLAUDE.md` (Core Principles line)

Reuse: `primary-source-audit.py` (Stop-audit skeleton), `stop_hooks_lib.py` (transcript walker, current-turn scoping), the existing ledger schema.

---

## Sequencing (atomic commits)

1. `adversarial-default.md` + ledger header: `diagnosis:` convention + Enforcement section (docs first, so the hook's remediation references a real convention).
2. `stop_hooks_lib.py` additions + `diagnostic-claim-audit.py` + tests.
3. Register in `settings.json` + optional CLAUDE.md line.

---

## Verification

- **Unit:** `python3 -m pytest .claude/hooks/test_diagnostic_claim_audit.py .claude/hooks/test_stop_hooks_lib.py -q`.
- **Detection precision (synthetic transcripts):** "the crash is caused by the off-by-one at utils.py:42" with no tool-calls this turn → BLOCK; same claim with a `Read` of utils.py this turn → allow; "we chose clustering because it matches assignment" (benign causal, no defect) → no block.
- **Ledger-consult path:** diagnostic claim + a `Read` of `verification-ledger.md` this session → allow.
- **Block-once:** `stop_hook_active=true` → exit 0 (no loop).
- **Escape hatch:** `<!-- diagnosis-ok: confirmed in #123 -->` in prose → allow.
- **Fail-open:** malformed stdin → exit 0, no output.
- **Config:** settings.json valid JSON; Stop array lists the new hook.
