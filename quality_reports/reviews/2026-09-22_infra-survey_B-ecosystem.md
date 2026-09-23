# Infra Survey B — Ecosystem enumeration
**Date:** 2026-09-22
**Reviewer:** survey agent B (general-purpose)
**Target:** psantanna.com guide ecosystem section + adoptable econ tools
**Status:** Active
**Score:** n/a (survey)

## Scope note / key finding

The task framed an "OpenEcon / hanlulong family" as if it lived in the psantanna guide. It does **not**. The guide's Section 6 ("The Ecosystem: What Others Have Built") never mentions `hanlulong` or `OpenEcon`, and the guide's Stata MCP is **SepineTam/stata-mcp**, a *different* repo from **hanlulong/stata-mcp**. The OpenEcon/hanlulong family is real and active but is an *external* econ-tool cluster the caller wants assessed alongside the guide. This report enumerates both: **Part A** = everything in the guide's ecosystem section; **Part B** = the OpenEcon/hanlulong family (external).

---

## Part A — Guide Section 6 ecosystem enumeration

Source: `https://psantanna.com/claude-code-my-workflow/workflow-guide.html#sec-ecosystem` (Section 6, HTML lines 6589–6821).

### 6.1 clo-author — Paper-Centric Research Workflows
- **Repo:** https://github.com/hugosantanna/clo-author — Author: Hugo Sant'Anna (UAB). A fork of the guide's own template.
- Reorients workflow from slides to papers; `Paper/main.tex` = single source of truth. Adversarial worker-critic agent pairs w/ separation of powers. Current release **v26.05 (2026-05-10)**: "MAS v2" multi-agent system, skill-centric restructure (**13 skills + 18 agents**), self-contained HTML dashboard (no server). Adds weighted aggregate scoring (submission gate ≥95, each component ≥80), simulated blind peer review (2 referees + editor), **humanizer pass stripping 24 AI writing patterns in 4 categories**, domain-profile calibration, full submission/R&R pipeline.
- **This is the direct ancestor lineage of the current repo.**

### 6.2 claudeblattman — Workflows for Non-Technical Academics
- **Site:** https://claudeblattman.com — **Repo:** https://github.com/chrisblattman/claudeblattman — Author: Chris Blattman (U. Chicago).
- Non-coder academic workflows: morning briefings, email triage (14 phases), proposal writing w/ **voice packs**, fresh-context critique, agent debates, self-improving "tips pipeline", depth calibration (Light/Standard/Deep), graceful degradation. **Writing-style rules:** numbers over adjectives, topic sentences make claims, no throat-clearing, hedge only with a reason or number.

### 6.3 Xu & Yang (2026) — Reproducibility as Architecture (PAPER, not a tool)
- Yiqing Xu (Stanford) & Leo Yang Yang (HKBU), "Scaling Reproducibility: An AI-Assisted Workflow for Large-Scale Reanalysis," 2026. 100% reproducibility across 92 papers / 215 specs (conditional on accessible data+code), <4 min/paper. Principles: template-executor separation, three-layer architecture, structured intermediate files, version-controlled knowledge accumulation, adaptation between-runs-not-during.

### 6.4 MixtapeTools — The Rhetoric of Decks
- **Repo:** https://github.com/scunning1975/MixtapeTools — Author: Scott Cunningham (Baylor; *Causal Inference: The Mixtape*).
- "Referee 2" 5-audit adversarial protocol; multi-agent deck-generation prompt (builder → rhetoric reviewer → graphics specialist); example Beamer decks + `theme_rhetoric()` ggplot2 themes; zero-warning compile standard.

### 6.5 AEA Data Editor Template
- **Site:** https://social-science-data-editors.github.io/template_README — **Repo:** https://github.com/social-science-data-editors/template_README — Maintainer: Lars Vilhuber (Cornell) + REStat/EJ/CJE editors.
- Compliance-standard replication-package README used at 5+ econ journals. Markdown/Word/LaTeX/PDF.

### 6.6 autoresearch — Constraint-Based Autonomous Research
- **Repo:** https://github.com/karpathy/autoresearch — Author: Andrej Karpathy.
- Autonomous ML-experiment agent. Key transferable idea: `program.md` as a "constitutional document" (what the agent CAN / CANNOT modify + success metric); structured TSV results logging; time-budgeted iterations. Guide gives a Monte-Carlo `program.md` adaptation example.

