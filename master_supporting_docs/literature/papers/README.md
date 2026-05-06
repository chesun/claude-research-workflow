# `master_supporting_docs/literature/papers/` — PDFs go here

This directory is for academic paper PDFs that ground citations in your project's load-bearing artifacts (decisions, plans, reviews, session logs, manuscripts).

## PDFs are gitignored by default

`*.pdf` files in this directory are gitignored in the workflow template, because:

- **Repo size.** PDF libraries grow quickly; tracking them in normal git bloats the repo for forkers who don't need someone else's collection. PDFs don't diff well, so every revision adds full size to history.
- **Per-project decision.** Each fork decides whether the project's PDFs are load-bearing enough to track. If they are, enable Git LFS (see `.claude/rules/data-version-control.md`); the gitignore lines come out and PDFs are tracked via LFS pointers.

If you fork the workflow, populate this directory with PDFs you've collected for the project.

## Naming convention

The `primary-source-first` hook (`.claude/rules/primary-source-first.md`) matches PDFs by surname-and-year stems:

- One author: `Surname_YYYY.pdf`, e.g. `Niederle_2025.pdf` matches stem `niederle_2025`
- Two authors: `Surname1_Surname2_YYYY.pdf`, e.g. `Snowberg_Yariv_2025.pdf` matches stem `snowberg_yariv_2025`
- Three or more: `Surname1_Surname2_Surname3_YYYY.pdf` (or use `et_al`); the hook reads the leading surname(s)
- Subdirectories are searched recursively, so `handbook_2025/Chapter-3_Healy_Leo.pdf` is fine

Trailing descriptive text is allowed: `Niederle_2025_hypothesis_driven_design.pdf` still matches `niederle_2025`.

## Where citations are documented

The workflow documents academic provenance in two places:

1. **Inline in rule files** — e.g., `.claude/rules/experiment-design-principles.md` cites Niederle on hypothesis-driven design, Snowberg and Yariv (2025) on parameter selection, Healy and Leo on IC hierarchy, Gillen 2019 on measurement error, and others. The rule files are the load-bearing source-of-truth for which papers informed which design choices.
2. **In docs** (`docs/` tree, when present) — overlay-specific docs like `docs/getting-started/behavioral.md` point readers at the rule files for the full citation list.

Reading-notes files (one `.md` per cited paper) are NOT required for the public template. They are an optional artifact for users who want to verify or extend the workflow's primary-source grounding. If you do produce reading notes, they live in `master_supporting_docs/literature/reading_notes/`.

## When the hook fires

The `primary-source-first` PreToolUse hook blocks edits to scoped files (`decisions/`, `quality_reports/plans/`, `quality_reports/session_logs/`, `quality_reports/reviews/`, etc.) when those files cite a paper without either (a) a PDF in this directory, or (b) a reading-notes file.

For your own use, you have two paths:

- **Drop the PDF in this directory** with the surname-and-year naming convention above. The hook then allows the citation.
- **Use the escape-hatch comment** for citations that aren't framing claims: `<!-- primary-source-ok: stem -->` in the file or in the assistant message. Suitable for test-case or illustrative citations only.

The hook does not fire on `.claude/rules/`, `.claude/references/`, `docs/`, or other unscoped paths — citations there don't need PDFs or notes (though grounding them in primary sources is still good practice).

See `.claude/rules/primary-source-first.md` for full hook semantics.
