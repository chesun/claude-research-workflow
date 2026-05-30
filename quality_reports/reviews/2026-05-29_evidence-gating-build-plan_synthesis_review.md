# Evidence-Gating Build Plan — Synthesis Review

**Date:** 2026-05-29
**Reviewer:** synthesis (four lens-reviewers + independent verification)
**Target:** `quality_reports/plans/2026-05-29_evidence-gating-build-plan.md` (implements `quality_reports/reviews/2026-05-28_whole-picture-critic-gates-dispatch.md` §7)
**Status:** Active

---

## Executive verdict

**REVISE-FIRST.** The plan's architecture is sound and faithfully implements the approved design, but Phase 1 — the declared "load-bearing guarantee" — is both (a) under-specified on five build-time mechanics that a builder cannot invent (git-show new-file handling, hook ordering, ledger write mechanics, refactor-mode manifest format, normdiff return types), and (b) carries an unmitigated design flaw: the guarantee is silently void whenever `refactor-mode` is not enabled, which is the *default* state — meaning the exact ADR-0011 incident class can recur uncaught. Fix the design flaw and close the spec gaps before any code is written.

---

## Confirmed findings (ranked by severity)

Findings raised by multiple lenses are merged; the contributing lenses are noted in brackets.

### CRITICAL

**C1. The "guarantee" is silently void by default — refactor-mode dependency reintroduces the ADR-0011 incident class.**
*[Adversarial lens, raised across three findings: refactor-mode-dependency, default-config-incident-recurs, silent-skip-on-missing-state-file]*
- **Plan section:** Phase 1, lines 43, 47; Risks section.
- **Problem:** Plan line 43 makes the hook `exit 0 (silent no-op)` if `.claude/state/refactor-mode.enabled` is absent or the file is not in the manifest. Line 47 states this file is "NOT committed as active; documented + created on demand" — so the default state of any clone/session is refactor-mode OFF. The design calls this hook the only "context-independent" mechanism (design §3) and claims it "directly closes the incident class" (plan line 54), yet the 2026-05-28 incident itself was "caught only by external diff review" (design §2, line 30) with no gate enabled. If a future refactor proceeds without someone remembering to enable refactor-mode, the contaminated edit ships uncaught — identical to the incident. The Risks section never lists "forgetting to enable refactor-mode" as a risk. A guarantee conditional on human memory is not context-independence; it is context-dependence relabeled.
- **Why critical:** This is the single defect that breaks the stated purpose of Phase 1. A silent no-op also violates the discipline's own doctrine (design §7.3: "UNVERIFIED — evidence absent... Loud, deducting, never silent").
- **Fix:** Adopt the design's own advisory-always option (design §7.5a / line 137): the hook fires on **every** Edit/Write to a supported file, and refactor-mode flips severity from *advisory* to *hard block* — it never controls *whether the check runs*. When refactor-mode is off and a logic change is detected, the hook must still (1) write an `UNVERIFIED` (not absent, not PASS) ledger row and (2) emit advisory context to the user. The skip becomes audible and evidence-bearing. Either implement this, or explicitly relabel Phase 1 from "the guarantee" to "an optional accelerator" and document the deployment burden plus a pre-refactor ceremony. The current framing hides the dependency.

**C2. `git show HEAD:<path>` crashes on brand-new files; unhandled, the hook fails-open and silently skips the check.**
*[Technical lens — git-show-head-new-file-risk; VERIFIED against repo]*
- **Plan section:** Phase 1, line 44 (baseline computation).
- **Problem:** Verified: `git show HEAD:<new-file>` exits 128 with `fatal: path '...' exists on disk, but not in 'HEAD'`. Grep across both plan and design shows zero mentions of "new file", "empty baseline", or "fallback". Plan line 46's generic "Fail-open on any exception" means a new file would fall into the fail-open path and skip the check entirely — the exact silent-miss the Tier-1 guarantee must prevent (a brand-new contaminated file is precisely the case to catch, not skip).
- **Fix:** Step computing the baseline must explicitly catch the non-zero exit from `git show` and treat a missing-in-HEAD file as an **empty baseline string** (a new file has no prior version → the entire post-text is "new", so normdiff sees all of it as residue). Do not let this collapse into the generic fail-open. Document this in the Phase 1 logic.

