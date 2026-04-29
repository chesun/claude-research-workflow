# Agents: Pairs, Separation of Powers, and Escalation

---

## 1. Adversarial Pairing

**Every worker agent has a paired critic. The Orchestrator never dispatches a creator without scheduling its critic.**

### Worker-Critic Pairs

| Worker (Creator) | Critic (Reviewer) | What's Reviewed |
|-----------------|-------------------|-----------------|
| librarian | librarian-critic | Literature coverage, gaps, recency |
| explorer | explorer-critic | Data feasibility, quality, identification fit |
| data-engineer | coder-critic | Data pipeline quality, reproducibility, transformation correctness |
| strategist *(applied-micro overlay)* | strategist-critic | Identification validity, assumptions, robustness |
| designer *(behavioral overlay)* | designer-critic | Experimental design, inference-first checklist |
| theorist *(behavioral overlay)* | theorist-critic | Formal model assumptions, proofs, testable predictions |
| coder | coder-critic | Code quality, reproducibility, code-strategy alignment |
| writer | writer-critic | Manuscript polish, LaTeX quality, hedging |
| storyteller | storyteller-critic | Talk structure, audience calibration, visual quality |

### Peer Review (Special Case)

Peer Review uses a different structure — the Orchestrator dispatches two independent referees:

1. Orchestrator assigns the paper to domain-referee and methods-referee (blind, independent)
2. Both referees produce scored reports
3. Orchestrator synthesizes a decision: Accept / Minor Revisions / Major Revisions / Reject

### Enforcement

- The Orchestrator checks: if a creator artifact exists without a critic score, it is **not approved**
- No artifact advances to the next phase without its critic's score >= 80
- Critics produce scores; creators produce artifacts — never the reverse

---

## 2. Separation of Powers

**Critics may not edit source artifacts. Critics write review reports. Creators never self-score.**

### Two artifact classes

The boundary between "what a critic may write" and "what a critic may not edit" runs along the source-vs-report distinction:

| Class | Examples | Critic permission |
|-------|----------|-------------------|
| **Source artifacts** | `paper/main.tex`, `paper/sections/*.tex`, `talks/*.tex`, `scripts/**/*.{do,R,py}`, `figures/`, `tables/`, `experiments/designs/`, `decisions/*.md`, `theory/`, `data/cleaned/*` | **Read-only** — never edit, rewrite, or "fix" |
| **Report artifacts** | `quality_reports/reviews/<name>_review.md`, scoring tables, deduction breakdowns, escalation memos | **Write encouraged** — produce a record |

A critic that edits source artifacts violates separation of powers. A critic that writes a review report is doing its job: evaluation produces a record.

### What critics DO

- Score artifacts against a rubric
- List issues with severity and deductions
- Suggest fixes (as recommendations, not implementations)
- **Write a review report** to `quality_reports/reviews/YYYY-MM-DD_<target>_<critic>_review.md` so the score and findings are auditable

### What critics DON'T DO

- Edit source files to fix the issues they found
- Rewrite paper sections, scripts, slides, designs, or decisions
- Produce alternative implementations of the artifact under review

**Why:** A critic who fixes their own findings has incentive to find only fixable issues. Separation keeps criticism honest. Writing a review report does not erode that separation — the report is a record, not a rewrite.

### Canonical review-report path

Every critic writes its review to:

```
quality_reports/reviews/YYYY-MM-DD_<target>_<critic>_review.md
```

- `YYYY-MM-DD` — date of the review (UTC; midnight rollover acceptable).
- `<target>` — slug of what was reviewed: `main` (paper), `01-clean` (script), `job_market` (talk), `bibliography`, `strategy-memo`, etc. Pick a stable slug per target so future reviews of the same target glob-match.
- `<critic>` — agent name without the `-critic` suffix where natural: `coder`, `writer`, `storyteller`, `librarian`, `explorer`, `tikz`, `domain`, `methods`, `verifier`, `editor`.

Examples: `2026-04-28_main_writer_review.md`, `2026-04-28_01-clean_coder_review.md`, `2026-04-28_job-market_storyteller_review.md`.

### Required header on every review report

```markdown
# <Target> Review — <Critic>
**Date:** YYYY-MM-DD
**Reviewer:** <critic-agent-name>
**Target:** <path or slug>
**Score:** XX/100 (or PASS/FAIL)
**Status:** Active
**Supersedes:** <prior review path, if applicable>
```

`Status` values: `Active` | `Completed` | `Superseded by <path>` | `Archived`. Default for a freshly written review is `Active`. See `quality_reports/reviews/README.md` for the full lifecycle.

### Creators can't self-score

A creator cannot evaluate the quality of its own work. The score always comes from the paired critic.

