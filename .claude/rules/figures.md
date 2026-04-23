# Figures: Standards and Prohibited Patterns

**Target:** Publication-quality figures matching AER, QJE, Econometrica visual standards.

## Core rules

- **Never add titles or subtitles inside ggplot** — use `labs(title = NULL, subtitle = NULL)`
- **Figure information goes in two places:**
  1. **File name** — descriptive, e.g., `fig1_hispanic_enrollment_ascm.pdf`
  2. **LaTeX `\caption{}`** — the authoritative title, numbered and editable without re-running the plotting script
- **Panel labels are the exception** — "Panel A: Employment" inside multi-panel figures (via `patchwork`, `cowplot`, etc.) is fine since they identify sub-panels, not the whole figure.
- **Axis labels must be publication-quality** — `Employment Rate` not `emp_rate`. Clean labels stay in the figure; titles and context go in the caption.
- **Use serif fonts** — match the paper's body. In ggplot: `theme(text = element_text(family = "serif"))` or `theme_minimal(base_family = "serif")`. Source Serif Pro via `showtext` is a good default.
- **Show all years on x-axis** when the panel spans ~20 years or fewer — use `scale_x_continuous(breaks = min_year:max_year)`. Thin only when labels overlap (>20 ticks).
- **Pair color with linetype/shape/fill** — never color alone. Grayscale-first for print; colorblind-safe palette (≤ 4–5 colors) when needed. `geom_ribbon(alpha = 0.15)` for confidence bands.
- **Export as vector** — `ggsave(..., device = cairo_pdf, bg = "transparent", width = 6.5, height = 4.0, dpi = 300)`. Widths: 6.5 in single-column, 12 in full-width / Beamer. PNG ≥ 300 dpi only for drafts and presentations.

## File naming

Self-documenting through path and filename.

```
figures/
├── descriptive/
│   ├── hist_income_distribution.pdf
│   └── scatter_education_earnings.pdf
├── estimation/
│   ├── coefplot_main_specification.pdf
│   └── event_study_treatment.pdf
└── robustness/
    └── coefplot_alternative_controls.pdf
```

Pattern: `{plot_type}_{variable_or_content}.pdf`

## Prohibited patterns

| Pattern | Reason |
|---------|--------|
| `ggtitle()` | Titles go in `\caption{}`, not the figure |
| `labs(title = ..., caption = ...)` | Same — no in-figure titles or notes |
| `theme_gray()` / `theme_bw()` default | Not journal quality |
| Sans-serif fonts | Journals require serif |
| Rainbow / jet color scales | Not colorblind-safe, not professional |
| 3D effects, excessive decoration | Violates minimalism standard |
| `png()` for final output | Use vector formats (PDF/EPS) for publication |
| Missing `bg = "transparent"` | White boxes on talk slides |
