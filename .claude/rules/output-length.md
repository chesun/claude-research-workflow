# Output Length: Export Long Responses

**Scope:** All responses

When a response would exceed **15 lines** of terminal output, write it to a markdown document instead of printing it inline. This includes reports, summaries, plans, reviews, tables, and any structured output.

## Rules

- **> 15 lines** → write to a `.md` file and tell the user where it is
- **<= 15 lines** → print directly in the terminal
- Choose a descriptive file name and location (e.g., `quality_reports/`, `explorations/`, or project root)
- Short confirmations, error messages, and follow-up questions always stay inline regardless of length

## Enforcement

Guidance, not a hook. Apply the 15-line rule as you write: export long structured output to a `.md` and leave short confirmations, errors, and follow-up questions inline. The former `output-length-check.py` Stop hook was pruned 2026-09-16.
