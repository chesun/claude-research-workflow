# Session Log — 2026-05-29: Evidence-Gating Discipline (design, not built)

**Goal:** Investigate a workflow-design improvement surfaced by the `tx_peer_effects` ADR-0011 incident (a coder-critic passed a contaminated mechanical Stata refactor `no_logic_change: true, 96/100`; an external normalized-content diff caught injected logic). Design — do not execute.

## Arc of the session

1. **Read the incident context** (ADR-0011, `fu00c_normdiff.py`, the 7G-catch session log in the other repo). Core lesson: the failure was using *LLM judgment* to verify a *deterministically-checkable* property.
2. **Assessed Workflow tooling** → wrote `quality_reports/reviews/2026-05-28_deterministic-gate-workflow-proposal.md`. Key constraint found: the JS `Workflow()` script sandbox has no Bash/filesystem, so a deterministic check must run inside an `agent()` or in the main loop, never the script body. `pipeline()` already drops items on throw; `agent(...,{schema})` can force structured evidence.
3. **Ran a 5-agent workflow** (`wf_0c0201da-98f`, 4 parallel repo-mappers → 1 synthesizer) to map every critic dispatch context, toolsets, gate-runner availability, and checkable-property inventory → wrote `quality_reports/reviews/2026-05-28_whole-picture-critic-gates-dispatch.md`. This doc is now the **design of record**.
4. **Resolved the user's core worry** (editing the critic affects all contexts, but a gate exists only in the JS-Workflow context): the fix is a context-independent **hook** (Tier-1 guarantee) + a uniformly **evidence-gated critic** (`PASS` only with evidence, else loud `UNVERIFIED`) — not a context-bifurcated checklist.
5. **Rejected giving critics Bash** (§5): capability ≠ determinism; erodes separation of powers (Bash bypasses the `Edit|Write` guardrails); weaker coverage than a hook.
6. **Documented the non-model actors** (§6, grounded in the real I/O contract of `stata-comment-balance-check.py` / `derive-check-advisory.py`): harness hook (the guarantee), pipeline gate-agent (fail-fast accelerator), git pre-commit (commit-path backstop). Surfaced the hard design point: the no-logic-change invariant is *conditional* (only desired during a refactor), so the hook needs a mode signal.
7. **Generalized to the Unified Evidence-Gating Discipline** (§7) after the user observed "goal A achieved without evidence" is the same problem class but judgment, not script-checkable. Framework: one principle (a verdict is only as good as its evidence; scale the *mechanism* to checkability) + Step 0 operationalize-first + 3 tiers + uniform `{PASS, UNVERIFIED, FAIL}` vocabulary + the ledger as universal record + actor-per-tier + generalized separation of powers + honest limits. It is the operational form of `adversarial-default`.

## Decisions (user-confirmed)

- **Q6 — operationalization gate = advisory** (reminder + critic deduction, not a block). Reduces friction; consistent with §7.5a.
- **Q10 — one rule**, mission = *operationalize `adversarial-default` using evidence gating*. Name not load-bearing; principle must not split across files.
- **§7.5a enforcement-strength principle** (proposed, resolves Q2): block only at Tier-1 and even there advisory-by-default + opt-in blocking (`refactor-mode.enabled`); Tier 2/3 + operationalization gate advise + deduct. `UNVERIFIED`-is-never-silent holds at every tier; hard stop reserved for deterministic checks. **Awaiting user confirm.**

## Decisions — ALL open questions now resolved (design phase complete)

- **Q1 — register broadly, act narrowly:** hook registered on PreToolUse `Edit|Write` with a `git show HEAD` baseline, but *activates* only when a no-logic-change claim is in force (`refactor-mode` on AND file in refactor set); silent no-op otherwise. Conditionality is on the *claim*, not the dispatch context. Surfaced the general principle: **the discipline gates on claims, not actions** (added to §7.0).
- **Q2 →** advisory-default, Tier-1 opt-in block (§7.5a, confirmed).
- **Q3 →** language-agnostic core + per-language normalizers; ship **Stata, Python, R, LaTeX** now (LaTeX = "no-content-change"); **Quarto deferred** (no Quarto infra; chunk extraction) → queued to `TODO.md`.
- **Q4 →** load-bearing Tier-1 `UNVERIFIED` = FAIL when refactor-mode on, else a deduction.
- **Q5 →** schema-enforced evidence from the start (not prose-first).
- **Q6 →** operationalization gate advisory.
- **Q7 →** build the Tier-2 citation existence-check.
- **Q8 →** Tier-3 adversarial verification mandatory only for load-bearing judgment verdicts.
- **Q9 →** extend ledger columns (`tier`, `artifact_citation`, `refuter_tally`).
- **Q10 →** one rule operationalizing `adversarial-default` via evidence gating.

## Pending (user)

- Go/no-go on writing the **build plan** (single rule + Tier-1 hook + four normalizers + ledger schema + schema-enforced critic evidence). Nothing built yet.

## Artifacts

- `quality_reports/reviews/2026-05-28_deterministic-gate-workflow-proposal.md` (options menu; Tier-1 slice)
- `quality_reports/reviews/2026-05-28_whole-picture-critic-gates-dispatch.md` (**design of record** — §1–7 + open questions)
- Workflow run `wf_0c0201da-98f` (context-mapping; script persisted in session dir)

## Status

Design phase only — **nothing built** (no rules, hooks, schema, or ledger changes). All work in two review docs. Not yet committed.
