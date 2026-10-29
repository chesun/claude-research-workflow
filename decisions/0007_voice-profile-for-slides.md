# 0007: Voice profile for slides: a separate slide profile from the author's own decks

- **Date:** 2026-10-29
- **Status:** Decided
- **Scope:** Methodology / writing
- **Data quality:** Full context
- **Supersedes:** #0006, item 6's papers-only scope (the rest of ADR-0006 stands)

## Context

ADR-0006 limited the author's voice profile to papers: `/humanize` used it "only for papers", and slides got no profile. The reason was register. The profile records prose habits (sentence rhythm, paragraph openings, hedging), and pushing those onto slides would make decks read like paper text. On 2026-10-29 the owner asked why slides were excluded, and offered decks they made themselves ("most of my decks are made by me entirely").

## Decision

1. **A separate slide profile,** `slides.md`, in the same private folder and repo as `profile.md` (ADR-0006 item 1). It is built only from the author's own decks, each with a provenance declaration as for papers.
2. **Its own schema:**
   - Titles (claim or topic, length);
   - Bullets (fragments or sentences, count, length);
   - Openings;
   - Results (how a finding is shown);
   - Math and figures;
   - Quirks.

   Rhythm is measured per slide and per bullet. Qualification needs 3 or more decks, or, with fewer, recurrence across a deck's parts, marked provisional.
3. **One profile per register.** Papers use `profile.md` and slides use `slides.md`. Neither stands in for the other, and docs, blog and correspondence get none.
4. **The same bounds as ADR-0006.** The same carve-out list and floor apply (on slides, tricolons stay a hard cap), and so does the privacy rule. Voice stays advisory: `storyteller` writes toward the profile, `storyteller-critic` reports conformance beside its advisory talk score, and `/humanize` spares only what the profile spares.

## Consequences

- `/voice-profile build` takes `--slides`, and extracts the text of Beamer, PDF and PowerPoint decks. PowerPoint uses a throwaway stdlib script; PowerPoint originals are gitignored in the private repo.
- `/talk` resolves the slide profile's path for `storyteller-critic`, which has no shell. `storyteller` resolves it itself.
- The slide profile waits for the owner's decks. Until then, decks are built as before, with "Voice: no profile" reported.

## Sources

- `decisions/0006_voice-preservation.md` :: Decision, item 6
- `.claude/references/voice-profile.md` :: § Slide-profile schema
- `quality_reports/plans/2026-10-29_voice-preservation.md` :: addendum (slides)
