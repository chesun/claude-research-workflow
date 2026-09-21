---
name: review-build
description: |
  Run the mandatory independent adversarial review for a load-bearing artefact
  before committing it (per .claude/rules/independent-review.md, ADR-0002).
  Dispatches the lens pair for the target, saves receipts to
  quality_reports/reviews/. Use before committing hooks, bin/ scripts, or a
  substantive rule/agent/skill/plan/ADR change.
argument-hint: "<path> [<path>...]"
allowed-tools: Read, Grep, Glob, Bash, Agent, Write
---

# /review-build — independent review of a load-bearing artefact

Produce the review receipt(s) the commit gate (`review-receipt-check.py`) reads.

## 1. Pick the lens pair by target type

| Target | Lenses |
|---|---|
| code — `.claude/hooks/**`, `bin/**`, `.githooks/**` | **red-team** + **correctness** |
| plan / ADR — `quality_reports/plans/*`, `decisions/NNNN_*` | **fit-for-purpose** + **efficiency** |
| rule — `.claude/rules/*` | **consistency** + **bloat** |
| agent / template / reference / skill | **correctness** (single lens) |

## 2. Dispatch each lens as a fresh general-purpose agent

Rules for every dispatch:

- **Fresh general-purpose agent, never a fork** — the reviewer must not inherit this session's context, or it is not independent.
- **Blind to the other lens** — do not tell it what the sibling lens is doing.
- **Read-only except its one report.** It may read the repo and run read-only commands; it writes only its review file.
- **Assume the artefact is defective** until evidence shows otherwise (`adversarial-default.md`). Every finding carries evidence: `file:line` or a runnable repro. Synthetic sentinels only — never real client/personal data.
- Run the lenses in parallel (one message, multiple Agent calls).

## 3. Report each lens must write

Path: `quality_reports/reviews/YYYY-MM-DD_<target-slug>_<lens>_review.md`. Header exactly:

```
# <Target> Review — <lens>
**Date:** YYYY-MM-DD
**Reviewer:** <lens> critic (independent, general-purpose agent)
**Target:** <every covered path, repo-relative, comma-separated>
**Score:** NN/100
**Status:** Active
```

Then: one-paragraph verdict; a findings table ranked by severity (Critical/High/Medium/Low) with columns Finding | Evidence | Verdict {SOUND/WEAK/WRONG} | Recommendation. Recommendations only — the reviewer never edits the artefact.

## 4. Resolve, then stage

- Fix each finding, or accept it with a one-line reason in the session log.
- A **Critical** additionally gets a verify pass by a fresh agent or a named regression test.
- A second full cycle only if a fix changed the design.
- `git add` the review report(s) so the receipt check sees them in the index, then commit.

## 5. Log the cost

Append one line to the session log: lenses run, agent tokens, wall-clock, findings by severity. Keeps the gate's cost visible so it can be tuned (narrow the gated set if reviews are firing on low-value changes).
