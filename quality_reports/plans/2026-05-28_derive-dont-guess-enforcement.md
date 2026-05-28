# Plan — Give `derive-dont-guess` (and other prose-only rules) Enforcement Teeth

**Status:** COMPLETED 2026-05-28. All 6 components implemented across 5 code commits (4c0cdb3 docs → 8b662b7). 59 hook unit/integration tests pass. Output-length decided: advisory, non-blocking. Deferred: Component 4d (`/write`→`writer-critic`); applying the CLAUDE.md Core Principles bullet to overlay branches; opt-in block hook stays off pending field calibration. See `TODO.md`.
**Date:** 2026-05-28
**Scope decisions (confirmed with user):** Full systemic fix · derive-dont-guess first but built for reuse · advisory-on-by-default, blocking opt-in later. **Plus (added 2026-05-28):** plan-persistence and output-length must become hook-enforced "hard" rules — same disease, same fix.
**Source audit:** `quality_reports/reviews/2026-05-28_derive-dont-guess-binding-audit.md`

---

## Context

The user keeps hitting `derive-dont-guess` violations in *other* (forked/consumer) repos — fabricated data paths, undefined macros, references that don't resolve. The audit established **why the rule is non-binding by construction**:

1. **No hook, no trigger.** `settings.json` registers only three `Edit|Write` hooks (`protect-files.sh`, `primary-source-check.py`, `stata-comment-balance-check.py`). `derive-dont-guess` has none. Its sibling `primary-source-first` binds *only* because it has two registered hooks.
2. **Critic-only enforcement is unreachable ad-hoc.** The deduction tables (`coder-critic.md:210`, `writer-critic.md:173`) fire only when `/analyze`, `/review`, or the orchestrator dispatch a critic. A plain "write me this `.do` file" runs none of them — `/write` doesn't even dispatch `writer-critic`, and `/commit` has no score gate (both confirmed).
3. **Propagation gap.** `settings.json` is git-tracked so forks get it on clone, but `/tools propagate` is pattern-driven and `settings.json` isn't an explicit universal pattern — so new hook registrations never reach already-cloned forks. This is why *other* repos leak worst.

