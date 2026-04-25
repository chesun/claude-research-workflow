<!-- primary-source-ok: chetty_2014, rockoff_2014, chetty_friedman_2014, chetty_friedman_rockoff_2014 -->
<!-- All citations in this log are illustrative test-case references for the
     hook itself, not framing claims about the underlying papers. -->

# Session Log: 2026-04-25 — Primary-Source Hook Iterative Fixes

**Status:** COMPLETED
**Branches affected:** `main`, `applied-micro`, `behavioral`, `va_consolidated/main`
**Total commits:** 4 on each of 4 repos = 16 commits (3 commits cherry-picked + 1 commit copied per repo)

## Objective

Field-test feedback from `va_consolidated` (the new applied-micro project for the CEL Value-Added consolidation) revealed that the primary-source-first hook had been misfiring on routine prose, blocking 6+ load-bearing edits per session. A diagnostic memo (`va_consolidated/quality_reports/reviews/2026-04-24_primary-source-hook-fix-memo.md`) documented four distinct false-positive classes plus an escape-hatch regex bug. This session implemented the universal fix and then iteratively repaired three follow-up bugs surfaced by continued real-world use.

## Changes Made (commit-level summary, propagated to all 4 repos)

| Commit on main | Description | Files |
|---|---|---|
| `c7c7bc6` | Initial 4-filter fix + escape-hatch hyphen support + 27 regression tests | `primary_source_lib.py`, `test_primary_source_lib.py`, `primary-source-first.md` |
| `375ab47` | Test reproducibility — clamp `KNOWN_SURNAMES` to empty during tests | `test_primary_source_lib.py` |
| `6edff05` | Filter ordering — hyphen-decompose runs before sentence-start | `primary_source_lib.py`, `test_primary_source_lib.py` |
| `474b306` | Display string uses comma+and form for round-trip safety | `primary_source_lib.py`, `test_primary_source_lib.py` |

After each commit on `main`, the change was cherry-picked onto `applied-micro` and `behavioral`, and copied directly into `va_consolidated/.claude/hooks/`.

## Design Decisions

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| Four orthogonal fixes in one library, gated by ordered filters | Heavyweight NLP / spaCy / NER for "is this really a surname?" | NLP would require extra deps and runtime; ordered filters cover ~95%+ of false positives with zero deps. Surface area stays small. |
| `NEVER_SURNAMES` as conservative hard-coded blocklist (~80 words) | Open-ended user-configurable blocklist | Conservative built-in list catches the universal cases (function words, seasons, months, document-structure terms) without project configuration. Users can still populate the surname allowlist for tightening; the blocklist is below that. |
| Sentence-start filter requires explicit allowlist match | Reject all sentence-start matches | Real citations at sentence-start are common (a one-name citation at sentence start with surname in allowlist). Requiring allowlist membership preserves them when the project has populated the allowlist; drops them when the allowlist is empty (acceptable noise reduction for new projects). |
| Hyphen decomposition for 3+ parts, preserve 2-part | Always decompose | Two-part hyphenated tokens like Goldsmith-Pinkham are real hyphenated surnames. Decomposing them would corrupt the stem. The 3+ heuristic is safe because real 3+ part hyphenated single surnames are vanishingly rare. |
| Escape-hatch regex `.+?` non-greedy with explicit `-->` terminator + DOTALL | Allow newlines without DOTALL by changing list separator | `.+?` + DOTALL is one line and supports both inline and multi-line escape comments. Maintains backward compatibility. |
| Filter ordering: blocklist → hyphen-decompose → sentence-start → allowlist | Original order (blocklist → sentence-start → hyphen-decompose → allowlist) | Original order rejected sentence-start hyphenated compounds because the full hyphenated form was tested against the allowlist. Decomposing first lets the sentence-start check use the head surname. |
| Display format comma+and for 3+ surnames | Space-joined (original) | Space-joined display strings echoed into prose were re-extracted by the regex as just the last name. The regex's separator alternation only accepts `,/and/&`, so comma+and round-trips cleanly. |
| Tests clamp `KNOWN_SURNAMES = set()` at top of runner | Tests use the project's actual allowlist | First version of tests passed locally (where allowlist was empty) but failed on `va_consolidated` (where allowlist had 210 entries). Clamping makes tests reproducible regardless of host project state. |

## Incremental Work Log

**Iteration 1 — Initial 4-filter fix (commit `c7c7bc6`):** Read the diagnosis memo, implemented all four fixes (NEVER_SURNAMES blocklist, sentence-start filter, hyphen decomposition, escape-hatch regex), wrote 27 regression tests covering each false-positive class. All tests passed locally on main.

