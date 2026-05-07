# `/tools propagate` — Detailed Plan

**Date:** 2026-05-06
**Status:** Active (DRAFT — pending user approval before implementation)
**Supersedes:** —
**Authors:** Christina + Claude

A workflow-feature-propagation skill that synchronizes selected files (hooks, rules, skills, templates, etc.) from `claude-code-my-workflow` to its consumer repos. Solves the general "feature propagation" problem the user surfaced after today's manual hook-sync — keeps repos in sync without per-update copy-paste loops.

---

## 0. Decisions locked in this plan

| # | Decision | Resolved value |
|---|---|---|
| D1 | Registry format | TOML (`.claude/state/consumers.toml` in workflow source repo) |
| D2 | Registry visibility | Gitignored (under `.claude/state/*` rule). Skill propagates; registry stays local. |
| D3 | Per-consumer sync state | Decentralized — each consumer has `.claude/state/workflow-sync.json` recording its last_synced_commit + last_synced_branch + checksum-by-file. |
| D4 | Overlay-branch handling | `git show <branch>:<path>` from workflow's git data. No branch switching, no worktree dependency. |
| D5 | Local-divergence policy | Detect-and-skip with warning, NOT silent overwrite. Preserves consumer customizations. |
| D6 | Identity detection | Three modes: source (has consumers.toml), consumer (has workflow-sync.json), neither. Skill behavior differs per mode. |
| D7 | Implementation language | Python helper at `.claude/skills/tools/propagate.py`. SKILL.md prose documents invocation. Python because: TOML parsing, JSON state, structured logic, predictable behavior across Claude sessions. |
| D8 | Commit policy | One commit per consumer with traceable source-commit reference. |

---

## 1. Goals and non-goals

### Goals

1. **One-command propagation** — `/tools propagate <pattern>...` updates all consumer repos with workflow changes matching the pattern.
2. **Overlay-aware** — picks the right branch's version when consumers are on `applied-micro` or `behavioral` overlays.
3. **Safe by default** — never silently overwrite local consumer modifications; surface conflicts for manual resolution.
4. **Auditable** — each propagation produces a structured commit in each consumer linking back to the source workflow commit.
5. **Fork-safe** — a fresh fork of the workflow doesn't accidentally try to propagate (no consumers list = no-op).
6. **Lightweight** — no database, no daemon. File-based state. Manual invocation by user.

### Non-goals (deferred to future versions)

- **Bidirectional sync** — consumers don't push back to the workflow.
- **Auto-trigger on workflow commits** — explicit invocation only.
- **Three-way merge** of divergent consumer files. We detect divergence and stop; user resolves manually.
- **GUI** — this is a CLI/Claude-skill thing.
- **Cross-machine registry sync** — `consumers.toml` is per-machine. If you propagate from multiple machines, maintain `consumers.toml` on each (or symlink it from a synced location like `claude-config`).

---

## 2. Architecture

### 2.1 Two repo identities

| Identity | Indicator | Behavior |
|---|---|---|
| **Workflow source** | `.claude/state/consumers.toml` exists | `/tools propagate` runs the propagation |
| **Consumer** | `.claude/state/workflow-sync.json` exists | `/tools propagate` exits with: "this is a consumer; run from the source repo. Your last sync: <commit> on <branch>." |
| **Neither** | Both absent | `/tools propagate` exits with: "no propagation context. To make this a source, create consumers.toml. To make this a consumer, run propagate from a source repo." |

A repo never has both. A workflow source's `.claude/state/` has `consumers.toml`; that source is itself NOT in its own consumer list (you can't propagate to yourself). A consumer's `.claude/state/` has `workflow-sync.json`; consumers don't have a `consumers.toml` of their own.

### 2.2 Registry: `consumers.toml` (workflow-source only, gitignored)

