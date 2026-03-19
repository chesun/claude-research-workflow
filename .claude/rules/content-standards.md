---
paths:
  - "**/*.R"
  - "**/*.tex"
  - "tables/**"
  - "master_supporting_docs/**"
  - "explorations/**"
---

# Content Standards: Tables, Figures, PDFs, and Explorations

---

## 1. Table Standards

**Target:** Publication-quality tables matching AER, QJE, and Econometrica formatting.

### No In-Table Titles or Notes

- **Never** embed titles inside the table body or as a table header row
- **Never** embed notes, sources, or footnotes inside the table itself
- Table numbering, titles, and notes are added in LaTeX via `\caption{}` and `\begin{tablenotes}`
- The file name and folder identify what the table contains

### Three-Line Format (Booktabs)

Every table uses exactly three horizontal rules and **zero vertical lines**:

```latex
\begin{table}[htbp]
\centering
\begin{tabular}{lcccc}
\toprule
            & (1)     & (2)     & (3)     & (4)     \\
\midrule
...coefficients...
\bottomrule
\end{tabular}
\end{table}
```

- `\toprule` above column headers
- `\midrule` below column headers (and to separate panels)
- `\bottomrule` at the very end
- `\cmidrule(lr){2-4}` for partial rules spanning column groups
- **Never** use `\hline`, `|`, or any vertical rules

### Coefficient Display

- Point estimates on one row, standard errors in parentheses on the row below
- Stars for significance: `*` p < 0.10, `**` p < 0.05, `***` p < 0.01
- Align significance note at the bottom: `\textit{Notes:} * p < 0.10, ** p < 0.05, *** p < 0.01`
- Standard errors labeled in the note (e.g., "Robust standard errors in parentheses" or "Clustered at municipality level")

```
Treatment        & 0.045**  & 0.038*   & 0.052*** \\
                 & (0.021)  & (0.020)  & (0.019)  \\
```

### Column and Row Structure

- **Column (1), (2), ...** headers in the first row after `\toprule`
- **Dependent variable** stated in a spanning header or the first subheader row
- **Variable names** left-aligned, human-readable (not raw R variable names)
  - `Log wages` not `ln_wage_deflated`
  - `Female` not `sex_2`
  - `Years of education` not `educ_yrs`
- **Numeric columns** right-aligned or decimal-aligned
- **N**, **R²**, **Fixed effects** (Yes/No), **Controls** (Yes/No) at the bottom before `\bottomrule`

### Panel Structure

For tables with multiple panels:

```latex
\multicolumn{5}{l}{\textit{Panel A: Full sample}} \\
\midrule
...
\\[0.5em]
\multicolumn{5}{l}{\textit{Panel B: Male workers}} \\
\midrule
...
```

- Panel labels in italics, left-aligned, spanning all columns
- `\midrule` after each panel label
- Small vertical space (`\\[0.5em]`) between panels

### Preferred R Packages

**Primary: `modelsummary`**

```r
library(modelsummary)

modelsummary(
  models,
  output   = "latex_tabular",  # bare tabular, no wrapper
  stars    = c("*" = 0.10, "**" = 0.05, "***" = 0.01),
  coef_rename = c(
    "treatment"  = "Treatment",
    "log_income" = "Log income"
  ),
  gof_map = c("nobs", "r.squared", "adj.r.squared"),
  escape  = FALSE
)
```

**Alternative: `fixest::etable`**

```r
fixest::etable(
  models,
  tex      = TRUE,
  style.tex = style.tex(
    main     = "aer",
    depvar.title = "",
    fixef.title  = "",
    yesNo    = c("Yes", "No")
  ),
  se.below = TRUE,
  signif.code = c("***" = 0.01, "**" = 0.05, "*" = 0.10)
)
```

**For summary / descriptive tables: `kableExtra`**

```r
library(kableExtra)

kbl(df, format = "latex", booktabs = TRUE, escape = FALSE,
    align = c("l", rep("c", ncol(df) - 1))) |>
  kable_styling(latex_options = "hold_position")
```

### Typography

- Serif font throughout (inherits from document class — no extra commands needed)
- `\small` or `\footnotesize` for tables that need to fit within column width
- Variable names in plain text, panel labels in `\textit{}`
- Never bold table body content; bold only for rare emphasis in headers

### Export

```r
# Write .tex fragment (no \begin{table} wrapper -- added in main.tex)
writeLines(tex_output, file.path("paper/tables", "reg_main_specification.tex"))
writeLines(tex_output, file.path("results/tables", "reg_main_specification.tex"))
```

- Output **bare `tabular` environment** (no `\begin{table}` float)
- The paper's `main.tex` wraps it with `\begin{table}`, `\caption{}`, and `\input{}`
- Always write to both `paper/tables/` and `results/tables/`

### File Naming

```
tables/
├── descriptive/
│   ├── sumstats_main_sample.tex
│   └── balance_treatment_control.tex
├── estimation/
│   ├── reg_main_specification.tex
│   ├── reg_heterogeneity_gender.tex
│   └── did_event_study_coefficients.tex
└── robustness/
    └── reg_alternative_controls.tex
```

