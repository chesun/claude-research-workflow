# Derive, Don't Guess

**The principle: if a fact is derivable from the repo, derive it.**

Filepath, variable name, macro, function, package version, output convention, directory structure, config value — any fact that *already exists somewhere in the project* must be looked up, not invented. Inventing facts that the repo has already decided produces code that won't run, references that don't resolve, and silent drift between what Claude writes and what the project uses.

This is the inward-facing twin of `primary-source-first.md`. That rule requires reading the actual paper before citing; this rule requires reading the actual code before referencing repo entities. Same epistemic stance, different artifact type.

---

## Enforcement

For most of this rule's life it had no enforcement mechanism — it was prose the model was expected to internalize, with critic deduction tables (`agents/coder-critic.md`, `agents/writer-critic.md`) that fire *only* when a critic is dispatched inside the orchestrated pipeline. In ad-hoc usage ("just write me this `.do` file") no critic runs, so the rule didn't bind. As of 2026-05-28 the rule has a deterministic trigger, mirroring the hook that gives `primary-source-first.md` its teeth.

- **`.claude/hooks/derive-check-advisory.py`** (PostToolUse, matcher `Write|Edit|MultiEdit`) — **on by default, non-blocking.** After any edit to an analysis/paper file (`.do .doh .R .r .py .tex`), it extracts newly-introduced **read/input** path-literals (`use`/`merge ... using`/`import`/`include` for Stata; `read_*`/`source`/`load` for R; `pd.read_*`/`np.load`/`open` for Python; `\input`/`\includegraphics`/`\addbibresource` for LaTeX) and resolves each against the working tree. A path that does not resolve — or a Stata `$global`/`` `local` `` defined nowhere in the repo — triggers an injected advisory naming the path and pointing back here. Write/output targets (`save`, `export`, `ggsave`, `esttab using`, ...) are never flagged, so non-existent output paths (routine and legitimate) stay silent.
- **`.claude/hooks/derive-check-block.py`** (PreToolUse, matcher `Write|Edit|MultiEdit`) — **opt-in, blocking.** Inert unless `.claude/state/derive-guess-block.enabled` exists. When enabled, blocks the edit only for the highest-confidence guess signal: a newly-added read/input path that doesn't resolve **and** (for Stata macro paths) whose macro is undefined repo-wide. Writes to `.claude/state/derive-guard.log` (append-only JSONL audit trail).

Shared detection logic lives in `.claude/hooks/derive_lib.py` (tested by `.claude/hooks/test_derive_lib.py`).

### What enforcement deliberately does NOT catch

The honest detection limit (same reasoning as the rule's "Citation requirement" below): a *guessed* entity that happens to resolve is byte-identical to a *derived* one, so the hook can only enforce the weaker proposition of **resolvability**, not derivation. It cannot see guessed variable names, function signatures, or runtime-constructed paths — those have no on-disk anchor. The hook is therefore a floor, not a ceiling: the critic deduction tables and the model's own discipline remain load-bearing for everything the hook can't mechanically see.

### Escape hatch

If a referenced read path is intentionally new, built at runtime, or otherwise legitimately absent, add a `derive-ok` comment to the edit:

```
* derive-ok: data/extract_built_at_runtime.dta
```

A bare `<!-- derive-ok -->` (or `// derive-ok`, `# derive-ok`) suppresses all warnings in that edit; a comma list (`derive-ok: a.dta, b.csv`) suppresses only paths containing those substrings. Auditable: `grep -R "derive-ok" scripts/ paper/` surfaces every use.

---

## Where this fits in the epistemic stack

This rule is one of four that together prevent four distinct failure modes of "filling in blanks." The canonical table mapping each rule to its source-of-truth and the failure mode it prevents lives in `no-assumptions.md` (§ "What this rule covers"). In the stack, `derive-dont-guess` is the repo-facing one: it prevents fabricating internal facts (filepaths, variables, configs) when the repo already encodes the answer.

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
