# Derive-Don't-Guess — Universal Rule Proposal

**Status:** PROPOSAL (awaiting your approval before implementation)
**Date:** 2026-04-28
**Triggered by:** csac codebook-script incident — Claude guessed dataset filepaths when the actual paths were defined in `do/settings.do` as globals (`$csacrawdatadir`, `$csacclndatadir`).

---

## The principle

**If a fact is derivable from the repo, derive it. Do not guess.**

Filepath, variable name, macro, function, package version, output convention, directory structure, config value — any fact that *already exists somewhere in the project* must be looked up, not invented. Inventing facts that the repo has already decided produces code that won't run, references that don't resolve, and silent drift between what Claude writes and what the project uses.

This is the inward-facing twin of `primary-source-first.md`: where that rule requires reading the actual paper before citing, this rule requires reading the actual code before referencing repo entities. Same epistemic stance, different artifact type.

---

## Relationship to other rules (so we don't proliferate)

Three rules already touch the same epistemic territory; this one fills the only remaining gap.

| Rule | Scope | Source-of-truth |
|---|---|---|
| `~/.claude/rules/no-assumptions.md` (global) | User preferences, workflow, tools, role boundaries | The user's stated requirements |
| `.claude/rules/primary-source-first.md` | Framing claims about external papers | The actual PDF in `master_supporting_docs/literature/papers/` |
| `.claude/rules/adversarial-default.md` | Compliance claims about any artifact | A grep / diagnostic / test output recorded in the verification ledger |
| **proposed** `.claude/rules/derive-dont-guess.md` | Fact-level references to internal repo content | The relevant file in this repo |

No overlap. Each rule has a distinct failure mode it deterministically catches.

---

## Failure modes the rule addresses

| Failure mode | Concrete example | What was missed |
|---|---|---|
| Filepath fabrication | "I need to load the cleaned dataset" → guesses `data/cleaned/main.dta` | `do/settings.do` defines `$csacclndatadir/main_v3.dta` |
| Variable-name fabrication | Generates `gen female = (gender == "F")` | Cleaning script has `gender_id`, not `gender`; values are coded `1`/`2`, not `"F"`/`"M"` |
| Macro / global reference | Uses raw paths in code | Project convention is global macros from `settings.do` |
| Package version drift | Imports `library(fixest)` | Other scripts import `library(fixest, quietly = TRUE)` and use a specific tF method that requires a min version |
| Output-path drift | Saves to `output/table1.tex` | Project convention saves to `tab/01_main_specification.tex` per existing `esttab` calls |
| Directory-structure assumption | Writes to `scripts/stata/` | Project uses flat `do/` layout (csac convention) |
| Config-value fabrication | Picks `seed = 42` | `settings.do` defines `set seed 20230501` for reproducibility |
| Function/dependency drift | Defines a new helper for log-cleaning | Project has `do/helpers/clean_logs.doh` |

The pattern: every one of these is a fact the repo already encodes. Reading the repo would have given the right answer. Guessing produced wrong answers.

---

## Proposed implementation

Two layers in v1. (Hook automation is conceivable but hard; skip for now, like with adversarial-default.)

### Layer 1 (required) — `.claude/rules/derive-dont-guess.md`

Articulates the principle, the failure modes, and a "where to look first" table for each entity type. Loaded by every agent.

Structure:

1. **The principle.** One paragraph: derivable facts must be derived; never invent what the repo has already decided.

2. **Pre-generation derivation checklist** — concrete by entity type:

   | Entity type | Where to look first | Example commands |
   |---|---|---|
   | Filepaths to datasets | Settings file, master script, existing analysis scripts that load same data | Stata: `grep -nE 'use \\| import' do/*.do`; R: `grep -nE 'read_csv\\|read_dta\\|readRDS' scripts/**/*.R` |
   | Variable names | Cleaning scripts, codebooks, label statements | `grep -nE 'label var\\|gen ' do/01_clean*.do`; `glimpse(df)` in R |
   | Macros / globals (Stata) | `settings.do`, master script's top | `grep -nE 'global ' do/settings.do do/main.do` |
   | Functions / packages | Existing scripts (mirror imports) | `grep -nE 'library\\(\\|require\\(\\|import ' scripts/**/*.{R,py}` |
   | Output paths | Existing `save`/`export`/`saveRDS`/`writeLines` calls | `grep -nE 'save \\| export \\| saveRDS' do/*.do scripts/**/*.R` |
   | Config values (seed, cutoff, etc.) | Settings file, top of master, project rules | `grep -nE 'set seed\\|set\\.seed\\(' do/*.do scripts/**/*.R` |
   | Directory structure | `ls` and `tree` the repo before assuming | `find . -maxdepth 2 -type d` |
   | Naming conventions | Existing variable / file names | `ls scripts/**/*.R do/*.do`; visual scan for snake_case vs camelCase |

