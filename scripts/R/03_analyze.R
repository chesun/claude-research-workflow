# =============================================================================
# 03_analyze.R — Regressions, tests, model fits. Save everything to RDS.
#
# Persist fitted objects to `_outputs/*.rds` so 04_tables.R and 05_figures.R
# don't have to refit. Keeps the downstream steps fast and deterministic.
# =============================================================================

if (!exists("df")) {
  stop("03_analyze.R: df not found. Run 00_run_all.R, not this script directly.")
}

# ---- Primary specification -------------------------------------------------
fit_main <- lm(delta ~ treated, data = df)

# ---- Persist for downstream scripts ---------------------------------------
results_path <- file.path(OUT_DIR, "results.rds")
saveRDS(
  list(
    fit_main = fit_main,
    n        = nrow(df),
    seed     = PROJECT_SEED
  ),
  file = results_path
)

message("Saved analysis results to ", results_path)
