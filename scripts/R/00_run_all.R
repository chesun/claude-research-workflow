# =============================================================================
# 00_run_all.R — Orchestrator. Run this, not the individual scripts.
#
# Reproducibility contract (enforced by /review-r and /audit-reproducibility):
#   - Fixed seed set below.
#   - Project root resolved via here::here() — no setwd().
#   - Every package loaded under a renv (or DESCRIPTION) lockfile.
#   - Outputs written to scripts/R/_outputs/ and listed at the end.
#   - sessionInfo() captured so reviewers can verify the environment.
# =============================================================================

# ---- Bootstrap -------------------------------------------------------------
suppressPackageStartupMessages({
  if (!requireNamespace("here", quietly = TRUE)) {
    stop("Install 'here' first: install.packages('here')")
  }
  library(here)
})

# Seed applies to everything downstream. Change ONLY with a reason in the
# session log — this is load-bearing for identical numerical outputs.
PROJECT_SEED <- 20260413L
set.seed(PROJECT_SEED)

# Output directory (create if missing; treat as ephemeral).
OUT_DIR <- here("scripts", "R", "_outputs")
dir.create(OUT_DIR, showWarnings = FALSE, recursive = TRUE)

# ---- Pipeline --------------------------------------------------------------
# Scripts share state through a single environment. 01_load.R produces
# raw_main, which 02_clean.R consumes; 02 produces df, which 03 consumes;
# 03 writes results.rds, which 04 and 05 read from disk.
pipeline_env <- new.env(parent = globalenv())
# Propagate the orchestrator's seed + OUT_DIR into the shared env so scripts
# can reference them without re-computing.
pipeline_env$PROJECT_SEED <- PROJECT_SEED
pipeline_env$OUT_DIR      <- OUT_DIR

pipeline <- c(
  "01_load.R",
  "02_clean.R",
  "03_analyze.R",
  "04_tables.R",
  "05_figures.R"
)

message("Running reproducibility pipeline with seed ", PROJECT_SEED, "...")

timings <- vapply(pipeline, function(script) {
  path <- here("scripts", "R", script)
  if (!file.exists(path)) {
    stop("Missing pipeline script: ", path)
  }
  start <- Sys.time()
  source(path, local = pipeline_env)
  elapsed <- as.numeric(Sys.time() - start, units = "secs")
  message(sprintf("  %s -> %.2fs", script, elapsed))
  elapsed
}, numeric(1))

# ---- Session capture -------------------------------------------------------
writeLines(
  capture.output(sessionInfo()),
  con = file.path(OUT_DIR, "sessionInfo.txt")
)

# ---- Report ----------------------------------------------------------------
outputs <- list.files(OUT_DIR, full.names = FALSE)
message("")
message("Pipeline complete. Total time: ", sprintf("%.2fs", sum(timings)))
message("Outputs in ", OUT_DIR, ":")
for (f in outputs) message("  - ", f)

invisible(list(timings = timings, outputs = outputs))
