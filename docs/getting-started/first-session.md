# Your first session

This page walks through what to expect on day one with the workflow. The goal: by the end, you'll know what to invoke, what plan-mode looks like, what agent dispatches feel like, and how to course-correct when something's off.

If you haven't installed yet, read [`installation.md`](installation.md) first. If git or terminal basics are unfamiliar, [`prerequisites.md`](prerequisites.md) points at resources.

---

## Open Claude Code in your project directory

```bash
cd my-project   # or whatever you named your fork's clone
claude
```

You'll see the Claude Code prompt. The workflow's `CLAUDE.md` loads automatically — Claude has context for your project before you say anything.

---

## A typical first prompt

The workflow is contractor-mode: you describe the goal, Claude plans and executes. A useful first prompt for any new project:

> I'm starting work on [your project, in 1–3 sentences]. I want to [your immediate goal — e.g., draft a strategy memo, set up the data-cleaning pipeline, write a literature review, design an experiment]. Read `CLAUDE.md`, look at what's already in this repo, and propose a plan in plan mode.

Two things to do here:

1. **Be specific about the goal.** "Help me with the project" produces vague output. "Help me draft an identification-strategy memo for the minimum-wage paper, given the dataset documentation in `data/raw/README.md`" produces something you can react to.
2. **Ask for plan mode.** Plan mode is the workflow's standard before non-trivial work. Claude proposes the approach; you approve or redirect; only then does code get written.

---

## What plan mode looks like

When plan mode fires, Claude responds with a structured proposal — typically:

- **Goal** (one sentence restating what you asked for)
- **Approach** (3–8 numbered steps)
- **Files to be created or modified**
- **Verification steps** (how Claude will know each step worked)
- **Open questions** (things Claude needs from you)

Read this carefully. You have three options:

- **Approve as-is.** Type "go ahead" or "approved" and Claude executes.
- **Redirect.** "Skip step 3 — I'll handle that myself." Or: "Add a robustness check using clustered standard errors at the state level." The plan iterates.
- **Reject.** "Wait, I want to do something different — let me think." No code is written until you approve.

The plan is saved to `quality_reports/plans/YYYY-MM-DD_<short-description>.md` so it survives context compression and you can refer back to it later.

---

## What agent dispatches look like

Once you've approved a plan, Claude executes. For non-trivial work, this involves dispatching specialized agents — `coder` to write code, `coder-critic` to review it, `writer` to draft prose, `writer-critic` to evaluate.

You'll see things like:

> *Dispatching `coder` agent to implement the cleaning script...*
>
> [code is written]
>
> *Dispatching `coder-critic` for review...*
>
> [score: 87/100. Issues: missing `set seed`, no esttab output for Table 2.]
>
> *Looping back to `coder` to fix the deductions...*

The pair iterates up to three rounds before escalating. You don't usually need to intervene mid-loop — let the pair converge. If they fail to converge after three rounds, the orchestrator escalates to either you or a higher-level critic; you'll see a clear signal when that happens.

You CAN intervene mid-loop if needed: "Stop — I want to review the script before the critic runs." Type that and Claude pauses, you read, you redirect, work resumes.

---

## What to expect from quality scores

Each component (literature, data, strategy, code, paper, polish, replication) gets a score from its critic. The scores aggregate into an overall project score. Three thresholds matter:

