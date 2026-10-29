# Voice preservation — build plan

**Status:** APPROVED v2 (owner, 2026-10-29); template part (deliverables 1–6) in build. v1 was reviewed: fit-for-purpose 72/100, efficiency 80/100 (`quality_reports/reviews/2026-10-29_voice-preservation-plan_{fit-for-purpose,efficiency}_review.md`); resolutions are at the end.
**Date:** 2026-10-29
**Design source:** `quality_reports/reviews/2026-09-22_infra-survey_C-voice.md` (survey C), adapted per synthesis `2026-09-22_infra-survey_synthesis.md` § Voice-preservation design and its review (`2026-09-23_infra-survey-synthesis_review.md`, 78/100).
**Prior decisions:** ADR-0002 (review gate), ADR-0003 (`writer` stays on `fable` while this is built; revisit after).

## Goal

The `writer` drafts toward the owner's own academic voice. `writer-critic` reports how far a draft is from it. `/humanize` stops stripping the owner's genuine habits as AI tells. The subtractive catalog (`anti-ai-prose.md`) stays as it is apart from three field-level carve-outs.

## Owner decisions (2026-10-29)

1. **Own-voice corpus** (settled 2026-10-29):
   - **The JMP draft** `belief_distortion_discrimination/draft/sun_draft_july23.pdf` (79 pages, about 23,600 words, dated 24 July 2025): the owner wrote it with ChatGPT help. Only the parts the owner declares their own enter the profile. **Which parts is pending (owner), asked at build time.**
   - **Older unaided writing:** from before ChatGPT (late 2022), which the owner will supply.
   - The two later PDFs (18 September and 28 October 2025) and the 2026 versions (Claude commits in `jmp_paper_overleaf` from 30 April 2026) are not used.
   - The only pre-2022 own text on disk is a one-page funding abstract (`bdm_bic`, November 2021), too short to build from.
2. **Style models:** the owner will add papers by other authors whose writing they admire. This is a new input the survey did not have.
3. **One author profile,** not the survey's two paradigm profiles.
4. **Private:** the filled profile, the notes and the source papers stay out of any public repo. The template ships only the mechanism and the schema.

## Changes to the survey design, and why

| Survey design | This plan | Reason |
|---|---|---|
| Two paradigm profiles in `.claude/references/voice-profiles/`, filled content as Class B on the overlays | One profile at user scope, `<home>/.claude/voice/profile.md`, where `<home>` is `%USERPROFILE%` on Windows and `$HOME` on the Mac. Agents resolve the home directory first, then read the absolute path. | Owner decisions 3–4. The papers live in sibling repos, so a user-scope file is the one place every project can reach. |
| A trait qualifies if it recurs across most of the corpus | With fewer than 3 own papers, a trait qualifies if it recurs across most of the paper's sections. A trait of one section type (how results paragraphs are built) carries a `sections:` tag and qualifies if it recurs across that type's instances; one seen in a single section is marked `provisional`. The front-matter says `evidence: within-paper` until 3 papers. | With one paper, "most of the corpus" is every trait in it. The tag keeps section-type habits rather than averaging them away (survey C:36). |
| (none) | Style models, built from other authors' papers, into `<home>/.claude/voice/style-models.md` with a reduced schema: Openings, Transitions and paragraph structure only, with no Lexicon, Hedging or Quirks. They never feed `carve_out_rows` or the whitelist. Where they conflict with the profile, the profile wins. | Owner decision 2. Another author's habits are not the owner's voice. |
| `voice_feature_lib.py` (Tier-1 feature checks) in v1 | **Deferred to v2.** The trigger is 3 own papers, or a consumer that reads its output. In v1, the build step measures sentence length and em-dash density with a throwaway script in the session scratch directory, on text from `pdftotext` (TeX Live 2026 on this machine). The front-matter records the method, and the script is not committed. | Efficiency review: nothing in v1 consumes it, and gated code costs two reviews and a sync. |
| CLAUDE.md override field | Not added. The default path is the only path, and is written in the reference. | No current user for an override (efficiency review). |

Kept from the survey as is: subtractive and additive stay separate skills sharing one artifact (Q1); bounded supersession, with an enumerated carve-out list keyed to catalog row IDs and a non-supersedable floor (Q2); field carve-outs at register level (Q3); measurement advisory only (Q4); no numeric fingerprinting, no fine-tuning, no detector framing.

## Privacy rule (standing; in ADR-0006 and the reference)

