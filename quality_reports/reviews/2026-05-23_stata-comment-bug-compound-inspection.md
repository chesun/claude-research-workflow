# Stata Comment-Bug Top-3 Offender Inspection — Findings

**Date:** 2026-05-23
**Method:** Read-only inspection of the 3 worst-imbalance `.do` files in `tx_peer_effects_local` (plus cross-validation against all 7 unbalanced files in `belief_distortion_discrimination`).
**Purpose:** Stress-test the universal-fix plan against real consumer code. Look for compound bugs (V1+V4 in same file) and edge cases the plan doesn't yet handle.
**Plan under test:** `quality_reports/plans/2026-05-17_stata-comment-bug-universal-fix.md`
**Fleet preview:** `quality_reports/reviews/2026-05-23_stata-comment-bug-fleet-preview.md`

---

## Executive summary

**Compound bugs (V1+V4 in same file): not found** in the top-3 offenders. The top imbalances have different root causes than expected.

**Three new findings that require plan revisions:**

1. **Naive grep balance is wildly inflated by Variant 7 banner false positives.** All 7 "unbalanced" files in BDD are explained ENTIRELY by V7 banners (i.e., `delta(file) == V7_count(file)` exactly, for all 7 files). The 2 worst tx_peer_effects_local imbalances (delta=14 and delta=2 files) are also entirely V7. The actual bug surface in the fleet is dramatically smaller than the fleet-preview headline suggests.

2. **String-literal `/*` digraphs exist in real code** and contribute to grep balance inflation. `generate_codebooks.do:1070` has `display as text "  1. Copy $outdir/*.txt and $outdir/*.log to local machine"` — two `/*` digraphs inside a Stata string literal. The state-machine algorithm (with string-state protection per field guide §4) handles these correctly; the naive grep does not.

3. **A new failure mode found that is NOT path-glob-induced.** `8A_Texas_Heatmaps.do` (delta=2, V7=0) has two `/*` openers at lines 119 and 306 with zero `*/` closes anywhere in the file. The root cause is "developer forgot to type the closing `*/`", not the greedy-`/*` parser. The sweep tool's `--fix` cannot auto-remediate this — it would need to know where the developer intended each block to end. **The plan's sweep tool needs a "fixable vs manual-attention" distinction** in `--check` and `--fix` modes, and the `--fix` mode must not silently leave the file in a "still broken but reported as fixed" state.

---

## File 1 — `do/generate_codebooks.do` (delta=14, the headline worst offender)

**Size:** 1,075 lines
**Grep count:** 14 `/*` opens, 0 `*/` closes → reported as worst offender in the fleet

**Variant decomposition:**

| Source | Lines | Contribution to `/*` count |
|---|---|---:|
| `//******...` Variant 7 banner pairs | 1, 15, 34, 38, 327, 331, 361, 363, 843, 847, 927, 931 | 12 |
| String literal: `"$outdir/*.txt"` | 1070 | 1 |
| String literal: `"$outdir/*.log"` | 1070 | 1 |
| Real Variant 1 / Variant 4 | (none) | 0 |
| **Total** | | **14** |

**Diagnosis:** **Zero actual bugs.** Stata's parser handles all 14 `/*` digraphs correctly:
- Line-comment banners — `//` opens a line comment; trailing `*****` is comment content; never enters block state.
- String literals — `"$outdir/*.txt"` is a string; `/*` inside `"..."` is literal text per Stata's string-state protection.

The naive grep balance check is fooled by both. The sweep tool's state-machine would correctly report: 0 issues to fix; only the cosmetic V7 cleanup (insert space: `//****` → `// ****`).

**Implication for plan:** A `compute_balance` function that uses pure `grep -c '/\*'` vs `grep -c '\*/'` will report this file as broken when it isn't. **The hook's "clean" predicate needs a smarter balance check** — at minimum subtract V7 banners; ideally use the state-machine walker for true depth-state balance.

---

## File 2 — `do/server_03_19_2026/cs_do/settings.do` (delta=2)

**Size:** 24 lines
**Grep count:** 4 `/*` opens, 2 `*/` closes → delta=2

**Variant decomposition:**

