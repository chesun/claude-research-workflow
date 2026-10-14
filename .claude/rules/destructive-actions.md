# Destructive Actions: Hook-Enforced Guardrails

**Scope (file-level):** all Bash invocations made by Claude Code, including those issued by subagents dispatched via the `Task` tool.

**Enforcement:**

- `.claude/hooks/destructive-action-guard.py` (PreToolUse, matcher `Bash`) — blocks the operations listed below.
- `.claude/hooks/post-rewrite-verify.py` (PostToolUse, matcher `Bash`) — soft-injects a verification reminder after history rewrites.

This rule is the codified enforcement layer for the prose-level guidance in `adversarial-default.md` and the system prompt's "executing actions with care" section. Those existed before this rule and were not enough — the 2026-04-25 incident still happened.

## Why this exists

On 2026-04-25, a Claude Code session ran `git filter-repo --invert-paths` on a Dropbox-shared git repo (3 coauthors) to shrink it for a failing push. The operation rewrote history *and* silently rewrote the working tree, deleting `output/dta/most_recent/` and several dated regression-export folders. Dropbox propagated the deletion to all coauthors. The session then force-pushed to origin, making the rewrite permanent on GitHub.

The session log claimed *"Working tree = 8.8 GB unchanged (all .dta files still present)"* — never verified with `ls`/`du`, and false. The deletion surfaced 8 days later when a coauthor noticed missing files.

Two failure modes compounded:

1. **No enforced gate on history rewrites** despite prose-level rules saying "destructive operations need explicit re-authorization."
2. **False-success narration** — the agent reported success without producing positive evidence (`ls`/`du` output) of what the rule actually required.

This rule installs hooks that close both gaps.

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

The companion hook `protect-files.py` (formerly `protect-files.sh`) is registered only on the `Edit|Write` matcher and cannot observe Bash invocations. Without Tier 3, any of the following would silently bypass it:

```bash
echo '{...}' > .claude/settings.json
echo '{...}' >> .claude/settings.json
echo '{...}' | tee .claude/settings.json
sed -i 's/foo/bar/' .claude/settings.json
mv tmp.json .claude/settings.json
cp template.json .claude/settings.json
python3 -c "Path('.claude/settings.json').write_text('{}')"
node -e "require('fs').writeFileSync('.claude/settings.json', '{}')"
```

Tier 3 detects all five write shapes (stdout redirection, `tee`, `sed -i`, `mv`/`cp` overwrite, scripted write) when the target path matches `.claude/settings.json` or `.claude/settings.local.json`. Reads (`cat`, `head`, `jq`, `grep`, `diff`, `python json.load`) are not blocked.

| Command shape | Detection method |
|---|---|
| `> path` / `>> path` | regex match on redirect operator followed by settings path |
| `tee path` / `tee -a path` | regex match on `tee` invocation with settings path as argument |
| `sed -i ... path` | per-pipeline-segment match on `sed`+`-i` flag with settings path in segment |
| `mv X path` / `cp X path` | last positional argument of `mv`/`cp` matches settings path |
| Scripted write | `python`/`node`/`ruby`/`perl` + settings path + write call (`write_text`, `json.dump`, `open(..., 'w')`, `writeFileSync`, `.write(...)`, etc.) |

Tier 3 is heuristic — Bash is too expressive to classify perfectly. Documented limitations:

- **Indirection.** A Python script that imports a module containing the settings path won't be caught by substring detection. Same for environment-variable indirection where the path is constructed at runtime.
- **Compound commands.** When a multi-command chain (`A && B`) contains a settings write in any segment, the entire chain is blocked. The hook can't surgically allow parts of a compound command. If you need to preserve the rest, run the safe parts separately.
- **`.vscode/settings.json` and similar.** Detection anchors on `.claude/settings`, so other tools' settings.json files are not gated.

**Bypass uses the same `BYPASS_SHARED_GUARD=1` env-var prefix.** Legitimate use cases (writing a new hook, modifying permissions, applying a vetted patch) are expected to use it. The workflow's own sync scripts (when shipping hooks across repos) prefix all settings.json writes with the bypass.

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

## `cd X && ...` chain handling

The guard parses leading `cd <path> &&` directives in the command string and updates the effective cwd before checking path arguments. Concretely, `cd ~/dropbox-repo && rm -rf output/` is evaluated as `rm -rf ~/dropbox-repo/output/` for the purposes of the path check.

This handles the realistic case where Claude prefixes a `cd` to localize a destructive command.

## Chains, heredocs and unparseable commands

