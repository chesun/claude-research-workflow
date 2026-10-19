# Instruction Budget References Review — correctness
**Date:** 2026-10-19
**Reviewer:** correctness critic (independent, general-purpose agent)
**Target:** .claude/references/primary-source-filter-stack.md, .claude/references/destructive-actions-detail.md
**Score:** 92/100
**Status:** Active

## Verdict

Both files are faithful moves and substantively accurate. Fidelity is proven by diff: the body of `primary-source-filter-stack.md` is byte-identical to lines 48–92 of `git show HEAD:.claude/rules/primary-source-first.md` apart from the one renamed heading ("Citation extraction — the filter stack" → "The filter stack"), and the body of `destructive-actions-detail.md` is byte-identical to the concatenation of lines 50–82 and 104–112 of `git show HEAD:.claude/rules/destructive-actions.md` — nothing lost, nothing added, and the moved text is not duplicated anywhere else in tracked markdown (the only other hit for the heredoc sentence is a quotation inside the 2026-10-14 review). Every concrete claim I checked against `.claude/hooks/primary_source_lib.py`, `.claude/hooks/destructive-action-guard.py`, `.claude/settings.json` and the test suites is SOUND, including the "136" regression-case count (confirmed by running the suite: "136 passed, 0 failed"), with three exceptions, all inherited from the original rule text rather than introduced by the move: the documented filter *order* does not match the code's execution order (Medium — the doc runs sentence-start before hyphenated decomposition; the code deliberately does the reverse), the `protect-files.py` matcher is `Edit|Write|MultiEdit`, not "only `Edit|Write`" (Low), and a few phrases ("the escape hatch", "Tier 3", "(see TODO)") dangle slightly when the files are read alone, though each intro points back to its parent rule (Low). All four intro paths exist on disk. Both new files use CRLF line endings; `core.autocrlf=true`, so they normalize at commit — noted, no action.

## Fidelity evidence (reproducible)

```bash
# primary-source-filter-stack.md — identical modulo renamed heading + CRLF + trailing blank:
git show HEAD:.claude/rules/primary-source-first.md | sed -n '48,92p' \
  | sed 's/^## Citation extraction — the filter stack$/## The filter stack/' > /tmp/a
tail -n +5 .claude/references/primary-source-filter-stack.md > /tmp/b
diff -u --strip-trailing-cr /tmp/a /tmp/b   # only difference: one trailing blank line

# destructive-actions-detail.md — identical modulo CRLF + trailing blank:
{ git show HEAD:.claude/rules/destructive-actions.md | sed -n '50,82p';
  git show HEAD:.claude/rules/destructive-actions.md | sed -n '104,112p'; } > /tmp/c
tail -n +5 .claude/references/destructive-actions-detail.md > /tmp/d
diff -u --strip-trailing-cr /tmp/c /tmp/d

# test count:
python -I .claude/hooks/test_destructive_action_guard.py   # "=== Summary: 136 passed, 0 failed ==="
```

The replacement summaries left in the two rules (`.claude/rules/primary-source-first.md` "Citation extraction", `.claude/rules/destructive-actions.md` §Settings.json gate and §Chains) name the correct reference paths, and both paths exist.

## Findings

