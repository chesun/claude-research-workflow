# Infra Survey D — Native-primitive cross-check
**Date:** 2026-09-22
**Reviewer:** survey agent D (general-purpose)
**Target:** Claude Code / Claude 5 native capabilities (late 2026)
**Status:** Active
**Score:** n/a (survey)

## Purpose

Reference table of what the **Claude Code harness + Claude 5 platform now provide natively** (late 2026), so the survey's other workstreams can say "adapt toward the native primitive" rather than keep a hand-rolled equivalent. This is the "don't hand-roll what's now first-class" check.

Relevance tags used throughout: **(a)** orchestration/critic loops · **(b)** memory/logging discipline · **(c)** voice/writing · **(d)** cross-repo distribution.

Evidence dates: official docs at `code.claude.com/docs` and `platform.claude.com/docs` fetched 2026-09-22; version numbers are as stated in those docs / corroborating write-ups. Where a claim rests on a secondary source it is marked.

---

## Capability table

### 1. Skills — named instruction bundles
- **What it is:** A `SKILL.md` file (YAML frontmatter + markdown body) plus optional scripts/templates/reference docs. Content loads *only when invoked*, so long reference material is nearly free until needed. Two invocation modes: **model-invoked** (Claude auto-loads based on `description`) and **user-invoked** (`/skill-name`, forceable via `disable-model-invocation: true`). Discovery locations, priority order: enterprise managed → `~/.claude/skills/` (user) → `.claude/skills/` (project) → nested `./<subdir>/.claude/skills/` → plugin `skills/` (namespaced `/plugin:skill`). Supports `context: fork` (run in a subagent), `agent:` (which subagent type), `allowed-tools:`, `arguments:`, `paths:` (glob-gated activation), and dynamic injection (`` !`git diff` ``).
- **Maturity:** First-class, actively enhanced (claude.ai sync, live change detection, nested discovery). Supersedes older `.claude/commands/`.
- **How you'd use it:** This template already uses skills heavily (`/review`, `/analyze`, `/talk`, `/tools`, ...). Nothing to migrate — it is already on the native primitive.
- **Replaces (hand-rolled):** custom-command macros; ad-hoc "read this doc first" prompting.
- **Relevance:** (a) skills can `context: fork` into a subagent = lightweight critic dispatch; (b) a skill can encode logging discipline; (c) a `/humanize`-style skill is the natural home for voice rules; (d) skills ship inside plugins.
- **Source:** https://code.claude.com/docs/en/skills

### 2. Subagents / agents — context isolation, forking, background dispatch
- **What it is:** Markdown file in `.claude/agents/` (frontmatter + system-prompt body). Each runs in its **own context window**, own system prompt, own tool allow/deny list, own model, own permission mode. Returns only a **summary** to the lead (+ an agent ID for resumption). Key frontmatter: `model` (sonnet/opus/haiku/inherit), `tools` / `disallowedTools`, `permissionMode`, `maxTurns`, `skills:` (preload), `memory:` (user/project/local), `background: true`, `isolation: worktree`, `omitClaudeMd`. Built-in types: **Explore** (read-only search, capped at Opus), **Plan** (read-only research), **general-purpose** (full tools), plus task helpers. **Fork** is the special case: subagent inherits the parent's *full* context, history, tool results, **and output style**. **Background** subagents run concurrently (default in interactive mode) with a restricted read/write tool set. Nesting default 3 deep (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`); 20 concurrent default (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`). Scope precedence: managed → `--agents` flag → project → user → plugin.
- **Maturity:** First-class, versioned rapidly (v2.1.198+ thinking inheritance; v2.1.246+ maxTurns partial marking; v2.1.271+ omitClaudeMd).
- **How you'd use it:** This template's worker/critic agents (`coder`, `coder-critic`, `writer`, `writer-critic`, ...) are *already* native subagents. The still-hand-rolled parts are (i) the **orchestrator dispatch loop** and (ii) the **worker→critic 3-round convergence** logic, which live as prose in `workflow.md`/`agents.md` and are executed by the model, not the harness.
- **Replaces (hand-rolled):** the `orchestrator` agent's manual "dispatch worker, then dispatch critic" narration where determinism matters (see Workflows, row 3).
- **Relevance:** (a) core — critics = read-only subagents, separation-of-powers = `tools`/`disallowedTools`; (b) `memory:` field scopes per-agent memory; (c) note: non-fork subagents do **not** inherit output style — only forks do; (d) agents ship inside plugins.
- **Source:** https://code.claude.com/docs/en/sub-agents

