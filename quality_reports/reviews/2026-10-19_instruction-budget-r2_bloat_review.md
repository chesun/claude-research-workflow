# Instruction Budget r2 Review — bloat
**Date:** 2026-10-19
**Reviewer:** bloat critic (independent, general-purpose agent)
**Target:** CLAUDE.md, .claude/rules/adversarial-default.md, .claude/rules/workflow.md, .claude/rules/quality.md, .claude/rules/agents.md, .claude/rules/primary-source-first.md, .claude/rules/destructive-actions.md
**Score:** 91/100
**Status:** Active

## Verdict

The repo's always-loaded set now measures **85,442 characters** (CLAUDE.md + 16 unscoped rules), down **35,913 (−29.6%)** from the prior review's 121,355. All 18 findings of `2026-10-19_instruction-budget_bloat_review.md` were applied — 16 fully, 2 with sound deviations (finding 2 keeps the in-text citation table inline; finding 16 moved the table to a new reference instead of pointing at the skill). The realised saving is 83% of the projected 43,560; the shortfall is pointer cost and deliberately conservative keeps, not omission. **No functionality loss found and no over-trimmed summary found**: every moved section leaves a pointer with a concrete "open it when …" trigger, the behavioural floors (lookup protocol, diagnosis protocol, blocked-command tables, bypass prefixes, escape hatches, three-strikes rules, gate thresholds) all stay inline, the eleven new/extended `.claude/references/*` files carry the moved content verbatim under matching headings, and `.claude/file-classes.toml` classifies them. Remaining low-risk savings are ~5,100 chars of internal duplication and rationale inside the surviving rules (the self-score table that restates the pairs table, two "why" paragraphs in workflow.md, the derive-dont-guess enforcement history, the no-assumptions "why separate" recap, the cd-chain paragraph subsumed by the chains summary) — diminishing returns, nothing Critical. One drift risk to watch: `revision-protocol.md` now duplicates the classification table that `.claude/skills/revise/SKILL.md` also carries.

## Always-loaded set (measured, `wc -m`, on-disk uncommitted state)