### MAJOR

**M1. Refactor-mode manifest format, parsing, and lifecycle are unspecified — the Phase 1 hook cannot be built without them.**
*[Technical lens — refactor-mode-manifest-definition (VERIFIED); Completeness lens — refactor_mode_manifest_unspecified; Adversarial lens — no-pre-refactor-ceremony]*
- **Plan section:** Phase 1 line 25 (open decision 2), lines 43, 47.
- **Problem:** Plan recommends "a manifest, one repo-relative path per line" but never nails (a) exact format (readlines? blank-line handling? trailing newline?), (b) parsing/match semantics (exact match vs glob? canonicalization?), (c) empty-manifest behavior, (d) git-ignored vs committed, (e) who creates/updates it and when. The activation check (line 43) reads this file but the hook builder has no contract. Verified: the file does not exist and no convention is documented.
- **Fix:** Decide and document before coding. Recommended: newline-delimited, one repo-relative path per line, exact-match after `Path.relative_to(repo_root)` canonicalization, blank/comment lines ignored, empty manifest = no files in scope, git-ignored (local-only). Add the convention to `.claude/state/`'s README. Tie to a pre-refactor activation step (a `/tools` subcommand or documented ceremony) so the toggle is not forgotten — this also partially mitigates C1.

**M2. Hook execution order relative to `stata-comment-balance-check.py` (and `derive-check-block.py`) is undefined; harness blocks halt downstream hooks.**
*[Technical lens — hook-ordering-with-stata-comment-balance (VERIFIED); Consistency lens — derive-check-hook-overlap-unclear]*
- **Plan section:** Phase 1, line 49 (settings.json edit).
- **Problem:** Verified: settings.json PreToolUse `Edit|Write|MultiEdit` matcher already chains 4 hooks (protect-files.sh → primary-source-check.py → stata-comment-balance-check.py → derive-check-block.py). Documented harness behavior (per `2026-04-23_primary-source-backport-review.md` line 97-98): a blocking hook halts the chain. `stata-comment-balance-check.py` can block (line 240). The plan says only "alongside" — no position, no statement of what happens when one hook blocks before the other runs. If `evidence-gate-check.py` is placed first and blocks, comment-balance never runs (and vice-versa).
- **Fix:** Specify exact insertion order. Recommended: place `evidence-gate-check.py` **last** (after derive-check-block.py), so independent always-on checks (comment balance, derive) run first regardless of refactor-mode. Document that a block by any earlier hook halts the chain. Differentiate error messages so a user can tell an evidence-gate block from a derive-check block.

**M3. Ledger write timing, row format, and IO-failure handling are unspecified.**
*[Technical lens — ledger-write-timing (VERIFIED); Completeness/Consistency lenses — phase2_ledger_schema_backward_compat, ledger-schema-backward-compat-unverified]*
- **Plan section:** Phase 1 lines 45-46 (PASS/UNVERIFIED/FAIL rows); Phase 2 line 66 (schema extension).
- **Problem:** Verified: current ledger is 6 columns (`Path | Check | Verified At | File hash | Result | Evidence`). The plan never states (a) the row format the hook writes, (b) whether the write happens before or after the block decision (if before-block-and-skipped, evidence is never recorded), (c) append vs replace for duplicate (path, check) pairs given the existing hash-staleness mechanism, (d) fail-open on unwritable ledger. Separately, Phase 2 adds `tier`, `artifact_citation`, `refuter_tally` columns and claims backward-compat (line 66, 70) but provides no test, and verified consumers parse by column position (coder-critic.md:205-207, diagnostic-claim-audit.py) — adding columns shifts positions.
- **Fix:** Define the exact row the Phase 1 hook writes; write the verdict **after** normdiff completes and **before** the block/pass output (so the ledger is always populated even on a block); wrap the write in try/except and fail-open on IO error (never block on ledger failure). For Phase 2, add a concrete backward-compat test showing an old 6-column row parses identically after extension, and spot-check every ledger consumer for hard-coded column counts.

