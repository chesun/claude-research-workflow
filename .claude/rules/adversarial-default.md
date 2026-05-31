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

**Enforcement strength — block only where the check is deterministic.** Hard *block* is reserved for **Tier 1** (script-decidable), and even there it ships advisory-by-default with opt-in blocking (the `derive-dont-guess` `.enabled` precedent). **Tier 2 / Tier 3** checks and the operationalization gate **advise + deduct** — never hard-block, because a probabilistic check has too many false positives to stop legitimate work. The audible-failure guarantee (`UNVERIFIED` is never silent) still holds at every tier.

**Known limit (state it plainly):** only **Edit/Write-tool-mediated edits are recorded** by the Tier-1 evidence recorder. Changes made in an external editor, and commits made with `git commit --no-verify`, bypass the recorder. This is an honest gap, not a defect — it is the boundary of what a tool-event hook can observe.

**Binding boundary (M9, updated for Phase 3).** Two mechanisms bind, with distinct scopes:

- **Tier 1 (no-logic-change)** binds via the **deterministic recorder + verification ledger** in every context — it is script-decidable, so the residue is real evidence regardless of who reads it.
- **Tier 2 (locatable-judgment verdicts)** is now **schema-enforceable**: when a critic runs inside a schema-routed JS `Workflow()` (via `agent(…, { schema })` with `required: [claim, artifact_citation]`), `StructuredOutput` mechanically rejects an empty-evidence verdict, and a fabricated/absent `artifact_citation` is caught by `.claude/hooks/citation_existence_lib.py` (`resolve_citation`). The schema mechanism *exists* as of Phase 3.

**Be precise — do not overclaim.** Tier-2 binding holds **only inside a schema-routed workflow**. In **ad-hoc / standalone** critic use (a `/review` invocation, an orchestrator dispatch with no schema, a human reading an agent file) there is no `StructuredOutput` gate, so the Tier-2 evidence requirement reverts to **advisory prose**. The citation-existence check is available in both contexts but only runs when invoked; the schema is what *forces* the citation to exist. Do not claim blanket binding for Tier 2.

**Read** `.claude/references/evidence-gating-detail.md` for the full tier table, the verdict vocabulary in detail, the normalizer interface, the citation-existence contract (Phase 3), and the optional-hardening (refactor-mode / pre-commit) spec — mirroring how `primary-source-first.md` points to `.claude/references/pdf-chunking.md` (there is no auto-load; open it when this section points you there).

---

## Inherited-artifact protocol

When working with code, text, data, or design materials that you didn't write *in this session*, the prior is "presumed non-compliant with this project's conventions." Original authors didn't have these conventions; even if they did, drift accumulates. Before any claim of compliance, run the per-domain pre-flight checklist (§ Per-domain checklists) and record results in the verification ledger.

This does not apply to artifacts produced earlier in the same session (you saw them being written; you have direct evidence) — though if substantial time has passed and the file has been further edited externally, treat it as inherited again.

---

## Per-domain checklists

Six domains. Each lists concrete checks with the specific command-or-equivalent that produces evidence. Run them before claiming compliance. Cache results in the ledger.

### Code — Stata

Convention reference: `.claude/rules/stata-code-conventions.md`.

| Check | Command | PASS criterion |
|---|---|---|
| No hardcoded absolute paths | `grep -nE '"/Users\|"/home\|"C:\\\\\\\\' *.do` | 0 matches |
| Seed set exactly once in master | `grep -c 'set seed' main.do` | exactly 1 |
| Master-script hygiene | `grep -E 'cap log close \\| set more off' main.do` | both present |
| Regressions cluster SEs | `grep -nE '^\\s*reg ' *.do \| grep -v 'cluster('` | empty (or each flagged manually) |
| Output-table exports | `grep -nE 'esttab\|outreg2\|estout' *.do` | nonzero |
| No raw-data overwrites | `grep -nE 'save .*data/raw' *.do` | 0 matches |

### Code — R

Convention reference: `.claude/rules/r-code-conventions.md`.