```toml
# .claude/state/consumers.toml — Christina's consumer registry. Gitignored.
# Edit by hand to add/remove projects.

[[consumer]]
path = "~/github_repos/belief_distortion_discrimination"
overlay = "behavioral"
note = "JMP project; behavioral overlay"

[[consumer]]
path = "~/github_repos/belief_distortion_discrimination_audit"
overlay = "behavioral"

[[consumer]]
path = "~/github_repos/tx_peer_effects_local"
overlay = "applied-micro"
note = "TX peer effects analysis repo. (Note: ~/github_repos/tx_peer_effects_paper is the Overleaf-sync paper/slides repo and has no .claude/ — not a workflow consumer; do not add it.)"

[[consumer]]
path = "~/github_repos/csac"
overlay = "main"

[[consumer]]
path = "~/github_repos/csac2025"
overlay = "main"

[[consumer]]
path = "~/github_repos/bdm_bic"
overlay = "behavioral"

[[consumer]]
path = "~/github_repos/va_consolidated"
overlay = "applied-micro"
```

Fields per consumer:

- `path` (required) — absolute or `~`-prefixed path to the consumer repo on the local machine.
- `overlay` (required) — one of `main`, `applied-micro`, `behavioral`. Determines which workflow branch to read files from.
- `note` (optional) — free-text description.

Validation at parse time:

- Path must exist and be a git repo (`<path>/.git` exists).
- Overlay must be one of the three valid values.
- No duplicate paths.

### 2.3 Per-consumer state: `workflow-sync.json` (in each consumer, gitignored)

```json
{
  "source_repo": "/Users/christinasun/github_repos/claude-code-my-workflow",
  "overlay": "behavioral",
  "last_synced_commit": "ad6c547",
  "last_synced_at": "2026-05-06T22:15:00-07:00",
  "synced_files": {
    ".claude/hooks/context-monitor.py": {
      "source_sha256": "<hash>",
      "consumer_sha256_at_sync": "<hash>"
    },
    ".claude/rules/data-version-control.md": {
      "source_sha256": "<hash>",
      "consumer_sha256_at_sync": "<hash>"
    }
  }
}
```

`source_sha256` = workflow's file content hash at sync time. Used on next sync to detect "did the workflow file change since I last synced this consumer?"

`consumer_sha256_at_sync` = consumer's file content hash IMMEDIATELY AFTER the sync wrote it. Used to detect "has the consumer modified this file locally since the sync wrote it?" — if yes → divergence, skip and warn (per D5).

This is the heart of the divergence-detection logic. Lightweight, fast, no git history needed.

### 2.4 File classes

The skill propagates by file path. Some categories that come up in practice:

| Class | Example paths | Overlay-sensitive? |
|---|---|---|
| Hooks | `.claude/hooks/*.py` | No (universal across overlays) |
| Universal rules | `.claude/rules/{verification-protocol, primary-source-first, ...}.md` | No |
| Overlay-specific rules | `.claude/rules/applied-micro-conventions.md` | Yes |
| Skills (universal) | `.claude/skills/{commit, compile, write, ...}` | Mostly no |
| Skills (overlay) | `.claude/skills/{strategize, design, ...}` | Yes |
| Agents | `.claude/agents/*.md` | Some yes (e.g., `strategist` only on applied-micro) |
| Templates | `templates/*.md`, `templates/*.txt` | Mostly no |
| References | `.claude/references/*.md` | Sometimes |

Overlay-sensitivity is handled by `git show <consumer-overlay>:<path>` — if the file doesn't exist on that branch, skip with a clear message.

---

## 3. Algorithm

### 3.1 Top-level entry: `/tools propagate <pattern>... [--dry-run]`