| # | Severity | Finding | Evidence | Verdict | Recommendation |
|---|---|---|---|---|---|
| 1 | Medium | Documented filter order ≠ code execution order. Doc order: blocklist → org (1b) → cue (1c) → suffix (1d) → all-caps (2) → sentence-start (3) → hyphenated (4) → allowlist (5). Code order: blocklist → suffix → all-caps → org → cue → **hyphenated → sentence-start** → allowlist. The hyphenated/sentence-start inversion is load-bearing: decomposition runs first "so that sentence-start hyphenated compounds can be tested against the allowlist using the decomposed head" | `.claude/hooks/primary_source_lib.py:770-840` (Filter 1 at 772, 1d at 780, 1a at 792, 1b at 798, 1c at 808, hyphenated at 823 with the "Runs BEFORE the sentence-start check" comment, sentence-start at 828, allowlist at 835); doc: `.claude/references/primary-source-filter-stack.md:9-23` | WEAK | Renumber the doc's stack to match execution order (1, 1d, 1a, 1b, 1c, then decomposition, sentence-start, allowlist), or state that the pure-drop filters are order-independent and only the decomposition-before-sentence-start order matters. Inherited from the original rule, not a regression of the move |
| 2 | Low | "`protect-files.py` ... is registered only on the `Edit\|Write` matcher" — the actual matcher is `Edit\|Write\|MultiEdit` | `.claude/settings.json:64` (`"matcher": "Edit\|Write\|MultiEdit"`); doc: `.claude/references/destructive-actions-detail.md:7` | WRONG (minor; the operative claim — it cannot observe Bash — stands) | Change to "the `Edit\|Write\|MultiEdit` matcher". Inherited from the original rule |
| 3 | Low | Self-containment residue: PSF file says "the org skip-list or escape hatch" and "either hook" without defining the escape hatch or naming the two hooks (`primary-source-check.py`, `primary-source-audit.py`); DA file uses "Tier 3" with Tiers 1–2 defined only in the rule (the chains bullet does gloss "all three tiers" parenthetically at line 40) and ends "(see TODO)" with no path | `.claude/references/primary-source-filter-stack.md:9,42`; `.claude/references/destructive-actions-detail.md:5,40,45` | WEAK | One-line fixes: name the two hook files in the PSF intro; in the DA intro add "Tiers 1–2 (always-blocked commands, shared-storage deletes) are in the rule"; replace "(see TODO)" with "(TODO.md)" or drop it. Each intro already points at the parent rule, so a reader can resolve them |
| 4 | Low | "rotates to `.old` past ~1MB" — the rotated file is `primary-source-blocks.jsonl.old` (suffix replace, not append), and the threshold is exactly 1,000,000 bytes | `.claude/hooks/primary_source_lib.py:999` (`_BLOCK_LOG_MAX_BYTES = 1_000_000`), `:1034` (`path.replace(path.with_suffix(".jsonl.old"))`) | SOUND (shorthand is fair) | No change needed |
| 5 | Low | New files are CRLF (`file` reports "with CRLF line terminators"); tracked siblings commit as LF | `file .claude/references/*.md`; `git config core.autocrlf` → `true` | SOUND (autocrlf normalizes at commit) | No action; verify `git diff --cached` shows no eol noise after staging |

## Claims verified SOUND (accuracy against code)

primary-source-filter-stack.md vs `.claude/hooks/primary_source_lib.py`:

| Claim | Evidence | Verdict |
|---|---|---|
| `NEVER_SURNAMES` blocklist exists; every quoted example present; collision-risk "Grant"/"Law"/"Bill"/"Nielsen" absent | `primary_source_lib.py:264` (frozenset, 438 entries); scripted membership check: all 39 quoted examples in, all 4 exclusions out | SOUND |
| Org skip-list at `.claude/state/primary_source_orgs.txt`, same loader as allowlist, missing/empty = off | `primary_source_lib.py:80,86` (both via `_load_state_wordlist`), `:53` (empty-set on missing) | SOUND |
| Allowlist at `.claude/state/primary_source_surnames.txt`, one lowercase surname per line, empty/missing = accept all | `primary_source_lib.py:16,80`; `.gitignore:64` keeps it tracked | SOUND |
| Suffix guard: `-tion/-sion/-ism/-nomics/-demic` length ≥ 7; `-ment` length ≥ 8; allowlist rescues | `primary_source_lib.py:497-513` (`_SUFFIX_GUARD_MIN_LEN = 7` at 498, `_MENT_SUFFIX_MIN_LEN = 8` at 504, rescue at 780-783) | SOUND |
| All-caps filter, length ≥ 2 | `primary_source_lib.py:792` (`len(first) >= 2 and first.isupper()`) | SOUND |
| Cue filter: cue words, all-caps acronyms, particle exemption, El Niño/La Niña carve-back, punctuation breaks the cue, allowlist override | `primary_source_lib.py:808-820` (`NAMED_ENTITY_CUES`, `_ACRONYM_TOKEN`, `PARTICLE_EVENT_BIGRAMS`, `_is_phrase_precursor`); whitespace-only separation `:210` | SOUND |
| Hyphenated: 3+ parts split, underscore stem; 2-part preserved | `primary_source_lib.py:568-582` (`len(parts) < 3` → no split) | SOUND |
| Sentence-start/structural-boundary drop unless allowlisted | `primary_source_lib.py:517,828-831` | SOUND |
| ISO-date/range guard `(?![-–—/]\d)` after the year | `primary_source_lib.py:145-157` (AUTHOR_YEAR regex) and comment `:115-123` | SOUND |
| Author list captured as one repeated span, split in Python | `primary_source_lib.py:145-157` (single `authors` group), `AUTHOR_SEP` `:159` | SOUND |
| Precomposed map exactly `ł ø ß æ œ ð þ`; curly quotes → `'`, en/em-dash → `-`, NBSP → space | `primary_source_lib.py:600-608,617-622` | SOUND |
| Possessive normalization, apostrophe-free stems, hyphen→underscore notes-lookup fallback, `**Citation:**`-line folding | `primary_source_lib.py:755-765` (strip `'s`), `:910-934` (`stem_underscored`) | SOUND |
| Rejected lowercase-determiner fix pinned by a regression test | `.claude/hooks/test_primary_source_lib.py:1187` ("eponymous 'the Heckman (1979) correction' still extracts") | SOUND |
| Telemetry: `.claude/state/primary-source-blocks.jsonl`, both hooks log, record carries ts/hook/source/missing{stem,display,status}, gitignored, fail-open | `primary_source_lib.py:998-1050` (record dict at 1037-1044, bare `except Exception: pass` at 1048); `primary-source-check.py:115`, `primary-source-audit.py:109`; `.gitignore:63` (`.claude/state/*`) | SOUND |