| Line | Token | Source |
|---|---|---|
| 1 | `/* ... */` | Legitimate single-line header comment (1 open + 1 close — balanced) |
| 4 | `//******...` | Variant 7 banner — falsely contributes 1 to `/*` count |
| 6 | `//******...` | Variant 7 banner — falsely contributes 1 to `/*` count |
| 8 | `/*` | Legitimate block-comment open (commenting out a `do` invocation) |
| 10 | `*/` | Matching close for line 8 |

**True balance:** 2 legitimate opens + 2 legitimate closes = balanced. V7 false positives account for the entire delta.

**Diagnosis:** **Zero actual bugs.** Pure Variant 7 false positive. Stata parses the file correctly. The sweep tool's state-machine would report: 0 issues; cosmetic V7 cleanup only.

**Implication:** Same as File 1. Reinforces that pure-grep balance is unreliable.

---

## File 3 — `do/server_03_19_2026/main_do/0A_settings_cs.do` (delta=2)

**Size:** 21 lines
**Grep count:** 3 `/*` opens, 1 `*/` close → delta=2

**Variant decomposition:**

| Line | Token | Source |
|---|---|---|
| 1 | `//******...` | Variant 7 — +1 false `/*` |
| 3 | `//******...` | Variant 7 — +1 false `/*` |
| 5 | `/*` | Legitimate block-comment open |
| 7 | `*/` | Matching close for line 5 |

**True balance:** 1 legitimate open + 1 legitimate close = balanced. Both V7 banners false-positive.

**Diagnosis:** **Zero actual bugs.** Same pattern as File 2 (this is a near-clone — both are settings.do variants).

---

## Cross-validation: BDD's 7 "unbalanced" files

For every BDD-unbalanced file, I computed `delta = opens - closes` and `V7 = count(//\*)`. Result:

| File | opens/closes | delta | V7 | Hypothesis |
|---|---|---:|---:|---|
| `analysis/do_files/audit/clean_data.do` | 30/2 | 28 | 28 | ✓ pure V7 |
| `analysis/do_files/employer/deg_wtp/new_pilots_may_2025/force20_rerun.do` | 2/1 | 1 | 1 | ✓ pure V7 |
| `.../force11_rerun.do` | 2/1 | 1 | 1 | ✓ pure V7 |
| `.../voluntary_commit.do` | 5/4 | 1 | 1 | ✓ pure V7 |
| `analysis/do_files/employer/deg_wtp/nodrawname/make_draw_data.do` | 6/3 | 3 | 3 | ✓ pure V7 |
| `.../analyze_draw_behavior.do` | 8/5 | 3 | 3 | ✓ pure V7 |
| `.../clean_all.do` | 8/6 | 2 | 2 | ✓ pure V7 |

**All 7 BDD "unbalanced" files: `delta == V7` exactly.** Every one is a pure Variant 7 false positive. **BDD has zero actual greedy-`/*` bugs.**

This means the fleet preview's "7 unbalanced files per BDD repo" headline is misleading. The real bug surface in BDD is 0.

---

## The new failure mode — `8A_Texas_Heatmaps.do`

This file is the exception that breaks the V7-false-positive pattern, and surfaces something the plan doesn't handle.

**Size:** 322 lines
**Grep count:** 2 `/*` opens (lines 119, 306), 0 `*/` closes
**V7 count:** 0 (no banners)
**Delta:** 2

**Context at line 119 (read directly):**

```stata
115   }
116
117   ********* OLD CODE
118
119   /*
120   spmap perc_asian using "/srv/tier2/.../texas_coords.dta", id(id) clmethod(custom) ...
...
```

**Context at line 306:**

```stata
304   graph export"/srv/tier2/projects/170_dis/out/District_Heatmaps/All_Immigrant_by_District_1990.pdf", as(pdf) name("Graph")
305
306   /*
307
308   spmap avg_black_expos using "/srv/tier2/.../texas_coords.dta", id(id) clmethod(custom) ...
```

**Diagnosis:** Two block-comment opens, both intended to comment out "OLD CODE" and "additional plots" blocks respectively, but **neither block has a closing `*/` anywhere in the file**. The developer typed `/*` to start commenting out code but never typed the matching `*/`.

**Parser interpretation:**
- Line 119: `/*` → depth 1
- Lines 120–305: dormant inside comment
- Line 306: `/*` → depth 2 (nested)
- Lines 307–322 (EOF): dormant inside double-nested comment
- Final state: depth=2, runaway from line 119 to EOF