- **Every command of a chain is checked** by all three tiers (always-blocked, settings write, shared-storage delete), with the working directory carried across `cd` commands: commands joined by `;`, `&&`, `||`, `|`, `&` or a newline, split on unquoted operators only, so a quoted commit message containing `; git reset --hard` is not a command. Before 2026-10-14 only the first command was checked, so `echo hi && git filter-repo ...` got through.
- **Wrappers and git's global options do not hide the subcommand:** `env [-u NAME] [--] A=1 git ...`, `command git ...`, `time -p git ...`, `(git ...)`, `{ git ...; }`, `/usr/bin/git`, `git.exe`, and every `git -C dir` / `git -c k=v` / `git --flag` before the subcommand are read as the git command they run.
- **Backslash continuations** are joined before the command is split.
- **Heredoc bodies are data unless a shell reads them.** Only an unquoted `<<` opens a heredoc (`echo "<<EOF"` does not). A body is checked as commands when a shell (`bash`, `sh`, `zsh`, `dash`, `ksh`, `fish`, `pwsh`, `powershell`) is named anywhere on its line (`bash <<EOF`, `sh -s <<EOF`, `cat <<EOF | bash`). Any other body (a commit message, a file being written, a Python script) is skipped. An unterminated `<<` removes nothing.
- **Unparseable commands** (an unbalanced apostrophe, typically): each segment is checked with the same always-blocked predicates and the settings gate. The shared-storage delete check stays fail-open there, as it always was.
- **Known limits:** commands inside `$(...)`, backticks, `eval "..."` or `sh -c '...'` strings are not unpacked, and neither is a script for another interpreter (`python - <<EOF` that calls `subprocess`). `sudo`, `timeout`, `nice` and `xargs` are not treated as wrappers. On the unparseable path the shared-storage delete check is fail-open. The shared-storage prefixes are macOS mount points, so on Windows the delete check does not fire for OneDrive or Dropbox folders (see TODO).

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

## Audit log

`.claude/state/destructive-action-guard.log` is an append-only JSONL record of every guard-eligible Bash invocation:

```json
{"ts": "2026-05-03T12:00:00+00:00", "decision": "BLOCK", "command": "git filter-repo --invert-paths", "cwd": "/Users/foo/Dropbox/repo", "effective_cwd": "...", "bypass": false}
{"ts": "2026-05-03T12:01:00+00:00", "decision": "ALLOW", "command": "BYPASS_SHARED_GUARD=1 git filter-repo --invert-paths", "cwd": "...", "bypass": true}
```

Rotates at ~1MB to `destructive-action-guard.log.old`. Failure to write the log never breaks the hook (fail-open on logging only).

## Subagent coverage assumption

This rule assumes `PreToolUse` and `PostToolUse` hooks fire on Bash invocations made by *any* agent — parent or subagent dispatched via the `Task` tool. Claude Code documentation (https://code.claude.com/docs/en/hooks) confirms this: hook input includes `agent_id` and `agent_type` fields when the call originates in a subagent, but the same hook script runs.

**Re-verification command** (run after any Claude Code version upgrade):

```bash
# Check that subagent Bash invocations show up in the audit log
grep '"agent_id"' .claude/state/destructive-action-guard.log | head -5
```

Note: `agent_id` is not currently logged by `destructive-action-guard.py` — extend the log entry to include it if subagent visibility becomes load-bearing.

## What this rule does NOT cover

- **Non-Bash tools.** `Edit`, `Write`, `NotebookEdit`, etc. do not pass through these hooks. Other rules (`primary-source-first`, `protect-files`) cover those for specific concerns.
- **`mv` overwrites within shared storage.** Renaming files that happen to overwrite existing targets is currently allowed; the v1 spec deemed friction outweigh protection. Revisit if a real incident hits this path.
- **`git pull --rebase`.** The command string is `git pull`, not `git rebase`, so it doesn't match the always-blocked patterns. Documented limitation; the underlying rebase is generally non-destructive (fast-forward + replay of local commits).
- **Non-macOS shared-storage paths.** WSL / Linux Dropbox mounts use different paths. If the workflow is forked to a Linux setup, extend `_shared_prefixes()` accordingly.
- **Repo-internal corruption from non-rewrite operations.** A normal `git checkout` that overwrites uncommitted local changes is not gated; standard git warnings handle that.

## Cross-references

- `.claude/rules/adversarial-default.md` — the prose-level rule this hook enforces. Compliance requires evidence.
- `.claude/hooks/destructive-action-guard.py` — implementation.
- `.claude/hooks/post-rewrite-verify.py` — verification reminder injection.
- `.claude/hooks/test_destructive_action_guard.py` — regression cases (136 as of 2026-10-14) covering both classes, bypass, chains, heredocs, the unparseable fallback, symlink resolution, and mount-point anchoring.
