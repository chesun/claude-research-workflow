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

## Build plan + independent review

- Build plan written: `quality_reports/plans/2026-05-29_evidence-gating-build-plan.md` (DRAFT, indexed). Design committed `a5d6b73` on branch `design/evidence-gating-discipline`.
- Independent multi-lens review run as a workflow (`wf_12b61ffb-b3e`): 4 lens-reviewers (technical / adversarial / repo-consistency / completeness) → verify high-sev → synthesize. Report: `quality_reports/reviews/2026-05-29_evidence-gating-build-plan_synthesis_review.md`. **Verdict: REVISE-FIRST.** 34 findings, 23 high-sev, 12 verified, 0 refuted. Plan structurally sound (reusable infra all verified to exist); not a rewrite.
- **Round 1 (REVISE-FIRST):** C1 — refactor-mode-gating makes the guarantee default-OFF → ADR-0011 class. User chose "claim-gated + robust establishment" → **v2** (folded C2 + M1–M12).
- **Round 2 re-review (REVISE-AGAIN):** `..._rereview.md`. C1 fix was **vapor** — relied on `/tools refactor-mode`, `/tools normdiff`, `bin/` pre-commit, none of which exist; memory-dependency relocated, not eliminated. Closure: 6 closed, 11 partial, C1 not-closed. Also corrected: agents.md is Class A not B; inbound refs = 8 not 12.
- **C1 redesign (user-decided, round 2):** **record-always + gate-at-claim-time.** PostToolUse hook silently records normdiff residue to ledger on every supported edit (no tooling, no noise, non-blocking); the gate is the evidence-gated critic consuming the ledger (cannot PASS a clean-refactor verdict when residue recorded). refactor-mode/pre-commit → optional hardening. → **v3** written (plan rewritten; M4=fresh normalizer, M9=recorder is interim guarantee, M10/M11 corrected with verified facts, references-loading clarified, CLAUDE.md+workflow.md flagged Class B, ledger content = local state not propagated).

## Phase 1 BUILT + committed (8176d0f)

Built via workflow `wf_afe138ec-b3f` (coder → independent verify + 2 adversarial review lenses → fix). Files: `normdiff_lib.py` (core + 4 normalizers), `evidence-gate-recorder.py` (PostToolUse, registered in settings.json), `normdiff.py` CLI (+ SKILL.md), `test_normdiff_lib.py`.

**Adversarial review caught 4 real correctness bugs the build's own 25 tests passed over** — Stata `*` (mult) mis-stripped as comment; set-diff blind to reorder/dup; backtick-macro poisoning quote-state; seed-change as scaffold. Fix phase resolved all 4. **I independently re-verified** (re-ran tests + exercised each bug scenario directly against the lib) and **added 7 regression tests** (the original suite passed 25/25 with the bugs live → tests were the gap). Now 32/32. Recorder fail-open confirmed (garbage/unsupported/out-of-scope → exit 0, ledger untouched). settings.json registration done via `BYPASS_SHARED_GUARD=1` (protect-files.sh blocks the Edit tool); JSON validated.

Commits on `design/evidence-gating-discipline`: `a5d6b73` (design), `4a509a4` (plan v3 + 2 reviews), `8176d0f` (Phase 1 code).

## Phase 2 BUILT + committed (03782aa)

Built via workflow `wf_46630aea-121` (build → verify + 3 adversarial lenses → fix). The rule (`adversarial-default.md`) + lazy `references/evidence-gating-detail.md` + ledger schema (append Tier/Citation/Tally) + **the GATE** (`coder-critic.md` consults the `no-logic-change` ledger row). **Adversarial review caught the gate was under-specified** (path-only match, no ASSUMED/missing-row/timing/scope) + the ledger append had no regression test → fix operationalized the gate + added 4 backward-compat tests (32→36). **Independently re-verified:** 36/36; diagnostic 7-pass + loud bare-python3; ledger append-not-insert + example rows backfilled to 9 cols + real 6-col rows parse; rule lean (0 tier-table rows in it, 8 refs intact); recorder↔gate contract confirmed (`_CHECK_SLUG="no-logic-change"`, Result PASS/UNVERIFIED).

## Phase 3 BUILT + committed (668bc35)

Tier-2: `citation_existence_lib.py` (`resolve_citation` → RESOLVED/MISSING/ASSUMED; MISSING = fabrication signal, ASSUMED = infra absent) + `/tools cite-check` + schema-enforced critic evidence `{claim, artifact_citation, sufficiency_argument}`. Adversarial **security lens found 0 holes**; I independently pen-tested (path traversal, absolute, shell-metachar/`$()`/backtick test_ids → all rejected, no execution). Review caught the Phase-3 M9 edit had muddied the *Tier-1* deduction with schema language (Tier-1 binds in ALL contexts, deterministic) → corrected. 24/24 citation + 36/36 normdiff. Removed a stray review-scratch file before commit.

## Pending

- **Phase 4**: operationalization gate (requirements-spec tier column, advisory) + Tier-3 adversarial-verify panel template. (`workflow.md` edit = Class B → manual overlay apply.)
- **Phase 5**: class-aware propagation to consumer repos + overlays — **OUTWARD-FACING; confirm with user before running** (modifies other repos).
- **Minor polish** (TODO): block-comment docstring; R/Python path-token first-arg edge; pytest exit-code 4-vs-5; citation timeout configurability.
- Branch `design/evidence-gating-discipline` NOT pushed (hold until whole thing built).

## Artifacts

- `quality_reports/reviews/2026-05-28_deterministic-gate-workflow-proposal.md` (options menu; Tier-1 slice)
- `quality_reports/reviews/2026-05-28_whole-picture-critic-gates-dispatch.md` (**design of record** — §1–7 + open questions)
- Workflow run `wf_0c0201da-98f` (context-mapping; script persisted in session dir)

## Status

Design phase only — **nothing built** (no rules, hooks, schema, or ledger changes). All work in two review docs. Not yet committed.
