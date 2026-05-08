# Stata Documentation Lookup

The Stata manuals are large PDFs. Never read them whole. Use `pdfgrep` to search and `pdfplumber` to extract only the relevant pages.

The docs directory below (`~/Documents/stata/docs/`) is the Stata 17 manual set on this machine — the version invoked by `stata17`. Do not look up commands in `/Applications/Stata/docs/` (older Stata 14 install).

## Prerequisites
```bash
brew install pdfgrep        # PDF search
pip3 install pdfplumber     # PDF page extraction
```

## Workflow: Look Up a Stata Command

### Step 1 — Find which manual covers it
```bash
DOCS=~/Documents/stata/docs
pdfgrep -i -l "reghdfe" $DOCS/*.pdf
```

### Step 2 — Find the page numbers
```bash
pdfgrep -i -n "^reghdfe" $DOCS/r.pdf | head -20
# -n prints page numbers; anchor with ^ to find command entries, not just mentions
```

### Step 3 — Extract those pages as text
```bash
python3 -c "
import os, pdfplumber
path = os.path.expanduser('~/Documents/stata/docs/r.pdf')
with pdfplumber.open(path) as pdf:
    for i in range(411, 418):
        print(pdf.pages[i].extract_text())
"
```

## Quick Single-Step Search
```bash
# Search all manuals at once, show surrounding context
pdfgrep -i -C 3 "vce(cluster" ~/Documents/stata/docs/r.pdf
```

## Manual-to-Topic Cheat Sheet

| Topic | Manual |
|-------|--------|
| General commands | `r.pdf` |
| Programming / macros / loops | `p.pdf` |
| Graphics | `g.pdf` |
| Data management | `d.pdf` |
| Panel / longitudinal | `xt.pdf` |
| Mixed-effects / multilevel | `me.pdf` |
| Time series | `ts.pdf` |
| Multiple imputation | `mi.pdf` |
| Mata | `m.pdf` |
| Functions | `fn.pdf` |
| Bayesian analysis | `bayes.pdf` |
| User's Guide (fundamentals) | `u.pdf` |
| Getting Started (Mac) | `gsm.pdf` |
