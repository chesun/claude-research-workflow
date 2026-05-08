#!/usr/bin/env python3
"""
Context Usage Monitor Hook

Monitors context usage and provides progressive warnings:
- At 40%, 55%, 65%: Suggest /learn for skill extraction
- At 80%: Info-level warning (auto-compact approaching)
- At 90%: Caution-level warning (complete current task with full quality)

Hook Event: PostToolUse (on common tools)
Throttles to 60-second intervals when below warning threshold.

Measurement: hybrid token-based + tool-call proxy.

  Primary: parse `message.usage` from the most recent assistant message in
  the active session transcript JSONL (`transcript_path` from hook stdin).
  Sums input + cache_creation + cache_read for the real context size.
  Internally cached for REAL_CHECK_TIME_INTERVAL / REAL_CHECK_TOOL_CALL_INTERVAL
  to avoid disk churn — typical cost is ~5ms once per ~10 tool calls.

  Fallback: when transcript is missing, unreadable, or has no usage blocks
  yet (very early session), the legacy tool-call counter proxy is used.
  MAX_TOOL_CALLS=400 default after recalibration on 2026-05-06.

  See get_model_max_context() for context-window detection (env override,
  model-field [1m] marker, heuristic from observed token counts).
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Colors for terminal output
CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
MAGENTA = "\033[0;35m"
NC = "\033[0m"  # No color

# Thresholds (effective percentage, where 100% = auto-compact)
LEARN_THRESHOLDS = [40, 55, 65]
THRESHOLD_WARN = 80
THRESHOLD_CRITICAL = 90

# Throttle interval in seconds (skip checks if below threshold and recent check)
THROTTLE_INTERVAL = 60

# Floor at which the PreCompact fallback snapshot starts refreshing on every
# tool call. The Claude Code PreCompact hook silently bypasses when MCP servers
# are loaded (anthropics/claude-code#14111), so this fallback is the only
# guarantee that pre-compact-state.json exists before auto-compact fires.
SNAPSHOT_FLOOR = 60
# Throttle snapshot refreshes to avoid filesystem churn — refresh at most
# once every N seconds while past the floor.
SNAPSHOT_REFRESH_INTERVAL = 30

# Token-based real-context-reading cache. The transcript is parsed at most
# once per N tool calls or M seconds — whichever fires first. Reads at most
# the last 50 KB of the transcript file (tail-backward), so disk I/O is
# bounded regardless of session length.
REAL_CHECK_TOOL_CALL_INTERVAL = 10
REAL_CHECK_TIME_INTERVAL = 120
TRANSCRIPT_TAIL_BYTES = 50_000


def get_session_dir() -> Path:
    """Get the session directory for storing cache files."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if not project_dir:
        return Path.home() / ".claude" / "sessions" / "default"

    import hashlib
    project_hash = hashlib.md5(project_dir.encode()).hexdigest()[:8]
    session_dir = Path.home() / ".claude" / "sessions" / project_hash
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


def read_cache() -> dict:
    """Read the context monitor cache."""
    cache_file = get_session_dir() / "context-monitor-cache.json"
    if not cache_file.exists():
        return {}
    try:
        return json.loads(cache_file.read_text())
    except (json.JSONDecodeError, IOError):
        return {}


def save_cache(data: dict) -> None:
    """Save the context monitor cache."""
    cache_file = get_session_dir() / "context-monitor-cache.json"
    try:
        cache_file.write_text(json.dumps(data, indent=2))
    except IOError:
        pass


def estimate_context_percentage() -> float:
    """
    Estimate context usage as a percentage.

    This is a heuristic since we don't have direct access to Claude's context
    window. We use the tool call count as a proxy.

    Returns a value from 0-100 representing estimated context usage.
    """
    cache = read_cache()

    # Set session_start_time on the first tool call of a session. Preserved
    # across compactions; reset by session-reset.py on startup|clear.
    if "session_start_time" not in cache:
        cache["session_start_time"] = time.time()

    # Increment tool call counter
    tool_calls = cache.get("tool_calls", 0) + 1
    cache["tool_calls"] = tool_calls
    save_cache(cache)

    # Proxy fallback. Used only when token-based reading is unavailable
    # (very early session, transcript missing, parse error). Recalibration
    # history:
    #   v1: 500 (Bash|Task-only matcher, undercounted by ~3x)
    #   v2: 1500 (widened matcher, overshot — fired AFTER compaction)
    #   v3: 1000 (2026-05-04 evidence)
    #   v4: 400 (2026-05-06 — token-based primary added, proxy is now just
    #            a low-floor fallback; tighter default helps in the early
    #            session window where transcript may not yet have usage
    #            blocks. Override via CONTEXT_MONITOR_MAX_TOOL_CALLS.)
    MAX_TOOL_CALLS = int(os.environ.get("CONTEXT_MONITOR_MAX_TOOL_CALLS", "400"))

    percentage = min((tool_calls / MAX_TOOL_CALLS) * 100, 100)
    return percentage


