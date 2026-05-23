<!-- primary-source-ok: new_2026, add_2026, added_2026, extend_2026, extended_2026, edit_2026, edited_2026, fix_2026, fixed_2026, port_2026, ported_2026, drop_2026, dropped_2026, revise_2026, revised_2026, defer_2026, deferred_2026, real_2026, mixed_2026, expect_2026, change_2026, changed_2026, none_2026, both_2026, three_2026, two_2026, one_2026, pure_2026, after_2026, before_2026, includes_2026, mirrors_2026, must_2026, should_2026 -->
# Universal Fix: Stata Block-Comment Greedy `/*` Bug

**Status:** APPROVED, REVISED 2026-05-23 (compute_balance + manual-attention + extra fixtures, from fleet inspection)
**Date:** 2026-05-17 (initial), revised 2026-05-18 (V8), revised 2026-05-23 (post-fleet-inspection)
**Scope:** workflow source repo + propagation to all 7 consumers
**Estimated effort:** ~1,600 LOC new code + tests, 3 atomic commits, 1 propagate cycle per commit
**Mirror:** `~/.claude/plans/now-another-urgent-item-peaceful-creek.md` (plan-mode write; superseded by this file)

---

## Revision history

- **2026-05-17** — Initial plan covering Variants 1 through 7 (7-variant taxonomy)
- **2026-05-18** — Variant 8 included. Library function inventory grew with `_is_path_glob_open`, `_is_path_glob_close`, `_rewrite_inner_block_markers`. Lib LOC ~350 to ~450. Test LOC ~500 to ~600. Hook "clean" predicate now incorporates V8 artifact detection.
- **2026-05-23** — Three revisions from fleet inspection (see `quality_reports/reviews/2026-05-23_stata-comment-bug-compound-inspection.md`):
  1. **`compute_balance` should use the state-machine walker, not pure grep.** All 7 BDD "unbalanced" files are pure Variant 7 false positives (`delta == V7_count` exactly). 2 of top-3 tx_peer_effects_local offenders are also pure V7. String-literal `/*` digraphs (e.g., `display "$outdir/*.txt"`) also inflate grep counts. Naive grep produces high false-positive block rate in the hook.
  2. **Sweep `--fix` should add MANUAL-ATTENTION classification** for files where the algorithm cannot produce a balanced post-state. Discovered `8A_Texas_Heatmaps.do`: two `/*` openers with no matching `*/` anywhere — root cause is "developer forgot the close marker", not greedy parser. Algorithm-walked prediction shows `--fix` would silently mutate the file (line 306 `/*` becomes `/<x>`) and leave it broken, reporting "1 transformation applied." Real silent-failure risk.
  3. **Three additional test fixtures.** `variant_7_only.do` (pure V7 — should report CLEAN), `string_literal_glob.do` (`display "$outdir/*.txt"` — should preserve verbatim), `missing_close.do` (mirrors `8A_Texas_Heatmaps.do` — should classify MANUAL-ATTENTION, not mutate).

Net effect of the 2026-05-23 revision: roughly +150 LOC (~1,450 to ~1,600). Hook false-positive rate drops sharply. Sweep silent-mutation risk eliminated.

---

## Context

**The bug.** Stata's parser counts `/*` opens **greedily** regardless of comment context. A path-glob like `prepare/*` inside a `*`-line comment, `//`-line comment, or `/* ... */` block header silently opens a runaway nested block comment that swallows everything down to the next stray `*/` (often EOF). Symptoms: scripts log "end of do-file" without errors but produce no outputs; per-file `.smcl` logs go missing; downstream pipelines fail several scripts later when an expected input doesn't exist.

**Empirical scale.** In `~/github_repos/va_consolidated` (applied-micro project, 129 active `.do`/`.doh` files), 89 of 129 files (69%) had unbalanced `/*` vs `*/` counts before the sweep. The 6,588-line master log showed every nested `do` reaching "end of do-file" with zero "file saved" messages — the pipeline reported success while producing no outputs. Variant 4 (fake-nested blocks) affected 5 files where a naive fix would have silently activated dormant code, changing saved variable values. Variant 8 (the round-2 over-flatten trap, discovered 2026-05-18) was triggered by the round-2 fix tool itself on 2 files (`secqoiclean1415.do`, `secqoiclean1617.do`) whose outer headers contained path-glob substrings (`$logdir/*`, `$datadir/*`).

