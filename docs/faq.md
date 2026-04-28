# FAQ

Anticipated questions, with brief answers and pointers to depth.

---

## Why use this workflow over plain Claude Code?

Plain Claude Code gives you a capable agent. This workflow adds **opinionated infrastructure on top**: the four-rule epistemic stack to prevent fabrication, paired worker–critic agents for adversarial review, a verification ledger to cache compliance evidence, an ADR convention, paradigm-specific overlays (applied-micro, behavioral) with codified rules.

If you don't need any of those, plain Claude Code is fine. If you've felt the bite of "agent confidently produced wrong-looking output" and want structural guards against it, this workflow exists for that reason.

See [`concepts/upstream-differences.md`](concepts/upstream-differences.md) for the verified file-by-file accounting of what this fork adds vs the upstreams it descends from.

---

## Do I need to know git, the command line, and LaTeX before using this?

Yes, at a basic level. The workflow is a CLI tool layered on top of Claude Code; basic terminal navigation and git operations are unavoidable. LaTeX is needed because the paper-production parts of the workflow assume a working LaTeX install.

If those are unfamiliar, [`getting-started/prerequisites.md`](getting-started/prerequisites.md) points at curated learning resources. Roughly 3 hours of reading covers what you need. The cleanest framing: this isn't a hand-held alternative to learning these tools — it's a reason to learn them.

See also [`concepts/appropriate-use.md`](concepts/appropriate-use.md) on what the workflow can and can't substitute for.

---

## Which branch should I pick — `main`, `applied-micro`, or `behavioral`?

- **`main`** if your work is general empirical research that doesn't fit cleanly into one paradigm.
- **`applied-micro`** if you do observational-data identification-strategy research (DiD, IV, RDD, synthetic control).
- **`behavioral`** if you run experiments (lab / online / field) or do formal theory in the experimental-economics tradition.

You can switch later — `git checkout` the right branch — without losing project content.

See [`getting-started/branch-model.md`](getting-started/branch-model.md) for the decision tree.

---

## What's the difference between rules, skills, agents, and hooks?

- **Rules** (`.claude/rules/`) — markdown files codifying conventions. Loaded into every agent's context via `CLAUDE.md`.
- **Skills** (`.claude/skills/`) — user-invocable slash commands like `/strategize`, `/write`, `/submit`. Each is a focused recipe that may dispatch one or more agents.
- **Agents** (`.claude/agents/`) — specialized workers with their own system prompts and tool permissions. Dispatched by skills or other agents.
- **Hooks** (`.claude/hooks/`) — programs that fire automatically at lifecycle events (PreToolUse, Stop, etc.). The only deterministically-blocking enforcement layer.

See [`reference/glossary.md`](reference/glossary.md) for one-paragraph definitions and [`reference/{skills,agents,rules,hooks}.md`](reference/) for full catalogues.

---

## Why does the `primary-source-first` hook keep blocking my edits?

Because you're citing a paper in a load-bearing artifact (`decisions/`, `quality_reports/plans/`, `quality_reports/session_logs/`, etc.) without reading-notes evidence. Two paths:

1. **Drop the PDF into `master_supporting_docs/literature/papers/`** with the surname-and-year naming convention, and produce a reading-notes file.
2. **Use the escape-hatch comment** `<!-- primary-source-ok: <stem> -->` if the citation is illustrative or test-case-only (not a fresh framing claim about the paper).

The hook does not fire on `.claude/rules/`, `.claude/references/`, `docs/`, or other unscoped paths.

See `.claude/rules/primary-source-first.md` for full semantics.

---

## Can I disable a hook or rule I don't like?

Yes. Edit `.claude/settings.json` to remove the hook entry, or remove the rule's reference from `CLAUDE.md`. Both are part of your fork — make them yours.

But: the workflow's defaults exist because they catch real failure modes. Before disabling, consider modifying instead. If the rule is too strict in one direction, edit its conditions; if a hook fires too often, tune the regex or the threshold. Pure deletion loses the protection without giving you the failure-mode catch.

---

## How does this interact with Overleaf?

Set the `Overleaf path:` field in `CLAUDE.md` to the local directory of your Overleaf project (typically a Dropbox-synced path). The workflow's compile and verify tooling targets that path instead of the in-repo `paper/` and `talks/` directories.

If you don't use Overleaf, leave the field blank.

