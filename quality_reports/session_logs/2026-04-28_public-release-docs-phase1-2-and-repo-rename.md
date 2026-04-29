<!-- primary-source-ok: nygard_2011, methodology_2025, author_author_2022, smith_jones_2024, chetty_2014, roth_list_2022 -->
<!--
Citations in this log are illustrative test-cases or escape-hatch references
to fabrication incidents earlier in the session. Not framing claims.
-->

# Session Log: 2026-04-28 — Public release docs (Phase 1, 2a, 2b, 2c-i) + repo rename + license + PDF policy

**Status:** IN PROGRESS — Phase 2c-i complete; Phase 2c-ii (overlay-specific docs) pending.

## Workflow-relevant work since last session log

### Public release prep

- **Repo renamed**: `chesun/claude-code-my-workflow` → `chesun/claude-research-workflow` via `gh repo rename --yes`. Local `origin` remote updated to the new URL. GitHub auto-redirects old URLs. Three files updated to reflect the rename: README clone-URL placeholder, CHANGELOG release-tag link, CONTRIBUTING fork-attribution boilerplate. Upstream references (`pedrohcgs`, `hugosantanna`) intentionally left unchanged — those repos still have their original names.
- **LICENSE updated to dual copyright**. `Pedro H. C. Sant'Anna (original)` + `Christina Sun (research-paper fork)`. Standard MIT pattern for derivative works. Single-owner replacement would be incorrect since Pedro's original code remains under his copyright.
- **PDF distribution policy**. `.gitignore` now excludes `master_supporting_docs/literature/papers/*.pdf` and `**/*.pdf` (copyright + repo-bloat concerns); `master_supporting_docs/literature/papers/README.md` documents the policy and the surname-and-year naming convention for hook compatibility. Reading-notes intentionally not required for the public template — the rule files (e.g., `experiment-design-principles.md`) carry the in-line attributions; docs reference those rule files for citations.

### Phase 1 (entry-point release files) — `6c01c16` on main

- README updated: v0.1.0 preview banner; "Where this fits in your research process" section with capable-RA analogy + applied-micro vs behavioral asymmetry; "Documentation" section pointing at `docs/`; "What this fork adds" section.
- New `CONTRIBUTING.md`: bug-issues welcome, PRs case-by-case, fork-encouraged with attribution-chain template, ground rules (respect epistemic stack, no silent renames, hook tests, conventional commits).
- New `CHANGELOG.md`: v0.1.0 entry covering rule additions / verification ledger / ADRs / replication protocol / code conventions / hooks / three-branch model / quality scoring; Unreleased section pointing at Phase 2 plan.

### Phase 2a (entry-point docs) — `fe4b6bd` (plus 4 follow-up fixes)

7 files: `docs/README.md` (nav hub with three-persona reading paths), `getting-started/{prerequisites, installation, branch-model}.md`, `concepts/{epistemic-rules, appropriate-use}.md`, `reference/glossary.md`, `contributing.md`. The `concepts/appropriate-use.md` page is the most important: capable-RA analogy + applied-micro vs behavioral asymmetry (settled methodology vs novel mechanisms) + when-to-trust-vs-verify table.

User-feedback round added `appropriate-use.md` after first version of `epistemic-rules.md` had a JMP-specific example (replaced with slide-draft). Also added: README docs-pointer section, ADR full name in glossary, Markdown explainer for tech-illiterate audience, section-specific Claude Code documentation links (verified via WebFetch — `code.claude.com/docs/en/<topic>` without `.md` suffix renders properly).

### Phase 2b (concept depth + reference catalogues) — `5cb62ee` + `7945a69`

- 4 concept pages: `worker-critic-pairs.md`, `quality-scoring.md`, `verification-ledger.md`, `upstream-differences.md`.
- 4 reference catalogues: `skills.md`, `agents.md`, `rules.md`, `hooks.md`.

### Overclaiming corrected in `upstream-differences.md` — `4a5362c`

Initial draft attributed many features (tikz-reviewer, methods-referee, domain-referee, multiple hooks) as net-new in this fork without verifying upstream contents. User caught this. Fetched both upstream remotes (`pedrohcgs/claude-code-my-workflow@main` and `hugosantanna/clo-author@main`) and ran a comprehensive provenance check. Verified findings:

