# Getting started

Pages for new users. The recommended reading order:

1. **[`prerequisites.md`](prerequisites.md)** — what you need to know before installing (git, terminal, Claude Code, LaTeX, primary analysis language). Curated external resources for each, with rough time estimates. Skip if you're already comfortable with the tooling.

2. **[`installation.md`](installation.md)** — fork → clone → branch-pick → CLAUDE.md customize → verify. Plus troubleshooting for the eight most common installation issues.

3. **[`branch-model.md`](branch-model.md)** — decision tree for picking `main` vs `applied-micro` vs `behavioral`. What each overlay adds beyond `main`. Switching between branches.

4. **[`first-session.md`](first-session.md)** — walkthrough of a typical first day. First-prompt template, what plan-mode looks like, agent-dispatch experience, course-correction signals, what gets preserved at end of session.

---

## Overlay-specific walkthroughs

5. **[`applied-micro.md`](applied-micro.md)** — walkthrough of the `applied-micro` overlay's three skills (`/strategize`, `/balance`, `/event-study`), the strategist + critic agent pair, the air-gapped-workflow rule, and the identification-checklists reference. **Read this even if you're on `main`** — it's the most useful preview of what `applied-micro` offers before you check it out. The actual skills/agents/rules live only on the `applied-micro` branch; this walkthrough describes them from any branch.
6. **[`behavioral.md`](behavioral.md)** — walkthrough of the `behavioral` overlay's five skills (`/design`, `/theory`, `/preregister`, `/otree`, `/qualtrics`), the four creator–critic agent pairs, the 13 design principles in `experiment-design-principles.md`, and the 14-step `inference-first-checklist.md`. **Read this even if you're on `main`** — preview of what `behavioral` offers. The actual content lives only on the `behavioral` branch; this walkthrough is portable.

Both walkthroughs live on all three branches so anyone evaluating the workflow can read them without first checking out an overlay. They describe what each overlay adds; running the skills they describe requires being on the corresponding branch.

---

## Where to go after getting started

- [`../concepts/`](../concepts/) — why the workflow is shaped the way it is
- [`../reference/`](../reference/) — catalogues of skills, agents, rules, hooks
- [`../customization/`](../customization/) — adapting `CLAUDE.md` and adding project-specific rules / skills / hooks
- [`../faq.md`](../faq.md) — anticipated questions
- [`../README.md`](../README.md) — top-level docs nav hub