destructive-actions-detail.md vs `.claude/hooks/destructive-action-guard.py` and tests:

| Claim | Evidence | Verdict |
|---|---|---|
| Gate targets `.claude/settings.json` / `.claude/settings.local.json`; `.vscode/settings.json` not gated (anchors on `.claude/settings`) | `destructive-action-guard.py:226-232` (`_SETTINGS_PATH_RE`) | SOUND |
| Five write shapes: redirect (incl. glued `>path`), `tee`, `sed -i` per pipeline segment, `mv`/`cp` last-arg, scripted write | `destructive-action-guard.py:255-363` (glued redirect at 306, scripted at 351-363) | SOUND |
| Scripted-write interpreters python/node/ruby/perl; write calls `write_text`, `json.dump`, `open(..., 'w')`, `writeFileSync`, `.write(...)` | `destructive-action-guard.py:241-252` (`_WRITE_CALL_RE`, incl. `open\s*\([^)]*['\"]w` and `\.write\(`), `:359` (`python[\d.]*|py|node|ruby|perl`) | SOUND |
| Compound chain containing a settings write is blocked whole; reads not blocked | segment check `:611-617` + whole-command settings pass `:697`; `_WRITE_CALL_RE` matches no read shapes | SOUND |
| Chain split on unquoted `;`, `&&`, `\|\|`, `\|`, `&`, newline; quoted commit message not a command | `:415` (`_SEGMENT_SPLIT_RE`), `:563-575` (`_parsed_segments` via shlex `punctuation_chars=";&\|\n"` — quotes protected) | SOUND |
| cwd carried across `cd` in chains | `:648` docstring + cd tracking in `check_command` (`:683-689`) | SOUND |
| Wrappers `env` (incl. `-u NAME`, `--`, `A=1`), `command`, `time -p`, `( )`, `{ ; }`, `/usr/bin/git`, `git.exe`, git `-C`/`-c`/`--flag` unwrapped | `:426-430` (`_WRAPPERS`, `_WRAPPER_OPT_ARG`, `_GIT_OPT_ARG`), `_normalize` `:513-551` | SOUND |
| Backslash continuations joined before splitting | `:416` (`_CONTINUATION_RE`), applied in `_parsed_segments` `:565` and `_fallback_check` `:624` | SOUND |
| Heredoc: only unquoted `<<` opens one; body checked when a shell (`bash sh zsh dash ksh fish pwsh powershell`) is named anywhere on the opening line; other bodies skipped; unterminated `<<` removes nothing | `:432` (`_SHELLS`, exact 8-shell set), `:438` (`_unquoted_heredoc_starts`), `:469-506` (`continue  # unterminated: keep the lines` at 500; shell-anywhere test at 502-503) | SOUND |
| Unparseable fallback: always-blocked predicates + settings gate per segment; shared-storage delete fail-open | `:621-645` (`_fallback_check` runs `_always_blocked` + `_settings_block` only), `:674-678` (comment: "shared-storage delete check stays fail-open on this path") | SOUND |
| `sudo`, `timeout`, `nice`, `xargs` not treated as wrappers; `$(...)`/backticks/`eval`/`sh -c` not unpacked | `:426` (`_WRAPPERS = {"env", "command", "builtin", "nohup", "exec", "time"}` — none of the four present); no substitution-unpacking code exists in the file | SOUND |
| "136 regression cases as of 2026-10-14" (claim retained in the rule's cross-references, not the reference file) | `python -I .claude/hooks/test_destructive_action_guard.py` → "=== Summary: 136 passed, 0 failed ===" (104 `assert_block`/`assert_allow` call sites, several in loops) | SOUND |
| Intro paths exist | `.claude/rules/destructive-actions.md`, `.claude/hooks/destructive-action-guard.py`, `.claude/hooks/test_destructive_action_guard.py`, `.claude/rules/primary-source-first.md`, `.claude/hooks/primary_source_lib.py` — all present on disk | SOUND |

## Scoring

100 − 5 (F1, Medium: documented order contradicts a deliberately ordered, load-bearing code sequence) − 2 (F2, Low: wrong matcher string) − 1 (F3, Low: dangling references readable only via the parent rule) = **92/100**. No deduction for F4/F5 (shorthand and eol, both effectively correct). All findings are inherited from the pre-move rule text; the move itself introduced zero defects.
