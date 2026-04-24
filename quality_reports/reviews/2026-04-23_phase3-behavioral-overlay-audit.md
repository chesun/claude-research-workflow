<!-- primary-source-ok: cochrane_2005 -->
# Phase 3 Audit — Behavioral Overlay Build

**Date:** 2026-04-23
**Comparing:** `behavioral-pre-universal` (e9260cf) vs `main` (5737307)
**Goal:** Foolproof plan to rebuild `behavioral` as a thin overlay on universal main.

---

## Summary

Phase 3 is much bigger than Phase 2. Behavioral has substantively diverged from applied-micro on **10–12 universal files** (not just paradigm-specific additions), so the overlay can't be just "reset to main + add 13 files." Some universal files need to remain on the behavioral version as **paradigm-specific overrides**.

| Layer | Count |
|---|---|
| Pure additions (behavioral-only files, copy as-is) | 17 |
| Paradigm-specific overrides on universal files | ~10 |
| Universal files inherited from main (no override) | ~30+ |
| Files to delete on behavioral (duplicates / lecture leftovers) | 7 |

---

## 1. Pure additions (restore from `behavioral-pre-universal`)

### Agents (6)

`designer.md`, `designer-critic.md`, `theorist.md`, `theorist-critic.md`, `otree-specialist.md`, `qualtrics-specialist.md`

### Skills (5)

`design/`, `theory/`, `otree/`, `qualtrics/`, `preregister/`

### Rules (1 — see Q1 below)

`experiment-design-principles.md`

### References (4)

`domain-profile-behavioral.md`, `inference-first-checklist.md`, `qualtrics-patterns.md`, `seminal-papers-by-subfield.md`

### Folders

`theory/` (formal models, proofs), `experiments/{designs,protocols,instructions,oTree,qualtrics,comprehension,pilots}/`

### CLAUDE.md, TODO.md (overrides — paradigm-flavored)

---

## 2. Paradigm-specific overrides — keep behavioral's version

These universal files have **substantive behavioral-specific content** that would be lost if we used main's version.

| File | Behavioral content not in main |
|---|---|
| `agents/orchestrator.md` | Two pipelines (Behavioral/Experimental + Observational), pre-registration HARD GATE, theorist/designer/qualtrics/oTree dispatch tables |
| `agents/verifier.md` | Check 5: Experimental Materials (instructions PDF, Qualtrics QSF, oTree devserver) |
| `agents/writer.md` | References `domain-profile-behavioral.md` for behavioral framing; behavioral-specific intro examples |
| `rules/quality.md` | Behavioral weights (theory 15%, design 25%, implementation 7%, paper 20%) |
| `rules/workflow.md` | Theory phase, Design phase, Pre-registration gate, behavioral phase severity |
| `skills/new-project/SKILL.md` | Orchestrates Theory → Design → Pre-registration → Implementation |
| `skills/discover/SKILL.md` | Behavioral subfield discovery (lab/field/online experiments, theory) |
| `skills/review/SKILL.md` | References designer-critic, theorist-critic |
| `skills/submit/SKILL.md` | References pre-registration in package |
| `skills/analyze/SKILL.md` | Spot-check during staging — only 3 paradigm mentions; may not need override |

**Heuristic basis:** Each file was probed for paradigm-specific keyword density (designer/theorist/otree/qualtrics/preregister/experiment/behavioral). Files with ~5+ mentions and substantive content blocks unique to behavioral are flagged as overrides.

---

## 3. Universal files — use main's version (no override)

These were modified on behavioral but the modifications are stale (older versions of universal content). Main has the better version.

