# To-Do Tracking

**Every project maintains a `TODO.md` in the project root.**

## Format

```markdown
# TODO — [Project Name]

Last updated: YYYY-MM-DD

## Active (doing now)
- [ ] [task description] — [context/blocker if any]

## Up Next
- [ ] [task description]

## Waiting On
- [ ] [task description] — waiting on [person/event/dependency]

## Backlog
- [ ] [task description]

## Done (recent)
- [x] [task description] — [date completed]
```

## Rules

1. **One file per project** — `TODO.md` in the project root, always.
2. **Update after completing work** — when a task is finished, check it off and move it to Done. If new tasks were discovered during the work, add them.
3. **Keep it scannable** — one line per item. Details belong in plans or session logs, not here.
4. **Four sections:** Active (in progress right now), Up Next (ready to start), Waiting On (blocked), Backlog (future). Plus a short Done section for recent completions.
5. **Not a replacement for plans** — plans document the approach and rationale. TODO tracks what's left to do.
6. **Prune Done regularly** — keep only the last ~10 completed items. Older completions are in session logs and git history.
7. **Skills should check TODO.md** — before starting work, read TODO.md to understand context. After finishing, update it.
