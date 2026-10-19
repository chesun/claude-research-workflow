# Derive, Don't Guess — lookup table and examples

**Class:** A (universal). Pointer-loaded detail for `.claude/rules/derive-dont-guess.md` § Pre-generation derivation checklist: the lookup table and Bad/Good examples (moved from the rule on 2026-10-19); there is no auto-load.

## Lookup table

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

If derivation truly fails, disclose it as the rule requires: "Creating a new convention here because no existing pattern was found in [files searched]."

---

## Examples

### Bad — fabrication

User: "Write a codebook script for the cleaned dataset."

Agent (without `derive-dont-guess`): Generates `use "data/cleaned/main.dta"` and proceeds. Path is fabricated; code fails on first run because the project uses `$csacclndatadir/main_v3.dta`.

### Good — derivation

User: "Write a codebook script for the cleaned dataset."

Agent (with `derive-dont-guess`): Runs `grep -nE 'global ' do/settings.do` first. Finds `global csacclndatadir = "..."` and `use "$csacclndatadir/main_v3.dta"` in `do/02_analyze.do:8`. Generates the codebook script using the same global. Cites: "Path derived from do/settings.do:14 + do/02_analyze.do:8."

### Bad — variable fabrication

Agent (without `derive-dont-guess`): `gen female = (gender == "F")` — guesses `gender` is a string variable.

### Good — derivation

Agent (with `derive-dont-guess`): `grep -nE 'gender' do/01_clean*.do` first. Finds `gen female = (gender_id == 2)` already in `do/01_clean_demographics.do:23` (variable name and coding both inferred from existing code). Either reuses that variable or, if creating a new one, mirrors the convention.

### Bad — output-path fabrication

Agent (without `derive-dont-guess`): `esttab using "output/table1.tex"` — fabricates `output/` dir.

### Good — derivation

Agent (with `derive-dont-guess`): `grep -nE 'esttab' do/*.do` first. Finds existing pattern `esttab using "tab/01_main.tex"`. Mirrors: `esttab using "tab/05_codebook.tex"`.

---

## Pruned hook (history)

(The former opt-in blocking variant `derive-check-block.py` was pruned 2026-09-16; the advisory check `.claude/hooks/derive-check-advisory.py` is retained.)
