# Derive, Don't Guess

**The principle: if a fact is derivable from the repo, derive it.**

Filepath, variable name, macro, function, package version, output convention, directory structure, config value — any fact that *already exists somewhere in the project* must be looked up, not invented. Inventing facts that the repo has already decided produces code that won't run, references that don't resolve, and silent drift between what Claude writes and what the project uses.

This is the inward-facing twin of `primary-source-first.md`. That rule requires reading the actual paper before citing; this rule requires reading the actual code before referencing repo entities. Same epistemic stance, different artifact type.

---

## Where this fits in the epistemic stack

Four rules together prevent four distinct failure modes of "filling in blanks":

| Rule | Source-of-truth | What it prevents |
|---|---|---|
| `no-assumptions.md` | The user's stated requirements | Guessing about user preferences, workflow, tools, role boundaries |
| `primary-source-first.md` | The actual PDF in `master_supporting_docs/literature/papers/` | Framing claims about external papers without reading them |
| `adversarial-default.md` | A `grep` / diagnostic / test output recorded in the verification ledger | Asserting compliance without producing evidence |
| **derive-dont-guess.md** (this rule) | The relevant file in this repo | Fabricating internal facts when the repo has the answer |

Each rule has a distinct scope. Together they form the workflow's epistemic floor: don't make things up, don't claim what you haven't checked, don't guess what you can derive.

---

## Pre-generation derivation checklist

Before generating any code or text that references a repo entity, perform the lookup for that entity type. Cost is small (one `grep` of a settings file usually answers most lookups); the savings from not running broken code are large.

| Entity type | Where to look first | Example commands |
|---|---|---|
| Filepaths to datasets | Settings file, master script, existing analysis scripts that load same data | Stata: `grep -nE 'use \\\| import' do/*.do`<br>R: `grep -nE 'read_csv\\\|read_dta\\\|readRDS' scripts/**/*.R`<br>Python: `grep -nE 'pd\\.read_\\\|np\\.load' scripts/**/*.py` |
| Variable names | Cleaning scripts, codebooks, label statements | `grep -nE 'label var\\\|gen ' do/0[12]_clean*.do`<br>R: `glimpse(df)` or `names(df)` |
| Macros / globals (Stata) | `settings.do`, master script's top section | `grep -nE 'global ' do/settings.do do/main*.do` |
| Functions / packages | Existing scripts (mirror imports / library calls) | `grep -nE 'library\\(\\\|require\\(\\\|import \\\|from ' scripts/**/*.{R,py}` |
| Output paths and naming | Existing `save`/`export`/`saveRDS`/`writeLines` calls | `grep -nE 'save \\\| export \\\| saveRDS' do/*.do scripts/**/*.R` |
| Config values (seed, cutoff, bandwidth) | Settings file, top of master, project rules | `grep -nE 'set seed\\\|set\\.seed\\(\\\|np\\.random\\.seed' do/*.do scripts/**/*.{R,py}` |
| Directory structure | `ls`/`find` the repo before assuming | `find . -maxdepth 2 -type d -not -path '*/.*'` |
| Naming conventions | Existing variable / file names | `ls do/ scripts/**/*.R`; visual scan for snake_case vs camelCase, prefix conventions |
| Helper functions / utilities | Existing `helpers/` or `lib/` content | `ls do/helpers/ scripts/R/utils/` |
| LaTeX preamble / commands | `paper/preamble.tex` or `\input` chain | `grep -nE '\\\\newcommand\\\|\\\\DeclareMathOperator' paper/*.tex preambles/*.{tex,sty}` |

If derivation truly fails — the entity doesn't exist anywhere in the repo and no analogous existing pattern can be mirrored — explicitly disclose: "Creating a new convention here because no existing pattern was found in [files searched]." Never silently fabricate.

---

## Citation requirement

When generating code that references a derived entity, name the source. Two acceptable formats:

- **In the agent's response or session log** (preferred): `"Path from do/settings.do:12"`, `"Variable from do/01_clean_demographics.do:47 (label: Female student)"`, `"Output convention mirrored from do/figures/fig01_main.do save block at line 34"`.
- **As a code comment** (only when natural): `// from settings.do:12` next to a usage. Optional; the citation in the response is the load-bearing record.

The user can audit by asking "where did you get that path from?" and the agent must point at a line in a tracked file. Citation requirement applies to *each external entity referenced*, not just one citation per script.

---

## Examples

### Bad — fabrication

User: "Write a codebook script for the cleaned dataset."

Agent (without this rule): Generates `use "data/cleaned/main.dta"` and proceeds. Path is fabricated; code fails on first run because the project uses `$csacclndatadir/main_v3.dta`.

### Good — derivation

User: "Write a codebook script for the cleaned dataset."

Agent (with this rule): Runs `grep -nE 'global ' do/settings.do` first. Finds `global csacclndatadir = "..."` and `use "$csacclndatadir/main_v3.dta"` in `do/02_analyze.do:8`. Generates the codebook script using the same global. Cites: "Path derived from do/settings.do:14 + do/02_analyze.do:8."

### Bad — variable fabrication

Agent (without this rule): `gen female = (gender == "F")` — guesses `gender` is a string variable.

### Good — derivation

Agent (with this rule): `grep -nE 'gender' do/01_clean*.do` first. Finds `gen female = (gender_id == 2)` already in `do/01_clean_demographics.do:23` (variable name and coding both inferred from existing code). Either reuses that variable or, if creating a new one, mirrors the convention.

### Bad — output-path fabrication

Agent (without this rule): `esttab using "output/table1.tex"` — fabricates `output/` dir.

### Good — derivation

Agent (with this rule): `grep -nE 'esttab' do/*.do` first. Finds existing pattern `esttab using "tab/01_main.tex"`. Mirrors: `esttab using "tab/05_codebook.tex"`.

---

## Cross-references

- `no-assumptions.md` — same epistemic stance, but for user-side facts
- `primary-source-first.md` — same stance, but for external paper citations
- `adversarial-default.md` — same stance, but for compliance claims (which are also a kind of fabrication when made without evidence)

When in doubt about which rule applies: think about the *source of truth* for the fact in question. Is it the user's stated requirement (no-assumptions)? An external paper (primary-source-first)? A compliance check (adversarial-default)? Or a fact already encoded in the repo (this rule)?
