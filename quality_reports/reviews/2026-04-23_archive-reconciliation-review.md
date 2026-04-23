# Archive Reconciliation Review — Applied-Micro Claudeflow

**Date:** 2026-04-23
**Scope:** `.claude/agents/archive/`, `.claude/skills/archive/`, `.claude/rules/archive/` on the `applied-micro` branch
**Context:** User reports archived items "sometimes get randomly activated and become wildcards."

---

## Activation risk — confirmed

Claude Code's discovery mechanisms:

- **Agents** — every `.md` file under `.claude/agents/**` is loaded as a subagent. **No disable flag exists.** All 16 archived agents are currently available for dispatch.
- **Skills** — Claude Code scans `.claude/skills/**/SKILL.md`. Skills with `disable-model-invocation: true` in frontmatter are hidden from model-triggered invocation but may still be visible as `/command` entries.
- **Rules** — `.md` files under `.claude/rules/` are not auto-loaded, but subagents and skills that read rules (e.g., via "see `rules/X.md`" pointers) will find archived copies if they're searched by name.

**Of 35 archived skills: 12 lack `disable-model-invocation` and can be invoked by the model.** These are the wildcards:

```
compile-latex, context-status, extract-tikz, journal, learn,
pedagogy-review, proofread, qa-quarto, review-r, slide-excellence,
translate-to-quarto, validate-bib, visual-audit
```

7 of these have active same-named replacements whose content differs (`commit`, `compile-latex`, `context-status`, `extract-tikz`, `learn`, `submit`, `validate-bib`). If the archived version fires instead of the active one, behavior silently diverges.

## Inventory

| Kind | Active | Archived | Discoverable |
|---|---:|---:|---:|
| Agents | 18 | 16 | 16 (no flag mechanism) |
| Skills | 20 | 35 | 12 wildcards + up to 23 as `/commands` |
| Rules | 18 | 29 | ~0 (passive, only found via name lookup) |
| **Total archived files** | | **80** | |

## Content analysis

### Agents (16 archived)

Most are clearly superseded by consolidation:

- **Superseded by specialist consolidation:**
  - `referee`, `domain-reviewer`, `editor` → `domain-referee` + `methods-referee` + `orchestrator` synthesis
  - `econometrician` → merged into `strategist-critic` + `methods-referee`
  - `discussant` → rolled into `storyteller-critic`
  - `proofreader` → rolled into `writer-critic`
  - `slide-auditor` → `storyteller-critic`
  - `quarto-critic`, `quarto-fixer`, `beamer-translator` → Beamer-only workflow; Quarto dropped
  - `pedagogy-reviewer`, `surveyor` → out-of-scope (lecture/survey work not part of research workflow)
  - `r-reviewer` → merged into `coder-critic`
  - `debugger` → merged into `coder-critic`
  - `replication-auditor` → merged into `verifier` (submission mode)
- **Exact duplicate:** `tikz-reviewer` (byte-identical to active version).

**No clear "absorb good features" candidates.** Consolidation already happened; archived versions are prior generations.

### Skills (35 archived)

- **Superseded by explicit consolidation (named in CLAUDE.md):**
  - `/discover` replaces: `interview-me`, `lit-review`, `find-data`, `research-ideation`
  - `/review` replaces: `paper-excellence`, `proofread`, `econometrics-check`, `review-r`, `review-paper`, `pedagogy-review`, `qa-quarto`, `visual-audit`
  - `/strategize` replaces: `identify`, `pre-analysis-plan`
  - `/analyze` replaces: `data-analysis`
  - `/talk` replaces: `create-talk`, `create-lecture`, `slide-excellence`
  - `/submit` replaces: `target-journal`, `audit-replication`, `data-deposit`
  - `/challenge` replaces: `devils-advocate`
  - `/write` replaces: `draft-paper`, `humanizer`
  - `/revise` replaces: `respond-to-referee`
  - `/tools` replaces: `commit`, `compile-latex`, `context-status`, `extract-tikz`, `learn`, `journal`, `deploy`, `validate-bib`
- **Quarto-specific (dropped workflow):** `translate-to-quarto`, `qa-quarto`

**No clear "absorb" candidates.** The consolidation is the intended surface. Archived versions are the prior surface.

### Rules (29 archived)