See [`customization/adapting-claude-md.md`](customization/adapting-claude-md.md) for details.

---

## What happens to my work when context compaction runs?

Two safeguards:

1. **`pre-compact.py`** captures session state (active plan, current task, recent decisions) to `~/.claude/sessions/<hash>/pre-compact-state.json` before the compact event.
2. **`post-compact-restore.py`** reads that snapshot at the start of the next session and surfaces it to the agent.

There's also a fallback in `context-monitor.py`: at 90% context, it writes the same snapshot directly. This works around [`anthropics/claude-code#14111`](https://github.com/anthropics/claude-code/issues/14111) (PreCompact silently bypasses on auto-compact under MCP-server load).

Plus: plans, session logs, ADRs, and the verification ledger are all on disk. None of them depend on the agent's context — they survive across compactions and across sessions.

See [`reference/hooks.md`](reference/hooks.md) for hook details.

---

## How do I cite a paper with two coauthors?

`Author and Author (year)` — always with `and`, never comma-separated, never with `&`.

```markdown
Yes:  Smith and Jones (2024) show ...
No:   Smith, Jones (2024) show ...
No:   Smith & Jones 2024 show ...
```

Two reasons: standard economics convention; avoids `primary-source-first` hook regex false-positives on comma-adjacent surnames. See `.claude/rules/primary-source-first.md` § "Citation-style convention."

For three or more coauthors, follow your target journal's convention (typically first-author "et al." in running text, full list in references).

---

## Can I trust the workflow to produce publication-ready output?

For *mechanical* aspects — yes, with critic review. The workflow reliably produces compilable code, properly formatted tables, balance-checked specifications, citation-grounded prose. The deduction tables in `quality.md` cover the categories of mechanical defect.

For *substantive* aspects — no. Whether the contribution is novel, the framing is correct for your subfield, the literature is properly read, the mechanism is well-identified, the design tests what you think it tests — those are judgment calls only you can make. The workflow's adversarial critics catch fabrication; they don't generate the missing knowledge.

[`concepts/appropriate-use.md`](concepts/appropriate-use.md) is the depth on this. Read it before using the workflow on real research.

---

## Why does the docs site keep saying "(planned for v0.2.x)"?

Because v0.1.0 ships with the entry-point and concept-and-reference docs, but a few pages (`first-session.md`, `customization/adapting-claude-md.md`, `faq.md`, plus overlay-specific walkthroughs on `applied-micro` and `behavioral`) are written incrementally over the v0.2.x cycle.

Some of those pages are now present in the v0.1.0 release if you're reading this; the "(planned)" tags will be removed as each lands.

---

## How do I keep my fork in sync with upstream?

```bash
git remote add upstream https://github.com/chesun/claude-research-workflow.git
git fetch upstream
git pull upstream main      # or applied-micro / behavioral
```

Most updates are additive (new rules, hook fixes). Conflicts are rare unless you've heavily modified the same files. For larger updates (renames, restructures), expect a merge conflict and resolve manually.

If you've made local changes to rules/skills/agents that you want to keep across upstream pulls, name them differently (e.g., `my-project-rule.md` rather than editing `existing-rule.md`). See [`customization/adapting-claude-md.md`](customization/adapting-claude-md.md) § "Don't fork-and-stretch the template."

---

## What if I find a bug?

Open an issue at [`chesun/claude-research-workflow/issues`](https://github.com/chesun/claude-research-workflow/issues). Include:

- Branch and commit hash (`git rev-parse HEAD`)
- What you expected
- What happened (logs, error output, screenshots)
- Minimal reproduction if possible

For security issues (a hook that could execute arbitrary commands, a permission rule that creates a vulnerability), please email rather than file a public issue.

See [`../CONTRIBUTING.md`](../CONTRIBUTING.md) for the full contribution policy.

---

## Where do I go if my question isn't here?

In order of likely productiveness:

1. The relevant `docs/` page — `getting-started/`, `concepts/`, `reference/`.
2. The relevant `.claude/rules/<name>.md` — most behavior is codified there.
3. The corresponding `.claude/agents/<name>.md` system prompt — explains why an agent does what it does.
4. The Claude Code platform documentation at [code.claude.com/docs](https://code.claude.com/docs/en/overview) for platform-level questions (not workflow-specific).
5. Open an issue if it's a bug or a workflow-specific question that the docs should address.
