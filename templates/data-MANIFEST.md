# Data Manifest

**Project:** [PROJECT NAME]
**Last updated:** YYYY-MM-DD

A human-readable inventory of every file and directory under `data/`. The companion `PROVENANCE.md` records *where each came from*; this file records *what's in the repo right now and what each piece is for*.

## When to update this file

- A new dataset is added to `data/raw/` or `data/cleaned/` → add a row.
- An existing dataset is removed → mark it as `Removed YYYY-MM-DD` (don't delete the row; history is useful).
- A file's contents materially change (new wave appended, schema changed, etc.) → update the row's "Notes" with a date.

The MANIFEST is committed to git; the actual data files are tracked by DVC (or gitignored). See `.claude/rules/data-version-control.md`.

---

## `data/raw/`

Untouched source data. Never overwrite or edit in place.

| Path | Description | Format | Size | Rows / units | Added | Status |
|---|---|---|---|---|---|---|
| `cps_2024.csv.dvc` | CPS Annual Social and Economic Supplement, 2024 | CSV | ~120 MB | ~150k persons | 2026-04-15 | Active |
| `acs_2018-2022.csv.dvc` | ACS 5-year sample, 2018–2022 | CSV | ~3.2 GB | ~12M persons | 2026-04-20 | Active |
| `tx_district_panel.dta.dvc` | TX school district panel, 2010–2024 | Stata 17 | ~85 MB | ~12k district-years | 2026-03-02 | Active |

## `data/cleaned/`

Outputs of cleaning scripts. Reproducible from `data/raw/` + scripts in `scripts/clean/`. Tracked because regeneration is slow.

| Path | Description | Source script | Rows | Generated | Status |
|---|---|---|---|---|---|
| `analysis_sample.dta.dvc` | Main analysis sample after restrictions | `scripts/clean/01_build_sample.do` | ~80k persons | 2026-04-22 | Active |
| `event_study_panel.dta.dvc` | Long-format panel for event-study spec | `scripts/clean/02_build_panel.do` | ~12M person-years | 2026-04-22 | Active |

## `data/external/` (optional — public reference data)

Reference datasets cited in the paper. Often published; may not need DVC tracking if the public source is stable and citeable.

| Path | Description | Source | License | Status |
|---|---|---|---|---|
| `nominatim_places.geojson` | OSM place lookup, US states + counties | nominatim.openstreetmap.org | ODbL | Active |

---

## Notes

- Sizes are approximate; check `du -sh <path>` for current actuals.
- `Status` values: `Active` | `Deprecated YYYY-MM-DD` | `Removed YYYY-MM-DD`.
- For `Deprecated` / `Removed`, also update the `CHANGELOG.md` with the reason.
- Keep this manifest *terse*. Long descriptions go in `PROVENANCE.md`.
