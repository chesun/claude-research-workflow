# Quality scoring

The workflow assigns a numeric score (0–100) to each component (literature, data, strategy/design, code, paper, polish, replication) and aggregates them into an overall project score. Three thresholds gate progress: 80 for commits, 90 for PRs, 95 + every component ≥ 80 for submission.

This page explains how the scoring works, why the thresholds are where they are, and what to do when you hit a gate.

---

## The aggregate formula

Each critic produces a per-component score (0–100). The overall project score is a weighted sum:

| Component | Weight | Source agent |
|---|---|---|
| Literature coverage | 10% | `librarian-critic` |
| Data quality | 10% | `explorer-critic` |
| Strategy / design validity | 25% | `strategist-critic` (applied) **or** `designer-critic` (behavioral) |
| Code quality | 15% | `coder-critic` |
| Paper quality | 25% | Average of `domain-referee` + `methods-referee` |
| Manuscript polish | 10% | `writer-critic` |
| Replication readiness | 5% | `verifier` (pass/fail mapped to 0/100) |

When a component hasn't been scored yet (e.g., a project still in early discovery has no peer-review score), it's excluded from the average and remaining weights are renormalized.

---

## Per-component scoring

Each critic starts at 100 and deducts based on a per-target rubric. The deduction tables are the meat of `.claude/rules/quality.md`. A few illustrative rows:

### Paper LaTeX (writer-critic)

| Severity | Issue | Deduction |
|---|---|---|
| Critical | Compilation failure (pdflatex/biber) | -100 |
| Critical | Numbers in text don't match tables | -25 |
| Critical | Undefined citation | -15 |
| Critical | Broken `\ref` | -15 |
| Critical | Overfull hbox > 10pt | -10 |
| Major | Notation inconsistency | -5 |
| Major | Hedging language ("interestingly", "it is worth noting") | -3 per occurrence (max -15) |
| Minor | Long lines > 100 chars (except math formulas) | -1 |

### Stata scripts (coder-critic)

| Severity | Issue | Deduction |
|---|---|---|
| Critical | Script doesn't run | -100 |
| Critical | Domain-specific bug (wrong clustering, wrong estimand) | -30 |
| Critical | Code doesn't match strategy memo | -25 |
| Critical | Hardcoded absolute paths | -20 |
| Major | Missing robustness checks | -15 |
| Major | Missing `set seed` | -10 |
| Major | Missing `esttab`/`outreg2` output | -5 |
| Minor | No documentation headers | -5 |

The full deduction tables for paper LaTeX, R scripts, Stata scripts, Python scripts, talks, identification claims, design claims, and bibliography all live in `quality.md`. Critics read them; you don't have to memorize them. The point is that scoring is mechanical — apply the rubric, sum the deductions, that's the score.

---

## Severity gradient by phase

The same issue may have different deductions depending on where in the pipeline it surfaces. The critic-prompt's severity setting is calibrated by phase:

| Phase | Stance | Rationale |
|---|---|---|
| Discovery | Encouraging (low severity) | Early ideas need space to develop |
| Strategy | Constructive (medium) | Identification must be sound, but alternatives should be suggested |
| Execution | Strict (high) | Code and paper are near-final — bugs are costly |
| Peer Review | Adversarial (max) | Simulates real referees — no mercy |
| Presentation | Professional (medium-high) | Talks should be polished but scored as advisory |

Concrete example — a missing citation:

| Phase | Deduction |
|---|---|
| Discovery | -2 |
| Strategy | -5 |
| Execution | -10 |
| Peer Review | -15 |

Same issue, four different costs. The principle: early phases should encourage exploration; late phases should enforce rigor. A first draft that's "encouraging-phase passing" is fine; the same draft at peer-review phase fails.

---

## The three gates

| Gate | Threshold | Per-component minimum | Action if below |
|---|---|---|---|
| Commit | ≥ 80 | None enforced | Block commit; list issues |
| PR | ≥ 90 | None enforced | Block PR; warn |
| Submission | ≥ 95 | ≥ 80 every component | Block submission; list components below 80 |
| Below 80 | — | — | Block all of the above |

Why these specific numbers:

- **80 (commit)** — work isn't broken. Compiles, runs, no obvious major issues. Catches the cases where a commit would just hand-off broken code to the next session.
- **90 (PR)** — work is good enough to share with collaborators. Polish issues remaining; substantive issues resolved.
- **95 + per-component 80 (submission)** — work is journal-ready. Every component is at least "good enough" (no perfect literature review compensating for broken identification).

The per-component minimum is the load-bearing part of the submission gate. A 95 overall with one component at 65 means you have a hidden weakness; the gate forces you to surface and fix it before submission.

---

## What to do when you hit a gate

The critic's report lists the deductions that pushed you below the gate, with severity and specific lines/files. Three options:

1. **Fix the issues**, then re-run the critic. Most common path. Gates exist to catch mistakes that are still cheap to fix.
2. **Override with justification.** If you disagree with a specific deduction (the critic's rule doesn't apply to your case), document the reason in the project's `research_journal.md` and override. Auditable.
3. **Escalate to the worker-critic pair's escalation target** if the disagreement is structural. See [`worker-critic-pairs.md`](worker-critic-pairs.md) § three-strikes loop.

Don't disable critics. The infrastructure costs nothing; running them less catches less.

---

## Talks are advisory, not blocking

Talk scores are reported as "Talk: XX/100" but **do not block** commits or PRs. The reason: talks are derivative artifacts (they derive from the paper); the paper's score is what gates submission. Talks getting a bad score is a signal, not a halt.

---

## Cross-references

- `.claude/rules/quality.md` — the full deduction tables and per-target rubrics
- [`worker-critic-pairs.md`](worker-critic-pairs.md) — how critics produce the per-component scores
- [`epistemic-rules.md`](epistemic-rules.md) — the four rules whose violations show up as deductions in the relevant component's table
- [`appropriate-use.md`](appropriate-use.md) — context for when scoring catches issues vs when human judgment is needed (scoring catches mechanical defects; substantive defects need you)