```
1. Detect identity (read .claude/state/{consumers.toml,workflow-sync.json}).
   - If neither → exit with hint.
   - If consumer → exit with "run from source" hint.
   - If source → continue.

2. Parse consumers.toml.

3. For each pattern in arguments:
   - Resolve to repo-relative file paths in the workflow's working tree.

4. For each consumer:
   a. cd to consumer path. Verify it's a git repo.
   b. Read .claude/state/workflow-sync.json (or treat as empty if absent).
   c. For each (workflow file, consumer's overlay):
      - Read workflow file content from `git show <overlay>:<path>` in the workflow's git data
        (NOT the working tree — ensures we use the overlay's version).
      - Compute source_sha256.
      - If file already exists in consumer:
         consumer_current_sha256 = sha256(consumer's file)
         If workflow-sync.json has a record for this file:
            If consumer_current_sha256 != record.consumer_sha256_at_sync:
               → DIVERGENCE. Print warning. Skip this file in this consumer.
               (User must manually reconcile.)
            Else if source_sha256 == record.source_sha256:
               → already in sync. Skip silently.
            Else:
               → workflow updated; consumer in sync with old version. SAFE TO COPY.
         Else (no record):
            If consumer_current_sha256 == source_sha256:
               → already matching. Add to records. Skip copy.
            Else:
               → consumer has SOMETHING different but no sync record. AMBIGUOUS:
               In v1: treat as divergence. Print warning. Skip.
               (User adds the file via explicit --force-initial flag if intended.)
      - Else (file doesn't exist in consumer):
         → SAFE TO CREATE. Copy.
   d. If --dry-run: print proposed actions, don't apply.
      Else: copy files, stage in git, commit, update workflow-sync.json.

5. Print aggregate summary: per-consumer (files_copied, files_skipped_divergent, files_skipped_in_sync), total commits, source commit hash referenced.
```

### 3.2 Commit message template (per consumer)

```
chore(workflow-sync): propagate updates from claude-code-my-workflow

Files updated (<N>):
- .claude/hooks/context-monitor.py
- .claude/rules/data-version-control.md
- ...

Source: claude-code-my-workflow @ <SHA-short> (<branch>)
Overlay: <consumer-overlay>
Synced via: /tools propagate

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

`<SHA-short>` is the workflow's HEAD short hash at propagation time, NOT the per-file source commits (since we use working-tree content). This ties the consumer commit to the workflow's state at propagation moment.

### 3.3 Divergence-detection examples

| Scenario | Detection | Action |
|---|---|---|
| Consumer cleanly matches last_synced state, workflow has new version | source_sha256 changed; consumer_current matches consumer_sha256_at_sync | Copy + commit + update record |
| Consumer matches workflow exactly (no change since last sync) | source_sha256 unchanged | Skip silently |
| Consumer has local modifications since last sync | consumer_current_sha256 != consumer_sha256_at_sync | Warn + skip; user reconciles manually |
| File never synced before; consumer doesn't have it | No sync record; file absent | Copy + create record |
| File never synced before; consumer has SOMETHING similar | No sync record; file present | Warn (ambiguous); skip unless `--force-initial` |
| File deleted in workflow | Source file no longer exists | Don't auto-delete in consumer; flag for user review |

### 3.4 Overlay-routing example

Workflow has three branches with potentially-different versions of the same file:

```
git show main:.claude/rules/figures.md
git show applied-micro:.claude/rules/figures.md   # may differ
git show behavioral:.claude/rules/figures.md      # may differ
```

When propagating `.claude/rules/figures.md`:

- For BDD (behavioral) → read from `behavioral:.claude/rules/figures.md`
- For tx_peer_effects_local (applied-micro) → read from `applied-micro:.claude/rules/figures.md`
- For csac (main) → read from `main:.claude/rules/figures.md`

If the path doesn't exist on the consumer's overlay branch (`git show` returns non-zero), skip with a clear message: "skipped: <path> doesn't exist on <overlay> branch."

---

## 4. Implementation

### 4.1 File layout

```
.claude/skills/tools/
├── SKILL.md                  # documents the subcommand
└── propagate.py              # the actual logic
```

`propagate.py` is a self-contained Python 3 script. Uses only stdlib (`tomllib` from 3.11, `pathlib`, `hashlib`, `subprocess`, `json`, `argparse`).

If `tomllib` not available (Python < 3.11), fall back to a hand-rolled minimal TOML parser for our format (just `[[consumer]]` + key=value lines). Avoids the `tomli` dependency.

### 4.2 `propagate.py` skeleton

```python
#!/usr/bin/env python3
"""
/tools propagate — synchronize selected files from this workflow source
repo to all configured consumer repos.

Reads:  .claude/state/consumers.toml
Writes: per consumer: copies files + commits + updates .claude/state/workflow-sync.json
"""