| Check | Command | PASS criterion |
|---|---|---|
| No hardcoded absolute paths | `grep -nE '"/Users\|"/home\|"C:\\\\\\\\' *.R` | 0 matches |
| `set.seed()` once at top | `grep -nE '^set\\.seed\\(' *.R` | exactly 1 in master |
| `library()` not `require()` | `grep -nE '^require\\(' *.R` | 0 matches |
| `feols()` for panel, not `lm()` | `grep -nE '^\\s*lm\\(' *.R` plus context | manual flag (panel data → must be `feols`) |
| Cluster spec on standard errors | `grep -nE 'feols\\(' *.R \| grep -v cluster` | empty (or each flagged) |
| Deprecated `se = "cluster"` arg form | `grep -nE 'se = "cluster"' *.R` | 0 matches |
| Heavy computations saved as `.rds` | `grep -nE 'saveRDS\\(' *.R` | nonzero |

### Code — Python

Convention reference: `.claude/rules/python-code-conventions.md`.

| Check | Command | PASS criterion |
|---|---|---|
| Active virtualenv (not global) | `[ -n "$VIRTUAL_ENV" ] \|\| ls .venv` | exists |
| Pinned dependencies | `ls requirements.txt pyproject.toml 2>/dev/null` | at least one present |
| Seeds set once at top | `grep -nE '^(random\\|np\\.random)\\.seed\\(\|torch\\.manual_seed\\(' *.py` | exactly 1 in master |
| No hardcoded absolute paths | `grep -nE '"/Users\|"/home\|"C:\\\\\\\\' *.py` | 0 matches |
| `pathlib.Path` usage | `grep -nE 'from pathlib' *.py` | nonzero |

### Data — cleaned dataset ready for analysis

| Check | Command | PASS criterion |
|---|---|---|
| Column dtypes after each `merge`/`reshape` | Stata: `describe`; R: `glimpse(df)` | documented in cleaning script comments |
| Duplicate keys | Stata: `isid <key>`; R: `anyDuplicated(df[, key])` | 0 |
| Missing-value inventory | Stata: `mdesc`; R: `naniar::miss_var_summary()` | each `NA` rate inspected, not assumed |
| Panel balance (if panel) | Stata: `xtdescribe`; R: `panelview` | balance documented; unbalance explained |
| Sample-restriction order | inspect cleaning script | each restriction shows N before/after |
| Sentinel values handled | grep for `-999`, `9999`, `.`, `NA` literals | explicit handling, not silently coerced |

### Design — experimental

| Check | What to produce | PASS criterion |
|---|---|---|
| Incentive compatibility | Derive optimal-deviation payoff; show ≤ truth-telling. Or cite published proof. Or run simulated participant. | proof or citation present |
| Comprehension-check pass rate | From pilot data | rate documented; below-threshold subjects' handling specified |
| Randomization integrity | Orthogonality test of treatment to baseline covariates | F-test p-value reported |
| Pre-registration | OSF / AsPredicted / AEA registry filing | registry ID + filing date in ADR or paper |

### Identification

| Strategy | Check | PASS criterion |
|---|---|---|
| DiD (parallel trends) | Pre-trends figure with CI; formal pre-trends test (Roth 2022 / Kahn-Lang 2020 / honest-DiD bounds) | both present, in paper or replication output |
| DiD (staggered) | Goodman-Bacon decomposition or de Chaisemartin-D'Haultfoeuille diagnostic; or use `did::att_gt`/`fastdid`/`fixest::sunab`/`did2s` | one diagnostic + non-TWFE estimator (or justified TWFE with diagnostic) |
| IV | First-stage F-stat (preferred: Montiel Olea-Pflueger effective F); exclusion-restriction argument; monotonicity discussion if LATE | F ≥ 10 reported; exclusion + monotonicity argued |
| RDD | McCrary density test (`rddensity::rddensity`); bandwidth choice rationale; manipulation argument | all three present |
| Synthetic control | Permutation inference / placebo on every donor; RMSPE ratios | placebo distribution + p-value |

### Replication