def read_real_token_usage(transcript_path: str | None) -> tuple[int | None, str | None]:
    """Parse the most recent assistant message's usage block from the transcript.

    Reads at most TRANSCRIPT_TAIL_BYTES from the end of the file (tail-backward),
    walks the last few lines in reverse looking for an assistant message with
    a `usage` block, and returns the summed real context size in tokens
    along with the model name (or (None, None) if unavailable).

    Tolerates partial-write at end-of-file (per-line JSONDecodeError → skip).
    """
    if not transcript_path:
        return None, None
    try:
        path = Path(transcript_path)
        if not path.exists():
            return None, None
        size = path.stat().st_size
        if size == 0:
            return None, None
        read_n = min(size, TRANSCRIPT_TAIL_BYTES)
        with path.open("rb") as f:
            f.seek(size - read_n)
            tail = f.read(read_n)
        # Drop any partial UTF-8 sequence at the start; full lines tail down.
        text = tail.decode("utf-8", errors="ignore")
        lines = text.splitlines()
        for line in reversed(lines):
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = rec.get("message")
            if not isinstance(msg, dict) or msg.get("role") != "assistant":
                continue
            usage = msg.get("usage")
            if not isinstance(usage, dict):
                continue
            inp = int(usage.get("input_tokens", 0) or 0)
            cache_create = int(usage.get("cache_creation_input_tokens", 0) or 0)
            cache_read = int(usage.get("cache_read_input_tokens", 0) or 0)
            total = inp + cache_create + cache_read
            if total <= 0:
                continue
            return total, msg.get("model")
    except Exception:
        # Fail open — never break the hook on transcript read issues.
        return None, None
    return None, None


def get_model_max_context(model: str | None, real_tokens: int) -> int:
    """Determine the model's max context window in tokens.

    Resolution priority:
      1. CONTEXT_MAX_TOKENS env var (explicit override, integer in tokens)
      2. `[1m]` marker in the model field → 1,000,000
      3. Heuristic: observed real_tokens > 200_000 → must be 1M tier
      4. Opus 4.x family → default to 1,000,000 (Christina's setup)
      5. Fallback: 200,000 (Sonnet/Haiku default)
    """
    env_max = os.environ.get("CONTEXT_MAX_TOKENS")
    if env_max:
        try:
            v = int(env_max)
            if v > 0:
                return v
        except ValueError:
            pass
    if model and "[1m]" in model:
        return 1_000_000
    if real_tokens > 200_000:
        return 1_000_000
    if model and "opus-4" in model:
        return 1_000_000
    return 200_000


def compute_real_percentage(transcript_path: str | None, cache: dict, tool_calls: int) -> float | None:
    """Return real % of context used (token-based), or None if unavailable.

    Cached for REAL_CHECK_TIME_INTERVAL seconds AND
    REAL_CHECK_TOOL_CALL_INTERVAL tool calls — whichever expires first.
    """
    if not transcript_path:
        return None
    now = time.time()
    cached_pct = cache.get("last_real_percentage")
    if cached_pct is not None:
        last_time = cache.get("last_real_check_time", 0)
        last_calls = cache.get("last_real_check_tool_calls", 0)
        time_ok = (now - last_time) < REAL_CHECK_TIME_INTERVAL
        calls_ok = (tool_calls - last_calls) < REAL_CHECK_TOOL_CALL_INTERVAL
        if time_ok and calls_ok:
            return cached_pct
    real_tokens, model = read_real_token_usage(transcript_path)
    if real_tokens is None:
        return None
    max_ctx = get_model_max_context(model, real_tokens)
    pct = min((real_tokens / max_ctx) * 100, 100)
    cache["last_real_percentage"] = pct
    cache["last_real_tokens"] = real_tokens
    cache["last_real_max_ctx"] = max_ctx
    cache["last_real_model"] = model or ""
    cache["last_real_check_time"] = now
    cache["last_real_check_tool_calls"] = tool_calls
    save_cache(cache)
    return pct


def is_throttled(percentage: float) -> bool:
    """Check if we should skip this check due to throttling."""
    cache = read_cache()
    last_check = cache.get("last_check_time", 0)
    now = time.time()

    # If below warning threshold and checked recently, skip
    if percentage < THRESHOLD_WARN and (now - last_check) < THROTTLE_INTERVAL:
        return True

    # Update last check time
    cache["last_check_time"] = now
    save_cache(cache)
    return False


