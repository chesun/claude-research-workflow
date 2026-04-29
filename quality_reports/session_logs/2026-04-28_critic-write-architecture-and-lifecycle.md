# Session log — 2026-04-28: Critic-write architecture + reviews/plans lifecycle

**Status:** Completed
**Branch (start):** main
**Branches touched:** main, applied-micro, behavioral
**Downstream repos updated:** tx_peer_effects_local, csac, va_consolidated, bdm_bic

---

## Goal

Resolve a recurring tension surfaced while doing two-layer code review in `tx_peer_effects_local`: the workflow's `coder-critic` agent has `tools: Read, Grep, Glob` (no `Write`) and a system prompt instruction "NEVER edit any files." That made it impossible for the critic to even *write a review report*, which forced the dispatcher to either (a) instruct the critic to print the review to stdout and then have the dispatcher transcribe it (lossy, no audit trail), or (b) violate the system prompt by giving the critic write permission for the report only.

Same problem on every other critic agent. The original "no editing" rule was meant to enforce separation of powers (critic doesn't fix what it finds), but it had collapsed two distinct concerns into one prohibition. The fix: split *source artifacts* from *report artifacts*.

Second, related concern: the user asked how we deal with file bloat in `quality_reports/reviews/` and `quality_reports/plans/` over time. Once critics start writing reports systematically, top-level browsing of these folders becomes navigationally problematic. Needed a lifecycle convention.

---

## Approach

### Source-vs-report distinction

| Class | Examples | Critic permission |
|-------|----------|-------------------|
| Source artifacts | `paper/main.tex`, `paper/sections/*.tex`, `talks/*.tex`, `scripts/**/*.{do,R,py}`, `figures/`, `tables/`, `references.bib`, `decisions/*.md`, `theory/`, `experiments/designs/`, `data/cleaned/*` | Read-only |
| Report artifacts | `quality_reports/reviews/<name>_review.md`, scoring tables, deduction breakdowns, escalation memos | Write encouraged |

Critics gain `Write` in their tools list. System prompt clarifies they may not edit source artifacts but must write a review report.

### Canonical review path

```
quality_reports/reviews/YYYY-MM-DD_<target>_<critic>_review.md
```

`<target>` is a stable per-target slug so glob-matching finds priors. `<critic>` is the agent name without `-critic` (e.g., `coder`, `writer`, `domain`, `methods`).

### Required header

```markdown
# <Target> Review — <Critic>
**Date:** YYYY-MM-DD
**Reviewer:** <agent>
**Target:** <slug>
**Score:** XX/100 (or PASS/FAIL)
**Status:** Active
**Supersedes:** <prior path, if applicable>
```

Status values: `Active | Completed | Superseded by <path> | Archived`.

### Lifecycle protocol

- **Supersession** (the natural mechanism): when a critic writes a new review for a target with an existing `Active` review, the prior review's `Status` is updated to `Superseded by <new>`, the file is `git mv`'d to `archive/`, and the new review's header carries `Supersedes:`.
- **Time-based archive** (slow-cadence sweep): `Status: Completed` + no edits for 90+ days → move to `archive/`.
- **`INDEX.md` per folder** lists `Active` items with one-line summaries; critics consult before writing to avoid parallel duplicates.

---

## What was changed

### `claude-research-workflow` (this repo) — main, applied-micro, behavioral

- `.claude/rules/agents.md` § 2 rewritten (source-vs-report distinction, canonical path, required header). New § 2a "Review and Plan Lifecycle" section.
- 13 critic-style agents: `Write` added to `tools`. System prompts updated with source/report boundary, save-the-report section pointing at canonical path, and the "consult INDEX.md and supersede" instruction.
  - Universal (10): `coder-critic`, `writer-critic`, `librarian-critic`, `explorer-critic`, `storyteller-critic`, `tikz-reviewer`, `domain-referee`, `methods-referee`, `verifier`, `editor`.
  - Applied-micro (1): `strategist-critic`.
  - Behavioral (2): `designer-critic`, `theorist-critic`.
- `quality_reports/reviews/README.md` (new) — full lifecycle conventions.
- `quality_reports/plans/README.md` (new) — same lifecycle for plans.
- `quality_reports/reviews/INDEX.md` and `quality_reports/plans/INDEX.md` (new) — seeded with current Active items.
- `quality_reports/reviews/archive/.gitkeep`, `quality_reports/plans/archive/.gitkeep` (new).
- `docs/concepts/worker-critic-pairs.md` — reflects new framing; lifecycle section added.

### Downstream repos

- **tx_peer_effects_local, csac, va_consolidated** (applied-micro): full critic agent set + `strategist-critic` + `agents.md` rule + lifecycle infra. Synced from workflow:applied-micro.
- **bdm_bic** (behavioral): full critic agent set + `designer-critic` + `theorist-critic` + `agents.md` rule + lifecycle infra. Only workflow files staged; user's unrelated WIP (TODO.md, advisor meeting slides, reading notes for healy_leo_2025.md) left untouched.

### CHANGELOG

v0.1.0 entry expanded to include critic-write architecture, lifecycle, and the docs ship (which had also already been completed in earlier sessions but was still listed as Unreleased). `Unreleased` slimmed to v0.1.1 polish items: `NEVER_SURNAMES` blocklist expansion and auto-archive sweep skill.

---

## Commits

- `claude-research-workflow:main` — `e80a9c1` feat(critics): allow review-report writes; add reviews/plans lifecycle
- `claude-research-workflow:applied-micro` — `667ef78` (cherry-pick) + `fedd3c2` strategist-critic
- `claude-research-workflow:behavioral` — `1dc91e4` (cherry-pick with verifier.md conflict resolved) + `431bbd5` designer-critic + theorist-critic
- `tx_peer_effects_local:main` — `7f8f425`
- `csac:main` — `fca625f`
- `va_consolidated:main` — `b2e5eba`
- `bdm_bic:main` — `2dd95bf`

All pushed to origin.

---

## Verifier-conflict resolution note

Cherry-picking the main commit onto `behavioral` produced a conflict in `.claude/agents/verifier.md`. The conflict was the rules numbering: behavioral has Stata-specific rule 5 ("check `.log` files for `r(...)` codes") and rule 6 ("Experimental materials checks N/A if no experiment"). The cherry-picked content added a new rule about source artifacts after rule 4. Resolution: kept behavioral's rules 5 and 6, added the source-artifacts rule as rule 7, and renumbered the adversarial-default rule from 5 to 8. The substantive content of all rules is preserved; only the numbering changed.

---

## Open follow-ups

- v0.1.0 tag across all 3 branches (next task this session).
- `/review` skill audit for stale critic framing (next task this session).
- `NEVER_SURNAMES` book/series-title expansion (deferred to v0.1.1; in CHANGELOG `Unreleased`).
- Auto-archive sweep skill (`/tools archive-stale`); deferred to v0.1.1.
- Backfilling `Status:` headers on pre-existing reviews and plans (low priority; can happen organically as files are touched).

---

## Cross-references

- Plan: did not write a separate plan file; user pre-approved the architecture in conversation.
- Rule: `.claude/rules/agents.md` § 2 and § 2a.
- Lifecycle docs: `quality_reports/reviews/README.md`, `quality_reports/plans/README.md`.
- Concepts page: `docs/concepts/worker-critic-pairs.md`.
- CHANGELOG: `CHANGELOG.md` § v0.1.0 — Critic-write architecture + reviews/plans lifecycle.