**M4. Scaffold/path-normalization logic in `stata_comment_lib.py` is entangled with comment-balance *repair*, not isolated for diff use.**
*[Technical lens — scaffold-logic-portability; Consistency lens — normdiff-reuse-pattern-underdefined]*
- **Plan section:** Phase 1 line 40-42 (normdiff_lib Stata normalizer).
- **Problem:** `stata_comment_lib.py` (lines 32-73) has `is_path_glob_open/close()` predicates and `_PATH_CHARS`, but they live inside `find_matching_close()` / `rewrite_inner_block_markers()` — *repair* functions. There is no standalone "normalize for diff." The plan's "port scaffold/path logic + reuse stata_comment_lib.py" understates the work: the library is not reusable as-is for normalization-only. The plan's claim that normdiff "mirrors the shared-lib convention" is also inexact — existing libs operate whole-file, not region-aware.
- **Fix:** Extract the path-glob predicates into a pure utility, or write a fresh `normalize()` in normdiff_lib applying the same path-char heuristics without the repair machinery. State plainly that normdiff_lib's interface is *new* (region-awareness reserved for future Quarto), and that current normalizers operate whole-file.

**M5. Normdiff three-step interface (extract / normalize / normdiff) lacks return types and algorithm.**
*[Technical lens — three-step-normalizer-interface]*
- **Plan section:** Phase 1 lines 36-40.
- **Problem:** The plan names the three functions but does not define: normalize() return type (list of lines? string? token set?), the normdiff algorithm (set difference? line diff?), or what "substantive" means operationally per language. The builder would have to invent the core contract.
- **Fix:** Pin the contract in a docstring spec before coding. Recommended: `normalize()` → list of normalized line strings; `normdiff()` → set comparison returning added/removed lines; "substantive" = non-comment, non-blank, non-path-token for code; non-comment, non-blank for LaTeX.

**M6. LaTeX "no-content-change" semantics are too vague to design the normalizer or test it.**
*[Completeness lens — latex_content_change_semantics]*
- **Plan section:** Phase 1 line 40; deferred to Phase 2 ("extend in place").
- **Problem:** "Substantive line = content" is not operationalized: does it include `\label{}` strings, `\cite{}` keys, blank lines? No LaTeX fixture is listed in the test corpus, yet a LaTeX refactor case (preamble reorder, macro rename) is exactly what must pass.
- **Fix:** Add LaTeX fixtures to Phase 1 tests — (a) pure preamble refactor / `\newcommand` rename → must pass; (b) changed `\label{}`/`\cite{}` argument → must flag. Decide blank-line treatment explicitly (recommend: stripped before normalization).

**M7. MultiEdit baseline/post-state ambiguity.**
*[Completeness lens — multiedit_baseline_unspecified]*
- **Plan section:** Phase 1 line 44.
- **Problem:** The plan borrows `_build_post_text` but doesn't say whether normdiff applies edits to HEAD-baseline or to current disk, nor how overlapping/conflicting old_string matches are handled.
- **Fix:** Specify: baseline = `git show HEAD:<path>`; post-text = serial `_apply_edit` simulation; if any `_apply_edit` fails (old_string not found) → fail-open (exit 0). Mirror the comment hook, but state it.

**M8. Non-UTF8 / binary content unhandled.**
*[Completeness lens — non_utf8_unhandled]*
- **Plan section:** Phase 1 line 42.
- **Problem:** No encoding-failure path; extraction will crash on a non-UTF8 `.do`. The comment hook already handles this (returns None on UnicodeDecodeError) but the plan doesn't carry the pattern forward.
- **Fix:** State that normdiff_lib reads via `read_text(encoding="utf-8")` and fail-opens (empty residue) on decode failure.

