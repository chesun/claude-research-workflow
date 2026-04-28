# Glossary

Terms used throughout the workflow's docs and rule files, with one-paragraph definitions and pointers to deeper resources. Use this for lookup when something's unfamiliar — keep reading the page you were on, then come back here when you hit a term you don't know.

This glossary covers (1) general technical terms (git, terminal, etc.) for users early on the prerequisites curve, and (2) workflow-specific terms (epistemic stack, worker–critic pair, etc.) for everyone.

---

## General technical terms

### Branch (git)

A movable pointer in a git repository to a particular line of commits. The workflow's three branches (`main`, `applied-micro`, `behavioral`) are alternate flavours of the same project; you check out one at a time. See Pro Git, chapter 3 for depth.

### CLI

Command-Line Interface. A program you interact with by typing commands in a terminal rather than clicking buttons. Claude Code is a CLI tool — you launch it with `claude` in a terminal. Contrast with GUI (graphical user interface).

### Clone (git)

Make a local copy of a remote git repository. `git clone <url>` downloads the repo and its history to your machine. After cloning, you can edit files, commit, and push back to the remote.

### Commit (git)

A snapshot of the project's state at a moment in time, recorded in git history. Each commit has a unique hash (a 7- or 40-character hex string), an author, a timestamp, and a message describing what changed.

### Fork (git)

A personal copy of someone else's repository, hosted on your own GitHub account. Forking lets you make changes without affecting the original. The workflow expects users to fork rather than push to the upstream — your fork is yours to customize.

### IDE

Integrated Development Environment. A program that combines a code editor with debugging, syntax checking, version-control integration, and other tools. Common IDEs: VS Code, Cursor, RStudio, JetBrains products. The workflow doesn't depend on a specific IDE.

### Pull / push (git)

`git pull` fetches changes from a remote repository and merges them into your local copy. `git push` sends your local commits up to the remote. Most workflow operations involve a `git pull` (to get fresh content) and `git push` (to publish your work).

### Remote (git)

A reference to a git repository hosted somewhere else (typically GitHub). Your local clone has at least one remote, conventionally named `origin`. You can have multiple remotes — for instance, your fork as `origin` plus the upstream original as `upstream`.

### Repository (git, "repo")

A project tracked by git. On disk, it's a directory containing your files plus a hidden `.git/` directory with the version history. On GitHub, it's a hosted version of the same.

### Terminal

A program that gives you a command-line interface to your operating system. macOS: open the Terminal app. Linux: any of bash, zsh, fish, etc. Windows: Git Bash (recommended for this workflow), PowerShell, or WSL.

### Working tree

The current state of files in your project directory, as you'd see them with `ls` or in a file browser. Distinct from the git index (staged changes) and HEAD (last commit). When you edit a file but don't `git add` it, the change is in the working tree but not in the index.

---

## Workflow-specific terms

### Adversarial default

The principle that compliance claims about any artifact require positive evidence (a `grep` result, a test pass, a diagnostic) — never "looks fine." Codified in `.claude/rules/adversarial-default.md`. See [`../concepts/epistemic-rules.md`](../concepts/epistemic-rules.md).

### Agent

A specialized worker in the workflow's pipeline. The workflow has 17 universal agents (creators like `librarian`, `coder`, `writer`; critics like `librarian-critic`, `coder-critic`, `writer-critic`; infrastructure like `orchestrator`, `verifier`). Each agent has a focused job and a system prompt that constrains it. See `reference/agents.md` *(planned for v0.2.x)*.

### Critic

An agent whose job is to evaluate another agent's output, score it against a deduction rubric, and report issues. Critics never create — they only review. Every creator agent has a paired critic (writer ↔ writer-critic, coder ↔ coder-critic, etc.). See `concepts/worker-critic-pairs.md` *(planned for v0.2.x)*.

### Decision log (ADR)

Append-only record of substantive design decisions, stored in `decisions/NNNN_slug.md`. Once a decision is marked `Decided`, the file is immutable; supersession happens via a new ADR. The log answers "what was decided when, and why" without requiring readers to spelunk through commit history.

### Epistemic stack (or four-rule stack)

The four rules that prevent fabrication: `no-assumptions.md` (user-side), `primary-source-first.md` (papers), `derive-don't-guess.md` (repo-side), `adversarial-default.md` (compliance). Together they form a complete-by-construction set covering every fact category an agent could fabricate. See [`../concepts/epistemic-rules.md`](../concepts/epistemic-rules.md).

### Hook

