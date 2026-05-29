# Logging: Session Logs and Reviews

---

## 1. Session Logging

**Location:** `quality_reports/session_logs/YYYY-MM-DD_description.md`
**Template:** `templates/session-log.md`

### Four Triggers (all proactive)

**1. Post-Plan Log**

After plan approval, immediately capture: goal, approach, rationale, key context.

**2. Incremental Logging**

Append 1-3 lines whenever: a design decision is made, a problem is solved, the user corrects something, or the approach changes. Do not batch.

**3. Hard-cap reminder (enforced by stop hook)**

The `log-reminder.py` Stop hook fires if **10 responses** pass without a session-log edit. When it fires, append progress to the most recent session-log file before stopping. This is a safety net for the incremental rule — if you hit the hook, the incremental rule was already missed.

**4. End-of-Session Log**

When wrapping up: high-level summary, quality scores, open questions, blockers.

### Quality Reports

Generated **only at merge time** — not at every commit or PR.
Save to `quality_reports/merges/YYYY-MM-DD_[branch-name].md` using `templates/quality-report.md`.

---

## 2. Review and Analysis Reports

**Location:** `quality_reports/reviews/YYYY-MM-DD_description.md`

### When to Save

Any analysis or review output longer than ~20 lines must be saved as a markdown file — not just printed to the conversation. This includes:

- Table notes reviews, consistency audits
- Paper section reviews, proofreading reports
- Code reviews, data quality checks
- Any structured finding that coauthors might reference

### Rules

1. **Always save to disk first**, then provide a concise summary in the conversation
2. **File naming:** `quality_reports/reviews/YYYY-MM-DD_short-description.md`
3. **Use markdown formatting** — headers, tables, bullet points for scanability
4. **Include priority levels** when reporting issues (High / Medium / Low)
5. **Reference specific files and line numbers** where issues are found