### 6.7 stata-mcp (SepineTam) — MCP server for Stata execution
- **Repo:** https://github.com/SepineTam/stata-mcp — Author: SepineTam. Guide says 171+ stars, 91 releases, v1.17.3 (May 2026). (Now also `SepineTam/mcp-for-stata`.)
- Executes Stata `.do` via command-guarded MCP interface (refuses `!`/`shell`/`erase`), RAM monitor, pairs w/ Stata Language Server. **Install:** `claude mcp add stata-mcp --scope user -- uvx stata-mcp` — **requires `uv` + a local Stata install.**

### 6.8 ClaudeCodeTools — The Editor Persona
- **Repo:** https://github.com/aspi6246/ClaudeCodeTools.
- "The Editor" persona runs **seven sequential audit passes**; R&R tracking mode; blunt specific feedback; "So What" 5-question litmus test.

### 6.9 Anthropic-shipped Apr–May 2026 utilities (first-party; no fork needed)
- `/team-onboarding`, `/autofix-pr`, `/powerup` (interactive lessons), **Ultraplan** (cloud plan draft/review), `/loop` self-pacing (alias `/proactive`), **`/goal <condition>`** (keep-working-until-X; v2.1.139), **`claude agents`** dashboard for background sessions, `/fewer-permission-prompts`. These are native primitives that fill gaps the template intentionally leaves.

### 6.10 Community adoption (not a tool)
- 15+ research groups (Mar 2026 survey); repo passed 2,900 forks / 1,500 stars (2026-08-24). Econ/energy/teaching adaptations listed.

---

## Part B — OpenEcon / hanlulong family (external to the guide)

Maintainer: **Lu Han (`hanlulong`) / the OpenEcon team**. Curated hub: https://github.com/hanlulong/awesome-ai-for-economists. Site: https://openecon.ai.

| Tool | URL | What it does | Stars | License | Key deps / flags |
|---|---|---|---|---|---|
| **econ-writing-skill** | github.com/hanlulong/econ-writing-skill | Skill giving agents econ-paper writing knowledge; synthesizes 50+ guides (Cochrane, McCloskey, Shapiro, Head, Bellemare, Goldin, Kremer, Schwabish); section formulas; simulated 3-reviewer feedback; **explicit anti-AI-prose rules** | 614 | MIT | **None.** Pure skill file. Claude Code + Codex. Cross-platform. No service. |
| **econ-paper-review-skill** | github.com/hanlulong/econ-paper-review-skill | AI referee report: verified comments, edit notes, revision plan (no rewrite). `/econ-review` (CC), `$econ-review` (Codex) | 23 | **PolyForm Noncommercial 1.0.0** | Python 3.10+ venv/pip; optional Poppler for PDF; local web "Review Desk" viewer. Cross-platform. |
| **econ-slides-skill** | github.com/hanlulong/econ-slides-skill | Paper → Beamer deck + timed speaker/discussant scripts; compile + visual audit | 16 | MIT | **Requires TeX + XeLaTeX** (TeX Live/MacTeX/MiKTeX) + PyMuPDF + Python 3.10+. CC + Codex. |
| **openecon-data** | github.com/hanlulong/openecon-data · openecon.ai | MCP server: 330K economic indicators (FRED, World Bank, IMF, Eurostat, OECD, BIS, UN Comtrade, +) in natural language | 78 | **AGPL-3.0** | **MCP server** (SSE at data.openecon.ai/mcp) + **requires OpenRouter API key (paid LLM)**; self-host = Python/Node/Redis/FastAPI/React; web app 20 free queries then signup. |
| **hanlulong/stata-mcp** | github.com/hanlulong/stata-mcp | Stata via MCP for VS Code/Cursor/Copilot/CC/Codex/Cline/Antigravity; in-editor output + syntax highlighting. **Distinct from SepineTam's.** | 500 | MIT | **MCP server + requires Stata 17+ (licensed) + `uv`.** |
| **econ-auto-research** | github.com/hanlulong/econ-auto-research | Economist-directed full-pipeline pipeline (question→working paper) w/ self-refereeing. **Vision stage — "no code here yet."** | 29 | MIT | Would chain the other 4 OpenEcon tools. Vaporware today. |
| **AI-research-setup** | github.com/hanlulong/AI-research-setup | Setup guide for CC + Codex for econ research (reference doc) | — | — | Reference only. |
| **overleaf-sync-now** | github.com/hanlulong/overleaf-sync-now | Keeps local LaTeX synced w/ Overleaf so agents don't edit stale papers | — | — | **Depends on Overleaf (service) + LaTeX.** |

---

## Per-tool integrate / adapt / skip pre-calls (downstream personal econ template)

