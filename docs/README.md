# Documentation

Welcome. This directory holds the depth that doesn't fit in [`README.md`](../README.md). Use the section headers below to find what you need.

---

## Quick reference

Two lookup utilities for finding things fast without reading a whole page:

- [`faq.md`](faq.md) — 14 anticipated questions covering installation, branch picking, hooks, customization, citation style, upstream sync, bug reporting, and more. Start here if you have a specific concrete question.
- [`reference/glossary.md`](reference/glossary.md) — terms that may be unfamiliar (git, fork, branch, terminal, CLI, IDE, markdown, ADR, epistemic stack, verification ledger, etc.) with one-paragraph definitions. Use for term lookup while reading other pages.

---

## I'm new to this workflow

Recommended reading order:

1. [`getting-started/prerequisites.md`](getting-started/prerequisites.md) — what you need to know before installing (git basics, terminal, Claude Code CLI, LaTeX, primary analysis language). Curated external resources for each. Skip if you're already comfortable with the tooling.
2. [`getting-started/installation.md`](getting-started/installation.md) — fork → clone → branch-pick → CLAUDE.md customize → first-launch verification. Includes troubleshooting for the eight most common issues.
3. [`getting-started/branch-model.md`](getting-started/branch-model.md) — decision tree for picking `main` vs `applied-micro` vs `behavioral`. What each overlay adds.
4. [`getting-started/first-session.md`](getting-started/first-session.md) — walkthrough of a typical first day. What plan-mode looks like, what agent dispatches feel like, course-correction signals.
5. **Overlay-specific walkthrough** — read both even if you're still evaluating, since these are portable previews of what each overlay offers:
   - [`getting-started/applied-micro.md`](getting-started/applied-micro.md) — `/strategize`, `/balance`, `/event-study`, the strategist + critic agents, the air-gapped-workflow rule, the identification-checklists reference.
   - [`getting-started/behavioral.md`](getting-started/behavioral.md) — `/design`, `/theory`, `/preregister`, `/otree`, `/qualtrics`, the four creator–critic agent pairs, the 13 design principles, the 14-step inference-first checklist.

   Both walkthroughs live on all three branches. Reading them requires no checkout. *Running* the skills they describe requires being on the corresponding overlay branch — `git checkout applied-micro` or `git checkout behavioral`.

> **Before using the workflow on real research, also read [`concepts/appropriate-use.md`](concepts/appropriate-use.md).** It's the most important page in these docs — explains where the workflow fits (handles execution) and where your judgment remains irreplaceable (substantive expertise, literature knowledge, quality control). The applied-micro vs behavioral asymmetry — how much you can lean on the workflow — is discussed in detail.

---

## I want to understand why this workflow makes the choices it does

The `concepts/` pages explain the *what* and *why* of each distinctive design decision:

- [`concepts/appropriate-use.md`](concepts/appropriate-use.md) — capable-RA analogy, applied-micro vs behavioral asymmetry, when-to-trust vs when-to-verify table. Read before real-research use.
- [`concepts/epistemic-rules.md`](concepts/epistemic-rules.md) — the four-rule "don't fabricate" stack (no-assumptions, primary-source-first, derive-don't-guess, adversarial-default). The most distinctive feature.
- [`concepts/verification-ledger.md`](concepts/verification-ledger.md) — what it caches, lookup protocol, file-hash semantics. The cache that makes adversarial-default sustainable.
- [`concepts/worker-critic-pairs.md`](concepts/worker-critic-pairs.md) — adversarial pairing, three-strikes escalation, separation of powers.
- [`concepts/quality-scoring.md`](concepts/quality-scoring.md) — weighted aggregate, deduction tables, the three gates (80 / 90 / 95).
- [`concepts/upstream-differences.md`](concepts/upstream-differences.md) — full diff vs `pedrohcgs/claude-code-my-workflow` and `hugosantanna/clo-author`. Verified file-by-file.

Or read the index: [`concepts/README.md`](concepts/README.md).

---

## I want to look up a specific skill, rule, agent, or hook

The `reference/` pages are catalogues, not tutorials:

- [`reference/skills.md`](reference/skills.md) — every `/command` with what it does and when to use it.
- [`reference/agents.md`](reference/agents.md) — agents and worker–critic mapping.
- [`reference/rules.md`](reference/rules.md) — every rule with one-paragraph summary.
- [`reference/hooks.md`](reference/hooks.md) — what fires when, escape hatches.
- [`reference/glossary.md`](reference/glossary.md) — term lookup.

Or read the index: [`reference/README.md`](reference/README.md).

---

## I'm forking this workflow for my own lab or research group

1. [`../CONTRIBUTING.md`](../CONTRIBUTING.md) — what's in scope here vs what should live in your fork. Fork-attribution boilerplate.
2. [`concepts/upstream-differences.md`](concepts/upstream-differences.md) — what this fork adds vs upstreams, so you know what's new.
3. [`customization/adapting-claude-md.md`](customization/adapting-claude-md.md) — bracketed placeholders in `CLAUDE.md` plus how to add project-specific rules / skills / hooks. Includes the "don't fork-and-stretch the template" principle.

Or read the index: [`customization/README.md`](customization/README.md).

---

## I'm a contributor

[`contributing.md`](contributing.md) summarizes contribution policy — bug issues welcome, PRs case-by-case, fork-encouraged for personal workflows. The full policy lives at [`../CONTRIBUTING.md`](../CONTRIBUTING.md).

---

## Full site map

Every page in `docs/`:

```
docs/
├── README.md                          ← you are here
├── faq.md
├── contributing.md
├── getting-started/
│   ├── README.md                      ← section index
│   ├── prerequisites.md
│   ├── installation.md
│   ├── branch-model.md
│   ├── first-session.md
│   ├── applied-micro.md               ← walkthrough (portable; runnable only on `applied-micro` branch)
│   └── behavioral.md                  ← walkthrough (portable; runnable only on `behavioral` branch)
├── concepts/
│   ├── README.md                      ← section index
│   ├── appropriate-use.md
│   ├── epistemic-rules.md
│   ├── verification-ledger.md
│   ├── worker-critic-pairs.md
│   ├── quality-scoring.md
│   └── upstream-differences.md
├── reference/
│   ├── README.md                      ← section index
│   ├── skills.md
│   ├── agents.md
│   ├── rules.md
│   ├── hooks.md
│   └── glossary.md
└── customization/
    ├── README.md                      ← section index
    └── adapting-claude-md.md
```

24 pages total. Subfolder `README.md` files render as the curated landing page for each section when clicked from GitHub.

---

## Status

Docs set is complete for v0.1.0 (preview release). No new pages planned for v0.2.x — content will be refined based on real user feedback. The repo root [`README.md`](../README.md) remains the canonical short-form pitch; these pages are the long form.
