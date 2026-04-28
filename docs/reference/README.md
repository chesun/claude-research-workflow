# Reference

Pure catalogues. Use these when you need to look up a specific skill, agent, rule, hook, or term — not when you want to understand the design (read [`../concepts/`](../concepts/) for that).

---

## Catalogues

- **[`skills.md`](skills.md)** — every `/command` with one-line summary, what it does, what agents it dispatches. Universal skills (14) + applied-micro overlay skills (3) + behavioral overlay skills (5).

- **[`agents.md`](agents.md)** — every agent with one-line role description and worker–critic pairing. Universal agents (17) organized by role (creators, critics, peer-review, infrastructure) + applied-micro overlay (2) + behavioral overlay (6).

- **[`rules.md`](rules.md)** — every rule with one-line summary, organized by category (epistemic stack, workflow / process, writing / output, code conventions, discipline / records, sandbox / experimentation). Universal rules (25) + applied-micro overlay (1) + behavioral overlay (1).

- **[`hooks.md`](hooks.md)** — every hook with event, behavior, escape hatch where applicable. The 11 hooks organized by purpose (citation grounding, session logging, verification, context survival, file protection, notification).

## Lookup utility

- **[`glossary.md`](glossary.md)** — terms used in the docs and rule files, both general technical (git, fork, branch, terminal, CLI, IDE, markdown) and workflow-specific (epistemic stack, worker–critic pair, verification ledger, ADR, three-strikes, etc.). Use for term lookup while reading other pages; bounce back to where you were when the unfamiliar term is resolved.

---

## When to use these vs when to use the source files

These reference pages are *indexes over* `.claude/`. Each entry points at the source-of-truth file (`.claude/skills/<name>/SKILL.md`, `.claude/agents/<name>.md`, `.claude/rules/<name>.md`, `.claude/hooks/<file>.{py,sh}`). For full behaviour, scoring rubrics, system prompts, or hook semantics, read the source file.

The reference pages exist for browsing — getting a sense of what exists in the catalogue — and for cross-linking from the concept pages. The source files exist for depth.

---

## Where to go from here

- [`../concepts/`](../concepts/) — design rationale for the items catalogued here
- [`../getting-started/`](../getting-started/) — installation and first-session
- [`../customization/`](../customization/) — adapting / extending these for your project
- [`../README.md`](../README.md) — top-level docs nav hub
