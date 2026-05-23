# Stata Comment-Bug Fleet Preview (Read-Only)

**Date:** 2026-05-23
**Method:** Field-guide §3 grep commands against all 7 consumers (purely read-only — no `--fix`, no in-place mutation, no writes to any consumer repo)
**Purpose:** Validate the universal-fix plan baseline before any code commits.
**Plan:** `quality_reports/plans/2026-05-17_stata-comment-bug-universal-fix.md`

---

## belief_distortion_discrimination
**Stata files (.do + .doh):** 134

### Variant 1 — unbalanced `/*` vs `*/` per file

- `analysis/do_files/audit/clean_data.do` — 30 opens / 2 closes
- `analysis/do_files/employer/deg_wtp/new_pilots_may_2025/force20_rerun.do` — 2 opens / 1 closes
- `analysis/do_files/employer/deg_wtp/new_pilots_may_2025/force11_rerun.do` — 2 opens / 1 closes
- `analysis/do_files/employer/deg_wtp/new_pilots_may_2025/voluntary_commit.do` — 5 opens / 4 closes
- `analysis/do_files/employer/deg_wtp/nodrawname/make_draw_data.do` — 6 opens / 3 closes
- `analysis/do_files/employer/deg_wtp/nodrawname/analyze_draw_behavior.do` — 8 opens / 5 closes
- `analysis/do_files/employer/deg_wtp/nodrawname/clean_all.do` — 8 opens / 6 closes

**Total unbalanced files: 7 of 134**

### Variant counts (lines matching)

