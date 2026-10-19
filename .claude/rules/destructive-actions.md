# Destructive Actions: Hook-Enforced Guardrails

**Scope (file-level):** all Bash invocations made by Claude Code, including those issued by subagents dispatched via the `Task` tool.

**Enforcement:**

- `.claude/hooks/destructive-action-guard.py` (PreToolUse, matcher `Bash`) — blocks the operations listed below.
- `.claude/hooks/post-rewrite-verify.py` (PostToolUse, matcher `Bash`) — soft-injects a verification reminder after history rewrites.

This rule is the codified enforcement layer for the prose-level guidance in `adversarial-default.md` and the system prompt's "executing actions with care" section. Those existed before this rule and were not enough — the 2026-04-25 incident still happened.

## Why this exists

On 2026-04-25 a session ran `git filter-repo` on a Dropbox-shared repo, which silently deleted coauthors' files, then force-pushed and reported the working tree unchanged without checking. The lesson: history rewrites need an enforced gate, and no success claim after one stands without `ls`/`du` evidence.

## Always-blocked commands (regardless of cwd)

These are blocked unconditionally; bypass requires explicit `BYPASS_SHARED_GUARD=1` env-var prefix on the command. The command must produce an audit trail (visible in shell history, session logs, and the guard's invocation log).

| Command | Reason |
|---|---|
| `git filter-repo` | History rewrite — silently mutates working tree; the 2026-04-25 incident |
| `git filter-branch` | Same risk class as filter-repo |
| `git push --force` / `-f` / `--force-with-lease` / `+refspec` | Overwrites remote history; coauthors lose work |
| `git rebase` (non-resumption) | History rewrite — interactive or range rebase mutates commit graph |
| `git reset --hard` | Discards uncommitted changes and resets HEAD |
| `git clean -f...` | Irreversibly deletes untracked files (--dry-run / -n allowed) |
| `git update-ref -d` | Removes references to commits; can orphan history |

**Resumption forms allowed without bypass:** `git rebase --continue`, `--abort`, `--skip`, `--quit`, `--edit-todo`, `--show-current-patch`. These don't mutate further; they finish or unwind an in-progress rebase.

## Path-conditional commands (blocked only on shared storage)

| Command | Block when path resolves under shared mount |
|---|---|
| `rm -r` / `-R` / `-rf` / `-fr` | Yes |
| `find ... -delete` | Yes |

`rm` without a recursive flag (single-file deletion) is not gated — friction would outweigh the protection.

## Settings.json write gate (Tier 3)

Bash writes to `.claude/settings.json` or `.claude/settings.local.json` (redirect, `tee`, `sed -i`, `mv`/`cp` onto it, or a scripted write from `python`/`node`/`ruby`/`perl`) are blocked, because `protect-files.py` sees only Edit/Write. Reads are not blocked. A chain containing such a write is blocked whole. Bypass with the same `BYPASS_SHARED_GUARD=1` prefix. Detection shapes and limits: `.claude/references/destructive-actions-detail.md`.

## Shared-storage prefixes

Anchored on canonical macOS cloud-storage mount points; substring matches (e.g., `/tmp/dropbox-clone/`) do *not* trigger the guard:

```
~/Library/CloudStorage/Dropbox*           (Dropbox-Personal, Dropbox-Work, ...)
~/Library/CloudStorage/GoogleDrive-*
~/Library/CloudStorage/OneDrive-*
~/Library/CloudStorage/Box-*
~/Library/Mobile Documents/com~apple~CloudDocs   (iCloud Drive)
~/Dropbox                                 (legacy direct mount)
```

Path resolution is realpath-aware: a symlink in a non-shared location that points into shared storage *will* trigger the guard. Tested case: `cd ~/foo && rm -rf bar` where `~/foo` symlinks into Dropbox → blocked.

**On Windows the delete check does not fire for OneDrive or Dropbox folders:** the prefixes above are macOS mount points.

## Chains, heredocs and unparseable commands

Every command of a chain (`;`, `&&`, `||`, `|`, `&`, newline) is checked by all three tiers, with `cd` carried across; wrappers (`env`, `command`, `time`, subshells, `git -C`/`-c`) do not hide a git subcommand; a heredoc body is checked only when a shell reads it. Commands inside `$(...)`, backticks, `eval` or `sh -c` strings are not unpacked, and on an unparseable command the shared-storage delete check fails open. Full parsing rules and known limits: `.claude/references/destructive-actions-detail.md`.

## Bypass mechanism

When the operation is genuinely intentional, prefix the command with the env-var:

```bash
BYPASS_SHARED_GUARD=1 git filter-repo --invert-paths --path output/legacy/
BYPASS_SHARED_GUARD=1 rm -rf ~/Library/CloudStorage/Dropbox/repo/dist/
```

The bypass covers the command it prefixes, as an env assignment does in the shell: in `cd repo && BYPASS_SHARED_GUARD=1 git rebase ...` the rebase is authorized, and in `BYPASS_SHARED_GUARD=1 git status && git push --force` the force push (and any later settings write or shared-storage delete) is still checked. On a shell that reads a heredoc (`BYPASS_SHARED_GUARD=1 bash <<EOF`) it covers the body.

The bypass:

- Is visible in shell history (audit trail).
- Is recorded in `.claude/state/destructive-action-guard.log` with `"bypass": true`.
- Does *not* exempt the user from the post-action verification protocol below — the PostToolUse hook still fires on history rewrites and injects the reminder.

**Conversational re-authorization is acceptable as a precursor** but does not by itself authorize the action — Claude must still re-issue the command with the env-var prefix. This is by design: the prefix is the audit anchor, not the conversation.

## Required post-action verification protocol

After any history rewrite (`filter-repo`, `filter-branch`, `rebase` non-resumption), the PostToolUse hook injects a verification reminder into the next agent turn. Claude must respond by running and capturing output of:

1. `ls -la <affected paths>` — confirm expected files still exist.
2. `du -sh <repo root>` — confirm size matches pre-rewrite snapshot (collect snapshot before bypassing, when feasible).

The agent is **not allowed** to narrate success (e.g., "working tree unchanged", "all files present") without `ls`/`du` output captured in its response. This is the adversarial-default rule applied to a specific failure mode: compliance is a positive claim that requires positive evidence.

## Audit log, coverage and limits

**Read** `.claude/references/destructive-actions-detail.md` for the full 2026-04-25 incident, the audit-log format, the subagent coverage assumption and what this rule does not cover (open it when debugging the guard or judging whether an operation is gated).

## Cross-references

- `.claude/rules/adversarial-default.md` — the prose-level rule this hook enforces. Compliance requires evidence.
- `.claude/hooks/destructive-action-guard.py` — implementation.
- `.claude/hooks/post-rewrite-verify.py` — verification reminder injection.
- `.claude/hooks/test_destructive_action_guard.py` — regression cases (136 as of 2026-10-14) covering both classes, bypass, chains, heredocs, the unparseable fallback, symlink resolution, and mount-point anchoring.