**Fleet preview validation (2026-05-23).** Read-only grep against all 7 consumers (732 .do/.doh files total) confirmed:
- va_consolidated reports 0 issues post-Round-3 (idempotence guarantee).
- tx_peer_effects_local: 297 files, 46 grep-unbalanced (but many are V7 false positives; true bug surface smaller).
- BDD and BDD-audit: 7 grep-unbalanced each — all pure Variant 7 false positives (`delta == V7_count` for every file).
- csac: 46 files, 3 grep-unbalanced.
- bdm_bic, csac2025: clean.
- Zero Variant 8 artifacts anywhere in the fleet (no consumer has been touched by a buggy round-2-equivalent tool). The Round-3 port becomes the first state-machine sweep these files will see.

**Why universal.** The bug is project-agnostic. The 8-variant taxonomy, the 3-pass state-machine fix with path-glob-aware predicates, and the two convention rules (no `*` glob in comments; commit-time balance check) all generalize. Every consumer using Stata is at risk. Reference implementation already exists at `~/github_repos/va_consolidated/py/sweep_comments_and_logdirs.py` (Round 3, 2026-05-18, ~750 LOC) and was validated by three rounds of coder-critic review.

**Intended outcome.** Ship three artifacts into the workflow that propagate to all 7 consumers via existing Class A propagation:

1. A sweep tool to detect and fix the bug across an existing codebase. The workflow's port starts at Round 3 from day one — no replay of round-1 narrow-regex or round-2 over-flatten bugs. Includes MANUAL-ATTENTION classification (per 2026-05-23 revision) so unfixable files are reported, not silently mutated.
2. A PreToolUse hook to block edits that introduce the bug going forward. `compute_balance` uses state-machine (not naive grep) to eliminate Variant 7 and string-literal false positives. Includes Variant 8 artifact detection.
3. Convention rules, critic deductions, and skill callouts so authors and reviewers know the pattern.

The field guide at `master_supporting_docs/stata-block-comment-bug-field-guide.md` (8 variants, last updated 2026-05-18) is the source of truth and propagates as Class A by default.

---

## Approach (one-paragraph summary)

Port Round 3 of `sweep_comments_and_logdirs.py` T1 to `.claude/skills/tools/stata_sweep.py` (drops T2 log-dir mirroring as va_consolidated-specific). Extract the state-machine state into `.claude/hooks/stata_comment_lib.py` shared with a new `.claude/hooks/stata-comment-balance-check.py` PreToolUse hook that mirrors `primary-source-check.py`'s structure. Critical Variant 8 prevention: both the depth-counted matcher and the inner rewriter use path-glob-aware predicates (`_is_path_glob_open`, `_is_path_glob_close`). Critical false-positive prevention (2026-05-23): `compute_balance` uses the state-machine walker, not pure grep — eliminates V7 banner and string-literal false positives that the fleet inspection showed inflate the grep imbalance count 7x to 14x on real consumer files. Sweep `--fix` includes a MANUAL-ATTENTION classification for files the algorithm can't auto-remediate (e.g., missing-close `/*` with no `*/` anywhere): these are reported, not silently mutated. Adds deduction rows to `coder-critic.md`, a "Comment Safety" section to `stata-code-conventions.md`, a callout to the stata `SKILL.md`, and a `/tools stata-sweep` subcommand entry. Stages the rollout into three commits so the hook lands last.

---

## File-by-file deliverables

### Commit 1 — Documentation and rules (no behavior change; safe to roll out first)

| File | Action | LOC | Notes |
|---|---|---:|---|
| `.claude/rules/stata-code-conventions.md` | Extend | +30 | Adds "Comment Safety" subsection. Adopts Rules 1 and 2 verbatim from field guide section 5. |
| `.claude/skills/stata/SKILL.md` | Extend | +12 | Adds "Common Pitfalls — Greedy `/*` Parser Bug" callout. Names the bug for grep, links to field guide. Mentions all 8 variants. |
| `.claude/agents/coder-critic.md` | Extend | +10 | Deduction rows in category 4: unbalanced `/*` vs `*/` = -25 Critical (verified via state-machine, not naive grep — see compute_balance below); `*` glob in any comment context = -5 per occurrence (cap -25) Major; Variant 8 artifacts present = -25 Critical. References field guide. |
| `.claude/file-classes.toml` | Extend | +1 | Adds explicit `master_supporting_docs/*.md` to `[universal]` for deterministic propagation. |
| `master_supporting_docs/stata-block-comment-bug-field-guide.md` | Edit | +0/-1 | Updates section 8 reference from `va_consolidated/py/sweep_comments_and_logdirs.py` to `.claude/skills/tools/stata_sweep.py`. Notes: "the workflow port starts at Round 3 from day one." |

