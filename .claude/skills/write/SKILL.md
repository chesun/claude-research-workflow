---
name: write
description: Draft academic economics paper sections with notation protocol and anti-hedging. Replaces /draft-paper. (For the humanizer pass, use /humanize — universal across papers, slides, and other external-facing docs.)
argument-hint: "[section: intro | strategy | results | conclusion | abstract | full]"
allowed-tools: Read,Grep,Glob,Write,Edit,Task
---

# Write

Draft paper sections by dispatching the **Writer** agent.

**Input:** `$ARGUMENTS` — section name.

---

## Modes

### `/write [section]` — Draft Paper Section
Draft a specific section: `intro`, `strategy`, `results`, `conclusion`, `abstract`, or `full`.

**Agent:** Writer
**Output:** LaTeX section file in paper/sections/

Workflow:
1. Read existing paper, research spec, literature review, results summary
2. Read .claude/references/domain-profile.md for field conventions
3. Check paper/references.bib for available citations
4. Dispatch Writer with section standards:
   - Introduction: contribution in first 2 pages, effect sizes with units
   - Strategy: estimating equation displayed and numbered, assumptions explicit
   - Results: every estimate with units and magnitudes
   - Conclusion: restate with effect size, limitations, implications
5. Writer applies notation protocol and anti-hedging rules
6. Humanizer pass runs automatically before finalizing
7. Save to paper/sections/[section].tex

### Humanizer pass — moved to `/humanize`

The humanizer pass is now a separate, universal skill: **`/humanize [path]`**. It dispatches the Writer (for `paper/`), Storyteller (for `talks/`), or generic-prose mode (for `docs/`, `blog/`, `README.md`, etc.) based on the path. See `.claude/skills/humanize/SKILL.md` and the catalog rule at `.claude/rules/anti-ai-prose.md`.

For backward compatibility, `/write humanize <file>` aliases to `/humanize <file>` and prints a one-line deprecation note.

---

## Section Standards

| Section | Length | Key Requirements |
|---------|--------|-----------------|
| Introduction | 1000-1500 words | Hook → question → method → finding → contribution → roadmap |
| Strategy | 800-1200 words | Formal assumption, numbered equation, threats addressed |
| Results | 800-1500 words | Main spec, effect sizes in economic terms, heterogeneity |
| Conclusion | 500-700 words | Restate with effect size, policy, limitations, future |
| Abstract | 100-150 words | Question, method, finding with magnitude, implication |

---

## Principles
- **This is the user's paper, not Claude's.** Match their voice and style.
- **Never fabricate results.** Use TBD placeholders.
- **Citations must be verifiable.** Only cite confirmed papers.
- **Humanizer is automatic.** Every draft gets de-AI-ified.