- **80** — commit gate (work isn't broken)
- **90** — PR gate (good enough to share)
- **95 + every component ≥ 80** — submission gate (journal-ready)

If a critic produces a score below the gate you're trying to clear, the workflow blocks the next step until you fix the deductions. The critic's report lists exactly which lines, which deductions, which severity. Pick the path: fix, override with documented reason, or escalate.

For depth on scoring see [`../concepts/quality-scoring.md`](../concepts/quality-scoring.md).

---

## When the primary-source-first hook fires

If you (or Claude) cite a paper in a load-bearing artifact (`decisions/`, `quality_reports/plans/`, `quality_reports/session_logs/`, `quality_reports/reviews/`, `theory/`) without having grounded the citation in reading notes, the hook blocks the edit.

The error message tells you what to do: either add the PDF to `master_supporting_docs/literature/papers/` and produce a reading-notes file, or use the escape-hatch comment `<!-- primary-source-ok: <stem> -->` if the citation is illustrative or test-case-only (not a fresh framing claim about the paper).

For depth see [`../concepts/epistemic-rules.md`](../concepts/epistemic-rules.md) (the section on `primary-source-first.md`) and [`../../.claude/rules/primary-source-first.md`](../../.claude/rules/primary-source-first.md).

---

## Course-correction signals

A few things to watch for and how to handle them:

| Signal | What's happening | What to do |
|---|---|---|
| Claude proposes a path that doesn't fit your project | Workflow defaults clashing with your specifics | Redirect explicitly: "no, this project uses X instead of the default Y because Z" |
| Critic deducts heavily on something you disagree with | Critic's rule is too strict for your case | Override with documented reason in `research_journal.md`, OR fix the deduction the critic suggests |
| Pair fails to converge after 3 rounds | Worker–critic disagreement is structural | The orchestrator should escalate automatically. If it doesn't, force escalation: "Escalate this to me — I'll resolve" |
| Claude makes a claim about a paper without reading it | Primary-source-first not catching subtle framing | The Stop hook will flag at turn-end. Resolve as the hook prompts. |
| Claude proceeds without asking when the answer wasn't in `CLAUDE.md` | `no-assumptions` not catching | Tell Claude to read [`../concepts/appropriate-use.md`](../concepts/appropriate-use.md) and re-evaluate |
| Output looks plausible but you suspect substantive issues | Workflow can't catch substantive defects (only mechanical) | Apply your judgment — see [`../concepts/appropriate-use.md`](../concepts/appropriate-use.md). The workflow doesn't substitute for expertise. |

---

## End of session: what gets preserved

When you wrap up a session, several things persist for next time:

- **Plans** in `quality_reports/plans/` — survive context compression and across sessions.
- **Session logs** in `quality_reports/session_logs/` — agents append here as work progresses.
- **ADRs** in `decisions/` — substantive decisions captured in `NNNN_slug.md` format.
- **Verification ledger** in `.claude/state/verification-ledger.md` — cached check results so unchanged artifacts aren't re-checked.
- **Auto-memory** at `~/.claude/projects/<hash>/memory/` — Claude Code's per-project memory, separate from the workflow's git-tracked records.

Next session, Claude reads `CLAUDE.md` + the most recent plan + the latest session log, plus any ADRs referenced. It picks up roughly where you left off without being re-briefed.

---

## A common first day, by example

| Task | Skill | What happens |
|---|---|---|
| Set up the project | Edit `CLAUDE.md` placeholders | Done by you; takes 5 minutes |
| Initial research-question scoping | `/discover interview` | `librarian` + `librarian-critic` and/or `explorer` + `explorer-critic` dispatch; produces a research spec |
| Identify identification strategy *(applied-micro)* | `/strategize` | `strategist` + `strategist-critic`; produces a strategy memo with identification check-offs |
| Set up cleaning pipeline | `/analyze` | `data-engineer` + `coder-critic`; produces cleaning scripts |
| Or design a brand-new experiment *(behavioral)* | `/design` | `designer` + `designer-critic`; produces an experiment design document |

That's a full day of orientation. Each step ends with a saved artifact, a session-log entry, and (for substantive decisions) an ADR.

---

## When you don't know what to do

Two skills are useful as default actions:

- **`/discover interview`** — asks structured questions about your project, produces a research spec. Useful if you're not sure where to start.
- **`/challenge --fresh`** — devil's-advocate cold read. Useful if you have something but want it stress-tested.

Or just describe your situation in plain English and ask Claude to suggest the right skill: "I have a working draft and I'm worried about referee objections — what should I run?"

---

## Cross-references

- [`installation.md`](installation.md) — fork → clone → branch → first-launch
- [`branch-model.md`](branch-model.md) — picking the right branch
- [`../concepts/appropriate-use.md`](../concepts/appropriate-use.md) — what the workflow can and can't do for you
- [`../concepts/worker-critic-pairs.md`](../concepts/worker-critic-pairs.md) — how the pair interactions work
- [`../concepts/quality-scoring.md`](../concepts/quality-scoring.md) — how scores aggregate and gates work
- [`../reference/skills.md`](../reference/skills.md) — full skill catalogue
