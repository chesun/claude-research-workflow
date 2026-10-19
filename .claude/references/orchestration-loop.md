# Orchestration — loop, dependency graph and standalone skills

**Class:** B (overlay-customized; see `.claude/file-classes.toml`, and merge by hand, never copy over an overlay's version). Pointer-loaded detail for `.claude/rules/workflow.md` § 2 The Orchestrator Loop, § 3 Dependency Graph and § 4 Standalone Access (moved from the rule on 2026-10-19); there is no auto-load.

The rule keeps the limits (3 rounds per pair, 5 overall rounds, 2 verification retries), Simplified Mode, "Just Do It" mode and the `/new-project` constraint. The `orchestrator` agent (`.claude/agents/orchestrator.md`) carries its own dependency, dispatch and routing tables for when it is dispatched.

## The Orchestrator Loop

**After a plan is approved, the orchestrator takes over autonomously.**

### The Dependency-Driven Loop

```
Plan approved → orchestrator activates
  │
  Step 1: IDENTIFY — Check dependency graph, determine which phases can activate
  │
  Step 2: DISPATCH — Launch worker agents (parallel when independent)
  │         Each worker paired with its critic (see agents.md)
  │
  Step 3: REVIEW — Critic evaluates worker output, produces score
  │         If score < 80 → worker fixes → critic re-reviews (max 3 rounds)
  │         If 3 rounds fail → ESCALATE (see agents.md)
  │
  Step 4: VERIFY — Compile, render, run code, check outputs
  │         If verification fails → fix → re-verify (max 2 attempts)
  │
  Step 5: SCORE — Aggregate scores across components (see quality.md)
  │
  └── Score >= threshold?
        YES → Present summary to user
        NO  → Identify blocking components, loop back to Step 2
              After max 5 overall rounds → present with remaining issues
```

### Agent Dispatch Rules

The Orchestrator selects agents based on what the task requires:

| Task Involves | Agents Dispatched |
|--------------|-------------------|
| Literature/references | librarian + librarian-critic |
| Data sourcing | explorer + explorer-critic |
| Data engineering | data-engineer + coder-critic |
| Identification strategy (applied-micro overlay) | strategist + strategist-critic |
| Experimental design (behavioral overlay) | designer + designer-critic |
| Formal theory/model | theorist + proof-verifier (per node) + theorist-critic (paper) |
| R/Stata/Python scripts | coder + coder-critic |
| Paper manuscript | writer + writer-critic |
| Peer review | Orchestrator → domain-referee + methods-referee |
| Beamer talks | storyteller + storyteller-critic |
| Replication package | verifier (submission mode) |
| Compilation only | verifier (standard mode) |

### Parallel Dispatch

Independent phases run concurrently:
- Literature and Data discovery run in parallel
- Code and Paper execution run in parallel (after Strategy)
- Presentation can run parallel with Peer Review

## Dependency Graph

**Phases activate by dependency, not sequence. Research is not a waterfall.**

### Phase Dependencies

| Phase | Requires | Can Re-enter? |
|-------|----------|---------------|
| Discovery | Research idea | Always — librarian is persistent |
| Strategy | At least one of: literature review OR data assessment | Yes — new data or literature can trigger re-strategy |
| Execution (Code) | Approved strategy/design (strategist-critic OR designer-critic >= 80) | Yes — strategy revision triggers re-coding |
| Execution (Write) | Approved code (coder-critic >= 80) | Yes — new results trigger rewriting |
| Peer Review | Approved paper (writer-critic >= 80) + approved code | Yes — major revisions loop back |
| Submission | Orchestrator accepts + Verifier PASS + overall >= 95 | No — terminal |
| Presentation | Approved paper (can run parallel with Peer Review) | Yes — paper revisions trigger talk updates |

### How It Works

The Orchestrator checks the dependency graph before dispatching any agent. If a phase's inputs are satisfied, it can activate — regardless of whether earlier phases are "complete."

**Example — entering mid-pipeline:**
You already have data and a draft paper. You can enter at Strategy (skip Discovery) or even at Peer Review (skip Execution). The Orchestrator checks dependencies, not phase numbers.

**Example — targeted re-entry:**
A referee says "control for X." The Orchestrator routes back to coder (not through the full pipeline), coder-critic reviews, writer updates, writer-critic reviews the update, then back to peer review.

### Parallel Activation

Independent phases run concurrently:
- Literature (librarian + librarian-critic) and Data (explorer + explorer-critic) run in parallel
- Code (coder + coder-critic) and Paper (writer + writer-critic) run in parallel after Strategy
- Presentation can run parallel with Peer Review

## Standalone Access

**Any skill can be invoked directly, bypassing the pipeline.**

### Two Modes

**Mode 1: Orchestrated (within the pipeline)**

The Orchestrator dispatches agents through the dependency graph. The user says:

> "I want to study the effect of minimum wage on employment using CPS data."

The Orchestrator activates Discovery → Strategy → Execution → Peer Review automatically.

**Mode 2: Standalone (direct access)**

The user invokes a skill directly:

> `/strategize paper/main.tex` (applied-micro overlay) or `/design experiment` (behavioral overlay)

This runs the relevant critic agent alone, right now, no phase dependencies. The concrete skill names depend on the overlay installed.

### Why Both Modes

- **Pipeline mode** is for full projects where the Orchestrator manages the flow
- **Standalone mode** is for targeted tasks: "just check this one thing"
- Most users start with standalone skills and graduate to the pipeline

### Standalone Skills

All skills in the reference below work without pipeline context when invoked directly. They dispatch their agent(s) and return results.

| Skill | What It Does |
|-------|-------------|
| `/discover` | Literature search + data discovery |
| `/strategize` (applied-micro overlay) | Identification strategy design + review |
| `/design`, `/theory`, `/preregister` (behavioral overlay) | Experiment design, formal model, pre-registration |
| `/analyze` | End-to-end data analysis (code + debug) |
| `/write` | Draft paper sections (anti-hedging, notation protocol) |
| `/humanize` | Strip AI writing patterns from any external-facing doc (paper, slide, README, blog, cover/response letter) per `.claude/rules/anti-ai-prose.md` |
| `/review` | Simulated peer review (domain + methods referees) |
| `/revise` | R&R routing per revision-protocol |
| `/talk` | Beamer talk from paper |
| `/submit` | Final gate: score >= 95, all components >= 80 |
| `/tools` | Utility skills (compile, validate-bib, commit, etc.) |
