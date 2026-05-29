<!-- primary-source-ok: compress_2026 -->
<!-- The string "Compress (2026...)" below refers to compressing the 2026-04-25 incident narrative in destructive-actions.md, not an academic citation. -->

# Workflow Context-Tightening Audit — workflow-audit

**Date:** 2026-05-28
**Reviewer:** workflow-audit
**Target:** `.claude/rules/*.md` always-on context footprint (28 files) + `CLAUDE.md`
**Status:** Active

---

## 1. Always-on footprint baseline

The harness auto-globs `.claude/rules/*.md` into always-on context on every session, plus `CLAUDE.md`. `.claude/references/` is **not** globbed — it is on-demand, pulled in by the skill/agent that needs it (precedent: `content-standards.md`, `replication-standards.md` already live there).

| Source | Bytes | Approx tokens | Auto-loaded? |
|--------|-------|---------------|--------------|
| `.claude/rules/*.md` (28 files) | 169,401 | ~42,400 | Yes (always-on) |
| `CLAUDE.md` | 10,340 | ~2,600 | Yes (always-on) |
| **Total always-on** | **179,741** | **~45,000** | — |
| `.claude/references/*.md` | (varies) | — | No (on-demand) |
| `.claude/agents/*.md`, `.claude/skills/*/SKILL.md` | (varies) | — | No (on-demand) |

Token estimate uses ~4 bytes/token. The user's stated concern — ~45k always-on tokens diluting attention / weakening rule binding — is confirmed at the byte level.

### Largest always-on rule files (bytes)

| File | Bytes | Hook rule? |
|------|-------|-----------|
| `adversarial-default.md` | 15,950 | Yes (trim-in-place only) |
| `primary-source-first.md` | 14,215 | Yes (trim-in-place only) |
| `data-version-control.md` | 13,585 | No |
| `anti-ai-prose.md` | 12,313 | No |
| `destructive-actions.md` | 11,158 | Yes (trim-in-place only) |
| `working-paper-format.md` | 10,939 | No |
| `workflow.md` | 10,893 | Yes (trim-in-place only) |
| `agents.md` | 9,870 | No |
| `derive-dont-guess.md` | 9,613 | Yes (trim-in-place only) |
| `quality.md` | 7,325 | No |
| `no-assumptions.md` | 7,218 | No |

The four largest non-hook files (`data-version-control`, `anti-ai-prose`, `working-paper-format`, `agents`) total ~46.7KB and are the dominant relocatable mass. Three of the largest hook files (`adversarial-default`, `primary-source-first`, `destructive-actions`) are trim-only but carry substantial compressible verbosity (incident narratives, duplicated checklists, example padding).

---

## 2. Redundancy map (cross-cutting duplication clusters)

Five duplication clusters span the rules. Each lists where the same content currently appears.

### Cluster 1 — Epistemic-stack "four rules / four failure modes" table

The comparison table (no-assumptions / primary-source-first / derive-dont-guess / adversarial-default, keyed by source-of-truth) appears in full **twice** and is restated as prose a third time:

- `no-assumptions.md` lines 21-28 (full table) + §"Why this is a separate rule" 102-109 + Cross-references 113-118
- `derive-dont-guess.md` lines 36-47 (full duplicate table) + "Where this fits in the epistemic stack" prose + Cross-references 115+
- `adversarial-default.md` opening framing + Cross-references 188-194 (partial restatement)

Canonical home: `no-assumptions.md` (the only non-hook member; prose IS its enforcement since it has no hook).

### Cluster 2 — AEA / Chicago author-date citation style

Fully canonicalized in `primary-source-first.md` lines 85-130 (et-al thresholds, Oxford comma, no author-year comma, worked examples). Restated in:

- `working-paper-format.md` §"Citation form" lines 226-244 — which *already names* primary-source-first as canonical (line 241) yet restates the examples
- `agents/writer-critic.md` deduction row (correctly references, does not fully restate)

Canonical home: `primary-source-first.md` (hook rule — leave intact; remove the duplicate from `working-paper-format.md`).

### Cluster 3 — Replication tolerance thresholds

Near-verbatim table (integers=exact, point estimates <0.01, SE <0.05, percentages <0.1pp, runtime within 2x) in:

- `replication-protocol.md` lines 43-51 (and again 122-128)
- `quality.md` §4 lines 167-178 — which itself says "See replication-protocol.md for the full workflow"

Canonical home: `replication-protocol.md`.

