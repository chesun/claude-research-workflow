# Quality — per-target deduction tables

**Class:** B (overlay-customized; see `.claude/file-classes.toml`, and merge by hand, never copy over an overlay's version). Pointer-loaded detail for `.claude/rules/quality.md` § 3 Per-Target Deduction Tables (moved from the rule on 2026-10-19); there is no auto-load.

The rule keeps the score gates, the severity gradient, the § 3 Enforcement block and the replication tolerances. Each critic agent in `.claude/agents/` carries the deduction table it applies, and that table is authoritative (owner decision, 2026-10-19).

## Where each table lives

| Target | Authoritative table |
|---|---|
| Paper LaTeX (`paper/main.tex`) | `.claude/agents/writer-critic.md` § Scoring, plus its anti-AI-prose subsection (capped at -30) |
| R, Stata and Python scripts | `.claude/agents/coder-critic.md` § Scoring |
| Talks (Beamer), advisory and non-blocking | `.claude/agents/storyteller-critic.md` § Scoring, plus its anti-AI-prose subsection (capped at -15) |

A paper that does not compile, a script that does not run, and slides that do not compile each cost -100, so they always fail the gate. Talk scores are reported as "Talk: XX/100" but do **not** block commits or PRs.

Until 2026-10-19 this file held separate tables copied from `quality.md` § 3, whose values differed from the agents' (compile failure -100 here against -20 in writer-critic, so a non-compiling paper could score 80 and pass the commit gate). The agents' values were kept, the -100 failure rows were adopted, and the rows that existed only here were added to the agents. The old tables are in git history (`c44ed88`).
