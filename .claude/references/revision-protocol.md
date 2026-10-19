# Revision protocol — classification and R&R flow

**Class:** A (universal). Pointer-loaded detail for `.claude/rules/revision.md` (comment classification and the R&R flow, moved from the rule on 2026-10-19); there is no auto-load.

The rule keeps the R&R rules, including that DISAGREE items always go to the user. The `/revise` skill (`.claude/skills/revise/SKILL.md`) runs the cycle.

## Comment Classification

| Classification | What It Means | Routed To |
|---------------|---------------|-----------|
| **NEW ANALYSIS** | Requires new estimation or data work | Coder → coder-critic |
| **CLARIFICATION** | Text revision sufficient | Writer → writer-critic |
| **DISAGREE** | Diplomatic pushback needed | Flagged for User review |
| **MINOR** | Typos, formatting | Writer |

## The R&R Flow

```
Referee reports arrive (real, not simulated)
        │
        ▼
   /revise classifies each comment
        │
        ├── NEW ANALYSIS → Coder → coder-critic → Writer updates
        ├── CLARIFICATION → Writer → writer-critic
        ├── DISAGREE → User decides → diplomatic response drafted
        └── MINOR → Writer
        │
        ▼
   Revised paper → writer-critic → Orchestrator re-checks
        │
        ▼
   Response letter produced
```
