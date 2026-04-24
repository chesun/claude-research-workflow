# Replication Protocol

**Core principle:** Replicate original results to the dot BEFORE extending.

This rule codifies the replication + deposit workflow. It complements `agents/verifier.md` (submission mode) with concrete tolerance tables and checklists.

---

## Phase 1: Inventory & Baseline

Before writing any analysis code that builds on another paper:

- Read the paper's replication README.
- Inventory the replication package: language, data files, scripts, outputs.
- Record the gold-standard numbers from the paper in a targets file saved to `quality_reports/replication_targets.md`:

```markdown
## Replication Targets: [Author (Year)]

| Target | Table/Figure | Value | SE/CI | Notes |
|--------|-------------|-------|-------|-------|
| Main ATT | Table 2, Col 3 | -1.632 | (0.584) | Primary specification |
```

## Phase 2: Translate & Execute

- Follow `stata-code-conventions.md` or `r-code-conventions.md` for language standards.
- Translate line-by-line initially — don't "improve" during replication.
- Match original specification exactly (covariates, sample, clustering, SE method).
- Save all intermediate results.

### Stata ↔ R Translation Pitfalls

| Stata | R | Trap |
|-------|---|------|
| `reg y x, cluster(id)` | `feols(y ~ x, cluster = ~id)` | Stata clusters df-adjust differently from some R packages |
| `areg y x, absorb(id)` | `feols(y ~ x \| id)` | Verify demeaning method matches |
| `probit` (PS) | `glm(family=binomial(link="probit"))` | R default is logit in some commands |
| `bootstrap, reps(999)` | method-dependent | Match seed, reps, and bootstrap type exactly |

## Phase 3: Verify Match

### Tolerance Thresholds

| Type | Tolerance | Rationale |
|------|-----------|-----------|
| Integers (N, counts) | Exact match | No reason for any difference |
| Point estimates | < 0.01 | Rounding in paper display |
| Standard errors | < 0.05 | Bootstrap/clustering variation |
| P-values | Same significance level | Exact p may differ slightly |
| Percentages | < 0.1pp | Display rounding |

### If Mismatch

**Do NOT proceed to extensions.** Isolate which step introduces the difference. Check common causes: sample size, SE computation, default options, variable definitions. Document the investigation even if unresolved.

### Replication Report

Save to `quality_reports/replication_report.md`:

```markdown
# Replication Report: [Author (Year)]
**Date:** [YYYY-MM-DD]
**Original language:** [Stata/R/etc.]
**Translation:** [script path]

## Summary
- **Targets checked / Passed / Failed:** N / M / K
- **Overall:** [REPLICATED / PARTIAL / FAILED]

## Results Comparison
| Target | Paper | Ours | Diff | Status |

## Discrepancies (if any)
- **Target:** X | **Investigation:** ... | **Resolution:** ...

## Environment
- Software version, key packages (with versions), data source
```

## Phase 4: Only Then Extend

After replication is verified (all targets PASS):

- Commit replication script: "Replicate [Paper] Table X — all targets match"
- Extend with new estimators, additional robustness, novel analyses.
- Each extension builds on the verified baseline.

---

## Phase 5: AEA Data Deposit Preparation

After all analyses are complete and paper is ready for submission:

### 5.1 Package Assembly

- [ ] All scripts numbered sequentially (`01_`, `02_`, ...)
- [ ] Master script present and tested end-to-end
- [ ] README in AEA Data Editor format (see required sections below)
- [ ] No hardcoded absolute paths anywhere (`grep -r '/Users/\|/home/\|C:\\\\'`)
- [ ] No API keys or credentials in scripts
- [ ] `sessionInfo()` (R) or package versions (Stata) documented

### 5.2 Audit

- [ ] Dispatch `verifier` in submission mode (all 6 AEA checks PASS)
- [ ] Runtime documented (time a fresh run)

### 5.3 Deposit

- [ ] openICPSR deposit: upload package, obtain DOI
- [ ] Update paper with Data Availability Statement referencing DOI
- [ ] Add data citation to `references.bib`

### AEA README Required Sections

- **Data Availability Statement** — describes all data sources; restricted data has access instructions
- **Computational Requirements** — software + version, packages + versions, hardware, memory (if >8GB), runtime estimate
- **Description of Programs** — what each script does, in order
- **Instructions for Replicators** — step-by-step, from data access to final output

### Audit Tolerance Thresholds (Deposit-time)

| Item | Standard |
|------|----------|
| Table values | Exact match (same software version) |
| Figure appearance | Visual match + same underlying data |
| Runtime estimate | Within 2× documented time |
| Package version mismatch | Warning (not failure) |

---

## Relationship to Other Rules

- **Scripts conventions:** `stata-code-conventions.md` or `r-code-conventions.md`
- **Verifier agent:** `agents/verifier.md` runs the 6-check AEA audit in submission mode using the criteria above
- **Verification:** `verification-protocol.md` handles end-of-task compile/run checks
