# Logging: Sessions, Reports, and Research Journal

---

## 1. Session Logging

**Location:** `quality_reports/session_logs/YYYY-MM-DD_description.md`
**Template:** `templates/session-log.md`

### Three Triggers (all proactive)

**1. Post-Plan Log**

After plan approval, immediately capture: goal, approach, rationale, key context.

**2. Incremental Logging**

Append 1-3 lines whenever: a design decision is made, a problem is solved, the user corrects something, or the approach changes. Do not batch.

**3. End-of-Session Log**

When wrapping up: high-level summary, quality scores, open questions, blockers.

### Quality Reports

Generated **only at merge time** — not at every commit or PR.
Save to `quality_reports/merges/YYYY-MM-DD_[branch-name].md` using `templates/quality-report.md`.

---

## 2. Session Report (Consolidated)

**File:** `SESSION_REPORT.md` in project root
**Mirror:** `.claude/SESSION_REPORT.md` (kept in sync)

### Purpose

Maintain a single, append-only MD file that consolidates everything Claude does across sessions. Unlike session logs (which are per-session files in `quality_reports/session_logs/`), this is one living document that accumulates the full project history.

### Triggers

1. **End of every session** — proactively append a new entry before wrapping up
2. **On user request** — "update the report", "log what we did", "add to the report"
3. **After significant milestones** — commits, completed analyses, major decisions

### Entry Format

Each entry is a dated section appended to the file:

```markdown
## YYYY-MM-DD HH:MM — [Brief Title]

**Operations:**
- [Scripts run, files created/modified/deleted]
- [Commands executed, packages installed]

**Decisions:**
- [Choice made] — [rationale]

**Results:**
- [Key findings, outputs produced]
- [Errors encountered → how resolved]

**Commits:**
- `[hash]` [commit message]

**Status:**
- Done: [what's complete]
- Pending: [what remains]
```

### Rules

1. **Append only** — never overwrite or edit previous entries
2. **Concise** — bullet points, not prose; 5–15 lines per entry
3. **Include commit hashes** when commits are made during the session
4. **Include file paths** for any files created or significantly modified
5. **Create the file** if it doesn't exist; add a title header: `# Session Report — [Project Name]`
6. **Sync both copies** — root `SESSION_REPORT.md` and `.claude/SESSION_REPORT.md` must match
7. **Do not duplicate** session logs — this report is a higher-level summary; detailed session logs remain in `quality_reports/session_logs/`

---

## 3. Research Journal

**After every agent produces a report, append a summary entry to `quality_reports/research_journal.md`.**

### Entry Format

```markdown
### YYYY-MM-DD HH:MM — [Agent Name]
**Phase:** [Discovery/Strategy/Execution/Peer Review/Presentation]
**Target:** [file or topic reviewed]
**Score:** [XX/100 or PASS/FAIL or N/A]
**Verdict:** [one line — the key finding or decision]
**Report:** [link to full report]
```

### Rules

- **Append only** — never overwrite or edit previous entries
- **One entry per agent invocation** — not per issue
- **Create the file** if it doesn't exist, with header: `# Research Journal — [Project Name]`
- **Include escalation events:** "Strike 2/3 — coder-critic flagged code-strategy misalignment"
- **Include phase transitions:** "Phase 2 → Phase 3: strategist-critic approved (score: 88)"
- **Include editorial decisions:** "Orchestrator decision: Minor Revisions"

### What Gets Logged

| Event | Logged? |
|-------|---------|
| Agent review report | Yes — score + verdict |
| Phase transition | Yes — which phase, approval score |
| Escalation (three strikes) | Yes — strike count, escalation target |
| User override | Yes — what was overridden and why |
| R&R comment routing | Yes — classification + routing target |
| Score changes | Yes — before/after when resubmitted |

### Relationship to Other Logs

- **Session logs** (`quality_reports/session_logs/`) — per-session, detailed, ephemeral
- **Session report** (`SESSION_REPORT.md`) — consolidated operations log
- **Research journal** (`quality_reports/research_journal.md`) — agent-level research history, append-only