| File | Reason main wins |
|---|---|
| `agents/coder.md`, `coder-critic.md` | Main has the absorbed Common Pitfalls table from BDM port + `stata-code-conventions` rename |
| `agents/writer-critic.md` | Same prose-quality content; main has correct `stata-code-conventions` ref |
| `agents/storyteller.md`, `storyteller-critic.md` | Identical (zero paradigm mentions) |
| `agents/data-engineer.md`, `librarian.md`, `librarian-critic.md`, `explorer.md`, `explorer-critic.md`, `methods-referee.md`, `domain-referee.md` | Universal pipeline agents — main has latest |
| `rules/agents.md` | Main has the recent strategist+designer+theorist references |
| `rules/replication-protocol.md`, `python-code-conventions.md`, `stata-code-conventions.md` | Main has correct rename + AEA detail |
| `rules/exploration-fast-track.md`, `exploration-folder-protocol.md` | Same |
| `skills/talk/SKILL.md` | Main describes Beamer (universal); behavioral version mentions Quarto (which user no longer uses) |
| `skills/write/SKILL.md`, `revise/SKILL.md`, `challenge/SKILL.md`, `tools/SKILL.md` | Universal; main has latest fleshed-out subcommands |
| `references/journal-profiles.md`, `domain-profile.md`, `replication-standards.md`, `content-standards.md` | Universal |

---

## 4. Decisions to make before executing

### Q1: `content-standards.md` location?

- Behavioral: `rules/content-standards.md` (full content + extra paths for .py, .jl, .do, .doh)
- Main: `references/content-standards.md` (universal version)

These are similar but the role differs — `rules/` means active rule, `references/` means reference doc.

**Recommendation:** Keep main's `references/content-standards.md` as the canonical location. Don't add a `rules/content-standards.md` on behavioral — its paths-list extension is already covered by language-specific code conventions rules.

### Q2: `writer.md` example sentence — override or inherit?

Main: applied-micro example (minimum-wage / border-discontinuity)
Behavioral: behavioral example (risk preferences / within-subject)

Both illustrate the same writing principle.

**Options:** (a) override on behavioral; (b) use main's; (c) replace main's with paradigm-neutral placeholder.

**Recommendation:** (a) override on behavioral with the behavioral example, since writer.md is already on the override list for the `domain-profile-behavioral.md` reference. Less work than refactoring main; behavioral writer is paradigm-specific anyway.

### Q3: Hooks (`post-merge.sh`, `post-compact-restore.py`, `pre-compact.py`, `protect-files.sh`)?

Behavioral versions are slightly older / longer. Main has the recent simplifications.

**Recommendation:** Use main's version. If a behavioral-specific hook behavior is needed, surface it as a separate review item.

### Q4: Three duplicate rules on behavioral — delete?

`session-logging.md` (superseded by `logging.md`), `plan-first-workflow.md` (superseded by `workflow.md` §1), `orchestrator-protocol.md` (superseded by `workflow.md` §2).