### 3. Workflows — deterministic multi-agent orchestration + schema-validated output
- **What it is:** A JavaScript file (the "Workflow tool") that orchestrates subagents with a small primitive set — **`agent()`, `parallel()`, `pipeline()`, `phase()`**. The **control flow is deterministic**: code owns order, routing, and stop condition, instead of the model deciding turn-by-turn "am I done." The script runs as orchestrator and **consumes zero tokens itself** (cost is only in the `agent()` calls). The runtime handles concurrency caps, progress reporting, and **resume on interruption**. Introduced ~2026-05-28 (secondary sources). Pairs with **schema-validated structured output**: pass a JSON Schema (`outputFormat`/`output_format`, or `agent(…, { schema })`), and the SDK **validates and re-prompts on failure**; the result carries a `structured_output` field, and exhausting retries yields `error_max_structured_output_retries`. Schemas accept types/enums/const/required/nested/`$ref`; generate from Zod or Pydantic.
- **Maturity:** First-class in the Agent SDK; the schema mechanism is what this template's own `adversarial-default.md` already cites as the Phase-3 Tier-2 binding ("`StructuredOutput` mechanically rejects an empty-evidence verdict").
- **How you'd use it:** Convert the orchestrator's fixed dependency graph (Discovery→Strategy→Execution→Peer-review) and the worker-critic loop into a `Workflow()` script. Force each critic verdict through a `required: [claim, artifact_citation, score]` schema so an empty-evidence PASS is *mechanically* impossible rather than prose-enforced.
- **Replaces (hand-rolled):** the entire hand-rolled orchestrator loop, the "max 3 rounds then escalate" counter, parallel-dispatch bookkeeping, and the aspirational Tier-2 evidence gate — all currently prose the model must remember to honor.
- **Relevance:** (a) direct, highest-value replacement for the hand-rolled orchestrator; (b) resume-on-interruption is a durability win for long pipelines; (c) —; (d) a workflow script can be distributed via a plugin.
- **Caveat:** requires committing to the Agent SDK / JS scripting; for a strictly-personal econ template this is real setup cost. Adopt selectively (the critic-verdict schema is the cheapest high-value slice).
- **Source (official mechanism):** https://heyclau.de/entry/guides/structured-output-from-claude-agent-sdk-workflows ; (overview, secondary) https://alexop.dev/posts/claude-code-workflows-deterministic-orchestration/

### 4. Memory — Auto Memory + memory tool + CLAUDE.md
- **What it is:** Three layers. (i) **CLAUDE.md / AGENTS.md** — instructions you write, loaded at every session start; `.claude/rules/` scopes rules to file types. (ii) **Auto Memory** — Claude writes its own `MEMORY.md` from your corrections/preferences; **on by default since v2.1.59 (Feb 2026)**, free, no setup; capped (~200 lines / 25KB) and fully loaded at session start (no semantic search). (iii) **The memory tool** (platform-level) — Claude create/read/update/deletes files in a memory directory that persist across conversations, building knowledge without holding it all in context. Docs state plainly: CLAUDE.md and Auto Memory are treated as **context, not enforced config** — "to block an action regardless of what Claude decides, use a PreToolUse hook instead."
- **Maturity:** First-class and default-on. This template's own `MEMORY.md` index (`.claude/projects/.../memory/MEMORY.md`) already rides the native Auto Memory system.
- **How you'd use it:** The template's "MEMORY.md discipline" is already the native mechanism — no hand-rolled parser needed. Session logs (`quality_reports/session_logs/`) remain a *human-durable, git-tracked* record that Auto Memory does not replace (Auto Memory is capped, unsearchable, and machine-local).
- **Replaces (hand-rolled):** any bespoke "read [LEARN] entries from MEMORY.md" bootstrapping — the harness now loads it automatically.
- **Relevance:** (a) `memory:` per-subagent scoping; (b) core — this *is* the memory/logging primitive; (c) —; (d) memory is machine/project-local, so it does **not** cross-repo-distribute (that stays a session-log + git concern).
- **Source:** https://code.claude.com/docs/en/memory ; https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool

### 5. Context management / automatic compaction
- **What it is:** Sessions auto-compact near the context limit; with Session Memory, compaction loads a **pre-written background summary** into the fresh window rather than re-analyzing. A `PreCompact` hook event fires before compaction.
- **Maturity:** First-class, default.
- **How you'd use it:** Rely on it; the template already pruned its `pre-compact.py` reminder hook (2026-09-16) in favor of "keep the session log current as you go."
- **Replaces (hand-rolled):** manual pre-compaction context-saving nags.
- **Relevance:** (a)/(b) keeps long orchestrated runs alive without losing the plan/log.
- **Source:** https://code.claude.com/docs/en/memory ; https://platform.claude.com/cookbook/misc-session-memory-compaction