**The general lesson** (user's meta-point): *a prose-only rule with no deterministic trigger does not bind.* This applies beyond derive-dont-guess — `output-length.md` (>15 lines → write to file) and the plan-persistence expectation in `workflow.md` have the same disease and the same cure: a hook trigger. Component 6 extends the fix to them.

**Intended outcome:** an enforcement layer that fires in the exact ad-hoc path where violations occur, on-by-default and near-zero false-positive (advisory), with a designed-but-gated blocking upgrade, a propagation fix so the teeth reach forks, and the same trigger-based treatment applied to plan-persistence and output-length.

---

## Recommended approach

### Component 1 — Advisory detection hook (the core; on by default)

New files:

- `.claude/hooks/derive_lib.py` — shared detection lib (built for reuse by future no-assumptions/adversarial hooks).
- `.claude/hooks/derive-check-advisory.py` — **PostToolUse** entry, matcher `Write|Edit|MultiEdit`.

Behavior:

- Gate on `tool_name`; act only on analysis/paper code: `.do .doh .R .r .py .tex`.
- Reconstruct the **added text only** (Edit→`new_string`, Write→`content`, MultiEdit→concat of `new_string`s). Scanning the delta, not the whole file, keeps it cheap and warns only on *newly introduced* references.
- Extract **read/input** path-literals via conservative, high-confidence per-language regexes:
  - Stata: `use "..."`, `import delimited "..."`, `merge ... using "..."`, `include ...`, `do ...`
  - R: `read_csv/read_dta/readRDS/fread/read.csv("...")`, `source("...")`
  - Python: `pd.read_*("...")`, `np.load("...")`, `open("...")` (read modes)
  - LaTeX: `\input{...}`, `\include{...}`, `\includegraphics[...]{...}`, `\addbibresource{...}`
- **Exclude write/output targets** (never warn): `save`, `export`, `graph export`, `esttab/estout ... using`, `saveRDS`, `writeLines`, `ggsave`, Python write-mode `open`. This is what keeps false-positives near zero — non-existent *output* paths are normal.
- Resolve each read path against `CLAUDE_PROJECT_DIR` (literal + glob). For Stata `$global` / `` `local` `` in a path: if the macro is **defined anywhere in the repo** (grep `global <name>` / `local <name>` / `set <name>`), stay silent (can't statically expand); if **undefined repo-wide**, warn (strong guess signal).
- For unresolved read paths: emit a **non-blocking** advisory via `hookSpecificOutput.additionalContext` listing the paths + the derive-dont-guess remediation. Always exit 0.
- **Escape hatch** `<!-- derive-ok: <reason> -->` (+ `* derive-ok:` / `// derive-ok:` forms) in the delta, mirroring `primary-source-ok`.
- **Per-session dedup**; **fail-open** on any exception.

Reused primitives: `post-rewrite-verify.py:73-82` (`_emit`/additionalContext), `stata-comment-balance-check.py:65-114` (MultiEdit reconstruction), `verify-reminder.py:104-131` (session cache), `primary_source_lib.py` escape-hatch + glob resolution.

### Component 2 — Blocking variant, built but opt-in (off by default)

- `.claude/hooks/derive-check-block.py` — **PreToolUse**, matcher `Write|Edit|MultiEdit`, reusing `derive_lib.py`.
- Blocks **only** when a newly-added **read/input** path doesn't resolve **and** its governing macro is undefined repo-wide. Never blocks on write targets or macro-expandable paths.
- **Inert unless** `.claude/state/derive-guess-block.enabled` exists (off by default). Escape hatch `<!-- derive-ok -->` + append-only JSONL audit log `.claude/state/derive-guard.log` (mirrors `destructive-action-guard.log`).

### Component 3 — Propagation fix (so teeth reach forks)

- Add `.claude/settings.json` to `file-classes.toml` `[universal]` patterns so `/tools propagate` includes hook registrations.
- **Tradeoff handled:** `settings.json` carries `permissions.allow`; document (plan + `file-classes.toml` comment) that consumer/machine-specific permission overrides belong in `.claude/settings.local.json` (gitignored, `.gitignore:62`). New hook `.py` already match universal `.claude/hooks/*.py`; rule edits match `.claude/rules/*.md`. Only `settings.json` needs adding.
- `CLAUDE.md` is Class B → Component-4a edit applied on `main` **and** each overlay branch manually (flag in `/tools sync-overlays`).

### Component 4 — Non-hook elevations (cheap, ship alongside)

- **a)** `CLAUDE.md` Core Principles: add a "**Derive, don't guess**" bullet beside "Primary source first", noting the advisory hook. (Class B → per branch.)
- **b)** Strengthen **creator** prompts (`coder.md:117`, `writer.md:118`) so the pre-generation derivation grep runs *before* generation. (`coder.md` Class A; `writer.md` Class B.)
- **c)** Wire a staged-files derive check into `/commit` (`commit/SKILL.md`) via `derive_lib --check`. (Class A.)
- **d)** *(lower priority)* Make `/write` dispatch `writer-critic` (`write/SKILL.md`). (Class A.)

### Component 5 — Tests + rule docs

- `.claude/hooks/test_derive_lib.py` — unit tests mirroring `test_primary_source_lib.py`/`test_stata_comment_lib.py`: per-language extraction, read-vs-write classification, macro-defined detection, glob resolution, escape hatch, MultiEdit reconstruction, fail-open. Fixtures under `.claude/hooks/tests/`.
- Add an `## Enforcement` section to `.claude/rules/derive-dont-guess.md` (it has none) documenting the advisory hook, opt-in block, escape hatch, propagation requirement.

### Component 6 — Make plan-persistence and output-length hook-enforced (added 2026-05-28; PROPOSED)

Same disease, same cure: give each a deterministic trigger.

