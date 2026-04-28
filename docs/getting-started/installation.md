# Installation

This page covers fork → clone → branch-pick → first-launch. It assumes you've worked through [`prerequisites.md`](prerequisites.md) and have a working installation of git, the Claude Code CLI, LaTeX, and your primary analysis language.

If any of those are missing, stop here and read `prerequisites.md` first.

---

## 1. Fork on GitHub

Visit [`chesun/claude-research-workflow`](https://github.com/chesun/claude-research-workflow) and click **Fork** in the top-right. This creates a copy of the repo under your own GitHub account.

You don't need to do anything special with the fork settings — leave defaults checked. The fork includes all three branches (`main`, `applied-micro`, `behavioral`).

## 2. Clone your fork

In a terminal:

```bash
git clone https://github.com/YOUR_USERNAME/claude-research-workflow.git my-project
cd my-project
```

Replace `YOUR_USERNAME` with your GitHub username. Replace `my-project` with whatever you want the local directory to be called — it doesn't need to match the repo name.

## 3. Pick your branch

The workflow has three branches. Pick one based on the kind of research you do:

- **`main`** — general empirical research. Paradigm-agnostic. Stay here if your work doesn't fit cleanly into one of the overlays.
- **`applied-micro`** — observational-data, identification-strategy research (DiD, IV, RDD, synthetic control). Adds identification-specific tooling.
- **`behavioral`** — experimental and theoretical work (lab, online, or theory papers). Adds experimental-design tooling, formal-theory tooling, oTree and Qualtrics specialists, the inference-first 14-step checklist.

Switch with:

```bash
git checkout applied-micro      # or
git checkout behavioral         # or
git checkout main               # default; can skip
```

For more on the branch model — when each fits, what each adds — see [`branch-model.md`](branch-model.md).

## 4. Customize `CLAUDE.md`

Open the project root's `CLAUDE.md`. It has bracketed placeholders:

```markdown
**Project:** [YOUR PROJECT NAME]
**Institution:** [YOUR INSTITUTION]
**Stata version:** [17 / 18 / N/A]
**LaTeX engine:** [pdflatex / xelatex]
...
```

Replace the placeholders with your project's details. This file is loaded by Claude Code at the start of every session, so getting it right early pays off.

## 5. Verify the install

```bash
claude
```

Once Claude Code launches, paste:

```
What workflow does this repo use?
```

The response should describe the workflow's branch model, the four-rule epistemic stack, and a couple of skills. If it does, you're ready. If it gets vague or generic, check that:

- You're in the cloned directory (not above it).
- `CLAUDE.md` exists at the project root.
- The `.claude/` directory exists with subdirectories for `rules/`, `skills/`, `agents/`, `hooks/`.

## 6. (Optional) Add upstream as a remote

If you want to pull future updates from the original repo:

```bash
git remote add upstream https://github.com/chesun/claude-research-workflow.git
git fetch upstream
```

Then pull updates with `git pull upstream main` (or `applied-micro` / `behavioral`). Resolve merge conflicts as needed. Most updates are additive (new rules, new skills) and don't conflict with project-specific customizations.

---

## Troubleshooting

**"`claude` command not found."** The Claude Code CLI isn't installed or isn't on your PATH. Re-run the official installer from [anthropic.com/claude-code](https://www.anthropic.com/claude-code).

**Hooks fail with "Permission denied" on the shell scripts.** The `.claude/hooks/*.sh` files need executable bit set. Run `chmod +x .claude/hooks/*.sh` to fix.

**Hooks fail with "python3: command not found."** Workflow hooks require Python 3.10+. Install Python (or symlink `python3` to your installed Python binary).

**LaTeX compilation fails on the first run.** The workflow's `working-paper-format.md` rule uses `biblatex` + `biber` (not `bibtex`). Make sure `biber --version` works in a terminal. If your LaTeX install is missing biber, re-run the LaTeX distribution installer or add the package via your distribution's package manager.

**`primary-source-first` hook blocks an edit you didn't expect.** The hook requires citations in load-bearing files (`decisions/`, `quality_reports/plans/`, `quality_reports/session_logs/`, etc.) to be backed by reading notes or PDFs. For details on when it fires and how to use the escape hatch, see [`.claude/rules/primary-source-first.md`](../../.claude/rules/primary-source-first.md). For citations in unscoped paths (`docs/`, `.claude/rules/`), the hook doesn't fire.

---

## What's next

- [`branch-model.md`](branch-model.md) — when each branch fits, what each adds
- `first-session.md` *(planned for v0.2.x)* — walkthrough of a typical first day
- [`../concepts/epistemic-rules.md`](../concepts/epistemic-rules.md) — what makes this fork different from upstream
