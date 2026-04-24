# Quality: Scoring, Thresholds, and Severity

---

## 1. Scoring Protocol

**How individual agent scores aggregate into the overall project score.**

### Weighted Aggregation

The overall project score that gates submission (>= 95) is a weighted aggregate:

| Component | Weight | Source Agent |
|-----------|--------|-------------|
| Literature coverage | 8% | librarian-critic's score of librarian |
| Theory/model quality | 15% | theorist-critic's score of theorist |
| **Experimental design** | **25%** | **designer-critic's score of designer** |
| Implementation quality | 7% | qualtrics/otree specialist review |
| Code quality | 10% | coder-critic's score of coder |
| Paper quality | 20% | Average of domain-referee + methods-referee scores |
| Manuscript polish | 10% | writer-critic's score of writer |
| Replication readiness | 5% | verifier pass/fail (0 or 100) |

### Minimum Per Component

No component can be below 80 for submission. A perfect literature review can't compensate for broken identification.

### Score Sources

- Each critic produces a score from 0 to 100 based on its deduction table
- Scores start at 100 and deduct for issues found
- The verifier is pass/fail (mapped to 0 or 100)
- Referee scores are averaged: `(domain-referee + methods-referee) / 2`

### Gate Thresholds

| Gate | Overall Score | Per-Component Minimum | Action |
|------|--------------|----------------------|--------|
| Commit | >= 80 | None enforced | Allowed |
| PR | >= 90 | None enforced | Allowed |
| Submission | >= 95 | >= 80 per component | Allowed |
| Below 80 | < 80 | — | Blocked |

### When Components Are Missing

Not every project uses all components. If a component hasn't been scored:
- It's excluded from the weighted average
- Remaining weights are renormalized
- Example: no theory component → remaining weights renormalized proportionally

---

## 2. Severity Gradient

**Critics calibrate severity based on the phase of the project.**

### Phase-Based Severity

| Phase | Critic Stance | Rationale |
|-------|--------------|-----------|
| Discovery/Ideation | Encouraging (low severity) | Early ideas need space to develop |
| Theory development | Constructive (medium severity) | Math must be rigorous, but alternatives should be suggested |
| Experimental design | **Strict** (high severity) | Bad design = wasted months and money |
| Implementation | Strict (high severity) | Qualtrics/oTree must work correctly |
| Execution/Analysis | Strict (high severity) | Code and paper are near-final — bugs are costly |
| Peer Review | Adversarial (maximum severity) | Simulates real referees — no mercy |
| Presentation | Professional (medium-high) | Talks should be polished but scored as advisory |

### How It Works

The Orchestrator includes the severity level in the critic's prompt:

```
You are reviewing at SEVERITY: HIGH (Execution phase).
Flag all issues. Do not suggest "consider" — state what must change.
```

### Deduction Scaling

The same issue may have different deductions by phase:

| Issue | Discovery | Design | Execution | Peer Review |
|-------|-----------|--------|-----------|-------------|
| Missing citation | -2 | -5 | -10 | -15 |
| Notation inconsistency | -1 | -3 | -5 | -5 |
| Hedging language | — | — | -3 | -5 |
| Missing robustness check | — | -5 | -15 | -20 |
| Missing power analysis | — | -15 | -15 | -20 |
| Design confound | — | -20 | -20 | -20 |
| Wrong clustering | — | -10 | -10 | -15 |

### Principle

Early phases are about getting the direction right. Late phases are about getting the details right. Critics should match their tone and rigor to the phase.

---

## 3. Per-Target Deduction Tables

**Concrete deductions critics apply when scoring their target.** These supplement the severity gradient with target-specific rubrics.

### Paper LaTeX (`paper/main.tex`)

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Compilation failure (pdflatex) | -100 |
| Critical | Numbers in text don't match tables | -25 |
| Critical | Undefined citation | -15 |
| Critical | Broken reference (`\ref`) | -15 |
| Critical | Overfull hbox > 10pt | -10 |
| Critical | Typo in equation | -10 |
| Major | Notation inconsistency | -5 |
| Major | Missing figure/table at referenced path | -5 |
| Major | Hedging language ("interestingly", "it is worth noting") | -3 per (max -15) |
| Minor | Overfull hbox 1–10pt | -1 |
| Minor | Long lines >100 chars (except math formulas) | -1 |

### Stata Scripts (`.do`) — primary

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Script doesn't run | -100 |
| Critical | Domain-specific bugs (wrong clustering, wrong estimand) | -30 |
| Critical | Code doesn't match design / strategy memo | -25 |
| Critical | Hardcoded absolute paths | -20 |
| Major | Missing robustness checks | -15 |
| Major | Missing `set seed` | -10 |
| Major | Missing `esttab`/`outreg2` output | -5 |
| Minor | No documentation headers | -5 |

### R / Python Scripts — secondary

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Syntax errors / script doesn't run | -100 |
| Critical | Domain-specific bugs (wrong clustering, wrong estimand) | -30 |
| Critical | Code doesn't match design / strategy memo | -25 |
| Critical | Hardcoded absolute paths | -20 |
| Major | Missing robustness checks | -15 |
| Major | Wrong clustering level | -15 |
| Major | Missing `set.seed()` | -10 |
| Major | Magnitude of main result implausible | -10 |
| Major | Non-reproducible output (no `sessionInfo()`) | -5 |
| Minor | No documentation headers | -5 |

### Talks (Beamer) — Advisory, Non-Blocking

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Compilation failure | -100 |
| Major | Slide count outside format range | -10 |
| Major | Result not in paper (talk-only result) | -10 |
| Major | Notation mismatch with paper | -5 |
| Minor | Overfull hbox | -2 |
| Minor | Dense slide without spacing fix | -1 |

Talk scores are reported as "Talk: XX/100" but do **not** block commits or PRs.

### Enforcement

- **Score < 80:** block commit; list blocking issues.
- **Score < 90:** allow commit, warn; list recommendations.
- **Score ≥ 95 + all components ≥ 80:** submission-ready.
- User can override with justification (logged in `research_journal.md`).

---

## 4. Replication Tolerance Thresholds

For verifying replication of an external paper or prior versions. See `replication-protocol.md` for the full workflow.

| Quantity | Tolerance | Rationale |
|----------|-----------|-----------|
| Integers (N, counts) | Exact match | No reason for any difference |
| Point estimates | < 0.01 | Rounding in paper display |
| Standard errors | < 0.05 | Bootstrap/clustering variation |
| P-values | Same significance level | Exact p may differ slightly |
| Percentages | < 0.1pp | Display rounding |
| Runtime estimate | Within 2× documented | Machine-dependent |
