# Adversarial Default — checklists and ledger detail

**Class:** A (universal). Pointer-loaded detail for `.claude/rules/adversarial-default.md` § Per-domain checklists and § Verification ledger (moved from the rule on 2026-10-19); there is no auto-load.

The rule states what to do: run the relevant checklist below before claiming compliance, consult and update the verification ledger (`.claude/state/verification-ledger.md`) by its lookup protocol, and record `diagnosis:` rows. This file holds the checklist tables, the ledger's row format, and worked examples.

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

## Verification ledger — row format

**File:** `.claude/state/verification-ledger.md`, one row per `(path, check)`; sortable, greppable. Its own header also documents the columns, including the optional `Tier`, `Artifact Citation` and `Refuter Tally` columns added for evidence gating.

```markdown
| Path | Check | Verified At | File hash | Result | Evidence |
|------|-------|-------------|-----------|--------|----------|
| scripts/01_clean.do | no-hardcoded-paths | 2026-04-28T10:00Z | a1b2c3d4e5f6 | PASS | grep returned 0 matches |
| scripts/01_clean.do | seed-set-once | 2026-04-28T10:00Z | a1b2c3d4e5f6 | PASS | line 5: `set seed 20260428` |
| scripts/02_analysis.do | no-hardcoded-paths | 2026-04-28T10:05Z | f7e8d9c0b1a2 | FAIL | line 47: `use "/Users/foo/data.dta"` |
```

**Columns:**
- *Path* — repo-relative.
- *Check* — slug from the per-domain checklists in this file (e.g., `no-hardcoded-paths`, `seed-set-once`, `parallel-trends`).
- *Verified At* — ISO 8601, UTC, minute precision.
- *File hash* — `sha256(<path>) | head -c 12`. Hash the file content, not the metadata.
- *Result* — `PASS`, `FAIL`, or `ASSUMED`. `ASSUMED` is for documented exceptions (cost-prohibitive, unavailable infrastructure).
- *Evidence* — short string with the specific detail (line number, count, p-value). Long output goes in a session log; the ledger shows the headline.

**Cost analysis:** `sha256` of a typical script is microseconds; a `grep` over a project is milliseconds; ledger lookup is microseconds. First check on a new artifact pays the verification cost; subsequent checks on the unchanged artifact pay only lookup cost. Net effect: no bloat under normal editing.

**Audit:** the ledger is a living receipt.
- `grep '| FAIL |' .claude/state/verification-ledger.md` → all open violations.
- `grep '01_clean.do' .claude/state/verification-ledger.md` → verification history of one file.
- `grep '| ASSUMED |' .claude/state/verification-ledger.md` → all unverified-by-cost claims, useful before submission to revisit each.

## Diagnosis rows — worked example

A `diagnosis:<symptom-slug>` row records an investigated bug/error cause:

| Path | Check | Verified At | File hash | Result | Evidence |
|------|-------|-------------|-----------|--------|----------|
| scripts/03_peer.do | diagnosis:peer-se-cluster-mismatch | 2026-05-28T14:00Z | 3f9a... | DIAGNOSED | SEs too small: clustered at student not classroom; confirmed by re-run with `cluster(classroom)` matching paper |
| scripts/03_peer.do | diagnosis:negative-r2 | 2026-05-28T14:10Z | 3f9a... | RULED-OUT | Not a reghdfe absorb bug; reproduced in plain `reg`, so it's a data issue upstream |

- **The File-hash staleness mechanism is the point:** a recorded diagnosis auto-invalidates when its file changes, so "we investigated this and recorded it" doesn't silently rot when the code moves on.


---

## Pruned hook (history)

The diagnosis protocol in `.claude/rules/adversarial-default.md` is a working discipline, not a hook. The former `diagnostic-claim-audit.py` Stop hook — which blocked turn-end when a bug/error causation claim was made with no investigation that turn and no consult of the verification ledger — was pruned 2026-09-16. Claude 5 investigates before asserting a cause without the nag; the protocol still binds as discipline, and the rule's critic enforcement still applies when a critic is dispatched.
