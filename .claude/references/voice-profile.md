# Voice profile — schema, carve-outs and floor (ADR-0006)

The author's voice profile says what *this author* does. `anti-ai-prose.md` stays subtractive: it is what AI prose does. This file is the single home of the profile's schema, its qualification rule, the carve-outs a profile may use and the floor it can never switch off. ADR-0006 records the decision; `/voice-profile` builds and audits the profile.

## Where the profile lives

- **The path is `<home>/.claude/voice/`,** where `<home>` is the user's home directory (`%USERPROFILE%` on Windows, `$HOME` on macOS).
  - The folder is a clone of the author's **private** git repo (for this template's owner, `chesun/voice-profile`), cloned to that path on each machine. So it is durable, versioned and portable, and no project repo carries it.
  - Never make that repo public, and never copy its contents into another repo.
- **Resolve it** in a shell: `py -I -c "import pathlib; print(pathlib.Path.home())"` on Windows, or the same with `python3 -I` on macOS. Then join `.claude/voice/profile.md`.
- **The repo tracks:**
  - `profile.md`: the author's voice;
  - `style-models.md`: the structure taken from other authors' papers;
  - `notes/`: one note per source document;
  - `sources/*.txt`: text extracts of the sources, enough to rebuild.

  PDFs and Word files are gitignored, and the originals stay where the author keeps them.
- **Who resolves it:**
  - an agent with a shell (`writer`) resolves it itself;
  - `writer-critic` has no shell, so its dispatcher (`/review`) resolves it and passes the absolute path, or "none";
  - the profile is for the `academic` register only (papers). Slides, docs and correspondence never get it.
- **A missing profile is reported, not skipped silently.** An agent that finds no `profile.md` writes "Voice: no profile at <path>" in its report, and the dispatcher passes that line to the user. A profile with an empty `corpus` is reported the same way. With no profile, the agent proceeds as before.

## Privacy rule

**No corpus text, excerpt, exemplar sentence or author-written paragraph goes in any committed file, in any repo.** This covers session logs, reviews, CHANGELOG entries and ADRs.

- Committed records hold verdicts, counts and catalog row IDs only.
- Texts used in a check stay in the session scratch directory or under `<home>/.claude/voice/`, referred to by path.
- A review of a voice-dependent draft quotes the draft (which is the project's own), never the profile's exemplars.

## What qualifies as a trait

A trait goes in the profile only if it recurs:
- **across most of the corpus,** with 3 or more own papers;
- **across most of the paper's sections,** with 1 or 2 papers. The front-matter then says `evidence: within-paper`.
- **Section-type traits:** a trait specific to one section type (introductions, results paragraphs, model sections) carries a `sections:` tag. It qualifies if it recurs across that type's instances.
- **Provisional:** a trait seen in a single section is marked `provisional`. It never enters `carve_out_rows` or the whitelist.

Subject words of the corpus papers never qualify for Lexicon. Their topic is not the author's voice.

**Provenance.** Only text the author declares written without AI help enters the profile. The front-matter records the declaration per source, and the parts used where only some sections qualify. Text the author did not write, or wrote with AI help, is excluded, not down-weighted.

## Profile schema (`profile.md`)

```markdown
---
built: YYYY-MM-DD
corpus:                      # one entry per source document
  - id: <short id>
    file: sources/<file>
    parts: all | <sections the author declared their own>
    provenance: "<author's declaration, e.g. 'own, no AI help'>"
corpus_size: <number of own documents>
evidence: within-paper | across-corpus
measured_by: "<how rhythm was measured, e.g. 'pdftotext + scratch script'> | not measured"
signature_vocab:             # the whitelist /humanize spares
  - {phrase: "<phrase>", count: "<n>/<N> sections or papers"}
avoid_vocab: ["<word the author never uses>"]
carve_out_rows: []           # only rows from the carve-out list below, each with evidence
rhythm: {median_sentence_words: <n>, iqr: "<a>-<b>", em_dash_per_100_words: <x>}
---

## Lexicon
## Rhythm
## Openings
## Transitions
## Hedging
## Quirks
```

Each section holds a few lines of narrative, each trait with its frequency and any `sections:` tag, then 3–6 verbatim exemplar sentences. Deliberate quirks are labelled `deliberate`, so `/humanize` does not strip them.

## Style-model schema (`style-models.md`)

Other authors' papers inform **structure only**:
- how an introduction states the contribution;
- how a paragraph moves from claim to evidence;
- how a results or figure discussion is built;
- how sections open and close.

A style model has only the sections below. It never adds to Lexicon, Hedging or Quirks, and never feeds `carve_out_rows` or the whitelist. Where it conflicts with the profile, the profile wins.

```markdown
---
built: YYYY-MM-DD
models:
  - id: <short id>
    file: sources/<file>
    author_year: "<author(s), year>"
---

## Openings
## Transitions
## Paragraph structure
```

## Per-document note (`notes/<id>.md`, about 300 words)

One fresh subagent per source document writes it, against the profile schema's six sections, or the style-model schema's three for a style model. Each trait in a note has:
- its count;
- the sections where it recurs, as a `sections:` tag;
- one or two verbatim examples.

The note records which sections it read, and skips any the provenance excludes. The subagent returns only the filename, so the corpus stays out of the main context.

## Carve-outs a profile may use

A profile may spare a catalog flag (`anti-ai-prose.md`) only on these rows, and only with corpus evidence recorded in `carve_out_rows`:

| Row | What the profile may spare | Evidence |
|---|---|---|
| L3 | A field verb the author uses habitually beyond the register carve-out (e.g. `methodology` in the methods-section sense) | qualifies as a trait |
| L4 | Role-assignment `serves as` beyond the register carve-out | qualifies as a trait |
| R4 | The author's single calibrated hedge ("suggests", "consistent with"); a stack of hedges is still flagged | Hedging section |
| S4, S5, T3 | The author's rhythm and structure habits | qualifies as a trait, with `rhythm` measured |
| Whitelist | Phrases in `signature_vocab` | qualifies as a trait |

**A profile cannot add rows to this list.**

## The floor (no profile can switch it off)

S1 (em-dash density), S2 (tricolon overuse), S3 (negative parallelism), M1 (mirror-and-echo openings), L1 (the AI vocabulary core) and C1 (significance inflation); in academic prose, also M3 (decorative emoji or arrows) and M4 ("comprehensive" claims).

A profile touches only the `anti-ai-prose` catalog. It never touches an epistemic check:
- claims against tables;
- identification fidelity;
- numbers derived from outputs;
- citations resolving;
- primary-source reading.

## How each consumer uses the profile

- **`writer`** writes toward the profile when drafting: its rhythm, openings, transitions, hedging and exemplars. It takes structure from the style models. It never breaks the floor, and still runs the humanizer pass.
- **`writer-critic`** adds an advisory "Voice conformance" section. Each finding cites the profile line it departs from. It is reported beside the score and never deducted from it.
- **`/humanize`** on a paper (`academic` register) spares the profile's `carve_out_rows` and `signature_vocab` phrases, and nothing else. This only removes flags, so a re-run stays a no-op.

## Rebuild

Rebuild with `/voice-profile build` when the corpus grows by a paper; the build commits and pushes to the private repo. At 3 own papers, `evidence` becomes `across-corpus` and the qualification rule tightens. `/voice-profile status` reports a profile older than its sources.
