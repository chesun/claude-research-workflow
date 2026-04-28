# Agents

Agents are specialized workers dispatched by Claude Code with their own system prompts and tool permissions. Definitions live in `.claude/agents/<name>.md`. See [`../glossary.md`](glossary.md#agent) for the platform mechanics.

This page is a catalogue. For the full system prompt and behaviour of each agent, see the corresponding `.md` file in `.claude/agents/`. For the worker–critic pairing model, see [`../concepts/worker-critic-pairs.md`](../concepts/worker-critic-pairs.md).

---

## Universal agents (17, on `main`)

### Creator agents (produce artifacts)

| Agent | What it produces | Paired critic |
|---|---|---|
| `librarian` | Annotated bibliography, frontier map, positioning recommendation | `librarian-critic` |
| `explorer` | Data-source assessment, ranked feasibility list | `explorer-critic` |
| `data-engineer` | Cleaning scripts, cleaned datasets, data documentation | `coder-critic` |
| `coder` | Analysis scripts (Stata / R / Python), tables, figures | `coder-critic` |
| `writer` | Paper sections, manuscript drafts | `writer-critic` |
| `storyteller` | Beamer presentations (job market / seminar / short / lightning) | `storyteller-critic` |

### Critic agents (review and score)

| Agent | What it reviews | Reviews output of |
|---|---|---|
| `librarian-critic` | Literature coverage, gaps, recency, journal quality, scope calibration | `librarian` |
| `explorer-critic` | Data feasibility, measurement validity, sample selection, identification compatibility | `explorer` |
| `coder-critic` | Code quality, code–strategy alignment, reproducibility (12 check categories) | `coder`, `data-engineer` |
| `writer-critic` | Manuscript polish, LaTeX quality, anti-hedging, claims–evidence alignment | `writer` |
| `storyteller-critic` | Talk structure, audience calibration, visual quality, paper-to-talk fidelity | `storyteller` |
| `tikz-reviewer` | TikZ diagrams — label positions, overlap, visual consistency, aesthetic quality | Whoever produces TikZ |

### Peer-review agents (independent referees + editor)

| Agent | What it does |
|---|---|
| `domain-referee` | Blind peer reviewer focused on subject expertise. Evaluates contributions, literature positioning, substantive arguments, external validity. |
| `methods-referee` | Blind peer reviewer focused on econometric methods. Evaluates identification, estimation, inference, robustness, replication. |
| `editor` | Synthesizes referee reports into editorial decisions (Accept / Minor Revisions / Major Revisions / Reject). Calibrated by journal culture via `journal-profiles.md`. |

These three are dispatched independently — the orchestrator does not pair them like worker–critic pairs.

### Infrastructure agents

| Agent | What it does |
|---|---|
| `orchestrator` | Manages phase transitions, agent dispatch, escalation routing, score aggregation. The pipeline coordinator; not used when invoking individual skills standalone. |
| `verifier` | Mechanical correctness checks. Two modes: standard (compile + execute + integrity + freshness) and submission (adds the 6-check AEA replication audit). Populates the verification ledger. |

---

## Applied-micro overlay agents (2 additional, on `applied-micro`)

| Agent | Role | Paired critic |
|---|---|---|
| `strategist` | Designs identification strategies (DiD, IV, RDD, synthetic control). Produces strategy memos. | `strategist-critic` |
| `strategist-critic` | Reviews strategy memos through 4 sequential phases (claim, design validity, inference, polish). Checks parallel trends, IV F-stat, RDD McCrary, synthetic-control permutation inference. | reviews `strategist` |

---

## Behavioral overlay agents (6 additional, on `behavioral`)

| Agent | Role | Paired critic |
|---|---|---|
| `designer` | Designs experiments using the inference-first 14-step checklist. Produces design documents covering hypotheses, treatments, IC, power, comprehension, pre-registration. | `designer-critic` |
| `designer-critic` | Reviews experiment designs against the 13 design principles in `experiment-design-principles.md`. Adversarial checks for MPL pitfalls, IC violations, measurement error, parameter selection, focal values, clustering, design-hacking. | reviews `designer` |
| `theorist` | Develops formal models. Produces model setups, definitions, propositions, proofs. | `theorist-critic` |
| `theorist-critic` | Verifies proofs, checks assumptions, audits notation, runs the 16-item theory-quality checklist (including the non-vacuity check — Item 16 — which catches theorems true of no real object). | reviews `theorist` |
| `otree-specialist` | Generates / reviews / explains oTree experiment code. oTree 5.x / 6.x. | (no direct critic; usual `coder-critic` for analysis code that uses the oTree output) |
| `qualtrics-specialist` | Generates / validates / improves Qualtrics surveys. QSF format, custom JS / CSS / HTML. | (no direct critic) |

---

## How agents get dispatched

Two modes:

**Standalone (most common).** A skill invocation directly dispatches one or more agents. Example: `/strategize` dispatches `strategist` then `strategist-critic`.

**Pipeline / orchestrated.** `/new-project` or `/discover` dispatches the orchestrator, which then runs through phases — Discovery → Strategy → Execution → Peer Review → Submission — dispatching agents per phase, sometimes in parallel where they're independent (e.g., `librarian` + `librarian-critic` in parallel with `explorer` + `explorer-critic`).

---

## Adding a new agent (for forkers)

To add a `myagent`:

1. Create `.claude/agents/myagent.md` with frontmatter (`name`, `description`, `tools`, `model`) and a body that's the agent's system prompt.
2. The `description` should be terse — that's what other agents see when deciding whether to dispatch.
3. The body (system prompt) should be focused on one job — agents that try to do too many things produce mediocre output everywhere.
4. If the agent is a creator, also create a paired critic. If it's a critic, define the deduction rubric clearly.
5. Test by dispatching the agent from a skill or directly with the Task tool.

See `.claude/agents/<existing>.md` for examples.

---

## Cross-references

- [`../concepts/worker-critic-pairs.md`](../concepts/worker-critic-pairs.md) — adversarial pairing model
- [`skills.md`](skills.md) — which skills dispatch which agents
- [`../glossary.md`](glossary.md#agent) — platform-level definition with link to Claude Code docs
- `.claude/agents/<name>.md` — the source-of-truth file for each agent
