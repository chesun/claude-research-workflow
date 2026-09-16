<!-- primary-source-ok: korinek_2025, kohler_zollikofer_einsiedler_hoyle_ash_2026, santanna_2026, long_2026, lastunen_2026, sargent_stachurski_2026, chen_2026 -->
# AI-for-economics research-workflow landscape and direction for this template

**Date:** 2026-09-16
**Author:** survey synthesis (two research agents + repo review), for the personal research template
**Status:** Advisory — no changes made; input for a "where next" decision

## Bottom line

The field moved while this template sat at Opus 4.8. The frontier upstream adopted the Claude 5 generation and a currency-enforcement discipline; the model family turned over completely; and the harness now makes first-class most of what this template hand-rolled. Two failure modes do not scale away with smarter models: confident fabrication (including invented citations) and irreversible-action risk. An economics-specific reproduction study says documentation completeness, not agent skill, is the binding constraint. So the highest-leverage direction is not more features — it is a modernize-and-simplify pass: keep the safety and citation gates, prune the process-nag hooks, and re-platform the orchestration onto native primitives.

## Where the upstreams and community are

- **Frontier upstream — Pedro Sant'Anna, `pedrohcgs/claude-code-my-workflow`.** Very active: v2.5.1 (Aug 2026), ~3,000 forks. Moved to the Claude 5 generation with model routing (Fable 5 as top tier) and added a "qualification ledger / backtest gate" that mechanically detects stale facts and model references. Watch this repo, not the direct parent, for where things go.
- **Direct parent — Hugo Sant'Anna, `hugosantanna/clo-author`.** Still up (this repo's worker-critic set, `/new-project`, 80/95 gates, journal profiles come from here) but visible activity slowed after May 2026 and shows no Claude 5 adoption.
- **Canonical reference — Anton Korinek, "AI Agents for Economic Research"** (NBER w34202, https://www.nber.org/papers/w34202) and his `genaiforecon` Substack. The build-your-own-agent playbook for economists.
- **Adjacent ecosystem — Hanlu Long / OpenEcon.** `awesome-ai-for-economists` list (https://github.com/hanlulong/awesome-ai-for-economists) plus drop-in Claude Code skills: a pre-referee review skill, a Stata MCP server, an auto-research pipeline, a data-query server. Adopt rather than rebuild.
- **Empirical evidence — Ash group (ETH), "Read the Paper, Write the Code"** (Apr 2026, https://arxiv.org/html/2604.21965v1). Best agent matched coefficient signs 91% of the time; >80% of estimates landed inside original 95% CIs; ~75% of failures traced to paper underspecification, not agent error. This validates the evidence-gating / derive-don't-guess / primary-source stance and argues for a method-specification completeness check.
- **Other reproducibility work:** LLM-assisted replication as a pre-submission self-check (https://arxiv.org/pdf/2602.18453); agentic replication-package scoring (https://arxiv.org/pdf/2606.02006). QuantEcon (https://quantecon.org) remains the computational substrate.

## Where the models and harness are (Sept 2026)

- **Model family fully turned over:** Sonnet 5 (Jun 30, now ~Opus 4.8-level, cheap agent workhorse), Opus 5 (Jul 24, 1M context, effort toggle), Fable 5.1 (Sep 1, "fewer confident wrong answers"), Haiku 4.5 (cheap multi-agent unit). All materially stronger at agentic coding, long-horizon autonomy, and instruction-following than Opus 4.8.
- **The nuance that constrains the redesign:** fabrication is reduced, not solved. Frontier models still invent citations with full confidence. The primary-source/citation gate keeps earning its keep.
- **Harness now first-class:** Skills, subagents (context isolation + forking, background by default), deterministic JS Workflows (`agent`/`parallel`/`pipeline` with schema-validated output), native Auto Memory + memory tool, automatic compaction, Plugins (ship skills + agents + hooks + commands + MCP as one versioned bundle), MCP. Much of the template's hand-rolled orchestration, memory, and cross-repo sync now has a native equivalent.

## Recommendation: a modernize-and-simplify pass

The organizing distinction: **gates vs nags.**

**Keep** — model-independent safety and truth:
- Destructive-action guard and settings-protection hooks (irreversibility; matches the OneDrive/shared-storage risk).
- The primary-source / citation gate (grounded in the fabrication data; a fabricated cite in a paper is the costliest failure).
- Tier-1 script-decidable checks (hardcoded paths, seed-once, undefined `\cite`) — cheap, deterministic.

**Simplify** — keep the intent, drop the brittle mechanism:
- Replace the citation-detection regex filter-stack (NEVER_SURNAMES, org skip-lists, suffix guards) with a cheap Haiku/Sonnet extraction subagent; keep the block, drop the maintenance.
- Move critic verdicts into Workflow `agent(..., {schema})` so empty-evidence verdicts are mechanically rejected, instead of a PostToolUse recorder plus a prose Stop audit.
- Lean on native Auto Memory + memory tool + compaction for session continuity; keep ADRs (a human artifact).

**Prune** — now over-engineering the Claude 5 models handle themselves:
- diagnostic-claim-audit Stop hook, plan-persist, log-reminder, output-length Stop hooks — process nags, brittle, Windows-fragile, and currently off anyway.
- The opt-in blocking variant of derive-don't-guess (keep the cheap advisory resolvability check).

**Add** — lean into the new primitives:
- Re-implement the Orchestrator + worker/critic pairs as a native JS Workflow (deterministic control flow, schema-validated scores). Biggest hand-rolled-to-native win.
- Ship the template as a Plugin; this replaces the hand-rolled `/tools propagate` cross-repo sync with the canonical versioned-bundle mechanism.
- Cost-tier the agents: Haiku/Sonnet for the many critics and extraction, Opus 5 / Fable 5.1 for identification-strategy and hard reasoning (cheap now that forking inherits the prompt cache).
- Add a method-specification completeness check (grounded in the Ash result).

## The decision that shapes all of this

Most of the current TODO is lab-scale machinery: propagation to seven consumer repos, two overlay branches, cross-repo DVC/LFS. That assumes an active multi-project academic lab. If that lab is now dormant while the day job is the focus, the propagation and overlay tooling is the first thing to retire, and this collapses to a leaner personal template — which is the same direction as the modernize pass. If the lab is still live, the propagation machinery stays but should migrate to the Plugin mechanism. **Answer needed:** is the academic research lab still active, or is this now a personal reference and occasional tool?

## Migration cautions

- Do not prune the citation gate on "models are better now" — the fabrication data says otherwise.
- Keep safety hooks regardless of model; alignment is not the same as refusing a destructive command you asked for.
- Schema evidence-gating binds only inside a Workflow; ad-hoc `/review` reverts to advisory.
- Subagent forking + background-by-default break rules that assume serial dispatch (three-strikes loops, orchestrator-dispatches-then-waits) — revisit those.