| Agent | Creates | Scored By |
|-------|---------|-----------|
| librarian | Annotated bibliography | librarian-critic |
| explorer | Data assessment | explorer-critic |
| data-engineer | Data pipeline and cleaned datasets | coder-critic |
| strategist *(applied-micro overlay)* | Strategy memo | strategist-critic |
| designer *(behavioral overlay)* | Design checklist | designer-critic |
| theorist *(behavioral overlay)* | Formal model and proofs | theorist-critic |
| coder | R/Stata/Python scripts | coder-critic |
| writer | Paper manuscript | writer-critic |
| storyteller | Beamer talk | storyteller-critic |

### Enforcement

The Orchestrator flags violations:

- If a critic invocation produces or modifies a file outside `quality_reports/reviews/` → flag (source-artifact edit).
- If a critic invocation does not produce a `quality_reports/reviews/...` file → flag (no record).
- If a creator reports its own score → discard, dispatch critic.

---

## 2a. Review and Plan Lifecycle

**The reviews/ and plans/ folders are append-mostly, but lifecycle-managed to prevent navigational bloat.**

### Status field

Every review and plan declares a status in its header:

- `Active` — current, load-bearing
- `Completed` — work is shipped or superseded by ADR; kept for history but not actively cited
- `Superseded by <path>` — explicit pointer to the newer review/plan that replaces this one
- `Archived` — moved to `archive/` subdir, kept for git history; not expected to be read

### Supersession protocol

When a critic writes a new review for a target that already has an `Active` review:

1. Read the existing review (find via `ls quality_reports/reviews/*<target>*_<critic>_review.md`).
2. Edit its header: `Status: Superseded by <new-path>`.
3. Move it: `git mv <old> quality_reports/reviews/archive/`.
4. Write the new review with `Supersedes: <archive/old-path>` in its header.

Same protocol for plans (`quality_reports/plans/`).

### Time-based archive

A review or plan in `Status: Completed` with no edits for 90+ days moves to `archive/`. The orchestrator's pre-dispatch step (or a manual `/tools archive-stale` invocation) sweeps these on a slow cadence.

### Index files

Each lifecycle-managed folder maintains an `INDEX.md` listing active items:

```markdown
# Active reviews

- [2026-04-28_main_writer_review.md](2026-04-28_main_writer_review.md) — paper/main.tex, score 92, Active
- [2026-04-25_01-clean_coder_review.md](2026-04-25_01-clean_coder_review.md) — scripts/01_clean.do, score 88, Active
```

Critics consult `INDEX.md` before writing a new review — if an `Active` review for the same target exists, follow the supersession protocol.

### What lives where

- `quality_reports/reviews/` — top-level: `Active` and recently `Completed` reviews
- `quality_reports/reviews/archive/` — `Superseded` and `Archived` reviews; rarely opened
- `quality_reports/plans/` — top-level: `Active`/recent plans
- `quality_reports/plans/archive/` — completed/superseded plans

The convention prevents indefinite top-level growth without losing history. Archive contents are still git-tracked and grep-able.

---

## 3. Three Strikes Escalation

**If a worker-critic pair fails to converge after 3 rounds, the Orchestrator escalates.**

### The Protocol

```
Round 1: Critic reviews → Worker fixes
Round 2: Critic reviews → Worker fixes
Round 3: Critic reviews → Worker fixes
         Still failing?
              ↓
         ESCALATION
```

### Escalation Routing

| Pair | Escalation Target | What Happens |
|------|-------------------|--------------|
| coder + coder-critic | strategist-critic (applied) / designer-critic (behavioral) | Re-evaluates whether the strategy/design is implementable |
| data-engineer + coder-critic | strategist-critic (applied) / designer-critic (behavioral) | Re-evaluates whether the data specification is tractable |
| writer + writer-critic | Orchestrator | Structural rewrite, not just polish |
| strategist + strategist-critic *(applied-micro overlay)* | User | Fundamental design question — needs human judgment |
| designer + designer-critic *(behavioral overlay)* | User | Fundamental experimental design question — needs human judgment |
| theorist + theorist-critic *(behavioral overlay)* | User | Fundamental modeling choice — needs human judgment |
| librarian + librarian-critic | User | Scope disagreement — user decides breadth vs depth |
| explorer + explorer-critic | User | Data feasibility deadlock — user decides resource trade-offs |
| storyteller + storyteller-critic | User | Talk scope/format disagreement |

### Rules

- **Max 3 rounds per pair per invocation** — no infinite loops
- **Escalation is logged** in the research journal with strike count
- **User escalation requires a clear question** — not "they disagree," but "strategist-critic requires X, which contradicts Y. Which takes priority?"
- **Post-escalation:** The worker starts fresh from the escalation target's decision, not from its previous attempt
