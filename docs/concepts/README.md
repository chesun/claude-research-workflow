# Concepts

The "why" pages. These explain the design decisions behind distinctive workflow features. Read these to understand what makes this workflow opinionated, where its rigor comes from, and where its limits are.

---

## In recommended reading order

### Read first — before using the workflow on real research

**[`appropriate-use.md`](appropriate-use.md)** — capable-RA analogy, applied-micro vs behavioral asymmetry, when-to-trust vs when-to-verify table. The most important page in these docs. Explains where the workflow fits (handles execution) and where your judgment remains irreplaceable (substantive expertise, literature knowledge, quality control). Forkers who skip this will produce mediocre research efficiently.

### The distinctive contributions

**[`epistemic-rules.md`](epistemic-rules.md)** — the four-rule "don't fabricate" stack: `no-assumptions`, `primary-source-first`, `derive-don't-guess`, `adversarial-default`. Each prevents a different category of fabrication. Together they form a complete-by-construction stance. The most distinctive feature of this fork.

**[`verification-ledger.md`](verification-ledger.md)** — the cache that makes `adversarial-default` sustainable. File format, six-state lookup protocol, stale-invalidation triggers, cost analysis. Enables "demand evidence on every claim" without re-check bloat.

### How the workflow operates internally

**[`worker-critic-pairs.md`](worker-critic-pairs.md)** — adversarial pairing model: every creator agent has a paired critic; critics never edit; three-strikes escalation when pairs can't converge. Why splitting roles avoids confirmation bias.

**[`quality-scoring.md`](quality-scoring.md)** — weighted aggregate formula, severity-gradient-by-phase, per-target deduction tables, the three gates (80 / 90 / 95). What to do when you hit a gate.

### Comparison with upstream

**[`upstream-differences.md`](upstream-differences.md)** — verified file-by-file accounting of what this fork adds vs `pedrohcgs/claude-code-my-workflow` and `hugosantanna/clo-author`. Net-new vs inherited vs reorganized. Migration notes for forkers coming from either upstream.

---

## Where to go from here

- [`../reference/`](../reference/) — pure catalogues of skills, agents, rules, hooks
- [`../getting-started/`](../getting-started/) — installation and first-session if you haven't gotten there yet
- [`../customization/`](../customization/) — adapting the workflow for your project
- [`../faq.md`](../faq.md) — quick answers to common questions
- [`../README.md`](../README.md) — top-level docs nav hub
