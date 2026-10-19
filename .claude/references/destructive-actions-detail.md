# Destructive Actions — detection detail

**Class:** A (universal). Pointer-loaded detail for `.claude/rules/destructive-actions.md` (moved from the rule on 2026-10-19); there is no auto-load.

The guard has three tiers: always-blocked commands (Tier 1), deletes under shared storage (Tier 2) and writes to the settings files (Tier 3). Implementation: `.claude/hooks/destructive-action-guard.py`; regression cases: `.claude/hooks/test_destructive_action_guard.py`.

## Settings.json write gate (Tier 3)

The companion hook `protect-files.py` (formerly `protect-files.sh`) is registered only on the `Edit|Write|MultiEdit` matcher and cannot observe Bash invocations. Without Tier 3, any of the following would silently bypass it:

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

## `cd X && ...` chain handling

The guard parses leading `cd <path> &&` directives in the command string and updates the effective cwd before checking path arguments. Concretely, `cd ~/dropbox-repo && rm -rf output/` is evaluated as `rm -rf ~/dropbox-repo/output/` for the purposes of the path check.

This handles the realistic case where Claude prefixes a `cd` to localize a destructive command.

## Chains, heredocs and unparseable commands

- **Every command of a chain is checked** by all three tiers (always-blocked, settings write, shared-storage delete), with the working directory carried across `cd` commands: commands joined by `;`, `&&`, `||`, `|`, `&` or a newline, split on unquoted operators only, so a quoted commit message containing `; git reset --hard` is not a command. Before 2026-10-14 only the first command was checked, so `echo hi && git filter-repo ...` got through.
- **Wrappers and git's global options do not hide the subcommand:** `env [-u NAME] [--] A=1 git ...`, `command git ...`, `time -p git ...`, `(git ...)`, `{ git ...; }`, `/usr/bin/git`, `git.exe`, and every `git -C dir` / `git -c k=v` / `git --flag` before the subcommand are read as the git command they run.
- **Backslash continuations** are joined before the command is split.
- **Heredoc bodies are data unless a shell reads them.** Only an unquoted `<<` opens a heredoc (`echo "<<EOF"` does not). A body is checked as commands when a shell (`bash`, `sh`, `zsh`, `dash`, `ksh`, `fish`, `pwsh`, `powershell`) is named anywhere on its line (`bash <<EOF`, `sh -s <<EOF`, `cat <<EOF | bash`). Any other body (a commit message, a file being written, a Python script) is skipped. An unterminated `<<` removes nothing.
- **Unparseable commands** (an unbalanced apostrophe, typically): each segment is checked with the same always-blocked predicates and the settings gate. The shared-storage delete check stays fail-open there, as it always was.
- **Known limits:** commands inside `$(...)`, backticks, `eval "..."` or `sh -c '...'` strings are not unpacked, and neither is a script for another interpreter (`python - <<EOF` that calls `subprocess`). `sudo`, `timeout`, `nice` and `xargs` are not treated as wrappers. On the unparseable path the shared-storage delete check is fail-open. The shared-storage prefixes are macOS mount points, so on Windows the delete check does not fire for OneDrive or Dropbox folders (tracked in `TODO.md`).

## Why this exists

On 2026-04-25, a Claude Code session ran `git filter-repo --invert-paths` on a Dropbox-shared git repo (3 coauthors) to shrink it for a failing push. The operation rewrote history *and* silently rewrote the working tree, deleting `output/dta/most_recent/` and several dated regression-export folders. Dropbox propagated the deletion to all coauthors. The session then force-pushed to origin, making the rewrite permanent on GitHub.

The session log claimed *"Working tree = 8.8 GB unchanged (all .dta files still present)"* — never verified with `ls`/`du`, and false. The deletion surfaced 8 days later when a coauthor noticed missing files.

Two failure modes compounded:

1. **No enforced gate on history rewrites** despite prose-level rules saying "destructive operations need explicit re-authorization."
2. **False-success narration** — the agent reported success without producing positive evidence (`ls`/`du` output) of what the rule actually required.

`destructive-actions.md` installs hooks that close both gaps.

## Audit log

`.claude/state/destructive-action-guard.log` is an append-only JSONL record of every guard-eligible Bash invocation:

```json
{"ts": "2026-05-03T12:00:00+00:00", "decision": "BLOCK", "command": "git filter-repo --invert-paths", "cwd": "/Users/foo/Dropbox/repo", "effective_cwd": "...", "bypass": false}
{"ts": "2026-05-03T12:01:00+00:00", "decision": "ALLOW", "command": "BYPASS_SHARED_GUARD=1 git filter-repo --invert-paths", "cwd": "...", "bypass": true}
```

Rotates at ~1MB to `destructive-action-guard.log.old`. Failure to write the log never breaks the hook (fail-open on logging only).

## Subagent coverage assumption

`destructive-actions.md` assumes `PreToolUse` and `PostToolUse` hooks fire on Bash invocations made by *any* agent — parent or subagent dispatched via the `Task` tool. Claude Code documentation (https://code.claude.com/docs/en/hooks) confirms this: hook input includes `agent_id` and `agent_type` fields when the call originates in a subagent, but the same hook script runs.

**Re-verification command** (run after any Claude Code version upgrade):

```bash
# Check that subagent Bash invocations show up in the audit log
grep '"agent_id"' .claude/state/destructive-action-guard.log | head -5
```

Note: `agent_id` is not currently logged by `destructive-action-guard.py` — extend the log entry to include it if subagent visibility becomes load-bearing.

## What the guard does NOT cover

- **Non-Bash tools.** `Edit`, `Write`, `NotebookEdit`, etc. do not pass through these hooks. Other rules (`primary-source-first`, `protect-files`) cover those for specific concerns.
- **`mv` overwrites within shared storage.** Renaming files that happen to overwrite existing targets is currently allowed; the v1 spec deemed friction outweigh protection. Revisit if a real incident hits this path.
- **`git pull --rebase`.** The command string is `git pull`, not `git rebase`, so it doesn't match the always-blocked patterns. Documented limitation; the underlying rebase is generally non-destructive (fast-forward + replay of local commits).
- **Non-macOS shared-storage paths.** WSL / Linux Dropbox mounts use different paths. If the workflow is forked to a Linux setup, extend `_shared_prefixes()` accordingly. On Windows the delete check does not fire for OneDrive or Dropbox folders either.
- **Repo-internal corruption from non-rewrite operations.** A normal `git checkout` that overwrites uncommitted local changes is not gated; standard git warnings handle that.