from __future__ import annotations
import argparse, hashlib, json, pathlib, subprocess, sys, time
try:
    import tomllib  # Python 3.11+
except ImportError:
    tomllib = None  # use fallback parser

VALID_OVERLAYS = {"main", "applied-micro", "behavioral"}

def detect_identity(repo_root: pathlib.Path) -> str:
    """Return one of: 'source', 'consumer', 'none'."""
    state = repo_root / ".claude" / "state"
    if (state / "consumers.toml").exists(): return "source"
    if (state / "workflow-sync.json").exists(): return "consumer"
    return "none"

def load_consumers(consumers_toml: pathlib.Path) -> list[dict]:
    """Parse consumers.toml. Returns list of dicts with path/overlay/note."""
    ...

def git_show_at(repo: pathlib.Path, branch: str, path: str) -> bytes | None:
    """Read file content from `branch:path` via `git show`. Returns None if absent."""
    ...

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def propagate_one_consumer(
    workflow_root: pathlib.Path,
    consumer: dict,
    file_paths: list[str],
    dry_run: bool,
    force_initial: bool,
) -> dict:
    """Propagate to a single consumer. Returns summary dict."""
    ...

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("patterns", nargs="+",
                        help="repo-relative paths or globs to propagate")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force-initial", action="store_true",
                        help="treat ambiguous (no record + present) as initial sync")
    parser.add_argument("--only", default=None,
                        help="limit to a comma-separated list of consumer paths")
    args = parser.parse_args()

    repo_root = pathlib.Path.cwd()  # or git rev-parse --show-toplevel
    identity = detect_identity(repo_root)
    if identity == "consumer":
        sys.exit("This is a consumer repo. Propagation runs from the source. ...")
    if identity == "none":
        sys.exit("No propagation context. ...")

    # Resolve patterns to file paths in workflow's working tree
    file_paths = resolve_patterns(repo_root, args.patterns)
    consumers = load_consumers(repo_root / ".claude" / "state" / "consumers.toml")
    if args.only:
        only = set(args.only.split(","))
        consumers = [c for c in consumers if c["path"] in only]

    summary = []
    for consumer in consumers:
        result = propagate_one_consumer(repo_root, consumer, file_paths,
                                        args.dry_run, args.force_initial)
        summary.append(result)

    print_summary(summary, args.dry_run)
```

### 4.3 SKILL.md addition (under existing `## Subcommands` heading)

The new section to insert in `.claude/skills/tools/SKILL.md` (rendered below in plain prose to avoid nested code-fence ambiguity):

