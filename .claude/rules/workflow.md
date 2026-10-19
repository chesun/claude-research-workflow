# Workflow: Planning, Orchestration, and Dependencies

---

## 1. Plan-First Protocol

**For any non-trivial task, enter plan mode before writing code.**

### The Protocol

1. **Enter Plan Mode** — use `EnterPlanMode`
2. **Check MEMORY.md** — read any `[LEARN]` entries relevant to this task
3. **Requirements Specification (for complex/ambiguous tasks)** — see below
4. **Draft the plan** — what changes, which files, in what order
5. **Save to disk** — write to `quality_reports/plans/YYYY-MM-DD_short-description.md`
6. **Present to user** — wait for approval
7. **Exit plan mode** — only after approval
8. **Save initial session log** — capture goal and key context while fresh
9. **Implement via orchestrator** — see Section 2

### Requirements Specification (For Complex/Ambiguous Tasks)

**When to use:**
- Task is high-level or vague ("improve the lecture", "analyze the data")
- Multiple valid interpretations exist
- Significant effort required (>1 hour or >3 files)

**When to skip:**
- Task is clear and specific ("fix typo in line 42")
- Simple single-file edit
- User has already provided detailed requirements

**Protocol:**
1. Use AskUserQuestion to clarify ambiguities (max 3-5 questions)
2. Create `quality_reports/specs/YYYY-MM-DD_description.md` using `templates/requirements-spec.md`
3. Mark each requirement:
   - **MUST** (non-negotiable)
   - **SHOULD** (preferred)
   - **MAY** (optional)
4. Declare clarity status for each major aspect:
   - **CLEAR:** Fully specified
   - **ASSUMED:** Reasonable assumption (user can override)
   - **BLOCKED:** Cannot proceed until answered
5. Tag each acceptance criterion with its **Verification Tier** — Step-0 operationalization (see below).
6. Get user approval on spec
7. THEN proceed to Step 4 (draft the plan) with spec as input

**Template:** `templates/requirements-spec.md`

**Why this helps:** Catches ambiguity BEFORE planning. Reduces mid-plan pivots by 30-50%.

#### Step-0 Operationalization: Tag Each Acceptance Criterion with a Verification Tier

Every acceptance criterion is operationalized into a falsifiable check and tagged with the tier at which "achieved" will later be confirmed:

- **Tier 1 — script-decidable:** a deterministic script gives yes/no (diff, grep, test exit).
- **Tier 2 — locatable judgment:** decomposes into sub-claims each pinned to an artifact (`file:line`, a test, an output value) plus a sufficiency argument.
- **Tier 3 — irreducible judgment:** no single artifact pins it; verified by independent refutation or a diverse-lens panel (see `.claude/references/evidence-gating-tier3-panel.md`).

**Why operationalize up front:** assigning a tier *before* any work runs forces the goal to become falsifiable. It prevents lazy "did it work? yes" prompting — a verdict of "achieved / compliant" must then cite a tagged criterion rather than assert itself — and it shrinks the irreducible-judgment residue by pushing as many sub-claims as possible down toward Tier 1. This is the planning-time face of `adversarial-default.md`'s evidence-gating discipline (burden of proof on the asserter; compliance is a positive claim requiring evidence). Full tier semantics live in `.claude/references/evidence-gating-detail.md`.

**Enforcement is ADVISORY ONLY — it NEVER blocks.** One non-blocking nudge:

1. A **reminder** when a spec's acceptance criteria are untagged.

An untagged criterion does not stop the spec, the plan, or the work. The discipline is a floor that makes "show evidence" the default; it is not a gate. (A critic deduction for verdicts that cite no tier-tagged criterion is a candidate future hardening — it is not wired into any critic agent today, so the rule does not promise it. See `.claude/references/evidence-gating-detail.md` § Optional hardening and `adversarial-default.md`.)

### Plans on Disk

Plans survive context compression. Save every plan to:

```
quality_reports/plans/YYYY-MM-DD_short-description.md
```

Format: Status (DRAFT/APPROVED/COMPLETED), approach, files to modify, verification steps.

### Enforcement

Convention, not a hook (`plan-persist-check.py` pruned 2026-09-16). After a plan is approved, copy it to `quality_reports/plans/YYYY-MM-DD_<slug>.md` and add an `INDEX.md` line so it survives context compaction.

---

## 2. The Orchestrator Loop

**After a plan is approved, the orchestrator takes over autonomously.** It identifies the phases whose inputs are satisfied, dispatches each worker with its paired critic (parallel when independent), has the critic score the work, verifies the outputs, aggregates the score against the gates in `quality.md`, and presents the summary to the user.

**Read** `.claude/references/orchestration-loop.md` for the loop steps, the agent dispatch table, parallel dispatch, the phase-dependency graph with re-entry and the standalone skills table (open it when you orchestrate in the main session without dispatching the `orchestrator` agent, or when choosing which agents a task needs).

### Limits

- **Worker-critic pairs:** max 3 rounds (then escalate)
- **Overall loop:** max 5 rounds
- **Verification retries:** max 2 attempts
- Never loop indefinitely

### Simplified Mode (R Scripts / Explorations)

For standalone R scripts, simulations, and explorations — use the simplified loop:

```
Plan approved → implement → run code → check outputs → score → done
```

No multi-agent reviews. Just: write, test, verify quality >= 80.

**Verification Checklist (Simplified):**
- [ ] Script runs without errors
- [ ] All packages loaded at top
- [ ] No hardcoded absolute paths
- [ ] `set.seed()` once at top if stochastic
- [ ] Output files created at expected paths
- [ ] Quality score >= 80

### "Just Do It" Mode

When user says "just do it" / "handle it":
- Skip final approval pause
- Auto-commit if score >= 80
- Still run the full verify-review-fix loop
- Still present the summary

---

## 3. Dependency Graph

**Phases activate by dependency, not sequence. Research is not a waterfall.** The Orchestrator checks the dependency graph before dispatching any agent; a phase whose inputs are satisfied can activate whether or not earlier phases are "complete". The phase table, with what each phase requires and when it re-enters, is in `.claude/references/orchestration-loop.md` § Dependency Graph.

---

## 4. Standalone Access

**Any skill can be invoked directly, bypassing the pipeline.** In orchestrated mode the Orchestrator dispatches agents through the dependency graph; in standalone mode the user invokes a skill, which runs its agent(s) right now with no phase dependencies and returns the results. The skills are listed in `CLAUDE.md` § Skills Quick Reference.

### Constraint

`/new-project` is the only skill that is always orchestrated — it exists to launch the full pipeline. Everything else can run standalone.

---

## 5. Context Management

### General Principles
- Prefer auto-compression over `/clear`
- Save important context to disk before it's lost
- `/clear` only when context is genuinely polluted

### Context Survival Strategy

**Before Auto-Compression:**
When approaching context limits, ensure:
1. MEMORY.md has all `[LEARN]` entries from this session
2. Session log is current (updated within 10 minutes)
3. Active plan is saved to disk
4. Open questions are documented in session log

Compaction is automatic near the context limit (a discipline, not a hook; `pre-compact.py` pruned 2026-09-16). Keep the session log and any active plan current as you go so a compaction never loses them.

**After Compression:**
First message should be: "Resuming after compression. Last task: [read most recent plan + git log]. Status: [next step]."

### Session Recovery

After compression or new session:
1. Read `CLAUDE.md` + most recent plan in `quality_reports/plans/`
2. Check `git log --oneline -10` and `git diff`
3. State what you understand the current task to be
