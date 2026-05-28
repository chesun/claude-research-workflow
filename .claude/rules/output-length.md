# Output Length: Export Long Responses

**Scope:** All responses

When a response would exceed **15 lines** of terminal output, write it to a markdown document instead of printing it inline. This includes reports, summaries, plans, reviews, tables, and any structured output.

## Rules

- **> 15 lines** → write to a `.md` file and tell the user where it is
- **<= 15 lines** → print directly in the terminal
- Choose a descriptive file name and location (e.g., `quality_reports/`, `explorations/`, or project root)
- Short confirmations, error messages, and follow-up questions always stay inline regardless of length

## Enforcement

Advisory, not blocking — the Stop hook `.claude/hooks/output-length-check.py` fires at turn-end and, when the final response exceeds 15 non-blank lines AND no `.md` file was written that turn, injects a reminder (`additionalContext`) to export. It never blocks: a genuinely conversational long answer can proceed. The point is that the reminder *reaches the model* (the prose rule alone did not bite — it scrolled out of context). Turns that already wrote a `.md` are exempt. Threshold lives in `LINE_THRESHOLD` in the hook if it proves noisy.