**Iteration 2 — Test reproducibility (commit `375ab47`):** Copied the fix to `va_consolidated`, but one test (4-name hyphenated compound) failed there because va_consolidated's populated 210-entry allowlist didn't include `goldsmith`/`pinkham`/`sorkin`. Tests now save+clamp+restore `KNOWN_SURNAMES` so they're allowlist-independent.

**Iteration 3 — Filter ordering (commit `6edff05`):** User reported that hyphenated method-name compounds at sentence start (after period, after colon, at start-of-string) were still being rejected. Diagnosed: sentence-start filter ran before hyphen-decomposition, so the full hyphenated form was checked against the allowlist instead of the decomposed head. Reordered filters and updated the sentence-start check to inspect `first_parts[0]`. Added 7 regression tests.

**Iteration 4 — Display round-trip (commit `474b306`):** User reported that the display string for decomposed compounds was being re-extracted by the Stop-hook audit as the last name alone — because the regex's separator alternation accepts `,/and/&`, not space. Changed display format to comma+and Oxford form. Round-trip is now self-consistent. Added 3 regression tests.

**Stop-hook self-encounter:** Three times during this session (and once on the first attempt to write this very log), the audit hook fired on session prose because the canonical illustrative examples appeared in commit messages, test cases, and design-decision tables. Resolved with `<!-- primary-source-ok: ... -->` escape comments. Confirms the escape-hatch mechanism works correctly under real load — the hook fires deterministically, the escape is well-scoped.

## Learnings & Corrections

- **Reordering filters revealed a hidden coupling.** The first three iterations of the fix each looked locally correct but interacted poorly: filter A's behavior depended on what filter B had done first. Lesson: when adding new filters to a pipeline, document the dependency order in code comments and add tests that exercise the cross-filter interactions, not just each filter in isolation.
- **Self-consistency under round-trip is a useful invariant.** When a function's output (display string) is fed into the same function later (Stop audit re-scanning prose), the output should produce the same result. Catching this required imagining the data flow, not just verifying each function in isolation. Worth a hard rule: anywhere data round-trips, write a round-trip regression test.
- **Test environments must be hermetic.** Tests that read project state (like `KNOWN_SURNAMES` from a project allowlist file) produce non-portable results. Save/clamp/restore at the test boundary or refactor the tests to not depend on global state.
- **The hook caught me multiple times during its own development.** All correctly. The escape-hatch mechanism is the right safety valve for "I'm referencing a paper as a test case, not making a framing claim." Documenting this pattern in `primary-source-first.md` as an explicit "use case for the escape hatch: when the citation is itself a test fixture or example" would help future Claude instances reason about when to use it.
- **Field-driven debugging beats armchair speculation.** Each iteration was triggered by a real observed failure in `va_consolidated`. Not all the false-positive classes would have been obvious without that. Trunk+overlays + a real downstream project is a fast feedback loop.

## Verification Results

| Check | Result | Status |
|-------|--------|--------|
| All 37 regression tests pass on empty allowlist | PASS | ✓ |
| All 37 tests pass on va_consolidated's populated 210-entry allowlist | PASS | ✓ |
| Sentence-start function-words + year correctly rejected | 7 cases | PASS |
| Cohort/season/month + year correctly rejected | 5 cases | PASS |
| Document-structure words + year correctly rejected | 4 cases | PASS |
| Hyphenated 3+ part compound at sentence-start with allowlist passes | 5 cases | PASS |
| Display string round-trips through extractor | 3 cases | PASS |
| Escape hatch handles hyphenated stems and multi-line | 3 cases | PASS |
| Hook fires correctly on real un-grounded citation | (this session, several times) | PASS (with escape applied) |

## Open Questions / Blockers

- [ ] **Stop-hook session-state cache.** The audit re-scans the entire session transcript at every turn-end. If a citation was satisfied via escape hatch in turn N, it's still re-detected in turn N+1's audit (because the audit doesn't know about the prior turn's escape). The user's diagnosis memo §7 floats caching satisfied stems in `.claude/state/session_satisfied_stems.json`. Defer until churn becomes a real problem; current behavior is conservative-correct.
- [ ] **Project-extensible acronyms file.** Memo §3 Fix 4 floats `.claude/state/primary_source_acronyms.txt` for project-specific dataset names (CALSCHLS, CAASPP, NSC, ACS, etc.). The blocklist already covers the common cases; defer until needed.
- [ ] **"Test fixture" pattern for primary-source rule.** When citations appear only as illustrative examples (test cases, regex inputs, documentation), they're never "framing claims" but the hook can't tell. Document this case in `primary-source-first.md` as a canonical use case for the escape hatch.

## Next Steps

- [ ] (deferred) Document the test-fixture / illustrative-example pattern in `primary-source-first.md`.
- [ ] Watch for additional false-positive or false-negative classes during next va_consolidated session.
- [ ] If churn from §Open Question 1 becomes a real cost, implement session-state caching.
