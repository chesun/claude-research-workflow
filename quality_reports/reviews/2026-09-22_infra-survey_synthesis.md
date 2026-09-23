# Infra survey — synthesis, feature catalog, and integration roadmap

**Date:** 2026-09-22
**Reviewer:** synthesis of survey workstreams A–D
**Target:** integrate/adapt/skip decisions across the Claude Code research-infra ecosystem
**Status:** Active
**Sources:** `2026-09-22_infra-survey_{A-base-deepread,B-ecosystem,C-voice,D-native}.md`

## Bottom line

The survey confirms the modernize direction rather than reversing it: the highest-value pickups are **voice preservation** (the owner's priority, and the ecosystem's most mature offering) and a **blind claim-verifier** fabrication gate; almost everything else is either already native, lab-scale, service/OS-locked, or a nag we already pruned. Net: a short integrate/adapt list, a long justified skip list. Nothing here argues for re-growing the template broadly.

Honest caveats from the agents: the base's version/fork-count claims (v2.5.1, "3000 forks") are **unverified** (likely summarizer noise) — ignore the numbers, the features are real. The base's model IDs (Opus 5 / Fable 5 / Sonnet 5) are its own SSOT and diverge from this harness — do not copy model pins.

## Revision after independent review (2026-09-23)

The synthesis review (`2026-09-23_infra-survey-synthesis_review.md`, 78/100) confirmed the voice design and the skip-list restraint, and confirmed `/verify-claims` is **genuinely non-redundant** with the citation gate (the citation gate only checks that reading notes exist and were touched; `/verify-claims` checks whether the claim actually matches the source — a draft can pass the former and still misstate a finding). It also caught corrections, applied here:

- **The roadmap is not a committed pipeline.** The binding 62/100 plan review capped this at 1–3 items, voice first; my 7-item "each = plan → review → build" list re-grew the very backlog the simplify effort removed. Corrected below: **voice preservation is the one committed next build; everything else is an uncommitted candidate list** to pull from only when a specific need appears, not a queue to work through.
- **Re-buckets:** `econ-writing-skill` moves INTEGRATE → **ADAPT/merge** (it heavily overlaps `anti-ai-prose.md`; merge its rules rather than adopt the skill whole). **Add `/audit-reproducibility`** (numbers-in-prose vs script-outputs) as **ADAPT** — I dropped it; it is distinct from `/verify-claims` (internal outputs, not external sources), cheap, and econ-relevant. **Add** a `.claude/hooks/` **bash-write coverage** item as ADAPT — report A noted a real gap: the settings-write guard is settings.json-only, so scripted writes to `.claude/hooks/` are ungated.
- **Re-cost:** the critic-verdict schema is **not cheap** — it only binds inside a JS `Workflow()`, which this template does not have, so it carries a Workflow-infra dependency; demote it.
- **Naming fix:** the voice design's "immutable Critical floor" collides with the catalog's Critical *severity* tier (some floor rows are catalog-Major). Rename to **"non-supersedable floor"** and key it to explicit row IDs, not the word "Critical."
- **Method honesty:** the 5-axis rubric was applied qualitatively, not tabulated per item; the ordering is a reasoned judgment, not a computed score. Stated plainly rather than implied.

## Decision catalog

### INTEGRATE (adopt largely as-is)
| Feature | Source | Why | Cost |
|---|---|---|---|
| `econ-writing-skill` anti-AI-prose + writing rules | B (`hanlulong`, MIT, zero-dep, cross-platform) | Synthesizes 50+ econ writing guides; near-sibling of our `anti-ai-prose.md`; directly strengthens the voice work | low |
| `writing-with-ai` honesty framing | A | "A model can't make its own output stop reading as model output"; provenance ≠ readability — a caveat worth stating in `anti-ai-prose.md` (but do NOT build around neural detectors) | low |
| AEA Data Editor Template README | B (Vilhuber, zero-dep) | Canonical replication-package README; the template already targets AEA compliance | low |

