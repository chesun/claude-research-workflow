# TODO — Claude Code Behavioral Workflow

Last updated: 2026-04-23

## Active
- [ ] Test `/discover lit` with mandatory agent dispatch fix in bdm_bic
- [ ] Test `/design experiment` with mandatory agent dispatch fix in bdm_bic

## Up Next
- [ ] Apply mandatory agent dispatch enforcement to remaining skills (/analyze, /write, /theory, /review, /talk)
- [ ] Share custom Beamer templates (pdflatex and xelatex)
- [ ] Provide a sample `.doh` file
- [ ] Clarify Stata license type (SE vs MP)

## Waiting On
- [ ] Set up Overleaf git sync for BDM and JMP — waiting on Christina
- [ ] Consolidate JMP satellite repos into main JMP repo — waiting on Christina
- [ ] Share swift raid Claude Chat memory/output — waiting on Christina

## Backlog
- [ ] Review and refine journal profiles after testing `/review --peer`
- [ ] Identify additional referee concerns from real reviews
- [ ] Customize notation conventions to Christina's exact preferences
- [ ] Set up Stata package auto-discovery hook

## Done (recent)
- [x] Port LaTeX features from applied-micro: writer-critic Critical Rules (ignore commented LaTeX, regression tables as source of truth), tikz-reviewer agent, tikz-visual-quality rule, storyteller-critic tikz dispatch pointer — 2026-04-23
- [x] Backport decision-log (ADR) rule from BDM + `decisions/` universal folder + template README; port `todo-tracking` rule to applied-micro — 2026-04-23
- [x] Port primary-source-first hook + rule from `behavioral` to `applied-micro` (cherry-pick with manual CLAUDE.md conflict resolve) — 2026-04-23
- [x] Backport primary-source-first rule + PreToolUse + Stop hooks from BDM BIC (generalized: externalized surname allowlist, generic paths, sanitized rule doc); added `master_supporting_docs/literature/{papers,reading_notes}/` to universal folder structure — 2026-04-23
- [x] Expand seminal papers list (37 → 232 entries, 12 sections) — 2026-03-29
- [x] Analyze JMP Qualtrics QSF files (3 files, 14 patterns documented) — 2026-03-29
- [x] Enrich qualtrics skill and agent from JMP patterns — 2026-03-29
- [x] Create qualtrics reference doc + auto-learning — 2026-03-29
- [x] Fix mandatory agent dispatch in /discover and /design — 2026-03-29
- [x] Fix Mendeley-first search order in /discover lit — 2026-03-29
- [x] Copy workflow infrastructure to bdm_bic — 2026-03-29
- [x] Export QSF for qualtrics skill development — 2026-03-29
