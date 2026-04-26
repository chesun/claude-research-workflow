# Session Log: 2026-04-26 — Context-Monitor stderr fix + PreCompact fallback

**Status:** COMPLETED

## Objective

Diagnose and fix why the user did not see any pre-compaction notification when an auto-compact fired during a `va_consolidated` session. The PreCompact hook (`.claude/hooks/pre-compact.py`) was correctly configured at the project level in both `claude-code-my-workflow` and `va_consolidated`, and worked when invoked manually. Empirically it had not fired during the user's auto-compact event, and the parallel `context-monitor.py` warnings at 80% / 90% had also gone unnoticed.

## Diagnosis

Two distinct bugs:

1. **Claude Code auto-compact silently bypasses PreCompact when MCP servers are present** — matches [anthropics/claude-code#14111](https://github.com/anthropics/claude-code/issues/14111). The `va_consolidated` session has many MCP servers enabled (Notion, Gmail, Spotify, Mendeley, Consensus, etc.). Evidence: `~/.claude/sessions/088d2ff7/` contained `context-monitor-cache.json` (PostToolUse hook ran) and `log-reminder-state.json` (Stop hook ran) but no `pre-compact-state.json` — the PreCompact hook never executed.
2. **`context-monitor.py` printed warnings to stdout, not stderr.** PostToolUse hook stdout is shown to the model, not the user. The cache showed `shown_warn_80: true, shown_warn_90: true` — the warnings did fire, but to me, not to the user. That's why the user does not remember seeing any context warnings.

A third issue, calibration: `MAX_TOOL_CALLS = 150` in `context-monitor.py:94`. With Opus 4.7 1M-context, the same `va_consolidated` session reached 519 tool calls before auto-compact — meaning the 80% warning at call 120 was crying wolf by ~280 tool calls.

## Changes Made

| File | Change | Reason |
|------|--------|--------|
| `claude-code-my-workflow/.claude/hooks/context-monitor.py:196,202,208` | `print(...)` → `print(..., file=sys.stderr)` for all three warning paths | Hook stdout goes to model; user-visible warnings must go to stderr (matches `pre-compact.py:206` convention) |
| `claude-code-my-workflow/.claude/hooks/context-monitor.py` | Added `capture_precompact_snapshot()` helper invoked at the 90% threshold | Even when Claude Code's PreCompact silently bypasses on auto-compact, state is captured by the PostToolUse path so `post-compact-restore.py` can still restore plan + task on the next session |
| `claude-code-my-workflow/.claude/hooks/context-monitor.py:94` | `MAX_TOOL_CALLS = 150` → `int(os.environ.get("CONTEXT_MONITOR_MAX_TOOL_CALLS", "500"))` | Calibrate to observed ~500 tool calls before auto-compact on Opus 4.7 1M; env var allows per-project override |
| `va_consolidated/.claude/hooks/context-monitor.py` | Mirrored from `claude-code-my-workflow` (identical copies of these hooks across both repos) | Both repos run the same hook code; sync is byte-for-byte |

## Design Decisions

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| Snapshot fallback in `context-monitor.py` rather than a new hook event | Add a separate `pre-auto-compact-watcher.py` hook on PostToolUse | `context-monitor.py` already runs on PostToolUse and tracks the 90% threshold — adding state capture there avoids a second hook invocation on every tool call |
| `"trigger": "context-monitor-fallback"` in fallback snapshot | Use the same `"auto"` trigger as the real PreCompact path | Distinguishable trigger lets future log analysis tell which path captured the state, and `post-compact-restore.py` does not key on `trigger` so behavior is identical at restore time |
| Env-var override for `MAX_TOOL_CALLS` | Hard-code a single value | Heuristic varies wildly by tool-call payload size; env var is the smallest-blast-radius escape hatch |
| Did NOT promote PreCompact hook to global `~/.claude/settings.json` | Move the config up to global so all projects get it | Per user instruction — they want it as a workflow feature, not a global setting; auto-compact bypass bug would not be fixed by going global anyway |

## Verification Results

| Check | Result | Status |
|-------|--------|--------|
| Manual invocation of `context-monitor.py` at 80% writes warning to stderr | Yellow message rendered on stderr | PASS |
| Manual invocation at 90% writes warning to stderr AND creates `pre-compact-state.json` | Both observed: red warning on stderr, JSON file with plan path + current task on disk | PASS |
| Snapshot JSON has `"trigger": "context-monitor-fallback"` | Verified | PASS |
| `pre-compact.py` still works when invoked manually (not regressed) | Stderr output + state file as before | PASS |
| `claude-code-my-workflow` and `va_consolidated` copies of `context-monitor.py` byte-identical | `diff` returns empty | PASS |

## Learnings & Corrections

- [LEARN:hooks] Claude Code PostToolUse hook output convention: stdout → model, stderr → user. For user-visible warnings, always use `file=sys.stderr`. The `pre-compact.py:206` comment ("PreCompact ignores stdout; stderr is shown to user") was the only place this convention was documented in this repo.
- [LEARN:hooks] PreCompact is unreliable on auto-compact when MCP servers are present (anthropics/claude-code#14111). Defensive design: have a PostToolUse-based fallback that snapshots state at a high threshold, so `post-compact-restore.py` works regardless of which compaction path Claude Code takes.
- [LEARN:heuristic] The `MAX_TOOL_CALLS` heuristic must be tuned per context-window size. The original 150 was set for the 200K-context era; under 1M-context Opus 4.7, observed auto-compact happens around 500 tool calls.

## Open Questions / Blockers

- None blocking. Calibration of `MAX_TOOL_CALLS=500` is empirical from a single `va_consolidated` session; if other sessions auto-compact at very different tool-call counts, the env-var override is the lever.

## Next Steps

- None. Verified end-to-end and synced.
