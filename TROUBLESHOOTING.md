# Troubleshooting

Top failure modes newcomers hit, with the fix. If you're stuck somewhere else, run `./scripts/validate-setup.sh` — it reports exactly what's missing.

## Environment / setup

### `claude: command not found`

Claude Code isn't installed. Install it from [claude.ai/install](https://claude.ai/install) (or your OS's package manager). Then re-run `./scripts/validate-setup.sh`.

### `xelatex: command not found`

No TeX Live on the system. Install MacTeX (macOS) or TeX Live (Linux/Windows). Until you do, `/compile-latex` and `/extract-tikz` are disabled; `/deploy` (Quarto) still works.

### `quarto: command not found`

Install Quarto from [quarto.org/docs/get-started](https://quarto.org/docs/get-started/). Until you do, `/deploy` and `/qa-quarto` are disabled; Beamer workflows still work.

### `pdf2svg: command not found`

Required by `/extract-tikz`. `brew install pdf2svg` (macOS) / `apt install pdf2svg` (Debian/Ubuntu) / `dnf install pdf2svg` (Fedora).

### Claude keeps asking permission for every tool

Default permission mode prompts on every `Bash`, `Edit`, `Write`. Two fixes:

- **Auto-accept edits** — keybinding in Claude Code; see guide's [permission modes section](https://psantanna.com/claude-code-my-workflow/workflow-guide.html#settings---permissions-and-hooks).
- **Bypass mode** — `claude --permission-mode acceptEdits` (auto-approves edits but still prompts for sensitive ops) or `claude --permission-mode bypassPermissions` (skips prompts entirely — use only on trusted repos).

The template's `.claude/settings.json` pre-approves ~100 common patterns, so even at default most routine work is unattended.

## Compilation / rendering

### `Undefined citation` in Beamer

The `.bib` key isn't in `Bibliography_base.bib`. Run `/validate-bib` to cross-check citations against the bib file. The 3-pass XeLaTeX + bibtex sequence in `/compile-latex` resolves keys that exist; it can't invent them.

### `Overfull \hbox` warnings

Text exceeds the slide's printable width. Either shorten the offending content, wrap it in a `text width=...` node (for TikZ), or switch to `\resizebox`. `/visual-audit` flags these; `/proofread` does too.

### Quarto render fails with `No valid input files`

You likely invoked `quarto render` from the wrong cwd. Run it from the repo root. `/deploy` handles this automatically.

### HelloWorld.tex fails to compile

`./scripts/validate-setup.sh` first. If XeLaTeX is installed, re-fork a clean copy — you may have edited the sample deck without realizing it. HelloWorld is intentionally minimal and should always compile on a fresh clone.

### `/extract-tikz` halts at prevention pre-check

Good — the pre-check caught a P3 (bare `scale=`) or P4 (missing directional keyword on an edge label) violation. Fix the offending line in the Beamer source and re-run. See `.claude/rules/tikz-prevention.md`.

## Git / hooks / CI

### Hook script permission denied

`chmod +x .claude/hooks/*.py .claude/hooks/*.sh`. `./scripts/validate-setup.sh` also reports non-executable hooks.

### Pre-compact hook didn't save the plan

The PreCompact hook (`.claude/hooks/pre-compact.py`) writes state to `~/.claude/sessions/<hash>/`. If the state isn't there after compaction:

- Check the hook's exit code: `echo '{}' | python3 .claude/hooks/pre-compact.py` should exit 0.
- Check permissions on `~/.claude/sessions/`.
- Check the session hash matches — compaction logs the hash.

### `/commit` fails with `quality_score.py` below threshold

The script detected issues in changed files. Either fix them (recommended) or override with `/commit --skip-quality-gate "reason"` — the override is logged in the commit message.

## Palette / theming

### Beamer and Quarto renderings use different colors

The palette contract broke. Run `./scripts/check-palette-sync.sh` — it reports which color names are missing from one surface. Fix HEX values in **both** `Preambles/header.tex` and `Quarto/theme-template.scss` to match. See `Preambles/README.md` for the full contract.

## R / data analysis

### `here::here()` resolves to the wrong directory

`here` needs a project root marker (`.here`, `.git`, `DESCRIPTION`, or `.Rproj`). If you see wrong paths, create an empty `.here` file at the repo root.

### `sessionInfo.txt` not updated after analysis changes

You ran `03_analyze.R` directly instead of `00_run_all.R`. Always go through the orchestrator — it writes the session snapshot as its last step.

## Still stuck?

- Read the [guide's troubleshooting section](https://psantanna.com/claude-code-my-workflow/workflow-guide.html#troubleshooting) for longer-form recovery scenarios.
- Open an issue at <https://github.com/pedrohcgs/claude-code-my-workflow/issues> — the bug-report template asks for the environment details we need to help.
