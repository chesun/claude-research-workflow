# Deep survey of Claude Code research infrastructure + an integrate/adapt/skip method

**Status:** RUNNING (v5) — owner chose the **broad** ecosystem scope (cost is not a constraint) with the **voice stream in mechanism-only mode** (design the machinery now; plug the owner's exemplar papers in at build time). Method + harmonization framing carried over from the reviewed lean version; the two plan reviews (`..._infra-survey-plan_review.md` 62/100, `..._infra-survey-plan-v3_review.md` 84/100) still bind — no re-importing pruned nags, no re-growing the template, decisions not dumps.

## Goal

At **feature level**, a decision for each candidate capability in the current Claude-Code-for-research ecosystem: **integrate / adapt / skip**, with a stated reason, ranked into a roadmap. Anchored on Pedro Sant'Anna's repo (this workflow's original base) and the ecosystem it points to. Academic **voice preservation** is a first-class stream.

Survey → decide. It does **not** build. Each chosen feature becomes its own plan → independent review → build per `independent-review.md`. The modernize overlay mirror is decoupled — not blocked on this.

## Workstreams (parallel, one fresh agent each)

- **A — Base deep-read.** Feature-level inventory of `github.com/pedrohcgs/claude-code-my-workflow` at its current version: each notable skill/agent/rule/hook, what's Claude-5-native vs hand-rolled, its qualification-ledger/backtest-gate discipline, model routing, and specifically its writing/voice handling. Output: a feature table with an integrate/adapt/skip pre-call.
- **B — Ecosystem enumeration.** Fetch the guide's ecosystem section (`psantanna.com/claude-code-my-workflow/workflow-guide.html#sec-ecosystem`), list every source, and for each adoptable tool (esp. the OpenEcon/`hanlulong` skills — paper-review, writing, slides, auto-research, Stata-MCP, data) extract what it does, maturity, dependencies (MCP/OS/services), licence.
- **C — Voice preservation (mechanism-only).** Answer Q1–Q4 (below) and return a buildable design for two per-paradigm voice profiles, **without** an exemplar corpus yet — design how profiles are represented, stored, kept current, measured, and wired into `writer`/`writer-critic`/`/humanize`/`anti-ai-prose`. Read the upstream `/voice-profile` as the exemplar.
- **D — Native cross-check.** For every candidate A–C surfaces, whether Claude Code / the Claude 5 platform now provides it natively (Skills, subagents, Workflows, memory, output styles, plugins), so "adapt toward native" is visible.

All agents: fresh general-purpose, web-enabled, read-only except their report, evidence/URLs per claim, synthetic sentinels, save to `quality_reports/reviews/2026-09-22_infra-survey_<stream>.md`.

## Harmonization: `/humanize` + a voice profile (workstream C's core)

`/humanize` and `anti-ai-prose.md` are intact (the modernize pruned only hooks). **Settled:** (1) rename the existing path-inferred *register* knob to **register profile**, freeing **voice profile** for the new positive per-paradigm author-voice spec; (2) `anti-ai-prose`/`/humanize` stay **subtractive**, a voice profile is **additive** (`writer` generates toward it); (3) two profiles (applied-micro, behavioral) from a named corpus (deferred — mechanism-only now).

**Open questions the survey must resolve (do NOT pre-decide):**
- **Q1** — keep `/humanize` and voice-profile **separate** (default; preserves `/humanize` idempotency, matches upstream's two-skill split) or combine? Justify any deviation.
- **Q2** — bound the supersession: an **enumerated** carve-out set + a **non-supersedable Critical floor** (em-dash density, tricolons, mirror-echo, etc.) a profile can never switch off.
- **Q3** — do the academic carve-outs (`Importantly,`, "implement an experiment", "serves as the control"; the open TODO names `storyteller-critic` too) live at the **register/catalog level** (all critics) rather than bound to a paper-only paradigm profile? Likely yes.
- **Q4** — how is **conformance measured** (feature checks / exemplar diff / rubric), and how is a profile stored and kept current? Explicit deliverable, not an assumption.

## The decision method (integrate / adapt / skip)

Hard filters first (pre-bucket): re-imports a pruned nag → SKIP unless re-justified; hand-rolled where Claude 5 is native → ADAPT toward native or SKIP; not cross-platform (Win+Mac) and not portably fixable → ADAPT/SKIP; lab/multi-consumer-scale → SKIP. Then score survivors on **value / fit / redundancy / cost / upkeep** → **INTEGRATE** (adopt as-is) / **ADAPT** (take the idea, rebuild minimal) / **SKIP** (with a one-line reason). Output: one feature catalog (source, what it does, native equivalent, five scores, bucket, rationale), ranked by value-over-cost.

## Deliverables

1. Four stream reports (A–D) under `quality_reports/reviews/2026-09-22_infra-survey_<stream>.md`.
2. A synthesized **feature catalog** with integrate/adapt/skip decisions (the core artefact).
3. A **voice-preservation design** answering Q1–Q4 (mechanism-only; corpus deferred).
4. A **ranked integration roadmap** — each item to be planned + reviewed + built separately.

## Guardrails

- Survey and decide only; no building here. Each integrate/adapt candidate is checked against the modernize decisions before it earns a place — a better template, not a bigger one.
- Agents read public sources + this repo only; no confidential/other-repo content; synthetic sentinels; evidence/URLs per claim.
- The synthesized catalog + roadmap is itself a candidate for an independent review before any build begins.
