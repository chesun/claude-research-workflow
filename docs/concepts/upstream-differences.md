# What this fork adds vs upstream

This page is the audit trail for this fork's distinctive contributions. The numbers below are verified against actual upstream files (`pedrohcgs/claude-code-my-workflow@main` and `hugosantanna/clo-author@main` as of v0.1.0); claims are scoped to "file present / file modified / file new" rather than "what the file does," because the latter requires reading each upstream file in depth.

A forker comparing this repo against the chain can use this page to decide whether the additions are useful for them.

---

## Lineage

Three repos in the chain:

1. **`pedrohcgs/claude-code-my-workflow`** — Pedro Sant'Anna's original. Targeted lecture and slide production. Source of much of the agent infrastructure (tikz-reviewer, editor, peer-review referees, verifier) and most of the context-management hooks (context-monitor, log-reminder, pre-compact, post-compact-restore, verify-reminder, notify).
2. **`hugosantanna/clo-author`** — Hugo Sant'Anna's adaptation, retargeted from lecture/slide to academic-writing production. Source of the universal worker–critic agent set (librarian / explorer / data-engineer / coder / writer / storyteller, each with paired critic) plus the strategist + theorist creator-critic pairs, plus most of the universal-trunk skills (analyze, discover, new-project, review, revise, submit, talk, tools, write), plus core workflow rules (agents, workflow, quality, logging, revision, working-paper-format).
3. **`chesun/claude-research-workflow`** *(this fork)* — research-paper production with explicit paradigm-specific overlays (applied-micro, behavioral) split off from the universal trunk, plus the four-rule epistemic stack and verification ledger.

Each upstream is properly credited in [`../../LICENSE`](../../LICENSE) (dual copyright with Pedro's original work) and [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md) (fork-attribution boilerplate).

---

## What's truly net-new in this fork

These are files present in this fork that exist in **neither** Pedro's main nor Hugo's main.

### Rules (11 net-new)

The four-rule epistemic stack and seven additional rules:

| Rule | Purpose |
|---|---|
| `adversarial-default.md` | Burden-of-proof inversion for compliance claims; six per-domain checklists; backed by the verification ledger |
| `derive-dont-guess.md` | Don't fabricate facts the repo encodes; per-entity-type lookup table; cite source `file:line` |
| `no-assumptions.md` | Don't guess about user-side facts; ask, leave out, or explicitly disclose |
| `primary-source-first.md` | Don't make framing claims about external papers without reading them; hook-enforced; citation-style convention |
| `decision-log.md` | ADR convention for substantive design decisions in `decisions/NNNN_slug.md` |
| `todo-tracking.md` | Project-root `TODO.md` conventions |
| `output-length.md` | Responses > 15 lines write to a markdown file rather than printing inline |
| `figures.md` | Publication-quality figure standards |
| `tables.md` | Booktabs-based table standards |
| `python-code-conventions.md` | Python-specific reproducibility conventions (Pedro has r-code-conventions; this fork adds Python and Stata) |
| `stata-code-conventions.md` | Stata-specific reproducibility conventions |

### Hooks (4 net-new files)

The primary-source-first hook set:

| Hook file | Purpose |
|---|---|
| `primary-source-check.py` | PreToolUse hook blocking edits citing un-read papers |
| `primary-source-audit.py` | Stop hook auditing conversation prose for the same |
| `primary_source_lib.py` | Shared library with the four-filter regex extractor (built-in blocklist, sentence-start filter, hyphenated-name decomposition, project allowlist) |
| `test_primary_source_lib.py` | 27 regression tests for the extractor |

### Skills (1 net-new)

| Skill | Purpose |
|---|---|
| `/challenge` | Devil's-advocate review across modes (`--paper`, `--identification`, `--design`, `--theory`, `--fresh`) |

### Verification ledger

`.claude/state/verification-ledger.md` format and the file-hash-keyed lookup protocol that backs the `adversarial-default` rule. Net-new: no analogous mechanism in either upstream.

### Other top-level

- `decisions/` directory and ADR template (paired with the new `decision-log.md` rule).
- `master_supporting_docs/literature/{papers,reading_notes}/` directory structure (paired with the new `primary-source-first.md` rule and the gitignored-PDF policy in this fork).

---

## What's inherited and substantively modified

These files exist in one or both upstreams; this fork's versions have been substantially edited (or the file is the same name but the content has been substantively rewritten — git shows non-trivial diffs against the upstream version).

### Agents — inherited (workflow may have modified content for tone, scope, or to integrate with new rules)

From Hugo's main: `coder`, `coder-critic`, `data-engineer`, `explorer`, `explorer-critic`, `librarian`, `librarian-critic`, `orchestrator`, `storyteller`, `storyteller-critic`, `writer`, `writer-critic`. The applied-micro overlay's `strategist` + `strategist-critic` and the behavioral overlay's `theorist` + `theorist-critic` also exist in Hugo's universal main (this fork moves them onto the paradigm-specific overlays).

From Pedro's main: `tikz-reviewer`. Also: `editor`, `methods-referee`, `domain-referee`, `verifier` exist in **both** upstreams; this fork inherits them (likely from Hugo, who already imported them from Pedro's lecture-template lineage).

### Hooks — inherited from Pedro (then modified here)

