# =============================================================================
# 04_tables.R — Regression tables → LaTeX.
#
# Reads fitted models from 03_analyze.R, writes publication-ready .tex files
# to _outputs/. Beamer lectures \input these files directly.
# =============================================================================

results_path <- file.path(OUT_DIR, "results.rds")
if (!file.exists(results_path)) {
  stop("04_tables.R: ", results_path, " missing. Run 00_run_all.R first.")
}
results <- readRDS(results_path)

# ---- Minimal base-R LaTeX table --------------------------------------------
# Swap this for modelsummary / fixest::etable / stargazer as your stack prefers.
coefs <- summary(results$fit_main)$coefficients
tex <- c(
  "\\begin{tabular}{lcc}",
  "\\toprule",
  "Term & Estimate & Std. Error \\\\",
  "\\midrule",
  sprintf("%s & %.3f & %.3f \\\\",
          rownames(coefs), coefs[, "Estimate"], coefs[, "Std. Error"]),
  "\\bottomrule",
  "\\end{tabular}"
)

tex_path <- file.path(OUT_DIR, "table_main.tex")
writeLines(tex, con = tex_path)
message("Wrote ", tex_path)