> ### `/tools propagate <pattern>... [--dry-run] [--force-initial] [--only <paths>]` — Workflow Propagation
>
> Sync selected files from this workflow source to all configured consumer repos (listed in `.claude/state/consumers.toml`).
>
> **Step 1: identity check.** Run `python3 .claude/skills/tools/propagate.py --check-identity` first. If this repo is a consumer or has no propagation context, exit with the helpful message and stop.
>
> **Step 2: invoke.** Shell:
>
> `python3 .claude/skills/tools/propagate.py [--dry-run] [--force-initial] [--only path1,path2] -- <pattern> [<pattern>...]`
>
> Patterns are repo-relative paths or globs: `.claude/hooks/context-monitor.py`, `.claude/rules/*.md`, `templates/data-*.md`.
>
> **Step 3: review output.** Per-consumer: files copied / skipped (in-sync) / skipped (divergent). Aggregate: total commits made, source commit hash.
>
> **Step 4: handle divergent files (if any).** For each consumer where a file was skipped due to divergence, the user must manually reconcile by either: accepting the workflow version (overwrite + recommit in that consumer), keeping consumer's local version (update its workflow-sync.json record manually), or doing a three-way merge by hand.
>
> **Common patterns:** new hook on workflow → `/tools propagate .claude/hooks/<file>.py`; big rules update → `/tools propagate .claude/rules/*.md`; new skill → `/tools propagate .claude/skills/<name>/SKILL.md`; template change → `/tools propagate templates/<file>`.
>
> **Reference:** `.claude/state/consumers.toml` for the registry; per-consumer `.claude/state/workflow-sync.json` for sync state.

Plus a sub-section `### /tools list-consumers` for read-only listing — handy.

---

## 5. Edge cases

| Edge case | Handling |
|---|---|
| Consumer has uncommitted changes in any tracked file | After staging and committing, only the propagated files end up in the commit. Other working-tree changes preserved. (Use targeted `git add <path>` per file, not `git add .`.) |
| Consumer in detached-HEAD state | Refuse to propagate; print "consumer is in detached-HEAD; check out a branch first." |
| Consumer's overlay branch missing in workflow | Print error + skip; user fixes consumers.toml. |
| File doesn't exist on workflow's overlay branch | Print "skipped: <path> not on <branch>"; continue. |
| Multiple machines syncing — consumers.toml drift | Out of scope for v1. User maintains consumers.toml per machine, OR symlinks it from `claude-config` (gitignored on workflow side, tracked there). |
| Consumer is itself the workflow worktree (e.g., `claude-code-my-workflow-behavioral`) | Refuse: that's a worktree of the source, not a consumer. Detect via `git rev-parse --git-common-dir` matching source's. |
| File renamed on workflow side | Treated as delete + create. Old name stays on consumers (flagged for user review); new name is created. User cleans up. |
| Binary files (e.g., a PDF or image template) | `git show` works for binary files (returns raw bytes). Hash + write as bytes. No special handling needed. |
| Pattern matches no files in workflow | Print "no files matched <pattern>"; exit cleanly with non-zero status if no patterns matched anything across all consumers. |

---

## 6. Testing

### 6.1 Unit tests (in `propagate.py`'s `__test__` block or sibling `test_propagate.py`)

- `detect_identity` returns correct value for: source dir, consumer dir, neither.
- `load_consumers` parses valid TOML, rejects invalid (missing path / overlay; bad overlay value; nonexistent path).
- `git_show_at` correctly reads from a branch, returns None on missing path.
- `sha256_bytes` deterministic.

### 6.2 Integration tests (manual, on a sandbox)

Create temp consumer dirs, run propagate with --dry-run and without, verify:

- New file → copied + record created.
- Updated file (consumer matches old hash) → copied + record updated.
- File matching workflow exactly → skipped silently, record updated.
- File divergent (consumer modified after sync) → skipped + warning printed.
- File not on consumer's overlay → skipped + message.
- --dry-run → no files modified, no commits made.

### 6.3 Real-world smoke test (after implementation)

Use today's already-propagated `context-monitor.py` (now in 7 consumers, all matching) as a baseline:

1. Run `/tools propagate .claude/hooks/context-monitor.py --dry-run`.
2. Expected: all 7 consumers report "already in sync" (after first run populates workflow-sync.json with current hashes).

Then make a trivial workflow change (add a comment to context-monitor.py) and re-run:

1. Expected: all 7 consumers receive the change with one commit each.

---

## 7. Rollout

### 7.1 Phase 1 — Implementation (~2 hours)

1. Write `propagate.py` (~150-200 lines).
2. Update `.claude/skills/tools/SKILL.md` with `/tools propagate` and `/tools list-consumers` subcommands.
3. Run unit tests.
4. Commit on `main` branch in workflow.