Grouped by disposition:

- **Absorbed into current consolidated rules (content preserved, just restructured):**
  - `adversarial-pairing`, `separation-of-powers`, `three-strikes` → `agents.md`
  - `scoring-protocol`, `severity-gradient`, `quality-gates` → `quality.md`
  - `plan-first-workflow`, `orchestrator-protocol`, `standalone-access`, `dependency-graph`, `orchestrator-research` → `workflow.md`
  - `session-logging`, `session-reporting`, `research-journal` → `logging.md`
  - `revision-protocol` → `revision.md`
- **Dropped workflow (Quarto / lecture / R-primary):**
  - `beamer-quarto-sync`, `no-pause-beamer`, `r-code-conventions`
- **Specialist rules never re-adopted (may contain absorbable content):**
  - `figure-generator-rule`, `table-generator` — possibly still useful; check against current `figures.md` and `tables.md`
  - `tikz-visual-quality` — differs from active; worth a diff
  - `pdf-processing` — workflow for chunked PDF reading; now partially replaced by `pdf-learnings` skill
  - `proofreading-protocol` — proofreader workflow; subsumed by `writer-critic`
  - `knowledge-base-template`, `single-source-of-truth` — may have been folded into CLAUDE.md/governance
  - `verification-protocol`, `replication-protocol` — verifier agent probably absorbed
- **Identical to active (safe to delete):**
  - `exploration-fast-track`, `exploration-folder-protocol`

## Course of action — recommendation

Three-step plan, in order of urgency.

### Step 1 (urgent): De-risk activation

Move the entire archive *out of `.claude/`* so Claude Code stops discovering it. This stops the wildcards immediately, preserves the content for future review, and doesn't require decisions per file.

```
.claude/agents/archive/   →  docs/archive/agents/
.claude/skills/archive/   →  docs/archive/skills/
.claude/rules/archive/    →  docs/archive/rules/
```

Or, if you want them gone from the working tree entirely: `git rm -r .claude/*/archive/` — the content stays in git history, recoverable via `git log --all -- .claude/agents/archive/referee.md`.

My vote: move to `docs/archive/` (or `.archive/` at project root). Keeps it browsable, out of Claude's scanning paths.

### Step 2: Absorb before deleting (the 4 possibly-valuable rules)

Before step 3, diff these against current consolidated rules:

1. `figure-generator-rule.md` vs `figures.md`
2. `table-generator.md` vs `tables.md`
3. `tikz-visual-quality.md` (archived differs from active)
4. `pdf-processing.md` vs what `pdf-learnings` skill covers

If any archived content is missing from the current rule, merge it in. Otherwise delete.

### Step 3: Delete the rest

Once moved out of `.claude/`, the content is in git history + whatever's in `docs/archive/`. After reviewing the 4 rules above, `git rm -r docs/archive/` to reclaim working-tree space. Git history is the permanent record.

## Why this sequence

- **Step 1 fixes the live problem** (wildcard activation) without requiring any content decisions. 10 minutes of work.
- **Step 2 catches the few cases where content is still valuable** without burning time on the obvious-duplicate 70+ files.
- **Step 3 is optional** — some teams prefer to keep `docs/archive/` as a browsable museum; others prefer clean git history only.

## Risks of alternatives

- **Delete everything now without review:** Fast but loses content if any absorbable pieces exist. Git history recovery is possible but friction-y.
- **Review everything file-by-file first:** Comprehensive but ~80 files × 5 min each = 7 hours. The incremental value after the first 4 is near zero because most files are confirmed supersessions.
- **Leave as-is with `disable-model-invocation` flags added to all skills:** Patches skills but leaves agents fully discoverable (no flag exists for agents). Doesn't address the root cause — archive material lives inside Claude's discovery paths.

---

## Decisions needed from Christina

1. **Step 1 target location:** `docs/archive/`, `.archive/` (hidden at root), or `git rm -r` outright (no filesystem copy, only git history)?
2. **Scope:** this review focused on `applied-micro`. Is `behavioral` affected too? (I can check — probably not since behavioral was more recently rebuilt.) Whichever branches have `.claude/*/archive/` should get the same treatment.
3. **Proceed with step 1 alone** (fast) or **steps 1+2** (thorough)?
