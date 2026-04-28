# Adapting `CLAUDE.md` for your project

`CLAUDE.md` at the project root is the file Claude Code reads at the start of every session. The workflow's universal version ships with bracketed placeholders — fill those in, and the workflow knows what your project is. This page walks through each placeholder and shows how to extend the file with project-specific rules.

For the platform mechanics of how `CLAUDE.md` is loaded, see the [Claude Code Memory documentation](https://code.claude.com/docs/en/memory).

---

## The bracketed placeholders

`CLAUDE.md` lists six fields at the top:

```markdown
**Project:** [YOUR PROJECT NAME]
**Institution:** [YOUR INSTITUTION]
**Branch:** main (universal)
**Primary analysis language:** [e.g., Stata 17 / R / Python / Julia]
**LaTeX engine:** [pdflatex | xelatex]
**Overleaf path:** [optional ...]
```

Replace each:

### Project

Free text. The name your project goes by — could be a working title, a slug, or a descriptive phrase. Used by agents in their session-start orientation; doesn't need to be the eventual paper title.

```markdown
**Project:** Minimum Wage and Teen Employment, 2010–2024
```

### Institution

Where the work is happening. Used by `/submit` for affiliation strings and by `writer` when adding `\thanks{}` footnotes. Multiple institutions: separate with semicolons.

```markdown
**Institution:** UC Davis Department of Economics
```

### Branch

`main`, `applied-micro`, or `behavioral`. Don't change this manually — it's set by which branch you're on. If you `git checkout applied-micro`, the CLAUDE.md on that branch already says `applied-micro`.

### Primary analysis language

What language your analysis scripts use. Affects which code-conventions rule applies (`stata-code-conventions.md`, `r-code-conventions.md`, `python-code-conventions.md`) and which agents and skills get prioritized in dispatch.

Acceptable values:

- `Stata 17` (or `Stata 18`)
- `R 4.x`
- `Python 3.10+`
- `Julia 1.x`
- combinations: `Stata 17 (primary), R 4.4 (figures and DiD diagnostics)` if you mix

```markdown
**Primary analysis language:** Stata 17
```

### LaTeX engine

`pdflatex` or `xelatex`. Affects which compile commands `/tools compile` runs and which preamble setup the `working-paper-format.md` rule expects. The default in this fork is `pdflatex`. Pick `xelatex` if you need OpenType fonts or non-Latin scripts.

```markdown
**LaTeX engine:** pdflatex
```

### Overleaf path

Optional. If you keep your paper LaTeX in an Overleaf project that syncs to your machine via Dropbox, set this field to the local path of that directory. The compile and verify tooling will target that path instead of the in-repo `paper/` and `talks/`.

```markdown
**Overleaf path:** ~/Library/CloudStorage/Dropbox/Apps/Overleaf/min-wage-paper
```

If you don't use Overleaf, leave this field blank or remove the line entirely.

---

## The "Current Project State" table

At the bottom of `CLAUDE.md`, the table tracking project-component status:

```markdown
| Component | File | Status | Description |
|-----------|------|--------|-------------|
| Paper | `paper/main.tex` | [draft/submitted/R&R] | [Brief description] |
| Data | `scripts/` | [complete/in-progress] | [Analysis description] |
| Replication | `replication/` | [not started/ready] | [Deposit status] |
| Job Market Talk | `talks/job_market_talk.tex` | — | [Status] |
```

Update the **Status** and **Description** cells as your project evolves. The table is a living summary that loads into every Claude Code session — keeping it current means agents have accurate context without you re-explaining each session.

For projects with multiple papers / chapters / sub-components, add rows. For overlay branches, add overlay-specific rows (e.g., on `behavioral`, you might add Theory, Experiment Design, Pre-registration, oTree code).

---

## Adding project-specific rules

The universal rules in `.claude/rules/` are starting points. Many real projects need additions — a `do-file naming convention.md` for a Stata-heavy project, a `clustering-conventions.md` for a project with idiosyncratic clustering, a `coauthor-process.md` for a collaboration with specific PR-review steps.

To add a project-specific rule:

1. Create the file in `.claude/rules/<my-rule>.md`.
2. Start with `**Scope:**` declaration if the rule applies to specific paths only:
   ```markdown
   # My Project's Stata Naming

   **Scope:** `scripts/stata/**/*.do`

   The body of the rule.
   ```
3. Follow the same structure as existing rules: principle / scope / mechanics / examples / cross-references.
4. Reference the rule from `CLAUDE.md`'s "Core Principles" section so it loads at session start.
5. If the rule should affect critic deductions, update `quality.md`'s deduction table for the relevant target.

For deeper guidance on rule structure, read several existing rules in `.claude/rules/` — they share a common shape.

---

## Adding project-specific skills

If you find yourself repeatedly invoking the same multi-step prompt (e.g., "generate a balance table for the latest cleaned data"), it's a candidate to become a skill.

To add a skill `/myskill`:

1. Create `.claude/skills/myskill/SKILL.md` with frontmatter (`name`, `description`, `tools`) and a body.
2. The frontmatter `description` is what shows in Claude Code's slash-command menu — keep it terse.
3. The body is the skill's "system prompt" — what Claude sees when the skill fires. Be specific about inputs, outputs, and what agents to dispatch.
4. Test the skill in a Claude Code session.

See `.claude/skills/<existing>/SKILL.md` for examples and [Claude Code Skills documentation](https://code.claude.com/docs/en/skills) for platform mechanics.

---

## Adding project-specific hooks

Project-specific hooks are less common than rules or skills, but useful for enforcement that needs to be deterministic. Examples: blocking commits to a specific data directory, validating a custom file format on save, requiring a specific git-commit-message template.

To add a hook:

1. Write the hook script in `.claude/hooks/<my-hook>.{py,sh}`. Read JSON from stdin, write to stdout/stderr per the [Claude Code Hooks documentation](https://code.claude.com/docs/en/hooks). Make executable with `chmod +x`.
2. Wire it up in `.claude/settings.json` under the appropriate event (PreToolUse, PostToolUse, Stop, etc.).
3. If the hook has non-trivial logic, write tests at `.claude/hooks/test_<hook>.py`.

Project-specific hooks should NOT be added to `settings.json` if you intend to upstream the project structure as a fork — they belong in `settings.local.json`, which is gitignored. That keeps the public-template version of the workflow uncluttered.

---

## Don't fork-and-stretch the template

A common failure mode for forkers: keep adding rules, skills, hooks, and customizations until the project's `.claude/` is unrecognizable from the upstream workflow. This makes future workflow updates impossible to merge.

The cleaner approach: keep your customizations *in named, documented additions* — files with clear names like `my-project-stata-conventions.md` rather than edits to `stata-code-conventions.md`. When a workflow update modifies the universal rule, your project file is unaffected. The cost is a slightly longer load list in `CLAUDE.md`; the benefit is being able to pull upstream updates without merge hell.

---

## Cross-references

- The current project's `CLAUDE.md` (at the repo root) — read what's already there before adding
- [`../reference/rules.md`](../reference/rules.md) — the universal rule catalogue you're starting from
- [`../reference/skills.md`](../reference/skills.md) — the universal skill catalogue
- [`../reference/hooks.md`](../reference/hooks.md) — the universal hook catalogue
- [Claude Code Memory documentation](https://code.claude.com/docs/en/memory) — platform mechanics for `CLAUDE.md` loading and import
