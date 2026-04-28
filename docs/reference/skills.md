# Skills (slash commands)

Skills are user-invocable commands defined in `.claude/skills/<name>/SKILL.md`. You type `/<name>` in a Claude Code session and the skill fires. Each skill is a focused recipe — it might dispatch a single agent, coordinate multiple, or run a utility. See [`../glossary.md`](glossary.md#skill) for the platform mechanics.

This page is a catalogue. For full skill behaviour, see the corresponding `SKILL.md` file in `.claude/skills/<name>/`.

---

## Universal skills (14, on `main` and inherited by overlays)

### Pipeline skills

| Skill | What it does | Dispatches |
|---|---|---|
| `/new-project` | Full pipeline: idea → paper. Orchestrated through all phases (Discovery → Strategy → Execution → Peer Review → Submission). | `orchestrator` + every worker–critic pair in turn |
| `/discover` | Discovery phase — literature search, data discovery, research interviews, ideation. Subcommands route to the right agents. | `librarian` + `librarian-critic`, `explorer` + `explorer-critic` |
| `/analyze` | End-to-end data analysis dispatching coder + data-engineer for implementation, coder-critic for review. Stata, R, Python, Julia. | `coder`, `data-engineer`, `coder-critic` |
| `/write` | Draft paper sections with the workflow's notation protocol, anti-hedging rules, contribution-statement-in-first-2-pages standard. Includes humanizer pass. | `writer` + `writer-critic` |
| `/review` | All quality reviews — routes to appropriate critics by target file type and flags. `--paper`, `--code`, `--peer`, etc. | Various critics |
| `/revise` | R&R cycle: classify referee comments (NEW ANALYSIS / CLARIFICATION / DISAGREE / MINOR) and route each to the right agent. | Various, depending on classification |
| `/talk` | Create, audit, or compile Beamer presentations. Format-specific (job market / seminar / short / lightning). | `storyteller` + `storyteller-critic` |
| `/submit` | Submission pipeline: journal targeting → replication package → audit → final gate. | `verifier` (submission mode) + `editor` for journal selection |

### Utility skills

| Skill | What it does |
|---|---|
| `/commit` | Stage, commit, create PR, merge to main. The standard commit-PR-merge cycle. |
| `/context-status` | Show current context status (% used, auto-compact distance, what state will be preserved). |
| `/learn` | Extract reusable knowledge from the current session into a persistent skill. Use when you discover something non-obvious worth keeping. |
| `/challenge` | Devil's advocate. Modes: `--paper`, `--identification`, `--design`, `--theory`, `--fresh` (cold read with no context). Stress-tests the work. |
| `/deep-audit` | Deep consistency audit of the entire repository. Launches 4 parallel specialist agents (factual errors, code bugs, count mismatches, cross-document inconsistencies). Loops until clean. |
| `/tools` | Multi-subcommand router. Subcommands: `compile`, `validate-bib`, `journal`, `context-status`, `deploy`, `learn`, `verify`. |

---

## Applied-micro overlay skills (3 additional, on `applied-micro`)

| Skill | What it does | Dispatches |
|---|---|---|
| `/strategize` | Design identification strategy. Produces a strategy memo with identification check-offs (DiD parallel trends, IV first-stage F, RDD McCrary, synthetic-control permutation). | `strategist` + `strategist-critic` |
| `/balance` | Generate balance tables comparing treatment and control groups. LaTeX-ready output with means, differences, p-values, normalized differences. Stata or R. | `coder` + `coder-critic` |
| `/event-study` | Generate event study plots with pre-trends + dynamic effects. Classic and staggered DiD. Stata or R. | `coder` + `coder-critic` |

---

## Behavioral overlay skills (5 additional, on `behavioral`)

| Skill | What it does | Dispatches |
|---|---|---|
| `/design` | Inference-first experiment design via the 14-step checklist. Modes: `experiment` (full checklist), `power` (standalone power analysis). | `designer` + `designer-critic` |
| `/theory` | Formal model development and proof review. Modes: `develop` (build model from assumptions to testable predictions), `review` (verify proofs, check assumptions, audit notation). | `theorist` + `theorist-critic` |
| `/preregister` | Generate pre-registration documents. Supports AsPredicted (11 questions, v2.00) and OSF (Coffman and Dreber 7-item PAP). Hard gate: no data collection without it. | The behavioral pre-reg workflow |
| `/otree` | Generate, review, or explain oTree experiment code. Modes: `create` (scaffold app from design doc), `review` (audit existing code), `explain` (teach oTree concepts). oTree 5.x / 6.x. | `otree-specialist` |
| `/qualtrics` | Create, validate, or improve Qualtrics surveys. Modes: `create` (generate QSF from design doc), `validate` (check exported QSF), `improve` (suggest fixes), `export-js` (custom JS / CSS / HTML). | `qualtrics-specialist` |

---

## How to discover what's available in your session

In a Claude Code session, type `/` to see the slash-command menu — the workflow's skills appear alongside the Claude Code platform's built-in commands. Each shows a one-line description from its `SKILL.md` frontmatter.

For more depth on any skill, ask the agent: "What does `/strategize` actually do?" — the SKILL.md content is loaded into the agent's context, so it can describe behaviour, output format, and which agents get dispatched.

---

## Adding a new skill (for forkers)

To add a skill `/myskill`:

1. Create `.claude/skills/myskill/SKILL.md` with a frontmatter block (`name`, `description`, `tools`) and a body describing what the skill does.
2. The frontmatter `description` should be terse — that's what shows in the slash-command menu.
3. The body is the skill's "system prompt" — what the agent sees when the skill fires.
4. If the skill should respect the workflow's adversarial-pairing convention, dispatch a creator + critic in the body.
5. Test the skill by invoking it in a Claude Code session.

See `.claude/skills/<existing-skill>/SKILL.md` for examples.

---

## Cross-references

- [`agents.md`](agents.md) — the workers / critics that skills dispatch
- [`rules.md`](rules.md) — the conventions skills enforce
- [`../glossary.md`](glossary.md#skill) — platform-level definition with link to Claude Code docs
- `.claude/skills/<name>/SKILL.md` — the source-of-truth file for each skill
