# Branch model

The workflow ships in three flavours. `main` is the universal trunk; `applied-micro` and `behavioral` are thin overlays maintained on their own branches. Pick one when you clone — the choice shapes which rules, skills, and agents you get out of the box.

---

## Decision tree

If your research fits the description below, pick the corresponding branch.

### Pick `main` if

- You want the paradigm-agnostic version. 17 agents, 14 skills, 25 rules — everything a general empirical project needs (discovery, data engineering, analysis, writing, peer review, submission) without paradigm-specific tooling.
- Your work doesn't fit cleanly into "identification strategy" or "experimental design" categories.
- You're a forker who plans to add your own paradigm-specific tooling on top.

### Pick `applied-micro` if

- You do observational-data research.
- Your identification strategy is one of: DiD (including staggered), event study, IV, RDD, synthetic control, matching.
- You want adversarial review against assumptions like parallel trends, exclusion restrictions, monotonicity, bandwidth choice, density continuity.

What `applied-micro` adds beyond `main`:

| Component | What it does |
|---|---|
| `strategist` agent + `strategist-critic` | Designs identification strategy; the critic checks parallel-trends tests, IV first-stage F, RDD McCrary density, synthetic-control permutation inference. |
| `/strategize` skill | Dispatches strategist + critic. Produces a strategy memo with identification check-offs. |
| `/balance` skill | Treatment–control balance tables with normalized differences. Stata or R. |
| `/event-study` skill | Event-study plots with pre-trends + dynamic effects. Stata or R. Handles classic and staggered DiD. |
| `air-gapped-workflow.md` rule | For projects on restricted-access remote servers (where data can't leave the server). |
| `identification-checklists.md` reference | Per-strategy pre-flight checks |

### Pick `behavioral` if

- You run experiments — lab, online, or hybrid.
- Or you do formal theory in the experimental-economics tradition.
- You want adversarial review against design pitfalls (incentive-compatibility, comprehension, focal values, measurement error, parameter selection, design-hacking).

What `behavioral` adds beyond `main`:

| Component | What it does |
|---|---|
| `designer` agent + `designer-critic` | Designs experiments using the inference-first 14-step checklist; the critic checks IC, comprehension pass rate, randomization integrity, pre-registration filing. |
| `theorist` agent + `theorist-critic` | Develops formal models; the critic verifies proofs, checks assumptions, audits non-vacuity. |
| `otree-specialist` agent | Generates / reviews / explains oTree experiment code (5.x / 6.x). |
| `qualtrics-specialist` agent | Generates / validates / improves Qualtrics surveys (QSF format, custom JS / CSS / HTML). |
| `/design`, `/theory`, `/preregister`, `/otree`, `/qualtrics` skills | The corresponding command interfaces. |
| `experiment-design-principles.md` rule | The 13 non-negotiable design principles with in-line academic attributions (Niederle on hypothesis-driven design, Snowberg and Yariv (2025) on parameter selection, Healy and Leo on IC hierarchy, Gillen 2019 on measurement error, and others). |
| `inference-first-checklist.md` reference | The portable 14-step checklist the designer agent reads when producing designs. |

For the academic provenance behind the behavioral overlay's design rules, see [`../../.claude/rules/experiment-design-principles.md`](../../.claude/rules/experiment-design-principles.md) on the `behavioral` branch.

---

## Switching after the fact

If you picked the wrong branch initially, just `git checkout` the right one. The rules, skills, and agents differ; the project-level files (`CLAUDE.md`, your code, your data) are unaffected because they're outside `.claude/`.

```bash
# Switch from main to applied-micro
git checkout applied-micro

# Or to behavioral
git checkout behavioral
```

If you've made commits on the wrong branch and want to move them, that's a `git rebase` or `git cherry-pick` operation — outside the scope of this page; refer to `git` documentation.

---

## Can I combine overlays?

In short: not without manual merging. The `applied-micro` and `behavioral` overlays diverge at the agent and skill layer (different agents for different review types). They're not designed to compose.

If your research mixes paradigms — for instance, an experiment that you analyze with DiD on quasi-experimental administrative data — pick the dominant paradigm and add the missing pieces from the other branch manually. Or fork twice and treat them as separate projects.

---

## How overlays stay in sync with `main`

`main` is the trunk. Universal improvements (new rules, hook fixes, agent updates that don't depend on a paradigm) land on `main` first, then propagate to `applied-micro` and `behavioral` via cherry-pick or rebase. The two overlays maintain only their *additions* on top of main; they don't carry duplicate copies of universal content.

This means: when you pull updates from upstream, expect `main` updates to flow into your fork's overlay branches via your own merge / rebase. If you're forking and modifying, keep your overlay-specific changes in dedicated commits so they're easy to rebase onto a fresh `main`.

---

## What's next

- [`installation.md`](installation.md) — fork, clone, branch, run
- `first-session.md` *(planned for v0.2.x)* — walkthrough of a typical first day
- [`../concepts/epistemic-rules.md`](../concepts/epistemic-rules.md) — the four-rule "don't fabricate" stack that's universal across all branches
