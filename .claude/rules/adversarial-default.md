# Adversarial Default

**The principle: burden of proof is on the asserter, not the critic.**

When evaluating any artifact — code, data, experimental design, identification strategy, replication, bibliography — the default assumption is that the artifact has defects. Compliance is a positive claim that requires positive evidence (a grep result, a test output, a diagnostic, a formal proof). "I read it and it looks fine" is not evidence; it is the absence of evidence.

This inverts the prevailing pattern. Without this rule, an agent reviewing inherited code says "no issues found" when no obvious red flags appear. With this rule, the same agent must produce concrete evidence that *each* relevant convention is satisfied — or note that evidence is missing and the claim is unverified.

**Counterbalance — non-bloat:** adversarial-default does not mean re-running every check on every task. A verified artifact stays verified until it changes. Verification results are cached in a project ledger; agents consult the ledger before running a check. See § Verification ledger.

**Three vocabulary cousins** (the principle borrows from each):
- *Engineering — fool-proofing / poka-yoke.* Design for the worst case so that even an inattentive operator can't produce a defect.
- *Security — zero trust.* Never trust by virtue of origin; always verify.
- *Falsifiability.* Claims that can't be falsified are claims you haven't actually checked.

---

## Evidence gating

This rule's operational form, generalized across the checkability spectrum.

**The one principle: a verdict is only as good as the evidence it carries. Scale the verification *mechanism* to how checkable the evidence is.** A grep/test/diff is script-decidable; "the proof is correct" is not. The requirement to show evidence never relaxes; the *mechanism* that produces and checks it differs by claim type.