### Commit 2 — Library, sweep tool, tests (medium risk; opt-in execution)

| File | Action | LOC | Notes |
|---|---|---:|---|
| `.claude/hooks/stata_comment_lib.py` | NEW | ~500 | Shared state-machine. Function inventory (Round 3 plus 2026-05-23 revisions): `_is_path_glob_open(text, i) -> bool` (V8 predicate — open), `_is_path_glob_close(text, i) -> bool` (V8 predicate — close), `find_matching_close(text, open_end) -> int` (path-glob aware), `_rewrite_inner_block_markers(inner) -> str` (context-aware inner rewriter; replaces blanket `inner.replace(...)`), `flatten_lone_block_opens(text)` (V4 pre-pass; delegates to rewriter), `transform_comment_globs(text)` (V1, V2, V3, V6 main pass), `strip_orphan_block_closes(text)` (V5 post-pass), `compute_balance(text) -> tuple[int, int]` (state-machine walker; returns TRUE balance after filtering V7 banners plus string-literal contents — NOT naive grep), `has_glob_in_line_comment(text) -> list[tuple[int, str]]`, `find_over_flatten_artifacts(text) -> list[tuple[int, str]]` (V8 grep: `^-+<x>$` and `^\s*<x>\s*$`), `classify_file(text) -> Literal["clean", "auto-fixable", "manual-attention"]` (2026-05-23 inclusion; runs the algorithm and decides whether post-sweep state would be balanced; manual-attention iff there's a `/*` open with no reachable matching `*/`), `sweep_text(text)` orchestrator. Stdlib-only Python 3.11+. Mirrors `primary_source_lib.py` placement convention. |
| `.claude/skills/tools/stata_sweep.py` | NEW | ~320 | CLI wrapper. Imports lib via `importlib.util`. Args: `--root PATH` (default cwd), `--exclude PATTERN...` (default `_archive`), `--check` (default, no-fix, exits 1/2/3 by class), `--fix` (mutates auto-fixable files only; MANUAL-ATTENTION files are skipped and reported), `--diff`, `--json`, positional `FILE...` overrides directory walk. Per-file classification report: AUTO-FIXED, MANUAL-ATTENTION, CLEAN. Variant 8 artifacts trigger a distinct message. Exit codes: 0 = all clean, 1 = auto-fixable issues found (check) or applied (fix), 2 = manual-attention issues found (subsumes 1), 3 = parse/IO error. |
| `.claude/hooks/test_stata_comment_lib.py` | NEW | ~700 | Stdlib `unittest`, mirrors `test_primary_source_lib.py`. Classes: `TestFindMatchingClose` (V8 regression — path-glob in outer header doesn't inflate depth), `TestPathGlobPredicates` (positive and negative for `_is_path_glob_open`/`_close`), `TestRewriteInnerBlockMarkers` (context-aware rewriter preserves path-globs and legitimate body markers), `TestFlattenLoneBlockOpens` (regression for round-1 narrow-regex bug and round-2 over-flatten bug mirroring `secqoiclean1415.do`'s pattern), `TestTransformCommentGlobs`, `TestStripOrphanBlockCloses`, `TestFindOverFlattenArtifacts`, `TestComputeBalance` (2026-05-23 inclusion: pure V7 banner file returns balanced; string-literal `/*` returns balanced; real V1 bug returns unbalanced), `TestClassifyFile` (2026-05-23 inclusion: pure V7 to CLEAN; real V1 path-glob to AUTO-FIXABLE; missing-close `/*` to MANUAL-ATTENTION), `TestSweepText` (end-to-end on a fixture with all 8 variants), `TestHookSimulation` (legacy-tolerant vs strict modes; V8 artifacts trigger block; manual-attention files don't trigger NEW-bug block but do trigger informational message). |
| `.claude/hooks/tests/fixtures/all_eight_variants.do` plus `.expected.do` | NEW | ~95 each | Synthetic fixture covering all 8 variants. Includes V8 risk pattern. Expected output asserts: legitimate body block markers remain `*/`, not `<x>`. |
| `.claude/hooks/tests/fixtures/over_flatten_artifact.do` | NEW | ~30 | Negative fixture: file already corrupted by hypothetical buggy round-2 tool. |
| `.claude/hooks/tests/fixtures/variant_7_only.do` | NEW 2026-05-23 | ~20 | Pure V7 banners (mirrors BDD's `clean_data.do` and tx_peer_effects_local's `cs_do/settings.do` patterns). Sweep `--check` reports CLEAN (no auto-fixable issues; cosmetic V7 cleanup at most). Validates `compute_balance` doesn't false-positive. |
| `.claude/hooks/tests/fixtures/string_literal_glob.do` | NEW 2026-05-23 | ~15 | Real-world pattern: `display as text "Copy $outdir/*.txt and $outdir/*.log to local"`. Sweep preserves the string verbatim. Validates string-state protection in `compute_balance` and main pass. |
| `.claude/hooks/tests/fixtures/missing_close.do` | NEW 2026-05-23 | ~40 | Mirrors `8A_Texas_Heatmaps.do`: two `/*` openers (lines ~20 and ~30) with no `*/` anywhere. Sweep `--check` classifies as MANUAL-ATTENTION; `--fix` does NOT mutate (and reports). Validates the new classification logic. |
| `.claude/skills/tools/SKILL.md` | Extend | +60 | `/tools stata-sweep` subcommand. Documents modes, exit codes (0/1/2/3), classification (CLEAN/AUTO-FIXED/MANUAL-ATTENTION), V8 artifact detection. |
| `templates/git-hooks/pre-commit-stata-balance` | NEW | ~50 | Opt-in shell template. Uses sweep tool's `--check` (not naive grep) for accurate balance assessment. |

### Commit 3 — Hook activation (highest risk; blocks edits going forward)

| File | Action | LOC | Notes |
|---|---|---:|---|
| `.claude/hooks/stata-comment-balance-check.py` | NEW | ~220 | PreToolUse hook. Matchers: `Edit\|Write\|MultiEdit`. Internal suffix check on `.do`/`.doh`. "Clean" predicate (revised 2026-05-23): uses `compute_balance` state-machine walker (NOT naive grep) AND zero line-comment glob hits AND zero V8 artifact hits AND not classified MANUAL-ATTENTION-new. Decision: `pre is None` to strict; `pre exists` to legacy-tolerant. Three message types: (a) "you introduced Variant N", (b) "file already had MANUAL-ATTENTION issue from before your edit; not your fault, but flagged", (c) "V8 corruption detected; investigate before editing". Fail-open on internal exception. |
| `.claude/settings.json` | Edit | +6 | Appends hook entry; adds `MultiEdit` matcher. |

**Total: 14 files (three new fixtures from 2026-05-23 revision). Total LOC: ~1,600 (~1,100 code, ~500 tests/fixtures).**

---

## Test plan

### Unit (Commit 2 verifies before merge)

1. `python3 -m unittest .claude/hooks/test_stata_comment_lib.py` — all classes pass. Coverage target: at least 95% of `stata_comment_lib.py`.
2. Each variant (1 through 8) has positive and negative cases. String-literal protection tested explicitly.
3. Idempotence test: `sweep_text(sweep_text(text)[0])[0] == sweep_text(text)[0]`.
4. V4 regression: `/* <text>\n /* inner */\n code\n*/` — pre-pass flattens both inner tokens.
5. V8 regression: fixture matching `secqoiclean1415.do` shape — depth counter doesn't overshoot; legitimate body `/* note */` retains `*/`; path-glob `$logdir/*` is rewritten only by main pass.
6. Path-glob predicates: `_is_path_glob_open("/*", 0)` = False; `_is_path_glob_open("a/*", 1)` = True; etc.
7. `compute_balance` (2026-05-23 inclusion):
   - `variant_7_only.do` fixture returns `(N, N)` (balanced) despite naive grep reporting `(N+banners, N)`.
   - `string_literal_glob.do` fixture returns `(N, N)` despite naive grep over-counting.
   - Real V1 fixture returns unequal counts.
8. `classify_file` (2026-05-23 inclusion):
   - Pure V7 to CLEAN
   - Real V1 path-glob to AUTO-FIXABLE
   - Missing-close `/*` (no `*/` anywhere) to MANUAL-ATTENTION

### Integration (Commit 2 verifies post-merge, before Commit 3)

9. `--check --root ~/github_repos/va_consolidated/do` to exit 0, all CLEAN.
10. `--check --root ~/github_repos/belief_distortion_discrimination` to TRUE bug surface, much smaller than fleet-preview headline (per 2026-05-23 inspection: BDD's 7 grep-unbalanced are all V7 false positives; expected outcome: 0 issues after state-machine balance).
11. `--check --root ~/github_repos/tx_peer_effects_local` to mixed report: some files AUTO-FIXABLE (real V1), some MANUAL-ATTENTION (8A_Texas_Heatmaps.do shape), some CLEAN (V7-only).
12. `--fix --root .claude/hooks/tests/fixtures` then `diff all_eight_variants.do all_eight_variants.expected.do` is byte-identical. Critical: `missing_close.do` UNCHANGED in `--fix` mode.
13. Negative V8 fixture: `--check over_flatten_artifact.do` is exit 1, "miscorrected; see V8".

### Hook integration (Commit 3 verifies post-merge)

14. 18 PreToolUse JSON payloads (8 variants by {introduce, repair} plus 2 V7-banner cases). Assert: V1 introductions block; V7 introductions DON'T block (compute_balance is V7-aware); repairs allowed; manual-attention legacy state allowed.
15. Smoke: V1 introduction blocks; replacing with `<x>` allows.
16. V8 hook smoke: synthesize `^------<x>$` to next Edit blocked.
17. V7 hook smoke (2026-05-23 inclusion): introducing `//****` banner to a clean file is NOT blocked (compute_balance subtracts V7).
18. Manual-attention legacy smoke (2026-05-23 inclusion): editing `missing_close.do` shape; the edit doesn't change the manual-attention state is allowed with informational message.

### Acceptance bar

- All 18 tests pass.
- Sweep on va_consolidated: 0 issues, 0 V8.
- Sweep on BDD: TRUE balance check returns at most 1 issue (expected: 0; the 7 grep-unbalanced files are V7 false positives that compute_balance correctly classifies as clean).
- One real Edit on a va_consolidated `.do` doesn't block.
- Hook V7 smoke (test 17) doesn't false-positive.

---

## Rollout sequence

Each commit: push to `origin/main` to `python3 .claude/skills/tools/propagate.py <files>` to `python3 .claude/skills/tools/sync_overlays.py` to push consumer commits.

| Commit | Risk | Verification gate |
|---|---|---|
| 1. Docs, rules, critic | Low | `/tools sync-status` clean on all consumers. Field guide propagated. |
| 2. Lib, sweep, tests, template | Medium | Tests 1 through 13 pass. Sweep `--check` on va_consolidated: 0 issues. Sweep on BDD: TRUE balance shows at most 1 issue (validates compute_balance fix). |
| 3. Hook, settings.json | High | Tests 14 through 18 pass. Real Edit on clean `.do` doesn't block. V7 banner inclusion (test 17) doesn't block. |

Pacing decision pending — user asked for plan-first; pacing confirmed in a later session.

---

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Hook false-positive blocks legitimate edit on a legacy-buggy file | Legacy-tolerant mode; fail-open on exception. |
| Hook false-positive from naive grep (V7 banners / string literals) | 2026-05-23: `compute_balance` uses state-machine walker, not pure grep. Test 7 plus test 17 verify. |
| `importlib.util` cross-dir load breaks on path edge cases | Absolute path resolution; unit test asserts lib loads. |
| `--fix` mutates unexpected files (cwd confusion) | `--root` defaults to cwd; prints resolved path; refuses uncommitted-changes files without `--force`. |
| `--fix` silently mutates files it can't actually fix (`8A_Texas_Heatmaps.do` shape) | 2026-05-23: MANUAL-ATTENTION classification. `--fix` skips these files; `--check` reports separately. Test 8 plus test 12 verify. |
| Variant 4 introduced via Claude Edit goes undetected | Documented gap. Coder-critic catches in review. Sweep catches on next run. |
| Sweep tool itself introduces Variant 8 (round-2 over-flatten trap) | Path-glob-aware predicates from Round 3 onwards. Tests 5 plus 6 are dedicated regression tests. Sweep on va_consolidated post-port: 0 V8 artifacts. |
| Future buggy round-2-equivalent tool corrupts files; balance check still passes | Hook's "clean" predicate explicitly checks for V8 artifact patterns. Coder-critic adds -25 deduction. Sweep `--check` reports distinctly. |
| Consumer with existing unbalanced files sees hook noise | Legacy-tolerant mode plus V7-aware compute_balance prevents this. Each consumer runs `/tools stata-sweep --check` for true baseline. |
| Hook lands before lib (propagation order failure) | Three-commit sequencing. |
| Test fixture `.do` files trigger coder-critic deductions | Fixtures under `.claude/hooks/tests/fixtures/`, not under `do/` or `scripts/stata/`. |
| MultiEdit not in matcher | Matcher: `Edit\|Write\|MultiEdit`. Confirmed in test 14. |
| Compound bugs (V1+V4 in same file) not discovered in top-3 inspection but may exist in fleet | 2026-05-23: deferred until Commit 2 — once V4 detector exists, run `sweep --check` across fleet to surface compound cases. Add compound fixture if real cases found. |

---

## Critical files for implementation

**Reference (read-only):**

- `~/github_repos/va_consolidated/py/sweep_comments_and_logdirs.py` — Round 3 (2026-05-18). Ports T1 from this.
- `master_supporting_docs/stata-block-comment-bug-field-guide.md` — source of truth for 8 variants.
- `.claude/hooks/primary-source-check.py` — pattern for the new hook.
- `.claude/hooks/primary_source_lib.py` — pattern for shared library.
- `.claude/hooks/test_primary_source_lib.py` — pattern for unit tests.
- `quality_reports/reviews/2026-05-23_stata-comment-bug-fleet-preview.md` — fleet baseline.
- `quality_reports/reviews/2026-05-23_stata-comment-bug-compound-inspection.md` — top-3 offender inspection plus revision rationale.

**To create or extend:** see file table above. 14 files total (12 plus 2 expected.do).

---

## What gets dropped from the va_consolidated reference

- Transform 2 (log-dir mirroring) — va_consolidated-specific.
- Hardcoded path anchors — `do/` root, `_archive`, `{main.do, settings.do}` skip list. Become CLI args or vanish with T2.
- va_consolidated-specific docstring references — to ADR-0021, project plans, internal reviews.
- No-args CLI — replaced with documented arg surface.
- Round-1 and Round-2 artifacts — port starts at Round 3.

---

## Out of scope (explicitly deferred)

- Auto-installation of the git pre-commit hook template.
- Variant 4 detection inside the PreToolUse hook (state-machine cost; sweep tool catches).
- CI integration (consumer-level decision).
- Retroactive sweep of consumer repos (each consumer's owner runs `--fix` on their own schedule).
- Compound-bug test fixture — deferred until Commit 2 sweep exposes real compound cases in the fleet.

---

## Verification (end-to-end)

After all 3 commits land:

```bash
# 1. Sweep tool tests pass
cd ~/github_repos/claude-code-my-workflow
python3 -m unittest .claude/hooks/test_stata_comment_lib.py

# 2. Sweep on va_consolidated (idempotence)
python3 .claude/skills/tools/stata_sweep.py --check --root ~/github_repos/va_consolidated/do
# expect: exit 0, 0 issues, 0 V8 artifacts

# 3. Explicit V8 grep (belt-and-suspenders)
grep -rnE '^-+<x>$' ~/github_repos/va_consolidated/do --include='*.do' --include='*.doh'
grep -rnE '^[[:space:]]*<x>[[:space:]]*$' ~/github_repos/va_consolidated/do --include='*.do' --include='*.doh'
# expect: both return 0

# 4. Sweep on BDD (state-machine balance — TRUE bug surface)
python3 .claude/skills/tools/stata_sweep.py --check --root ~/github_repos/belief_distortion_discrimination
# expect: 0 issues (per 2026-05-23 inspection, all 7 grep-unbalanced files are pure V7)

# 5. Sweep on tx_peer_effects_local (mixed report)
python3 .claude/skills/tools/stata_sweep.py --check --root ~/github_repos/tx_peer_effects_local
# expect: mix of AUTO-FIXABLE plus MANUAL-ATTENTION; 8A_Texas_Heatmaps.do classified MANUAL-ATTENTION

# 6. Hook live test
cd ~/github_repos/va_consolidated/do
# Edit a .do file: introduce `* prepare/*` to a comment, blocked; switch to `* prepare/<x>`, allowed.

# 7. Hook V7 test
# Introduce `//****...` banner to a clean .do file, must NOT block (compute_balance is V7-aware).

# 8. Hook V8 test
echo '------<x>' > /tmp/scratch.do
# Edit /tmp/scratch.do, blocked (V8 artifact detected).

# 9. Propagation verified
cd ~/github_repos/claude-code-my-workflow
python3 .claude/skills/tools/propagate.py --check-identity
# expect: all 7 consumers in-sync on the 14 paths.
```

All 9 checks pass — universal fix is live; both the original bug AND the meta-bug (buggy fix tool) eliminated AND the false-positive class (V7 banners plus string literals) handled correctly.
