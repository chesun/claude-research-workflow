---
name: compile-latex
description: Compile LaTeX documents (papers or talks) with 3 passes + bibtex. Reads CLAUDE.md for engine choice (pdflatex default for papers, configurable for talks).
argument-hint: "[filename without .tex] [--paper | --talk]"
allowed-tools: ["Read", "Bash", "Glob"]
---

# Compile LaTeX

Compile a LaTeX document with full citation resolution.

## Steps

1. **Read CLAUDE.md** for engine choice and directory structure. Default: pdflatex for papers.

2. **Detect mode** from arguments or file location:
   - `--paper` or file in `paper/`: compile as paper
   - `--talk` or file in `talks/`: compile as talk
   - No flag: infer from file path

3. **Compile with 3-pass sequence:**

### Paper Mode (pdflatex)
```bash
cd Paper
pdflatex -interaction=nonstopmode $ARGUMENTS.tex
BIBINPUTS=..:$BIBINPUTS bibtex $ARGUMENTS
pdflatex -interaction=nonstopmode $ARGUMENTS.tex
pdflatex -interaction=nonstopmode $ARGUMENTS.tex
```

### Talk Mode (pdflatex with preambles)
```bash
cd Talks
TEXINPUTS=../Preambles:$TEXINPUTS pdflatex -interaction=nonstopmode $ARGUMENTS.tex
BIBINPUTS=..:$BIBINPUTS bibtex $ARGUMENTS
TEXINPUTS=../Preambles:$TEXINPUTS pdflatex -interaction=nonstopmode $ARGUMENTS.tex
TEXINPUTS=../Preambles:$TEXINPUTS pdflatex -interaction=nonstopmode $ARGUMENTS.tex
```

4. **Check for warnings:**
   - Grep output for `Overfull \\hbox` warnings
   - Grep for `undefined citations` or `Label(s) may have changed`
   - Report any issues found

5. **Open the PDF** for visual verification:
   ```bash
   open [dir]/$ARGUMENTS.pdf          # macOS
   ```

6. **Report results:**
   - Compilation success/failure
   - Number of overfull hbox warnings
   - Any undefined citations
   - PDF page count

## Why 3 passes?
1. First pass: Creates `.aux` file with citation keys
2. bibtex: Reads `.aux`, generates `.bbl` with formatted references
3. Second pass: Incorporates bibliography
4. Third pass: Resolves all cross-references with final page numbers

## Important
- Read CLAUDE.md for engine choice — default is **pdflatex** for applied micro projects
- **TEXINPUTS** needed for talks if preambles are in separate directory
- **BIBINPUTS** needed if `.bib` file is not in the same directory
