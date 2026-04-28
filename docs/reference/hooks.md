# Hooks

Hooks are programs that fire automatically at Claude Code lifecycle events. They live in `.claude/hooks/` and are wired up in `.claude/settings.json`. See [`../glossary.md`](glossary.md#hook) for the platform mechanics.

This page is a catalogue. The full hook-event semantics, exit codes, and configuration syntax are in the [Claude Code Hooks documentation](https://code.claude.com/docs/en/hooks).

---

## The 11 hooks

### Citation grounding (2)

| Hook | Event | What it does | Escape hatch |
|---|---|---|---|
| `primary-source-check.py` | PreToolUse (Edit, Write) | Blocks edits to scoped files (`decisions/`, `quality_reports/plans/`, `quality_reports/session_logs/`, `quality_reports/reviews/`, `theory/`, etc.) when those edits cite a paper that lacks reading-notes evidence. Four-filter Author-Year regex (built-in blocklist, sentence-start filter, hyphenated-name decomposition, project allowlist). | `<!-- primary-source-ok: stem -->` in the delta |
| `primary-source-audit.py` | Stop | Audits the agent's conversation prose at turn-end for the same. Conversation citations subject to the same rule as file citations. Respects `stop_hook_active` to avoid loops. | `<!-- primary-source-ok: stem -->` in the assistant message |

Shared logic in `.claude/hooks/primary_source_lib.py`. See `.claude/rules/primary-source-first.md` for full semantics. The blocklist excludes role-words ("author", "coauthor", "editor", etc.) and standard non-surname capitalized words ("Spring", "Table", "Cohort", etc.) to prevent false-positives.

### Session logging (1)

| Hook | Event | What it does |
|---|---|---|
| `log-reminder.py` | Stop | Tracks how many turns have passed without an edit to any session-log file. After 10 turns, blocks turn-end with a reminder to append progress to the most recent session log. Safety net for the incremental-logging convention in `.claude/rules/logging.md`. |

### Verification (1)

| Hook | Event | What it does |
|---|---|---|
| `verify-reminder.py` | PostToolUse (Edit, Write) | Prompts verification after edits to artifacts that should be verified (paper LaTeX → recompile; analysis script → re-run; etc.). Throttles to avoid spam. |

### Context survival (3)

| Hook | Event | What it does |
|---|---|---|
| `context-monitor.py` | PostToolUse (Bash, Task) | Estimates context usage from tool-call count. Emits warnings on `stderr` (visible to user) at 40 / 55 / 65 / 80 / 90 % thresholds. At 90%, also writes a `pre-compact-state.json` snapshot as a fallback for [`anthropics/claude-code#14111`](https://github.com/anthropics/claude-code/issues/14111) (PreCompact silently bypasses on auto-compact under MCP-server load). Heuristic `MAX_TOOL_CALLS=500` env-overridable via `CONTEXT_MONITOR_MAX_TOOL_CALLS`. |
| `pre-compact.py` | PreCompact | Captures session state (active plan path + status + current task + recent decisions) to `~/.claude/sessions/<hash>/pre-compact-state.json` before context compaction. Output goes to `stderr` so the user sees it. |
| `post-compact-restore.py` | SessionStart (matcher: `compact|resume`) | Reads the pre-compact-state snapshot at the start of a fresh session post-compact (or resume) and surfaces the active plan, current task, and recent decisions to the agent. Bridge across the compaction boundary. |

### File protection (1)

| Hook | Event | What it does |
|---|---|---|
| `protect-files.sh` | PreToolUse (Edit, Write) | Blocks Edit/Write on files matching protected patterns (currently `settings.json`). Customize the pattern list in the script for per-project protection. |

### Notification (1)

| Hook | Event | What it does |
|---|---|---|
| `notify.sh` | Notification | macOS notification when Claude Code's native notification event fires. Useful when running long tasks in the background. |

---

## Test infrastructure

`.claude/hooks/test_primary_source_lib.py` — 27 regression tests covering the four-filter citation extractor (built-in blocklist, sentence-start filter, hyphenated-name decomposition, project allowlist). Run with `python3 test_primary_source_lib.py` from the `.claude/hooks/` directory. New regression tests should be added when fixing false-positive or false-negative bugs.

---

## Configuration

Hooks are wired up in `.claude/settings.json`'s `hooks` block. Each entry maps an event (PreToolUse, PostToolUse, Stop, etc.) and optionally a matcher pattern (e.g., `Edit|Write`) to a list of commands. See `.claude/settings.json` for the current configuration.

Per-project customizations go in `.claude/settings.local.json`, which is gitignored. Use this to add project-specific hooks without bloating the public template.

---

## Hook output conventions in this workflow

- **Block**: exit code 2, error message on `stderr`, JSON response if needed (e.g., `primary-source-check.py` returns a structured rejection).
- **Warn**: exit code 0, message on `stderr` (visible to user), no block.
- **Side effect only**: exit code 0, no message, just file writes (e.g., `context-monitor.py` updating its cache, `pre-compact.py` writing the state snapshot).

The convention `stderr → user, stdout → model` is followed throughout: warnings users need to see go to stderr (visible in their terminal); structured information for the agent goes to stdout (consumed by Claude Code).

---

## Adding a new hook (for forkers)

To add a hook:

1. Write the script in `.claude/hooks/<name>.{py,sh}`. Make executable with `chmod +x`.
2. Wire it up in `.claude/settings.json` under the appropriate event.
3. Decide on output convention: stderr for user-facing warnings, exit code 2 for blocks, stdout only for agent-facing data.
4. Write tests if the hook has any non-trivial logic (esp. regex extraction or path matching).
5. Document the hook here.

For Python hooks, the standard pattern: read JSON from stdin, do the check, write to stderr/stdout, exit with appropriate code. See existing hooks for examples.

---

## Cross-references

- [`rules.md`](rules.md) — rules whose enforcement is automated by hooks (especially `primary-source-first.md`)
- [`../concepts/epistemic-rules.md`](../concepts/epistemic-rules.md) — depth on the four-rule stack; hook enforcement is one mechanism
- [`../glossary.md`](glossary.md#hook) — platform-level definition with link to Claude Code hooks docs
- [Claude Code Hooks documentation](https://code.claude.com/docs/en/hooks) — official hook event list and configuration syntax
