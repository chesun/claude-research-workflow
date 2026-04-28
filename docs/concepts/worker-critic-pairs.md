# Worker–critic pairs

Every creator agent in this workflow has a paired critic. The creator produces an artifact (code, paper section, talk, strategy memo, experiment design); the critic evaluates it against a deduction rubric and produces a score. Critics never edit files; creators never self-score. This separation is structural, not advisory.

This page explains why the model is shaped this way, how the pairs interact, and what happens when a pair can't converge.

---

## Why adversarial pairing

Single-agent self-review fails predictably. When the same agent that wrote a paper section also reviews it, two failure modes dominate:

1. **Confirmation bias.** The agent is invested in the work it just produced; finding flaws costs more than declaring success. The bias goes one direction (toward "looks fine") regardless of actual quality.
2. **Blind spots.** The same agent that didn't notice the bug while writing won't notice the same bug while reviewing. Self-review catches typos, not structural mistakes.

Splitting the roles doesn't solve these problems perfectly — the underlying model is the same — but it changes the prompt-level incentives. The critic's job, by construction, is to find issues. The creator's job is to produce. Keeping the roles distinct, with separate system prompts and separate report formats, is enough to surface issues that single-agent self-review consistently misses.

---

## The pair list

| Creator | Critic | Domain |
|---|---|---|
| `librarian` | `librarian-critic` | Literature coverage, gaps, recency |
| `explorer` | `explorer-critic` | Data feasibility, quality, identification fit |
| `data-engineer` | `coder-critic` | Data pipeline quality, reproducibility |
| `coder` | `coder-critic` | Code quality, code–strategy alignment, reproducibility |
| `writer` | `writer-critic` | Manuscript polish, LaTeX quality, anti-hedging |
| `storyteller` | `storyteller-critic` | Talk structure, audience calibration, visual quality |

Plus paradigm-specific pairs in the overlays:

| Creator | Critic | Domain | Branch |
|---|---|---|---|
| `strategist` | `strategist-critic` | Identification validity, assumptions, robustness | `applied-micro` |
| `designer` | `designer-critic` | Experimental design, inference-first checklist | `behavioral` |
| `theorist` | `theorist-critic` | Formal model assumptions, proofs, non-vacuity | `behavioral` |

Note: `coder-critic` reviews both `coder` and `data-engineer` outputs (the latter is data-pipeline code, structurally similar to analysis code).

---

## Peer review uses a different structure

Peer review (the simulated-referees phase) doesn't follow the worker-critic-pair model directly. Instead:

1. The orchestrator dispatches the paper to **`domain-referee`** and **`methods-referee`** as independent blind reviewers.
2. Both produce scored reports.
3. **`editor`** synthesizes the two reports into an editorial decision (Accept / Minor Revisions / Major Revisions / Reject).

The structure mirrors a real journal review where two referees and an editor each have distinct roles. See `agents.md` *(planned for v0.2.x)* and `quality-scoring.md` for how the synthesized score feeds back into the overall component score.

---

## What critics do

Critics produce:

- A **scored report** with a numeric score (0–100, derived from a deduction rubric).
- A **list of issues**, each tagged with severity (Critical / Major / Minor) and a deduction value.
- **Suggestions for fixes**, but as recommendations only — never implementations.

What critics never do:

- Edit source files. The job is to evaluate, not produce.
- Score themselves or other critics' work.
- Run code (only specific critics like `verifier` do).

If a critic invocation produces a file in `scripts/`, `paper/`, or `talks/`, the orchestrator flags it as a violation of the separation-of-powers rule.

---

## What creators do

Creators produce:

- The **artifact** (a script, a paper section, a strategy memo, etc.).
- A **summary** of what was done and what choices were made.

What creators never do:

- Score themselves. The score always comes from the paired critic.
- Implement the critic's fixes silently — they implement them, then resubmit for re-review.

---

## The three-strikes loop

A worker–critic pair has at most three rounds before escalation:

```
Round 1: Critic reviews → Worker fixes → resubmit
Round 2: Critic reviews → Worker fixes → resubmit
Round 3: Critic reviews → Worker fixes → resubmit
         Still failing?
              ↓
         ESCALATION
```

Escalation routing depends on which pair is stuck:

| Pair | Escalation target | Why |
|---|---|---|
| `coder` + `coder-critic` | `strategist-critic` (applied) / `designer-critic` (behavioral) | Maybe the strategy / design is unimplementable, not just the code |
| `data-engineer` + `coder-critic` | `strategist-critic` / `designer-critic` | Maybe the data spec is intractable |
| `writer` + `writer-critic` | Orchestrator (structural rewrite, not just polish) | Writer-critic disagreements often indicate the underlying argument needs restructuring |
| `strategist` / `designer` / `theorist` + their critic | User | Fundamental design questions need human judgment |
| `librarian` + `librarian-critic` | User | Scope disagreement (breadth vs depth) |
| `explorer` + `explorer-critic` | User | Data feasibility deadlock |
| `storyteller` + `storyteller-critic` | User | Talk scope/format disagreement |

The principle: pairs handle execution-level disputes; structural / scope / fundamental-design questions escalate. The user is the final arbiter for design questions. Other senior critics (strategist, designer) are arbiters for execution-level questions in their domain.

After escalation, the worker starts fresh from the escalation target's decision, not from its previous attempt. Resets the loop counter.

---

## Why three rounds

Three is empirical. One round catches obvious issues; the worker fixes; the second round catches subtler issues; the worker fixes; the third round either converges or surfaces that the disagreement is structural rather than tactical. Beyond three, the pair tends to oscillate — same fixes proposed by the worker, same objections from the critic — without convergence. Escalating earlier wastes a round of human attention; escalating later wastes agent compute on a problem the pair can't solve.

Adjustable per project: edit `.claude/rules/agents.md`'s "Three Strikes Escalation" section if you want a different cap.

---

## Logging

Every escalation is logged in `quality_reports/research_journal.md` with strike count, escalation target, and the specific reason. Useful for postmortems ("why did this pair fail to converge?") and for tuning critic prompts when patterns emerge ("the writer-critic always escalates on the same thing — maybe the rule is too strict / the writer is missing something specific").

---

## Cross-references

- [`epistemic-rules.md`](epistemic-rules.md) — the four rules that critics enforce (no-assumptions, primary-source-first, derive-don't-guess, adversarial-default)
- [`quality-scoring.md`](quality-scoring.md) — how the per-pair scores aggregate into the overall component score
- [`appropriate-use.md`](appropriate-use.md) — context for when worker-critic adversarial review catches issues vs when human judgment is irreplaceable
- `.claude/rules/agents.md` — the rule that codifies pairing, separation of powers, and three-strikes escalation
