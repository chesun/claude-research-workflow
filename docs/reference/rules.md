# Rules

Rules are markdown files in `.claude/rules/` that codify workflow conventions. They're loaded into every agent's context via the `CLAUDE.md` import system. Some apply universally; others are scoped to specific paths.

This page is a catalogue with one-line summaries. For full rule semantics, read the corresponding `.md` file.

---

## Universal rules (25, on `main`)

### Epistemic stack — the four "don't fabricate" guards

| Rule | One-line summary |
|---|---|
| `no-assumptions.md` | Don't guess about user-side facts (preferences, deadlines, target journal, infrastructure). Ask, leave out, or explicitly disclose the assumption. |
| `primary-source-first.md` | Don't make framing claims about external papers without reading them. Hook-enforced. Includes citation-style convention (two-coauthor "Author and Author (year)"). |
| `derive-dont-guess.md` | Don't fabricate facts the repo encodes (filepaths, variable names, macros, output conventions). Cite source `file:line` for derived entities. |
| `adversarial-default.md` | Don't claim compliance without evidence. Verification ledger caches results to prevent re-check bloat. Six per-domain checklists. |

See [`../concepts/epistemic-rules.md`](../concepts/epistemic-rules.md) for depth.

### Workflow / process

| Rule | One-line summary |
|---|---|
| `agents.md` | Worker–critic pairing, separation of powers (critics never create), three-strikes escalation routing. |
| `workflow.md` | Plan-first protocol, the orchestrator loop, dependency graph, parallel dispatch, simplified mode for explorations. |
| `quality.md` | Weighted aggregate score, severity gradient by phase, per-target deduction tables, gates (80 / 90 / 95). |
| `logging.md` | Session logs (incremental + hard-cap reminder), session report (consolidated), research journal (agent-output append-only log). |
| `revision.md` | R&R cycle: comment classification (NEW ANALYSIS / CLARIFICATION / DISAGREE / MINOR), routing to agents, response-letter mapping. |

### Writing / output

| Rule | One-line summary |
|---|---|
| `working-paper-format.md` | Economics-specific LaTeX preamble standards. `biblatex` + `biber` (not `natbib`); `lmodern`; `microtype`; deduction tables for the writer-critic. |
| `figures.md` | Publication-quality ggplot / Stata graphs. No in-figure titles; serif fonts; vector PDF output; transparent backgrounds. Banned patterns. |
| `tables.md` | Booktabs, no vertical lines, threeparttable for notes. esttab / fixest::etable / modelsummary. Bare tabular fragments only — float wrapper in the paper. |
| `tikz-visual-quality.md` | TikZ diagram standards — label positioning, overlap, visual consistency. |
| `single-source-of-truth.md` | Paper as authoritative. Talks and supplementary derive from it. SSOT chain. Per-format slide counts. |
| `replication-protocol.md` | 5-phase protocol from inventory through AEA-deposit prep. Concrete tolerance thresholds. AEA README required sections. |
| `verification-protocol.md` | Per-target end-of-task verification checklists (paper LaTeX, talks, R, Stata, Python). |

### Code conventions

| Rule | One-line summary |
|---|---|
| `stata-code-conventions.md` | Project structure (master + settings + numbered .do files), packages, table export (esttab / texsave), figures, regression-command standards. |
| `r-code-conventions.md` | Reproducibility (`set.seed()` once, `library()` not `require()`), function design, domain correctness (TWFE diagnostics, IV F-stat, RDD McCrary), common pitfalls. |
| `python-code-conventions.md` | Virtualenv default, pinned dependencies, type hints, seed once, `pathlib.Path` for paths, no Jupyter for production. |

### Discipline / records

| Rule | One-line summary |
|---|---|
| `decision-log.md` | ADRs in `decisions/NNNN_slug.md`. Append-only, immutable once `Decided`, supersession via new ADRs. |
| `todo-tracking.md` | Project root `TODO.md` with Active / Up Next / Waiting / Backlog / Done sections. Update after completing tasks. |
| `output-length.md` | Responses > 15 lines write to a markdown file rather than printing inline. |
| `meta-governance.md` | This repository's dual nature (working project + public template). Decision rule for what gets committed. |

### Sandbox / experimentation

| Rule | One-line summary |
|---|---|
| `exploration-folder-protocol.md` | Conventions for the `explorations/` sandbox — README per exploration, archive when superseded. |
| `exploration-fast-track.md` | Lightweight protocol for quick experiments that don't need full plan-first treatment. |

---

## Applied-micro overlay rules (1 additional, on `applied-micro`)

| Rule | One-line summary |
|---|---|
| `air-gapped-workflow.md` | Conventions for projects on restricted-access remote servers (data can't leave the server). Edit locally, upload via SSH/SFTP, execute remotely. |

Plus modifications to several universal rules to add applied-micro-specific content (`stata-code-conventions.md` with TWFE warnings, `r-code-conventions.md` with `did::att_gt` configuration, etc.).

---

## Behavioral overlay rules (1 additional, on `behavioral`)

| Rule | One-line summary |
|---|---|
| `experiment-design-principles.md` | The 13 non-negotiable design principles. Carries in-line academic attributions (Niederle on hypothesis-driven design, Snowberg and Yariv (2025) on parameter selection, Healy and Leo on IC hierarchy, Gillen 2019 on measurement error, others). |

Plus the references file `inference-first-checklist.md` (in `.claude/references/`) which is the operationalized 14-step checklist the designer agent reads.

---

## How rules get loaded

Claude Code reads `CLAUDE.md` at the start of every session. `CLAUDE.md` lists which rules are active and at what scope. Rules with file-path scopes (e.g., `figures.md` applies to `**/figures.md`) only fire when an agent edits a matching path. Universal rules apply to every agent invocation.

See the [Claude Code Memory documentation](https://code.claude.com/docs/en/memory) for the import system mechanics.

---

## Adding a new rule (for forkers)

To add a `myrule.md`:

1. Create `.claude/rules/myrule.md` with a leading paragraph summarizing the rule, then sections for principle / scope / mechanics / examples.
2. If the rule has a path scope, declare it at the top: `**Scope:** path/pattern/**`. Otherwise it's universal.
3. Reference the rule from `CLAUDE.md` so it gets loaded.
4. If the rule has a corresponding deduction in a critic's rubric, update `quality.md`.
5. Consider whether the rule needs hook enforcement — most don't, but some (like `primary-source-first`) do.

See `.claude/rules/<existing>.md` for examples.

---

## Cross-references

- [`../concepts/epistemic-rules.md`](../concepts/epistemic-rules.md) — depth on the four-rule stack
- [`../concepts/quality-scoring.md`](../concepts/quality-scoring.md) — how rules' deductions roll up into component scores
- [`agents.md`](agents.md) — agents whose system prompts internalize these rules
- [`hooks.md`](hooks.md) — hooks that enforce some rules deterministically
- [`../glossary.md`](glossary.md#rule) — platform-level definition with link to Claude Code memory docs