No corpus text, excerpt, exemplar sentence or owner-written paragraph goes in any committed file, in any repo. Committed records (session logs, reviews, CHANGELOG, ADRs) hold verdicts, counts and catalog row IDs only. Any texts used in a check stay in the session scratch directory or under `<home>/.claude/voice/`, and are referred to by path.

## Deliverables

### Template (this repo)

1. **ADR-0006** `decisions/0006_voice-preservation.md`:
   - the owner decisions;
   - the privacy rule;
   - why voice stays advisory;
   - a pointer to the reference for the two lists.

   It stays in this repo: `decisions/**` is excluded from sync (`file-classes.toml:153-154`).
2. **`.claude/references/voice-profile.md`**, the single home of the schema and the lists (lazy-loaded). It holds:
   - the path and how to resolve it;
   - the six categories, and the reduced style-model schema;
   - the per-document note schema, about 300 words, with `sections:` tags;
   - the qualification rule;
   - the profile and style-model skeletons, as fenced blocks with YAML front-matter (`built`, `corpus` with each source's owner-declared provenance, `corpus_size`, `evidence`, `measured_by`, `signature_vocab`, `avoid_vocab`, `carve_out_rows`, `rhythm`) and 3–6 exemplar sentences per section;
   - **the carve-out list** a profile may use: L3 field verbs, L4 role-assignment `serves as`, R4 single calibrated hedge, S4/S5/T3, and a frequency-backed signature-phrase whitelist;
   - **the floor** no profile can switch off: S1, S2, S3, M1, L1, C1, and M3 and M4 in academic prose;
   - the epistemic gates, which are out of scope;
   - the privacy rule;
   - who reads the profile, and how.

   No separate template files.
3. **`.claude/skills/voice-profile/SKILL.md`** (`disable-model-invocation: true`). Modes:
   - `build --own <file>... [--model <file>...]`. The skill:
     - extracts the text with `pdftotext` into `<home>/.claude/voice/sources/`;
     - dispatches one fresh subagent per document, which writes its note to `<home>/.claude/voice/notes/` and returns only the filename;
     - measures rhythm with a scratch script;
     - synthesizes the profile (and the style models from `--model` papers);
     - shows the owner the result to approve.
   - `audit <draft>`: read-only; every finding cites the profile line it departs from.
   - `status`: compares the front-matter corpus with `notes/` and `sources/`, and reports a stale or missing profile.
4. **`.claude/rules/anti-ai-prose.md`** (path-scoped):
   - rename § Voice profiles to **Register profiles** (the `--profile` flag keeps its name);
   - add register-level carve-outs on its own rows: R1 (`Importantly,` / `Notably,` as literature signals, as distinct from filler), L3 (`implement` an experiment or treatment) and L4 (`serves as the control`);
   - add one cross-reference line to the reference.
5. **Agent and skill edits:**
   - `writer.md`: a voice step before drafting. Read the profile if present, write toward it, take structure from the style models, and never break the floor.
   - `writer-critic.md`:
     - an advisory "Voice conformance" section that cites profile lines, reported beside the score and not deducted from it;
     - a carve-out note on Cochrane item 8 (`writer-critic.md:51`), since `implement` an experiment or treatment is field-standard.
   - `storyteller-critic.md:85`: a pointer to the register carve-outs.
   - `humanize/SKILL.md`: read the profile if present, and spare only its `carve_out_rows` and whitelisted phrases, never a floor row. Idempotency is kept, because the profile only suppresses flags.
   - Wording that says "voice profile" for registers is updated in `writer.md:103`, `writer-critic.md:205`, `storyteller-critic.md:85`, `humanize/SKILL.md` and `docs/reference/skills.md:19`.

   Together with item 4, this closes Backlog `TODO.md:43`.
6. **Records:**
   - CLAUDE.md skills-table row and `docs/reference/skills.md` row;
   - CHANGELOG, TODO and a session log (verdicts and counts only).

### Owner's private files (user scope, never committed to a public repo)

7. **`<home>/.claude/voice/`:** `sources/` (the owner's copies of the papers and their text extracts), `notes/`, `profile.md` and `style-models.md`.
   - **Updated 2026-10-29:** the folder is a clone of the private repo `chesun/voice-profile`, created that day. It tracks the profile, the notes and the text extracts; PDFs are gitignored.
   - On the Mac: `git clone` to `~/.claude/voice`.
   - A missing profile is reported, never skipped silently.

## Order of work

1. Owner approves v2 and confirms the corpus.
2. Deliverables 1–6. Reviews:
   - correctness lens on the skill, reference and agent edits;
   - one consistency-and-bloat review of the `anti-ai-prose.md` edit (advisory, `independent-review.md` item 4).
3. Commit and push the template (owner's OK). No gated code, so no receipt is needed.
4. Build the profile from the confirmed corpus, holding out three paragraphs for A4 (below). The owner reads `profile.md` and approves it: the owner is the judge of their own voice. The style models come when the owner supplies papers.
5. Acceptance checks (below).
6. Sync. The consumers (deliverables 4–5) and the skill and reference go to `behavioral`, BDD and `bdm_bic`; bdm_bic has no `paper/`, so the owner decides whether it needs them. The CLAUDE.md row is merged into each consumer's CLAUDE.md by hand (`file-classes.toml:139-147`).

## Acceptance criteria (tier-tagged)

| # | Criterion | Tier | Check |
|---|---|---|---|
| A2 | No committed file holds the owner's prose | 1 | Before each commit of this build: a scratch script samples 20 random 8-word runs from each corpus text and greps the staged diff for them; none found. The privacy rule is the binding control; this is a spot check. |
| A3 | The profile cites a carve-out only from the enumerated list, and never a floor row | 1 | Compare front-matter `carve_out_rows` with the reference's list |
| A4 | The profile tells the owner's prose from AI-assisted prose and from another author's | 3 | Three trials. Each gives a fresh agent only the profile and three unlabelled excerpts in random order: a held-out paragraph of the corpus (excluded from the build); the corresponding passage in a Claude-era JMP version (2026, `jmp_paper_overleaf`); and a paragraph from another author's paper in the same field (a style model or a paper in BDD's literature folder). It ranks them by closeness, citing the profile lines it relies on. **Pass:** the held-out paragraph is ranked first in at least 2 of 3. A miss is reported, not retried until it passes. Excerpts stay in scratch; the session log gets the ranks only. |
| A5 | Drafting with the profile sounds more like the owner | 3 (owner) | Three bullet outlines; the writer drafts each with and without the profile, and the owner sees the pairs in random order. **Pass:** the owner picks the with-profile draft in at least 2 of 3. |
| A6 | `/humanize` keeps whitelisted phrases and still flags the floor | 2 | On an owner paragraph with floor patterns planted (S1, L1, M1), the run keeps each whitelisted phrase and flags each planted row. The texts stay in scratch; the log names the rows. |
| A7 | Nothing blocks: no new hook, no gate | 1 | `git diff --stat` shows no `.claude/hooks/`, `bin/` or `settings.json` change |

## Out of scope

- `bin/voice_features.py`: v2, on the trigger above.
- Merging `econ-writing-skill` into `anti-ai-prose.md`: it stays on the candidate list (a catalog change, not voice).
- A voice for slides: the register carve-outs reach slides; the profile does not.
- The `writer` model routing revisit (ADR-0003): after this build, as a separate read-out.

## Risks

- **A corpus of one paper.** The profile is provisional and marked so, and may overfit the paper's topic. Topic words are excluded from Lexicon by rule. A4's third excerpt, from another author on a nearby topic, tests whether the profile only captures the topic.
- **Unknown AI help in the corpus.** The owner's declaration is the only evidence; the front-matter records it per source.
- **Copying another author's quirks.** Style models have a reduced schema and never feed the carve-outs or the whitelist.

## Review resolutions (v1 → v2)

**Fit-for-purpose, 72/100:**
- **High findings, all adopted:**
  - A4 rebuilt: three trials, an excerpt from another author, cited lines, a pass threshold.
  - Standing privacy rule added.
  - Backlog closure made true: `writer-critic.md:51` and `storyteller-critic.md` edits added.
- **Medium findings:**
  - Adopted: the sync list corrected (ADR and CLAUDE.md are excluded); the reduced style-model schema; home-path resolution; A5 at three pairs.
  - Declined: "no LaTeX on this machine, so `pdftotext` is unavailable". This came from a stale memory note: TeX Live 2026 has been installed since 2026-10-22, and its `pdftotext` extracted the corpus PDF on 2026-10-29. The memory note is corrected.
- **Low findings, all adopted:**
  - the `sections:` tag;
  - the consistency-and-bloat review for the rule edit;
  - A2 bounded.
  - A1 is moot, since the script is deferred.

**Efficiency, 80/100:**
- **Adopted:**
  - the script deferred, with a trigger;
  - the sync list per repo;
  - one home for the lists, with the reference and skeletons merged;
  - the CLAUDE.md override field dropped;
  - A2 bounded.
- **Partly adopted:** the style-models machinery. The `--model` mode and the reduced schema stay, because the owner said papers are coming; there is no separate template file.
