# Session Log: 2026-05-04 — Context-monitor visibility + MAX recalibration + compaction logging

**Status:** COMPLETED

## Objective

User reported: "still not seeing any context usage warnings or precompact hook firings before compaction while working in belief_distortion_discrimination."

Diagnose why and fix. Three coupled fixes shipped:

1. Visibility — switch hook output channel from `sys.stderr` to JSON `additionalContext`.
2. Threshold recalibration — `MAX_TOOL_CALLS` 1500 → 1000 based on empirical compaction point.
3. Durable cross-session compaction event log for ongoing calibration.

## Changes Made

| File | Change | Reason |
|---|---|---|
| `.claude/hooks/context-monitor.py` | (a) `print(..., file=sys.stderr)` → JSON `hookSpecificOutput.additionalContext` for all three warning tiers (40/55/65 LEARN, 80 WARN, 90 CRITICAL). (b) `MAX_TOOL_CALLS` default 1500 → 1000. (c) New striking format functions with unicode bars + emoji + metrics (no ANSI; system-reminder block can't render colors). (d) Track `session_start_time` (set on first tool call if missing). (e) Snapshot enriched with `tool_calls`, `max_tool_calls`, `percentage`, `session_start_time`. | PostToolUse stderr is unreliably surfaced in current Claude Code — empirical evidence: belief_distortion_discrimination cache showed `shown_learn=[40,55,65]` (warnings WERE printed) but user reported not seeing them. JSON channel is reliable (verified via post-rewrite-verify in prior session). Recalibration: belief_distortion_discrimination compacted at ~1000 tool calls; with MAX=1500 the 80%/90% warnings would have fired AFTER compaction. |
| `.claude/hooks/pre-compact.py` | (a) Read context-monitor cache to enrich snapshot with metrics. (b) New `append_compaction_log()` writes append-only JSONL to `~/.claude/sessions/<hash>/compactions.jsonl`. (c) Comment update on stderr-print noting it's now best-effort. | Durable cross-session log for ongoing MAX calibration. Snapshot enrichment lets post-compact-restore show exact compaction metrics. |
| `.claude/hooks/post-compact-restore.py` | (a) `print(message)` → JSON `hookSpecificOutput.additionalContext` for SessionStart event. (b) New striking restoration format showing "Compacted at: N / M tool calls (X%)". (c) Belt-and-suspenders compaction log: appends `:restored`-trigger entry to JSONL when reading the snapshot, so coverage is preserved if pre-compact bypassed (Claude Code bug #14111). | Visibility + cross-session metrics. The restoration message is now the load-bearing user-facing cue (since pre-compact stderr is unreliable). |
| `.claude/hooks/session-reset.py` | Also clear `session_start_time` and `last_snapshot_time` on `startup\|clear`. | Ensure new fields re-init cleanly on fresh sessions. |

## Design Decisions

| Decision | Alternatives Considered | Rationale |
|---|---|---|
| Use JSON `additionalContext` channel for warnings | (a) Keep stderr; (b) Force exit code 2 to surface as PreToolUse-style error | We've seen the JSON channel work reliably in this very session (post-rewrite-verify). Stderr is the channel that's silently captured. Exit code 2 would block the underlying tool — wrong semantics for a non-blocking warning. |
| Lower `MAX_TOOL_CALLS` default 1500 → 1000 | (a) Keep 1500 + document override; (b) Drop further to 800 | Single empirical data point (belief_distortion_discrimination at ~1000) — but the asymmetric cost favors over-warning. 1000 gives 100-200 call buffer at 80/90%. The new compactions.jsonl log will produce real calibration data within weeks. |
| Compactions.jsonl with two writers (pre-compact + post-compact-restore) | Single writer in pre-compact only | PreCompact silently bypasses on auto-compact when MCP servers are present (Claude Code bug #14111). Belt-and-suspenders: post-compact-restore writes a `:restored`-trigger entry when reading the snapshot, ensuring coverage. Some compactions may produce two log entries; downstream analysis can dedupe by `session_start_time`. |
| Striking format: unicode bars + emoji, no ANSI | (a) Keep ANSI colors; (b) ASCII-only | System-reminder blocks render as plain text — ANSI codes appear as literal escape sequences. Emoji + unicode bars work in plain text and create visual weight. User explicitly requested visual striking-ness; emoji is in scope per direct authorization. |
| Snapshot enrichment fields are optional (default-handle missing) | Migration to enforce schema | Old snapshots from prior sessions (or downstream repos pre-sync) lack the new fields. post-compact-restore handles missing keys gracefully. No migration needed. |

## Incremental Work Log

**21:00 UTC:** User reported missing warnings in belief_distortion_discrimination. Diagnosed:
- Cache at `~/.claude/sessions/056b1cbe/context-monitor-cache.json`: `tool_calls=994`, `shown_learn=[40,55,65]`. Warnings WERE marked as shown (printed) but user couldn't see them.
- Snapshot file at same dir: present, last updated 21:12, written by `context-monitor-fallback`.
- Hypothesis: PostToolUse stderr unreliably surfaced. JSON `additionalContext` is the working channel (verified via post-rewrite-verify).

**21:15 UTC:** Confirmed hypothesis by inspecting workflow's own session cache (different project hash; current session at 12% — under threshold so no warnings expected/issued).

**21:20 UTC:** User confirmed terse + visually striking format. Drafted three-tier visual hierarchy:
- 40/55/65 (LEARN): 💡 + thin unicode bar `━`
- 80 (WARN): 🔴 + thick block `█`
- 90 (CRITICAL): 🚨 + thick block + escalation language
- Restoration: 🔄 + thin bar + metrics

**21:25 UTC:** User asked about pre-compaction metrics — what tool count, what state. Showed what we know NOW from the cache + snapshot, flagged what we DON'T know (no historical record of compaction events). Proposed adding compactions.jsonl + enriched snapshot.

**21:30 UTC:** User pointed out empirical: compaction in belief_distortion_discrimination "perhaps around 1000 tool calls". With MAX=1500, that would mean 80% (1200) and 90% (1350) fire AFTER compaction — explaining why those tiers are `False` in the cache. Recommended dropping default to 1000.

**21:35 UTC:** Implementation. First Edit on context-monitor.py left orphaned triple-quote causing syntax error. Caught immediately by smoke test. Fixed.

**21:40 UTC:** Smoke-tested at 65% (LEARN tier) and 90% (CRITICAL tier). Both produced valid JSON output with the striking format and correct metrics. Tested full pre-compact → snapshot → post-compact-restore → JSONL flow end-to-end with a fake project tempdir; confirmed:
- Snapshot includes new metric fields
- compactions.jsonl gets both pre-compact entry and post-compact-restore `:restored` entry
- post-compact-restore JSON output includes "Compacted at: 950 / 1000 tool calls (95%)"

**21:45 UTC:** All hooks compile cleanly; existing test suites (primary-source-lib, destructive-action-guard) still pass — no regressions.

**21:50 UTC:** Committed `16cc557` to workflow main. Cherry-picked to applied-micro (`f5b667f`) and behavioral (`21b9ed7`). Pushed all three.

**22:00 UTC:** Synced to 7 downstream repos: bdm_bic, belief_distortion_discrimination, belief_distortion_discrimination_audit, csac, csac2025, tx_peer_effects_local, va_consolidated. All clean pushes.

## Learnings & Corrections

- **[LEARN:hooks]** PostToolUse stderr is unreliable in current Claude Code UI. Default to JSON `hookSpecificOutput.additionalContext` for any user-facing message. Same applies to SessionStart hooks (post-compact-restore was using `print()` to stdout, also switched to JSON channel for consistency).
- **[LEARN:hooks]** `system-reminder` blocks render as plain text — ANSI escape codes appear as literal sequences. For visual weight: unicode block elements (`█`), unicode box-drawing (`━`, `┏`, `┗`), and emoji all work and create attention-grabbing formatting.
- **[LEARN:calibration]** Heuristic constants tuned without empirical data drift. The 1500 default came from a `500 → 3x multiplier` recalibration when the matcher was widened — but the multiplier was an estimate, not measured. Single real data point (belief_distortion_discrimination at ~1000) shifted the default. Compactions.jsonl now provides ongoing data so future calibrations are evidence-based, not estimates.
- **[LEARN:cache]** Cache files in `~/.claude/sessions/<project_hash>/` persist across sessions and across compactions — only `session-reset.py` (matcher `startup|clear`) clears them. When adding new cache fields, update session-reset.py too or stale fields leak across sessions.
- **[LEARN:partial-edit]** Edit tool only replaces the matched substring. When refactoring a multi-line function with format changes (e.g., changing return-statement form), make sure the closing brackets/quotes are part of the matched region or you'll get an orphaned tail. Caught the syntax error immediately via smoke test, but cost a debug cycle.

## Verification Results

| Check | Result | Status |
|---|---|---|
| All 4 changed hooks compile | yes | PASS |
| Existing test suites still pass (71 destructive-action + primary-source) | yes | PASS |
| Smoke test at 65% LEARN threshold produces JSON additionalContext | yes (with metrics) | PASS |
| Smoke test at 90% CRITICAL threshold produces JSON | yes | PASS |
| pre-compact.py writes enriched snapshot + JSONL entry | yes | PASS |
| post-compact-restore.py reads snapshot + emits JSON + writes JSONL | yes | PASS |
| Striking format renders correctly (unicode + emoji + metrics) | yes | PASS |
| Workflow main pushed; both overlays cherry-picked + pushed | yes (3 commits) | PASS |
| All 7 downstream repos synced + pushed | yes | PASS |

## Open Questions / Blockers

- [ ] **MAX_TOOL_CALLS=1000 is one data point.** Other projects may compact at different counts depending on tool-mix. Real calibration depends on accumulating compactions.jsonl data over weeks.
- [ ] **JSON channel for PreCompact event itself.** I left pre-compact.py's stderr print as best-effort; the user-visible cue now lives in post-compact-restore (which fires after). Confirm this UX is acceptable: warnings appear at 40/55/65/80/90 BEFORE compaction; restoration summary appears AFTER. The actual compaction moment itself is silent.

## Next Steps

- [ ] After ~2 weeks of normal use across the 10 instrumented projects, run the calibration query (in the most recent message) on accumulated `compactions.jsonl` data and re-tune MAX_TOOL_CALLS if median diverges from 1000.
- [ ] Future enhancement consideration: emit a `<system-reminder>` *during* the next user turn after a session ends, summarizing tool-call burn rate vs MAX. Useful for projects whose tool-mix differs systematically from the default. Out of scope for this fix.
