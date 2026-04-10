# Output Length: Export Long Responses

**Scope:** All responses

When a response would exceed **15 lines** of terminal output, write it to a markdown document instead of printing it inline. This includes reports, summaries, plans, reviews, tables, and any structured output.

## Rules

- **> 15 lines** → write to a `.md` file and tell the user where it is
- **<= 15 lines** → print directly in the terminal
- Choose a descriptive file name and location (e.g., `quality_reports/`, `explorations/`, or project root)
- Short confirmations, error messages, and follow-up questions always stay inline regardless of length
