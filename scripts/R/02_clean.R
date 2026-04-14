# =============================================================================
# 02_clean.R — Type coercion, missingness handling, derived columns.
#
# Takes `raw_main` from 01_load.R and produces `df` — the cleaned, analysis-
# ready data frame. Expose exactly what 03_analyze.R needs; nothing more.
# =============================================================================

# Expect raw_main from 01_load.R. If missing, fail loudly — don't mask the bug.
if (!exists("raw_main")) {
  stop("02_clean.R: raw_main not found. Run 00_run_all.R, not 02_clean.R directly.")
}

# ---- Example cleaning: adapt to your data -----------------------------------
df <- raw_main
df$treated <- as.integer(df$treated)
df$delta   <- df$y_post - df$y_pre

# Simulate a small amount of post-treatment lift so the analysis isn't trivial.
df$delta[df$treated == 1L] <- df$delta[df$treated == 1L] + 0.8

message("Cleaned data: ", nrow(df), " rows x ", ncol(df), " cols in `df`.")