### 7.2 Phase 2 — Initial setup (~10 minutes)

1. Create `.claude/state/consumers.toml` with the 7 known consumers (per registry above).
2. Run `/tools propagate .claude/hooks/context-monitor.py --dry-run` to validate the path & report.
3. Run without `--dry-run` to populate each consumer's `workflow-sync.json` with the current state.
4. Verify each consumer commit lands cleanly.

### 7.3 Phase 3 — Daily use

When the workflow updates a hook/rule/skill/template:

1. Commit the change in the workflow repo.
2. `/tools propagate <changed-path>` (or `... .claude/rules/*.md` for rule sweeps).
3. Review per-consumer summary; reconcile any divergent files.

### 7.4 Phase 4 — Overlay-branch-sync helper (deferred to v1.1)

The `applied-micro` and `behavioral` branches currently lag `main` (e.g., today's §7 work is on `main` only). A separate `/tools sync-overlays` skill would merge `main` into both overlays after a stable period. Out of scope here, but the propagate skill is designed to coexist with it (overlay branches just have their own `git show` results).

---

## 8. What this does NOT solve

- **Workflow-source bidirectional sync** — if you edit a hook on a consumer first, then want to push it back to the workflow. Not supported. Edit the workflow first, then propagate.
- **Per-machine registry sync** — if you propagate from two laptops, you have to maintain `consumers.toml` on each. Could symlink from `claude-config` if needed, separately.
- **Automatic propagation on workflow commit** — explicit invocation only. A future post-commit hook could auto-trigger, but the current design requires intent (since propagation modifies multiple repos).
- **GUI / dashboard** — text output only.
- **Granular consumer-side opt-out per file** — could add `[[consumer.exclude]]` in TOML in v1.1; for v1 you handle by using `--only` or by manually reconciling divergent files.

---

## 9. Open questions for user approval **[USER]**

1. **Approve the architecture in §2?** Specifically: TOML registry, JSON per-consumer state, gitignored both, identity-detection trinary.
2. **Approve the divergence-skip policy?** Detect divergent local edits and skip + warn (per D5). Alternative was silent overwrite.
3. **Approve `propagate.py` as separate Python script** vs putting all logic in SKILL.md prose? Plan recommends Python helper for predictability.
4. **Initial consumer list**: the 7 currently identified — confirm or amend before Phase 2 setup.
5. **Add `/tools list-consumers`** as a sibling read-only subcommand? Useful for quick inspection.

---

## 10. Acceptance criteria

After Phase 2 setup:

- [ ] `consumers.toml` exists in workflow with 7 entries
- [ ] Each consumer has `.claude/state/workflow-sync.json` populated
- [ ] Running `/tools propagate <file> --dry-run` from workflow reports all consumers correctly
- [ ] Running `/tools propagate <file>` makes one commit per affected consumer
- [ ] Running `/tools propagate <file>` from a consumer (or a fresh fork) exits cleanly with the right hint
- [ ] `propagate.py` is <300 lines, uses only stdlib, runs in <2 seconds for 7 consumers + 1 file each
- [ ] Unit tests pass
- [ ] SKILL.md updated with the new subcommand documentation

---

## Cross-references

- **Today's manual sync** (the impetus): hook propagation across 7 repos in commits `edda972`/`82619c7`/`873de29`/`3aae0af`/`528d77d`/`2210cd0`/`173404e` (one per consumer) plus source `ad6c547` in workflow.
- `.claude/rules/meta-governance.md` — the public-template-vs-working-project distinction this design respects.
- `.claude/rules/destructive-actions.md` — propagation modifies many repos; not destructive but worth being mindful (per-file `git add`, not `git add .`; no force-pushes).
- `.claude/rules/no-assumptions.md` — `consumers.toml` is hand-maintained because the workflow can't know which repos count as "consumers" without explicit user declaration.