A program that fires automatically at a Claude Code lifecycle event (PreToolUse, PostToolUse, Stop, PreCompact, SessionStart). The workflow uses 11 hooks for citation grounding, session-log reminders, context-survival snapshots, and file-protection guards. Hooks can block tool calls (exit code 2) or just emit warnings (exit code 0). See `reference/hooks.md` *(planned for v0.2.x)*.

### Inference-first checklist

The 14-step checklist on the `behavioral` branch (`.claude/references/inference-first-checklist.md`) that the designer agent reads when producing experiment designs. Steps cover research question, hypotheses, statistical tests co-designed with treatments, IC, comprehension, power, budget, parameter selection, and pre-registration. Operationalizes the 13 design principles in `experiment-design-principles.md`.

### Orchestrator

The infrastructure agent that manages the dependency graph of the workflow's pipeline (Discovery → Strategy → Execution → Peer Review → Submission), dispatches worker–critic pairs in parallel where independent, and tracks scores across components. Used in pipeline mode (`/new-project`); not used when invoking individual skills standalone.

### Overlay

A branch that adds paradigm-specific content (`applied-micro` for identification work, `behavioral` for experimental work) on top of the universal `main` trunk. Overlays carry only their additions; they inherit everything in `main` via rebase / cherry-pick.

### Plan-first protocol

The convention that non-trivial tasks enter Plan Mode before writing code, save the plan to `quality_reports/plans/YYYY-MM-DD_short-description.md`, and wait for user approval before executing. Plans survive context compression; they're the durable record of what's about to happen.

### Primary-source-first

The rule (and pair of hooks) that requires reading-notes evidence before citing a paper in a load-bearing artifact. See [`../concepts/epistemic-rules.md`](../concepts/epistemic-rules.md).

### Quality scoring

The weighted aggregate score computed across components (literature, data, identification/design, code, paper, polish, replication). Gates: 80 (commit), 90 (PR), 95 + every component ≥ 80 (submission). Each critic produces a per-component score; the orchestrator aggregates. See `concepts/quality-scoring.md` *(planned for v0.2.x)*.

### Rule

A markdown file in `.claude/rules/` that codifies a workflow convention. Rules apply to scoped paths (e.g., `figures.md` applies to figure-generating scripts) or universally. Loaded by every agent at session start.

### Skill

A user-invocable command in the workflow's vocabulary, e.g., `/discover`, `/strategize`, `/write`, `/submit`. Defined in `.claude/skills/<name>/SKILL.md`. Each skill is a focused workflow recipe — it might dispatch one agent or coordinate multiple.

### Skeleton (template-skeleton form)

How the public template ships its per-project files (`CLAUDE.md`, `TODO.md`, `MEMORY.md`) — with placeholder content like `[YOUR PROJECT NAME]` that forkers fill in. Distinct from "active project" form where a real fork has filled the placeholders.

### Three-strikes escalation

The convention that a worker–critic pair has at most three rounds of "produce → critique → fix" before the orchestrator escalates to a higher level (a different critic, the user, or a different agent type). Prevents infinite loops where the worker can't satisfy the critic.

### Verification ledger

A markdown table at `.claude/state/verification-ledger.md` that caches results of `(path, check, sha256[:12])` tuples. Critics consult before re-running a check; if the file hash matches a prior PASS row, the cached result is cited. File-hash mismatch triggers re-run. Prevents re-check bloat under the adversarial-default regime. See `concepts/verification-ledger.md` *(planned for v0.2.x)*.

### Worker–critic pair

The unit of agent-level adversarial review: one agent creates an artifact, a paired agent reviews it. The creator never self-scores; the critic never edits files. Each pair has a maximum of three rounds before escalation. See `concepts/worker-critic-pairs.md` *(planned for v0.2.x)*.

---

## Conventions used in this workflow's prose

### `Author and Author (year)`

Two-coauthor papers are always cited with `and`, never comma-separated, never with `&`. Standard economics convention plus avoids `primary-source-first` hook regex false-positives. See `.claude/rules/primary-source-first.md` § "Citation-style convention."

### Backticks for filenames and commands

`like-this.md` is a filename. `git status` is a command. `function_name()` is a function reference. Plain prose without backticks for everything else.

### Status tags in headings

Section headings or list items marked *(planned for v0.2.x)* are roadmap items not yet written. They're listed for completeness; click-throughs will 404.

### Square-bracket placeholders

`[YOUR PROJECT NAME]`, `[Author Name]`, etc. are placeholders forkers replace with their own values. Always uppercase, always in square brackets — easy to grep for at customization time.