**M9. Phase 2 introduces the {PASS, UNVERIFIED, FAIL} verdict vocabulary as prose-to-an-LLM before Phase 3 schema enforcement gives it teeth.**
*[Consistency lens — phase-2-critic-unverified-gap]*
- **Plan section:** Phase 2 line 68; Phase 3 lines 80-81.
- **Problem:** Phase 2 tells critics to emit UNVERIFIED, but the design itself notes "prose without a trigger doesn't bind" (derive-dont-guess precedent), and the 2026-05-28 incident was precisely an LLM critic asserting a verdict by judgment. Without Phase 3's schema enforcement, Phase 2 deductions are advisory prose on an LLM — the failure mode repeats in the interim.
- **Fix:** Either co-ship the Phase 3 schema check with Phase 2, or add an explicit interim warning to Phase 2: "verdict vocabulary is advisory until Phase 3 schema validation is live; the Phase 1 hook + ledger population is the real interim guarantee." Soften interim deductions accordingly.

**M10. Phase 5 propagation treats all `.claude/rules/*.md` as Class A, which would clobber overlay-customized rules.**
*[Consistency lens — file-classes-propagation-overlay-mismatch; VERIFIED]*
- **Plan section:** Phase 5 lines 106-108.
- **Problem:** Verified: `.claude/file-classes.toml` lines 65-66 mark `rules/quality.md` and `rules/workflow.md` as **Class B** (overlay-customized: overlay-specific component weights and phase/dispatch tables). Phase 2 edits agents.md/quality.md/workflow.md for the ledger-consult logic; Phase 5 propagating these as Class A would overwrite overlay variants.
- **Fix:** In Phase 5, distinguish: the evidence-gating rule + its `references/` detail + the new hooks/lib → Class A (universal); but agents.md/quality.md/workflow.md keep Class B status — only the universal ledger-consult edits merge into overlay branches manually. State this explicitly so `/tools propagate` is invoked correctly.

**M11. Rule-home decision (extend adversarial-default.md vs rename to evidence-gating.md) has no inbound-reference audit, and extending in place risks context-tightening bloat.**
*[Completeness lens — rule_home_cross_reference_risk; Consistency lens — context-tightening-bloat-risk; both VERIFIED]*
- **Plan section:** Phase 2 line 24 (open decision 1), line 26 (open decision 3).
- **Problem:** Verified: 12 files reference `adversarial-default` (agents/coder-critic, verifier, writer-critic; hooks/diagnostic-claim-audit, destructive-action-guard, post-rewrite-verify; rules/anti-ai-prose, derive-dont-guess, destructive-actions, no-assumptions; plus the ledger and the rule itself). A rename without grep-and-replace silently breaks these. Separately, the context-tightening plan just cut always-on rules 27% (165KB→119KB) via lazy-loading; adversarial-default.md is ~16KB with no `paths:` frontmatter, and extending in place with the full §7 tier tables/vocabulary (~3-5KB) re-bloats the always-on footprint.
- **Fix:** Resolve both open decisions in Phase 2. Recommended: keep the filename (preserves all 12 refs), but split content — keep only the one principle (§7.0) + enforcement-strength rule (§7.5a) always-on; push tier tables + vocabulary + operationalization to `.claude/references/evidence-gating-detail.md` (lazy-loaded). If renaming is chosen instead, add a Phase 2 verification step that re-runs the grep and confirms all 12 refs updated.

**M12. Phase 3 (citation_existence_lib, Workflow schema integration) and Phase 4 (requirements-spec template) specified too vaguely to build.**
*[Completeness lens — citation_existence_lib_vague, phase3_workflow_schema_integration, phase4_requirements_template_integration]*
- **Plan section:** Phase 3 lines 80-82; Phase 4 line 94.
- **Problem:** citation_existence_lib has no I/O contract (input citation format, output shape, hook vs /tools registration, test-naming/dispatch convention). The Workflow-tool schema integration names no schema shape, required field, or error path. The requirements-spec tier-tagging has no tag format, no template location, and no critic deduction logic. Verified: `templates/requirements-spec.md` currently has no tier column.
- **Fix:** These are later phases (not Phase-1-blocking) but should be specified before their respective phases start. Add concrete contracts: `resolve_citation(citation: str) -> {exists, output}` with `file:line-range[:test_id]` format and extension-dispatched test runs (fail-open if infra unavailable); a `verdict_schema` field shape for critics with `required: [claim, artifact_citation]`; and a "Verification Tier" column in the requirements-spec table with a matching critic deduction.