| File | Chars (r1 → now) | Saved |
|---|---|---|
| .claude/rules/adversarial-default.md | 18,609 → 9,784 | −8,825 |
| .claude/rules/workflow.md | 12,718 → 8,052 | −4,666 |
| .claude/rules/primary-source-first.md | 12,004 → 8,151 | −3,853 |
| .claude/rules/agents.md | 11,168 → 9,642 | −1,526 |
| CLAUDE.md | 11,126 → 9,423 | −1,703 |
| .claude/rules/destructive-actions.md | 10,235 → 7,589 | −2,646 |
| .claude/rules/derive-dont-guess.md | 9,078 → 5,974 | −3,104 |
| .claude/rules/quality.md | 7,942 → 5,297 | −2,645 |
| .claude/rules/no-assumptions.md | 7,662 → 6,187 | −1,475 |
| .claude/rules/decision-log.md | 4,560 → 2,909 | −1,651 |
| .claude/rules/independent-review.md | 4,445 → 3,897 | −548 |
| .claude/rules/single-source-of-truth.md | 2,360 → 0 (path-scoped) | −2,360 |
| .claude/rules/verification-protocol.md | 2,644 (unchanged) | 0 |
| .claude/rules/logging.md | 1,980 → 1,886 | −94 |
| .claude/rules/revision.md | 1,480 → 861 | −619 |
| .claude/rules/todo-tracking.md | 1,342 (unchanged) | 0 |
| .claude/rules/meta-governance.md | 1,110 (unchanged) | 0 |
| .claude/rules/output-length.md | 892 → 694 | −198 |
| **Repo always-loaded total** | **121,355 → 85,442** | **−35,913** |
| User-scope rules (owner's installed copies, out of scope; noted only) | ~17,909 | — |
| **Grand total vs 150k limit** | **~103,351** | ~46.6k headroom |

## Application of r1 findings 1–18

| # | r1 finding (est.) | Applied | Evidence | Chars actually saved |
|---|---|---|---|---|
| 1 | Per-domain checklists → reference (5,300) | **Fully** | adversarial-default.md:46–50 stub + pointer; adversarial-default-detail.md:9–102 carries all 8 domain tables | part of −8,825 (file total) |
| 2 | AEA citation guide → reference (4,500) | **Fully, sound deviation** | primary-source-first.md:77–90 keeps the 6-row in-text form table (the per-sentence-used part) inline; aea-citation-style.md (5,161) carries the rest | ~−3,000 |
| 3 | Orchestrator loop + dependency graph → pointer (4,000) | **Fully** | workflow.md:86–88 two-sentence summary + pointer, :127 §3 one-liner; orchestration-loop.md:7–93 carries loop, dispatch table, graph; Limits/Simplified/Just-Do-It kept (:90–121) as recommended | ~−4,000 |
| 4 | Ledger mechanics → reference (3,400) | **Fully** | adversarial-default.md:58–60 one-line column list + pointer; lookup protocol (:62–68), staleness (:70–73) and diagnosis protocol (:81–84) kept inline as recommended; detail at adversarial-default-detail.md:104–143 | part of −8,825 |
| 5 | destructive-actions residue → detail reference (3,600) | **Fully** | destructive-actions.md:12–14 incident in 2 sentences; :41–43 Tier-3 compressed; :68–70 chains compressed; :100–102 pointer; detail file grew 4,827 → 8,607; Windows caveat usefully promoted inline (:60) | −2,646 |
| 6 | Derivation lookup table + examples → reference (3,200) | **Fully** | derive-dont-guess.md:…§ Pre-generation checklist is now 3 lines + pointer; derive-lookup-table.md (4,016) has table + all 3 Bad/Good pairs | −3,104 |
| 7 | quality.md §3 tables → reference (2,900) | **Fully** | quality.md:95–106 keeps the talk-advisory line, pointer and the 4-line Enforcement block; quality-deduction-tables.md (3,527) has all 4 tables | −2,645 |
| 8 | Path-scope single-source-of-truth (2,360) | **Fully** | single-source-of-truth.md:1–10 frontmatter, globs broader than recommended (adds `replication/**`, `**/*.tex`, `**/*.bib`) — safe direction | −2,360 |
| 9 | agents.md §2a lifecycle → reference (2,000) | **Fully** | agents.md:127–133: summary + blueprint-evidence exception (kept verbatim, correctly) + pointer; review-plan-lifecycle.md (3,061) | −1,526 |
| 10 | CLAUDE.md bulk-storage / overlays / getting-started (2,100) | **Fully** | CLAUDE.md:45–47, :86–88, :92–94 — each compressed to the operative lines (DVC two-step push and sync-status check survive inline) | −1,703 |
| 11 | Evidence-gating compression (1,900) | **Fully** | adversarial-default.md:18–34 — principle, verdict vocabulary, gate-on-claims, known limit, no-overclaim all kept; M9/Phase-3 detail moved (evidence-gating-detail.md grew +2,112) | part of −8,825 |
| 12 | no-assumptions table + examples trim (1,800) | **Fully** | no-assumptions.md: what-counts table at 3 rows, one Bad/Good pair kept, canonical 4-rule table kept; no-assumptions-examples.md (2,956) | −1,475 |
| 13 | workflow.md §4 skills table (1,500) | **Fully** | workflow.md:131–137 — two-modes sentence, pointer to CLAUDE.md § Skills Quick Reference (which survives at CLAUDE.md:125–142), `/new-project` constraint kept | part of −4,666 |
| 14 | decision-log format detail → decisions/README + reference (1,200) | **Fully (beyond estimate)** | decision-log.md § Format, fields and supersession — one paragraph keeps field names, the only-allowed-edit rule and cite-by-number; detail in decision-log-detail.md (3,089) | −1,651 |
| 15 | independent-review mechanism caveats (1,000) | **Partly (sound)** | independent-review.md § Mechanism keeps 3 compressed bullets (the two load-bearing ones + fails-closed-escapably, a defensible third keep); independent-review-detail.md (1,595) | −548 |
| 16 | revision.md table → skill pointer (1,000) | **Fully, deviation (see finding R5)** | revision.md:5 points to new revision-protocol.md (1,288) rather than the skill; Rules block incl. the DISAGREE-never-autonomous line kept | −619 |
| 17 | Six hook obituaries compressed (900) | **Fully** | logging.md:22 "Discipline, not a hook (pruned 2026-09-16)"; output-length.md:16; workflow.md:80,157; adversarial-default.md:107; derive-dont-guess obituary moved to derive-lookup-table.md:58 | ~−600 |
| 18 | primary-source "Why this exists" (900) | **Fully** | primary-source-first.md:92–96 — two sentences + pointer; full narrative at primary-source-filter-stack.md:52 | part of −3,853 |

Functionality spot-checks that passed: every pointer target exists and carries the moved headings; critics (`writer-critic.md:152`, `coder-critic.md:180`) and `skills/review/SKILL.md:80` carry the supersession steps independently of agents.md §2a; CLAUDE.md:121 now routes to the deduction-tables reference; the stale "Stop hook blocks unverified causal claims" claim in CLAUDE.md:36 was corrected in passing; file-classes.toml registers the new references.

## Findings (residual savings and watch items)

| # | Sev | Finding | Evidence (`file:line`) | Verdict | Recommendation (chars saved) |
|---|---|---|---|---|---|
| R1 | Medium | "Creators can't self-score" 9-row table restates §1's worker-critic pairs table (same nine pairs, third column adds nothing the pairs table lacks) | agents.md:105–115 vs agents.md:11–21 | SOUND | Replace the table with one sentence: "The score always comes from the paired critic — pairs in §1." (**~800**) |
| R2 | Medium | Two rationale paragraphs: "Why this helps … Reduces mid-plan pivots by 30-50%" and "Why operationalize up front" (persuasion, not instruction; tier semantics already pointer-loaded) | workflow.md:50, :60 | SOUND | Keep the first sentence of :60 ("assigning a tier before any work runs forces the goal to become falsifiable"); move the rest to evidence-gating-detail.md, which :60 already cites (**~900**) |
| R3 | Medium | Enforcement-history preamble ("For most of this rule's life it had no enforcement mechanism …") narrates the pre-2026-05-28 state; the hook description below it is the operative content | derive-dont-guess.md § Enforcement, first paragraph | SOUND | Compress to "Deterministic trigger since 2026-05-28; critic deduction tables also fire when a critic is dispatched." (**~600**) |
| R4 | Medium | "Why this is a separate rule from derive-dont-guess.md" restates the canonical 4-rule mapping table and the "Use this rule when…" paragraph earlier in the same file; the closing Cross-references list the siblings a third time | no-assumptions.md § Why this is a separate rule; § Cross-references | SOUND | Keep the two-line filepath-vs-target-journal example (it is the sharpest statement); fold it into § What this rule covers and drop the rest + the Cross-references list (**~900**) |
| R5 | Low | Drift risk, not budget: the new revision-protocol.md duplicates the classification/routing content `.claude/skills/revise/SKILL.md` already carries — two non-loaded copies of one table | .claude/references/revision-protocol.md vs .claude/skills/revise/SKILL.md:26–52 | WEAK | Either make the skill the single copy (r1's original recommendation) or add a sync note; zero always-loaded chars either way (**0**) |
| R6 | Low | "`cd X && ...` chain handling" section is subsumed by the Chains summary two sections below ("with `cd` carried across") | destructive-actions.md:62–66 vs :70 | SOUND | Delete the section; the worked example can join destructive-actions-detail.md § Chains (**~550**) |
| R7 | Low | Maintenance-bait factoid: regression-case count "136 as of 2026-10-14" dates itself and duplicates the test file header | destructive-actions.md:109 | SOUND | "regression cases covering both classes, bypass, chains, heredocs, …" (**~30**) |
| R8 | Low | Fork-time HOW-TO comment (branch choice, template attribution) loads every session; CLAUDE.md:45–47 and README Quick Start already cover fork setup | CLAUDE.md:3–13 | SOUND | Keep the "Replace [BRACKETED PLACEHOLDERS] / keep under ~150 lines" lines; move branch guidance and attribution to README (**~400**) |
| R9 | Low | Severity-prompt example block + closing Principle paragraph are illustration; the two tables in §2 are the behavioural content | quality.md:69–76, :89–91 | SOUND | Move the prompt example to orchestration-loop.md (the orchestrator is who writes that prompt); keep one summary line (**~450**) |
| R10 | Low | Duplicate pointer: primary-source-first points at the filter-stack reference twice, 44 lines apart | primary-source-first.md:52 and :96 | SOUND | Merge: end § Why this exists at the two-sentence narrative; the :52 pointer suffices (**~170**) |
| R11 | Low | Stale text: "institutional context (UAB)" in a template shipped to forks | meta-governance.md:7 | SOUND | "(your institution)" (**~0**) |
| R12 | Low | Over-trim sweep — negative result, recorded deliberately: decision-log's one-paragraph format summary, quality §3's talk-advisory line, workflow §3's one-liner and adversarial-default's one-line ledger column list were each checked against their use sites and remain actionable without the reference (field names, gates, round limits and column names stay inline; only formats/examples moved). No pointer lacks a trigger condition. | decision-log.md § Format; quality.md:95–99; workflow.md:127; adversarial-default.md:58 | SOUND | No action — do not trim these summaries further; they are at the floor (**0**) |

Residual low-risk savings if R1–R4, R6–R10 applied: **~4,800** chars (floor ~80,600). No recommendation deletes a behavioural rule; every remaining pointer is conditioned on a concrete moment, so the per-session pointer tax stays near zero.

## Process note

The whole change is uncommitted. Under `independent-review.md` these are advised (non-blocking) doc paths; this report and r1 together are the receipt — commit with both staged.