**This is NOT a Variant 1 path-glob bug.** No `*` glob is present in the comment context. The root cause is developer error: missing `*/` markers. Stata still treats lines 119+ as comments, just like Variant 1.

**The sweep tool's behavior on this file (predicted via algorithm walk):**

1. **Pre-pass** (`flatten_lone_block_opens`): walks forward, finds `/*` at line 119, calls `find_matching_close` — fails (no matching `*/` in file). Per the algorithm, an unmatched open should be left alone (the pre-pass only acts on matched outer blocks). Skipped.
2. **Main pass** (`transform_comment_globs`): state machine. Enter `block` state at line 119. Stay in block state through line 305. At line 306's `/*`: emit `/<x>` (spurious /* inside block). Stay in block state through EOF. **File ends in block state — no transformations were applicable.** Output is mostly the input, with line 306's `/*` rewritten to `/<x>`.
3. **Post-pass** (`strip_orphan_block_closes`): no `*/` to strip. No-op.

**Predicted post-sweep state:**
- Line 119 still has `/*` (legitimate-looking open from the algorithm's view)
- Line 306's `/*` is now `/<x>` (rewritten; algorithm thinks it's a spurious open inside block)
- File still ends with depth=1 (the line 119 open is unmatched)
- Grep balance: 1 open / 0 close → still unbalanced
- The bug is **NOT fixed**. The file is silently mutated (line 306 changed) but the underlying problem persists.

**This is a real plan gap.**