| Hook | Origin | Modifications in this fork (significant items) |
|---|---|---|
| `context-monitor.py` | Pedro | Output redirected to `stderr` (was stdout, invisible to user); fallback at 90% writes a `pre-compact-state.json` snapshot to work around [`anthropics/claude-code#14111`](https://github.com/anthropics/claude-code/issues/14111) (PreCompact bypass under MCP-server load); `MAX_TOOL_CALLS=500` env-overridable, tuned for Opus 4.7 1M-context. |
| `log-reminder.py` | Pedro | Inherited; behavior verified. |
| `notify.sh` | Pedro | Inherited; macOS notifications. |
| `pre-compact.py` | Pedro + Hugo | Inherited; state-capture for context survival. |
| `post-compact-restore.py` | Pedro + Hugo | Inherited; reads pre-compact-state.json on session start. |
| `verify-reminder.py` | Pedro | Inherited; prompts verification after edits. |
| `protect-files.sh` | Hugo | Inherited; guards against accidental edits to protected files (settings.json). |

### Skills — inherited

From Pedro's main: `commit`, `context-status`, `deep-audit`, `learn` (4 skills).

From Hugo's main: `analyze`, `discover`, `new-project`, `review`, `revise`, `submit`, `talk`, `tools`, `write` (9 skills).

This fork's skill catalogue is essentially the union of those plus `/challenge` (net-new).

### Rules — inherited

From Pedro's main: `exploration-fast-track`, `exploration-folder-protocol`, `r-code-conventions`, `replication-protocol`, `single-source-of-truth`, `tikz-visual-quality`, `verification-protocol`.

From Hugo's main: `agents`, `logging`, `quality`, `revision`, `workflow`, `working-paper-format`.

From **both**: `meta-governance`.

This fork inherits the union of these plus the 11 net-new rules listed above.

---

## Reorganization (not addition, but worth noting)

Beyond net-new content, this fork **reorganizes** what's inherited:

### Three-branch model with paradigm overlays

Hugo's `clo-author` has the strategist + theorist creator-critic pairs on a single main branch. This fork separates them onto paradigm-specific overlay branches (`applied-micro` for strategist, `behavioral` for designer + theorist + otree-specialist + qualtrics-specialist). The `main` branch is the universal trunk; overlays are thin diffs.

Practical implication: forkers checkout the overlay matching their work; they get only the agents/skills/rules relevant to their paradigm rather than all of them.

### Behavior shifts in inherited critics

- **Anti-hedging enforcement** in writer + writer-critic (banned-word lists with deductions). The writer agent inherited from Hugo; the anti-hedging emphasis was added.
- **Universal anti-AI-prose rule** (`.claude/rules/anti-ai-prose.md`) — catalog of ~35 patterns across 6 categories (lexical, syntactic, structural, rhetorical, content, communication) with severity tiers and voice profiles (academic / slide / correspondence / blog / docs). Paired with the universal `/humanize [path]` skill, deduction tables in writer-critic and storyteller-critic, and references from the writer + storyteller agents. Hugo's writer had a paper-only inline humanizer section; this fork promotes the catalog to a rule, applies it to slides + correspondence + docs + blog, and adds structural / burstiness patterns the original didn't cover.
- **Severity gradient by phase** in the orchestrator and critics (encouraging in Discovery, adversarial in Peer Review, with deduction-by-phase tables in `quality.md`).
- **Three-strikes escalation routing** for worker-critic pairs (configured in `agents.md`, applied by the orchestrator).

These are non-trivial behavior changes layered onto inherited agent definitions — not net-new agents, but substantive enough to mention.

### Hook + rule integration

The new `primary-source-first` hooks integrate with the new `primary-source-first.md` rule and the new `master_supporting_docs/literature/` directory structure. Same for `adversarial-default` rule + verification ledger. These are integrations between net-new components rather than additions on top of inherited ones.

---

## What this fork *does not include*

Be honest about scope:

- **No code-execution sandbox / containerization.** Assumes the user runs scripts directly.
- **No CI/CD integration for paper compilation.** Whether/how to wire LaTeX builds into GitHub Actions is the user's call.
- **No web interface.** CLI-only.
- **No domain coverage outside empirical economics / social science.** The applied-micro and behavioral overlays are calibrated for that audience.
- **No commercial / paid-API integration assumptions.**

---

## Migration notes

For someone coming from `pedrohcgs/claude-code-my-workflow`:

- The lecture / slide / Quarto-specific skills (`create-lecture`, `slide-excellence`, `qa-quarto`, `translate-to-quarto`, `pedagogy-review`, `seven-pass-review`, `audit-reproducibility`, `permission-check`, `verify-claims`, `respond-to-referees`, etc.) are not present in this fork — they were dropped in Hugo's research re-target, and this fork didn't re-add them.
- The agent set is mostly Hugo's universal worker-critic pairs; Pedro's lecture-specific agents (`beamer-translator`, `pedagogy-reviewer`, `quarto-critic`, `quarto-fixer`, `r-reviewer`, `slide-auditor`, `domain-reviewer`, `proofreader`, `claim-verifier`) are not present.
- The four-rule epistemic stack is the major net-new rule set; expect more "the agent asked instead of guessing" interactions.

For someone coming from `hugosantanna/clo-author`:

- The agent / skill catalogue is similar; the differences are the four net-new rules, the new primary-source-first hooks, the verification ledger, the strategist / theorist split onto overlay branches, and the new ADR + replication-protocol + per-language code conventions.
- The writer-critic's anti-hedging deductions may flag prose patterns that worked in Hugo's version.

---

## Cross-references

- [`../../README.md`](../../README.md) — short-form pitch
- [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md) — attribution chain template for your own forks
- [`epistemic-rules.md`](epistemic-rules.md) — depth on the four-rule stack (the net-new contribution)
- [`verification-ledger.md`](verification-ledger.md) — depth on the ledger format (also net-new)
- [`worker-critic-pairs.md`](worker-critic-pairs.md) — the adversarial-pairing model inherited from Hugo and behavior-modified here
- [`quality-scoring.md`](quality-scoring.md) — the scoring rubric, rules-from-multiple-upstreams plus deductions added here
