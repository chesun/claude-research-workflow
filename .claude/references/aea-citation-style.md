# AEA / Chicago author-date citation style

**Class:** A (universal). Pointer-loaded detail for `.claude/rules/primary-source-first.md` § Citation-style convention (moved from the rule on 2026-10-19); there is no auto-load.

## Citation-style convention (AEA / Chicago author-date)

The project uses the AEA reference style. Per the AER style guide, "Text citations and reference list entries should follow author-date style (see *Chicago Manual of Style*)." AER specifies the et al. threshold; everything else inherits from Chicago author-date. This applies to all in-text citations in load-bearing artifacts: paper, talks, ADRs, plans, reviews, session logs, response letters, and any external-facing prose.

References: https://www.aeaweb.org/journals/aer/style-guide (AER style — et al. thresholds), https://www.aeaweb.org/journals/policies/sample-references (sample reference entries), https://www.aeaweb.org/journals/data/references (data citations).

### In-text citation form

AER explicitly states: "1–4 authors: include all author names" and "5+ authors: list only the name of the first author followed by 'et al.'"

| Authors | Form | Examples |
|---|---|---|
| 1 | `Author (year)` or `(Author year)` | `Smith (2020)`; `(Smith 2020)` |
| 2 | `Author and Author (year)` — never `&`, never comma-separated | `Roth and List (2022)`; `Healy and Leo (2024)`; `(Romer and Romer 2010)` |
| 3 | `Author, Author, and Author (year)` — Oxford comma required | `Gaduh, Hanna, and Olken (2021)`; `Smith, Jones, and Brown (2020)` |
| 4 | `Author, Author, Author, and Author (year)` — all four listed, Oxford comma | `Smith, Jones, Brown, and Lee (2024)` |
| 5+ | `First-author et al. (year)` from first cite onward; reference list shows more (see below) | `Smith et al. (2024)` |
| Same author, same year | suffix-disambiguate with lowercase letter | `Smith (2020a)`, `Smith (2020b)` — order matches the reference list |

### Multiple works in one parenthetical

Use semicolons between works; chronological order within author, alphabetical between authors:

- `(Smith 2020; Jones 2021; Brown 2022)`
- `(Smith 2020a, 2020b; Jones 2021)` — same-author works comma-separated within their cluster

### Punctuation and form details

- Always `and` between names; never `&` in running text. The ampersand belongs in tables and footnotes only when journal style permits, and AEA does not.
- Always include the period in `et al.` (Latin abbreviation requires it).
- Year in parentheses when the author is part of the running sentence (`Smith (2020) shows...`); year inside the parenthetical when the whole citation is parenthetical (`...is shown elsewhere (Smith 2020).`).
- No comma between author and year in the parenthetical form: `(Smith 2020)`, not `(Smith, 2020)`. Chicago author-date omits the author-year comma; this distinguishes it from APA.

### Reference list form (AEA / Chicago)

The reference list itself is rendered by `biblatex` with `style=authoryear` per `working-paper-format.md`. AER specifies: "Reference list entries with one to ten authors should include all author names; for eleven or more authors, list the first seven, followed by a comma and 'et al.'" Note this is laxer than the in-text et al. threshold — the reference list shows up to 10 authors before truncating, while in-text uses et al. at 5+.

Manual reference entries follow Chicago author-date form:

- **Journal article:** `Author, FirstName M., and FirstName M. Author. Year. "Title of Article." Journal Name Volume (Issue): Pages.`
- **Book:** `Author, FirstName M. Year. Title in Italics. City: Publisher.`
- **Working paper:** `Author, FirstName M. Year. "Title." Series Name Working Paper No. NNNN.`
- **Edited volume chapter:** `Author, FirstName M. Year. "Chapter Title." In Volume Title, edited by FirstName M. Editor, pages. City: Publisher.`
- **Dataset:** `Author. Year. Title in Italics, Version. Database. Publisher. URL or DOI (accessed date).`

Authors after the first list given-name first within a single entry: `Smith, John A., Jane Doe, and Mary Roe.` (Oxford comma between Doe and Roe).

### Why this matters for the hook

The Author-Year regex in `primary_source_lib.py` is permissive on the parser side — it still detects `&`-form, comma-form, and various malformed citations so that no real citation slips past the audit. But the writing convention is strict: prose that follows AEA form produces no false positives, never invokes the escape hatch, and ports cleanly to AEA submission without retroactive rewrites. The writer-critic enforces AEA form via deduction rows (see `agents/writer-critic.md`).

### One-author and corporate-author cases

- **Single author:** `Author (year)` or `(Author year)`.
- **Corporate / institutional author:** spell out on first mention, abbreviate thereafter — `(Bureau of Labor Statistics 2024)`, then `(BLS 2024)` with the abbreviation introduced parenthetically on first use.
- **Anonymous / no author:** use a short form of the title in italics — `(Title in Italics 2020)`.
- **Forthcoming:** use `forthcoming` in place of the year — `Smith (forthcoming)`.
