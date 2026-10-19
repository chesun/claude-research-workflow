# Orchestration — loop, dependency graph and standalone skills

**Class:** B (overlay-customized; see `.claude/file-classes.toml`, and merge by hand, never copy over an overlay's version). Pointer-loaded detail for `.claude/rules/workflow.md` § 2 The Orchestrator Loop, § 3 Dependency Graph and § 4 Standalone Access (moved from the rule on 2026-10-19; behavioral overlay version); there is no auto-load.

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
| Formal theory/model | theorist + proof-verifier (per node) + theorist-critic (paper) |
| Experiment design | designer + designer-critic |
| Qualtrics survey | qualtrics-specialist |
| oTree experiment | otree-specialist |
| Stata/R/Python scripts | coder + coder-critic |
| Paper manuscript | writer + writer-critic |
| Peer review | Orchestrator → domain-referee + methods-referee |
| Beamer talks | storyteller + storyteller-critic |
| Replication package | verifier (submission mode) |
| Compilation only | verifier (standard mode) |

### Parallel Dispatch

Independent phases run concurrently:
- Literature and Data discovery run in parallel
- Theory and Design can overlap (theory produces predictions that feed design)
- Code and Paper execution run in parallel (after Design + Pre-registration)
- Presentation can run parallel with Peer Review

## Dependency Graph

**Phases activate by dependency, not sequence. Research is not a waterfall.**

### Phase Dependencies

| Phase | Requires | Can Re-enter? |
|-------|----------|---------------|
| Discovery | Research idea | Always — librarian is persistent |
| Theory | Literature review or research question | Yes — new evidence can trigger model revision |
| Design | Testable predictions (from theory) OR research question | Yes — theory revision triggers redesign |
| **Pre-registration** | **Approved design (designer-critic >= 80)** | **GATE — no data collection without it** |
| Implementation | Approved design → Qualtrics/oTree code | Yes — design changes trigger reimplementation |
| Data Collection | Pre-registration filed + implementation approved | No — once started, design is locked |
| Execution (Code) | Data collected + approved design | Yes — new data triggers re-analysis |
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
- Theory (theorist + theorist-critic) and Design (designer + designer-critic) can overlap
- Code (coder + coder-critic) and Paper (writer + writer-critic) run in parallel after Pre-registration
- Presentation can run parallel with Peer Review

The pre-registration gate itself stays in `.claude/rules/workflow.md` § 3: no data collection or analysis agent is dispatched before `/preregister` has produced a filed registration.

## Standalone Access

**Any skill can be invoked directly, bypassing the pipeline.**

### Two Modes

**Mode 1: Orchestrated (within the pipeline)**

The Orchestrator dispatches agents through the dependency graph. The user says:

> "I want to study the effect of minimum wage on employment using CPS data."

The Orchestrator activates Discovery → Strategy → Execution → Peer Review automatically.

**Mode 2: Standalone (direct access)**

The user invokes a skill directly:

> `/strategize paper/main.tex`

This runs the strategist-critic agent alone, right now, no phase dependencies.

### Why Both Modes

- **Pipeline mode** is for full projects where the Orchestrator manages the flow
- **Standalone mode** is for targeted tasks: "just check this one thing"
- Most users start with standalone skills and graduate to the pipeline

### Standalone Skills

All skills in the reference below work without pipeline context when invoked directly. They dispatch their agent(s) and return results.

| Skill | What It Does |
|-------|-------------|
| `/discover` | Literature search + data discovery |
| `/strategize` | Identification strategy design + review |
| `/analyze` | End-to-end data analysis (code + debug) |
| `/write` | Draft paper sections (anti-hedging, notation protocol) |
| `/humanize` | Strip AI writing patterns from any external-facing doc (paper, slide, README, blog, cover/response letter) per `.claude/rules/anti-ai-prose.md` |
| `/review` | Simulated peer review (domain + methods referees) |
| `/revise` | R&R routing per revision-protocol |
| `/talk` | Beamer talk from paper |
| `/submit` | Final gate: score >= 95, all components >= 80 |
| `/tools` | Utility skills (compile, validate-bib, commit, etc.) |
