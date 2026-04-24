# Session Log: 2026-04-24 — Universal-Main Trunk + Dual-Overlay Refactor

**Status:** COMPLETED
**Branches affected:** `main`, `applied-micro`, `behavioral` (and 3 archive branches)
**Total commits across branches:** 13

## Objective

Promote the `applied-micro` workflow to `main` (which had been a stale parking lot for Pedro Sant'Anna's upstream lecture template + 6 planning commits), but *as a paradigm-agnostic universal trunk* rather than a 1:1 copy. Rebuild both `applied-micro` and `behavioral` as thin overlays on the new universal main. Universal improvements henceforth land on main and propagate to both overlays.

## Architecture decision

Trunk + overlays pattern (analogous to Debian + Ubuntu + Mint):

- `main` = universal research-workflow trunk. Paradigm-agnostic. Forkers land here by default.
- `applied-micro` = thin overlay on main. Adds identification-strategy tooling for observational/administrative-data research.
- `behavioral` = thin overlay on main. Adds experimental-economics + formal-theory tooling.

Universal improvements flow main → overlays via rebase. Paradigm-specific work stays on the relevant overlay.

## Phase-by-phase summary

### Phase 0 — Archives (5 min)

Created three preservation branches before any destructive operation:

- `main-lecture-archive` ← prior main (Pedro's lecture template)
- `applied-micro-pre-universal` ← prior applied-micro
- `behavioral-pre-universal` ← prior behavioral

All pushed to origin. Recovery is `git reset --hard <archive-branch>`.

### Phase 1 — Build universal main from applied-micro base (~2 hours, 5 commits)

**Source:** `applied-micro` HEAD (closest to "universal" of the existing branches).

**Removed (applied-specific):**
- 2 agents: `strategist`, `strategist-critic`
- 3 skills: `strategize`, `balance`, `event-study`
- 1 rule: `air-gapped-workflow`
- Lecture-template leftovers: `Bibliography_base.bib`, `guide/`, `docs/`, `quarto/`, `slides/`, `scripts/sync_to_docs.sh`, `scripts/quality_score.py`, `templates/constitutional-governance.md`, `master_supporting_docs/{supporting_slides,experimental_design}/`
- 3 standalone utility skills consolidated into `/tools`: `compile-latex`, `validate-bib`, `extract-tikz`

**Added (universal content from behavioral):**
- 1 agent: `editor` (referee-report synthesis)
- 1 rule: `meta-governance`

**Modified (paradigm neutralization):**
- `CLAUDE.md` rewritten as paradigm-neutral template with placeholders + Overleaf-path header
- `README.md` rewritten with three-branch framing, credits to Pedro and Hugo as base
- `workflow.md` and `agents.md` reference both `strategist` (applied) and `designer`/`theorist` (behavioral)
- `quality.md` weighted-aggregation row generalized to "Strategy / design validity"
- Renamed `stata-conventions.md` → `stata-code-conventions.md` (matches `r-code-conventions.md` pattern)
- `/tools` subcommands `compile` and `validate-bib` fleshed out from the standalone-skill procedures

**Folder reconciliation:** added stub directories for `paper/`, `paper/sections/`, `talks/`, `data/{raw,cleaned}/`, `tables/`, `replication/`, `scripts/{stata,python}/` so forkers land on a complete scaffold matching CLAUDE.md's diagram.

**Phase 1.5 cleanup (audit before Phase 2):**
- Removed 4 applied-specific files from `.claude/references/` (`domain-profile-applied-micro.md`, `journal-profiles-applied-micro.md`, `identification-checklists.md`, duplicate `meta-governance.md`).
- Fixed 5 stale references missed in Phase 1: `coder.md`, `replication-protocol.md` (×2), `write/SKILL.md`, `protect-files.sh` — all referencing the renamed `stata-conventions.md` or deleted `Bibliography_base.bib`.

**Result:** main = 17 agents, 14 skills, 22 rules, 5 references.

### Phase 2 — Applied-micro overlay (~30 min, 2 commits)

Branched staging from main, restored 11 applied-specific items from `applied-micro-pre-universal`:

- 2 agents: `strategist`, `strategist-critic`
- 3 skills: `strategize`, `balance`, `event-study`
- 1 rule: `air-gapped-workflow`
- 3 references: `domain-profile-applied-micro`, `journal-profiles-applied-micro`, `identification-checklists`
- Applied-flavored CLAUDE.md and TODO.md

**Reference reconciliation (3 fixes):**
- `agents/strategist-critic.md`: `Bibliography_base.bib` → `paper/references.bib`
- `skills/balance/SKILL.md`: `stata-conventions.md` → `stata-code-conventions.md`
- `skills/event-study/SKILL.md`: same

Commit message preserved as overlay record. `applied-micro` ended up at HEAD with linear history (fast-forward, not actual force-push, since applied-micro's prior HEAD was an ancestor of universal-main-staging).

**Result:** applied-micro = 19 agents, 17 skills, 23 rules, 8 references.

### Phase 3 — Behavioral overlay (~50 min, 1 commit)

More complex than Phase 2 because behavioral had 10 paradigm-specific overrides on universal files (not just pure additions). Required deep audit before restoration.

**Audit findings (`quality_reports/reviews/2026-04-23_phase3-behavioral-overlay-audit.md`):**

For each modified universal file, I probed paradigm-keyword density and per-file diff sizes:

| Layer | Count | Disposition |
|---|---|---|
| Pure behavioral additions | 17 files + 2 folder trees | Restore from archive |
| Paradigm-specific overrides | 10 universal files | Restore behavioral version |
| Universal inheritance | ~30 files | Use main's (latest) |
| Cleanup by exclusion | 7 files | Don't restore (duplicates, lecture leftovers) |

**Pure additions restored:**
- 6 agents: `designer`, `designer-critic`, `theorist`, `theorist-critic`, `otree-specialist`, `qualtrics-specialist`
- 5 skills: `design`, `theory`, `otree`, `qualtrics`, `preregister`
- 1 rule: `experiment-design-principles`
- 4 references: `domain-profile-behavioral`, `inference-first-checklist`, `qualtrics-patterns`, `seminal-papers-by-subfield`
- Behavioral-flavored CLAUDE.md, TODO.md
- Folder stubs created (theory/, experiments/{designs,protocols,instructions,oTree,qualtrics,comprehension,pilots}/) — gap caught: behavioral-pre-universal didn't track these as git folders

**Paradigm-specific overrides:**
- `agents/orchestrator.md` — dual pipeline (behavioral/experimental + observational), pre-registration HARD GATE, theorist/designer/qualtrics/oTree dispatch tables
- `agents/verifier.md` — Check 5 Experimental Materials (instructions PDF, Qualtrics QSF, oTree devserver)
- `agents/writer.md` — references `domain-profile-behavioral.md`
- `rules/quality.md` — behavioral weights (theory 15%, design 25%, implementation 7%)
- `rules/workflow.md` — Theory phase, Design phase, Pre-registration gate
- `skills/{new-project, discover, review, submit, analyze}/SKILL.md` — paradigm-flavored orchestration

**Cleanup by exclusion (NOT restored):**
- 3 duplicate rules: `session-logging.md` (superseded by `logging.md`), `plan-first-workflow.md` (superseded by `workflow.md` §1), `orchestrator-protocol.md` (superseded by `workflow.md` §2)
- `rules/content-standards.md` (kept main's `references/` version as canonical)
- 3 lecture leftovers: `Bibliography_base.bib`, `guide/`, `CHANGELOG.md`

**Result:** behavioral = 23 agents, 19 skills, 23 rules, 9 references.

### Phase 4 — Verification (~10 min)

| Check | main | applied-micro | behavioral |
|---|---|---|---|
| Agent count | 17 ✓ | 19 ✓ | 23 ✓ |
| Skill count | 14 ✓ | 17 ✓ | 19 ✓ |
| Rule count | 22 ✓ | 23 ✓ | 23 ✓ |
| Reference count | 5 ✓ | 8 ✓ | 9 ✓ |
| Stale `stata-conventions.md` refs | 0 ✓ | 0 ✓ | 0 ✓ |
| Stale `Bibliography_base.bib` refs | 0 ✓ | 0 ✓ | 0 ✓ |
| Primary-source hook fires on test write | PASS ✓ | PASS ✓ | PASS ✓ |

### Phase 5 — TODO updates per branch (3 commits)

- `behavioral`: Phase 1–3 entry to Done; guide-site v1 + screenshots/demos added to Backlog.
- `applied-micro`: same (paradigm-flavored).
- `main`: kept as paradigm-neutral fork-and-fill template stub (no project-specific Done entries).

## Changes Made (commit-level summary across branches)

| Commit | Branch | Phase | Notes |
|---|---|---|---|
| `f742f93` | main (was staging) | 1a–1h | Initial universal-main build |
| `90f7ed3` | main | 1 | Drop redundant standalone skills |
| `9cd6241` | main | 1 | Remove lecture-template leftovers |
| `c38d91a` | main | 1 | Reconcile folder structure with CLAUDE.md |
| `018fe51` | main | 1 | Flesh out /tools compile and validate-bib |
| `bceaf37` | main | 1.5 | Cleanup references/ + quality.md |
| `5737307` | main | 1.5 | Fix 5 stale references missed in Phase 1 |
| `ec48949` | applied-micro | 2 | Applied-micro overlay on universal main |
| `2393427` | applied-micro | 5 | TODO update |
| `0c0d8ba` | behavioral | 3 | Behavioral overlay on universal main |
| `4ca2c7f` | behavioral | 5 | TODO update |

## Design Decisions

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| Trunk + overlays pattern | (a) Hard replace main with applied-micro 1:1; (b) router-main with branches as primaries; (c) separate repo for each paradigm | (a) loses universal abstraction; (b) creates friction for forkers; (c) overhead. Trunk+overlays is industry-standard (Debian/Ubuntu/Mint) |
| Universal main as **superset of common content**, not lowest common denominator | Strip everything paradigm-specific (smaller main); keep all consolidations | Forkers benefit from substantial out-of-box capability. Removing paradigm-specific (strategist, designer/theorist) is the only essential paring. |
| `editor` and `/preregister` decisions: editor universal, preregister behavioral | Editor: behavioral-only; preregister: also applied | Editor's referee-synthesis logic applies to any paradigm. Preregister has applied-micro AEA pre-analysis-plan analogues but the existing skill is built around AsPredicted/OSF Coffman-Dreber for behavioral; defer applied-side until needed. |
| `air-gapped-workflow` as applied-only | Universal | Decision made by user — narrowly scoped to secure-data-room workflows that primarily affect applied-micro use cases |
| Quality weights: main inherits applied weights as default; behavioral overrides | Universal weight algorithm with renormalization | Cleaner per-overlay file; behavioral has Theory + Implementation components that don't exist in applied. Each overlay declares its own weighting. |
| Strategist/designer/theorist references in workflow.md/agents.md by name (no abstraction) | Abstract "strategy slot" with overlay-supplied agent | KISS — both names present. Forkers reading the rules see the paradigm split explicitly. |
| `/tools` subcommands fleshed out vs restoring standalone skills | Keep /tools light, accept the loss | The lightweight subcommands missed substantive procedures (engine detection, warning grep, structured reporting). Fleshing inside /tools preserves single-skill consolidation. |
| Force-push vs PR merge for main | Standard PR with `-X theirs` merge strategy | Main and applied-micro had ~90% file overlap with totally different structure. PR would produce a single massive diff commit; force-push to applied-micro's HEAD is cleaner for downstream readability. Archive branches preserve the prior history. |
| CLAUDE.md per-overlay vs universal-with-includes | Universal CLAUDE.md with conditional sections | Each overlay has substantively different framing. CLAUDE.md is naturally per-overlay anyway. |
| Defer guide site to future | Build it now | Premature — workflow just stabilized; need real-project examples before writing the guide |

## Incremental Work Log

**Phase 0 (early):** Archived three branches.
**Phase 1a–1i:** Built universal-main-staging by surgery on applied-micro base; merged to main via force-reset after staging review.
**Phase 1 follow-up (1.5):** Caught 4 reference-file orphans + 1 duplicate during Phase 2 audit; cleaned and pushed before Phase 2 staging.
**Phase 1 /tools deepening:** User noticed /tools compile was a 4-line stub vs the deleted standalone skill's 6-step procedure. Fleshed out compile and validate-bib with full procedures.
**Phase 1 stale-ref fix:** Phase 2 audit found 5 references on main pointing at the renamed stata-conventions.md or deleted Bibliography_base.bib. Sed-fixed.
**Phase 2:** Restored 11 applied-specific items, fixed 3 stale refs, fast-forward to applied-micro.
**Phase 3 audit:** Per-file paradigm-density analysis classified universal-modified files as keep-main vs override-with-behavioral.
**Phase 3 staging:** Restored 17 pure additions + 10 paradigm overrides + folder stubs. Stale-ref scan: clean. Force-pushed to behavioral.
**Phase 4–5:** Smoke tests + TODO updates per branch.

## Learnings & Corrections

- **Audit before each major step.** Phase 1 missed 4 reference files and 5 stale internal references; Phase 1.5 caught them only because Phase 2 audit grep'd for stata-conventions and Bibliography_base. Lesson: enumerate all references inside restored files BEFORE the bigger force-push.
- **Behavioral has more paradigm-specific elaboration on universal files than applied-micro did.** Phase 2 was naive (reset + add); Phase 3 needed per-file judgment for ~10 files. The "thin overlay" pattern works best when paradigm-specific content is in distinct files; mixed paradigm-and-universal files require explicit override decisions.
- **Folder stubs needed early.** Both `behavioral-pre-universal` and `applied-micro-pre-universal` lacked `theory/`, `experiments/`, `paper/sections/`, `data/raw,cleaned/`, etc. as git-tracked folders despite CLAUDE.md describing them. CLAUDE.md and reality drifted because Overleaf was the actual paper home. Universal main now ships with all the diagram folders as `.gitkeep` stubs.
- **Force-push behavior:** Phase 2 turned out to be a fast-forward (applied-micro's prior HEAD was an ancestor of staging via the main rebuild lineage). Phase 3 was a real force-push because behavioral diverged in parallel. Both safe due to archive branches.
- **/tools subcommand depth matters:** The standalone skills had structured outputs (engine detection, log parsing, formatted reports) that the consolidation lost. Fleshing the subcommands recovered this without un-doing the consolidation.
- **Hook escape hatch tested in real workflow:** Writing the Phase 3 audit doc tripped primary-source-first on a Cochrane (2005) reference. Used the `<!-- primary-source-ok: cochrane_2005 -->` escape hatch correctly. Confirms the hook + escape mechanism is working as designed.

## Verification Results

| Check | Result | Status |
|-------|--------|--------|
| Universal main agent/skill/rule/ref counts | 17/14/22/5 | PASS |
| Applied-micro overlay counts | 19/17/23/8 | PASS |
| Behavioral overlay counts | 23/19/23/9 | PASS |
| Stale `stata-conventions` refs (any branch) | 0 | PASS |
| Stale `Bibliography_base` refs (any branch) | 0 | PASS |
| Primary-source-first hook fires (behavioral) | block on test citation | PASS |
| Universal CLAUDE.md folder structure matches reality | All folders exist as stubs | PASS |
| Archive branches reachable on origin | 3 branches | PASS |

## Open Questions / Blockers

- [ ] **Reverse direction sync workflow:** if a universal improvement lands on main, what's the canonical procedure to bring it to both overlays? Rebase (preserves history but may conflict on the 10 behavioral overrides) or cherry-pick (cleaner but loses parent linkage)? Document when a real cross-branch change happens.
- [ ] **Main's `quality.md` overlap with behavioral's override.** Behavioral overrides quality.md with its own weights. If main updates quality.md's structure (e.g., adding a new component row), behavioral's override may need manual reconciliation. Watch for this on next universal-main quality.md change.
- [ ] **Decision-log usage going forward.** No actual ADRs have been written yet for the dual-overlay architecture decisions made in this session. Worth writing 1–2 ADRs (e.g., "Trunk + overlays architecture", "Paradigm overrides on universal files") in `decisions/` to lock in these decisions for future reference. Defer to next session.

## Next Steps

- [ ] Write 1–2 ADRs in `decisions/` for the architecture decisions in this session (deferred from §Open Questions).
- [ ] On next BDM/JMP session, exercise the new structure: confirm `/strategize` (or `/design`/`/theory` on behavioral) dispatches correctly, primary-source hooks fire as expected, /tools compile reads CLAUDE.md correctly.
- [ ] When a real cross-branch sync occurs (universal improvement on main → overlays), document the procedure as a learning.
- [ ] Eventually: guide site v1 (deferred — pre-req: real-project examples).