- **6a — Plan persistence (hard rule, blocking) — via Stop hook.** New `.claude/hooks/plan-persist-check.py` — **Stop** hook. **Mechanism decided after doc verification:** `ExitPlanMode` is *not* `PreToolUse`-hookable (it's a `PermissionRequest` event, docs `hooks-guide.md:389-419`), and during plan mode the agent can only write the harness plan file, never `quality_reports/plans/` — so plan-*exit* cannot be the gate. Instead, the Stop hook fires at turn-end and blocks (`{"decision":"block","reason":...}`) when: (i) the session transcript shows plan-mode activity (an `ExitPlanMode` tool_use event and/or a write to `~/.claude/plans/`), AND (ii) no `quality_reports/plans/*.md` was created/edited this session (transcript-walk via the `notes_touched_in_session` pattern, `primary_source_lib.py:489-515`). Remediation: "You planned this session but didn't persist it — copy your plan to `quality_reports/plans/YYYY-MM-DD_<slug>.md` (`workflow.md` §1) before stopping." Respects `stop_hook_active` to fire at most once per turn. Also update `workflow.md` §1 ("Save to disk" becomes hook-enforced), add a Core Principles bullet, and a `## Enforcement` section to `workflow.md`.
- **6b — Output length (advisory, with teeth).** New `.claude/hooks/output-length-check.py` — **Stop** hook. Measures the final assistant message; if > 15 non-trivial lines AND no `Write`/`Edit` to a `.md` happened this turn, inject an `additionalContext` advisory ("this response exceeds 15 lines — export to a `.md` per `output-length.md` and summarize inline"). Respects `stop_hook_active` to fire at most once per turn (pattern from `primary-source-audit.py`). **Advisory, non-blocking** (user decision 2026-05-28): legitimate long conversational answers exist; blocking would be high-false-positive. The win over today's rule is that the reminder is *injected* (`additionalContext`) so it actually reaches the model, vs being ignored prose.

---

## Sequencing (atomic commits, per meta-governance — all reusable by forks)

1. **Commit 1:** `derive_lib.py` + `derive-check-advisory.py` + tests + fixtures + rule `## Enforcement` section.
2. **Commit 2:** register advisory PostToolUse hook in `settings.json` + propagation fix (`file-classes.toml`) + CLAUDE.md Core Principles bullet.
3. **Commit 3:** opt-in blocking variant (`derive-check-block.py`, flag-gated) + audit log + enable-it docs.
4. **Commit 4:** non-hook elevations (creator prompts, `/commit` check, optional `/write` critic dispatch).
5. **Commit 5 (Component 6):** plan-persist hook + output-length hook + `workflow.md`/`output-length.md` `## Enforcement` sections + Core Principles bullets + settings.json registration. Built after hookability verification.

(This repo is `~/github_repos/claude-code-my-workflow`, not `~/.claude/**` — the global `sync-global-config` rule does not apply; commits stay here.)

---

## Verification

- **Unit:** `python3 -m pytest .claude/hooks/test_derive_lib.py` — all pass.
- **Advisory hook (synthetic PostToolUse stdin):** non-existent read path → warning + exit 0; existing path → silent; write target → silent; `$macro` defined → silent, undefined → warning; escape hatch → silent; malformed JSON → exit 0 no output (fail-open); always exit 0.
- **Block variant:** flag absent → no-op; flag present → blocks only undefined-macro/unresolved-read; escape hatch + audit-log entry verified.
- **Component 6a:** synthetic Stop input where transcript shows plan-mode activity but no `quality_reports/plans/` write this session → turn-end blocked with remediation; with a plan file written → allowed; `stop_hook_active` true → exit early (no loop).
- **Component 6b:** synthetic Stop input with a >15-line final message and no `.md` write → advisory injected once; with a `.md` write this turn → silent.
- **Config integrity:** `json.load(open('.claude/settings.json'))` after edits; confirm `/tools propagate` listing now includes `.claude/settings.json`.
