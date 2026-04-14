# =============================================================================
# 01_load.R — Load raw data. No transformations, no derivations.
#
# This script's only job is to read files into R objects and assign them to
# names that 02_clean.R can pick up. It should be boring and idempotent.
# =============================================================================

# library(readr); library(readxl); library(haven)   # uncomment as needed

# ---- Example: replace with your real load calls ----------------------------
# raw_main <- readr::read_csv(
#   here::here("data", "raw", "main_survey.csv"),
#   show_col_types = FALSE
# )

# Placeholder dataset so the pipeline runs end-to-end on a fresh fork.
# Delete this when you wire up real data.
raw_main <- data.frame(
  id = 1:50,
  treated = rep(c(0, 1), each = 25),
  y_pre   = rnorm(50, mean = 10, sd = 2),
  y_post  = rnorm(50, mean = 10, sd = 2)
)

message("Loaded ", nrow(raw_main), " rows into `raw_main`.")
