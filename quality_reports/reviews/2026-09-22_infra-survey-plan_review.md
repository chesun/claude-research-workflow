# Infra-Survey Plan — Independent Review
**Date:** 2026-09-22
**Reviewer:** independent plan critic (general-purpose agent)
**Target:** quality_reports/plans/2026-09-22_infra-survey-and-integration-method.md
**Score:** 62/100
**Status:** Active

## Verdict (fit / efficient / worth-the-cost)

The *method* is sound and the *voice* workstream is genuinely worth doing — but the plan as scoped is over-investment for a strictly-personal template whose lab is dormant, whose two live projects are behavioral and not even on this machine, and which is mid-way through a deliberate *shrink*. It is **fit** on paper (the hard filters explicitly guard against re-importing pruned nags and lab-scale machinery, and SKIP is treated as a real answer), but **not efficient** (four parallel web agents where the payoff concentrates in one-and-a-half; workstreams B and D substantially duplicate the 2026-09-16 landscape brief and one rubric column respectively), and **not worth its full cost**: the true expense is not the survey tokens but the build backlog it manufactures — every INTEGRATE item now triggers its own plan → independent-review → build cycle under the just-added ADR-0002 gate, which is the opposite vector from the modernize pass. Written by the same agent that authored the Sept-16 brief ("the highest-leverage direction is **not** more features") and the simplify plan, then pivots one week later to a feature hunt *before finishing the simplify*. Do the lean, voice-first version.

## Findings