**Recommendation:** Delete by exclusion (just don't restore them on the staging branch).

### Q5: Top-level legacy on behavioral — drop?

- `Bibliography_base.bib` — lecture-template leftover
- `guide/` — Quarto guide site source
- `CHANGELOG.md` — clo-author upstream changelog (no longer accurate)

**Recommendation:** Drop all three. Already dropped from main; behavioral should mirror.

### Q6: Quality weights — behavioral overrides?

Main: literature 10%, data 10%, identification/strategy 25%, code 15%, paper 25%, polish 10%, replication 5%
Behavioral: literature 8%, theory 15%, design 25%, implementation 7%, code 10%, paper 20%, polish 10%, replication 5%

Behavioral adds Theory and Implementation components.

**Recommendation:** Already in §2 — behavioral overrides quality.md.

---

## 5. Stale references audit (within behavioral-only files)

Need to grep restored files for references to deleted/renamed things. Will run during Phase 3 staging build (analogous to Phase 2 pre-flight). Specifically scan for:

- `stata-conventions.md` (old name → `stata-code-conventions.md`)
- `Bibliography_base.bib` (deleted → `paper/references.bib`)
- `extract-tikz`, `compile-latex`, `validate-bib` (standalone skills no longer exist; folded into `/tools`)
- `references/content-standards.md` references inside behavioral-only files (verify path)

---

## 6. Foolproof Phase 3 plan

### Step 0 — pre-flight (already done)

`behavioral-pre-universal` archive exists ✓
Main is at `5737307` ✓

### Step 1 — staging branch from main

```
git checkout -b behavioral-rebuild-staging main
```

### Step 2 — restore pure additions (17 files + 2 folders)

```
git checkout behavioral-pre-universal -- \
  .claude/agents/{designer,designer-critic,theorist,theorist-critic,otree-specialist,qualtrics-specialist}.md \
  .claude/skills/{design,theory,otree,qualtrics,preregister}/ \
  .claude/rules/experiment-design-principles.md \
  .claude/references/{domain-profile-behavioral,inference-first-checklist,qualtrics-patterns,seminal-papers-by-subfield}.md \
  theory/ experiments/ \
  CLAUDE.md TODO.md
```

### Step 3 — apply paradigm-specific overrides (~10 files)

```
git checkout behavioral-pre-universal -- \
  .claude/agents/orchestrator.md \
  .claude/agents/verifier.md \
  .claude/agents/writer.md \
  .claude/rules/quality.md \
  .claude/rules/workflow.md \
  .claude/skills/new-project/SKILL.md \
  .claude/skills/discover/SKILL.md \
  .claude/skills/review/SKILL.md \
  .claude/skills/submit/SKILL.md
# Spot-check skills/analyze/SKILL.md — restore only if paradigm content is substantive
```

### Step 4 — fix stale references inside restored files

Grep for the patterns from §5. Apply same surgical fixes Phase 2 did.

### Step 5 — clean up duplicates and legacy

Handled by exclusion (we never bring them back from `behavioral-pre-universal`):

- `rules/{session-logging,plan-first-workflow,orchestrator-protocol}.md` (duplicates)
- `rules/content-standards.md` (Q1: keep main's `references/` version)
- `Bibliography_base.bib`, `guide/`, `CHANGELOG.md` (legacy)

### Step 6 — verify

```
# References sanity (must be empty)
grep -rn "stata-conventions\.md\|Bibliography_base\.bib" .claude/

# File counts vs expected
ls .claude/agents/*.md | wc -l   # expect 23 (17 universal + 6 behavioral)
ls .claude/skills/ | wc -l       # expect 19 (14 universal + 5 behavioral)
ls .claude/rules/*.md | wc -l    # expect 23 (22 universal + 1 behavioral)
ls .claude/references/ | wc -l   # expect 9 (5 universal + 4 behavioral)

# Diff vs main: expect only behavioral additions and overrides
diff <(git ls-tree -r --name-only main -- .claude/ | sort) \
     <(git ls-tree -r --name-only HEAD -- .claude/ | sort)
```

### Step 7 — commit + push staging for review

### Step 8 — after approval: force-reset behavioral

Same fast-forward pattern as Phase 2.

---

## 7. Risks specific to Phase 3

1. **Behavioral has more divergence than applied-micro had.** Higher chance an override decision misses context. *Mitigation:* per-file diff sampling above caught the heavy-paradigm files; spot-check borderline ones during staging.

2. **`agents.md` rule on behavioral lacks the recent strategist+designer+theorist update from main.** Resolved: main's agents.md already has the three-paradigm references — behavioral overlay inherits them.

3. **Behavioral `writer.md` references `domain-profile-behavioral.md`.** Now in §2 overrides (10 files, not 9).

4. **`skills/analyze/SKILL.md` borderline (3 mentions).** Spot-check during staging; restore only if substantive.

5. **CLAUDE.md describes behavioral folder structure (theory/, experiments/, etc.)** — that's correct, restored as-is.

---

## 8. Decisions needed before execution

| # | Question | Recommendation |
|---|---|---|
| Q1 | content-standards location | Keep main's `references/`, drop behavioral's `rules/` version |
| Q2 | writer.md example | Override on behavioral with the existing behavioral phrasing |
| Q3 | hooks | Use main's version |
| Q4 | duplicate rules | Delete by exclusion |
| Q5 | top-level legacy | Drop Bibliography_base.bib, guide/, CHANGELOG.md |
| Q6 | quality weights | Behavioral overrides (decided earlier) |

---

## 9. Estimated effort

- 5 min: pre-flight + staging branch
- 10 min: pure additions restoration
- 10 min: paradigm-specific overrides
- 10 min: stale-reference fixes
- 10 min: verification, commit, push staging
- **Total: ~45 min** to staging-pushed; force-push to behavioral after approval.
