<!-- primary-source-ok: trim_2026, compress_2026, incident_dates -->
<!-- Any "(YYYY-MM-DD)" / "(2026...)" strings below are incident dates or globs, not academic citations. -->

# Context-Tightening Consolidation Plan (path-scoping–led)

**Status:** LEVER 1 EXECUTED 2026-05-28 (commits 27d03a7, f48d554) — all 8 convention rules path-scoped; always-on rules 165,455 → 119,914 B (−45,541 B / ~11,385 tokens / 27%). Levers 2 (references/ split) and 3 (trim/dedup) NOT yet executed (await separate approval). **Lever-1 smoke check FULLY VERIFIED 2026-05-28 (both directions):** (a) fresh session with no matching file touched → anti-ai-prose absent from context (user-confirmed at session start); (b) after `Read README.md` (matches the `paths:` glob) → harness injected anti-ai-prose.md into context via system-reminder. Lazy-load confirmed on this Claude Code build. Branch ready to merge.
**Date:** 2026-05-28
**Goal:** Cut the always-on `.claude/rules/*.md` footprint WITHOUT losing any requirement. Location/loading + verbosity only — no requirement deleted.
**Primary mechanism (revised after the `paths:` finding):** add `paths:` YAML frontmatter to convention rules so they load **lazily** (only when a matching file is touched), instead of moving content to `references/`. Path-scoping needs **no file move, no rename, no consumer rewiring**, and hook-referenced paths stay intact. References/-relocation is used only where a rule has no clean file trigger.
**Empirical basis:** `tikz-visual-quality.md`, `exploration-fast-track.md`, `exploration-folder-protocol.md` already use `paths:` frontmatter and were confirmed **absent from this session's context** — proof the mechanism works on this Claude Code.
**Companion audit:** `quality_reports/reviews/2026-05-28_workflow-context-audit.md`

---

## Corrected baseline

- Always-on rules: **25 files / 165,455 B (~41.4k tokens)** + CLAUDE.md 10,340 B (~2.6k). (3 of the 28 rule files are already path-scoped/lazy and were excluded.)
- `.claude/references/` is on-demand (not globbed) — the relocation target for content with no path trigger.

---

## Lever 1 — Path-scope the convention rules (PRIMARY; low risk, zero rewiring)

Add `paths:` frontmatter; the file stays exactly where it is, hooks/cross-refs unaffected, and it drops out of always-on context until a matching file is edited. Each removes its **whole** size from always-on (no stub needed).

| # | Rule | `paths:` glob | Bytes off always-on | Hook? | Risk |
|---|------|---------------|--------------------|-------|------|
| 1 | anti-ai-prose.md | `paper/**`, `talks/**`, `**/*.tex`, `README.md`, `docs/**`, `**/*-blog.md` | 12,313 | no | low |
| 2 | working-paper-format.md | `paper/**`, `**/*.tex` | 10,939 | no | low |
| 3 | replication-protocol.md | `replication/**` | 4,977 | no | low |
| 4 | r-code-conventions.md | `**/*.R`, `**/*.r`, `**/*.Rmd` | 4,922 | no | low |
| 5 | stata-code-conventions.md | `**/*.do`, `**/*.doh` | 4,837 | **yes** | med-care |
| 6 | tables.md | `tables/**`, `paper/**`, `**/*.tex` | 3,496 | no | low |
| 7 | figures.md | `figures/**`, `paper/**`, `**/*.tex` | 2,650 | no | low |
| 8 | python-code-conventions.md | `**/*.py` | 1,407 | no | low |

**Lever 1 subtotal: 45,541 B (~11,385 tokens) ≈ 28% of always-on.**