| Severity | Finding | Evidence | Verdict | Recommendation |
|---|---|---|---|---|
| Critical | ROI inverted for a personal, shrinking repo: the survey's real cost is the downstream build backlog, not the agent tokens. Each INTEGRATE feeds the ADR-0002 review gate (plan→independent-review→build). | Plan lines 11, 71, 75 ("ranked integration roadmap — the ordered list of what to build next, each … planned+reviewed+built separately"); `.claude/rules/independent-review.md` (blocking review gate); modernize plan line 9 ("the real payoff is **removal**"). | WEAK | Scope to *decisions the owner will actually act on soon*, not a full ecosystem catalog. Cap the roadmap at the 1–3 items with clear near-term value (voice first). |
| Critical | Bias toward surveying/building by the author-agent. The Sept-16 brief (same author) concluded "not more features — modernize-and-simplify"; this plan reopens "what to add" a week later, before Track A steps 3–5 are done. | Landscape brief line 10 vs. this plan's whole framing; git log shows Track A steps 1–2 done (`7345c4d`, `12be99e`) but overlay-mirror/live-update/retire-propagation (modernize steps 3–5) still pending; this plan *gates the overlay mirror on the survey* (line 5, 75). | WEAK | Finish the simplify's overlay mirror on its own timeline; don't hold it hostage to an open-ended survey. If the survey is deferred, the mirror still ships. |
| High | Four agents is over-sized. Workstream D ("native cross-check") is a single rubric column, not a workstream; the Sept brief already inventoried native primitives (Skills, subagents, Workflows, memory, Plugins). | Plan line 28 (D) vs. line 47 (rubric already has a "native-equivalent" column) vs. landscape brief line 25 (native primitives already enumerated). | WEAK | Delete workstream D; keep "native-equivalent" as the rubric column it already is. |
| High | Workstream B (ecosystem enumeration) largely re-scans the Sept-16 brief, which already enumerated the ecosystem with URLs and maturity notes. | Landscape brief lines 14–19 (Sant'Anna v2.5.1, hanlulong/OpenEcon skills, Korinek NBER w34202, Ash reproduction, QuantEcon — all with URLs); this plan line 20 re-lists the same set. Web check confirms upstream still at v2.5.1 (last data 2026-08-24), i.e. little genuinely new in the ~1 week since the brief. | WEAK | Replace B with a *diff*: "what changed upstream since 2026-09-16?" — a 10-minute check, not a fresh full enumeration. |
| High | The one high-value, owner-prioritized item already exists upstream as a buildable exemplar — so it does not need a four-agent hunt to find. | Upstream README (web-fetched 2026-09-22): `/voice-profile` skill "extracts your written voice from prior papers and audits drafts against it … positive counterpart to /humanize." This *is* workstream C's target. | SOUND (for C) / WEAK (for the 4-agent framing) | Point one focused agent at the upstream's voice handling + `/voice-profile` and this repo's `anti-ai-prose.md` + open TODO. That is the whole job. |
| Medium | The decision method itself is genuinely good and does respect the modernize decisions — this is the plan's strongest part and should be preserved in any lean version. | Plan lines 34–56: hard filter 1 (pruned-nag re-import → SKIP), filter 4 (lab-scale → SKIP), 5-axis rubric incl. Redundancy and Upkeep; "the point is a better template, not a bigger one" (line 80). | SOUND | Keep the filters + rubric verbatim; apply them to the *lean* candidate set. |
| Medium | Voice workstream C is well-specified and correctly wired to existing infra — buildable, not hand-wavy. | Plan lines 58–65: two profiles (applied-micro, behavioral) from exemplar corpus, primary-source-first on the exemplars, wired into `writer`/`writer-critic`/`/humanize`, closes the open TODO. Repo has `anti-ai-prose.md` voice-profiles table (lines 46–58) and TODO line 26 "Econ academic voice profiles" open. | SOUND | Proceed with C essentially as written. Fold in the anti-ai-prose academic-FP carve-out TODO (TODO lines 48–53) as an explicit sub-item. |
| Low | "Save four stream reports + feature catalog + voice proposal + roadmap" risks producing dumps over decisions if the survivor set is large. | Plan lines 66–71 (four reports + catalog + proposal + roadmap). | WEAK | A SKIP-with-one-line-reason is already blessed (line 54) — enforce brevity: the deliverable is the decision table, not four long inventories. |
| Low | TODO.md is stale (last updated 2026-07-01) and does not reflect the modernize effort, so "the open TODO" the plan cites is real but the tracker around it is out of date. | TODO.md line 3 ("Last updated: 2026-07-01"); modernize work is Sept. | SOUND (the voice TODO is real) | Minor — refresh TODO.md when the voice work lands. |

## What to cut to make it cheaper

Concretely, collapse four web-enabled agents into **one focused agent (voice) plus a 10-minute owner-run diff**:

1. **Cut workstream D entirely.** "Is there a native equivalent?" is already a rubric column and was already inventoried in the Sept brief. Zero agents.
2. **Cut workstream B down to a diff.** Do not re-enumerate the ecosystem — the Sept-16 brief did that with URLs. Ask only "what changed upstream (`pedrohcgs`) since 2026-09-16?" Web evidence says: still v2.5.1, so likely near-nothing. Zero-to-light.
3. **Narrow workstream A to voice + genuinely-new.** Don't feature-inventory the entire base. Read the upstream's writing/voice handling (`/voice-profile`, `/humanize`, model-routing as a concept) and note only features that (a) are new since the brief and (b) survive the hard filters. Fold into the voice agent.
4. **Keep workstream C in full** — this is the payoff. Sourced from the owner's exemplar papers, two profiles, wired into existing `writer`/`writer-critic`/`/humanize`, closing the open TODO, with the upstream `/voice-profile` as the adopt-rather-than-rebuild reference.
5. **Keep the method (filters + rubric) verbatim**, apply to the lean candidate set.
6. **Decouple the overlay mirror** from the survey so finishing the simplify is not blocked on an open-ended feature hunt.

Net: ~1 agent instead of 4; the modernize pass finishes on its own schedule; the one thing the owner actually asked for (voice) still gets a concrete, buildable design.

## What the plan gets right

- The **decision method is disciplined**: hard filters run *before* scoring, and two of them (pruned-nag re-import; lab-scale machinery) are aimed squarely at not undoing the modernize pass. SKIP-with-a-reason is explicitly a valid output.
- **Survey-only, build-deferred** is the correct posture — it refuses to build inside the survey and routes each candidate through the normal review gate.
- The **voice workstream is a real gap with a real, buildable answer** (open TODO + existing anti-ai-prose infra + an upstream exemplar to adapt). This part deserves to run.
- It **cites the Sept-16 brief and says "build on, don't redo"** — the intent is right; the execution (four agents) just doesn't honor it.

## Sharpest single recommendation

Kill three of the four workstreams. Run **one voice-preservation agent** that reads the upstream's `/voice-profile` + `/humanize`, this repo's `anti-ai-prose.md`, and 2–3 exemplar papers, and returns a concrete two-profile design wired into `writer`/`writer-critic`/`/humanize` (closing the open TODO). Replace the ecosystem survey with a 10-minute "what changed upstream since 2026-09-16" diff. Let the modernize overlay-mirror finish on its own timeline rather than gating it on the survey. That captures ~90% of the benefit at ~25% of the cost, and it stops a simplify effort from quietly turning back into a feature-accretion effort.