Pattern: `{table_type}_{content_description}.tex`

- `sumstats_` for summary statistics
- `balance_` for balance / pre-treatment tests
- `reg_` for regression output
- `did_` for difference-in-differences specific tables
- `first_stage_` for IV first stage

### Prohibited Patterns

| Pattern | Reason |
|---------|--------|
| Title row inside the table | Titles go in `\caption{}`, not the table body |
| Notes embedded in table body | Notes go below via `\begin{tablenotes}` |
| `\hline` | Use `\toprule` / `\midrule` / `\bottomrule` (booktabs) |
| Vertical rules (`\|` in column spec) | Never used in economics journals |
| `stargazer` package | Deprecated workflow; use `modelsummary` or `fixest::etable` |
| Raw variable names in labels | Human-readable labels required |
| `xtable` without booktabs | Produces non-journal-quality output |
| `\begin{table}` in R output | R exports bare `tabular`; float wrapper lives in `main.tex` |

---

## 2. PDF Processing

### The Safe Processing Workflow

**Step 1: Receive PDF Upload**
- User uploads PDF to `master_supporting_docs/supporting_papers/` or `supporting_slides/`
- Claude DOES NOT attempt to read it directly

**Step 2: Check PDF Properties**
```bash
pdfinfo paper_name.pdf | grep "Pages:"
ls -lh paper_name.pdf
```

**Step 3: Create Subfolder and Split**
```bash
mkdir -p paper_name/

for i in {0..9}; do
  start=$((i*5 + 1))
  end=$(((i+1)*5))
  gs -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dSAFER \
     -dFirstPage=$start -dLastPage=$end \
     -sOutputFile="paper_name/paper_name_p$(printf '%03d' $start)-$(printf '%03d' $end).pdf" \
     paper_name.pdf 2>/dev/null
done
```

**Step 4: Process Chunks Intelligently**
- Read chunks ONE AT A TIME using the Read tool
- Extract key information from each chunk
- Build understanding progressively
- Don't try to hold all chunks in working memory

**Step 5: Selective Deep Reading**
- After scanning all chunks, identify the most relevant sections
- Only read those sections in detail for slide development
- Skip appendices, references, or less relevant sections unless needed

### Error Handling Protocol

**If a chunk fails to process:**
1. Note the problematic chunk (e.g., "Chunk p021-025 failed")
2. Try splitting into 1-2 page pieces
3. If still failing, skip and document the gap

**If splitting fails:**
1. Check if Ghostscript is installed: `gs --version`
2. Try alternative: `pdftk paper.pdf burst output paper_%03d.pdf`
3. If all else fails, ask user to upload specific page ranges manually

**If memory/token issues persist:**
1. Process only 2-3 chunks per session
2. Focus on specific sections user identifies as most important

---

## 3. Exploration Folder Protocol

**All experimental work goes into `explorations/` first.** Never directly into production folders.

### Folder Structure

```
explorations/
├── ACTIVE_PROJECTS.md
├── [project]/
│   ├── README.md          # Goal, status, findings
│   ├── R/                 # Code (use _v1, _v2 for iterations)
│   ├── scripts/           # Test scripts
│   ├── output/            # Results
│   └── SESSION_LOG.md     # Progress notes
└── ARCHIVE/
    ├── completed_[project]/
    └── abandoned_[project]/
```

### Lifecycle

1. **Create** — `mkdir -p explorations/[name]/{R,scripts,output}` + README from `templates/exploration-readme.md`
2. **Develop** — work entirely within the exploration folder
3. **Decide:**

   - **Graduate to production** — copy to `R/`, `scripts/`; requires quality >= 80, tests pass, code clear. Move to `ARCHIVE/completed_[project]/`
   - **Keep exploring** — document next steps in README
   - **Abandon** — move to `ARCHIVE/abandoned_[project]/` with explanation (use `templates/archive-readme.md`)

### Graduate Checklist

- [ ] Quality score >= 80
- [ ] All tests pass
- [ ] Results replicate within tolerance
- [ ] Code is clear without deep context
- [ ] README explains approach and findings

---

## 4. Exploration Fast-Track

**Lightweight workflow for experimental work.** Quality threshold: 60/100 (vs 80 for production). No planning needed.

### Steps

1. **Research value check** — Does this improve the project? If NO, don't build it.
2. **Create folder** — `mkdir -p explorations/[name]/{R,scripts,output}` + README + SESSION_LOG.md
3. **Code immediately** — no plan needed. Must-haves: code runs, results correct, goal documented. Not needed: Roxygen docs, full tests, perfect style.
4. **Log progress** — append 2-3 lines to SESSION_LOG.md as you work
5. **Decision point** — keep exploring, graduate to production (upgrade to 80/100), or archive with brief explanation

### When to Stop (Kill Switch)

At any point: stop, archive with note ("Attempted X, hit blocker Y"), move on. No guilt — exploration is inherently uncertain.
