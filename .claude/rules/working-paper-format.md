# Working Paper Format Standard

All LaTeX papers generated or reviewed by this system must conform to the standard economics working paper format. This rule applies to the writer, writer-critic, and verifier agents.

## Document Class and Layout

- `\documentclass[12pt]{article}`
- Margins: 1 inch all sides (`\usepackage[margin=1in]{geometry}`)
- Body text: `\doublespacing`
- References: `\singlespacing`

## Required Packages

At minimum, the preamble must load:
- `geometry` (margins)
- `setspace` (line spacing)
- `amsmath`, `amssymb` (math)
- `graphicx` (figures)
- `natbib` with `authoryear,round` (citations)
- `hyperref` with `colorlinks=true` (links)
- `booktabs` (professional tables)
- `threeparttable` (table notes)
- `titling` (title page font control)

## Title Font Sizes

Use `titling` package to set proper sizes — the default article class title is too large:

```latex
\usepackage{titling}
\pretitle{\begin{center}\large\bfseries}
\posttitle{\end{center}}
\preauthor{\begin{center}\normalsize}
\postauthor{\end{center}}
\predate{\begin{center}\normalsize}
\postdate{\end{center}}
```

- Title: `\large` (14pt at 12pt base) with bold — NOT the default `\Large` (17pt)
- Authors: `\normalsize` (12pt)
- Date: `\normalsize` (12pt)

## Title Page Format

```latex
\title{Paper Title\thanks{Acknowledgments footnote.}}

\author{
Author One\thanks{Affiliation and email.} \quad
Author Two\thanks{Affiliation.} \quad
Author Three\thanks{Affiliation.}
}

\date{\today}
```

Rules:
- Do NOT wrap title in `\textbf{}` — `\maketitle` already bolds it
- Do NOT use `\and` for authors — use `\quad` spacing on a single line
- Do NOT repeat university name under each author — affiliations go in `\thanks{}` footnotes only
- Suppress page number on title page: `\thispagestyle{empty}`
- Reset page counter after title page: `\newpage \setcounter{page}{1}`

## Abstract and Metadata

```latex
\begin{abstract}
\noindent \singlespacing
Abstract text here.
\end{abstract}

\vspace{1em}
\noindent \textbf{JEL Codes:} X00, Y00

\vspace{0.5em}
\noindent \textbf{Keywords:} keyword one, keyword two
```

- Abstract must have `\noindent` and `\singlespacing` (body is double-spaced but abstract is always single-spaced)
- Abstract should be 150 words or fewer to fit on the title page with authors and metadata
- JEL codes and keywords follow the abstract, not inside it
- The entire title page (title, authors, abstract, JEL, keywords) must fit on one page — if it overflows, shorten the abstract

## Section Structure

Standard economics paper order:
1. Introduction
2. Background / Institutional Setting (if needed)
3. Literature Review (or combined with Introduction)
4. Data
5. Empirical Strategy / Methodology
6. Results
7. Discussion (if separate from Results)
8. Robustness (if separate section)
9. Conclusion

Each section uses `\section{}` with `\label{sec:name}`. Subsections use `\subsection{}`.

## Tables and Figures

- Tables and figures may be placed inline (modern standard) or collected after references (traditional)
- Use `\begin{threeparttable}` for tables with notes
- Table notes use the project's `\tablenote{}` command
- Figures include a `\begin{minipage}` notes block with `\footnotesize \textit{Notes.}`
- Use `booktabs` rules (`\toprule`, `\midrule`, `\bottomrule`) — never `\hline`

## Bibliography

```latex
\newpage
\singlespacing
\bibliographystyle{aer}
\bibliography{../Bibliography_base}
```

- `aer` bibliography style (or journal-specific style if targeting a specific journal)
- Single-spaced references
- New page before references

## What the Writer-Critic Checks

The writer-critic deducts points for:
- Wrong document class or font size (-5)
- Missing `\doublespacing` in body (-5)
- `\textbf{}` wrapping `\title{}` (-3)
- `\and` between authors instead of `\quad` (-3)
- Repeated affiliation text outside `\thanks{}` (-3)
- Missing JEL codes or keywords (-5)
- `\hline` instead of `booktabs` rules (-3)
- Missing table notes on any table (-5)
- Missing figure notes on any figure (-5)