### Cluster 4 — Output-standard "two places" + booktabs principle

The "information goes in two places (descriptive filename + LaTeX caption/notes)" convention and the booktabs / threeparttable / no-in-output-titles / bare-tabular rule appear in **three** files:

- `tables.md` lines 7-13
- `figures.md` lines 8-10, 40-41
- `working-paper-format.md` Tables-and-Figures section lines 206-212

Plus heavy overlap with the orphaned `.claude/references/content-standards.md` (§ Table Standards + figure spec), which currently has **zero consumers**.

### Cluster 5 — Orchestration tables (dispatch / dependency / escalation / parallel)

- `workflow.md` §2 Agent Dispatch Rules (100-113) overlaps `agents.md` Worker-Critic Pairs table
- `workflow.md` Standalone Skills table (224-236) overlaps `CLAUDE.md` Skills Quick Reference
- `workflow.md` SELF-duplicates: "Parallel Dispatch" (115-120) is near-identical to "Parallel Activation" (183-188)
- `agents/orchestrator.md` re-tabulates the dependency graph (workflow.md §3), three-strikes routing (agents.md §3), and gate thresholds (quality.md)
- Critic-vs-creator boilerplate ("never edit source / DO write a review report") restated verbatim in all 6 critic agents vs. canonical `agents.md` §2
- Journal-calibration 4-step block + "Critical Rules" (ignore commented LaTeX; tables are source of truth) restated verbatim across `domain-referee.md`, `methods-referee.md`, `editor.md`

---

## 3. Per-cluster / per-file findings

| File | Bytes | Hook | Disposition | Movable / trimmable substance |
|------|-------|------|-------------|-------------------------------|
| `data-version-control.md` | 13,585 | No | Move ~85% to references | Enabling LFS/DVC, new-machine setup, coauthor onboarding, rollback, failure-modes — all only-needed-when-enabling. Keep 3-class table + when-to-enable + daily-sync stub (~2KB) always-on |
| `working-paper-format.md` | 10,939 | No | Move preamble to references | ~120-line LaTeX preamble + design-decisions + title/abstract boilerplate; consulted only when authoring/compiling. Dedup citation block to primary-source-first pointer |
| `anti-ai-prose.md` | 12,313 | No | Move to references | 35-pattern catalog; ALL real consumers (writer.md:103, storyteller.md:64, writer-critic.md:198, storyteller-critic.md:82, write/SKILL:39, humanize/SKILL:10/30/59) already read it by path. Always-on copy is redundant |
| `agents.md` | 9,870 | No | Move §2/§2a detail to references; keep invariants stub | Review-report path/header conventions, lifecycle/supersession/INDEX format — on-demand. Keep: every worker has a critic, critics never edit source, creators never self-score, three-strikes escalates |
| `quality.md` | 7,325 | No | Move §3+§4 to references; keep §1/§2 | Per-target deduction tables (each critic already embeds its own copy) + replication tolerances (dup of cluster 3). Keep scoring protocol + gate thresholds + severity gradient |
| `r-code-conventions.md` | 4,922 | No | Move to references | Referenced by ZERO agents/skills today; load-bearing checks survive in adversarial-default R checklist + quality R table |
| `python-code-conventions.md` | 1,407 | No | Move to references | Referenced by ZERO agents/skills; tertiary language; checks survive in adversarial-default Python checklist |
| `figures.md` | 2,650 | No | Merge into references/content-standards | Produce-time only; heavy overlap with orphaned content-standards.md |
| `tables.md` | 3,496 | No | Merge into references/content-standards | Produce-time only; heavy overlap with orphaned content-standards.md |
| `tikz-visual-quality.md` | 1,714 | No | Move to references | tikz-reviewer.md:98 + storyteller-critic.md:49 already read by path |
| `replication-protocol.md` | 4,977 | No | Move/merge into references (w/ replication-standards.md) | Phase-specific; verifier.md:67 + /submit are on-demand callers |
| `logging.md` | 5,445 | No | Move format templates to references; keep triggers | §1 hard-cap trigger is hook-backed (log-reminder.py) — keep trigger always-on; move verbose entry templates |
| `decision-log.md` | 4,661 | No | Move format to references; keep stub | No agent references by name; template already in decisions/README.md |
| `exploration-fast-track.md` | 880 | No | Merge with folder-protocol | Same `explorations/**` scope; one merged exploration.md |
| `exploration-folder-protocol.md` | 1,352 | No | Merge with fast-track | Same scope; overlapping lifecycle |
| `revision.md` | 1,510 | No | Trim in place (drop ASCII diagram) | Diagram duplicates the table; keep table + rules |
| `verification-protocol.md` | 2,502 | No | Trim in place | Genuinely always-on (routine task-boundary). Compress verifier-dispatch redundancy only |
| `single-source-of-truth.md` | 2,355 | No | Trim in place | Genuinely always-on (paper-authoritative constrains routine edits). Dedup fidelity checklist |
| `todo-tracking.md` | 1,326 | No | Trim in place (light) | Keep behavioral nudge always-on; dedup crosswalk only |
| `meta-governance.md` | 1,100 | No | Keep as-is | Genuinely always-on; commit/don't-commit applies to every commit. (Note: line 7 says "UAB"; user is UC Davis per memory — content-accuracy flag, not footprint) |
| `no-assumptions.md` | 7,218 | No | Trim in place (canonical scaffolding home) | Keep table once; remove §"Why this is a separate rule" prose 102-109 |
| `adversarial-default.md` | 15,950 | **Yes** | TRIM IN PLACE ONLY | Tighten 6 per-domain checklist rows that re-grep conventions files. Ledger machinery + exception protocol stay verbatim |
| `primary-source-first.md` | 14,215 | **Yes** | TRIM IN PLACE ONLY | Compress "Why this exists" narrative + five-filter prose. Do NOT move citation block (Stop-hook audit references it) |
| `derive-dont-guess.md` | 9,613 | **Yes** | TRIM IN PLACE ONLY | Collapse duplicate epistemic-stack table to pointer; tighten 4 examples to 2 |
| `destructive-actions.md` | 11,158 | **Yes** | TRIM IN PLACE ONLY | Compress the 2026-04-25 incident narrative + duplicated Tier-3 prose. Keep all command tables + bypass + verification protocol verbatim |
| `stata-code-conventions.md` | 4,837 | **Yes** | TRIM IN PLACE ONLY | Compress Invocation prose; dedup figure/table rows. Keep Comment Safety section (lines 51-67) verbatim (hook-load-bearing) |
| `workflow.md` | 10,893 | **Yes** | TRIM IN PLACE ONLY | Collapse self-duplicated parallel block; remove dup dispatch/skills tables. Keep §1 Plan-First + §5 Context Mgmt |
| `output-length.md` | 1,188 | **Yes** | TRIM IN PLACE ONLY | Tighten Enforcement paragraph by 1-2 sentences. Keep hook path + threshold pointer |