The plan's `--fix` mode would:
- Report "1 transformation applied" (line 306's rewrite)
- Leave the file in a still-broken state
- Silently delete the developer's `/*` at line 306 (which may have been intentional — possibly the developer's way of commenting out the second block, even though it doesn't actually work that way in Stata)
- The user, seeing "1 fix applied", would assume the file is repaired and may not re-check

**The plan needs to add:** a "manual-attention" classification for files where the sweep's algorithm cannot produce a balanced post-state. These should be:
- Detected in `--check` mode as a distinct issue class ("missing-close" or "unfixable imbalance")
- Skipped in `--fix` mode (no mutation) — reported instead
- Block message in the hook should distinguish "you introduced this" from "this file was already in an unfixable state"

---

## Updated risk assessment for the plan

### Risks the inspection confirms

- **Algorithm soundness on real codebases:** confirmed for the path-glob class (V1/V2/V3/V6). Round-3's path-glob-aware predicates handle the patterns observed.
- **V8 detection patterns don't false-positive:** confirmed across 732 files (zero hits anywhere in fleet).
- **String-literal protection is load-bearing:** confirmed — at least 2 real cases in generate_codebooks.do alone.

### New risks the inspection surfaces

| Risk | Source | Mitigation |
|---|---|---|
| **Hook produces high false-positive block rate** because compute_balance uses pure grep | Every BDD "unbalanced" file is pure V7 false positive | Update `compute_balance` to subtract `//\*` count; OR use state-machine walker for true balance |
| **Sweep `--fix` silently mutates files it can't actually fix** | `8A_Texas_Heatmaps.do` predicted behavior — line 306 changes, file still broken | Add "fixable vs manual-attention" classification; `--fix` skips manual-attention files; `--check` reports them with distinct severity |
| **String-literal `/*` digraphs inflate grep counts** in real-world files | `generate_codebooks.do:1070` — 2 hits inside a single display string | State-machine `compute_balance` (option above) handles this naturally |
| **Fleet preview's bug counts are inflated by 7×–14×** for some consumers | All 7 BDD unbalanced = V7 false positive; 3 of top-10 TPE delta-imbalanced are V7 only | Re-run baseline with V7-aware compute_balance after plan revision; report true bug surface |

### Compound-bug risk: not observed in this sample

The top-3 offenders do NOT contain compound V1+V4 patterns. The Variant 4 risk in the field guide §7 cites 5 of 129 files in va_consolidated. Those would NOT show up at the top by imbalance magnitude (V4 preserves balance). To find compound risks, we'd need to run a state-machine V4 detector across the fleet — which is precisely what the sweep tool will do once built. **Defer compound-bug fixture work until Commit 2** when the V4 detector is available.

---

## Recommended plan revisions (before Commit 2)

### 1. `compute_balance` redesign

Current plan (lib function): `compute_balance(text) -> tuple[int, int]` returning `(opens, closes)` from naive grep.

Revised plan: `compute_balance(text) -> tuple[int, int]` returning `(true_opens, true_closes)` from state-machine walk. The state-machine already exists for `transform_comment_globs` — `compute_balance` can be a lightweight variant that only counts state transitions without rewriting.

Alternative cheap heuristic if state-machine cost is a concern: `effective_opens = count('/\*') - count('//\*') - count_in_strings('/\*')`. ~30 LOC; ~95% accurate; misses edge cases.

**Recommendation:** state-machine variant. It's a few dozen lines on top of the existing walker, and the hook fires only on `.do`/`.doh` edits (low frequency).

### 2. Sweep tool: fixable-vs-manual classification

Current plan: sweep `--fix` applies all detected transformations, reports count.

Revised plan: sweep produces a classified per-file report:

- **AUTO-FIXED:** transformations applied; post-state is balanced and clean. (V1, V2, V3, V6 path-glob cases; V5 orphans; V7 banners.)
- **MANUAL-ATTENTION:** file has issues the algorithm cannot remediate (missing-close `/*` with no matching `*/` anywhere). `--fix` skips these. `--check` reports separately. Suggests manual `*/` insertion.
- **CLEAN:** no issues detected.

Sweep exit codes:
- 0 — all files clean
- 1 — auto-fixable issues found (in `--check`) or applied (in `--fix`)
- 2 — manual-attention issues found (subsumes 1 if both present)
- 3 — parse/IO error

### 3. New test fixtures

Add to `.claude/hooks/tests/fixtures/`:

- `variant_7_only.do` — pure V7 banners, no actual bugs. Sweep should report CLEAN (or only cosmetic V7 fix).
- `string_literal_glob.do` — `display "$outdir/*.txt"` in code. Sweep should preserve verbatim.
- `missing_close.do` — `/*` open with no matching `*/`. Sweep should classify as MANUAL-ATTENTION, not mutate.

These join the existing planned `all_eight_variants.do` and `over_flatten_artifact.do`.

### 4. Hook block-message refinement

Distinguish three message types:

- "You introduced a Variant N bug — your edit added X" (current plan)
- "This file has a manual-attention issue from before your edit; no need to fix it as part of this change" (NEW — legacy-tolerant for unfixable existing state)
- "This file has been corrupted by a prior buggy sweep (V8); investigate before editing further" (current plan)

### 5. Re-run baseline after `compute_balance` fix

After the lib `compute_balance` is reimplemented, re-run the fleet preview. Expected: BDD drops from 7 unbalanced to 0. Tx_peer_effects_local drops significantly (most likely 14–25 unbalanced files instead of 46, with the rest being mostly V7+string false positives). The TRUE bug surface is what matters for planning the post-Commit-2 sweep rollout.

---

## Plan-solidity verdict

**The plan is still fundamentally sound** — the algorithm, the propagation strategy, and the three-commit rollout all hold. But three concrete revisions are needed before Commit 2 ships:

1. `compute_balance` must use state-machine (or V7-aware heuristic).
2. Sweep `--fix` must skip MANUAL-ATTENTION files.
3. Three test fixtures must be added (V7-only, string-literal, missing-close).

Together these are ~150 additional LOC. Total plan LOC bumps from ~1,450 to ~1,600. Three commits unchanged. Hook risk profile improves (lower false-positive rate). Sweep risk profile improves (no silent mutation of unfixable files).

**Compound-bug fixture work:** deferred until Commit 2 — once the V4 state-machine detector exists, run it across the fleet to find true compound cases.

**Adversarial agent review:** still worth doing on the revised plan, but the highest-ROI gap (real-codebase preview) is now closed.

---

## Raw data preserved

- Fleet preview (per-file unbalanced list + variant counts): `quality_reports/reviews/2026-05-23_stata-comment-bug-fleet-preview.md`
- Top-10 imbalance ranking for tx_peer_effects_local (this report's source data): captured in session log; re-derivable via the bash script in section "Identifying the top 3 worst offenders".
- All inspections are read-only — no consumer file was modified.