**Gate on claims, not actions.** Enforcement fires when a verifiable claim is *made or in force* (a "no-logic-change" refactor declaration, a critic's "goal achieved" verdict) — never on every edit indiscriminately. An edit that makes no verifiable claim has nothing to gate.

**Verdict vocabulary — `{PASS, UNVERIFIED, FAIL}`.** `PASS` only with tier-appropriate evidence attached; `UNVERIFIED` when evidence is absent or not yet produced (loud, deducting, never silent — this is the floor that turns a silent false `PASS` into an audible failure); `FAIL` when disproven. No bare assertion is ever a `PASS`. Vocabulary detail, the three checkability tiers, and the normalizer interface live in the reference doc.

**Enforcement strength.** Hard block only for **Tier 1** (script-decidable), and there opt-in; **Tier 2 / Tier 3** checks and the operationalization gate advise and deduct, never block. `UNVERIFIED` stays audible at every tier.

**Known limit (state it plainly):** only **Edit/Write-tool-mediated edits are recorded** by the Tier-1 evidence recorder. Changes made in an external editor, and commits made with `git commit --no-verify`, bypass the recorder. This is an honest gap, not a defect — it is the boundary of what a tool-event hook can observe.

**Do not overclaim binding.** Tier 1 (no-logic-change) binds in every context through the recorder and the verification ledger. Tier 2 binds only when the critic runs inside a schema-routed `Workflow()`; in ad-hoc or standalone critic use its evidence requirement is advisory prose. Do not claim blanket binding for Tier 2.

**Read** `.claude/references/evidence-gating-detail.md` for the full tier table, the verdict vocabulary in detail, the enforcement-strength and binding-boundary (M9) detail, the normalizer interface, the citation-existence contract (Phase 3), and the optional-hardening (refactor-mode / pre-commit) spec (open it when you build or adjudicate an evidence gate).

---

## Inherited-artifact protocol

When working with code, text, data, or design materials that you didn't write *in this session*, the prior is "presumed non-compliant with this project's conventions." Original authors didn't have these conventions; even if they did, drift accumulates. Before any claim of compliance, run the per-domain pre-flight checklist (§ Per-domain checklists) and record results in the verification ledger.

This does not apply to artifacts produced earlier in the same session (you saw them being written; you have direct evidence) — though if substantial time has passed and the file has been further edited externally, treat it as inherited again.

---

## Per-domain checklists

Before claiming compliance, run the per-domain checklist (code: Stata, R, Python; data; experimental design; identification; replication; bibliography) and cache the results in the ledger.

**Read** `.claude/references/adversarial-default-detail.md` § Per-domain checklists for the check, command and PASS criterion of each domain (open it before any compliance claim or pre-flight).

---

## Verification ledger

A project-level cache so checks aren't re-run on unchanged artifacts.

**File:** `.claude/state/verification-ledger.md` — tracked in git so the cache is cross-session and cross-machine. Format: one row per `(path, check)`, with columns Path, Check, Verified At, File hash (`sha256(<path>) | head -c 12`, content not metadata), Result (`PASS`, `UNVERIFIED`, `FAIL`, or `ASSUMED`; `DIAGNOSED` / `RULED-OUT` for `diagnosis:` rows) and Evidence.

**Read** `.claude/references/adversarial-default-detail.md` § Verification ledger — row format for the column spec, example rows, cost analysis and audit greps (open it when you write or audit a ledger row).

**Lookup protocol — before running check `C` on path `P`:**
1. Compute `current_hash = sha256(P) | head -c 12`.
2. Read the ledger row for `(P, C)`.
3. If row exists AND `File hash` matches `current_hash` AND `Result == PASS`: cite the ledger entry; skip running the check.
4. If row exists AND `File hash` differs: stale → re-run, update the row in place.
5. If row doesn't exist: run, append a new row.
6. If row exists AND `Result == FAIL` AND file unchanged: still FAIL — flag as an unresolved violation. (Don't re-run; the agent or user must fix `P` first, then recheck explicitly.)

**Stale invalidation triggers — force re-run regardless of cached row:**
- The convention itself changed: if the relevant rule file (`stata-code-conventions.md`, etc.) was modified after the ledger row's `Verified At`, re-run.
- User invokes `/tools verify --force` (rebuilds ledger from scratch).
- Pre-submission gate: `verifier` in submission mode rebuilds the ledger paranoically.

### Diagnostic findings (`diagnosis:` checks)

A diagnosis — "bug/error X is caused by line B in file C" — is a positive claim, so it lives in the ledger like any other check. Use a `diagnosis:<symptom-slug>` check-type (worked example in `.claude/references/adversarial-default-detail.md` § Diagnosis rows).

- **Path** = the file (or `file:line`) where the cause lives. **Result** = `DIAGNOSED` (cause confirmed) or `RULED-OUT` (hypothesis investigated and rejected — equally worth recording so it isn't re-chased). **Evidence** = the root cause in one line + how it was confirmed (re-run, grep, repro, test).

**Diagnosis protocol — before asserting a cause for a bug/error:**
1. `grep` the ledger for a `diagnosis:` row on that file or symptom. If a fresh (`File hash` matches) `DIAGNOSED`/`RULED-OUT` row exists, cite it — do **not** re-guess. This is the institutional-memory check; the recorded answer often already exists.
2. If no fresh row exists, investigate (read the code / run a repro / grep), then **record** a `diagnosis:` row with the evidence.
3. Asserting a cause with neither prior-record consultation nor in-session investigation is the failure this protocol exists to prevent: investigate, or cite a recorded `diagnosis:` row, before asserting a cause.

---

## Exception protocol

When full verification isn't feasible (cost too high, infrastructure unavailable, only run on a remote cluster, etc.), the agent must explicitly state "Assumed compliant; not independently verified" — both in any associated session log and in the ledger row's `Result = ASSUMED` cell. The Evidence column then names the reason: `Cost-prohibitive: requires HPC re-run`. This makes the unverified claim auditable. It is *never* an option to imply compliance without evidence and without an `ASSUMED` ledger entry.

---

## Cross-references

This rule reinforces — does not replace — the following:

- `verification-protocol.md` — provides per-target end-of-task checklists. This rule changes the *stance* (assume defects) and adds the *cache* (ledger).
- `replication-protocol.md` — replication tolerance thresholds. The "Replication" per-domain checklist is a per-row enforcement of those thresholds.
- `primary-source-first.md` — citation evidence. The bibliography checklist's "reading notes exist" check delegates to that rule's hooks.
- `agents.md` § Adversarial Pairing — worker-critic separation. This rule extends the same adversarial stance to workers evaluating artifacts (not just to critics evaluating workers).

---

## Diagnostic-claim discipline

The diagnosis protocol above is a discipline, not a hook (the `diagnostic-claim-audit.py` Stop hook was pruned 2026-09-16); the critic enforcement below still applies when a critic is dispatched.

## Critic enforcement

Critic agents (`coder-critic`, `writer-critic`, `verifier`, plus `strategist-critic` on applied-micro and `designer-critic` / `theorist-critic` on behavioral) all check whether the artifact under review has the relevant ledger rows in `PASS` state. Missing ledger rows in load-bearing paths trigger a deduction. See each critic agent for the specific deduction table.