| Variant | Count |
|---|---:|
| 2 (`*`-line + /*) | 0 |
| 3 (`//`-line + /*) | 0 |
| 5 (orphan-close candidates) | 119 |
| 6 (`*/` + path-char) | 0 |
| 7 (`//``*` banner) | 39 |
| 8a (`^---<x>$` artifact) | 0 |
| 8b (lone `<x>` artifact) | 0 |

## belief_distortion_discrimination_audit
**Stata files (.do + .doh):** 99

### Variant 1 — unbalanced `/*` vs `*/` per file

- `analysis/do_files/audit/clean_data.do` — 26 opens / 2 closes
- `analysis/do_files/employer/deg_wtp/new_pilots_may_2025/force20_rerun.do` — 2 opens / 1 closes
- `analysis/do_files/employer/deg_wtp/new_pilots_may_2025/force11_rerun.do` — 2 opens / 1 closes
- `analysis/do_files/employer/deg_wtp/new_pilots_may_2025/voluntary_commit.do` — 5 opens / 4 closes
- `analysis/do_files/employer/deg_wtp/nodrawname/make_draw_data.do` — 6 opens / 3 closes
- `analysis/do_files/employer/deg_wtp/nodrawname/analyze_draw_behavior.do` — 8 opens / 5 closes
- `analysis/do_files/employer/deg_wtp/nodrawname/clean_all.do` — 8 opens / 6 closes

**Total unbalanced files: 7 of 99**

### Variant counts (lines matching)

| Variant | Count |
|---|---:|
| 2 (`*`-line + /*) | 0 |
| 3 (`//`-line + /*) | 0 |
| 5 (orphan-close candidates) | 119 |
| 6 (`*/` + path-char) | 0 |
| 7 (`//``*` banner) | 35 |
| 8a (`^---<x>$` artifact) | 0 |
| 8b (lone `<x>` artifact) | 0 |

## bdm_bic
**Stata files (.do + .doh):** 15

### Variant 1 — unbalanced `/*` vs `*/` per file


**Total unbalanced files: 0 of 15**

### Variant counts (lines matching)

| Variant | Count |
|---|---:|
| 2 (`*`-line + /*) | 0 |
| 3 (`//`-line + /*) | 0 |
| 5 (orphan-close candidates) | 14 |
| 6 (`*/` + path-char) | 0 |
| 7 (`//``*` banner) | 0 |
| 8a (`^---<x>$` artifact) | 0 |
| 8b (lone `<x>` artifact) | 0 |

## csac
**Stata files (.do + .doh):** 46

### Variant 1 — unbalanced `/*` vs `*/` per file

- `do/csac_survey_finaid.do` — 31 opens / 32 closes
- `do/resources/DataCleaning.do` — 30 opens / 31 closes
- `do/getting_down_to_facts/gdtf_latex_tables.do` — 1 opens / 2 closes

**Total unbalanced files: 3 of 46**

### Variant counts (lines matching)

| Variant | Count |
|---|---:|
| 2 (`*`-line + /*) | 1 |
| 3 (`//`-line + /*) | 0 |
| 5 (orphan-close candidates) | 63 |
| 6 (`*/` + path-char) | 0 |
| 7 (`//``*` banner) | 0 |
| 8a (`^---<x>$` artifact) | 0 |
| 8b (lone `<x>` artifact) | 0 |

## csac2025
**Stata files (.do + .doh):** 12

### Variant 1 — unbalanced `/*` vs `*/` per file


**Total unbalanced files: 0 of 12**

### Variant counts (lines matching)

| Variant | Count |
|---|---:|
| 2 (`*`-line + /*) | 0 |
| 3 (`//`-line + /*) | 0 |
| 5 (orphan-close candidates) | 11 |
| 6 (`*/` + path-char) | 0 |
| 7 (`//``*` banner) | 0 |
| 8a (`^---<x>$` artifact) | 0 |
| 8b (lone `<x>` artifact) | 0 |

## tx_peer_effects_local
**Stata files (.do + .doh):** 297

### Variant 1 — unbalanced `/*` vs `*/` per file

- `do/generate_codebooks.do` — 14 opens / 0 closes
- `do/server_03_19_2026/cs_do/newtransmat_debug_edit.do` — 10 opens / 11 closes
- `do/server_03_19_2026/cs_do/doall.do` — 3 opens / 1 closes
- `do/server_03_19_2026/cs_do/transitionmatrix.do` — 2 opens / 3 closes
- `do/server_03_19_2026/cs_do/newtransmat_debug.do` — 4 opens / 5 closes
- `do/server_03_19_2026/cs_do/settings.do` — 4 opens / 2 closes
- `do/server_03_19_2026/cs_do/newtransmat.do` — 3 opens / 4 closes
- `do/server_03_19_2026/cs_do/prep_transmat.do` — 3 opens / 4 closes
- `do/server_03_19_2026/main_do/9I_family_checks.do` — 1 opens / 0 closes
- `do/server_03_19_2026/main_do/7C_Regressions_Employment.do` — 6 opens / 5 closes
- `do/server_03_19_2026/main_do/7C_Regressions_SROutcomes.do` — 11 opens / 12 closes
- `do/server_03_19_2026/main_do/1E_Clean_Enrollment_and_SpecialEd_data.do` — 0 opens / 1 closes
- `do/server_03_19_2026/main_do/8B_Replicate_Figlio_Appendix_Figure.do` — 4 opens / 3 closes
- `do/server_03_19_2026/main_do/0A_settings_cs.do` — 3 opens / 1 closes
- `do/server_03_19_2026/main_do/8A_Texas_Heatmaps.do` — 2 opens / 0 closes
- `do/server_03_19_2026/main_do/plot_results.do` — 1 opens / 2 closes
- `do/code_fix/cs_do/newtransmat_debug_edit.do` — 10 opens / 11 closes
- `do/code_fix/cs_do/doall.do` — 3 opens / 1 closes
- `do/code_fix/cs_do/transitionmatrix.do` — 2 opens / 3 closes
- `do/code_fix/cs_do/newtransmat_debug.do` — 4 opens / 5 closes
- `do/code_fix/cs_do/settings.do` — 4 opens / 2 closes
- `do/code_fix/cs_do/newtransmat.do` — 3 opens / 4 closes
- `do/code_fix/cs_do/prep_transmat.do` — 3 opens / 4 closes
- `do/code_fix/main_do/9I_family_checks.do` — 1 opens / 0 closes
- `do/code_fix/main_do/7C_Regressions_Employment.do` — 6 opens / 5 closes
- `do/code_fix/main_do/7C_Regressions_SROutcomes.do` — 11 opens / 12 closes
- `do/code_fix/main_do/1E_Clean_Enrollment_and_SpecialEd_data.do` — 0 opens / 1 closes
- `do/code_fix/main_do/8B_Replicate_Figlio_Appendix_Figure.do` — 4 opens / 3 closes
- `do/code_fix/main_do/0A_settings_cs.do` — 3 opens / 1 closes
- `do/code_fix/main_do/plot_results.do` — 1 opens / 2 closes
- `server_out/170_2026_03_13_cleared_ml/cs_do/newtransmat_debug_edit.do` — 9 opens / 10 closes
- `server_out/170_2026_03_13_cleared_ml/cs_do/doall.do` — 2 opens / 0 closes
- `server_out/170_2026_03_13_cleared_ml/cs_do/transitionmatrix.do` — 1 opens / 2 closes
- `server_out/170_2026_03_13_cleared_ml/cs_do/newtransmat_debug.do` — 3 opens / 4 closes
- `server_out/170_2026_03_13_cleared_ml/cs_do/settings.do` — 3 opens / 1 closes
- `server_out/170_2026_03_13_cleared_ml/cs_do/newtransmat.do` — 2 opens / 3 closes
- `server_out/170_2026_03_13_cleared_ml/cs_do/prep_transmat.do` — 2 opens / 3 closes
- `server_out/170_2026_03_13_cleared_ml/main_do/9I_family_checks.do` — 1 opens / 0 closes
- `server_out/170_2026_03_13_cleared_ml/main_do/7C_Regressions_Employment.do` — 6 opens / 5 closes
- `server_out/170_2026_03_13_cleared_ml/main_do/7C_Regressions_SROutcomes.do` — 11 opens / 12 closes
- `server_out/170_2026_03_13_cleared_ml/main_do/1E_Clean_Enrollment_and_SpecialEd_data.do` — 0 opens / 1 closes
- `server_out/170_2026_03_13_cleared_ml/main_do/8B_Replicate_Figlio_Appendix_Figure.do` — 4 opens / 3 closes
- `server_out/170_2026_03_13_cleared_ml/main_do/0A_settings_cs.do` — 3 opens / 1 closes
- `server_out/170_2026_03_13_cleared_ml/main_do/7H_regression_trans_mat.do` — 3 opens / 2 closes
- `server_out/170_2026_03_13_cleared_ml/main_do/8A_Texas_Heatmaps.do` — 2 opens / 0 closes
- `server_out/170_2026_03_13_cleared_ml/main_do/plot_results.do` — 1 opens / 2 closes

**Total unbalanced files: 46 of 297**

### Variant counts (lines matching)

| Variant | Count |
|---|---:|
| 2 (`*`-line + /*) | 18 |
| 3 (`//`-line + /*) | 0 |
| 5 (orphan-close candidates) | 363 |
| 6 (`*/` + path-char) | 0 |
| 7 (`//``*` banner) | 31 |
| 8a (`^---<x>$` artifact) | 0 |
| 8b (lone `<x>` artifact) | 0 |

## va_consolidated
**Stata files (.do + .doh):** 129

### Variant 1 — unbalanced `/*` vs `*/` per file


**Total unbalanced files: 0 of 129**

### Variant counts (lines matching)

| Variant | Count |
|---|---:|
| 2 (`*`-line + /*) | 0 |
| 3 (`//`-line + /*) | 0 |
| 5 (orphan-close candidates) | 187 |
| 6 (`*/` + path-char) | 0 |
| 7 (`//``*` banner) | 0 |
| 8a (`^---<x>$` artifact) | 0 |
| 8b (lone `<x>` artifact) | 0 |
