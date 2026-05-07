# Comprehensive Propagation Plan: File Taxonomy, Routing, and Overlay Sync

**Date:** 2026-05-07
**Status:** Active (DRAFT — pending user approval before implementation)
**Extends:** `2026-05-06_tools-propagate-plan.md` (v1 plan; propagate.py implementation stays — this plan adds the file-class layer on top)
**Authors:** Christina + Claude

---

## TL;DR

The v1 `/tools propagate` skill works for the simple case (a hook that's identical across branches). It breaks for two harder cases, both surfaced by the 2026-05-06 cherry-pick attempt:

1. **Universal-but-recent files** — e.g., `data-version-control.md` exists only on `main`. Today, propagating to a behavioral consumer reads `behavioral:.claude/rules/data-version-control.md`, doesn't find it, and skips. Wrong: the file *should* land on every consumer regardless of overlay.
2. **Overlay-customized files** — e.g., `orchestrator.md` has genuine behavioral-specific content on the `behavioral` branch. Reading from `main` would clobber the customization. Reading from `behavioral` is correct, but only because someone hand-curated that branch.

The fix has three pieces:

- **A three-class file taxonomy** (Universal, Overlay-customized, Overlay-only) declared in a manifest at `.claude/file-classes.toml`.
- **Modified routing in `propagate.py`** — pick the source branch based on the file's class, not blindly the consumer's overlay.
- **A new `/tools sync-overlays` skill** — periodically push Universal-class updates from `main` to `applied-micro` and `behavioral` so overlay branches stay current on shared infrastructure.

A one-time bootstrap audits every tracked file, classifies it, and applies the initial overlay sync.

---

## 0. Decisions to lock in this plan

Items marked **[USER]** need explicit confirmation before implementation. Items without **[USER]** are recommendations the author of this plan is ready to defend; flag any you disagree with on review.

| # | Decision | Recommended value | Rationale |
|---|---|---|---|
| C1 | Number of file classes | 3: Universal, Overlay-customized, Overlay-only | Matches observed reality; more classes = more complexity; fewer classes = can't represent today's branches |
| C2 | Manifest location | `.claude/file-classes.toml` (tracked in git on main) | Versioned + reviewable; not under `.claude/state/*` so not gitignored; lives at the workflow level |
| C3 | Manifest distribution to overlays | Manifest is itself Class A (Universal); `/tools sync-overlays` copies it to overlay branches | Single source of truth on main; overlays don't drift on classification |
| C4 | Default class for unlisted files | Universal | Matches the empirical majority; overlay-customized and overlay-only are the exceptions and must be declared explicitly |
| C5 | Manifest format | Per-class lists with glob support; explicit per-file entries override globs | Easy to scan; globs handle bulk paths (all hooks); per-file handles ambiguous dirs (agents) |
| C6 | propagate.py routing per class | Universal → read from `main`; Overlay-customized → read from consumer's overlay; Overlay-only → read from consumer's overlay (skip if consumer is on `main`) | Each class has a single source-of-truth branch; routing follows that |
| C7 | sync-overlays scope | Class A only; never touches Class B or C | Class B/C live on the overlay branch by design; mechanical sync would clobber customizations |
| C8 | sync-overlays mechanism | Per-file copy from `main` worktree to overlay worktrees, then commit per overlay | Avoids parallel-history cherry-pick conflicts; works because Class A files have *no* legitimate overlay-side edits |
| C9 | sync-overlays cadence | On-demand (manual invocation); not automated | Same reasoning as propagate — cross-branch operations need user intent |
| C10 | **[USER]** sync-overlays as separate skill vs subcommand of propagate | Recommend: separate skill `/tools sync-overlays` | Different conceptual operation (intra-workflow overlay sync, not workflow→consumer); separate testing surface |
| C11 | **[USER]** Bootstrap classification approach | Recommend: one-shot audit script that proposes a manifest from current branch diffs; user reviews and edits before commit | Alternative: hand-write the manifest from scratch — slower, error-prone for ~200 paths |
| C12 | **[USER]** Initial overlay sync after bootstrap | Recommend: run sync-overlays immediately after manifest is committed; commit-per-class on each overlay | Catches up overlays in one structured operation; easier to review than dozens of cherry-picks |
| C13 | Class B file divergence detection in propagate | Already handled — propagate's existing `consumer_sha256_at_sync` mechanism applies per-file regardless of class | No extra logic needed |
| C14 | Class B file editing workflow | When a Class B file needs updating, edit it directly on the relevant overlay branch (or on a shared subset that lives in main and gets `\input{}`-style included into overlay versions — out of scope for v1) | The decision to make a file Class B *is* the decision that its overlay-side maintenance is manual |

---

## 1. Context: why we need this

The v1 propagate plan (2026-05-06) settled the architecture for syncing the workflow source repo to its consumer repos. It deferred the harder branch-aware question to a "v1.1 sync-overlays helper, out of scope here."

Tonight's cherry-pick attempt revealed that the deferred question is not optional. Three observations:

**Observation 1: Three branches with parallel histories.** `main`, `applied-micro`, and `behavioral` are not strict descendants. Same-day commits appear on all three with different SHAs (e.g., the 2026-05-04 session log). Christina's historical pattern has been manual cherry-picking from main onto overlays, which produces the parallel SHAs. Mechanical re-cherry-pick generates conflicts on every commit that touches `INDEX.md`, `CLAUDE.md`, or `.claude/skills/tools/SKILL.md`.

**Observation 2: Overlay branches mix two failure modes.** A diff of `main behavioral` shows ~50 paths. Some are stale-of-main (`context-monitor.py` shows -224 lines on overlay because the v1 hook is older). Some are genuinely customized (`orchestrator.md` has a "Behavioral/Experimental Pipeline" section the user authored that doesn't belong on main; `analyze/SKILL.md` defaults to Stata and references the behavioral domain-profile). A single sync mechanism that treats all of these the same will either drop user customizations (if it copies from main) or skip legitimate updates (if it never copies).

**Observation 3: New universal files have no overlay home.** `data-version-control.md`, `propagate.py`, the LFS+DVC plan — these were authored on main and exist nowhere else. They are universal infrastructure that should land on every consumer. Today's `propagate.py` reads from the consumer's overlay branch and finds nothing, so consumers on overlays never receive them. This is the immediate, concrete gap.

The taxonomy below is the smallest representation that captures these three cases distinctly.

---

## 2. The three-class taxonomy

### Class A — Universal

Definition: file is intended to be byte-identical on `main`, `applied-micro`, and `behavioral`. Source of truth is `main`. Any overlay-side divergence is *staleness*, not customization.

Examples:

- All hooks: `.claude/hooks/*.py`
- Most rules: `.claude/rules/{primary-source-first, derive-dont-guess, no-assumptions, adversarial-default, anti-ai-prose, destructive-actions, single-source-of-truth, decision-log, todo-tracking, logging, output-length, ...}.md`
- Most skill internals: `.claude/skills/{commit, compile, humanize, write, ...}/SKILL.md` — when their behavior is identical across overlays
- Templates: `templates/*` (gitattributes-lfs, setup-machine, data-MANIFEST/PROVENANCE/CHANGELOG)
- Cross-cutting infra: `.claude/state/.gitkeep`, `.gitignore`, `LICENSE`, root `README.md` (when project-state-section is overlay-agnostic)
- The manifest itself: `.claude/file-classes.toml`

Routing: `propagate.py` reads from `main:<path>`. `/tools sync-overlays` copies from `main` worktree → overlay worktrees.

### Class B — Overlay-customized

Definition: file exists on all three branches (or on `main` + at least one overlay) but with genuinely different content per branch. Source of truth is *the consumer's overlay*. `main` has its own version, but each overlay's version is authoritative for that overlay's consumers.

Examples (likely Class B based on observed diffs):

- `CLAUDE.md` — overlay branches add overlay-specific Skills Quick Reference rows
- `.claude/agents/orchestrator.md` — behavioral has an experimental pipeline section
- `.claude/agents/verifier.md` — diffs observed in stat
- `.claude/agents/writer.md` — small diffs observed
- `.claude/skills/analyze/SKILL.md` — behavioral defaults to Stata + behavioral domain-profile
- `.claude/skills/discover/SKILL.md` — likely overlay-flavored
- `.claude/skills/new-project/SKILL.md` — overlay pipeline differs
- `.claude/skills/review/SKILL.md` — overlay-flavored
- `.claude/skills/submit/SKILL.md` — overlay-flavored
- `.claude/skills/tools/SKILL.md` — likely Class B (some subcommands universal, some not — see §7.3 for the harder case)
- `.claude/rules/quality.md` — overlay weights differ
- `.claude/rules/workflow.md` — overlay phase tables differ
- `TODO.md` — per-branch task lists (this is also fine to treat as Class A and just not propagate; tag as "out-of-scope" in §7)
- Possibly: `master_supporting_docs/literature/papers/README.md` (small diffs observed)

Routing: `propagate.py` reads from `<consumer-overlay>:<path>`. `/tools sync-overlays` does not touch Class B files.

Maintenance burden: when the *universal portion* of a Class B file changes (e.g., a fix to a shared rule cross-reference in CLAUDE.md), the user must edit it on each overlay branch individually. This is a known cost. v2 could explore include-style decomposition (`\input{universal-section.md}`) but is out of scope here — the cost is small for ~10 files at low edit frequency.

### Class C — Overlay-only

Definition: file exists only on one or more overlay branches; does not exist on `main`. Source of truth is the overlay branch where it lives.

Examples:

**Behavioral overlay only:**

- `.claude/agents/{designer, theorist, theorist-critic, otree-specialist, qualtrics-specialist}.md`
- `.claude/references/{domain-profile-behavioral, inference-first-checklist, qualtrics-patterns, seminal-papers-by-subfield}.md`
- `.claude/rules/experiment-design-principles.md`
- `.claude/skills/{design, otree, preregister, qualtrics, theory}/SKILL.md`

**Applied-micro overlay only:**

- `.claude/agents/{strategist, strategist-critic}.md`
- `.claude/references/{domain-profile-applied-micro, identification-checklists, journal-profiles-applied-micro}.md`
- `.claude/rules/air-gapped-workflow.md`
- `.claude/skills/{balance, event-study, strategize}/SKILL.md`

Routing: `propagate.py` reads from `<consumer-overlay>:<path>`. If the consumer is on `main`, the file does not apply — skip with a clear message. `/tools sync-overlays` does not touch Class C files (each overlay-only file lives on exactly one branch; no syncing needed).

### Decision tree for classifying a new file

```
Is this file intended to be byte-identical on every branch where it exists?
├── Yes ──► Does it exist on main? 
│           ├── Yes  ──► Class A (Universal). Add to manifest under [universal] (or rely on default).
│           └── No   ──► This shouldn't happen. If it's universal, add it to main first.
└── No  ──► Does it exist on main?
            ├── Yes  ──► Class B (Overlay-customized). Add to manifest under [overlay-customized].
            └── No   ──► Class C (Overlay-only). Add to manifest under [overlay-only], specify which overlay branch(es).
```

---

## 3. The manifest: `.claude/file-classes.toml`

### 3.1 Location and visibility

Tracked in git, on `main` branch (and replicated to overlays via the manifest itself being Class A). NOT under `.claude/state/*` (that path is gitignored). Why `.claude/`: same family as other workflow-config files; not user-data.

### 3.2 Format

```toml
# .claude/file-classes.toml
# Workflow propagation manifest: classifies tracked paths into propagation classes.
# See quality_reports/plans/2026-05-07_comprehensive-propagation-plan.md for design.

# CLASS A — Universal: byte-identical on every branch; source-of-truth is main.
# DEFAULT: any path not listed in [overlay-customized] or [overlay-only] is treated as Class A.
# This section is the explicit allowlist for paths that *would otherwise be ambiguous*
# (e.g., a path that lives in a directory containing both Class A and Class B files).
[universal]
patterns = [
  ".claude/hooks/*.py",
  ".claude/rules/primary-source-first.md",
  ".claude/rules/derive-dont-guess.md",
  ".claude/rules/no-assumptions.md",
  ".claude/rules/adversarial-default.md",
  ".claude/rules/anti-ai-prose.md",
  ".claude/rules/destructive-actions.md",
  ".claude/rules/single-source-of-truth.md",
  ".claude/rules/decision-log.md",
  ".claude/rules/todo-tracking.md",
  ".claude/rules/logging.md",
  ".claude/rules/output-length.md",
  ".claude/rules/data-version-control.md",
  ".claude/rules/figures.md",
  ".claude/rules/tables.md",
  ".claude/rules/replication-protocol.md",
  ".claude/rules/verification-protocol.md",
  ".claude/rules/working-paper-format.md",
  ".claude/rules/{r,stata,python}-code-conventions.md",
  ".claude/rules/agents.md",
  ".claude/rules/meta-governance.md",
  ".claude/rules/revision.md",
  ".claude/skills/{commit,compile,humanize,write,context-status,learn,validate-bib,journal,deploy,sync-status,propagate,list-consumers,archive-stale}/SKILL.md",
  ".claude/skills/tools/propagate.py",
  ".claude/skills/{challenge,revise,talk}/SKILL.md",
  ".claude/file-classes.toml",
  "templates/*",
]

# CLASS B — Overlay-customized: exists on all branches (or main + overlay), 
# but content differs per branch. Source-of-truth is the overlay where the consumer lives.
[overlay-customized]
patterns = [
  "CLAUDE.md",
  "TODO.md",                                # see note below — may move to "exclude"
  ".claude/agents/orchestrator.md",
  ".claude/agents/verifier.md",
  ".claude/agents/writer.md",
  ".claude/skills/analyze/SKILL.md",
  ".claude/skills/discover/SKILL.md",
  ".claude/skills/new-project/SKILL.md",
  ".claude/skills/review/SKILL.md",
  ".claude/skills/submit/SKILL.md",
  ".claude/skills/tools/SKILL.md",
  ".claude/rules/quality.md",
  ".claude/rules/workflow.md",
  "master_supporting_docs/literature/papers/README.md",
]

# CLASS C — Overlay-only: file exists on exactly one overlay branch.
# `branches` lists the overlay(s) where the file lives.
[[overlay-only]]
pattern = ".claude/agents/{designer,theorist,theorist-critic,otree-specialist,qualtrics-specialist}.md"
branches = ["behavioral"]

[[overlay-only]]
pattern = ".claude/references/{domain-profile-behavioral,inference-first-checklist,qualtrics-patterns,seminal-papers-by-subfield}.md"
branches = ["behavioral"]

[[overlay-only]]
pattern = ".claude/rules/experiment-design-principles.md"
branches = ["behavioral"]

[[overlay-only]]
pattern = ".claude/skills/{design,otree,preregister,qualtrics,theory}/SKILL.md"
branches = ["behavioral"]

[[overlay-only]]
pattern = ".claude/agents/{strategist,strategist-critic}.md"
branches = ["applied-micro"]

[[overlay-only]]
pattern = ".claude/references/{domain-profile-applied-micro,identification-checklists,journal-profiles-applied-micro}.md"
branches = ["applied-micro"]

[[overlay-only]]
pattern = ".claude/rules/air-gapped-workflow.md"
branches = ["applied-micro"]

[[overlay-only]]
pattern = ".claude/skills/{balance,event-study,strategize}/SKILL.md"
branches = ["applied-micro"]

# CLASS D — Excluded from propagation entirely.
# Files that exist in the workflow but should NEVER propagate (per-instance content).
[exclude]
patterns = [
  "quality_reports/**",                     # session logs, plans, reviews — workflow-source-only
  "decisions/**",                           # ADRs are project-specific
  "master_supporting_docs/literature/papers/**.pdf",  # papers are project-specific
  ".claude/state/**",                       # gitignored anyway; defensive belt-and-suspenders
  ".git/**",
  ".dvc/**",
  "data/**",
  "scripts/**",                             # consumers have their own scripts
  "paper/**",
  "talks/**",
  "figures/**",
  "tables/**",
  "explorations/**",
  "replication/**",
  "preambles/**",
  "MEMORY.md",
  "SESSION_REPORT.md",
]
```

### 3.3 Class precedence rules

When a path matches multiple sections (a glob in `[universal]` plus a specific entry in `[overlay-customized]`), the more-specific section wins:

1. `[exclude]` — highest priority. If a path matches here, propagation skips it entirely.
2. `[overlay-only]` — if path matches here, treat as Class C.
3. `[overlay-customized]` — if path matches here, treat as Class B.
4. `[universal]` — if path matches here OR doesn't match any other section, treat as Class A.

Example: `.claude/skills/tools/SKILL.md` matches both `[universal]` (via the broad skills glob in §3.2 — note: the actual manifest above does NOT include this in the universal glob, intentionally) and `[overlay-customized]` (explicit). Class B wins. → propagate reads from consumer's overlay.

### 3.4 Validation rules

`propagate.py` validates the manifest at load time:

- TOML parses without error.
- Every pattern under `[overlay-only]` has `branches` ⊆ `{applied-micro, behavioral}`.
- No path is listed in two non-exclude sections (single classification per file).
- (Optional, for v2) Every Class A pattern resolves to at least one file on `main`. Every Class B pattern resolves on at least one branch. Every Class C pattern resolves on each declared overlay.

### 3.5 TODO.md special case

`TODO.md` is technically Class B (each branch has its own task list), but it's also project-state-of-the-workflow that *probably shouldn't propagate to consumer projects at all* (consumers have their own TODOs). Two options:

- **(A)** Treat as Class B. Propagate reads from consumer's overlay → overwrites consumer's TODO with workflow's. This is wrong.
- **(B)** Add to `[exclude]`. Workflow's TODOs stay workflow-internal; consumers maintain their own.

**Recommendation: (B).** Same reasoning applies to `SESSION_REPORT.md`, `MEMORY.md`, `quality_reports/**`, `decisions/**` — workflow project state is not consumer project state.

The manifest above already lists these under `[exclude]`. Class B section keeps `TODO.md` listed for transparency; we'll move it to `[exclude]` once user confirms.

---

## 4. Modified routing in `propagate.py`

The current `propagate.py` reads from `<consumer-overlay>:<path>` for every file. Change: classify each file first, then route per class.

### 4.1 New routing logic (pseudocode)

```python
def resolve_source_branch(file_path: str, consumer_overlay: str, manifest: Manifest) -> str | None:
    """Return the branch to read this file from, or None if file should be skipped."""
    if manifest.is_excluded(file_path):
        return None
    if manifest.is_overlay_only(file_path):
        branches = manifest.overlay_only_branches(file_path)
        if consumer_overlay not in branches:
            return None  # consumer is on a different overlay; file doesn't apply
        return consumer_overlay
    if manifest.is_overlay_customized(file_path):
        return consumer_overlay
    # Default: Universal (Class A)
    return "main"
```

### 4.2 New CLI behavior

`/tools propagate <pattern>...` resolves patterns to file paths in `main`'s working tree (since main is the canonical source for Class A and the place where the manifest lives), then for each (file, consumer) pair calls `resolve_source_branch`. Output now reports the source branch per file:

```
[BDD (behavioral)]
  ✓ .claude/hooks/context-monitor.py             ← main           [universal]
  ✓ .claude/rules/data-version-control.md        ← main           [universal]
  ✓ .claude/agents/orchestrator.md               ← behavioral     [overlay-customized]
  ✓ .claude/agents/designer.md                   ← behavioral     [overlay-only]
  − .claude/agents/strategist.md                 (skipped)        [overlay-only on applied-micro]
  − quality_reports/plans/...                    (skipped)        [excluded]
```

### 4.3 Manifest discovery

`propagate.py` reads the manifest from `git show main:.claude/file-classes.toml` (NOT the working tree — ensures the canonical version, even if the operator is currently on an overlay worktree). Validates per §3.4 before proceeding. If the manifest is missing or invalid, exit with a clear error.

### 4.4 Backward compatibility

Today's `consumers.toml` and per-consumer `workflow-sync.json` formats are unchanged. The sync-state JSON gains an optional `class` field per file that records the source branch + class at sync time:

```json
{
  ".claude/rules/data-version-control.md": {
    "source_branch": "main",
    "class": "universal",
    "source_sha256": "...",
    "consumer_sha256_at_sync": "..."
  }
}
```

This lets a future propagate run detect a class change (e.g., a file moved from Class A to Class B) and treat it as a divergence requiring user attention.

### 4.5 Patch size estimate

`propagate.py` is currently 433 lines. Adding manifest parsing (~50 lines), `resolve_source_branch` (~20 lines), report formatting changes (~30 lines), and validation (~20 lines) = ~120 new lines, ~30 modified. Roughly 550 lines total. Still well under any complexity bound that warrants a refactor.

---

## 5. New skill: `/tools sync-overlays`

### 5.1 Purpose

Periodically push Class A (Universal) updates from `main` to `applied-micro` and `behavioral`. This catches up overlay branches on shared infrastructure without touching Class B/C content.

### 5.2 Why this is separate from propagate

- **Different operation:** propagate is workflow-source → consumer-repo (cross-repo, configurable list). sync-overlays is intra-workflow, between branches of the same repo (cross-branch, fixed set).
- **Different state:** propagate maintains per-consumer JSON state. sync-overlays operates on git refs directly; no separate state file.
- **Different invocation cadence:** propagate fires on every workflow change. sync-overlays fires periodically (weekly?) or on demand before propagating.

### 5.3 Algorithm

```
1. Load manifest from main.
2. List all Class A paths that exist on main and have content.
3. For each overlay (applied-micro, behavioral):
   a. cd into that overlay's worktree.
   b. For each Class A path:
      - Compute sha256(main:path) and sha256(overlay:path).
      - If overlay path missing OR sha differs:
        Copy the main version into the overlay's working tree.
        git add <path>
   c. If any files were staged:
      Commit with message: "sync(overlays): pull universal-class updates from main @ <sha>"
4. Print summary: per-overlay (files updated, new files added).
```

### 5.4 What this does NOT do

- **Does not touch Class B files.** Even if `main`'s `CLAUDE.md` has a fix to a universal section, sync-overlays leaves overlay CLAUDE.md alone. Class B updates require manual editing of each overlay's version.
- **Does not delete files removed from main.** A file removed from main but still on the overlay is left as-is and reported in the summary (user reviews).
- **Does not push or merge git branches.** sync-overlays only writes to overlay worktrees and commits there. The user pushes to remote separately via normal git workflow.
- **Does not run on consumers.** Consumers receive Class A updates via `propagate`. sync-overlays is workflow-source-only.

### 5.5 Worktree assumption

sync-overlays expects worktrees for `applied-micro` and `behavioral` to exist alongside the main worktree. Standard layout:

```
~/github_repos/claude-code-my-workflow                     (main)
~/github_repos/claude-code-my-workflow-applied-micro       (applied-micro worktree)
~/github_repos/claude-code-my-workflow-behavioral          (behavioral worktree)
```

This is the user's existing setup. If a worktree is missing, sync-overlays prints setup instructions:

```
git worktree add ../claude-code-my-workflow-applied-micro applied-micro
```

### 5.6 SKILL.md sketch

```markdown
---
name: sync-overlays
description: Pull Class A (Universal) file updates from main to overlay branches.
allowed-tools: Read,Bash,Write
---

# /tools sync-overlays

Sync Universal-class files from main to applied-micro and behavioral overlay
worktrees. Skips Overlay-customized and Overlay-only files (those live on the
overlay).

Step 1: identity check — must run from the workflow source repo (has 
`.claude/file-classes.toml` in main's tree).

Step 2: invoke — `python3 .claude/skills/tools/sync_overlays.py [--dry-run]`.

Step 3: review per-overlay summary; commit per overlay; manually `git push` 
each overlay branch when ready.
```

---

## 6. One-time bootstrap

### 6.1 Phase 1 — Audit and propose manifest (30-60 min)

A bootstrap script `bootstrap_manifest.py` (write once, throw away) reads every tracked path on each branch and proposes a classification:

- File exists on main only → propose Class A (universal) if it's clearly infrastructure, else flag.
- File exists on all 3 branches with identical content → propose Class A.
- File exists on all 3 branches with different content → propose Class B.
- File exists on overlay only → propose Class C.
- File exists on main + one overlay → flag for human review.

Output: a draft `.claude/file-classes.toml` with comments per file explaining the classification, written to `quality_reports/plans/2026-05-07_proposed-manifest.toml`. Christina reviews, edits as needed, approves.

### 6.2 Phase 2 — Commit the manifest (10 min)

Once approved, commit `.claude/file-classes.toml` to `main`. This is itself a Class A file, so it'll propagate to overlays in Phase 3.

### 6.3 Phase 3 — Initial overlay sync (15-30 min)

Run `/tools sync-overlays` for the first time. Each overlay receives:

- All Class A files added since the overlay last sync'd from main.
- Updated Class A files where main has a newer version than the overlay.

Commit per overlay; review the diffs.

Expected scale (rough estimate from today's diff stat):
- Behavioral receives ~25-30 Class A updates (hooks, rules, templates added on main since the last manual sync).
- Applied-micro similar.

### 6.4 Phase 4 — Initial consumer propagation (15 min)

Run `/tools propagate '.claude/**' 'templates/**' '.gitignore' 'LICENSE'` (or equivalent broad pattern) `--force-initial` to populate every consumer's `workflow-sync.json` with the current state of every tracked path.

Per consumer, this should produce one commit catching the consumer up on:

- Universal-class files that the consumer was missing (data-version-control.md, propagate.py, etc.).
- Class B files where the overlay version is newer than the consumer's version (rare — usually the consumer matches because the overlay matches).
- Class C files for the consumer's overlay.

Consumers on `main` (csac, csac2025) get only Class A. Behavioral consumers (BDD, BDD-audit, bdm_bic) get A + B + C-from-behavioral. Applied-micro consumers (tx_peer_effects_local, va_consolidated) get A + B + C-from-applied-micro.

### 6.5 Phase 5 — Tag and document (10 min)

Tag the workflow-source state: `git tag bootstrap-2026-05-NN`. Update CLAUDE.md (Class B — edit on each branch) with a note about the new propagation infrastructure. Close out the related TODO entries.

Total bootstrap effort: ~1-2 hours, mostly user review of the manifest.

---

## 7. Edge cases

### 7.1 A file changes class after bootstrap

Scenario: `quality.md` is initially Class A. Later, the behavioral overlay starts diverging on weight assignments (overlay-specific deductions). User wants to promote it to Class B.

Process:
1. Edit the manifest on main: move `quality.md` from `[universal]` to `[overlay-customized]`. Commit.
2. Run `/tools sync-overlays` — won't touch `quality.md` anymore (now Class B).
3. Edit each overlay's `quality.md` to its desired customized form. Commit per overlay.
4. Run `/tools propagate .claude/rules/quality.md` — consumers now receive their overlay's version.

The `class` field in `workflow-sync.json` lets propagate detect the class transition and warn if a consumer's previous sync was from a different branch.

### 7.2 New universal file added to workflow

Scenario: a new hook `.claude/hooks/foo.py` is added on main. By default (Class A by virtue of being unlisted), it auto-classifies as universal. User runs:

1. `git add .claude/hooks/foo.py && git commit && git push` — file lands on main.
2. `/tools sync-overlays` — file copies to applied-micro and behavioral worktrees, commits per overlay.
3. `/tools propagate .claude/hooks/foo.py` — file lands on every consumer.

No manifest edit needed for unambiguous Class A files. The default-to-Universal rule pays off here.

### 7.3 Skill SKILL.md with both universal and overlay-flavored subcommands

`.claude/skills/tools/SKILL.md` is the canonical example. It documents `/tools propagate` (universal — fresh, identical on every branch) AND `/tools commit`, `/tools compile` (which may differ slightly per overlay if e.g. compile flags differ).

Resolution options:
- **(A) Treat the whole file as Class B.** Each overlay maintains its own tools/SKILL.md. Loss: universal-portion edits (like adding `propagate` documentation) require manual edit on each branch.
- **(B) Decompose into per-subcommand files.** `tools/SKILL.md` becomes a thin shell that includes `subcommands/{commit,compile,propagate,...}.md`. Each sub-file is independently classified. Win: granular classification. Loss: bigger refactor; not all skill systems support includes.
- **(C) Treat as Class A, accept that overlay-specific tweaks happen rarely enough to maintain via PR-like workflow.** Wins on simplicity. Loses if overlays genuinely need different commit/compile behavior.

**Recommendation: (A)** for v1. Accept the maintenance cost. Revisit decomposition if it becomes painful.

### 7.4 Consumer's overlay branch is stale

Scenario: consumer is on `behavioral`, but the consumer hasn't pulled overlay updates in a while. Their version of an overlay-customized file is older than what's on the workflow's `behavioral` branch.

Today: propagate reads from workflow's `behavioral`, copies to consumer, commits. Consumer is now caught up.

Edge case: if the consumer has *modified* their copy locally (divergence detected via `consumer_sha256_at_sync` mismatch), propagate skips with warning. User reconciles manually. No change from current behavior.

### 7.5 Overlay branch has a Class A file modified directly (out-of-band edit)

Scenario: someone (Christina, in a hurry) edits `data-version-control.md` directly on the `behavioral` worktree without touching main.

Detection: next `/tools sync-overlays` run sees `behavioral`'s `data-version-control.md` differs from `main`'s. Behavior:

- **(A)** Overwrite (sync-overlays' default): main wins, the overlay-side edit is lost. Bad if the edit was intentional.
- **(B)** Detect-and-skip with warning: print the conflict and require user to either commit the change to main first, or move the file to Class B if the overlay-side version is intentional.

**Recommendation: (B).** Same divergence-detection philosophy as propagate. Users can override with `sync-overlays --force` to apply main wholesale.

### 7.6 Overlay branch has a file that should be Class C but isn't in the manifest

Scenario: a new agent `.claude/agents/foo.md` is created on `behavioral` only. Not in manifest.

Default classification: Class A (universal — anything not listed). sync-overlays would try to copy from main → fails because main doesn't have it.

Detection: sync-overlays' Class A loop: "for each path P that exists on main, copy to overlay if needed." A file that exists on overlay but not main is invisible to that loop — no copying attempted. Safe.

But propagate would then try to read `behavioral:.claude/agents/foo.md` for behavioral consumers, find it, and treat it as Class A — reading from main would fail. The routing function should fall through gracefully:

```python
if manifest.is_universal(path):  # default, since not listed
    if path exists on main:
        return "main"
    else:
        return None  # silently skip; not a propagatable file
```

The fallback handles this case without a manifest edit. To make the file propagatable, user adds it to `[overlay-only]` with `branches = ["behavioral"]`.

### 7.7 Worktrees pinned to old commits

Scenario: applied-micro worktree's HEAD is several commits behind `applied-micro` ref. sync-overlays detects this and refuses (similar to the v1 plan's "consumer in detached-HEAD" handling): "applied-micro worktree is at commit X; the applied-micro ref is at Y. Run `git pull` in the worktree first."

### 7.8 Manifest itself is invalid

If `.claude/file-classes.toml` fails parse or validation, propagate.py and sync-overlays exit cleanly with the validation error. Until the manifest is fixed and committed, propagation is blocked. (No silent fallback to v1 behavior — fixing the manifest is the right action.)

---

## 8. Implementation phases

### Phase A — Manifest creation (this week, ~2 hours)

1. Write `bootstrap_manifest.py` (one-shot script, ~150 LOC).
2. Run it; review proposed manifest; edit; commit `.claude/file-classes.toml` on main.
3. Acceptance: manifest exists, parses, validates, classifies every tracked file.

### Phase B — Routing changes in propagate.py (~1 hour)

1. Add `Manifest` class (load + validate + lookup).
2. Add `resolve_source_branch` function.
3. Modify `propagate_one_consumer` to use `resolve_source_branch` instead of hardcoded `<consumer-overlay>`.
4. Update report formatting to show source branch + class per file.
5. Update SKILL.md.
6. Acceptance: dry-run propagation reports correct routing for at least one example per class.

### Phase C — sync-overlays skill (~1 hour)

1. Write `sync_overlays.py` (~150 LOC).
2. Add `/tools sync-overlays` to `tools/SKILL.md` (this edit happens on `main` then propagates via the new sync-overlays itself — chicken-and-egg handled in §8.1).
3. Acceptance: dry-run reports proposed copies; without --dry-run, applies and commits per overlay.

### Phase D — Bootstrap (~1 hour user time)

1. Run `/tools sync-overlays` for first time. Review per-overlay diffs and commits.
2. Run `/tools propagate '.claude/**' 'templates/**' '.gitignore' 'LICENSE' --force-initial`. Review per-consumer diffs.
3. Tag: `git tag bootstrap-2026-05-NN`.
4. Acceptance: every consumer's `workflow-sync.json` is populated; behavioral and applied-micro overlays are caught up on Class A files.

### Phase E — Documentation and TODO cleanup (~30 min)

1. Update CLAUDE.md (Class B, edit per overlay) with a reference to this plan.
2. Update INDEX.md.
3. Mark this plan Status: Active → Completed once Phase D acceptance criteria pass.
4. Close out related TODO entries.

### Total estimated effort: ~5-6 hours over 1-2 sessions.

### Phase ordering for the chicken-and-egg

Phase A (manifest on main) → Phase B (propagate.py modifications on main) → Phase C (sync-overlays.py on main).

Then Phase D-1: run sync-overlays. This propagates the manifest, the new propagate.py, and sync-overlays.py itself to applied-micro and behavioral. Now all three branches have the new infrastructure.

Then Phase D-2: run propagate. This pushes the new infrastructure to consumers.

The ordering matters: do not run propagate before sync-overlays in the bootstrap, because propagate's pre-sync routing for behavioral consumers reads `behavioral:.claude/file-classes.toml` (nonexistent until sync-overlays runs).

---

## 9. Acceptance criteria

After all phases complete:

- [ ] `.claude/file-classes.toml` exists on `main`, parses, validates.
- [ ] Manifest classifies every tracked file under one of {universal, overlay-customized, overlay-only, exclude}.
- [ ] `propagate.py` reads the manifest, routes per class, reports source branch in output.
- [ ] `sync_overlays.py` exists and applies cleanly to both overlay worktrees.
- [ ] Both overlay branches contain the new manifest, new propagate.py, and new sync_overlays.py (verified by checkout + ls).
- [ ] Each of the 7 consumer repos has an updated `workflow-sync.json` with class metadata per file.
- [ ] Re-running `/tools propagate '.claude/**' 'templates/**' --dry-run` reports zero pending changes (idempotency check).
- [ ] Re-running `/tools sync-overlays --dry-run` reports zero pending changes (idempotency check).
- [ ] Adding a new file under `.claude/hooks/` to main, then running sync-overlays + propagate, lands the file on all overlays and all 7 consumers without manual intervention.
- [ ] CLAUDE.md updated on each branch (Class B, manual edit) with a one-line pointer to this plan.

---

## 10. Open [USER] questions

1. **Approve the three-class taxonomy?** (§2) Or push for a different decomposition?
2. **Approve `.claude/file-classes.toml` as the manifest path?** (§3.1) Alternatives: `.claude/state/file-classes.toml` (gitignored — bad), or root `file-classes.toml` (less namespaced).
3. **Approve `sync-overlays` as a separate skill?** (§5) Or fold into propagate as `propagate --sync-overlays`?
4. **Approve the bootstrap classification approach** — auto-propose then human-review? (§6.1) Alternative: hand-write the manifest from scratch.
5. **Confirm the Class B examples list in §3.2.** Specifically: are `quality.md`, `workflow.md`, `master_supporting_docs/literature/papers/README.md` actually Class B (genuinely customized), or just stale-of-main (Class A with overlay versions to be overwritten)?
6. **Approve adding `TODO.md`, `SESSION_REPORT.md`, `MEMORY.md` to `[exclude]`?** (§3.5) These are workflow-source project state, should not propagate.
7. **Approve the §7.3 recommendation** for `tools/SKILL.md` (Class B, accept maintenance cost)?
8. **Approve the §7.5 recommendation** that out-of-band overlay edits to Class A files are detect-and-skip (not silent overwrite)?
9. **Confirm the worktree assumption in §5.5**: applied-micro and behavioral worktrees exist at the documented paths.
10. **Approve initial overlay sync as part of this plan's bootstrap (Phase D-1)?** Alternative: defer the initial sync to a separate session for review.

---

## 11. What changes vs. the v1 plan (2026-05-06)

| Aspect | v1 plan | This plan |
|---|---|---|
| Routing | Always read from `<consumer-overlay>:<path>` | Route per file class (universal → main; B/C → consumer overlay) |
| Manifest | None | `.claude/file-classes.toml` with three-class taxonomy + exclude |
| Overlay sync | Deferred to v1.1 helper | First-class skill `/tools sync-overlays` |
| Class metadata in sync state | Not present | `class` and `source_branch` fields added per file |
| Bootstrap | Set up consumers.toml + first-run populate | Audit + manifest + initial overlay sync + initial propagation |
| Edge cases handled | 9 (consumer state, divergence, etc.) | 9 + 8 new (class transitions, manifest validity, worktree state, etc.) |
| LOC for propagate.py | 433 | ~550 (manifest parsing + routing) |
| New scripts | propagate.py | + sync_overlays.py + bootstrap_manifest.py (throwaway) |

The v1 propagate.py implementation is **not discarded**. The `consumers.toml`, `workflow-sync.json`, identity-detection trinary, divergence-skip policy, and commit format are all preserved. This plan adds a routing layer on top.

---

## 12. Cross-references

- `2026-05-06_tools-propagate-plan.md` — v1 plan; this extends it.
- `.claude/state/consumers.toml` — registry of 7 consumers (existing).
- `.claude/skills/tools/propagate.py` — implementation to be modified per Phase B.
- `.claude/skills/tools/SKILL.md` — to be updated with `/tools sync-overlays` subcommand documentation.
- `quality_reports/session_logs/2026-05-05_workflow-storage-rethink-and-macdown-rule.md` (Day 2 evening section) — origin of the cherry-pick conflict that motivated this plan.
- `.claude/rules/meta-governance.md` — public-template-vs-working-project distinction; this plan respects the boundary by excluding all `quality_reports/`, `decisions/`, `data/`, etc. from propagation.
- `.claude/rules/destructive-actions.md` — sync-overlays touches multiple branches; the per-overlay commit (no force-push, no rebase) keeps it within the safe-action envelope.

---

## Appendix A — Concrete classification examples for review

To make §3.2 less abstract, here are spot-checks against today's branch state:

**Definitely Class A (Universal)** — tested or near-certain:

- `.claude/hooks/context-monitor.py` — recently propagated to all 7 consumers; identical content the goal.
- `.claude/hooks/destructive-action-guard.py` — universal infrastructure.
- `.claude/rules/data-version-control.md` — created on main 2026-05-05; should land everywhere.
- `templates/data-MANIFEST.md`, `templates/data-PROVENANCE.md`, `templates/data-CHANGELOG.md` — universal data-doc contract.
- `templates/gitattributes-lfs.txt`, `templates/setup-machine.sh` — LFS-related, universal.
- `.claude/skills/tools/propagate.py` — universal infrastructure.
- `.claude/state/.gitkeep`, `.gitignore`, `LICENSE` — repo plumbing.

**Definitely Class B (Overlay-customized)** — confirmed by today's diff inspection:

- `.claude/agents/orchestrator.md` — behavioral has experimental pipeline section.
- `.claude/skills/analyze/SKILL.md` — behavioral defaults to Stata 17, references behavioral domain-profile.

**Likely Class B but worth user confirmation:**

- `CLAUDE.md` — overlay-specific Skills Quick Reference rows, but ~80% of content is universal.
- `.claude/agents/verifier.md`, `.claude/agents/writer.md` — small diffs observed; user may prefer to flatten back to Class A.
- `.claude/rules/quality.md`, `.claude/rules/workflow.md` — diffs observed; user may prefer to flatten.
- `.claude/skills/{discover,new-project,review,submit}/SKILL.md` — overlay flavor.

**Definitely Class C (Overlay-only)** — files exist on exactly one overlay:

- `.claude/agents/{designer,theorist,theorist-critic,otree-specialist,qualtrics-specialist}.md` — behavioral.
- `.claude/agents/{strategist,strategist-critic}.md` — applied-micro.
- `.claude/skills/{design,otree,preregister,qualtrics,theory}/SKILL.md` — behavioral.
- `.claude/skills/{balance,event-study,strategize}/SKILL.md` — applied-micro.
- `.claude/references/domain-profile-{behavioral,applied-micro}.md` — overlay-specific.
- `.claude/rules/experiment-design-principles.md` — behavioral.
- `.claude/rules/air-gapped-workflow.md` — applied-micro.

A "flatten back to Class A" decision for the items in the "likely Class B" bucket would mean: edit the overlay versions to match main, then remove from Class B, treat as Class A going forward. Worth considering for files where overlay-side customization is small enough to not be worth the maintenance overhead.

---

## Appendix B — What `/tools propagate` looks like after this plan lands

Example session: user adds a new universal hook on main, then runs propagate.

```
$ ls .claude/hooks/new-hook.py
.claude/hooks/new-hook.py  # newly created

$ git add .claude/hooks/new-hook.py
$ git commit -m "hooks: new-hook.py — universal validation"

$ /tools sync-overlays
[main → applied-micro]
  + .claude/hooks/new-hook.py                    [universal]
  Committed: sync(overlays): pull universal-class updates from main @ 1abc234

[main → behavioral]
  + .claude/hooks/new-hook.py                    [universal]
  Committed: sync(overlays): pull universal-class updates from main @ 1abc234

$ /tools propagate .claude/hooks/new-hook.py
[BDD (behavioral)]                                ← behavioral
  ✓ .claude/hooks/new-hook.py                    ← main           [universal]
  Committed: chore(workflow-sync): propagate updates from claude-code-my-workflow

[BDD-audit (behavioral)]
  ✓ .claude/hooks/new-hook.py                    ← main           [universal]
  Committed.

[bdm_bic (behavioral)]
  ✓ .claude/hooks/new-hook.py                    ← main           [universal]
  Committed.

[csac (main)]
  ✓ .claude/hooks/new-hook.py                    ← main           [universal]
  Committed.

[csac2025 (main)]
  ✓ .claude/hooks/new-hook.py                    ← main           [universal]
  Committed.

[tx_peer_effects_local (applied-micro)]
  ✓ .claude/hooks/new-hook.py                    ← main           [universal]
  Committed.

[va_consolidated (applied-micro)]
  ✓ .claude/hooks/new-hook.py                    ← main           [universal]
  Committed.

Total: 7 consumers updated, 7 commits made. Workflow source: 1abc234.
```

The Class A routing means the consumer's overlay doesn't matter for this file — they all read from main. This is the v1 gap that today's propagate hits, fixed.