- **#5 is the key reframe:** the workflow could only *trim* `stata-code-conventions` (~900 B) because it's a hook-rule. But path-scoping is **not** a move/rename — the file stays at its path, so the `stata-comment-balance-check.py` remediation reference still resolves and the hook still fires from `settings.json`. So the whole 4,837 B goes lazy, and it auto-loads exactly when you edit a `.do`/`.doh` file (when you need it). Net: bigger win than trimming, same safety. (Verify with the Lever-1 smoke check below.)
- Multiple `**/*.tex`-triggered rules (anti-ai-prose, working-paper-format, figures, tables) all co-load when you edit a `.tex` — correct, they're all relevant then.

---

## Lever 2 — References/ relocation (only where there's NO clean file trigger)

| # | Rule | Action | Bytes off always-on | Risk |
|---|------|--------|--------------------|------|
| 9 | data-version-control.md | Keep ~2.5 KB always-on stub (the 3-tier table + "see ref for setup"); relocate ~11 KB of LFS/DVC enable/rollback/failure-mode procedure to `references/data-version-control-setup.md`. LFS/DVC setup isn't file-edit-triggered, so path-scoping doesn't fit. | ~11,000 | med |
| 10 | quality.md §3/§4 (optional) | Relocate per-target deduction tables + tolerance tables to `references/scoring-rubrics.md`; keep §1 weights + §2 severity always-on. Critics Read the rubric on demand. | ~3,400 | med |
| 11 | agents.md §2/§2a (optional) | Relocate review/plan lifecycle detail to `references/agent-orchestration.md`; keep the pairing + separation-of-powers invariants always-on. | ~3,500 | med |

**Lever 2 subtotal: ~11,000 B core (data-version-control), up to ~17,900 B with the two optionals.**

---

## Lever 3 — Trim-in-place + cross-file dedup (universal always-on rules)

Mechanism-agnostic; for the rules that must stay always-on. Hook-rules are **trim-in-place only** — never moved/renamed, never touching a hook-referenced path or remediation string.

| # | Target | Action | Bytes | Hook? |
|---|--------|--------|-------|-------|
| 12 | epistemic-stack table | Keep the canonical "four rules / four failure modes" table in `no-assumptions.md`; collapse the duplicated copies in `derive-dont-guess`, `adversarial-default`, `primary-source-first` to a one-line pointer | ~1,400 | yes (3 files, in place) |
| 13 | destructive-actions.md | Condense the 2026-04-25 incident narrative + Tier-3 prose to essentials | ~2,500 | yes |
| 14 | workflow.md | Drop duplicated dispatch/parallel tables (point to agents.md) | ~2,400 | yes |
| 15 | adversarial-default.md | Condense per-domain checklist prose | ~2,200 | yes |
| 16 | primary-source-first.md | Condense narrative + the 5-filter walkthrough to a summary | ~1,800 | yes |
| 17 | crosswalk dedup | `logging.md` canonical; `decision-log.md` + `todo-tracking.md` point to it instead of restating the relationship | ~1,100 | no |
| 18 | misc light trims | `revision.md` ASCII diagram, `verification-protocol`↔`single-source-of-truth` overlap, `output-length`, `todo-tracking` | ~2,000 | mixed |