| Check | Command | PASS criterion |
|---|---|---|
| End-to-end run on fresh clone | execute master script | exits 0 |
| Targets file present | `cat quality_reports/replication_targets.md` | exists, populated |
| Output diff against targets | per `.claude/rules/replication-protocol.md` § tolerances | all targets PASS within tolerance |
| Runtime documented | from end-to-end timing | ≤ 2× claimed in README |
| No absolute paths | `grep -rnE '"/Users\|"/home\|"C:\\\\\\\\' replication/` | 0 matches |
| No API keys / credentials | `grep -rnE 'api_key\|password\|secret' replication/` | 0 matches |

### Bibliography

| Check | Command | PASS criterion |
|---|---|---|
| All `\cite{}` resolve | `pdflatex && bibtex/biber && pdflatex && pdflatex` then `grep -E 'undefined\|Citation .* undefined' main.log` | 0 lines |
| `.bib` syntax valid | `biber --validate-datamodel main` | 0 errors |
| Required fields present per type | `biber` warnings | 0 missing-field warnings |
| Reading notes exist for every cited author | per `.claude/rules/primary-source-first.md` | hooks pass |

---

## Verification ledger

A project-level cache so checks aren't re-run on unchanged artifacts.

**File:** `.claude/state/verification-ledger.md` — tracked in git so the cache is cross-session and cross-machine. Format: one row per `(path, check)`; sortable, greppable.

```markdown
| Path | Check | Verified At | File hash | Result | Evidence |
|------|-------|-------------|-----------|--------|----------|
| scripts/01_clean.do | no-hardcoded-paths | 2026-04-28T10:00Z | a1b2c3d4e5f6 | PASS | grep returned 0 matches |
| scripts/01_clean.do | seed-set-once | 2026-04-28T10:00Z | a1b2c3d4e5f6 | PASS | line 5: `set seed 20260428` |
| scripts/02_analysis.do | no-hardcoded-paths | 2026-04-28T10:05Z | f7e8d9c0b1a2 | FAIL | line 47: `use "/Users/foo/data.dta"` |
```

**Columns:**
- *Path* — repo-relative.
- *Check* — slug from the per-domain table above (e.g., `no-hardcoded-paths`, `seed-set-once`, `parallel-trends`).
- *Verified At* — ISO 8601, UTC, minute precision.
- *File hash* — `sha256(<path>) | head -c 12`. Hash the file content, not the metadata.
- *Result* — `PASS`, `FAIL`, or `ASSUMED`. `ASSUMED` is for documented exceptions (cost-prohibitive, unavailable infrastructure).
- *Evidence* — short string with the specific detail (line number, count, p-value). Long output goes in a session log; the ledger shows the headline.

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

**Cost analysis:** `sha256` of a typical script is microseconds; a `grep` over a project is milliseconds; ledger lookup is microseconds. First check on a new artifact pays the verification cost; subsequent checks on the unchanged artifact pay only lookup cost. Net effect: no bloat under normal editing.

**Audit:** the ledger is a living receipt.
- `grep '| FAIL |' .claude/state/verification-ledger.md` → all open violations.
- `grep '01_clean.do' .claude/state/verification-ledger.md` → verification history of one file.
- `grep '| ASSUMED |' .claude/state/verification-ledger.md` → all unverified-by-cost claims, useful before submission to revisit each.

### Diagnostic findings (`diagnosis:` checks)

A diagnosis — "bug/error X is caused by line B in file C" — is a positive claim, so it lives in the ledger like any other check. Use a `diagnosis:<symptom-slug>` check-type:

| Path | Check | Verified At | File hash | Result | Evidence |
|------|-------|-------------|-----------|--------|----------|
| scripts/03_peer.do | diagnosis:peer-se-cluster-mismatch | 2026-05-28T14:00Z | 3f9a... | DIAGNOSED | SEs too small: clustered at student not classroom; confirmed by re-run with `cluster(classroom)` matching paper |
| scripts/03_peer.do | diagnosis:negative-r2 | 2026-05-28T14:10Z | 3f9a... | RULED-OUT | Not a reghdfe absorb bug; reproduced in plain `reg`, so it's a data issue upstream |