### 6. Hooks — deterministic lifecycle enforcement
- **What it is:** Shell/script commands the harness runs on lifecycle events. **~30 events as of 2026-07-26** (secondary count), including the load-bearing ones this template uses: `PreToolUse` (only event where exit code 2 hard-blocks the call), `PostToolUse`, `Stop`, `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `PreCompact`. Newer/expanded events include `PostToolUseFailure`, `PostToolBatch`, `PermissionRequest`/`PermissionDenied`, `SubagentStart`/`SubagentStop`, `TaskCreated`/`TaskCompleted`, `FileChanged`, `SessionEnd`, `Notification`, `UserPromptExpansion`, `InstructionsLoaded`, `WorktreeCreate`/`WorktreeRemove`.
- **Maturity:** First-class, mature; the enforcement backbone this template already depends on (`destructive-action-guard.py`, `primary-source-check.py`, `derive-check-advisory.py`, `review-receipt-check.py`).
- **How you'd use it:** Already native — this is the template's "gates not nags" foundation. Note `SubagentStart`/`SubagentStop` and `TaskCreated`/`TaskCompleted` are *newer* events that could replace some prose orchestration bookkeeping with real harness callbacks.
- **Replaces (hand-rolled):** N/A — hooks *are* the native primitive; the template is correctly on it.
- **Relevance:** (a) `SubagentStop`/`TaskCompleted` = native critic-completion signals; (b) `Stop`/`SessionStart` for logging; (c) a `Stop` hook could enforce a voice check; (d) hooks ship in plugins.
- **Source:** https://code.claude.com/docs/en/hooks ; event-count corroboration https://claudefa.st/blog/tools/hooks/hooks-guide

### 7. Output styles — role/tone/format ("voice") control  ← key for voice/writing
- **What it is:** A markdown file (frontmatter + instructions) that **changes Claude Code's default instructions** — role, tone, and output format — for **every response**. Distinct from CLAUDE.md (adds a user message) and `--append-system-prompt` (one-off). Built-ins: **Default, Proactive, Concise (v2.1.237+), Explanatory, Learning**. Custom styles live at `~/.claude/output-styles` (user), `.claude/output-styles` (project), or managed policy. Frontmatter: `name`, `description`, `keep-coding-instructions` (default false — omit the SWE instructions entirely for a writing/analyst persona), `force-for-plugin` (a plugin can auto-apply its style whenever enabled). Switch via `/output-style <name>` or the `outputStyle` settings field; applies from the next message. **Crucial scope limit:** an output style applies to the **main conversation and forks only** — other (non-fork) subagents run their own system prompt, so a style does **not** change how critic/worker subagents write.
- **Maturity:** First-class, dedicated docs, plugin-shippable, versioned (`/output-style` in headless + SDK v2.1.269+).
- **How you'd use it:** This is the closest native analogue to the template's **anti-AI-prose / humanizer voice rules** (`.claude/rules/anti-ai-prose.md`, `/humanize`). A project-level output style with `keep-coding-instructions: true` could carry the house voice for the *main* conversation cheaply. BUT because it doesn't reach subagents, the paper/talk writing done inside `writer`/`storyteller` subagents still needs the voice rules in *their* system prompts (or a fork). So output styles **complement, not replace**, the humanizer skill for artifact writing.
- **Replaces (hand-rolled):** re-prompting for tone each turn in the main session; a `Concise`-style default. Does **not** fully replace the humanizer pass on generated artifacts.
- **Relevance:** (c) direct — the one native voice/writing primitive; (a) forks inherit it; (d) `force-for-plugin` distributes a house voice.
- **Source:** https://code.claude.com/docs/en/output-styles

### 8. Plugins — versioned bundles (skills + agents + hooks + commands + output-styles + MCP)  ← key for cross-repo distribution
- **What it is:** A self-contained, **versioned** directory bundling skills, agents, hooks, slash commands, output-styles, and MCP server configs into one installable/updatable unit. Discovered/installed via **marketplaces** (`/plugin marketplace add`); Claude Code auto-adds the official `claude-plugins-official` marketplace on first interactive start. Solves the "works-on-my-machine" distribution problem.
- **Maturity:** First-class, official marketplace, dedicated docs.
- **How you'd use it:** This is the native replacement for the template's **hand-rolled cross-repo propagation system** (`/tools propagate`, `/tools sync-overlays`, `.claude/file-classes.toml`, the consumer registry). Packaging the workflow as a plugin lets consumer repos `install`/`update` a versioned bundle instead of the file-class-routed copy loop.
- **Replaces (hand-rolled):** `/tools propagate`, `/tools sync-overlays`, file-class manifest, consumer registry — the whole Class A/B/C routing machinery.
- **Relevance:** (d) direct and highest-value for distribution; (a)/(b)/(c) it's the container that ships all the other primitives.
- **Caveat:** the template's propagation is **class-aware** (universal vs overlay-customized vs overlay-only files, read from different branches). A plugin is a single versioned bundle; overlay-specific customization (applied-micro vs behavioral) would need either separate plugins or plugin-level config. Migrating gains versioning/update UX but must re-express the overlay routing.
- **Source:** https://code.claude.com/docs/en/discover-plugins ; https://code.claude.com/docs/en/plugins-reference

### 9. MCP — tool/data servers
- **What it is:** Model Context Protocol servers expose external tools/data (databases, issue trackers, internal docs) to Claude over a standard protocol; configured per-project or shipped inside plugins.
- **Maturity:** First-class, mature.
- **How you'd use it:** Marginal for this template (personal econ workflow, hard enterprise-remote-only + no-client-names constraints per project memory). Relevant only if the workflow later needs live data/tooling (e.g., a citations or dataset server).
- **Replaces (hand-rolled):** N/A here — the template doesn't hand-roll data servers.
- **Relevance:** (a) tools for agents; otherwise low for this template.
- **Source:** https://code.claude.com/docs/en/discover-plugins (bundling)

### 10. Background tasks / structured output (misc first-class)
- **What it is:** `background: true` subagents run concurrently and report back on completion (surfaced via `TaskCreated`/`TaskCompleted`/`SubagentStop` hooks). Structured output (row 3) is the schema-validated result channel. Together they enable fan-out research with deterministic collection.
- **Relevance:** (a) parallel critic/referee dispatch without blocking; (b) —.
- **Source:** https://code.claude.com/docs/en/sub-agents

---

## Hand-rolled → native mapping (the four template areas)

| Template's hand-rolled thing | Native primitive to adapt toward | Verdict |
|---|---|---|
| **Orchestrator + worker-critic loop** (prose dispatch in `workflow.md`/`agents.md`, executed by the model) | **Workflows** (`agent`/`parallel`/`pipeline`/`phase`, deterministic control flow) + **subagents** (already native) + **structured-output schema** for critic verdicts + `SubagentStop`/`TaskCompleted` **hooks** | *Adapt, selectively.* The agents are already native; the **loop determinism and the Tier-2 evidence gate** are the parts worth moving from prose to a `Workflow()` script with a `required:[claim, artifact_citation, score]` schema. Full migration = Agent-SDK/JS commitment; cheapest slice is the critic-verdict schema. |
| **MEMORY.md discipline** (bespoke `[LEARN]` bootstrapping) | **Auto Memory** (default-on since v2.1.59) + **memory tool** + **CLAUDE.md/`.claude/rules/`** | *Already on the native primitive.* Keep git-tracked **session logs** as the durable/searchable record Auto Memory (capped, machine-local, unsearchable) does not provide. No parser to hand-roll. |
| **Anti-AI-prose / humanizer voice rules** (`anti-ai-prose.md`, `/humanize`) | **Output styles** (native voice/role/tone control; `keep-coding-instructions`, `force-for-plugin`) | *Complement, don't replace.* An output style carries house voice in the **main conversation + forks** cheaply — but **not** inside `writer`/`storyteller` subagents (they run their own system prompt). So keep the humanizer pass for generated artifacts; add an output style for main-session voice. This is the one native voice primitive that exists. |
| **Cross-repo propagation** (`/tools propagate`, `/tools sync-overlays`, `file-classes.toml`, consumer registry) | **Plugins + marketplaces** (versioned bundle of skills+agents+hooks+commands+output-styles+MCP; `/plugin marketplace add`) | *Adapt toward it.* Native versioning/update UX replaces the copy-loop. Cost: re-express the **class-aware overlay routing** (universal vs applied-micro vs behavioral, per-branch) as separate plugins or plugin config — a plugin is one bundle, not a branch-routed manifest. |

### One-line takeaways
- **Biggest genuine replacements:** propagation → **plugins**; MEMORY.md → **Auto Memory** (already there).
- **Biggest "adapt, don't wholesale-replace":** orchestrator loop → **Workflows** (adopt the critic-verdict *schema* first — it directly hardens this repo's own Tier-2 evidence-gating claim).
- **Voice:** **output styles** are the native voice primitive, but scope-limited to main conversation + forks, so they supplement rather than supplant the humanizer for subagent-authored papers/talks.
- **Already correctly native:** skills, subagents, hooks, context compaction — no migration needed.
