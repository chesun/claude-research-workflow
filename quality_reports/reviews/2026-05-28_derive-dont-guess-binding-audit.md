# Why `derive-dont-guess` Doesn't Bind — Enforcement Audit

**Date:** 2026-05-28
**Reviewer:** workflow-audit
**Target:** `.claude/rules/derive-dont-guess.md` enforcement
**Status:** Active

---

## Bottom line

`derive-dont-guess` does not bind because it has no enforcement teeth: no hook fires on it, and its only scoring path lives inside critic-agent prompts (`coder-critic.md:210`, `writer-critic.md:173`) that are dispatched only by skills (`/analyze`, `/review`) or the orchestrated pipeline — never by a routine `Edit`/`Write`. In the dominant failure mode you describe ("just write me this `.do` file" in another repo, no `/analyze`, no `/review`), zero `derive-dont-guess` checks execute, and the documented `Commit >= 80` gate in `quality.md` is never wired into the `/commit` path (`commit/SKILL.md` has no score check). So the rule's sole delivery is the model reading the auto-loaded text and complying — which is exactly what fails. Its sibling `primary-source-first` binds because it has two registered hooks (`settings.json:73`, `settings.json:168`); `derive-dont-guess` was given a rubric but no trigger, and the asymmetry is not detectable to the user until a fabricated path breaks a script at runtime.

---

## Enforcement matrix

Mechanism legend: **HOOK** = deterministic PreToolUse/PostToolUse/Stop block or injection; **CRITIC** = scored deduction inside a critic agent prompt, fires only on explicit skill/orchestrator dispatch; **MIXED** = both; **PROSE-ONLY** = no hook and no critic deduction table, relies on the model reading the auto-loaded file. "Binds in ad-hoc usage?" = does anything fire on a plain `Edit`/`Write` with no skill and no orchestrator?

| Rule | Mechanism | Binds ad-hoc? | Evidence |
|---|---|---|---|
| primary-source-first | HOOK | **Y** | `settings.json:73` (PreToolUse check), `settings.json:168` (Stop audit) |
| destructive-actions | HOOK | **Y** (Bash) | `settings.json:88` (guard), `settings.json:152` (post-rewrite reminder) |
| stata-code-conventions | MIXED | **Y** (.do/.doh) | `settings.json:78` (balance check hook) + `coder-critic.md:86` |
| adversarial-default | MIXED | partial | `post-rewrite-verify.py:67` (hook, history-rewrite only) + `coder-critic.md:188`, `writer-critic.md:160` |
| **derive-dont-guess** | **CRITIC** | **N** | `coder-critic.md:210` (deduction table), `writer-critic.md:173`; no hook in `settings.json` |
| no-assumptions | CRITIC | **N** | `writer-critic.md:190`; no hook |
| anti-ai-prose | CRITIC | **N** | `writer-critic.md:199`, storyteller-critic; rule itself says "No hooks" |
| single-source-of-truth | CRITIC | **N** | `storyteller-critic.md:33`, `quality.md:150` |
| figures | CRITIC | **N** | coder-/writer-/storyteller-critic references; no hook |
| tables | CRITIC | **N** | coder-/writer-/storyteller-critic references; no hook |
| tikz-visual-quality | CRITIC | **N** | `storyteller-critic.md:49`; no hook |
| working-paper-format | CRITIC | **N** | `working-paper-format.md` "What the Writer-Critic Checks"; no hook |
| quality | CRITIC | **N** | scoring rubric consumed by critics; no hook |
| agents | CRITIC | **N** | orchestrator-mediated; no hook |
| r-code-conventions | CRITIC (weak) | **N** | `quality.md` R-Scripts table; rule filename not cited in any critic, no hook |
| python-code-conventions | CRITIC (weak) | **N** | `quality.md` Python table; rule filename not cited, no hook |
| verification-protocol | PROSE-ONLY (+ soft nudge) | **N** | `verify-reminder.py` (PostToolUse, non-blocking, does not name the rule) `settings.json:142` |
| logging | PROSE-ONLY (+ soft nudge) | **N** | `log-reminder.py` (Stop, non-blocking) `settings.json:163` |
| replication-protocol | PROSE-ONLY | **N** | no hook, no critic deduction table |
| decision-log | PROSE-ONLY | **N** | no hook, no critic deduction table |
| todo-tracking | PROSE-ONLY | **N** | no hook, no critic deduction table |
| workflow | PROSE-ONLY | **N** | no hook, no critic deduction table |
| meta-governance | PROSE-ONLY | **N** | no hook, no critic deduction table |
| output-length | PROSE-ONLY | **N** | no hook, no critic deduction table |
| revision | PROSE-ONLY | **N** | no hook, no critic deduction table |
| data-version-control | PROSE-ONLY | **N** | no hook, no critic deduction table |
| exploration-fast-track | PROSE-ONLY | **N** | no hook, no critic deduction table |
| exploration-folder-protocol | PROSE-ONLY | **N** | no hook, no critic deduction table |
| markdown-macdown-compat (global) | PROSE-ONLY | **N** | no hook, no critic deduction table |

