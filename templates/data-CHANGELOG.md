# Data Changelog

**Project:** [PROJECT NAME]

Append-only log of substantive changes to data under `data/`. The MANIFEST tells you *what's there now*; this file tells you *how we got here*.

The DVC pointer file (`*.dvc`) for each dataset records the *content* hash of each version; this file records the *reason* a version changed. Together, they let future-you understand both what the data was at a given commit AND why it differs from earlier versions.

## When to write an entry

- New raw dataset added → log it (date, what, why)
- New cleaning step added that changes a derived dataset → log it
- Sample restriction changed → log it (with rationale)
- A dataset is replaced or extended (new wave, schema change, vendor switch) → log it
- A bug in cleaning is found and fixed → log it (this is a data-version change!)

## Format

Each entry: dated heading + bullet list. Reverse-chronological (newest at top).

---

## 2026-04-22 — Built initial event-study panel

- **What:** Created `data/cleaned/event_study_panel.dta` from `data/raw/cps_2024.csv` and `data/raw/tx_district_panel.dta` via `scripts/clean/02_build_panel.do`.
- **Why:** Need long-format panel for the staggered DiD spec in the paper draft.
- **Sample restrictions applied:** Workers aged 25–64; non-institutional population; states with at least 5 years of pre-treatment data.
- **DVC version:** committed in git as `<commit hash>`; data hash recorded in `data/cleaned/event_study_panel.dta.dvc`.

## 2026-04-22 — Built analysis sample

- **What:** Created `data/cleaned/analysis_sample.dta` from `data/raw/cps_2024.csv` via `scripts/clean/01_build_sample.do`.
- **Why:** Initial cut of analysis sample for descriptive tables.
- **Sample restrictions:** Same as event-study panel; further restricted to workers with non-missing wages.

## 2026-04-20 — Added ACS 5-year sample

- **What:** Pulled `data/raw/acs_2018-2022.csv` from IPUMS USA. See `PROVENANCE.md`.
- **Why:** Expanding from CPS-only to ACS+CPS to address referee point about smaller-state cells.

## 2026-04-15 — Initial CPS extract

- **What:** Pulled `data/raw/cps_2024.csv` from IPUMS CPS. See `PROVENANCE.md`.
- **Why:** Initial data for the project.

## 2026-03-02 — Initial TX district panel

- **What:** Received `data/raw/tx_district_panel.dta` from TERC. See `PROVENANCE.md` for access agreement details.
- **Why:** Primary data for the TX project.

---

## How this differs from git log

`git log -- data/` shows when DVC pointers changed. This file explains *why* — the rationale that won't be in a one-line commit message.

When in doubt, write here. Future-you with no recall of 2026-decisions cannot reverse-engineer rationales from pointer hashes.
