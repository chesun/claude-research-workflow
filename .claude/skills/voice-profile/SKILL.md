---
name: voice-profile
description: Build, audit or check the author's private voice profile (ADR-0006). build reads the author's own papers and slide decks (and other authors' papers as style models) through one fresh subagent per document and writes the profile to ~/.claude/voice/; audit compares a draft with the profile, citing profile lines; status reports a missing or stale profile. Explicit invocation only.
argument-hint: "[build [--own <file>...] [--slides <file>...] [--model <file>...] | audit <draft> | status]"
allowed-tools: Read, Grep, Glob, Write, Bash, Task
disable-model-invocation: true
---

# Voice profile

The schema, the qualification rule, the carve-outs, the floor and the privacy rule are in `.claude/references/voice-profile.md`. Read it first. All paths below are under `<home>/.claude/voice/`; resolve `<home>` as the reference says.

**The privacy rule binds every mode.** No corpus text goes in any committed file; report verdicts, counts and row IDs.

---

## `/voice-profile build [--own <file>...] [--slides <file>...] [--model <file>...]`

Each input type is optional, but give at least one:
- `--own`: the author's own papers, for `profile.md`;
- `--slides`: the author's own decks, for `slides.md` (ADR-0007);
- `--model`: other authors' papers, used for structure only.

A build with only one kind rebuilds only that file.

1. **Provenance.** For each `--own` and `--slides` file, ask the author for:
   - a one-line declaration (for example "own, no AI help");
   - the parts that qualify, if only some sections are theirs alone.

   Record both; a file without a declaration is not used. `--model` files need only the author and year.
2. **Text.** Copy each file into `sources/` (PDF, Word and PowerPoint copies are gitignored), and make a text extract beside it:
   - a `.pdf`: `pdftotext -layout <file> sources/<id>.txt` (TeX Live ships `pdftotext`). For a Beamer deck, clean the extract with a short stdlib script in the session scratch directory (never committed). Pages are separated by form feeds. The script:
     - drops lines repeated on most pages once digits are masked (page numbers, footers);
     - keeps only the last page of an overlay build (a page whose lines are all on the next page);
     - writes each page's first line as `# <title>` and its bullet-glyph lines (`•`, `▶`, `–`) as `- <bullet>`.

     Checked on one of the owner's Beamer decks (2026-10-29): titles were the first line on 53 of 54 pages, only page numbers repeated, and 2 pages were overlay builds;
   - a `.tex` or `.md` (including a Beamer deck): a plain copy;
   - a `.pptx`: the text of each slide, from a short stdlib script (`zipfile` plus `xml.etree`) in the session scratch directory, never committed. The script:
     - takes the presentation order from `p:sldIdLst` in `ppt/presentation.xml`, mapped to slide files through `ppt/_rels/presentation.xml.rels` (the file numbers are not the order once slides are moved);
     - in each slide, writes the shape whose placeholder type is `title` or `ctrTitle` as `# <title>`;
     - writes every other paragraph (`<a:p>`, its `<a:t>` runs joined) as `- <bullet>`, indented by its `lvl` attribute;
     - heads each slide with its position in the deck.

   If `pdftotext` is missing, the subagents read the PDF directly and `measured_by` is `not measured`.

   **Versions.** For decks, measure with a scratch script the share of each deck's lines found verbatim in each other deck. Where it is half or more, the two are versions of one talk, as are decks linked through a chain of such pairs: keep the fullest for steps 3–5 and list the others under its `versions:` (the reference's slide schema).
3. **Notes.** Dispatch one fresh general-purpose subagent per document, in parallel. Each gets:
   - the reference's note schema (the paper schema for an own paper, the slide schema for a deck, the three sections for a style model);
   - its one extract;
   - the parts it may read.

   It writes `notes/<id>.md` and returns only the filename. Do not read the extracts in the main session.
4. **Rhythm.** Measure on the qualifying parts:
   - for own papers, sentence length (median, interquartile range) and em-dashes per 100 words;
   - for decks, words per slide, bullets per slide and words per bullet. Use a short script in the session scratch directory, never committed. Record the method in `measured_by`.
5. **Synthesize.** Read the notes and keep only traits that qualify under the reference's rule. Write:
   - `profile.md` from the own-paper notes, `slides.md` from the deck notes, and `style-models.md` from the style-model notes, each to its schema;
   - `carve_out_rows`, only from the reference's carve-out list, each with its evidence;
   - never a floor row.
6. **Show the author** the profile and ask for approval or corrections. The author is the judge of their own voice. Apply the corrections, and set `built` to today.
7. **Save it.** In `<home>/.claude/voice/`, the private repo:
   - check that the remote is the author's private repo;
   - commit the profiles, the style models, the notes and the text extracts (PDF, Word and PowerPoint originals are gitignored);
   - push.

   If the folder is not a clone of a private repo, stop and tell the author: the profile is not durable until it is.

Report in the conversation: the sources used, the trait counts per section, the carve-out rows and anything marked provisional. Do not quote the profile in any committed file.

## `/voice-profile audit <draft>`

Read-only. Resolve the profile for the draft's register, inferred from its path as `/humanize` does (`talks/**` or a Beamer deck is a deck, `paper/**` a paper; otherwise ask): `profile.md` for a paper, `slides.md` for a deck. If there is none, say so and stop. Compare the draft with each of that profile's six sections. Every finding:
- cites the profile line it departs from;
- quotes the draft passage, which is the project's own text.

Then list the floor rows the draft breaks, as `anti-ai-prose.md` defines them. The report goes in the conversation. If the user asks for a file, write it to `quality_reports/reviews/YYYY-MM-DD_<target>_voice_review.md`, with the standard review header and `**Score:** n/a (advisory)`. Either way it quotes the draft, never the profile's exemplars.

## `/voice-profile status`

Resolve the folder, then report:
- whether it is a git clone with a remote, and any uncommitted or unpushed changes (a profile that is not pushed is not durable);
- whether `profile.md`, `slides.md` and `style-models.md` exist;
- their `built` dates and corpus sizes;
- any file in `sources/` that is not in the front-matter, and any front-matter source that is missing;
- any source newer than `built`.

Suggest a rebuild when a source has been added since the last build.
