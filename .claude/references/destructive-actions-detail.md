# Destructive Actions — detection detail

**Class:** A (universal). Pointer-loaded detail for `.claude/rules/destructive-actions.md` (moved there from the rule on 2026-10-19); there is no auto-load.

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

## Chains, heredocs and unparseable commands

- **Every command of a chain is checked** by all three tiers (always-blocked, settings write, shared-storage delete), with the working directory carried across `cd` commands: commands joined by `;`, `&&`, `||`, `|`, `&` or a newline, split on unquoted operators only, so a quoted commit message containing `; git reset --hard` is not a command. Before 2026-10-14 only the first command was checked, so `echo hi && git filter-repo ...` got through.
- **Wrappers and git's global options do not hide the subcommand:** `env [-u NAME] [--] A=1 git ...`, `command git ...`, `time -p git ...`, `(git ...)`, `{ git ...; }`, `/usr/bin/git`, `git.exe`, and every `git -C dir` / `git -c k=v` / `git --flag` before the subcommand are read as the git command they run.
- **Backslash continuations** are joined before the command is split.
- **Heredoc bodies are data unless a shell reads them.** Only an unquoted `<<` opens a heredoc (`echo "<<EOF"` does not). A body is checked as commands when a shell (`bash`, `sh`, `zsh`, `dash`, `ksh`, `fish`, `pwsh`, `powershell`) is named anywhere on its line (`bash <<EOF`, `sh -s <<EOF`, `cat <<EOF | bash`). Any other body (a commit message, a file being written, a Python script) is skipped. An unterminated `<<` removes nothing.
- **Unparseable commands** (an unbalanced apostrophe, typically): each segment is checked with the same always-blocked predicates and the settings gate. The shared-storage delete check stays fail-open there, as it always was.
- **Known limits:** commands inside `$(...)`, backticks, `eval "..."` or `sh -c '...'` strings are not unpacked, and neither is a script for another interpreter (`python - <<EOF` that calls `subprocess`). `sudo`, `timeout`, `nice` and `xargs` are not treated as wrappers. On the unparseable path the shared-storage delete check is fail-open. The shared-storage prefixes are macOS mount points, so on Windows the delete check does not fire for OneDrive or Dropbox folders (tracked in `TODO.md`).
