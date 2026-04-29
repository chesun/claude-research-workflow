# Changelog

All notable changes to this fork are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the version scheme follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html), with the caveat that under `0.x.y` the rule/skill/agent contracts may shift between minor versions. Once at `1.0.0`, contracts will be stable per semver.

---

## [v0.1.0] — 2026-04-28 (Preview)

First public release. The workflow has been tested internally on multiple research projects across applied micro and behavioral economics, and is now opened up for forking.

### Added

#### Four-rule epistemic stack
The workflow's "don't fabricate" guards. Each addresses a distinct failure mode of "filling in blanks":

- **`no-assumptions.md`** — don't guess about user-side facts (preferences, deadlines, target journal, infrastructure, role boundaries). Ask, leave out, or explicitly state the assumption with "Assuming X (let me know if otherwise)." Ported and expanded from the user's global `~/.claude/rules/no-assumptions.md` so public-release forks get it bundled.
- **`primary-source-first.md`** — don't make framing claims about external papers without reading them. Hook-enforced: PreToolUse blocks file edits citing un-read papers; Stop hook audits conversation prose for the same. Reading notes required at `master_supporting_docs/literature/reading_notes/`. Includes a citation-style convention (two-coauthor papers as "Author and Author (year)").
- **`derive-dont-guess.md`** — don't fabricate facts the repo encodes (filepaths, variable names, macros, output conventions, config values). Per-entity-type lookup table; cite source `file:line` for derived entities; "new convention" disclosure when no precedent exists. Triggered by an incident where Claude guessed dataset paths instead of reading `do/settings.do`.
- **`adversarial-default.md`** — don't claim compliance without evidence. Burden of proof is on the asserter. Verification results cache in `.claude/state/verification-ledger.md` (file-hash-keyed) so unchanged artifacts aren't re-checked. Six per-domain checklists (code: Stata/R/Python; data; design; identification; replication; bibliography). Triggered by an incident where Claude assumed inherited Stata code satisfied the no-hardcoded-paths convention.

#### Verification ledger
Markdown cache at `.claude/state/verification-ledger.md`. Each row: `path | check | verified_at | sha256[:12] | result | evidence`. Lookup protocol: file-hash match → cite cached PASS, no re-run. Stale invalidation triggers when convention rule modified or `/tools verify --force` invoked. Tracked in git for cross-session and cross-machine persistence.

#### Decision log (ADRs)
Substantive decisions live in `decisions/NNNN_slug.md`. Append-only; immutable once `Decided`; supersession via new ADRs. Referenced by number from session logs, plans, and other ADRs.

#### Replication protocol
5-phase protocol from inventory through AEA-deposit prep. Concrete tolerance thresholds (integers exact, point estimates < 0.01, SEs < 0.05, p-values same significance level, percentages < 0.1pp). Verifier in submission mode runs the full 6-check AEA audit against this protocol.

#### Code conventions
Per-language standards as standalone rules: `stata-code-conventions.md`, `r-code-conventions.md`, `python-code-conventions.md`. Cover hardcoded-path detection, seed discipline, package conventions, output formats, and language-specific pitfalls (e.g., TWFE diagnostics in R, `cap log close` discipline in Stata).

#### Single-source-of-truth rule
`single-source-of-truth.md` — paper is authoritative; talks and supplementary derive from it. SSOT chain documented; per-format slide counts (job market 40-50, seminar 25-35, short 10-15, lightning 3-5).

#### Working-paper-format rule
`working-paper-format.md` — economics-specific LaTeX preamble standards. `biblatex` + `biber` (not `natbib`); `lmodern`; `microtype`; UC Davis dissertation-friendly title page; deduction tables for the writer-critic.

#### Editor agent
Synthesizes referee reports into editorial decisions. Selects dispositions (Accept / Minor Revisions / Major Revisions / Reject) using journal-culture calibration from `.claude/references/journal-profiles.md`.

#### Specialized critics
- `tikz-reviewer` — devil's-advocate review of TikZ diagrams (label positioning, overlap, visual consistency).
- `methods-referee` and `domain-referee` — independent blind reviewers for peer-review simulation.