Only **four** rules ever fire on a routine edit: the three PreToolUse `Edit|Write` hooks (`protect-files.sh` at `settings.json:68`, `primary-source-check.py` at `settings.json:73`, `stata-comment-balance-check.py` at `settings.json:78`) plus the Bash-scoped destructive-action guard. `derive-dont-guess` is in none of them.

---

## Root-cause chain

Ordered most load-bearing first.

1. **No hook, no deterministic trigger (the decisive cause).** `settings.json` registers no `derive-dont-guess` hook on any matcher; a `grep` of `.claude/hooks/` for `derive-dont-guess` returns nothing. Unlike `primary-source-first.md`, which opens with an explicit **Enforcement** section naming `primary-source-check.py` (PreToolUse) and `primary-source-audit.py` (Stop), `derive-dont-guess.md` has no Enforcement section at all. So on a plain `Edit`/`Write` — the path you hit in other repos — nothing intercepts a fabricated path or undefined macro. The rule is non-binding *by construction*.

2. **Critic-only enforcement is unreachable outside the orchestrated pipeline.** The `derive-dont-guess` deduction tables exist solely inside agent prompts: `coder-critic.md:210` (Critical −25 for a filepath that doesn't resolve on disk, −20 for an undefined Stata global) and `writer-critic.md:173` (Critical −25 for a numeric value not in tracked `tables/*.tex`). Those critics are dispatched only by `/analyze` Step 4 (`analyze/SKILL.md:40`), `/review --code` (`review/SKILL.md:17`), or the orchestrator (`workflow.md` §2 Step 3). Critically, `/write` — the natural ad-hoc authoring path — dispatches the Writer + humanizer but **not** `writer-critic` (`write/SKILL.md:20`), so even the obvious prose path skips the table. And for a `.do`-file request there is usually no skill at all, just a direct edit. Two further weaknesses compound this: the checks are judgment-based (the rubric *lists* grep commands the critic "should run" but nothing forces execution), and even when a critic runs it is read-only — it writes a scored advisory report and cannot block (`agents.md` §2 Separation of Powers; `coder-critic.md:10`). The `Commit >= 80` gate documented in `quality.md` §1 is never implemented: `commit/SKILL.md:13-71` has no score check, and `/tools commit` merely "notes" a score "if available" (`tools/SKILL.md:25`). So a fabricated entity ships uncaught unless the user *manually* runs `/review` first.

3. **Context dilution among ~28 rules.** Every `.claude/rules/*.md` auto-loads as a "project instruction" (confirmed by the system reminder labeling). That means the model receives ~28 rule files of context, most of them long, with `derive-dont-guess` competing for attention against `primary-source-first`, `adversarial-default`, `working-paper-format`, etc. CLAUDE.md does **not** elevate it: there is no `@import` anywhere in CLAUDE.md (grep for `@` returns nothing), and the only `rules/` mention is an incidental doc link at `CLAUDE.md:104`. A purely-advisory rule buried mid-stack in a large instruction set is the weakest possible delivery mechanism — it depends entirely on the model internalizing it on the relevant turn.

4. **Loading/propagation gaps into consumer repos.** Rules reach a fork via Claude Code's automatic `.claude/rules/` discovery (a harness feature, not anything the repo asserts or verifies), so a fork gets the file on clone and it auto-loads — but three silent-break points follow. (a) Propagation is a **manual, source-initiated push**: a fork only receives an updated `derive-dont-guess.md` if the source maintainer runs `/tools propagate .claude/rules/*.md` AND the fork is registered in `consumers.toml`, which is gitignored (`.gitignore:63`, `.claude/state/*`) — so a fork created by `git clone` is invisible to the propagation system and gets a one-time snapshot that then drifts. (b) `propagate.py` skips files marked DIVERGENT (consumer locally edited) or AMBIGUOUS (no sync record) per `tools/SKILL.md:261`, so a consumer that ever touched the file silently stops receiving updates with no error surfaced. (c) `settings.json` — the file that registers the *entire* hook layer — is not named in `file-classes.toml`'s explicit universal list nor in any documented propagate common-pattern, so it ships only on the initial clone; if a fork's `settings.json` drifts, even the hook-backed rules de-register. `derive-dont-guess` is unaffected by (c) only because it had no hook to lose. Net: a fork can carry a `derive-dont-guess.md` that looks authoritative but is arbitrarily stale and still has zero teeth.

---

## Why it's genuinely hard to hook

The honest detection problem: a citation is a self-announcing surface pattern — an `Author (Year)` regex mechanically finds every citation in a file delta or in turn-end prose, which is exactly why `primary-source-check.py` can demand a notes file. A "guessed" repo entity has **no intrinsic marker**. The only observable proxy is "references something that does not resolve on disk," and that proxy has irreducible blind spots:

- **The decisive asymmetry:** a correctly-derived entity and a lucky-guessed entity are byte-identical in the edit delta. A hook can only catch entities that *don't* resolve; it cannot distinguish a resolving path that was looked up from one that was guessed and happened to be right. The hook can enforce a strictly weaker proposition (*resolvability*) than the rule (*derivation*), and the gap is undetectable in principle.
- **Non-existent paths are routinely legitimate**, unlike non-existent citations. Output/`save`/`export` targets, files created later in a pipeline, and DVC/LFS-pointer or remote-only data paths all reference paths absent from the working tree *by design* (`stata-code-conventions.md` documents machine-branched, server-only `settings.do`). A naive "path must exist" block overfires on normal code, whereas "cited paper must have notes" rarely has a legitimate counterexample.
- **Repo entities are constructed dynamically** far more than citations are — globals/macros expand at runtime, paths are built by string concatenation, variable names are programmatically generated. Static delta scanning produces both misses and false positives.

So the rule's authors had a defensible cost/benefit call: unlike `destructive-actions` (a real data-loss incident drove a blocking hook) or `primary-source-first` (a documented error-propagation incident), a guessed entity's cost is a failed script run caught immediately at execution — low enough stakes that a prose rule plus the natural feedback loop of broken code was reasonable. The flaw is not that judgment; it is that the rule's own text claims it "binds like `primary-source-first`" while the enforcement layer gives it none of that sibling's teeth.

---

## Remediation options

Ranked by leverage-per-effort. The hook primitives already exist in-repo and are directly reusable: `primary-source-check.py:51-117` is a clean PreToolUse template (read stdin JSON, gate on `tool_name`, extract delta, run detector, emit `{"decision":"block"}` only on missing evidence, fail-open on exception); `primary_source_lib.py:436-460` already resolves a stem against the filesystem with `Path.is_dir()`/`glob`; `primary_source_lib.py:486-515` already inspects the session transcript for Read/Edit/Write of a given path; the escape-hatch (`primary-source-ok`) and bypass-flag + JSONL audit-log patterns are established convention.

**(i) PostToolUse advisory hook — grep new path-literals against the filesystem (RECOMMENDED FIRST).**

- *What it catches:* after the edit lands, extract literal path strings from the delta of `.do`/`.R`/`.py`/`.tex` via language-specific regexes — Stata `use`/`import`/`save`/`esttab using "<path>"` and `$global`/`` `local` `` refs; R `read_csv`/`read_dta`/`readRDS`/`source`/`saveRDS("<path>")`; Python `pd.read_*`/`np.load`/`open(Path("<path>"))`; LaTeX `\input`/`\include`/`\includegraphics{<path>}`. Resolve each against `CLAUDE_PROJECT_DIR`; for any that does NOT exist AND is not a write/output target, inject a non-blocking warning ("path X referenced but not found — derive it from settings or disclose it's new"). Catches the dominant failure mode: fabricated data-load paths, on *every* edit including ad-hoc, with no skill or orchestrator needed.
- *What it misses:* lucky guesses that resolve; runtime-constructed paths; entities other than paths (variable names, function signatures).
- *False-positive cost:* **low** — it is advisory (no block), and outputs/new files are legitimately non-existent so they're simply un-warned-on if classified as write targets. Must handle `MultiEdit` (reconstruct content across the edits list, as `stata-comment-balance-check.py:85-105` already demonstrates) or it silently misses multi-edit guesses.

**(ii) PreToolUse block — non-resolving READ/input data paths only (opt-in).**

- *What it catches:* block ONLY when a newly-added *read/input* path literal (Stata `use`/`include`, R `read_*`/`source`, Python `read_*`/`load`) resolves to neither an on-disk file nor a glob matching existing files, AND the macro/global it expands from is not defined anywhere in the repo (grep for `global <name>`/`local <name>`/`set <name>` before declaring unresolved). Restricting to read verbs (not writes) is what keeps it safe — a read of a nonexistent file is almost always a guess; a write is normal.
- *What it misses:* same blind spots as (i) plus anything built by concatenation.
- *False-positive cost:* **medium** — string-concatenated paths, runtime names, and globals defined in a remote-only/server `settings.do` will misfire. Needs an escape hatch `<!-- derive-ok: <reason> -->` mirroring `primary-source-ok`, a `BYPASS` env-var, and a JSONL audit log. **Gate behind a per-project opt-in flag in `.claude/state/`** because the false-positive surface needs field calibration before it's safe to ship on by default.

**(iii) Stop-audit "citation requirement" — analogous to `primary-source-audit.py`.**

- *What it catches:* at turn-end, scan assistant prose for the rule's own citation convention ("Path from `settings.do:14`", "Variable from `01_clean.do:47`"); when a code-file edit this session introduced new repo-entity references, verify the prose (or a session log) asserted a source line, and block turn-end if references were introduced with zero derivation citations. Reuses `extract_assistant_text` and the session-transcript walk already in `primary_source_lib.py:486-515,537-551`.
- *What it misses:* it verifies a citation was *made*, not that it is *true* — catches silent fabrication-without-disclosure, not wrong derivations. Weakest of the three on correctness.
- *False-positive cost:* low-medium; depends on how strictly "new repo-entity reference" is defined. Treat as optional belt-and-suspenders.

**(iv) Non-hook options (cheap, partial, ship alongside any of the above).**

- *Elevate the rule in CLAUDE.md:* add `derive-dont-guess` to the Core Principles list with a one-line summary and an explicit cross-link, so it's not competing as undifferentiated mid-stack context. Effort: trivial. Catches: marginal attention improvement only. FP cost: none.
- *Inject the rule into agent system prompts that run in ad-hoc usage:* the `coder`/`writer` *creator* prompts (not just the critics) should restate the derivation checklist, since creators run before any critic and in ad-hoc paths the critic never runs. Effort: low. Catches: shifts enforcement upstream to where the entity is actually written. FP cost: none.
- *Wire the documented commit gate:* add a `derive-dont-guess` pre-commit grep (option (i)'s detector in `--check` mode) to `/commit`, or implement the `quality.md` `>= 80` gate that is currently fiction. Effort: medium. Catches: fabrications at commit boundary. FP cost: same as the detector it wraps.
- *Tighten critic dispatch:* make `/write` dispatch `writer-critic` (it currently does not, `write/SKILL.md:20`). Effort: low. Catches: brings the prose-side table into the main authoring path. FP cost: none, but only helps when `/write` is actually used.

---

## Recommended next step

Ship remediation **(i)** — the PostToolUse advisory path-literal hook — first. It is the single highest-leverage change because it is the only option that fires in the exact ad-hoc path where violations occur (no skill, no orchestrator, no commit-skill), it targets the dominant real failure mode (fabricated data-load paths), it is cheap to build (the stdin/delta/`MultiEdit`/filesystem-resolution primitives all exist in `primary-source-check.py` and `primary_source_lib.py`), and being advisory it carries near-zero false-positive risk so it can ship on-by-default without per-project calibration. Pair it with the trivial non-hook step of registering the new hook in `settings.json` (and adding `.claude/settings.json` to `file-classes.toml`'s universal patterns so the enforcement layer actually propagates to forks). Defer the blocking PreToolUse variant (ii) behind an opt-in flag until the advisory hook's logs show its false-positive profile in the field.
