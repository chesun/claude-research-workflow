# Claude Code Research Workflow

> **Preview release (v0.1.0).** A fork-and-adapt foundation for AI-assisted empirical research — identification, analysis, manuscript, talks, peer review, and submission. Based on Pedro Sant'Anna's [claude-code-my-workflow](https://github.com/pedrohcgs/claude-code-my-workflow) and Hugo Sant'Anna's clo-author template, re-targeted from lecture/slide production to research-paper production.

**Last Updated:** 2026-04-28

You describe what you want — an identification strategy, a data analysis, a paper draft, a replication package, a conference talk — and Claude plans the approach, runs specialized agents, fixes issues, verifies quality, and presents results. Like a contractor who handles the job end-to-end.

> **Status:** v0.1.0 is a preview. The rule/skill/agent contracts may shift before v1.0.0. Pinning to a tagged release will give you a stable snapshot while the trunk evolves. See [CHANGELOG.md](CHANGELOG.md) for what's new and [CONTRIBUTING.md](CONTRIBUTING.md) for how to engage.

---

## Three branches, three surfaces

- **`main` (universal).** Paradigm-agnostic research template. 17 agents, 14 skills, ~18 rules. Everything a general empirical project needs: discovery, data engineering, analysis, writing, peer review, submission.
- **`applied-micro`** (overlay). Adds identification-strategy tooling for observational/administrative-data research: `strategist` + `strategist-critic` agents, `/strategize`, `/balance`, `/event-study` skills, `air-gapped-workflow` rule.
- **`behavioral`** (overlay). Adds experimental-economics and formal-theory tooling: `theorist`, `designer`, `otree-specialist`, `qualtrics-specialist` agents, `/theory`, `/design`, `/otree`, `/qualtrics`, `/preregister` skills, `experiment-design-principles` rule, experiments/theory folder trees.

Main is the trunk. The two overlays are thin diffs maintained on their own branches. Universal improvements land on main and flow to both overlays via rebase.

---

## What this fork adds (vs. upstream)

The original `pedrohcgs/claude-code-my-workflow` was a lecture/slide production template (source of much of the agent infrastructure and most context-management hooks). `hugosantanna/clo-author` adapted it for academic-writing production (source of the universal worker–critic agent set, most pipeline skills, and core workflow rules). This fork inherits both, adds five distinctive net-new contributions, and reorganizes the agent set into paradigm-specific overlay branches:

1. **Four-rule epistemic stack** (net-new — none of these rules exist in either upstream):
   - **`no-assumptions.md`** — don't guess about user-side facts. Ask, leave out, or explicitly disclose.
   - **`primary-source-first.md`** — don't make framing claims about external papers without reading them. Hook-enforced (PreToolUse + Stop audit, both net-new in this fork).
   - **`derive-dont-guess.md`** — don't fabricate facts the repo encodes (filepaths, vars, macros). Cite source `file:line`.
   - **`adversarial-default.md`** — don't claim compliance without evidence. Backed by the verification ledger.
2. **Verification ledger** (net-new). `.claude/state/verification-ledger.md` caches `(path, check, sha256[:12])` triples so adversarial-default's "demand evidence" doesn't cause re-check bloat.
3. **Behavioral overlay's design rules with academic provenance** (net-new). The 13 design principles (`.claude/rules/experiment-design-principles.md`) and 14-step inference-first checklist (`.claude/references/inference-first-checklist.md`) carry in-line attributions to the experimental-economics literature.
4. **Decision log (ADRs)** (net-new rule). Substantive decisions live in `decisions/NNNN_slug.md`, append-only, supersession via new ADRs. Convention codified in net-new `decision-log.md`.
5. **Three-branch reorganization with paradigm overlays.** `main` is the universal trunk; `applied-micro` and `behavioral` are thin overlay branches with paradigm-specific agents and skills. Hugo's `clo-author` had `strategist` + `theorist` on a single main; this fork moves them onto the relevant overlays so forkers see only what's relevant to their paradigm.

For the verified file-by-file provenance — what's net-new, what's inherited from Pedro, what's inherited from Hugo, what's inherited and substantively modified — see [`docs/concepts/upstream-differences.md`](docs/concepts/upstream-differences.md).

---

## Where this fits in your research process

**Treat Claude as a capable first- or second-year graduate student RA** — technically proficient (writes Stata / R / Python that runs, formats LaTeX, drafts paper sections, debugs) but with limited subject-matter expertise on cutting-edge work. The four-rule epistemic stack and the worker–critic infrastructure catch *mechanical* defects (fabricated paths, ungrounded citations, unverified compliance). They cannot catch *substantive* defects (a misframed contribution, a misunderstood literature, a confounded mechanism). Those remain yours.

The asymmetry across overlays is real: **applied-micro work leans more on the workflow** (settled methodology, codified diagnostics) while **behavioral work involving novel mechanisms or theories needs heavier human review** (every textbook design pattern can be wrong for *your* specific question). Subject-matter expertise and literature knowledge are irreplaceable; quality control is your job; the workflow is leverage.

Read [`docs/concepts/appropriate-use.md`](docs/concepts/appropriate-use.md) before using this on real research. It's the most important page in the docs.

---

## Documentation

The repo root README (this file) is the short-form pitch. Depth lives under [`docs/`](docs/):

- [`docs/README.md`](docs/README.md) — nav hub with reading paths for new users, forkers, and contributors
- [`docs/getting-started/`](docs/getting-started/) — installation, prerequisites (with curated learning resources), branch-picker
- [`docs/concepts/`](docs/concepts/) — the four-rule epistemic stack, where Claude fits in research, more depth coming in v0.2.x
- [`docs/reference/`](docs/reference/) — glossary; full skill / agent / rule / hook catalogues coming in v0.2.x
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — issues, PRs, fork policy
- [`CHANGELOG.md`](CHANGELOG.md) — what's in `v0.1.0`, what's planned

---

## Quick Start (5 minutes)

### 1. Fork & Clone

```bash
# Fork this repo on GitHub (click "Fork" on the repo page), then:
git clone https://github.com/YOUR_USERNAME/claude-research-workflow.git my-project
cd my-project
```

### 2. Pick your branch

Stay on `main` for general empirical work, or:

```bash
git checkout applied-micro      # identification-strategy research
git checkout behavioral         # experimental/theoretical research
```

### 3. Start Claude Code and adapt

```bash
claude
```

Paste a starter prompt like:

> I am starting work on **[PROJECT NAME]**. **[2–3 sentences on the project.]** Read `CLAUDE.md`, fill in my project name and institution, and enter plan mode to adapt the template for my project.

Claude reads the config, adapts placeholders, and enters contractor mode — planning, implementing, reviewing, verifying.

---

## How It Works

### Contractor Mode

You approve a plan. Claude takes over: implements, runs critics, fixes issues, re-verifies, and reports quality scores. The orchestrator manages the dependency graph: Discovery → Strategy/Design → Code → Writing → Peer Review → Submission, with parallel dispatch where phases are independent.

### Specialized Agents (worker + critic pairs)

Every creator has a paired critic. Critics never edit files — they score and report. Worker-critic pairs converge in at most 3 rounds before escalating.

- `librarian` + `librarian-critic` — literature coverage and gaps
- `explorer` + `explorer-critic` — data feasibility and fit
- `data-engineer` + `coder-critic` — data pipeline quality
- `coder` + `coder-critic` — analysis code (Stata / R / Python)
- `writer` + `writer-critic` — manuscript drafting and polish
- `storyteller` + `storyteller-critic` — talks (narrative + visual quality)
- `tikz-reviewer` — merciless TikZ diagram audit
- `domain-referee` + `methods-referee` — simulated peer review
- `editor` — synthesizes referee reports into an editorial decision
- `orchestrator` — dispatches agents, manages escalation, tracks scores
- `verifier` — LaTeX compile, script execution, AEA replication audit

Overlays add: `strategist` (applied), `designer`/`theorist`/`otree-specialist`/`qualtrics-specialist` (behavioral).

### Quality Gates

Weighted aggregate score across components (literature, data, identification/design, code, paper, polish, replication). Thresholds:

- **80** — commit gate
- **90** — PR gate
- **95** — submission gate (plus every component ≥ 80)

See `.claude/rules/quality.md` for the full rubric and per-target deduction tables.

### Verification Ledger

Critic agents demand positive evidence for every compliance claim — a `grep` result, a diagnostic output, a test pass, a hash match. Results cache in `.claude/state/verification-ledger.md` (one row per `(path, check, sha256[:12])`); subsequent checks on unchanged files cite the cache and skip the re-run. File-hash mismatch or convention-rule modification triggers re-run automatically. Net effect: adversarial verification without re-check bloat.

### Primary-Source-First (hook-enforced)

Load-bearing files (decisions, analysis memos, session logs, plans, reviews) cannot cite a paper unless reading notes for that paper exist in `master_supporting_docs/literature/reading_notes/` AND were opened in the current session. The `primary-source-check` PreToolUse hook and `primary-source-audit` Stop hook enforce this deterministically. Escape hatch: `<!-- primary-source-ok: stem -->` in the delta. Two-coauthor papers are rendered "Author and Author (year)" — never comma-separated, never with `&`.

### Decision Log (ADRs)

Substantive decisions live in `decisions/NNNN_slug.md` — append-only, immutable once Decided, supersession via new ADRs. Analysis docs hold reasoning; ADRs hold the record.

### Context Survival

Pre-compact hook saves state to disk. Session logs capture incremental progress. ADRs preserve decisions. A new session can pick up from `CLAUDE.md` + most recent plan + `git log` and know where it is. The `context-monitor` PostToolUse hook also writes a state snapshot at 90% context as a fallback for when Claude Code's PreCompact silently bypasses (a known interaction with MCP servers).

---

## What's Included

### Agents (`.claude/agents/` — 17 universal)

Creators: librarian, explorer, data-engineer, coder, writer, storyteller
Critics: librarian-critic, explorer-critic, coder-critic, writer-critic, storyteller-critic, tikz-reviewer
Peer review: domain-referee, methods-referee, editor
Infrastructure: orchestrator, verifier

Overlays add their own paradigm-specific agents.

### Skills (`.claude/skills/` — 14 universal)

Pipeline: `/new-project`, `/discover`, `/analyze`, `/write`, `/review`, `/revise`, `/talk`, `/submit`
Utilities: `/commit`, `/context-status`, `/learn`, `/challenge`, `/deep-audit`, `/tools`

`/tools` is a multi-subcommand router (compile, validate-bib, journal, deploy, learn, upgrade).

### Rules (`.claude/rules/` — 25 universal)

- **Epistemic stack** ("don't fabricate" guards): `no-assumptions`, `primary-source-first`, `derive-dont-guess`, `adversarial-default`
- **Workflow:** agents, workflow, quality, logging, revision
- **Writing:** working-paper-format, figures, tables, tikz-visual-quality, single-source-of-truth, replication-protocol, verification-protocol
- **Code:** stata-code-conventions, r-code-conventions, python-code-conventions
- **Discipline:** decision-log, todo-tracking, output-length, meta-governance
- **Sandbox:** exploration-folder-protocol, exploration-fast-track

### Hooks (`.claude/hooks/` — 11 scripts)

- `primary-source-check` (PreToolUse) + `primary-source-audit` (Stop) — citation-grounding enforcement (Author-Year regex with sentence-start filter, hyphenated-name decomposition, project-allowlist; escape-hatch comments for illustrative citations)
- `log-reminder` (Stop) — hard-cap reminder to write session logs every 10 responses
- `verify-reminder` (PostToolUse) — prompts verification after edits
- `context-monitor` (PostToolUse) — usage warnings at 40/55/65/80/90%; writes pre-compact-state.json snapshot at 90% as fallback for the MCP-induced PreCompact bypass
- `pre-compact` + `post-compact-restore` — state preservation across context compaction
- `protect-files` (PreToolUse) — guards against accidental writes to sensitive files (settings.json, etc.)

---

## Prerequisites

- **Claude Code CLI** (see [anthropic.com/claude/code](https://www.anthropic.com/claude/code))
- **LaTeX distribution** (MacTeX, TeX Live, MiKTeX) with `pdflatex` + `biber`
- **Primary analysis language** (Stata 17, R ≥ 4.0, or Python ≥ 3.10)
- **Ghostscript** (optional — for PDF chunking fallback; see `.claude/references/pdf-chunking.md`)

Optional per overlay:

- `applied-micro`: Stata packages `reghdfe`, `ivreghdfe`, `estout`, `did_multiplegt`, `csdid` (as relevant)
- `behavioral`: oTree 5.x/6.x, Qualtrics account, R for `did`/`fixest`/power simulations

---

## Adapting for Your Field

1. Edit `CLAUDE.md` — project name, institution, language, LaTeX engine.
2. Populate `.claude/state/primary_source_surnames.txt` with authors you cite frequently (reduces false positives from the primary-source hook).
3. Drop relevant reference material into `master_supporting_docs/` (field-specific style guides, journal notes).
4. If your field is well-served by an overlay, check out the overlay branch. Otherwise keep `main` and customize as needed.

---

## Origin & Credits

- Foundation: Pedro Sant'Anna, [`pedrohcgs/claude-code-my-workflow`](https://github.com/pedrohcgs/claude-code-my-workflow) — originally a lecture/slide production template.
- Research-adaptation base: Hugo Sant'Anna, [`hugosantanna/clo-author`](https://github.com/hugosantanna/clo-author).
- This fork: reoriented to research-paper production with paradigm-specific overlays for applied micro and behavioral/experimental economics.

---

## License

MIT (see `LICENSE`).
