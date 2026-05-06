# Data Provenance

**Project:** [PROJECT NAME]
**Last updated:** YYYY-MM-DD

Where each dataset under `data/` came from: source institution, license, access path, who collected, when, and any access restrictions.

This is the file your future self will thank you for in 2029 when you can't remember whether the TX panel came from TEA or TERC.

## When to update this file

- A new dataset is added → write a full provenance entry (source, license, who, when, access path).
- A dataset's source changes (e.g., switched from public ACS to restricted ACS) → add a new entry with the change date; don't edit the old one (history is what makes provenance trustworthy).
- A dataset's license terms change → flag and add a new entry.

---

## `data/raw/cps_2024.csv`

- **Source:** IPUMS CPS Annual Social and Economic Supplement
- **URL / DOI:** https://cps.ipums.org/cps/ (DOI: 10.18128/D030.V11.0)
- **License:** IPUMS terms (free for research; cite per IPUMS guidelines)
- **Access:** Downloaded by Christina via IPUMS extract builder, 2026-04-15
- **Variables selected:** AGE, SEX, RACE, HISPAN, EMPSTAT, INCWAGE, EDUC, STATEFIP, MONTH, YEAR
- **Sample restriction in extract:** ASEC supplement only; 2024 calendar year
- **Citation:** Sarah Flood et al. 2024. "Integrated Public Use Microdata Series, Current Population Survey: Version 11.0." Minneapolis, MN: IPUMS.
- **Stored at:** `data/raw/cps_2024.csv` (DVC-tracked; pointer in git)

## `data/raw/acs_2018-2022.csv`

- **Source:** IPUMS USA, ACS 5-year sample
- **URL / DOI:** https://usa.ipums.org/usa/ (DOI: 10.18128/D010.V14.0)
- **License:** IPUMS terms
- **Access:** Downloaded by Christina via IPUMS extract builder, 2026-04-20
- **Variables selected:** [list]
- **Sample restriction in extract:** 2018–2022 5-year ACS, all states
- **Stored at:** `data/raw/acs_2018-2022.csv` (DVC-tracked)

## `data/raw/tx_district_panel.dta`

- **Source:** TERC (Texas Education Research Center) restricted-access via UT Austin
- **URL / DOI:** N/A — restricted-access; provided through TERC data agreement
- **License:** TERC data use agreement (Christina's project ID: [REDACTED])
- **Access restrictions:** PII at the student level. **Do not redistribute outside research team.** Authorized researchers: Christina (PI), [coauthor 1], [coauthor 2]. Aggregated to district-year before storing in this repo.
- **Access:** Provided by TERC liaison [name], 2026-03-02; current data agreement valid through [date]
- **Citation:** Texas Education Research Center. 2024. "Texas Public School District Panel, 2010–2024." Restricted-access dataset. The University of Texas at Austin.
- **Stored at:** `data/raw/tx_district_panel.dta` (DVC-tracked; DVC remote is in PRIVATE Dropbox cache shared only with authorized coauthors)

---

## Notes

- For restricted-access data, ALWAYS document the data agreement, expiration, and authorized-user list. If a coauthor leaves the project, update.
- For public data (IPUMS, FRED, BLS), URL + DOI + access date is enough.
- For data scraped or compiled in-house, document the script and date of scrape.
- License field matters for AEA replication packages. Be specific.

## Audit checklist (run quarterly)

- [ ] Are all current `data/raw/*` files listed here?
- [ ] Are licenses still valid? (Restricted-access agreements expire.)
- [ ] Is the authorized-user list current?
- [ ] Are DOIs / URLs still resolvable?
