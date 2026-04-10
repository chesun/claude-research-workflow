# Replication Package Standards (AEA Data Editor)

Reference for replication package requirements. Used by verifier, `/submit audit`, and `/submit package`.

---

## Required Directory Structure

```
replication/
├── README.md                    # Master documentation
├── code/
│   ├── main.do                  # Master script — runs everything
│   ├── settings.do              # Path configuration
│   ├── 01_clean.do              # Data cleaning
│   ├── 02_analysis.do           # Main analysis
│   ├── 03_tables.do             # Table generation
│   ├── 04_figures.do            # Figure generation
│   └── helpers/                 # .doh files and utilities
├── data/
│   ├── raw/                     # Original data (or instructions to obtain)
│   └── cleaned/                 # Processed data (if shareable)
├── output/
│   ├── tables/                  # Generated .tex tables
│   └── figures/                 # Generated .pdf/.png figures
└── logs/                        # Stata log files from full run
```

## README Must Include

1. **Data Availability Statement** — where to obtain each dataset, access requirements, licenses
2. **Computational Requirements** — software versions, packages, hardware, runtime estimate
3. **Instructions** — exact steps to reproduce all results (ideally: "run main.do")
4. **Output Map** — which script produces which table/figure in the paper
5. **Data Citations** — proper citations for all datasets

## For Confidential/Restricted Data (e.g., TERC, FSRDC)

- README explains how to apply for data access
- Code is fully included and documented
- Synthetic or simulated data provided if possible
- Output (tables, figures) included so reviewers can verify format
- Log files from actual run included

## Checklist Before Submission

- [ ] `main.do` runs start-to-finish without manual intervention
- [ ] All file paths are relative (via settings.do globals)
- [ ] All required packages listed with installation commands
- [ ] `set seed` for any randomization
- [ ] Output map: every table/figure traced to a script
- [ ] No absolute paths in code (only in settings.do)
- [ ] Data availability statement present
- [ ] Computational requirements documented
- [ ] Log files demonstrate successful execution
- [ ] README follows AEA template format

## Common Rejection Reasons (AEA Data Editor)

- Missing package dependencies
- Absolute paths in code
- No master script (reviewer must figure out execution order)
- Missing data documentation
- tables/figures don't match paper (wrong version of output)
- No seed set for stochastic results