- **Path** = the file (or `file:line`) where the cause lives. **Result** = `DIAGNOSED` (cause confirmed) or `RULED-OUT` (hypothesis investigated and rejected — equally worth recording so it isn't re-chased). **Evidence** = the root cause in one line + how it was confirmed (re-run, grep, repro, test).
- **The File-hash staleness mechanism is the point:** a recorded diagnosis auto-invalidates when its file changes, so "we investigated this and recorded it" doesn't silently rot when the code moves on.

**Diagnosis protocol — before asserting a cause for a bug/error:**
1. `grep` the ledger for a `diagnosis:` row on that file or symptom. If a fresh (`File hash` matches) `DIAGNOSED`/`RULED-OUT` row exists, cite it — do **not** re-guess. This is the institutional-memory check; the recorded answer often already exists.
2. If no fresh row exists, investigate (read the code / run a repro / grep), then **record** a `diagnosis:` row with the evidence.
3. Asserting a cause with neither prior-record consultation nor in-session investigation is exactly the failure the `diagnostic-claim-audit.py` Stop hook blocks (see § Hook enforcement).

---

## Exception protocol

When full verification isn't feasible (cost too high, infrastructure unavailable, only run on a remote cluster, etc.), the agent must explicitly state "Assumed compliant; not independently verified" — both in any associated session log and in the ledger row's `Result = ASSUMED` cell. The Evidence column then names the reason: `Cost-prohibitive: requires HPC re-run`. This makes the unverified claim auditable. It is *never* an option to imply compliance without evidence and without an `ASSUMED` ledger entry.

---

## Cross-references

This rule reinforces — does not replace — the following:

- `verification-protocol.md` — provides per-target end-of-task checklists. This rule changes the *stance* (assume defects) and adds the *cache* (ledger).
- `replication-protocol.md` — replication tolerance thresholds. This rule's "Replication" checklist is a per-row enforcement of those thresholds.
- `primary-source-first.md` — citation evidence. The bibliography checklist's "reading notes exist" check delegates to that rule's hooks.
- `agents.md` § Adversarial Pairing — worker-critic separation. This rule extends the same adversarial stance to workers evaluating artifacts (not just to critics evaluating workers).

---

## Hook enforcement

The stance above was prose-only until 2026-05-28 — and prose without a trigger doesn't bind (the same gap `derive-dont-guess` had). The diagnostic-claim slice now has a deterministic trigger:

- **`.claude/hooks/diagnostic-claim-audit.py`** (Stop hook, block-once). At turn-end it scans the current turn's assistant prose for **bug/error causation claims** (a causal connective — "caused by", "root cause", "fails because", "the bug is", … — co-occurring with a defect indicator or a `file:line`). If such a claim was made but the turn shows **no investigation** (`Read`/`Grep`/`Glob`/`Bash`) **and** the session never consulted `.claude/state/verification-ledger.md`, it blocks the stop once with a remediation: investigate, or read the recorded `diagnosis:` finding. It respects `stop_hook_active` (nudges at most once per turn; a false positive costs one cycle, never a loop).
- **Honest limit:** the hook checks the *procedure* (did you investigate / consult), not the *truth* of the claim — a causal claim is not mechanically verifiable, and evidence is matched at turn granularity, not tied to the specific cited file. It catches the dominant failure (a diagnosis with zero investigation and no prior-record consult), not every wrong diagnosis.
- **Escape hatch:** `<!-- diagnosis-ok: <reason> -->` in the turn's prose (e.g. when restating a previously-recorded finding, or a cause confirmed outside this repo). Auditable: `grep -R "diagnosis-ok" quality_reports/`.

This complements — does not replace — the critic enforcement below; the hook fires in ad-hoc usage where no critic is dispatched.

## Critic enforcement

Critic agents (`coder-critic`, `writer-critic`, `verifier`, plus `strategist-critic` on applied-micro and `designer-critic` / `theorist-critic` on behavioral) all check whether the artifact under review has the relevant ledger rows in `PASS` state. Missing ledger rows in load-bearing paths trigger a deduction. See each critic agent for the specific deduction table.
