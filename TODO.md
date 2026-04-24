# TODO — Claude Code Applied-Micro Workflow

Last updated: 2026-04-24

## Active

- [ ] *(add current work here)*

## Up Next

- [ ] *(add next tasks here)*

## Waiting On

- [ ] *(add blocked items here)*

## Backlog

- [ ] **Guide site v1** — when 1–2 finished applied-micro projects exist, copy `guide/` scaffolding from `main-lecture-archive` and adapt for applied-micro research workflow. Publish via `quarto publish gh-pages`. Pre-req: real-project examples for the guide.
- [ ] **Guide screenshots/demos** — short demos of `/new-project`, `/strategize`, `/balance`, `/event-study`, `/submit` once guide structure exists.

## Done (recent)

- [x] Phase 1–3 trunk-and-overlays refactor: rebuilt `applied-micro` as thin overlay on universal `main` (which itself was promoted from applied-micro's pre-refactor state). Overlay adds 2 agents (strategist, strategist-critic), 3 skills (strategize, balance, event-study), 1 rule (air-gapped-workflow), 3 references (domain-profile-applied-micro, journal-profiles-applied-micro, identification-checklists), applied-flavored CLAUDE.md + TODO.md. Phase 1.5 caught 5 stale references and fixed inline. Archive: `applied-micro-pre-universal`. — 2026-04-24
- [x] Reverse port prose-quality features from behavioral: writer/writer-critic McCloskey 11-item, Cochrane style flags, Knuth math rules, Cochrane introduction structure; working-paper-format.md concrete reference preamble (biblatex+biber, lmodern, microtype, full theorem envs); storyteller-critic tikz-reviewer dispatch pointer — 2026-04-23
- [x] Add decision-log (ADR) rule + `decisions/` universal folder; port `todo-tracking` rule from behavioral — 2026-04-23
- [x] Port primary-source-first hook + rule from behavioral branch — 2026-04-23
