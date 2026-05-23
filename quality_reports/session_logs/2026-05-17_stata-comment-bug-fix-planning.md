<!-- primary-source-ok: add_2026, added_2026, new_2026, extend_2026, extended_2026, fix_2026, fixed_2026, change_2026, changed_2026, edit_2026, edited_2026, real_2026, mixed_2026, none_2026 -->
# Session Log — Stata Block-Comment Bug Universal-Fix Planning

**Started:** 2026-05-17
**Last updated:** 2026-05-23
**Scope:** plan, validate, and revise a universal fix for the Stata greedy-`/*` parser bug, to ship as Class A workflow infrastructure to all 7 consumers. Execution deferred.

---

## Goal

Take a bug pattern discovered + remediated in `va_consolidated` (89 of 129 files affected; round-3 fix at `py/sweep_comments_and_logdirs.py`) and lift the fix into the universal workflow so every consumer benefits:

1. Port the state-machine sweep tool into `.claude/skills/tools/stata_sweep.py` (drop va-specific bits)
2. Ship a PreToolUse hook that blocks edits introducing the bug
3. Codify the convention (no `*` glob in comments; commit-time balance check) in rules + critic + skill

Field guide is at `master_supporting_docs/stata-block-comment-bug-field-guide.md` (added by user 2026-05-17, updated 2026-05-18 with Variant 8).

---

## Day 1 — 2026-05-17: Plan-mode draft

- User invoked plan mode pointing at the new field guide.
- Phase 1: 2 Explore agents in parallel mapped (a) workflow Stata infrastructure (rules, hooks, agents, file-classes) + (b) va_consolidated reference implementation (763 LOC, function inventory, va-specific elements to drop).
- Phase 2: 1 Plan agent stress-tested the design. Surfaced 8 gaps:
  1. `Edit` with `replace_all=True` semantics
  2. `MultiEdit` tool missing from matcher (would silently slip through)
  3. Test fixture `.do` files would trigger coder-critic on themselves if placed under `do/` or `scripts/stata/`
  4. `--check` exit codes need to differentiate "issues found" from "tool broke" (separate 1 vs 2 vs 3)
  5. Field guide §8 reference becomes stale post-port — needs update in Commit 1
  6. Hook matcher is tool-name-based; suffix-check must be inside the hook
  7. Coder-critic deduction cap at -25 (otherwise files with 30 hits dock -150)
  8. Propagation needs both `/tools propagate` AND `/tools sync-overlays`
- Plan written to plan-mode file `~/.claude/plans/now-another-urgent-item-peaceful-creek.md`.
- ExitPlanMode called, approved.
- User asked to write plan to disk first (not execute). Copied to `quality_reports/plans/2026-05-17_stata-comment-bug-universal-fix.md` per workflow convention.

**Status end of Day 1:** plan APPROVED, awaiting pacing decision. 11 files, ~1,300 LOC.

---

## Day 2 — 2026-05-18: Variant 8 incorporated

- User updated field guide with Variant 8 ("over-flatten bug in fix-tool pre-pass" — the round-2 trap where the fix tool itself can introduce silent corruption).
- Re-read field guide. Variant 8 is a meta-bug: a buggy Variant-4 fix tool destroys legitimate `*/` body block markers when the depth counter overshoots due to path-glob `/*` in the outer header.
- Round-3 (2026-05-18) closes Variant 8 via path-glob-aware predicates: `_is_path_glob_open`, `_is_path_glob_close`. Both the depth-counted matcher AND the inner rewriter must skip path-glob digraphs.
- Plan revised. Key changes:
  - Function inventory grows: `_is_path_glob_open`, `_is_path_glob_close`, `_rewrite_inner_block_markers`
  - Lib LOC bumped ~350 to ~450
  - Test LOC bumped ~500 to ~600
  - Hook "clean" predicate gains V8 artifact detection (cheap grep on `^-+<x>$` and `^\s*<x>\s*$`)
  - New negative fixture `over_flatten_artifact.do`
  - New risk row: "Our sweep tool itself introduces Variant 8"
  - Coder-critic deduction includes V8 artifacts (-25 Critical)

**Status end of Day 2:** plan APPROVED with V8 revisions. 12 files, ~1,450 LOC.

---

## Day 3 — 2026-05-23: Fleet preview + top-3 inspection + 3rd revision

### Fleet preview (read-only)

User asked how to validate plan solidity. Recommended three layers (real-codebase preview, agent review, fixture pre-build). User approved Layer 1.

Ran field-guide §3 grep commands against all 7 consumers (732 .do/.doh files). Pure read-only. Report saved to `quality_reports/reviews/2026-05-23_stata-comment-bug-fleet-preview.md`.

Headline metrics:

| Consumer | files | V1 unbalanced | V2 | V7 | V8 |
|---|---:|---:|---:|---:|---:|
| va_consolidated | 129 | 0 ✓ | 0 | 0 | 0 |
| tx_peer_effects_local | 297 | 46 (15%) | 18 | 31 | 0 |
| belief_distortion_discrimination | 134 | 7 | 0 | 39 | 0 |
| belief_distortion_discrimination_audit | 99 | 7 | 0 | 35 | 0 |
| csac | 46 | 3 | 1 | 0 | 0 |
| bdm_bic | 15 | 0 | 0 | 0 | 0 |
| csac2025 | 12 | 0 | 0 | 0 | 0 |