#### Hooks
- `primary-source-check` (PreToolUse) + `primary-source-audit` (Stop) — citation grounding.
- `log-reminder` (Stop) — hard-cap reminder every 10 responses.
- `verify-reminder` (PostToolUse) — prompts verification after edits.
- `context-monitor` (PostToolUse) — usage warnings at 40/55/65/80/90%; writes pre-compact-state.json snapshot at 90% as a fallback for [anthropics/claude-code#14111](https://github.com/anthropics/claude-code/issues/14111) (PreCompact silently bypasses on auto-compact when MCP servers are present). Warning output uses stderr so it actually reaches the user; the heuristic is `MAX_TOOL_CALLS=500` (env-overridable via `CONTEXT_MONITOR_MAX_TOOL_CALLS`), tuned for Opus 4.7 1M context.
- `pre-compact` + `post-compact-restore` — state preservation across context compaction.
- `protect-files` (PreToolUse) — guards against accidental writes to `settings.json`.

#### Three-branch model with paradigm overlays
- `main` (universal) — paradigm-agnostic research template. 17 agents, 14 skills, 25 rules.
- `applied-micro` (overlay) — adds `strategist` + `strategist-critic` agents, `/strategize`, `/balance`, `/event-study` skills, `air-gapped-workflow.md` rule.
- `behavioral` (overlay) — adds `designer`, `theorist`, `otree-specialist`, `qualtrics-specialist` agents, `/design`, `/theory`, `/otree`, `/qualtrics`, `/preregister` skills, `experiment-design-principles.md` rule (13 design principles with academic attributions), `inference-first-checklist.md` reference (14-step checklist), `experiments/` and `theory/` folder trees.

#### Quality scoring
Weighted aggregate score across components: literature 10%, data 10%, strategy/design 25%, code 15%, paper 25%, polish 10%, replication 5%. Gate thresholds: 80 (commit), 90 (PR), 95 + every component ≥ 80 (submission). Per-target deduction matrices in `quality.md`.

#### Critic-write architecture + reviews/plans lifecycle
Reframes the "critics never create" rule as a source-vs-report distinction. *Source artifacts* (`paper/`, `talks/`, `scripts/`, `do/`, `decisions/`, `theory/`, `experiments/designs/`, `figures/`, `tables/`, `references.bib`, `data/cleaned/`) remain read-only for critics. *Report artifacts* (`quality_reports/reviews/`) are write-encouraged so every critic invocation produces an audit trail.

All 13 critic-style agents (10 universal: `coder-critic`, `writer-critic`, `librarian-critic`, `explorer-critic`, `storyteller-critic`, `tikz-reviewer`, `domain-referee`, `methods-referee`, `verifier`, `editor`; plus `strategist-critic` on applied-micro and `designer-critic`, `theorist-critic` on behavioral) gained `Write` permission and a canonical save path:

```
quality_reports/reviews/YYYY-MM-DD_<target>_<critic>_review.md
```

Required header per review: `Date`, `Reviewer`, `Target`, `Score`, `Status: Active`, optional `Supersedes:`. Status values: `Active | Completed | Superseded by <path> | Archived`.

Lifecycle protocol prevents indefinite top-level growth in `quality_reports/reviews/` and `quality_reports/plans/`:

- **Supersession**: new review of the same target marks the prior `Status: Superseded by <new>`, `git mv` it to `archive/`, set `Supersedes:` in the new report, update `INDEX.md`.
- **Time-based archive**: `Status: Completed` + 90 days idle → move to `archive/`.
- **`INDEX.md` per folder**: lists `Active` items; critics consult before writing to avoid parallel duplicates.

Conventions documented in `quality_reports/reviews/README.md` and `quality_reports/plans/README.md`. Rule encoded in `.claude/rules/agents.md` § 2 + § 2a. Concepts page updated at `docs/concepts/worker-critic-pairs.md`.

#### Public documentation site
`docs/` ships with v0.1.0 as the long-form companion to `README.md`. 24 pages organized by audience:

- `docs/getting-started/` (7 pages) — prerequisites, installation, branch model, first-session walkthrough, plus portable applied-micro and behavioral overlay previews readable from any branch.
- `docs/concepts/` (7 pages) — appropriate-use ("capable-RA" analogy), epistemic-rules deep-dive, verification-ledger, worker-critic pairs, quality scoring, file-by-file upstream-differences diff vs `pedrohcgs/claude-code-my-workflow` and `hugosantanna/clo-author`.
- `docs/reference/` (6 pages) — catalogues of skills, agents, rules, hooks; glossary.
- `docs/customization/` (2 pages) — adapting `CLAUDE.md`, extending rules.
- `docs/faq.md`, `docs/contributing.md` — top-level lookup utilities.

### Acknowledgements

This fork descends from [`pedrohcgs/claude-code-my-workflow`](https://github.com/pedrohcgs/claude-code-my-workflow) (original lecture/slide template by Pedro Sant'Anna) and [`hugosantanna/clo-author`](https://github.com/hugosantanna/clo-author) (academic-writing adaptation by Hugo Sant'Anna). The research-paper re-target, the four-rule epistemic stack, the verification ledger, the three-branch overlay model, the quality scoring system, and the domain-specific tooling are added in this fork.

---

## [v0.1.1] — 2026-04-28

### Fixed

- **`NEVER_SURNAMES` blocklist expanded** with common book/series-title nouns (`methodology`, `handbook`, `encyclopedia`, `review`, `annual`, `bulletin`, `journal`, `volume`, `issue`, plus plurals). These were previously parsed as surnames when adjacent to a year (e.g., "Handbook of Experimental Methodology 2025" → false-positive citation `methodology_2025`). Same blocklist mechanism that catches seasons, months, and document-structure words. Updated regression tests in `.claude/hooks/test_primary_source_lib.py` cover all 9 added words.

## [Unreleased] — Planned for v0.1.2

- **Auto-archive sweep skill.** A `/tools archive-stale` subcommand to sweep `Status: Completed` reviews/plans older than 90 days into `archive/`. Currently the lifecycle rule documents the protocol but moves are manual.

[v0.1.0]: https://github.com/chesun/claude-research-workflow/releases/tag/v0.1.0
