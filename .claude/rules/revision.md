# Revision Protocol — R&R Cycle

**When referee reports arrive, `/revise` classifies each comment and routes it to the right agent.**

**Read** `.claude/references/revision-protocol.md` for the comment classes (NEW ANALYSIS, CLARIFICATION, DISAGREE, MINOR), the agent each routes to, and the R&R flow from referee report to response letter (open it when classifying referee comments or running `/revise`).

## Rules

- This uses the same agents but in a targeted way — not a full pipeline restart
- Each comment gets its own routing — a single referee report may trigger multiple agent pairs
- The response letter maps each referee comment to the specific change made
- DISAGREE items are always flagged for user review — Claude never autonomously pushes back on referees
- The Orchestrator tracks which comments are resolved and which are pending
