# Repo catch-up survey — where things stand

**Date:** 2026-10-11
**Sources read:** `CLAUDE.md`, `README.md`, `CHANGELOG.md`, `TODO.md` (last updated 2026-09-24), `decisions/` (ADR-0001–0003), session logs 2026-09-16 / 09-21 / 09-24, plans `2026-09-16_modernize-and-simplify-plan.md` and `2026-09-22_infra-survey-and-integration-method.md`, `2026-09-22_infra-survey_synthesis.md`, the archived work branch (plan `2026-09-15_claude-only-repo-split-and-personal-class.md`), git state, `.claude/settings.json`, `.claude/hooks/`.

## 1. What this repo is now

- A **strictly personal** research-workflow template (fork of Pedro Sant'Anna's `claude-code-my-workflow` via Hugo Sant'Anna's `clo-author`), re-targeted to research papers. Public release v0.1.0/v0.1.1 (2026-04-28).
- Three branches: `main` (universal trunk), plus `applied-micro` and `behavioral` overlays on origin.
- Remote: personal `chesun` account; git identity is the personal address. `main` matches `origin/main` (0 ahead/0 behind); working tree clean.
- **The consulting work has been split out** to a sibling consulting repo (enterprise-remote only, local for now). The guard and Copilot work done here is archived on two local-only branches, the work branch (`101bf43`) and `copilot-port` (`0ac057d`). The plan was to drop Copilot and run on Claude Code only (2026-09-15).
- `CLAUDE.md` header placeholders (`[YOUR PROJECT NAME]` etc.) are intentionally unfilled. This is the template, not a project.

## 2. Arc of work (high level)

| Period | Work |
|---|---|
| Feb–Apr 2026 | Restructure from lecture template to research template; universal trunk + overlays; four-rule epistemic stack; primary-source citation hook; v0.1.0 release + docs site |
| May 2026 | Destructive-action guardrails (after the 2026-04-25 `filter-repo` incident); class-aware propagation to 7 consumer repos + overlay sync; Stata block-comment fix; context-tightening (−30% always-on rules); derive-don't-guess advisory hook |
| late May 2026 | Evidence-gating discipline (Tier-1 normdiff recorder, coder-critic gate, Tier-2 citation-existence, Tier-3 advisory), distributed to all consumers |
| Jun–Jul 2026 | DVC pilot on BDD finished; lab DVC guide; citation-guard regex hardening (~344 tests, telemetry); **ADR-0001**: GO for bulk LFS (+ selective DVC) migration |
| Sep 2026 | Job change: a port to a Windows work laptop, then the repo split. **Modernize-and-simplify for Claude 5** (gates vs nags): pruned 10 nag hooks, ported `notify`/`protect-files` to Python. **ADR-0002**: mandatory independent review gate (`review-receipt-check.py`, fail-closed-escapably). Infra survey (integrate/adapt/skip). **ADR-0003**: reviewers on `fable`, workers on `opus` |

## 3. Decisions in force

- **ADR-0001** (2026-07-03): LFS for PDFs in every research repo (forward-only conversion); DVC selective; anti-dangling-pointer check mandatory where DVC is on.
- **ADR-0002** (2026-09-21, amended 09-22): staged code under `.claude/hooks/**`, `bin/**`, `.githooks/**` cannot be committed without a fresh review receipt in `quality_reports/reviews/`. Docs are advised only. Waiver: `REVIEW_WAIVE=1`. `review.required=true` is set here.
- **ADR-0003** (2026-09-24): critics/referees/editor/verifier/tikz-reviewer/`writer` on `fable`; coder/data-engineer/explorer/librarian/storyteller on `opus`; orchestrator inherits. Framed as an experiment to read out after the next few builds.
- Session-level (09-16): live projects are **`bdm_bic` and `belief_distortion_discrimination`, both behavioral**. The applied-micro overlay is frozen, and `tx_peer_effects_local` and four other consumers are dormant. Both overlays are kept. Everything must run on Windows and Mac.

## 4. Open work, in rough priority

1. **Modernize Track A, unfinished:** step 3 (mirror the hook prune + Python ports onto the `behavioral` overlay), step 4 (one-time `.claude/` update of the two live behavioral projects, with restore-point tags first), step 5 (retire `/tools propagate`, `sync-overlays`, `list-consumers` + `consumers.toml`).
2. **Voice preservation:** the one *committed* next build from the infra survey. It needs your exemplar-paper corpus. Design is settled (two per-paradigm feature-list profiles, additive and separate from `/humanize`, a non-supersedable floor, advisory checks). It also closes the anti-AI-prose academic carve-out TODO.
3. **ADR-0003 experiment read-out:** record findings by severity and fix rounds over the next builds; revisit the `writer` exception after voice.
4. Uncommitted candidates (pull only on need): `/verify-claims` blind claim-verifier (most likely second), `/audit-reproducibility`, `.claude/hooks/` Bash-write coverage gap, AEA README template, guard-test "vaccination".
5. Older backlog still listed in TODO: bulk LFS/DVC migration (ADR-0001), `/tools sync-status` script, citation-guard re-propagation, housekeeping automation, atomic-commit default, Quarto normalizer, `~/.claude/settings.json` drift. Several assume the multi-consumer lab setup, which the modernize plan is retiring. They are worth re-triaging against the 09-16 direction.
6. Waiting on you: BDD `data/PROVENANCE.md` fields; csac2026 CLAUDE.md fields.

## 5. Problems found during this survey

**A. Hooks are not running on this machine right now (High).** Every hook in `.claude/settings.json` launches with `python3`. In this shell `python3` resolves to the Microsoft Store stub (`…\Microsoft\WindowsApps\python3.exe`, PATH entry 30), which prints "Python was not found" and exits 49. The real interpreter (`…\AppData\Local\Python\bin\python3.exe`, installed 2026-10-08, PATH entry 32) comes later on PATH.
- Evidence: running `notify.py` directly through `python3` exits 49. A harmless probe `git update-ref -d refs/heads/zz-guard-probe-nonexistent` (the ref did not exist) was **not blocked**, though the guard's `_is_update_ref_delete` rule should block it. The guard logs every invocation, ALLOW or BLOCK, yet `.claude/state/destructive-action-guard.log` has 1 entry for today's ~10 Bash calls, against 9 on 2026-09-24.
- Consequence: Claude Code treats exit codes other than 0 and 2 as non-blocking errors, so the destructive-action guard, the primary-source citation gate, settings protection, and the review-receipt gate are all **silently failing open**. The review gate's fail-closed design can't help, because the interpreter never starts.
- Not explained: why the very first Bash call today was logged.
- Fix options: disable the `python3`/`python` App Execution Aliases (Settings → Apps → Advanced app settings → App execution aliases), or move `AppData\Local\Python\bin` ahead of WindowsApps on PATH. The modernize plan's intended `python`/`py` launcher fallback is not in `settings.json`. Changing that file is a settings edit, so it needs your go-ahead.

**B. Stale public docs (Low).** `README.md` (dated 2026-04-28) still describes the pruned hooks (`log-reminder`, `context-monitor`, `pre-compact`, `verify-reminder`, "11 scripts") and `/tools journal`. `CHANGELOG.md [Unreleased]` does not record the September modernize, review gate, or model routing.

**C. TODO header** still says `claude-code-my-workflow` (the pre-rename name). Cosmetic.