---

## 4. What does NOT move (honest constraints)

### Hook-load-bearing rules — TRIM-IN-PLACE ONLY, never move/merge/rename

Their hook remediation messages reference these exact paths; moving or renaming breaks the hook:

- `primary-source-first.md` — `primary-source-check.py` / `primary-source-audit.py`
- `derive-dont-guess.md` — `derive-check-advisory.py` / `derive-check-block.py`
- `adversarial-default.md` — critic enforcement + ledger references
- `destructive-actions.md` — `destructive-action-guard.py` / `post-rewrite-verify.py`
- `stata-code-conventions.md` — `stata-comment-balance-check.py` (Comment Safety section must stay verbatim)
- `workflow.md` — `plan-persist-check.py` (§1 Plan-First path)
- `output-length.md` — `output-length-check.py`

These collectively total ~67.6KB always-on; trimming verbosity in place can recover a meaningful fraction without touching any hook-referenced path or remediation text.

### Genuinely always-on rules — keep loaded

These constrain *routine* behavior at every task boundary, not just one phase:

- `meta-governance.md` — commit/don't-commit gate applies to every commit (1,100 B)
- `no-assumptions.md` — has no hook; prose IS the enforcement; user-facing entry rule for the epistemic stack
- `quality.md` §1/§2 — gate thresholds (commit/PR/submission) + severity gradient govern every gate
- `workflow.md` §1/§5 — Plan-First (hook) + Context-Management (compression survival)
- `verification-protocol.md` — applies at every commit/PR/end-of-session boundary
- `single-source-of-truth.md` — paper-authoritative constrains routine editing across sessions
- `todo-tracking.md` — behavioral nudge worth keeping ambient

### Substance preserved, not deleted

Every move targets `.claude/references/` (on-demand) and is paired with a pull-in pointer from the consuming skill/agent, or folds into an existing reference file. No requirement is removed — this is location + verbosity, per the MODERATE-aggressiveness constraint.
