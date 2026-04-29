# Plan: Universal humanizer feature

**Status:** APPROVED — Phase 1 lean v1 implemented 2026-04-29 (commit forthcoming). Phase 2 hooks and Phase 3 sophistication deferred per user instruction (rule + skill + critic deductions sufficient for now; revisit hooks if patterns persistently slip through).
**Date:** 2026-04-29
**Sources:** existing `writer.md` Humanizer Pass (24 patterns, 4 categories); community survey (5 resources, see § References).

## What's already built

- `writer` agent has a "Humanizer Pass" section: 24 patterns across Content / Language / Style / Communication.
- `/write humanize [file]` skill mode runs the writer in humanizer-only mode.
- Anti-hedging deduction line in working-paper-format.md ("interestingly", "it is worth noting" → −3 each, max −15).
- Scope is paper-only (`paper/main.tex`, `paper/sections/*.tex`).

## What the user wants

Make the humanizer apply universally to **external-facing** documents — papers, slide decks (Beamer talks), README updates, blog posts, response letters, cover letters, abstracts, presentation handouts. Anything a human audience reads. NOT internal artifacts (session logs, ADRs, code comments, plans, reviews, reading notes).

## Community survey (top 5 resources, full agent report archived in conversation)

| # | Resource | What we'd borrow |
|---|---|---|
| 1 | [Aboudjem/humanizer-skill](https://github.com/Aboudjem/humanizer-skill) | 37-pattern taxonomy + 5 voice profiles + burstiness/perplexity grounding |
| 2 | [adenaufal/anti-slop-writing](https://github.com/adenaufal/anti-slop-writing) | Universal-system-prompt distribution pattern (one rule, multiple skills cite) |
| 3 | [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) | Structural-pattern categories (symmetric sectioning, promotional tone, over-explanation) — your current taxonomy underweights these |
| 4 | [lmmx AI tells rubric](https://gist.github.com/lmmx/d91de290ea4e6d9631e32c2dd43da413) | Severity-weighted rubric format that drops cleanly into critic deduction tables |
| 5 | [sam-paech/antislop-sampler](https://github.com/sam-paech/antislop-sampler) | Empirical-derivation method (corpus statistics, not curated wordlists) — v2 idea |

Field convergence: ~30–50 curated patterns, voice/register profiles, distribution as a Claude Code skill or universal system prompt. Your 24/4 is in the right ballpark; gaps are structural patterns + severity weighting + sentence-length variance.

## Architecture recommendation

Five layers, but not all at once. Phased rollout below.

### Layer 1 — Rule: `.claude/rules/anti-ai-prose.md`

The single source of truth. Documents:

- **Pattern catalog** (~35 patterns, 6 categories): lexical (vocabulary tells), syntactic (sentence structure), structural (sectioning, parallelism), rhetorical (signposting, hedging, tricolons), content (significance inflation, vague attribution), communication (filler phrases). Migrates the existing 24 + adds Wikipedia structural categories + Aboudjem burstiness checks.
- **Severity tiers** (critical / major / minor) following lmmx rubric. Ports cleanly to existing `quality.md` deduction conventions.
- **Scope (file globs)**: `paper/**/*.tex`, `talks/**/*.tex`, `**/*.md` external-facing only (README, CONTRIBUTING, CHANGELOG, docs/, blog/, response letter, cover letter), `paper/cover-letter.tex`. EXCLUDES `quality_reports/**`, `decisions/**`, `master_supporting_docs/**`, `.claude/**`, code comments.
- **Voice profiles**: `academic` (paper register, formal, dense), `slide` (terse, declarative, bulleted-but-not-AI-bulleted), `blog` (warmer, direct), `formal-correspondence` (cover/response letter), `casual`. Profile selected by file path or explicit flag.

### Layer 2 — Skill: `/humanize [path] [--profile <name>]`

Universal entry point. Replaces / generalizes `/write humanize`. Dispatches the humanizer agent against any path. Profile inferred from path (`paper/` → academic, `talks/` → slide, etc.) or explicit override.

### Layer 3 — Agent: `humanizer` (new)

Standalone agent with the full pattern catalog in system prompt. Modes:
- **Audit**: produces a review report listing every pattern hit, severity, location, suggested rewrite. Writes to `quality_reports/reviews/YYYY-MM-DD_<target>_humanizer_review.md`.
- **Apply**: edits in place, reports changes.

Critic-style — reads the rule, scores severity, but unlike a critic it can also apply edits when in Apply mode. (Different from writer-critic; writer-critic is read-only and scores manuscript polish overall; humanizer is targeted at AI-pattern stripping specifically.)

### Layer 4 — Hook: `.claude/hooks/anti-ai-prose-check.py` (PostToolUse, Edit|Write)

Lightweight regex check on Edit/Write deltas to scoped paths. **Warns**, doesn't block — this is stylistic, not factual. Counts: em-dash density per 100 words, "delve"/"navigate"/"leverage"/"tapestry" frequency, "It's worth noting" / "It is important to" instances. Stderr-prints if thresholds exceeded with prompt to run `/humanize`. Stop hook variant scans turn-end prose like primary-source-audit does — same architectural slot.

### Layer 5 — Critic integration

`writer-critic`, `storyteller-critic`, plus a new lightweight `humanizer-critic` (or fold into `writer-critic` as a separate deduction section) reference the rule and score against it. Deduction table entries:

| Severity | Issue | Deduction |
|---|---|---|
| Critical | High-confidence AI vocabulary (delve, tapestry, landscape, navigate, robust as filler) | −5 each, max −20 |
| Critical | Em-dash density >5 per 100 words | −10 |
| Major | Tricolon overuse (>3 per page) | −5 |
| Major | Signposting filler ("It's worth noting", "It is important to") | −3 each, max −15 |
| Major | Promotional inflation ("groundbreaking", "pivotal", "comprehensive") | −3 each, max −10 |
| Minor | Uniform sentence length (low burstiness) | −3 |
| Minor | "Not just X but Y" / negative parallelism overuse | −2 per |

## Phased rollout

**Phase 1 — universal foundation (v0.1):**
1. Write `.claude/rules/anti-ai-prose.md` (catalog migrated from writer.md + Wikipedia structural categories)
2. New `/humanize [path] [--profile]` skill (replaces `/write humanize`, retains backward compat)
3. New `humanizer` agent (Audit + Apply modes)
4. Update `writer.md` and `storyteller.md` to reference the rule (remove duplicated catalog from writer.md)
5. Critic deduction tables in `quality.md` § 3
6. Doc: surface in `docs/concepts/upstream-differences.md` as a contribution

**Phase 2 — enforcement (v0.2):**
1. PostToolUse hook on Edit|Write for highest-confidence patterns (warn-only)
2. Stop-hook prose audit (mirror primary-source-audit architecture)
3. `humanizer-critic` agent with severity-weighted rubric

**Phase 3 — sophistication (v0.3+):**
1. Burstiness check (sentence-length variance against academic baseline)
2. Voice-profile expansion + per-target tuning
3. Empirical pattern derivation (antislop-sampler-inspired) — pull tells from a corpus rather than curating

## Open design questions

- **Hook severity:** PostToolUse warn-only vs Stop-hook block-with-override. Stylistic violations probably shouldn't block, but a habitual-offender override (e.g., 3+ patterns in one edit) might warrant a Stop block to force `/humanize` before continuing.
- **Profile inference:** path-based vs explicit flag. Path-based is easier; explicit lets a paper section have "casual" register temporarily (e.g., a footnote anecdote).
- **Voice profile coverage:** academic and slide are obvious. The cover-letter / response-letter / README registers diverge — single "formal-correspondence" profile, or three?
- **Where does the humanizer agent fit in the orchestrator dependency graph?** Standalone (any time) or part of the Execution → Write pipeline as a final-pass agent before writer-critic?
- **Testing:** how do we validate the humanizer doesn't strip *legitimate* academic prose (the word "robust" is real in econometrics)? Need a regression suite of "do not flag" examples.

## Recommended decision points (for user)

1. **Phase 1 only**, or commit to all 3 phases now? (Phase 1 alone is the universal-feature ask; Phase 2-3 are upgrades.)
2. **Single humanizer agent** vs **fold into writer/storyteller** as shared library? (My lean: standalone agent. Cleaner abstraction; reusable across contexts.)
3. **Pattern catalog source:** migrate writer.md's 24 only, OR add Wikipedia structural + Aboudjem burstiness for ~35? (My lean: ~35 from day one. Migration cost small, coverage gap real.)
4. **Critic location:** new `humanizer-critic` agent vs add deduction section to existing writer-critic and storyteller-critic? (My lean: extend existing critics. One agent per artifact-type is the convention; adding a second critic on the same artifact splits responsibility.)
5. **Hook scope (Phase 2):** PreToolUse Edit/Write block, PostToolUse warn, or Stop-hook audit? (My lean: PostToolUse warn + Stop-hook for prose. Mirrors primary-source-first architecture exactly. Don't block — that overfires on legitimate uses.)

## Estimated effort

- Phase 1: 3–4 hours (1 rule, 1 skill, 1 agent, 2 agent updates, 1 critic-rubric extension, 1 doc page)
- Phase 2: 2–3 hours (2 hooks + 1 critic agent variant)
- Phase 3: 5–8 hours (burstiness scoring, profile tuning, corpus-derived patterns)

## References

1. Aboudjem/humanizer-skill: https://github.com/Aboudjem/humanizer-skill
2. adenaufal/anti-slop-writing: https://github.com/adenaufal/anti-slop-writing
3. Wikipedia: Signs of AI writing: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
4. lmmx AI tells rubric: https://gist.github.com/lmmx/d91de290ea4e6d9631e32c2dd43da413
5. sam-paech/antislop-sampler: https://github.com/sam-paech/antislop-sampler