Template context: strictly-personal, gates-not-nags, Claude-5-native-first, personal-scale, cross-platform (Win+Mac). User's current work machine has **no Stata, no LaTeX** (per MEMORY). Flags: process-nag, lab-scale, OS-locked, service-dependent, redundant-with-native-primitive.

| Tool | Pre-call | One-line reason |
|---|---|---|
| **econ-writing-skill** | **INTEGRATE** | Top pick: MIT, zero deps, cross-platform, no service; directly overlaps this template's anti-ai-prose/anti-hedging — adopt its 50-guide synthesis wholesale or merge into `/write`. |
| AEA Data Editor Template | **INTEGRATE** | Zero-dependency canonical README; template already targets AEA compliance — vendor the file. |
| econ-paper-review-skill | **ADAPT** | Borrow the referee checklist into existing referee agents; don't integrate wholesale — **PolyForm Noncommercial license** (fine for personal research, blocks any commercial use) + Python/local-server dep + redundant with template's domain/methods-referee. |
| MixtapeTools | **ADAPT** | Deck-rhetoric + `theme_rhetoric()` + Referee-2 audit are useful, no service dep; cherry-pick into `/talk` and dataviz rather than fork. |
| autoresearch (Karpathy) | **ADAPT pattern, SKIP repo** | `program.md` constraint doc is a clean fit for personal Monte-Carlo work; the repo itself is ML-training, not econ. |
| Anthropic Apr–May utilities | **USE natively** | `/goal`, `/loop`, `claude agents`, `/fewer-permission-prompts` are native Claude primitives — redundant to re-implement; several already surface as skills here. |
| clo-author | **SKIP (mine for patterns)** | It is the heavyweight 18-agent/13-skill ancestor this template deliberately simplified *away from*; adopting it re-adds the nag-scale machinery. Lift individual patterns only. |
| ClaudeCodeTools "Editor" | **SKIP / light ADAPT** | Seven-audit persona is largely redundant with the template's existing adversarial critics; borrow the "So What" 5-question test at most. |
| claudeblattman | **SKIP (borrow style rules)** | Morning-briefing/email-triage are exactly the process-nags and lab/PA-scale workflows to avoid; its concise writing-style rules are the only transferable bit. |
| econ-slides-skill | **SKIP** | Requires TeX+XeLaTeX (absent on user's current machine) and is redundant with the template's `/talk`/storyteller. |
| openecon-data | **SKIP (optional opt-in)** | **Service-dependent: running MCP server + paid OpenRouter API key + AGPL-3.0 copyleft.** Exactly the profile to avoid for a personal template; keep as an optional, clearly-flagged MCP if verified data lookup is ever needed. |
| hanlulong/stata-mcp & SepineTam/stata-mcp | **SKIP** | MCP server + **requires licensed local Stata** (user has none); OS/tooling-locked. Revisit only on a Stata-equipped Mac. |
| overleaf-sync-now | **SKIP** | Depends on Overleaf (service) + LaTeX; neither is in this user's mandated stack. |
| econ-auto-research | **SKIP (watch)** | Vaporware ("no code yet"); philosophically aligned with the template's orchestrator — monitor, don't adopt. |
| Xu & Yang (2026) | **n/a (paper)** | Conceptual reference; its principles are already embodied in the template's spec→plan / structured-files / `/learn` design. |

---

## Academic voice / writing-style / anti-AI-prose notes

- **econ-writing-skill (hanlulong)** is the most directly relevant external artifact: explicit anti-AI rules — "banned words, uniform sentence length, generic phrasing" — plus a 50+-guide synthesis (Cochrane, McCloskey, Shapiro's "Four Steps," Head's "Introduction Formula," Bellemare, Goldin, Kremer, Schwabish). This is a near-sibling of the template's own `anti-ai-prose.md` + humanizer, MIT-licensed and free to lift.
- **clo-author humanizer** strips **24 AI writing patterns across 4 categories** (structural tics, lexical tells, rhetorical patterns, formatting tells) — the lineage of the template's own humanizer/`/humanize`.
- **claudeblattman writing-style rules**: "numbers over adjectives, topic sentences make claims, no throat-clearing, hedge only with a reason or number" — echoes the template's anti-hedging rule; a tight, adoptable checklist.
- **MixtapeTools**: "Beauty is function — every visual element earns its presence" for decks/figures.
- **ClaudeCodeTools "Editor"**: blunt specificity ("This paragraph is incoherent," not "might benefit from clarity") as a voice model for self-critique.