Plan premise validated:
- va_consolidated reports 0 issues post-Round-3 (idempotence confirmed on real corpus)
- V8 detection patterns return 0 everywhere (specific enough to not false-positive)
- No consumer touched by buggy round-2 tool yet — Round-3 port enters greenfield

### Top-3 inspection — surprises

User asked to inspect tx_peer_effects_local's top-3 worst-imbalance files for compound bugs (V1+V4 in same file).

**Compound bugs not found** in top-3. But three new findings instead, all logged in detail at `quality_reports/reviews/2026-05-23_stata-comment-bug-compound-inspection.md`:

1. **Naive grep balance is wildly inflated by V7 banners.** ALL 7 BDD unbalanced files have `delta == V7_count` exactly. 2 of top-3 tx_peer_effects_local offenders are also pure V7. The fleet's TRUE bug surface is dramatically smaller than the grep headlines.
2. **String-literal `/*` digraphs exist in real code.** generate_codebooks.do:1070 has `display "$outdir/*.txt"` — two `/*` inside a single string. State-machine handles via string-state protection; grep doesn't.
3. **`8A_Texas_Heatmaps.do` surfaces a new failure mode the plan doesn't handle.** Two `/*` openers at lines 119 and 306, no `*/` anywhere, V7=0 (no banner false-positive). Root cause: developer forgot the close marker, NOT greedy parser. Algorithm-walked prediction: sweep `--fix` silently mutates line 306 (`/*` becomes `/<x>`) and reports "1 transformation applied" — but the file remains broken. Real silent-failure risk.

### Plan revisions (third pass)

Folded three changes into `quality_reports/plans/2026-05-17_stata-comment-bug-universal-fix.md`:

1. `compute_balance` uses state-machine walker (not pure grep) — eliminates V7 + string-literal false positives. Test 7 + test 17 verify.
2. Sweep `--fix` adds MANUAL-ATTENTION classification for files with unmatched `/*` opens. `--check` reports them; `--fix` skips. Test 8 + test 12 verify.
3. Three new test fixtures: `variant_7_only.do`, `string_literal_glob.do`, `missing_close.do`.

Net effect: ~150 LOC, 14 files total (~1,600 LOC). Hook false-positive rate drops sharply. Sweep silent-mutation eliminated.

---

## Open items at end of Day 3

- [ ] Execution of the plan — three commits, deferred. User has approved the plan + revisions; pacing to be confirmed next session.
- [ ] Compound-bug fixture — deferred to Commit 2. Once V4 detector exists, run `--check` across fleet to surface real compound cases.
- [ ] Adversarial agent review (Layer 2) — optional now; Layer 1 (fleet preview) already closed the highest-risk gaps.
- [ ] Fixture pre-build (Layer 3) — also optional; the 3 new fixtures specified by the 2026-05-23 revision will be built as part of Commit 2.
- [ ] Run sweep `--check` on tx_peer_effects_local once Commit 2 lands — will reveal real bug surface (estimated 15-25 AUTO-FIXABLE + a few MANUAL-ATTENTION, NOT the 46 headline).

## Open items unrelated to this work (still outstanding)

- [ ] Extend `NEVER_SURNAMES` in `primary_source_lib.py` to absorb table-cell verbs (`New`, `Add`, `Extend`, `Fix`, `Edit`, etc.) — hit these as false positives 4+ times during this session's plan writing. Currently absorbed via escape hatches at top of plan + this session log. Sister TODO for unicode-fix proposal landing should batch with this fix.

---

## Day 3 — learnings

- **[LEARN:planning]** A plan that survives 2 revision passes is much stronger than one that ships on first draft. The fleet-preview Layer-1 validation alone added 3 substantive changes that would have caused silent failures in production. Always preview against real consumer codebases before committing to a multi-component infrastructure plan.
- **[LEARN:planning]** "Compound bugs" wasn't actually the most important class to look for. Inspecting the top-3 worst offenders surfaced 3 OTHER bug classes (V7 false positive, string-literal, missing-close) instead. Lesson: don't anchor too hard on the suspected risk; let the data tell you what's actually there.
- **[LEARN:hooks]** Naive grep balance checks have surprisingly high false-positive rate on real Stata codebases (~7×–14× inflation in BDD). State-machine balance is the only safe primitive for an edit-time gate. Cheap heuristics (subtract `//\*` count) catch most but miss string-literals.
- **[LEARN:planning]** A fix tool's `--fix` mode is dangerous if it can mutate files without producing a fixed post-state. The MANUAL-ATTENTION classification pattern (algorithm decides whether post-state would be balanced; only mutates if yes) is the right safety primitive. Generalizable beyond Stata.
- **[LEARN:primary-source-hook]** The primary-source-first audit hook produces frequent false positives on table-cell-start words (`New`, `Add`, `Extend`, etc.) followed by year-like strings (`2026-05-23`). Escape hatch works but generates noise. Already in TODO backlog as a high-priority fix; consider batching with the unicode-fix proposal.