def get_shown_thresholds() -> dict:
    """Get which thresholds have already been shown in this session."""
    cache = read_cache()
    return {
        "learn": cache.get("shown_learn", []),
        "warn_80": cache.get("shown_warn_80", False),
        "warn_90": cache.get("shown_warn_90", False)
    }


def mark_threshold_shown(threshold_type: str, value: int | bool = True) -> None:
    """Mark a threshold as shown."""
    cache = read_cache()
    if threshold_type == "learn":
        shown = cache.get("shown_learn", [])
        if value not in shown:
            shown.append(value)
        cache["shown_learn"] = shown
    else:
        cache[f"shown_{threshold_type}"] = value
    save_cache(cache)


def _session_age_str(cache: dict) -> str:
    """Return human-readable elapsed session time, e.g. '~12m', '~1h32m'."""
    start = cache.get("session_start_time", time.time())
    elapsed = max(0, time.time() - start)
    if elapsed < 60:
        return "<1m"
    minutes = int(elapsed // 60)
    if minutes < 60:
        return f"~{minutes}m"
    hours = minutes // 60
    rem = minutes % 60
    return f"~{hours}h{rem}m" if rem else f"~{hours}h"


def _format_usage_line(cache: dict) -> str:
    """Single-line context-usage display. Prefers real token info when available,
    falls back to the tool-call proxy.
    """
    real_tokens = cache.get("last_real_tokens")
    real_max = cache.get("last_real_max_ctx")
    tool_calls = cache.get("tool_calls", 0)
    max_calls = int(os.environ.get("CONTEXT_MONITOR_MAX_TOOL_CALLS", "400"))
    if isinstance(real_tokens, int) and isinstance(real_max, int) and real_max > 0:
        # Real reading available — primary display
        return (
            f"   Real: {real_tokens / 1000:.1f}k / {real_max // 1000}k tokens"
            f"   |   Tool calls: {tool_calls}"
        )
    # Proxy only
    return f"   Tool calls (proxy): {tool_calls} / {max_calls}"


def format_learn_reminder(percentage: float, threshold: int) -> str:
    """Terse striking reminder at LEARN thresholds (40/55/65). Plain text — system-reminder block can't render ANSI."""
    cache = read_cache()
    age = _session_age_str(cache)
    return (
        "💡 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 💡\n"
        f"   CONTEXT AT {percentage:.0f}%\n"
        f"{_format_usage_line(cache)}\n"
        f"   Session age: {age}\n"
        "   → /learn anything reusable now — capture skills before compaction.\n"
        "💡 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 💡"
    )


def format_warn_80(percentage: float) -> str:
    """Striking 80% warning. Terse but visually heavy."""
    cache = read_cache()
    age = _session_age_str(cache)
    last_snap = cache.get("last_snapshot_time", 0)
    snap_str = (
        datetime.fromtimestamp(last_snap).strftime("%H:%M:%S")
        if last_snap else "(none yet)"
    )
    return (
        "🔴 ████████████████████████████████████████ 🔴\n"
        f"   ⚠️  CONTEXT AT {percentage:.0f}% — auto-compact approaching\n"
        f"{_format_usage_line(cache)}    Session age: {age}\n"
        f"   Snapshot fallback: ACTIVE (last: {snap_str})\n"
        "   ▶ Save key decisions to session log\n"
        "   ▶ Ensure plan status updated\n"
        "   ▶ Mark completed todos as done\n"
        "🔴 ████████████████████████████████████████ 🔴"
    )


def format_warn_90(percentage: float) -> str:
    """Striking 90% critical warning. Heaviest visual weight; compaction is imminent."""
    cache = read_cache()
    age = _session_age_str(cache)
    return (
        "🚨 ████████████████████████████████████████ 🚨\n"
        f"   ⛔ CONTEXT AT {percentage:.0f}% — COMPACTION IMMINENT\n"
        f"{_format_usage_line(cache)}    Session age: {age}\n"
        "   Complete current task with full quality.\n"
        "   Do NOT cut corners or skip verification.\n"
        "   No context is lost — snapshot preserves state across compaction.\n"
        "   ▶ Save key decisions to session log NOW\n"
        "   ▶ Update plan status\n"
        "   ▶ Mark completed todos as done\n"
        "🚨 ████████████████████████████████████████ 🚨"
    )


def capture_precompact_snapshot() -> None:
    """Write the same pre-compact-state.json that pre-compact.py would write.

    Used as a fallback so state is captured even when Claude Code's PreCompact
    hook silently bypasses on auto-compact (anthropics/claude-code#14111).
    Always overwrites — the latest snapshot is the one closest to compaction,
    and PreCompact (if it ever fires) runs after the last PostToolUse, so
    its write would still win.
    """
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if not project_dir:
        return

    # Import lazily so the main hook path stays cheap.
    hook_path = Path(__file__).parent / "pre-compact.py"
    if not hook_path.exists():
        return

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("pre_compact", hook_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        plan_info = mod.find_active_plan(project_dir)
        decisions = mod.extract_recent_decisions(project_dir)
        # Snapshot is enriched with metrics so post-compact-restore can
        # show "compacted at N tokens / X%". These fields don't exist in
        # older snapshots; consumers must default-handle missing keys.
        # Prefer real token info when available; fall back to proxy.
        cache_now = read_cache()
        max_calls = int(os.environ.get("CONTEXT_MONITOR_MAX_TOOL_CALLS", "400"))
        tool_calls = cache_now.get("tool_calls", 0)
        real_tokens = cache_now.get("last_real_tokens")
        real_max = cache_now.get("last_real_max_ctx")
        if isinstance(real_tokens, int) and isinstance(real_max, int) and real_max > 0:
            percentage = min((real_tokens / real_max) * 100, 100)
        else:
            percentage = min((tool_calls / max_calls) * 100, 100) if max_calls else 0
        state = {
            "trigger": "context-monitor-fallback",
            "plan_path": plan_info["plan_path"] if plan_info else None,
            "plan_status": plan_info["status"] if plan_info else None,
            "current_task": plan_info.get("current_task") if plan_info else None,
            "decisions": decisions,
            "tool_calls": tool_calls,
            "max_tool_calls": max_calls,
            "real_tokens": real_tokens,
            "real_max_ctx": real_max,
            "percentage": percentage,
            "session_start_time": cache_now.get("session_start_time"),
        }
        mod.save_state(state)
    except Exception:
        # Fail open — never block Claude due to a fallback bug.
        pass


def run_context_monitor() -> int:
    """Main monitoring logic."""
    # Read hook input
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, IOError):
        hook_input = {}

    transcript_path = hook_input.get("transcript_path") if isinstance(hook_input, dict) else None

    # Always increment the proxy counter and get its (fallback) %.
    proxy_percentage = estimate_context_percentage()

    # Try the real, token-based reading. Internally cached, so the transcript
    # is parsed at most once per ~10 tool calls or 2 minutes (whichever first).
    cache = read_cache()
    tool_calls = cache.get("tool_calls", 0)
    real_percentage = compute_real_percentage(transcript_path, cache, tool_calls)

    # Effective % drives all threshold checks: real if available, else proxy.
    percentage = real_percentage if real_percentage is not None else proxy_percentage

    # Refresh the PreCompact fallback snapshot continuously past SNAPSHOT_FLOOR.
    # This runs BEFORE the throttle check so a fresh snapshot is guaranteed
    # even when warnings are throttled. Self-throttled to SNAPSHOT_REFRESH_INTERVAL.
    if percentage >= SNAPSHOT_FLOOR:
        cache = read_cache()
        last_snapshot = cache.get("last_snapshot_time", 0)
        now = time.time()
        if (now - last_snapshot) >= SNAPSHOT_REFRESH_INTERVAL:
            capture_precompact_snapshot()
            cache["last_snapshot_time"] = now
            save_cache(cache)

    # Check throttling
    if is_throttled(percentage):
        return 0

    shown = get_shown_thresholds()

    # Switch from stderr-print to JSON `additionalContext` output —
    # PostToolUse stderr is unreliably surfaced in current Claude Code; the
    # JSON channel injects the message as a system-reminder block, which
    # IS visible. Verified empirically via post-rewrite-verify hook.
    def _emit_warning(message: str) -> None:
        payload = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": message,
            },
            "suppressOutput": True,
        }
        try:
            sys.stdout.write(json.dumps(payload))
            sys.stdout.flush()
        except Exception:
            pass

    # Check /learn thresholds (40%, 55%, 65%)
    for threshold in LEARN_THRESHOLDS:
        if percentage >= threshold and threshold not in shown["learn"]:
            _emit_warning(format_learn_reminder(percentage, threshold))
            mark_threshold_shown("learn", threshold)
            return 0  # Only show one message at a time

    # Check 90% threshold (critical). Snapshot already refreshed above via
    # SNAPSHOT_FLOOR logic — no need to call capture_precompact_snapshot here.
    if percentage >= THRESHOLD_CRITICAL and not shown["warn_90"]:
        _emit_warning(format_warn_90(percentage))
        mark_threshold_shown("warn_90", True)
        return 0  # Non-blocking warning (exit 2 would block Claude)

    # Check 80% threshold (info)
    if percentage >= THRESHOLD_WARN and not shown["warn_80"]:
        _emit_warning(format_warn_80(percentage))
        mark_threshold_shown("warn_80", True)
        return 0

    return 0


def main() -> int:
    """Main entry point."""
    return run_context_monitor()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Fail open — never block Claude due to a hook bug
        sys.exit(0)