**Lever 3 subtotal: ~13,400 B (~3,350 tokens).** (Citation-style dup in working-paper-format is moot once #2 makes it lazy.)

---

## Bottom line — estimated always-on reduction

| Scope | Bytes off always-on | ~Tokens | % of ~165 KB |
|-------|--------------------|---------|--------------|
| **Lever 1 only (path-scope conventions)** | 45,541 | ~11,385 | **~28%** |
| Lever 1 + 2-core (data-version-control split) | ~56,541 | ~14,135 | ~34% |
| Lever 1 + 2 + 3 (full) | ~70,000–77,000 | ~17,500–19,250 | **~42–47%** |

The decisive change from the workflow's references/-led plan: the **biggest savings (Lever 1, 28%) are now LOW risk with zero rewiring** — previously those same files (anti-ai-prose, working-paper-format) required relocating content and retargeting 7+ pointers. Path-scoping makes the safe tier the *large* tier.

---

## Sequencing as atomic commits (branch `audit/workflow-context-tightening`)

1. `feat(context): path-scope the 7 non-hook convention rules (Lever 1 #1-4,6-8)` — add frontmatter only.
2. `feat(context): path-scope stata-code-conventions (#5)` — separate commit; verify the comment-balance hook still fires after.
3. `refactor(context): split data-version-control — stub + references/ setup doc (#9)`.
4. `refactor(context): dedup epistemic-stack table to no-assumptions canonical (#12)` — touches 3 hook files in place.
5. `chore(rules): trim-in-place hook-rule verbosity — destructive-actions, workflow, adversarial-default, primary-source-first (#13-16)` — one commit per file.
6. `refactor(context): crosswalk + misc dedup (#17-18)`.
7. (optional, separate approval) `refactor(context): quality/agents detail → references (#10-11)`.

---

## Verification

**Lever 1 smoke check (do this first, on rule #7 figures or #8 python — smallest):** add frontmatter, start a fresh session in a non-matching cwd, confirm the rule is absent from context (ask "is figures.md in your context?" → should be no); then edit a matching file and confirm it loads. (Already proven by the 3 existing path-scoped rules, but re-confirm one we add.)

**Frontmatter validity** — each path-scoped rule begins with a well-formed `paths:` block:

```bash
for f in anti-ai-prose working-paper-format replication-protocol r-code-conventions \
         stata-code-conventions tables figures python-code-conventions; do
  head -1 .claude/rules/$f.md | grep -q '^---$' && echo "OK $f" || echo "NO FRONTMATTER $f"
done
```

**Hook-path integrity** — path-scoping must not move/rename any hook rule; all seven still present at their exact paths:

```bash
for f in primary-source-first derive-dont-guess adversarial-default destructive-actions \
         stata-code-conventions workflow output-length; do
  test -f .claude/rules/$f.md && echo "OK $f" || echo "MISSING $f"
done
```

**Hook scripts still reference live paths:**

```bash
grep -rho '\.claude/rules/[a-z-]*\.md' .claude/hooks/ | sort -u | while read p; do
  test -f "$p" && echo "OK $p" || echo "BROKEN REF $p"; done
```

**Comment-balance hook smoke test (after #5):** `python3 .claude/skills/tools/stata_sweep.py --check` on a fixture — Comment Safety section must be byte-untouched.

**Always-on re-measure (after Lever 1):**

```bash
# Sum only rules WITHOUT paths: frontmatter = the true always-on set.
for f in .claude/rules/*.md; do head -1 "$f" | grep -q '^---$' || cat "$f"; done | wc -c
```

**No dangling pointers (after Lever 2 moves):** `grep -rn 'rules/data-version-control.md' .claude` shows only the intentional stub pointer, no stale full-path refs.

---

## Hook-rules — guard list

Trim-in-place ONLY; never move/rename/relocate (path references would break). **Exception:** adding `paths:` frontmatter is permitted (it is neither a move nor a rename) — used for `stata-code-conventions` (#5).

- `primary-source-first.md`, `derive-dont-guess.md`, `adversarial-default.md`, `destructive-actions.md`, `workflow.md`, `output-length.md` — trim only.
- `stata-code-conventions.md` — path-scope OK (#5) + trim; Comment Safety section byte-verbatim.

---

## What does NOT change (stays always-on)

The genuinely universal rules — `no-assumptions`, `derive-dont-guess`, `adversarial-default`, `primary-source-first` (prose-wide), `workflow` §1, `output-length`, `quality` core, `meta-governance`, `verification-protocol`, `single-source-of-truth`, `decision-log` trigger, `logging` triggers, `todo-tracking`, `revision`. These apply regardless of which file (if any) you're editing, so they can be *trimmed* but not path-scoped. `derive-dont-guess` is a borderline path-scope candidate (code-files) but kept always-on as a Core Principle; revisit if further reduction is needed.
