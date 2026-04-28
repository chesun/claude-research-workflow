# Documentation

Welcome. This directory holds the depth that doesn't fit in [`README.md`](../README.md). Pick a path based on where you are.

---

## I'm new to this workflow

Two prerequisites paths depending on where you're starting:

- **Have you used git, the terminal, and Claude Code before?** → start at [`getting-started/installation.md`](getting-started/installation.md).
- **Any of those unfamiliar?** → start at [`getting-started/prerequisites.md`](getting-started/prerequisites.md). It points at external resources that get you to working competence in ~3 hours of reading. Come back when you're ready.

After installation, decide which branch you want — [`getting-started/branch-model.md`](getting-started/branch-model.md) walks through `main` vs `applied-micro` vs `behavioral` with one-line guidance for picking. Then read [`getting-started/first-session.md`](getting-started/first-session.md) to see what a typical first day with the workflow looks like.

**Before using the workflow on real research, also read [`concepts/appropriate-use.md`](concepts/appropriate-use.md).** It's the most important page in these docs — explains where the workflow fits (handles execution) and where your judgment remains irreplaceable (substantive expertise, literature knowledge, quality control). The applied-micro vs behavioral asymmetry — how much you can lean on the workflow — is discussed there in detail.

## I want to understand why this workflow makes the choices it does

Read the `concepts/` pages — they explain the *what* and *why* of each distinctive design decision:

- [`concepts/epistemic-rules.md`](concepts/epistemic-rules.md) — the four-rule "don't fabricate" stack (no-assumptions, primary-source-first, derive-don't-guess, adversarial-default). The most distinctive feature.
- [`concepts/appropriate-use.md`](concepts/appropriate-use.md) — capable-RA analogy, applied-micro vs behavioral asymmetry, when to trust vs verify. Read before real-research use.
- [`concepts/worker-critic-pairs.md`](concepts/worker-critic-pairs.md) — adversarial pairing, three-strikes escalation, separation of powers.
- [`concepts/quality-scoring.md`](concepts/quality-scoring.md) — weighted aggregate, deduction tables, gates.
- [`concepts/verification-ledger.md`](concepts/verification-ledger.md) — what it caches, lookup protocol, file-hash semantics.
- [`concepts/upstream-differences.md`](concepts/upstream-differences.md) — full diff vs `pedrohcgs/claude-code-my-workflow` and `hugosantanna/clo-author`.

## I want to look up a specific skill, rule, agent, or hook

The `reference/` pages are catalogues, not tutorials:

- [`reference/skills.md`](reference/skills.md) — every `/command` with what it does and when to use it.
- [`reference/agents.md`](reference/agents.md) — agents and worker–critic mapping.
- [`reference/rules.md`](reference/rules.md) — every rule with one-paragraph summary.
- [`reference/hooks.md`](reference/hooks.md) — what fires when, escape hatches.
- [`reference/glossary.md`](reference/glossary.md) — terms that may be unfamiliar (git, fork, branch, terminal, CLI, IDE, etc.) with one-paragraph definitions.

## I'm forking this workflow for my own lab or research group

Read [`../CONTRIBUTING.md`](../CONTRIBUTING.md) for what's in scope here vs what should live in your fork. Then [`concepts/upstream-differences.md`](concepts/upstream-differences.md) for what this fork adds vs upstreams, so you know what's new. Then [`customization/adapting-claude-md.md`](customization/adapting-claude-md.md) for the bracketed placeholders in `CLAUDE.md` plus how to add project-specific rules / skills / hooks.

## I'm a contributor

[`contributing.md`](contributing.md) summarizes contribution policy — bug issues welcome, PRs case-by-case, fork-encouraged for personal workflows.

---

## Status of these docs

This is the v0.1.0 preview docs set. The universal pages are complete: entry points (prerequisites, installation, branch model, first session), concepts (epistemic rules, appropriate use, worker–critic pairs, quality scoring, verification ledger, upstream differences), reference catalogues (skills, agents, rules, hooks, glossary), customization (adapting CLAUDE.md), contributing, and FAQ. Overlay-specific walkthroughs (`getting-started/applied-micro.md` on the `applied-micro` branch and `getting-started/behavioral.md` on `behavioral`) ship in v0.2.x. The `README.md` at the project root remains the canonical short-form pitch; these pages are the long form.
