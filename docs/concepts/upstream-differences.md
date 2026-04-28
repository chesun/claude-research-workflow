# What this fork adds vs upstream

This page is the audit trail for the workflow's distinctive contributions. A forker comparing this repo against the upstream chain can use this page to decide whether the additions are useful for them.

---

## Lineage

Three repos in the chain:

1. **`pedrohcgs/claude-code-my-workflow`** — Pedro Sant'Anna's original. Targeted lecture and slide production.
2. **`hugosantanna/clo-author`** — Hugo Sant'Anna's adaptation, retargeted toward academic writing.
3. **`chesun/claude-research-workflow`** *(this fork)* — research-paper production, with paradigm-specific overlays for applied micro and behavioral economics, plus the four-rule epistemic stack.

Each upstream is properly credited in [`../../LICENSE`](../../LICENSE) (dual copyright with Pedro's original work) and [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md) (fork-attribution boilerplate).

---

## What this fork *adds*

Twelve categories of new content. Each one is something forkers get when they fork this repo that they would not get from either upstream.

### 1. Four-rule epistemic stack

The most distinctive contribution. Four rules that prevent four categories of fabrication: `no-assumptions.md` (user-side facts), `primary-source-first.md` (external papers, hook-enforced), `derive-don't-guess.md` (repo-internal facts), `adversarial-default.md` (compliance claims, ledger-backed). See [`epistemic-rules.md`](epistemic-rules.md) for depth.

### 2. Verification ledger

Markdown cache at `.claude/state/verification-ledger.md` that prevents the adversarial-default rule from causing re-check bloat. Each row keys on `(path, check, sha256[:12])`; subsequent checks on unchanged artifacts cite the cache and skip re-running. See [`verification-ledger.md`](verification-ledger.md).

### 3. Three-branch model with paradigm overlays

`main` is the universal trunk; `applied-micro` adds identification tooling (DiD/IV/RDD/synthetic-control diagnostics, balance tables, event studies); `behavioral` adds experimental tooling (inference-first 14-step checklist, formal theory, oTree, Qualtrics, pre-registration). The overlays maintain only their additions on top of main. See [`../getting-started/branch-model.md`](../getting-started/branch-model.md).

### 4. Quality scoring with deduction tables

Weighted aggregate score across components (literature, data, identification/design, code, paper, polish, replication). Gates: 80 (commit), 90 (PR), 95 + every component ≥ 80 (submission). Per-target deduction matrices that critics apply consistently. See [`quality-scoring.md`](quality-scoring.md).

### 5. Decision log (ADRs)

Substantive decisions live in `decisions/NNNN_slug.md` — append-only, immutable once `Decided`, supersession via new ADRs. The convention is borrowed from software-engineering practice; this fork applies it to research design choices (identification strategy, sample restrictions, experimental parameters).

### 6. Replication protocol

Five-phase protocol from inventory through AEA-deposit prep. Concrete tolerance thresholds (integers exact, point estimates < 0.01, SEs < 0.05, p-values same significance level, percentages < 0.1pp). The verifier in submission mode runs the full 6-check AEA audit against this protocol. See `.claude/rules/replication-protocol.md`.

### 7. Editor agent

Synthesizes referee reports into editorial decisions (Accept / Minor Revisions / Major Revisions / Reject). Calibrated by journal culture via `.claude/references/journal-profiles.md`.

### 8. Specialized critics

Beyond the universal worker–critic pairs, this fork adds:

- `tikz-reviewer` — devil's-advocate review of TikZ diagrams (label positioning, overlap, visual consistency).
- `methods-referee` and `domain-referee` — independent blind reviewers for peer-review simulation. Score reports synthesized by the editor agent.

### 9. Per-language code conventions

`stata-code-conventions.md`, `r-code-conventions.md`, `python-code-conventions.md` — each codifies hardcoded-path detection, seed discipline, package conventions, output formats, and language-specific pitfalls (TWFE diagnostics in R, `cap log close` discipline in Stata, virtualenv enforcement in Python).

### 10. Hooks beyond the upstreams

- **`primary-source-check`** (PreToolUse) + **`primary-source-audit`** (Stop) — citation-grounding enforcement with four-filter regex extractor (built-in blocklist, sentence-start filter, hyphenated-name decomposition, project allowlist). Includes the citation-style convention (two-coauthor "Author and Author (year)") and the role-words blocklist (author, coauthor, editor, etc.) to prevent false-positives.
- **`log-reminder`** (Stop) — hard-cap reminder every 10 responses to write to a session log; safety net for the incremental-logging rule.
- **`verify-reminder`** (PostToolUse) — prompts verification after edits to Edit/Write artifacts.
- **`context-monitor`** (PostToolUse) — usage warnings at 40 / 55 / 65 / 80 / 90%; writes a `pre-compact-state.json` snapshot at 90% as a fallback for [anthropics/claude-code#14111](https://github.com/anthropics/claude-code/issues/14111) (PreCompact silently bypasses on auto-compact when MCP servers are present). Output goes to `stderr` so the user actually sees it; `MAX_TOOL_CALLS=500` env-overridable, tuned for Opus 4.7 1M context.
- **`pre-compact`** + **`post-compact-restore`** — state preservation across context compaction.
- **`protect-files`** (PreToolUse) — guards against accidental writes to `settings.json`.

### 11. Session-logging discipline

Incremental rule (append a few lines whenever a design decision is made, the user corrects something, or the approach changes). Hard-cap reminder hook fires every 10 responses. Post-compact restoration via `SessionStart` hook reading the snapshot. Session logs survive context compaction.

### 12. Single-source-of-truth + working-paper-format rules

`single-source-of-truth.md` — paper as authoritative; talks/supplementary derive from it; SSOT chain documented; per-format slide counts.

`working-paper-format.md` — economics-specific LaTeX preamble standards. `biblatex` + `biber` (not `natbib`); `lmodern`; `microtype`; deduction tables that the writer-critic applies.

---

## What this fork *changes* (modifies upstream behavior)

Three behavior shifts that aren't strictly additions:

- **Anti-hedging enforcement in writer + writer-critic.** Banned-word lists ("interestingly", "it is worth noting", "arguably", "it is important to note", "needless to say") with concrete deductions in the writer-critic.
- **Severity gradient by phase.** Critics calibrate stance by phase (encouraging in Discovery, constructive in Strategy, strict in Execution, adversarial in Peer Review). Same issue gets different deductions depending on where in the pipeline it surfaces. See `quality.md` § "Severity gradient."
- **Three-strikes escalation routing for worker-critic pairs.** If a pair fails to converge after 3 rounds, the orchestrator escalates to a higher level (different critic, the user, or a different agent type). Prevents infinite loops where the worker can't satisfy the critic. See [`worker-critic-pairs.md`](worker-critic-pairs.md).

---

## What this fork *does not include*

Be honest about scope:

- **No code-execution sandbox / containerization.** Assumes the user runs scripts directly. If you want isolated execution, layer a container or Codespaces config on top.
- **No CI/CD integration for paper compilation.** Whether/how to wire LaTeX builds into GitHub Actions is left to the user's preference.
- **No web interface.** CLI-only, follows Claude Code's model.
- **No domain coverage outside empirical economics / social science.** The applied-micro and behavioral overlays are calibrated for that audience. Other empirical fields (epi, finance, marketing) might fork and re-target.
- **No commercial / paid-API integration assumptions.** The workflow uses Claude Code natively; no Anthropic API direct integration is assumed.

---

## Migration notes

For someone coming from `pedrohcgs/claude-code-my-workflow`:

- Rule and skill names have changed in some cases. Check `.claude/rules/` and `.claude/skills/` against your previous fork; the directory layout is similar but content differs.
- The decision log (`decisions/`) and session logs (`quality_reports/session_logs/`) are new conventions; you don't need to retrofit old work.
- The four-rule epistemic stack imposes more rigor than the upstream defaults. Expect more "the agent asked instead of guessing" interactions; that's intentional.

For someone coming from `hugosantanna/clo-author`:

- The folder layout is similar; the differences are in `.claude/` (more rules, more agents, hooks) and the addition of the overlay branches.
- The writer-critic's anti-hedging enforcement may flag prose patterns that worked in the original. Read `.claude/rules/working-paper-format.md` and the writer-critic agent.

---

## Cross-references

- [`../../README.md`](../../README.md) — short-form pitch with the same five contribution highlights
- [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md) — attribution chain template for your own forks
- [`epistemic-rules.md`](epistemic-rules.md) — depth on the four-rule stack
- [`verification-ledger.md`](verification-ledger.md) — depth on the ledger format
- [`worker-critic-pairs.md`](worker-critic-pairs.md) — depth on the adversarial-pairing model
- [`quality-scoring.md`](quality-scoring.md) — depth on the scoring rubric