### ADAPT (take the idea, rebuild minimal)
| Feature | Source | Adaptation | Value |
|---|---|---|---|
| **Voice preservation** (`/voice-profile` + humanize-suppression) | A, C | Six-category feature-list `voice-profile.md` + additive generate-toward path (beyond upstream's audit-only) + two paradigm profiles + advisory Python feature checks + register-level carve-outs + immutable Critical floor. **The flagship; see design below.** | **high** |
| `/verify-claims` + blind forked `claim-verifier` | A | Chain-of-Verification: a forked verifier that never sees the draft checks each claim/cite against the source. Complements the citation gate and the review gate; matches the fabrication-gate philosophy | high |
| Critic-verdict JSON schema | D | Force each critic verdict through `required:[claim, artifact_citation, score]` so an empty-evidence PASS is mechanically rejected — hardens `adversarial-default.md` Phase-3 cheaply (no full Workflow migration) | med |
| `/vaccinate` hook-battery **principle** | A | "An unqualified check is none": add a planted-defect re-seed to the existing guard tests to prove each still fires. Skip the 10-gate LEDGER | med |
| Propagation → **Plugin** packaging | D | Fold with modernize step 5: retire `/tools propagate`/`sync-overlays`/`consumers.toml`; ship as a plugin bundle. Caveat: class-aware overlay routing must re-express as separate plugins | med (structural) |
| MixtapeTools deck rhetoric + Referee-2 audit | B | Mine for the talk/figure path | low-med |
| Main-session house-voice **output style** | D | Native output styles set main-conversation voice — but do NOT reach the `writer`/`storyteller` subagents, so they complement, not replace, `/humanize` | low |

### SKIP (with reason)
- Base nag hooks (`context-monitor`, `pre-compact`, `post-compact-restore`, `log-reminder`, `notify.sh`) — the exact class already pruned here.
- Full `backtest.sh` 10-gate + LEDGER, `/promote-memory` council, `/deploy`, `/seven-pass-review`, `/oracle-review` — lab/multi-consumer ceremony.
- Duplicate `git-guardrails.py`/`root-of-trust-guard.py` — overlap existing destructive-action + settings-write gates.
- Teaching/Quarto stack — out of scope.
- `openecon-data` — paid OpenRouter key + AGPL + MCP server.
- Both `stata-mcp` repos — need licensed local Stata (none on this machine).
- `econ-slides-skill`, `overleaf-sync-now` — need LaTeX/Overleaf (absent).
- `econ-auto-research` — no code yet (watch).
- `clo-author`, `claudeblattman` — heavyweight/nag-ish ancestors; mine patterns only.
- Neural-detector framing, voice fingerprinting, fine-tuning — provenance theater; token-stat detectors score surface-de-AI'd text as 100% AI anyway.
- `MEMORY.md` parser work — already native (Auto Memory); no action.
- Model-version hard-expiry / per-agent 70-20-10 pins — brittle; keep only an effort-first note.

## Voice-preservation design (workstream C, the flagship)

- **Represent** a voice as a six-category feature list (Lexicon, Rhythm, Openings, Transitions, Hedging, Quirks) with frequency annotations, **not** a numeric fingerprint. Two per-paradigm files `.claude/references/voice-profiles/{applied-micro,behavioral}.md`: YAML front-matter (corpus list, dates) + the six narrative categories + 3–6 few-shot exemplar sentences.
- **Build** by forking one subagent per exemplar paper (owner's named corpus, deferred); a trait qualifies only if it recurs across most of the corpus; reading the papers is gated by primary-source-first.
- **Q1 — separate skills.** `/humanize` (subtractive) and the voice-profile capability (additive) stay separate, wired by the shared profile artifact; combining breaks `/humanize` idempotency.
- **Q2 — bounded supersession.** An enumerated carve-out whitelist keyed to `anti-ai-prose` row IDs (L3 field verbs, L4 `serves as`, R4 single hedge, minor-rhythm rows, plus a frequency-backed signature-phrase whitelist), each needing corpus evidence; a **non-supersedable floor** (keyed to explicit catalog row IDs, not the word "Critical") a profile can never switch off: em-dash density, tricolon, negative parallelism, mirror-echo, AI-vocab core, hyperbole. Voice never touches the epistemic gates.
- **Q3 — carve-outs at register/catalog level,** not the paper-only profile: they're field conventions, must reach `storyteller-critic`, and must work with no corpus. (Catalog = what the field does; profile = what this author does.)
- **Q4 — measurement, three advisory tiers:** Tier 1 cross-platform Python feature checks (`voice_feature_lib.py`, advisory); Tier 2 `writer-critic` rubric scoring that cites profile lines (the positive counterpart to today's subtractive table); Tier 3 exemplar diff. All non-blocking (gates-not-nags). Kept current via a front-matter corpus list + rebuild-on-+3-papers + a `--check-stale` reusing the ledger-hash idea.
- **Call:** ADAPT. One cross-platform Python piece, advisory by default, no new blocking hook.

## Next build (committed) + candidate list (uncommitted)

Per the binding plan-review cap, this is not a pipeline. **One committed next build:**

1. **Voice preservation** (ADAPT) — the owner's priority, self-contained, closes the two open voice TODOs. Merge the `econ-writing-skill` rules and the `writing-with-ai` honesty caveat into it. Needs the owner's exemplar corpus at build time. → its own plan → review → build.

**Candidate list (documented, uncommitted — pull one only when a concrete need appears, each then its own plan → review → build):**

- `/verify-claims` blind claim-verifier (ADAPT) — the strongest genuinely-new fabrication gate; complements the citation + review gates. The most likely second pick.
- `/audit-reproducibility` (ADAPT) — numbers-in-prose vs script-outputs; cheap, econ-relevant.
- `.claude/hooks/` bash-write coverage (ADAPT) — closes a real settings-guard gap.
- AEA replication README (INTEGRATE) — cheap, do when assembling a replication package.
- hook-battery vaccination principle (ADAPT) — harden guard tests.
- Critic-verdict schema (ADAPT, **higher cost** — needs JS `Workflow()` infra the template lacks; only worth it if a Workflow is adopted anyway).
- Propagation → plugin (ADAPT, structural) — fold into finishing the modernize (subsumes step 5), independent of this survey.
- Lower still: MixtapeTools, a main-session house-voice output style, an effort-first model note.

## Next

Per the survey plan's guardrail, this synthesis is itself a candidate for an independent review before any build. Then roadmap items proceed one at a time through plan → review → build, starting with voice preservation (which needs the owner's exemplar corpus at build time).