3. **The "ask" exception.** When derivation truly fails (no settings file, no analogous existing script, no convention to mirror), explicitly say "Creating a new convention here because no existing pattern found in [files searched]." Do not silently fabricate.

4. **Citation requirement.** When generating code that references a derived entity, the agent must name the source: `# path from do/settings.do:12`, or `# variable from do/01_clean_demographics.do:47`, or `# convention mirrored from do/figures/fig01.do save block`. Comments are optional in production code; the citation requirement is for the agent's *internal* response (or the session log) — the user can audit by asking "where did you get that path from?"

5. **Cross-references.** Lists which other rules this principle reinforces (no-assumptions, primary-source-first, adversarial-default).

### Layer 2 (high-value) — coder + writer agent prompt updates

**coder agent** (the worker, not the critic): before generating any new script, must perform the pre-generation derivation checklist for whatever entities the script will reference. Output should include either:

- "Derived from: [file:line]" pointers for each external entity, OR
- "New convention: [name]; no existing pattern found in [files searched]"

**coder-critic**: deduct when generated code references entities that aren't in the repo — i.e., when the worker fabricated a path/var/macro that the repo didn't define. Concretely:

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Generated code uses a filepath that doesn't exist in the project AND no analogous existing path was cited | -25 |
| Critical | Generated code references a Stata global (`$foo`) that's not defined in `settings.do` or the master script | -20 |
| Major | Variable name in generated code doesn't appear in cleaning scripts and isn't being created in this same script | -10 |
| Major | Output path doesn't follow any existing convention (no other script writes to a parallel location) AND no "new convention" disclosure | -10 |
| Minor | Config value (seed, cutoff, bandwidth) chosen without citing where the project sets it | -3 per occurrence (max -15) |

**writer agent + writer-critic**: same logic for paper text. If a paper paragraph cites a number, that number must exist in a tracked output file. Fabricating values is the writing-side analog of fabricating paths.

### What we're NOT proposing

- **No hooks.** A hook that detects fabricated paths is conceivable (compare every string-literal-path in generated code against actual files) but lots of false positives (paths that *will* be created by this script, paths in comments, etc.). Skip for v1. Revisit if Layer 1+2 underdeliver.
- **No verification ledger entries.** Adversarial-default has the ledger because compliance claims are slow to verify (run a `grep`, run `pdflatex`, etc.). Derivation is fast — re-reading `settings.do` is cheap, no caching needed. Don't add ledger overhead.

---

## Naming

Recommendation: **`derive-dont-guess.md`**. Direct, action-oriented, parallels the imperative tone of `primary-source-first.md`.

Alternates considered:

- `read-the-code-first.md` — descriptive but verbose
- `no-guessing.md` — terse but doesn't say what to do instead
- `derivation-required.md` — formal but stiff
- `evidence-before-generation.md` — covers the spirit but echoes adversarial-default too much
- `rtfc.md` — fun but unprofessional in a public template

---

## Tradeoffs

| Pro | Con | Mitigation |
|---|---|---|
| Catches the filepath-guessing failure (the trigger) and many similar failure modes | Extra read step before generation | Cost is small — one `grep` of `settings.do` answers most "what's the path" questions |
| Forces explicit "new convention" disclosure when no precedent exists | Some false positives in fast iterating projects (precedent doesn't yet exist) | The "new convention" exception covers this; user can override |
| Auditable — agent must name source files | Harder to write totally fresh code in a brand-new repo with no precedent | Brand-new repos: the rule is degenerate (everything is "new convention"); cost is the disclosure overhead, which is small |

---

## Where to ship

This is a universal rule, so:

1. `claude-code-my-workflow@main` — write the rule + critic updates
2. Cherry-pick to `applied-micro` and `behavioral`
3. Sync to all downstream repos that have the workflow installed: `va_consolidated`, `tx_peer_effects_local`, `bdm_bic`, `csac2025`, `csac` (now full-workflow)
4. Optionally: a stripped-down version goes to global `~/.claude/rules/` so it applies even outside research projects. The principle is universal even though the per-entity-type table is research-flavored. My recommendation: ship a one-paragraph stripped version to global. The full per-entity table stays project-level.

---

## Decision points for you

1. **Concept ok?** Or refine scope (e.g., only apply when generating code, not when writing text)?
2. **Layers** — Layer 1 (rule alone) or Layer 1 + Layer 2 (rule + coder/coder-critic + writer/writer-critic prompt updates)? My recommendation: 1+2.
3. **Name** — `derive-dont-guess.md` recommended. Alternate: any of the others above.
4. **Skip hooks?** My recommendation: yes, skip.
5. **Global stripped-down version?** A one-paragraph version of the principle in `~/.claude/rules/derive-dont-guess.md` so it applies to non-research sessions too. My recommendation: yes — universal applicability, low overhead.

Tell me your answers and I'll write the rule, update the agents, ship to main + overlays + downstream repos, and (if approved) the global config.