- **Truly net-new in this fork** (not in either upstream): 11 rules (the 4 epistemic-stack rules + decision-log + todo-tracking + output-length + figures + tables + python-code-conventions + stata-code-conventions + experiment-design-principles), 4 hook files (primary-source-{check,audit}, primary_source_lib, test_primary_source_lib), 1 skill (`/challenge`), the verification ledger format.
- **Inherited from Pedro**: tikz-reviewer agent, 6 hooks (context-monitor, log-reminder, notify, post-compact-restore, pre-compact, verify-reminder; many heavily modified here but originating with Pedro), 4 skills, 8 rules.
- **Inherited from Hugo**: 12 universal worker-critic agents + strategist + theorist (this fork moves the latter two to overlay branches), 9 universal-trunk skills, 7 rules.

Lesson: the workflow's `primary-source-first` rule applies to claims about upstream repos too. "I think Pedro has X" is not a substitute for `git ls-tree upstream/main:.claude/`. README's "what this fork adds" section also tightened from 5 vague claims to 5 verified ones.

### Phase 2c-i (universal walkthrough + customization + FAQ) — `d315dac` on `docs-v0.1.0-phase2c`

3 files: `getting-started/first-session.md` (typical-first-day walkthrough), `customization/adapting-claude-md.md` (placeholder guide + project-specific extension patterns), `faq.md` (14 anticipated questions). Universal docs now complete; overlay-specific (Phase 2c-ii) pending.

### Hook hygiene improvements (commits across multiple branches)

- `b1f9bfb` — citation-style convention added to `primary-source-first.md` (two-coauthor "Author and Author (year)").
- `0742d27` — `NEVER_SURNAMES` blocklist expanded with role-words (`author`, `coauthor`, `editor`, `name`, `surname`, etc.) to prevent placeholder-pattern false-positives.
- Behavioral-only `2f3bb1b` — fixed stale plan reference in `inference-first-checklist.md` (was pointing at non-existent late-March plan; now points at `experiment-design-principles.md`).

All shipped to all 8 targets (workflow main + applied-micro + behavioral, plus downstream va_consolidated, tx_peer_effects_local, bdm_bic, csac, csac2025).

### Branch hygiene

- `docs-v0.1.0` (Phase 1) merged to main; deleted local + remote.
- `docs-v0.1.0-phase2` (Phase 2a + 2b) merged to main; cherry-picked to applied-micro and behavioral; deleted local + remote.
- `docs-v0.1.0-phase2c` (current) holds Phase 2c-i; Phase 2c-ii (overlay-specific docs) coming next.

## Hook incidents in this session (useful as case studies)

- **Multiple primary-source-first false-positive trips on illustrative citations** ("Roth and List (2022)", "Author and Author (2022)", "Methodology (2025)"). Fixed in some cases by escape-hatch comments; in others by `NEVER_SURNAMES` expansion (role-words); in others by restructuring prose to avoid comma-adjacent surnames.
- **Hook caught Claude making framing claims about Nygard 2011** when describing ADR origins. Reverted to a generic adr.github.io community-site link, no specific authorship/chronology claim.
- **Hook caught Claude making framing claims about behavioral inference-first-checklist sources** without having read the cited papers. Resolution: docs reference the rule files (`experiment-design-principles.md`) which already carry the in-line attributions, rather than re-stating what the cited papers say. Meta-claims about the workflow's own attribution chain don't trigger the hook (they're not fresh framing claims about paper content).

## Pending decisions

- User to review Phase 2c-i (`docs-v0.1.0-phase2c@d315dac`) before Phase 2c-ii.
- Phase 2c-ii (overlay-specific docs `applied-micro.md` and `behavioral.md`) requires reading the actual overlay rule + reference files first; will not be written from memory.

## Reference

- Plan doc: `quality_reports/plans/2026-04-28_public-release-docs-plan.md` (untracked — working-tree journal artifact, per earlier decision that release/docs-strategy plans don't ship publicly).
- Predecessor session log: `2026-04-28_derive-dont-guess-shipped-and-docs-planning.md` (untracked).


---
**Context compaction (auto) at 21:54**
Check git log and quality_reports/plans/ for current state.