### MINOR

- **m1. Quarto deferral not tracked.** *(Completeness — qmd_deferral_todo_location)* Plan line 127 defers `.qmd` to "TODO backlog" but no TODO.md entry exists. Add one: "Quarto .qmd support for normdiff hook — needs chunk_extract() + Quarto YAML parsing + integration tests."
- **m2. Phase 1 verification says "all four" languages but `_SUFFIX_LANG` has six suffixes.** *(Completeness — phase1_verification_incomplete)* Enumerate explicitly: `.do/.doh` (Stata), `.R/.r` (R), `.py` (Python), `.tex` (LaTeX); smoke-test each suffix.
- **m3. BYPASS_SHARED_GUARD applicability to the settings.json edit could cite the exact destructive-actions.md Tier-3 mechanism.** *(Technical — bypass-destructive-actions-guard)* Non-blocking clarification.
- **m4. Phase 5 should verify file-classes.toml has entries for the new files before propagating.** *(Completeness — phase5_propagation_class_file_location)* Add a verification step confirming the new hooks/lib/references are listed and class-tagged.

---

## Refuted / not reproduced

No high-severity finding was refuted. Three lens findings were verifications that the plan is *correct* (kept here so the audit trail is complete, not as defects):

- **language_for_path() coverage** — VERIFIED complete: `derive_lib.py` lines 47-69 map all six suffixes (`.do/.doh/.r/.R/.py/.tex`). No action; reuse as-is.
- **Hook stdin JSON contract** — VERIFIED against `stata-comment-balance-check.py` lines 124-141; Phase 1 step 1 is implementable as written.
- **`_build_post_text` reuse pattern** — VERIFIED at `stata-comment-balance-check.py` lines 85-114; directly reusable. (Note: this reuse still needs the M2/M7/C2 clarifications layered on top — the *pattern* is proven, the *baseline edge cases* are not.)

---

## Must-fix before Phase 1

Blocking items only, in order:

1. **C1 — Resolve the refactor-mode default-off flaw.** Make the hook advisory-always with refactor-mode controlling block-severity (not activation), emitting an UNVERIFIED ledger row + advisory on every off-mode logic change. Or formally relabel Phase 1 as an optional accelerator and document the precondition. (Design decision — do this first; it changes the hook's shape.)
2. **C2 — Specify new-file baseline handling.** Catch `git show HEAD:<path>` exit 128 explicitly → empty baseline; do not let it fall into generic fail-open.
3. **M1 — Pin the refactor-mode manifest format, parse semantics, and lifecycle.** (Also partially mitigates C1.)
4. **M2 — Specify hook insertion order and document block-halts-chain behavior.**
5. **M3 (Phase-1 half) — Define the ledger row format, write-after-normdiff/before-block timing, and fail-open-on-IO.**
6. **M4 — Decide scaffold-logic isolation vs re-implementation for normdiff_lib.**
7. **M5 — Pin normdiff return types and the diff algorithm in a docstring spec.**
8. **M6, M7, M8 — Add LaTeX semantics + fixtures, MultiEdit baseline rule, and non-UTF8 fail-open.**

M9–M12 and the minors gate Phases 2–5, not Phase 1, and can be resolved as those phases begin — but M11's rule-home/bloat decision and M10's overlay-class distinction should be settled before the first rule edit lands.

---

## Bottom line

The plan is structurally sound and correctly grounded in the existing hook/library infrastructure — the lenses independently confirmed the reusable pieces all exist and the design is faithfully tracked. It is *not* a rewrite. But Phase 1 ships a guarantee that, as written, is silently disabled by default (C1) and is missing the edge-case and interface specifications a builder cannot invent (C2, M1–M8). Close those, and Phase 1 is buildable.
